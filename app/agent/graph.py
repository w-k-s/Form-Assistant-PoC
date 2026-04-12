from typing import Annotated

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import SystemMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.config import settings


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_graph():
    llm = ChatBedrockConverse(
        model_id=settings.bedrock_model_id,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None,
    )

    async def call_model(state: AgentState, config: RunnableConfig) -> dict:
        # user = config.get("configurable", {}).get("user")

        system_content = "You are a helpful and concise assistant."
        # if user:
        #     system_content += (
        #         f" The user's name is {user.get('name', 'there')}."
        #         " Personalize your responses to them."
        #     )

        messages = [SystemMessage(content=system_content)] + state["messages"]
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("call_model", call_model)
    graph.add_edge(START, "call_model")
    graph.add_edge("call_model", END)

    return graph
