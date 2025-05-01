import bpy
import math
from mathutils import Euler, Vector
from pathlib import Path
from bpy.types import Operator


def set_loc_rotation(value, obj):
    rot = Euler(value, "ZYX")
    obj.rotation_euler = (obj.rotation_euler.to_matrix() @ rot.to_matrix()).to_euler(obj.rotation_mode)


def get_asset_in_lib(asset_name):
    prefs = bpy.context.preferences
    filepaths = prefs.filepaths
    asset_libraries = filepaths.asset_libraries

    for library in asset_libraries:
        if library.name == "ME Tools":
            library_path = Path(library.path)
            blend_files = [fp for fp in library_path.glob("**/*.blend") if fp.is_file()]
            for blend_file in blend_files:
                if blend_file.name == "UE_Colliders.blend":
                    with bpy.data.libraries.load(str(blend_file), link=False) as (
                        data_from,
                        data_to,
                    ):
                        data_to.objects = [asset_name]
                    appended_obj = bpy.data.objects.get(asset_name)
                    if appended_obj is not None:
                        bpy.context.collection.objects.link(appended_obj)
                    break

    return appended_obj


def fix_colliders(obj):
    ue_col_prefix = ("UBX_", "USP_", "UCX_", "UCP_")
    ue_col_obj = []
    for child in obj.children:
        if child.name.startswith(ue_col_prefix):
            ue_col_obj.append(child)

    if not ue_col_obj:
        return False

    if len(ue_col_obj) == 1:
        col = ue_col_obj[0]
        col_modifier = col.modifiers.get("GeometryNodes")

        if not col_modifier:
            col.name = f"UCX_{obj.name}"
            bpy.ops.object.select_all(action="DESELECT")
            col.select_set(True)
            bpy.context.view_layer.objects.active = col
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.convex_hull()
            bpy.ops.object.mode_set(mode="OBJECT")
        else:
            node_group_prefix = col_modifier.node_group.name.split("_")[0]
            col.name = f"{node_group_prefix}_{obj.name}"
    else:
        for i, col in enumerate(ue_col_obj):
            i += 1
            if i < 10:
                i = f"0{i}"

            col_modifier = col.modifiers.get("GeometryNodes")

            if not col_modifier:
                col.name = f"UCX_{obj.name}_{i}"
                bpy.ops.object.select_all(action="DESELECT")
                col.select_set(True)
                bpy.context.view_layer.objects.active = col
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.convex_hull()
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                node_group_prefix = col_modifier.node_group.name.split("_")[0]
                col.name = f"{node_group_prefix}_{obj.name}_{i}"

    return True


# TODO: Make generic function for collider creation
class N_OT_SetBoxCollider_Op(Operator):
    bl_idname = "object.set_box_collider"
    bl_label = "Set Box Collider"
    bl_description = "Add a box collider to the selected object"

    def execute(self, context):
        for obj in context.selected_objects:
            asset_name = "UBX_Collider_Box"
            appended_obj = get_asset_in_lib(asset_name)

            if not obj:
                self.report({"WARNING"}, "No object selected")
                return {"CANCELLED"}

            if not appended_obj:
                self.report(
                    {"WARNING"},
                    "Collider object not found, make sure the ME Tools library is correctly set and up to date",
                )
                return {"CANCELLED"}

            dims = obj.dimensions
            bbox_corners = [Vector(c) for c in obj.bound_box]
            center_local = sum(bbox_corners, Vector()) / len(bbox_corners)

            appended_obj.location = center_local
            appended_obj.scale = (dims.x, dims.y, dims.z)
            appended_obj.display_type = "WIRE"
            appended_obj.name = f"UBX_{obj.name}"
            appended_obj.parent = obj
            appended_obj.matrix_parent_inverse = obj.matrix_world.inverted()

        self.report({"INFO"}, "Collider Set")
        return {"FINISHED"}


class N_OT_SetSphereCollider_Op(Operator):
    bl_idname = "object.set_sphere_collider"
    bl_label = "Set Sphere Collider"
    bl_description = "Add a sphere collider to the selected object"

    def execute(self, context):
        for obj in context.selected_objects:
            asset_name = "USP_Collider_Sphere"
            appended_obj = get_asset_in_lib(asset_name)

            if not obj:
                self.report({"WARNING"}, "No object selected")
                return {"CANCELLED"}

            if not appended_obj:
                self.report(
                    {"WARNING"},
                    "Collider object not found, make sure the ME Tools library is correctly set and up to date",
                )
                return {"CANCELLED"}

            dims = obj.dimensions
            bbox_corners = [Vector(c) for c in obj.bound_box]
            center_local = sum(bbox_corners, Vector()) / len(bbox_corners)

            if dims.x > dims.y and dims.x > dims.z:
                x = dims.x
                y = dims.x
                z = dims.x
            elif dims.y > dims.x and dims.y > dims.z:
                x = dims.y
                y = dims.y
                z = dims.y
            else:
                x = dims.z
                y = dims.z
                z = dims.z

            appended_obj.location = center_local
            appended_obj.scale = (x, y, z)
            appended_obj.display_type = "WIRE"
            appended_obj.name = f"USP_{obj.name}"
            appended_obj.parent = obj
            appended_obj.matrix_parent_inverse = obj.matrix_world.inverted()

        self.report({"INFO"}, "Collider Set")
        return {"FINISHED"}


class N_OT_SetCylinderCollider_Op(Operator):
    bl_idname = "object.set_cylinder_collider"
    bl_label = "Set Cylinder Collider"
    bl_description = "Add a cylinder collider to the selected object"

    def execute(self, context):
        for obj in context.selected_objects:
            asset_name = "UCX_Collider_Cylinder"
            appended_obj = get_asset_in_lib(asset_name)

            if not obj:
                self.report({"WARNING"}, "No object selected")
                return {"CANCELLED"}

            if not appended_obj:
                self.report(
                    {"WARNING"},
                    "Collider object not found, make sure the ME Tools library is correctly set and up to date",
                )
                return {"CANCELLED"}

            dims = obj.dimensions
            bbox_corners = [Vector(c) for c in obj.bound_box]
            center_local = sum(bbox_corners, Vector()) / len(bbox_corners)

            if dims.x > dims.y:
                d = dims.x
            else:
                d = dims.y

            if dims.x > dims.y and dims.x > dims.z:
                rx = 0
                ry = math.radians(90)
                rz = 0
                h = dims.x
                if dims.y > dims.z:
                    d = dims.y
                else:
                    d = dims.z
            elif dims.y > dims.x and dims.y > dims.z:
                rx = math.radians(90)
                ry = 0
                rz = 0
                h = dims.y
                if dims.x > dims.z:
                    d = dims.x
                else:
                    d = dims.z
            else:
                rx = 0
                ry = 0
                rz = 0
                h = dims.z
                if dims.x > dims.y:
                    d = dims.x
                else:
                    d = dims.y

            appended_obj.location = center_local
            appended_obj.rotation_euler = (rx, ry, rz)
            appended_obj.scale = (d, d, h)
            appended_obj.display_type = "WIRE"
            appended_obj.name = f"UCX_{obj.name}"
            appended_obj.parent = obj
            appended_obj.matrix_parent_inverse = obj.matrix_world.inverted()

        self.report({"INFO"}, "Collider Set")
        return {"FINISHED"}


class N_OT_SetCapsuleCollider_Op(Operator):
    bl_idname = "object.set_capsule_collider"
    bl_label = "Set Capsule Collider"
    bl_description = "Add "

    def execute(self, context):
        for obj in context.selected_objects:
            asset_name = "UCP_Collider_Capsule"
            appended_obj = get_asset_in_lib(asset_name)
            col_modifier = appended_obj.modifiers.get("GeometryNodes")

            if not obj:
                self.report({"WARNING"}, "No object selected")
                return {"CANCELLED"}

            if not appended_obj:
                self.report(
                    {"WARNING"},
                    "Collider object not found, make sure the ME Tools library is correctly set and up to date",
                )
                return {"CANCELLED"}

            dims = obj.dimensions
            bbox_corners = [Vector(c) for c in obj.bound_box]
            center_local = sum(bbox_corners, Vector()) / len(bbox_corners)

            if dims.x > dims.y:
                r = dims.x / 2
            else:
                r = dims.y / 2

            if dims.x > dims.y and dims.x > dims.z:
                rx = 0
                ry = math.radians(90)
                rz = 0
                h = dims.x
                if dims.y > dims.z:
                    r = dims.y / 2
                else:
                    r = dims.z / 2
            elif dims.y > dims.x and dims.y > dims.z:
                rx = math.radians(90)
                ry = 0
                rz = 0
                h = dims.y
                if dims.x > dims.z:
                    r = dims.x / 2
                else:
                    r = dims.z / 2
            else:
                rx = 0
                ry = 0
                rz = 0
                h = dims.z
                if dims.x > dims.y:
                    r = dims.x / 2
                else:
                    r = dims.y / 2

            col_modifier["Socket_2"] = r
            col_modifier["Socket_3"] = h
            appended_obj.location = center_local
            appended_obj.rotation_euler = (rx, ry, rz)
            appended_obj.display_type = "WIRE"
            appended_obj.name = f"UCP_{obj.name}"
            appended_obj.parent = obj
            appended_obj.matrix_parent_inverse = obj.matrix_world.inverted()

            # Refresh the object
            obj.update_tag()
            bpy.context.view_layer.update()

        self.report({"INFO"}, "Collider Set")
        return {"FINISHED"}


class N_OT_SetConvexCollider_Op(Operator):
    bl_idname = "object.set_convex_collider"
    bl_label = "Set Convex Collider"
    bl_description = "Add a convex collider to the selected object"

    def invoke(self, context, event):
        if event.shift:
            for obj in context.selected_objects:
                asset_name = "UCX_Collider_Convex"
                appended_obj = get_asset_in_lib(asset_name)

                if not obj:
                    self.report({"WARNING"}, "No object selected")
                    return {"CANCELLED"}

                if not appended_obj:
                    self.report(
                        {"WARNING"},
                        "Collider object not found, make sure the ME Tools library is correctly set and up to date",
                    )
                    return {"CANCELLED"}

                dims = obj.dimensions
                bbox_corners = [Vector(c) for c in obj.bound_box]
                center_local = sum(bbox_corners, Vector()) / len(bbox_corners)

                appended_obj.location = center_local
                appended_obj.scale = (dims.x, dims.y, dims.z)
                appended_obj.display_type = "WIRE"
                appended_obj.name = f"UCX_{obj.name}"
                appended_obj.parent = obj
                appended_obj.matrix_parent_inverse = obj.matrix_world.inverted()

        else:
            for obj in context.selected_objects:
                bpy.ops.object.duplicate()
                col = context.active_object
                bpy.ops.object.select_all(action="DESELECT")
                col.select_set(True)
                bpy.context.view_layer.objects.active = col
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.convex_hull()
                bpy.ops.object.mode_set(mode="OBJECT")

                col.display_type = "WIRE"
                col.name = f"UCX_{obj.name}"
                col.parent = obj
                col.matrix_parent_inverse = obj.matrix_world.inverted()

        self.report({"INFO"}, "Collider Set")
        return {"FINISHED"}

    def execute(self, context):
        return self.invoke(context, None)


class N_OT_FixColliderName_Op(Operator):
    bl_label = "Fix Collider Name"
    bl_idname = "object.fix_collider_name"
    bl_description = "Fix the collider name"

    def execute(self, context):
        for obj in context.selected_objects:
            is_fixed = fix_colliders(obj)

            if not is_fixed:
                self.report({"WARNING"}, "No collider found for the selected objects")
                return {"CANCELLED"}

        self.report({"INFO"}, "Collider Renamed")
        return {"FINISHED"}
