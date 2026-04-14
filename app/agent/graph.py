from typing import Annotated, Literal, NotRequired, Callable
import structlog
from langchain.agents import AgentState, create_agent
from langchain.tools import tool, ToolRuntime
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from app.agent.models import InsuranceFormState
from app.agent.tools import (
    record_emirate,
    record_car_make,
    record_car_model,
    record_car_year,
    record_number_of_accidents,
    calculate_premium,
    print_premium,
)
from app.agent.prompts import (
    EMIRATE_COLLECTOR_PROMPT,
    CAR_MAKE_COLLECTOR_PROMPT,
    CAR_MODEL_COLLECTOR_PROMPT,
    CAR_YEAR_COLLECTOR_PROMPT,
    NUMBER_OF_ACCIDENTS_COLLECTOR_PROMPT,
    PRINT_PREMIUM_PROMPT,
)

from app.config import settings

log = structlog.get_logger(__name__)

llm = ChatBedrockConverse(
    model_id=settings.bedrock_model_id,
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id or None,
    aws_secret_access_key=settings.aws_secret_access_key or None,
    max_tokens=settings.bedrock_max_tokens,
    temperature=settings.bedrock_temperature,
)


# Step configuration: maps step name to (prompt, tools, required_state)
STEP_CONFIG = {
    "emirate_collector": {
        "prompt": EMIRATE_COLLECTOR_PROMPT,
        "tools": [record_emirate],
        "requires": [],
    },
    "car_make_collector": {
        "prompt": CAR_MAKE_COLLECTOR_PROMPT,
        "tools": [record_car_make],
        "requires": [],
    },
    "car_model_collector": {
        "prompt": CAR_MODEL_COLLECTOR_PROMPT,
        "tools": [record_car_model],
        "requires": ["car_make"],
    },
    "car_year_collector": {
        "prompt": CAR_YEAR_COLLECTOR_PROMPT,
        "tools": [record_car_year],
        "requires": [],
    },
    "number_of_accidents_collector": {
        "prompt": NUMBER_OF_ACCIDENTS_COLLECTOR_PROMPT,
        "tools": [record_number_of_accidents, calculate_premium],
        "requires": ["emirate", "car_make", "car_model", "car_year"],
    },
    "print_premium": {
        "prompt": PRINT_PREMIUM_PROMPT,
        "tools": [print_premium],
        "requires": [
            "premium",
        ],
    },
}


@wrap_model_call
async def apply_step_config(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """Configure agent behavior based on the current step."""

    log.info("Current State", **request.state)

    # Get current step (defaults to emirate_collector for first interaction)
    current_step = request.state.get("current_step", "emirate_collector")

    # Look up step configuration
    stage_config = STEP_CONFIG[current_step]

    # Validate required state exists
    for key in stage_config["requires"]:
        if request.state.get(key) is None:
            raise ValueError(f"{key} must be set before reaching {current_step}")

    # Format prompt with state values (supports {warranty_status}, {issue_type}, etc.)
    system_prompt = stage_config["prompt"].format(**request.state)

    # Inject system prompt and step-specific tools
    request = request.override(
        system_prompt=system_prompt,
        tools=stage_config["tools"],
    )

    response = await handler(request)

    return response


all_tools = [
    record_emirate,
    record_car_make,
    record_car_model,
    record_car_year,
    record_number_of_accidents,
    calculate_premium,
    print_premium,
]


def build_graph(checkpointer=None):
    log.info("Built the graph")
    return create_agent(
        model=llm,
        tools=all_tools,
        state_schema=InsuranceFormState,
        middleware=[apply_step_config],
        checkpointer=checkpointer,
    )
