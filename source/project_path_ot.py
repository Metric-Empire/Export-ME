import bpy
from bpy.types import Operator
from .utils import (
    get_custom_path_prefs,
    get_subpath_prefs,
)
from bpy.props import StringProperty, IntProperty
from pyme.getset import get_project_path
from pathlib import Path


class N_OT_SetProjectPath(Operator):
    bl_idname = "os.set_project_path"
    bl_label = "Set Project Path"
    bl_description = "Set the appdata project path"

    def execute(self, context):
        project_path = get_project_path()
        print(project_path)
        sub_path = get_subpath_prefs(context)
        print(sub_path)

        print(project_path / sub_path)
        context.scene.export_smoothing = "FACE"
        context.scene.export_folder = str(project_path / sub_path)
        return {"FINISHED"}


class N_OT_SetCustomProjectPath(Operator):
    bl_idname = "os.set_custom_project_path"
    bl_label = "Set Project Custom Path"
    bl_description = "Set a custom project path"

    index: IntProperty(name="Path Index", default=0)  # type: ignore

    def execute(self, context):
        pref = get_custom_path_prefs(context)
        try:
            selected_path = Path(pref[self.index].filepath)
            context.scene.export_folder = str(selected_path)
        except IndexError:
            self.report({"ERROR"}, "Invalid path index.")
            return {"CANCELLED"}

        context.scene.export_smoothing = "OFF"

        return {"FINISHED"}


class N_OT_SelectFolder(Operator):
    bl_idname = "os.select_folder"
    bl_label = "Select Folder"

    folder_path: StringProperty()  # type: ignore

    def execute(self, context):
        print(self.folder_path)
        context.scene.export_folder = self.folder_path
        return {"FINISHED"}


class N_OT_ParentFolder(Operator):
    bl_idname = "os.parent_folder"
    bl_label = "Parent Folder"
    bl_description = "Go back to the parent folder"

    def execute(self, context):
        parent_dir = Path(context.scene.export_folder).resolve().parent
        context.scene.export_folder = str(parent_dir)
        return {"FINISHED"}


class N_OT_NewFolder(Operator):
    bl_idname = "os.new_folder"
    bl_label = "New Folder"
    bl_description = "Create a new folder in the current directory"

    def execute(self, context):
        new_folder_name = bpy.context.scene.new_folder_name
        if not new_folder_name:
            self.report({"ERROR"}, "Folder name cannot be empty.")
            return {"CANCELLED"}

        # Create the new folder in the current directory
        Path(context.scene.export_folder, new_folder_name).mkdir()
        return {"FINISHED"}
