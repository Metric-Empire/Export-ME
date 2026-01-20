from bpy.types import Operator, Context
from bpy.props import IntProperty
from pathlib import Path

from ..core.preferences import get_custom_paths, get_preferences


class N_OT_SetProjectPath(Operator):
    bl_idname = "os.set_project_path"
    bl_label = "Set Project Path"
    bl_description = "Set the project path from preferences"

    def execute(self, context: Context) -> set[str]:
        # Reserved for future project path API implementation
        project_path = Path()

        context.scene.export_smoothing = "FACE"
        context.scene.export_folder = project_path.as_posix()
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

        # Update selected project enum
        context.scene.selected_project_enum = str(self.index)

        selected_path = Path(custom_paths[self.index].filepath)
        context.scene.export_folder = selected_path.as_posix()
        context.scene.export_smoothing = "OFF"

        return {"FINISHED"}


class N_OT_SetProjectSubpath(Operator):
    bl_idname = "os.set_project_subpath"
    bl_label = "Set Project Subpath"
    bl_description = "Set export folder to project root + subpath"

    project_index: IntProperty(name="Project Index", default=0)
    subpath_index: IntProperty(name="Subpath Index", default=0)

    def execute(self, context: Context) -> set[str]:
        prefs = get_preferences(context)

        if self.project_index >= len(prefs.custom_project_paths):
            self.report({"ERROR"}, "Invalid project index")
            return {"CANCELLED"}

        project = prefs.custom_project_paths[self.project_index]

        if self.subpath_index >= len(project.subpaths):
            self.report({"ERROR"}, "Invalid subpath index")
            return {"CANCELLED"}

        # Update selected project enum
        context.scene.selected_project_enum = str(self.project_index)

        subpath = project.subpaths[self.subpath_index]
        project_root = Path(project.filepath)
        
        if subpath.relative_path:
            full_path = project_root / subpath.relative_path
        else:
            full_path = project_root

        context.scene.export_folder = full_path.as_posix()
        context.scene.export_smoothing = "OFF"

        return {"FINISHED"}
