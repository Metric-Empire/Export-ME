import bpy

from bpy.types import Operator


class N_OT_OpenFolder(Operator):
    bl_idname = "object.openfolder"
    bl_label = "Open folder."
    bl_description = "Open the export folder"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.wm.path_open(filepath=str(context.scene.export_folder))
        return {"FINISHED"}
