import structlog
from langchain_core.messages import AIMessage, ToolMessage

log = structlog.get_logger(__name__)


def clean_orphaned_tool_calls(messages: list) -> list:
    """Remove AIMessages whose tool_calls have no matching ToolMessage responses.

    Bedrock Converse requires every tool_use to have a corresponding tool_result.
    Orphaned calls appear when the graph is interrupted or an exception fires
    after the model responds but before the tool result is appended.
    """
    responded_ids: set[str] = {
        m.tool_call_id for m in messages if isinstance(m, ToolMessage)
    }
    cleaned = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            call_ids = {tc["id"] for tc in msg.tool_calls}
            if not call_ids.issubset(responded_ids):
                log.warning(
                    "dropping orphaned tool_calls from history",
                    call_ids=call_ids - responded_ids,
                )
                continue
        cleaned.append(msg)
    return cleaned
