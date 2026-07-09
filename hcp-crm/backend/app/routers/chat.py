from fastapi import APIRouter
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from app.agent.graph import hcp_agent_graph
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


def _to_lc_messages(messages):
    lc_messages = []
    for m in messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        else:
            lc_messages.append(AIMessage(content=m.content))
    return lc_messages


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    """Conversational entry point for the Log Interaction Screen's chat mode.
    Runs the full message history through the LangGraph agent, which decides
    which of the 5 CRM tools (if any) to call, then returns the final natural
    language reply plus a trace of which tools fired (useful for your demo
    video)."""
    lc_messages = _to_lc_messages(payload.messages)

    # Give the agent HCP context if the UI already has one selected
    if payload.hcp_id:
        lc_messages = [
            HumanMessage(content=f"(context: current HCP id is {payload.hcp_id})")
        ] + lc_messages

    result = hcp_agent_graph.invoke({"messages": lc_messages})

    final_messages = result["messages"]
    tool_calls_fired = [m.name for m in final_messages if isinstance(m, ToolMessage)]

    reply = ""
    for m in reversed(final_messages):
        if isinstance(m, AIMessage) and m.content:
            reply = m.content
            break

    return ChatResponse(reply=reply, tool_calls=tool_calls_fired)
