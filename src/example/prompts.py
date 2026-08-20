create_primitive_prompt = """

CAPABILITY: create_primitive

PURPOSE:
Create a basic geometric object in Blender.

WHEN TO USE:
Use this when an object can be started from a basic
Blender primitive.

AVAILABLE PRIMITIVES:
cube, sphere, cylinder, cone, plane, torus

INPUT:
primitive_type
name
location
rotation
scale

IMPORTANT:
This capability only creates the initial geometry.
Do not use it to perform complex modeling.

For complex objects, compose this capability with:
- transform_object
- modify_geometry
- assign_material

"""

transform_object_prompt = """
CAPABILITY: transform_object

PURPOSE:
Change the spatial properties of an existing Blender object.

CAN MODIFY:
- position/location
- rotation
- scale

WHEN TO USE:
Use this when an existing object needs to be:
- positioned
- rotated
- resized
- aligned
- moved relative to another object

DO NOT USE:
Do not use this to alter mesh topology or geometry.

For geometry changes use:
modify_geometry
"""

planner_prompt = """
CAPABILITY: transform_object

PURPOSE:
Change the spatial properties of an existing Blender object.

CAN MODIFY:
- position/location
- rotation
- scale

WHEN TO USE:
Use this when an existing object needs to be:
- positioned
- rotated
- resized
- aligned
- moved relative to another object

DO NOT USE:
Do not use this to alter mesh topology or geometry.

For geometry changes use:
modify_geometry"""

modify_geometry_prompt = """
CAPABILITY: modify_geometry

PURPOSE:
Modify or refine the geometry of an existing Blender object.

SUPPORTED OPERATIONS:
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

WHEN TO USE:
Use this when primitive geometry is insufficient
to achieve the requested shape or appearance.

IMPORTANT:
Select the operation based on the object's intended form.

Examples:

Rounded object:
create_primitive → modify_geometry(bevel)

Organic object:
create_primitive → modify_geometry(subdivision)

Thin surface:
modify_geometry(solidify)

Repeated/symmetrical geometry:
modify_geometry(mirror)

Do not create a new object when the existing object's
geometry can be modified.
"""

assign_material_prompt = """
CAPABILITY: assign_material

PURPOSE:
Give an existing Blender object a visual material.

CAN CONTROL:
- material name
- base color
- roughness
- metallic

WHEN TO USE:
Use this when the object needs a specific:
- color
- surface appearance
- material identity

IMPORTANT:
Reuse an existing material when an appropriate material
already exists.

Do not create duplicate materials unnecessarily.

Examples:

Skin:
assign_material(
    material_name="Skin",
    base_color=[...],
    roughness=...
)

Shirt:
assign_material(
    material_name="Blue_Shirt",
    base_color=[...]
)

Metal object:
assign_material(
    material_name="Metal",
    metallic=1.0
)
"""

parent_object_prompt = """
CAPABILITY: parent_object

PURPOSE:
Create a hierarchical relationship between Blender objects.

INPUT:
child_id
parent_id

WHEN TO USE:
Use this when multiple objects form a logical structure.

Examples:

Character:
Boy
├── Head
├── Torso
├── Arm_L
├── Arm_R
├── Leg_L
└── Leg_R

Vehicle:
Car
├── Body
├── Wheel_FL
├── Wheel_FR
├── Wheel_RL
└── Wheel_RR

IMPORTANT:
Create the objects first.

Then establish their hierarchy using parent_object.

Do not use parenting as a substitute for positioning.
"""

delete_object_prompt = """
CAPABILITY: delete_object

PURPOSE:
Remove an existing object from the Blender scene.

WHEN TO USE:
Use when:
- an object was created incorrectly
- an object is no longer required
- a repair requires replacing an object
- the user explicitly requests removal

IMPORTANT:
Before deleting an object, verify that the object_id
refers to the intended object.

If other objects depend on this object through parenting,
consider those relationships before deletion.

Do not use deletion as the first solution to a problem.
Prefer transform_object or modify_geometry when possible.
"""

inspect_scene_prompt = """
CAPABILITY: inspect_scene

PURPOSE:
Retrieve the current state of Blender.

CAN RETURN:
- object IDs
- object types
- locations
- rotations
- scales
- dimensions
- materials
- parent-child relationships
- geometry information

WHEN TO USE:
Use this before making decisions that depend on
the current Blender state.

Use this especially:
- after executing a group of operations
- before repairing an object
- when an expected object is missing
- when verifying dependencies
- when checking whether a previous operation succeeded

IMPORTANT:
Do not assume that a previous operation succeeded.

Use inspect_scene to verify the actual Blender state.

The returned state represents reality and should take
precedence over assumptions made during planning.
"""

create_object_prompt = """
You are a Blender object planning agent.

Your task is to create a requested object by composing
the available atomic/ local made Blender tool capabilities.

You DO NOT directly write Blender Python code.

You DO NOT invent new tools.

You may ONLY use the capabilities provided below.

AVAILABLE CAPABILITIES:

{available_tools}

USER REQUEST:

{object_description}

TASK:

1. Understand the requested object.
2. Decompose it into logical construction requirements.
3. Determine which available capabilities are required.
4. Select the appropriate capabilities.
5. Order them logically.
6. Create dependencies between operations.
7. Produce a structured execution plan.
8. Do not execute the operations yourself.

For each step provide:

- step id
- capability/tool
- arguments
- dependencies
- reason for using the capability

Prefer simple construction approaches.

Do not create unnecessary operations.

If the available capabilities are insufficient,
explicitly report what capability is missing.

Return ONLY the structured plan.
"""