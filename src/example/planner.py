import json

from distro import name
from pydantic import BaseModel, Field
from typing import TypedDict, Optional, List
from example.state import AgentState
from example.mcp_client_blender import BlenderMCP
from example.prompts import create_primitive_prompt, modify_geometry_prompt, assign_material_prompt, parent_object_prompt, delete_object_prompt, inspect_scene_prompt, transform_object_prompt
from uuid import uuid1
import re, os

from langchain_anthropic import ChatAnthropic

blender_mcp = BlenderMCP()

def init_llm():
    return ChatAnthropic(model="claude-haiku-4-5-20251001", api_key=os.environ.get("CLAUDE_API_KEY"))

from typing import Optional
from pydantic import BaseModel, Field

class PlanStep(BaseModel):
    args: dict = Field(default_factory=dict)
    depends_on: list[str] = Field(
        default_factory=list,
        description="List of step IDs that this step depends on"
    )
    agent_id: str = Field(
        description="Agent id of the agent to complete this task."
    )
    mcp_tool_id: str = Field(
        description="MCP tool id to be run in this task."
    )
    to_be_completed_in_this: str = Field(
        description="This will be completed in this step according to plan."
    )
    completed_in_this_step: Optional[str] = Field(
        default=None,
        description="What is completed in this step"
    )

async def getblender_tools():
    return await blender_mcp.tools()

class Plan(BaseModel):
    steps: list[PlanStep]

def modify_geometry(
    state: AgentState
) -> dict:
    """
    Modify the geometry of an existing Blender object.

    Supported operations can include:
    - bevel
    - subdivision
    - smooth
    - solidify
    - extrude
    - inset
    - boolean
    - mirror
    - join
    - separate

    Parameters depend on the selected operation.
    """
    current_step = state["plan"][state["current_plan_step"]]
    blender_tools = state["blender_tools"]
    prompt = modify_geometry_prompt + f"This needs to be done in this step : {current_step.to_be_completed_in_this}, arguments to complete the task are : {current_step.args}. There is a list of tools in here which you can go through to select the list of tool required to build this. This is list of blender tools, blender is a movie generation software : {json.dumps(blender_tools)}. Understand these tools, Give out a plan in structured format, while building a dependency graph to form complete object told to you. If you select a mcp tool, put its name as id in the response as mcp_tool_id."
    llm = init_llm().with_structured_output(Plan)
    plan = llm.invoke(prompt)
    return {
            **state,
            "current_plan_step" : state["current_plan_step"] + 1,
            "plan": plan,
    }


def assign_material(
    state: AgentState
) -> dict:
    """
    Create or reuse a material and assign it to an object.

    Supports basic Principled BSDF properties.
    """
    current_step = state["plan"][state["current_plan_step"]]
    blender_tools = state["blender_tools"]
    prompt = assign_material_prompt + f"This needs to be done in this step : {current_step.to_be_completed_in_this}, arguments to complete the task are : {current_step.args}. There is a list of tools in here which you can go through to select the list of tool required to build this. This is list of blender tools, blender is a movie generation software : {json.dumps(blender_tools)}. Understand these tools, Give out a plan in structured format, while building a dependency graph to form complete object told to you. If you select a mcp tool, put its name as id in the response as mcp_tool_id."
    llm = init_llm().with_structured_output(Plan)
    plan = llm.invoke(prompt)
    return {
            **state,
            "current_plan_step" : state["current_plan_step"] + 1,
            "plan": plan,
    }
def parent_object(
    state: AgentState,
) -> dict:
    """
    Establish a parent-child relationship between
    two Blender objects.
    """
    current_step = state["plan"][state["current_plan_step"]]
    blender_tools = state["blender_tools"]
    prompt = parent_object_prompt + f"This needs to be done in this step : {current_step.to_be_completed_in_this}, arguments to complete the task are : {current_step.args}. There is a list of tools in here which you can go through to select the list of tool required to build this. This is list of blender tools, blender is a movie generation software : {json.dumps(blender_tools)}. Understand these tools, Give out a plan in structured format, while building a dependency graph to form complete object told to you. If you select a mcp tool, put its name as id in the response as mcp_tool_id."
    llm = init_llm().with_structured_output(Plan)
    plan = llm.invoke(prompt)
    return {
        **state,
        "current_plan_step" : state["current_plan_step"] + 1,
        "plan": plan,
    }

def delete_object(
    state: AgentState
) -> dict:
    """
    Delete an existing Blender object.
    """
    current_step = state["plan"][state["current_plan_step"]]
    blender_tools = state["blender_tools"]
    prompt = delete_object_prompt + f"This needs to be done in this step : {current_step["to_be_completed_in_this"]}, arguments to complete the task are : {current_step.args}. There is a list of tools in here which you can go through to select the list of tool required to build this. This is list of blender tools, blender is a movie generation software : {json.dumps(blender_tools)}. Understand these tools, Give out a plan in structured format, while building a dependency graph to form complete object told to you. If you select a mcp tool, put its name as id in the response as mcp_tool_id."
    llm = init_llm().with_structured_output(Plan)
    plan = llm.invoke(prompt)
    return {
        **state,
        "current_plan_step" : state["current_plan_step"] + 1,
        "plan": plan,
    }
def inspect_scene(
    state: AgentState
) -> dict:
    current_step = state["plan"][state["current_plan_step"]]
    """
    Inspect the current Blender scene and return
    structured information about its current state.
    """
    blender_tools = state["blender_tools"]
    prompt = inspect_scene_prompt + f"This needs to be done in this step : {current_step.to_be_completed_in_this}, arguments to complete the task are : {current_step.args}. There is a list of tools in here which you can go through to select the list of tool required to build this. This is list of blender tools, blender is a movie generation software : {json.dumps(blender_tools)}. Understand these tools, Give out a plan in structured format, while building a dependency graph to form complete object told to you. If you select a mcp tool, put its name as id in the response as mcp_tool_id."
    llm = init_llm().with_structured_output(Plan)
    plan = llm.invoke(prompt)
    return {
        **state,
        "current_plan_step" : state["current_plan_step"] + 1,
        "plan": plan,
    }

def transform_object(
   state: AgentState
) -> dict:
    current_step = state["plan"][state["current_plan_step"]]
    """
    Transform an existing Blender object.

    Can modify:
    - location
    - rotation
    - scale

    Does not modify the underlying mesh geometry.
    """
    blender_tools = state["blender_tools"]
    prompt = transform_object_prompt + f"This needs to be done in this step : {current_step.to_be_completed_in_this}. There is a list of tools in here which you can go through to select the list of tool required to build this. This is list of blender tools, blender is a movie generation software : {json.dumps(blender_tools)}. Understand these tools, Give out a plan in structured format, while building a dependency graph to form complete object told to you. If you select a mcp tool, put its name as id in the response as mcp_tool_id."
    llm = init_llm().with_structured_output(Plan)
    plan = llm.invoke(prompt)
    return {
        **state,
        "current_plan_step" : state["current_plan_step"] + 1,
        "plan": plan,
    }

    

def route_execution(state: AgentState):
    plan = state["plan"]
    current_step = plan[state["current_plan_step"]]
    print("zxczxc", current_step)
    if current_step.mcp_tool_id == "mcp_tool_executor_node":
        return "mcp_tool_executor_node"
    if current_step.mcp_tool_id != None:
        return current_step.mcp_tool_id




def create_primitive(state: AgentState):
    info = ""
    llm = init_llm().with_structured_output(Plan)
    current_step = state["current_plan_step"]
    if len(state["plan"]) > 0 & current_step > 0:
        info += f"Here is what needs to be done : {state["plan"][current_step].to_be_completed_in_this}"
        current_step  = current_step + 1,
    plan = llm.invoke(
            state["messages"] + [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Based on the provided image and prompt in a previous message, "
                        "break down the current scene into a set of steps. "
                        "Each step should describe in detail what needs to be done. "
                        "Also provide descriptive properties, if any, which can later "
                        "be used to fill Blender MCP tools. Do not assume properties "
                        "that are not provided. Use simple descriptive terms.\n\n"
                        "You are provided with the following local agents and their "
                        "capabilities:\n\n"
                        + "\n".join(
                            f"{k.upper().replace('_', ' ')}: {v}"
                            for tool in local_mcp_tools_dict
                            for k, v in tool.items()
                        )
                    ),
                }
            ],
        }
    ]
    )

    if len(state["plan"]) == 0:
        idx_plan_step = [v for i, v in enumerate(plan.steps)]
    return {
        **state,
        "plan": plan.steps,
        "current_plan_step" : current_step
    }


local_mcp_tools = [modify_geometry, create_primitive,
                    assign_material, parent_object, delete_object,
                    inspect_scene, transform_object]



local_mcp_tools_dict = [
   { "modify_geometry" : modify_geometry, "description": modify_geometry_prompt, "id": "modify_geometry" },
   { "create_primitive" : create_primitive, "description": create_primitive_prompt, "id": "create_primitive" },
   { "assign_material" : assign_material, "description": assign_material_prompt, "id": "assign_material" },
   { "parent_object" : parent_object, "description": parent_object_prompt, "id": "parent_object" },
   { "delete_object" : delete_object, "description": delete_object_prompt, "id": "delete_object" },
   { "inspect_scene" : inspect_scene, "description": inspect_scene_prompt, "id": "inspect_scene" },
   { "transform_object" : transform_object, "description": transform_object_prompt, "id": "transform_object" }
]