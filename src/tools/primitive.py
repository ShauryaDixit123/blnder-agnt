import bpy


def create_object(
    object_type: str,
    name: str,
    location=(0, 0, 0),
):
    if object_type == "cube":
        bpy.ops.mesh.primitive_cube_add(location=location)

    elif object_type == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(location=location)

    elif object_type == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(location=location)

    elif object_type == "cone":
        bpy.ops.mesh.primitive_cone_add(location=location)

    elif object_type == "plane":
        bpy.ops.mesh.primitive_plane_add(location=location)

    else:
        raise ValueError(
            f"Unsupported object type: {object_type}"
        )

    obj = bpy.context.object
    obj.name = name

    return {
        "success": True,
        "object_id": obj.name,
        "type": object_type,
        "location": list(obj.location),
    }

def transform_object(
    object_id: str,
    location=None,
    rotation=None,
    scale=None,
):
    obj = bpy.data.objects.get(object_id)

    if obj is None:
        return {
            "success": False,
            "error": f"Object '{object_id}' not found"
        }

    if location is not None:
        obj.location = location

    if rotation is not None:
        obj.rotation_euler = rotation

    if scale is not None:
        obj.scale = scale

    return {
        "success": True,
        "object_id": obj.name,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
    }

def modify_geometry(
    object_id: str,
    operation: str,
    parameters: dict = None,
):
    obj = bpy.data.objects.get(object_id)

    if obj is None:
        return {
            "success": False,
            "error": f"Object '{object_id}' not found"
        }

    parameters = parameters or {}

    if operation == "bevel":

        modifier = obj.modifiers.new(
            name="Bevel",
            type="BEVEL"
        )

        modifier.width = parameters.get("width", 0.1)
        modifier.segments = parameters.get("segments", 2)

    elif operation == "subdivision":

        modifier = obj.modifiers.new(
            name="Subdivision",
            type="SUBSURF"
        )

        modifier.levels = parameters.get("levels", 2)

    elif operation == "smooth":

        for polygon in obj.data.polygons:
            polygon.use_smooth = True

    else:
        return {
            "success": False,
            "error": f"Unsupported geometry operation: {operation}"
        }

    return {
        "success": True,
        "object_id": obj.name,
        "operation": operation,
    }

def modify_geometry(
    object_id: str,
    operation: str,
    parameters: dict = None,
):
    obj = bpy.data.objects.get(object_id)

    if obj is None:
        return {
            "success": False,
            "error": f"Object '{object_id}' not found"
        }

    parameters = parameters or {}

    if operation == "bevel":

        modifier = obj.modifiers.new(
            name="Bevel",
            type="BEVEL"
        )

        modifier.width = parameters.get("width", 0.1)
        modifier.segments = parameters.get("segments", 2)

    elif operation == "subdivision":

        modifier = obj.modifiers.new(
            name="Subdivision",
            type="SUBSURF"
        )

        modifier.levels = parameters.get("levels", 2)

    elif operation == "smooth":

        for polygon in obj.data.polygons:
            polygon.use_smooth = True

    else:
        return {
            "success": False,
            "error": f"Unsupported geometry operation: {operation}"
        }

    return {
        "success": True,
        "object_id": obj.name,
        "operation": operation,
    }

def assign_material(
    object_id: str,
    material_name: str,
    base_color=(0.8, 0.8, 0.8, 1.0),
    roughness=0.5,
    metallic=0.0,
):
    obj = bpy.data.objects.get(object_id)

    if obj is None:
        return {
            "success": False,
            "error": f"Object '{object_id}' not found"
        }

    material = bpy.data.materials.get(material_name)

    if material is None:
        material = bpy.data.materials.new(material_name)

    material.use_nodes = True

    bsdf = material.node_tree.nodes.get("Principled BSDF")

    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic

    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material

    return {
        "success": True,
        "object_id": object_id,
        "material": material_name,
    }

def parent_object(
    child_id: str,
    parent_id: str,
):
    child = bpy.data.objects.get(child_id)
    parent = bpy.data.objects.get(parent_id)

    if child is None:
        return {
            "success": False,
            "error": f"Child '{child_id}' not found"
        }

    if parent is None:
        return {
            "success": False,
            "error": f"Parent '{parent_id}' not found"
        }

    child.parent = parent

    return {
        "success": True,
        "child": child_id,
        "parent": parent_id,
    }

def delete_object(object_id: str):
    obj = bpy.data.objects.get(object_id)

    if obj is None:
        return {
            "success": False,
            "error": f"Object '{object_id}' not found"
        }

    bpy.data.objects.remove(
        obj,
        do_unlink=True
    )

    return {
        "success": True,
        "deleted": object_id
    }


def inspect_scene():
    objects = []

    for obj in bpy.context.scene.objects:

        object_info = {
            "id": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        }

        if obj.type == "MESH":
            object_info["dimensions"] = list(obj.dimensions)

        if obj.parent:
            object_info["parent"] = obj.parent.name

        if obj.type == "MESH":
            object_info["materials"] = [
                material.name
                for material in obj.data.materials
                if material
            ]

        objects.append(object_info)

    return {
        "success": True,
        "object_count": len(objects),
        "objects": objects,
    }