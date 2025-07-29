import bpy
import math
from mathutils import Euler, Vector
from pathlib import Path
from bpy.types import Operator


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
