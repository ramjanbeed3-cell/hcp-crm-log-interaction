"""
LangGraph agent for the HCP "Log Interaction" conversational chat mode.

The graph is a simple, standard tool-calling loop:

    START -> agent -> (tool_calls?) -> tools -> agent -> ... -> END

`agent` is the Groq-hosted LLM (gemma2-9b-it) bound to the 5 CRM tools.
`tools` executes whichever tool calls the model requested and feeds the
results back to the model. The loop continues until the model responds
without requesting further tool calls.
"""

from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

from app.agent.tools import ALL_TOOLS
from app.llm import get_primary_llm

SYSTEM_PROMPT = """You are the AI CRM assistant embedded in the HCP (Healthcare
Professional) module of a life-sciences CRM. Field reps talk to you in natural
language after a call or visit, and you are responsible for turning that into
structured CRM data using your tools.

Guidelines:
- If the rep is describing a new interaction, first call fetch_hcp_profile to
  get context, then call log_interaction with the rep's raw description.
- If the rep wants to correct or add detail to something already logged, call
  edit_interaction.
- If the rep wants a reminder to follow up, call schedule_followup.
- If the rep asks "what's my history with Dr. X" or wants a pre-visit brief,
  call generate_summary_report.
- Always confirm back to the rep, in plain conversational language, what you
  logged/changed - don't just dump raw JSON at them.
"""


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_graph():
    llm = get_primary_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


# Compiled once at import time and reused across requests
hcp_agent_graph = build_graph()
