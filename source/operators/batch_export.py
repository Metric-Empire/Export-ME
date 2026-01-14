import bpy
from bpy.types import Operator

from .export import FBXExporter


IGNORED_UV_NAMES = {"Decal UVs", "UVMap", "Atlas UVs"}


def has_multiple_uv_sets(obj) -> bool:
    if obj.type != "MESH" or len(obj.data.uv_layers) <= 1:
        return False
    return any(uv.name not in IGNORED_UV_NAMES for uv in obj.data.uv_layers)


def any_child_has_multiple_uvs(obj) -> bool:
    return any(has_multiple_uv_sets(child) for child in obj.children)


class N_OT_BatchExport(Operator):
    bl_idname = "object.bat_export"
    bl_label = "Batch Export"
    bl_description = "Export selected objects as FBX"
    bl_options = {"REGISTER"}

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "MESH" and (has_multiple_uv_sets(obj) or any_child_has_multiple_uvs(obj)):
                self.report({"WARNING"}, "Some objects have more than one UV set")
                break

        exporter = FBXExporter(context)
        path = exporter.export()

        self.report({"INFO"}, f"Exported to {path.as_posix()}")
        return {"FINISHED"}
