from typing import Callable, Literal
import structlog
from langchain.agents import create_agent
from langchain_aws import ChatBedrockConverse
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from pydantic import BaseModel
from app.agent.models import InsuranceFormState
from app.agent.utils import clean_orphaned_tool_calls
from app.agent.tools import (
    validate_emirate,
    record_emirate,
    record_car_make,
    record_car_model,
    validate_year_of_manufacture,
    record_car_year,
    record_number_of_accidents,
    calculate_premium,
    print_premium,
    create_payment_intent,
    print_checkout_session_url,
    check_and_update_payment_status,
    search_knowledge_base,
)
from app.agent.prompts import (
    EMIRATE_COLLECTOR_PROMPT,
    CAR_MAKE_COLLECTOR_PROMPT,
    CAR_MODEL_COLLECTOR_PROMPT,
    CAR_YEAR_COLLECTOR_PROMPT,
    NUMBER_OF_ACCIDENTS_COLLECTOR_PROMPT,
    PRINT_PREMIUM_PROMPT,
    ENQUIRY_AGENT_PROMPT,
    CHECK_PAYMENT_STATUS_PROMPT,
    CLASSIFIER_PROMPT,
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

all_tools = [
    validate_emirate,
    record_emirate,
    record_car_make,
    record_car_model,
    validate_year_of_manufacture,
    record_car_year,
    record_number_of_accidents,
    calculate_premium,
    print_premium,
    create_payment_intent,
    print_checkout_session_url,
    check_and_update_payment_status,
]

# Step configuration: maps step name to (prompt, tools, required_state)
STEP_CONFIG = {
    "emirate_collector": {
        "prompt": EMIRATE_COLLECTOR_PROMPT,
        "tools": [record_emirate, validate_emirate],
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
        "tools": [
            record_car_year,
            validate_year_of_manufacture,
        ],
        "requires": [],
    },
    "number_of_accidents_collector": {
        "prompt": NUMBER_OF_ACCIDENTS_COLLECTOR_PROMPT,
        "tools": [record_number_of_accidents],
        "requires": ["emirate", "car_make", "car_model", "car_year"],
    },
    "print_premium": {
        "prompt": PRINT_PREMIUM_PROMPT,
        "tools": [calculate_premium, print_premium, create_payment_intent],
        "requires": [],
    },
    "print_checkout_url": {
        "prompt": PRINT_PREMIUM_PROMPT,
        "tools": [],
        "requires": ["checkout_session_url"],
    },
    "check_and_update_payment_status": {
        "prompt": CHECK_PAYMENT_STATUS_PROMPT,
        "tools": [check_and_update_payment_status],
        "requires": ["checkout_session_url"],
    },
}


class _RouteDecision(BaseModel):
    route: Literal["question", "form"]


def build_graph(checkpointer=None):

    insurance_knowledge_agent = create_agent(
        model=llm,
        tools=[search_knowledge_base],
        system_prompt=ENQUIRY_AGENT_PROMPT,
    )

    @wrap_model_call
    async def apply_step_config(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Configure agent behavior based on the current step."""

        current_step = request.state.get("current_step", "emirate_collector")
        stage_config = STEP_CONFIG[current_step]

        for key in stage_config["requires"]:
            if request.state.get(key) is None:
                raise ValueError(f"{key} must be set before reaching {current_step}")

        system_prompt = stage_config["prompt"].format(**request.state)

        request = request.override(
            system_prompt=system_prompt,
            tools=stage_config["tools"],
            messages=clean_orphaned_tool_calls(request.messages),
        )

        return await handler(request)

    form_agent = create_agent(
        model=llm,
        tools=all_tools,
        state_schema=InsuranceFormState,
        middleware=[apply_step_config],
    )

    classifier = llm.with_structured_output(_RouteDecision)

    def router(state: InsuranceFormState) -> Command[Literal["knowledge_agent", "form_agent"]]:
        last_message = state["messages"][-1].content
        decision = classifier.invoke([
            SystemMessage(content=CLASSIFIER_PROMPT),
            HumanMessage(content=last_message),
        ])
        goto = "knowledge_agent" if decision.route == "question" else "form_agent"
        log.info("Router decision", route=decision.route)
        return Command(goto=goto)

    async def knowledge_agent_node(state: InsuranceFormState):
        last_message = state["messages"][-1]
        result = await insurance_knowledge_agent.ainvoke({"messages": [last_message]})
        return {"messages": result["messages"][1:]}

    graph = StateGraph(InsuranceFormState)
    graph.add_node("router", router)
    graph.add_node("knowledge_agent", knowledge_agent_node)
    graph.add_node("form_agent", form_agent)
    graph.add_edge(START, "router")
    graph.add_edge("knowledge_agent", END)
    graph.add_edge("form_agent", END)

    log.info("Built the graph")
    return graph.compile(checkpointer=checkpointer)
