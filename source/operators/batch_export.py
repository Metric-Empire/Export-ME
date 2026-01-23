from typing import Set
from bpy.types import Operator, Context, Object, Mesh
from pathlib import Path

from .export import FBXExporter
from ..core.preferences import add_recent_export_path, get_game_engine_for_path
from ..core.types import ExportSettings


IGNORED_UV_NAMES: Set[str] = {"Decal UVs", "UVMap", "Atlas UVs"}


def has_multiple_uv_sets(obj: Object) -> bool:
    if obj.type != "MESH":
        return False
    mesh: Mesh = obj.data
    if len(mesh.uv_layers) <= 1:
        return False
    return any(uv.name not in IGNORED_UV_NAMES for uv in mesh.uv_layers)


def any_child_has_multiple_uvs(obj: Object) -> bool:
    return any(has_multiple_uv_sets(child) for child in obj.children)


class N_OT_BatchExport(Operator):
    bl_idname = "object.bat_export"
    bl_label = "Batch Export"
    bl_description = "Export selected objects as FBX"
    bl_options = {"REGISTER"}

    def execute(self, context: Context) -> set[str]:
        for obj in context.selected_objects:
            if obj.type == "MESH" and (has_multiple_uv_sets(obj) or any_child_has_multiple_uvs(obj)):
                self.report({"WARNING"}, "Some objects have more than one UV set")
                break

        import bpy
        export_folder_str = context.scene.export_folder
        if export_folder_str.startswith("//"):
            export_folder = Path(bpy.path.abspath(export_folder_str)).resolve()
        else:
            export_folder = Path(export_folder_str)
        
        game_engine = get_game_engine_for_path(context, export_folder)
        
        exporter = FBXExporter(context, game_engine)
        path = exporter.export()

        if path:
            add_recent_export_path(context, str(path.parent))
            self.report({"INFO"}, f"Exported to {path.as_posix()}")
        return {"FINISHED"}
