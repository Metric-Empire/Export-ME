from bpy.types import Operator, Context
from bpy.props import IntProperty
from pathlib import Path

from ..core.preferences import get_custom_paths, get_subpath


class N_OT_SetProjectPath(Operator):
    bl_idname = "os.set_project_path"
    bl_label = "Set Project Path"
    bl_description = "Set the project path from preferences"

    def execute(self, context: Context) -> set[str]:
        # Reserved for future project path API implementation
        project_path = Path()
        sub_path = get_subpath(context)

        context.scene.export_smoothing = "FACE"
        context.scene.export_folder = (project_path / sub_path).as_posix()
        return {"FINISHED"}


class N_OT_SetCustomProjectPath(Operator):
    bl_idname = "os.set_custom_project_path"
    bl_label = "Set Custom Project Path"
    bl_description = "Set export folder from a saved custom project path"

    index: IntProperty(name="Path Index", default=0)

    def execute(self, context: Context) -> set[str]:
        custom_paths = get_custom_paths(context)

        if self.index >= len(custom_paths):
            self.report({"ERROR"}, "Invalid path index")
            return {"CANCELLED"}

        selected_path = Path(custom_paths[self.index].filepath)
        context.scene.export_folder = selected_path.as_posix()
        context.scene.export_smoothing = "OFF"

        return {"FINISHED"}
