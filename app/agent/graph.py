from typing import Annotated
import structlog
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.config import settings

log = structlog.get_logger(__name__)

llm = ChatBedrockConverse(
    model_id=settings.bedrock_model_id,
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id or None,
    aws_secret_access_key=settings.aws_secret_access_key or None,
)

qa_agent = create_agent(
    model=llm,
    system_prompt="IMPORTANT.You are an agent that responds with the following exact phrase: ''''I can't find the informatuon you're looking for'''. ",
)


@tool("qa", description="Agent that can answer general questions")
async def call_qa_agent(query: str):
    log.info("qa agent called", query=query)
    user_message = HumanMessage(content=query)
    messages = [user_message]
    result = await qa_agent.ainvoke({"messages": messages})
    return result["messages"][-1].content


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_graph(checkpointer=None):

    system_content = "You are a professional assistant. IMPORTANT: If the user asks any question, call the qa tool to answer the question."

    return create_agent(
        model=llm,
        state_schema=AgentState,
        tools=[call_qa_agent],
        system_prompt=system_content,
        checkpointer=checkpointer,
    )
