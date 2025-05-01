import bpy
from bpy.types import Operator
from .export_ot import N_export


class N_OT_bat_export(Operator):
    bl_idname = "object.bat_export"
    bl_label = "Batch Export"
    bl_description = "Export selected objects as fbx"
    bl_options = {"REGISTER"}

    def show_message(self, message):
        self.report({"WARNING"}, message)

    def execute(self, context):
        def hasMultipleUVSets(obj):
            if obj.type == "MESH":
                uv_map_count = len(obj.data.uv_layers)
                if uv_map_count > 1:
                    for uv_layer in obj.data.uv_layers:
                        if uv_layer.name != "Decal UVs" and uv_layer.name != "UVMap" and uv_layer.name != "Atlas UVs":
                            return True

        def anyChildHasMultipleUVSets(obj):
            for child in obj.children:
                # if child.type == 'MESH':
                if hasMultipleUVSets(child):
                    return True

        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if hasMultipleUVSets(obj) or anyChildHasMultipleUVSets(obj):
                    self.show_message("Some object have more than one UV set")
                    break

        bat_export = N_export(context)
        path = bat_export.do_export(context)

        self.report({"INFO"}, f"Exported to {path}")

        return {"FINISHED"}
