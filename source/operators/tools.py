import bpy
from bpy.types import Operator

UE_COLLIDER_PREFIXES = ("UBX_", "USP_", "UCX_", "UCP_")


def fix_colliders(obj) -> bool:
    colliders = [child for child in obj.children if child.name.startswith(UE_COLLIDER_PREFIXES)]

    if not colliders:
        return False

    for idx, collider in enumerate(colliders, start=1):
        suffix = f"_{idx:02d}" if len(colliders) > 1 else ""
        _process_collider(collider, obj.name, suffix)

    return True


def _process_collider(collider, parent_name: str, suffix: str):
    geo_modifier = collider.modifiers.get("GeometryNodes")

    if geo_modifier:
        prefix = geo_modifier.node_group.name.split("_")[0]
        collider.name = f"{prefix}_{parent_name}{suffix}"
    else:
        collider.name = f"UCX_{parent_name}{suffix}"
        _apply_convex_hull(collider)


def _apply_convex_hull(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.convex_hull()
    bpy.ops.object.mode_set(mode="OBJECT")


class N_OT_FixColliderName(Operator):
    bl_idname = "object.fix_collider_name"
    bl_label = "Fix Collider Name"
    bl_description = "Fix collider names and ensure they are convex"

    def execute(self, context):
        any_fixed = False

        for obj in context.selected_objects:
            if fix_colliders(obj):
                any_fixed = True

        if not any_fixed:
            self.report({"WARNING"}, "No colliders found for selected objects")
            return {"CANCELLED"}

        self.report({"INFO"}, "Colliders renamed")
        return {"FINISHED"}
