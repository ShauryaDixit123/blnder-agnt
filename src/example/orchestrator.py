"""
Simple LangGraph orchestrator that chains multiple MCP servers behind one LLM agent.

Architecture
------------
                ┌─────────────────────────────────────────┐
                │              LangGraph StateGraph         │
                │                                           │
   user msg --> │  [agent] --tool_call--> [tools] --> loop  │ --> final answer
                │     ^                        |            │
                │     └────────────────────────┘            │
                └─────────────────────────────────────────┘
                          |                |
                     MCP Server A     MCP Server B   (e.g. blender-mcp, filesystem-mcp)
                     (tools loaded via langchain-mcp-adapters, merged into ONE toolset)

The "agent" node is a normal LLM call with tools bound to it. The "tools" node executes
whichever MCP tool(s) the LLM asked for, across ANY connected MCP server, then routes
back to the agent. This repeats until the LLM stops calling tools.

Install:
    pip install langgraph langchain-anthropic langchain-mcp-adapters mcp
"""

import asyncio
import os
import sys
from typing import Annotated, Optional, TypedDict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from example.state import AgentState
from example.planner import create_primitive, route_execution, local_mcp_tools_dict
from example.mcp_client_blender import MCP_SERVERS
# Load environment variables from .env file∆
load_dotenv()

# Ensure the repo root is on sys.path so `blender_mcp` can be imported when
# running this example from `example/`.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

# ---------------------------------------------------------------------------
# 1. Define the graph state (just a running message list)
# ---------------------------------------------------------------------------
class StoryLine(BaseModel):
    id: str = Field(..., description="The unique identifier for the story line")
    image: Optional[str] = Field(None, description="The image to be processed")
    prompt: Optional[str] = Field(None, description="The prompt for the image processing")
    image_style: Optional[str] = Field(None, description="The style of the image to be generated")



class OrchestratorResponse(TypedDict):
    next_step: str = Field(None, description="The next step in the story to be executed")

# ---------------------------------------------------------------------------
# 2. Configure the chain of MCP servers you want the agent to have access to.
#    MultiServerMCPClient merges all their tools into a single list, so the
#    LLM can freely call across servers in whatever order it needs.
# ---------------------------------------------------------------------------
MCP_DIR = os.path.expanduser("~/Documents/vesai/")


class AgentToolResponse(TypedDict):
    tool_calls: list[dict]

def init_llm():
    return ChatAnthropic(model="claude-haiku-4-5-20251001", api_key=os.environ.get("CLAUDE_API_KEY"))

def llm_with_tools(tools):
    llm = init_llm().bind_tools(tools)
    return llm



def verify_node(state: AgentState):
    print("Verifying the last message...")
    return {"messages": [{"role": "system", "content": {"type": "text", "text": "Verification complete."}}]}



def tools_condition(state: AgentState):
    last_message = state["messages"][-1]
    tool_calls = None
    if isinstance(last_message, dict):
        tool_calls = last_message.get("tool_calls")
    else:
        tool_calls = getattr(last_message, "tool_calls", None)

    print(f"Last message tool_calls: {tool_calls}")
    return "tools" if tool_calls else END


blender_mcp_client = MultiServerMCPClient(MCP_SERVERS)
async def getblender_tools_list():
    return await blender_mcp_client.get_tools()

async def build_graph():
    # --- Load tools from every configured MCP server ---
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()
    # --- Node: executes whatever MCP tool call(s) the LLM requested ---
    tool_node = ToolNode(tools)
 
    # --- Wire the graph ---
    graph = StateGraph(AgentState)
    graph.add_node("agent", create_primitive)
    graph.add_node("mcp_tool_executor_node", tool_node)
    for v in local_mcp_tools_dict:
        graph.add_node(v["id"], v[v["id"]])
    # graph.add_node("verify", verify_node)
 
    graph.set_entry_point("agent")
    # tools_condition inspects the last message: if it has tool_calls, go to
    # "tools"; otherwise the agent is done and we route to END.
    graph.add_conditional_edges("agent", route_execution, create_local_mcp_tools_list([
        {"id" : "mcp_tool_executor_node", "description" : "final tool execution node for blender mcp","mcp_tool_executor_node" : "mcp_tool_executor_node" }
    ]))
    # graph.add_edge(create_local_mcp_tools_list(), "agent")  
      # after running tools, loop back to the agent
    # graph.add_edge("verify", "agent")  # after verifying, loop back to the agent
 
    return graph.compile()

def create_local_mcp_tools_list(l=None):
    if l is None:
        l = []

    l.extend(local_mcp_tools_dict)
    tool_dict = {}
    for v in l:
        tool_dict[v["id"]] = v["id"]
    tool_dict[END] = END
    print(tool_dict)
    return tool_dict


# async def build_graph_tes():
#     # --- Load tools from every configured MCP server ---
#     client = MultiServerMCPClient(MCP_SERVERS)
#     tools = await client.get_tools()
 
#     llm = init_llm().bind_tools(tools)
 
#     # --- Node: the LLM reasoning/decision step ---
#     async def agent_node(state: AgentState):
#         response = await llm.ainvoke(state["messages"])
#         return {"messages": [response]}
 
#     # --- Node: executes whatever MCP tool call(s) the LLM requested ---
#     tool_node = ToolNode(tools)
 
#     # --- Wire the graph ---
#     graph = StateGraph(AgentState)
#     graph.add_node("agent", create_primitive)
#     graph.add_node("tools", tool_node)
#     # graph.add_node("verify", verify_node)
 
#     graph.set_entry_point("agent")
#     # tools_condition inspects the last message: if it has tool_calls, go to
#     # "tools"; otherwise the agent is done and we route to END.
#     graph.add_conditional_edges("agent", route_execution, create_local_mcp_tools_list())
#     graph.add_edge(create_local_mcp_tools_list(), "agent")  # after running tools, loop back to the agent
#     # graph.add_edge("verify", "agent")  # after verifying, loop back to the agent
 
#     return graph.compile()
async def main():
    app = await build_graph()

    initial_state: AgentState = {
        "messages": [
            (
                "user",
                "There is a boy sitting on a chair."
            )
        ],
        "plan": [],
        "current_plan_step": 0,
        "completed_steps": [],
        "failed_steps": {},
        "status": "planning",
        "error": None,
        "blender_tools" : await getblender_tools_list()
    }

    result = await app.ainvoke(initial_state)

    for msg in result["messages"]:
        msg.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())