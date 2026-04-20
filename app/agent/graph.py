from typing import Callable
import json
import structlog
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_aws import ChatBedrockConverse
from langchain_qdrant import QdrantVectorStore
from langchain.agents.structured_output import ProviderStrategy
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from app.agent.models import InsuranceFormState, KnowledgeBaseAnswer
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
)
from app.agent.prompts import (
    EMIRATE_COLLECTOR_PROMPT,
    CAR_MAKE_COLLECTOR_PROMPT,
    CAR_MODEL_COLLECTOR_PROMPT,
    CAR_YEAR_COLLECTOR_PROMPT,
    NUMBER_OF_ACCIDENTS_COLLECTOR_PROMPT,
    PRINT_PREMIUM_PROMPT,
    ENQUIRY_AGENT_PROMPT,
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
}


def build_graph(vector_store: QdrantVectorStore, checkpointer=None):
    @tool
    def search_knowledge_base(query: str) -> str:
        """Search the knowledge base for insurance policy information. Returns a JSON list of results with content, source, page, and relevance score."""
        log.info("search_knowledge_base invoked", query=query)
        results = vector_store.similarity_search_with_score(query, score_threshold=0.60)
        results_json = json.dumps(
            [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "page": doc.metadata.get("page", "unknown"),
                    "score": round(float(score), 2),
                }
                for doc, score in results
            ],
            indent=2,
        )
        log.info("search_knowledge_base", results_json=results_json)
        return results_json

    # A dedicated sub-agent to avoid polluting the context of the form agent.
    insurance_knowledge_agent = create_agent(
        model=llm,
        tools=[search_knowledge_base],
        system_prompt=ENQUIRY_AGENT_PROMPT,
        # response_format=ProviderStrategy(KnowledgeBaseAnswer),
    )

    @tool
    def answer_insurance_question(query: str) -> str:
        """Answer a question about car insurance in the UAE using the knowledge base."""
        result = insurance_knowledge_agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        answer = result["messages"][-1].content
        log.info("Insurance knowledge agent raw result", answer=answer)
        return answer

    @wrap_model_call
    async def apply_step_config(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Configure agent behavior based on the current step."""

        # log.info("Current State", **request.state)

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

        tools = [*stage_config["tools"], answer_insurance_question]

        request = request.override(
            system_prompt=system_prompt,
            tools=tools,
        )

        return await handler(request)

    log.info("Built the graph")
    return create_agent(
        model=llm,
        tools=[*all_tools, answer_insurance_question],
        state_schema=InsuranceFormState,
        middleware=[apply_step_config],
        checkpointer=checkpointer,
    )
