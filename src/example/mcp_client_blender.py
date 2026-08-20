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

def init_llm():
    return ChatAnthropic(model="claude-haiku-4-5-20251001", api_key=os.environ.get("CLAUDE_API_KEY"))


MCP_SERVERS = {
    "blender": {
        "transport": "http", 
        "url": "http://127.0.0.1:9191",
    },
    # Add more MCP servers here — each one just adds more tools to the pool.
    # "github": {"command": "...", "args": [...], "transport": "stdio"},
}


async def blender_mcp_agent_node(state: AgentState):
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()
    llm = init_llm().bind_tools(tools)
    tool_calls = await llm.ainvoke(state["next_step"])
    return {"messages": [tool_calls]}

async def blender_mcp_tools():
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()
    return tools

class BlenderMCP():
    def __init__(self):
        self.client = MultiServerMCPClient(MCP_SERVERS)
    def execute(self, state: AgentState):
        return self.tool_node.execute(state["messages"][-1])
    async def tools(self):
        return await self.client.get_tools()
    


def blender_mcp_tool_node(state: AgentState):
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = client.get_tools_sync()
    tool_node = ToolNode(tools)
    return tool_node.execute(state["messages"][-1])

