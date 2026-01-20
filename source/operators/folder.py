from bpy.types import Operator, Context
from bpy.props import StringProperty
from pathlib import Path


class N_OT_SelectFolder(Operator):
    bl_idname = "os.select_folder"
    bl_label = "Select Folder"

    folder_path: StringProperty()

    def execute(self, context: Context) -> set[str]:
        context.scene.export_folder = self.folder_path
        return {"FINISHED"}


class N_OT_ParentFolder(Operator):
    bl_idname = "os.parent_folder"
    bl_label = "Parent Folder"
    bl_description = "Navigate to the parent folder"

    def execute(self, context: Context) -> set[str]:
        parent = Path(context.scene.export_folder).resolve().parent
        context.scene.export_folder = parent.as_posix()
        return {"FINISHED"}


class N_OT_NewFolder(Operator):
    bl_idname = "os.new_folder"
    bl_label = "New Folder"
    bl_description = "Create a new folder in the current directory"

    def execute(self, context: Context) -> set[str]:
        folder_name = context.scene.new_folder_name
        if not folder_name:
            self.report({"ERROR"}, "Folder name cannot be empty")
            return {"CANCELLED"}

        new_path = Path(context.scene.export_folder) / folder_name
        try:
            new_path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            self.report({"WARNING"}, "Folder already exists")
        except OSError as e:
            self.report({"ERROR"}, f"Failed to create folder: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}
