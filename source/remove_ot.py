import bpy
from bpy.types import Operator


class N_OT_RemoveMat_All_Op(Operator):
    bl_idname = "object.remove_all_material"
    bl_label = "Remove all Mat"
    bl_description = "Remove all the material for active object"

    def execute(self, context):
        obj = context.object

        if obj.mode == "EDIT":
            bpy.ops.object.editmode_toggle()

        active = context.view_layer.objects.active

        for obj in context.selected_editable_objects:
            if obj.type == "MESH":
                context.view_layer.objects.active = obj
                obj.active_material_index = 0
                for x in range(len(obj.material_slots)):
                    bpy.ops.object.material_slot_remove({"object": obj})
                context.view_layer.objects.active = active

        self.report({"INFO"}, "All materials Removed")

        return {"FINISHED"}


class N_OT_RemoveUV_All_Op(Operator):
    bl_idname = "object.remove_all_uv"
    bl_label = "Remove all UV"
    bl_description = "Remove all the UV for active object"

    def execute(self, context):
        obj = context.object

        for obj in context.selected_editable_objects:
            if obj.type == "MESH":
                if obj.data.uv_layers:
                    while obj.data.uv_layers:
                        obj.data.uv_layers.remove(obj.data.uv_layers[0])

        self.report({"INFO"}, "All UVs Removed")

        return {"FINISHED"}


class N_OT_RemoveUV_Specific_Op(Operator):
    bl_idname = "object.remove_specific_uv"
    bl_label = "Remove Specific UV"
    bl_description = "Remove Specific UV for active object"

    def execute(self, context):
        obj = context.object
        specificuv = context.scene.specificuv
        for obj in context.selected_editable_objects:
            if obj.type == "MESH":
                specificuvmap = obj.data.uv_layers.get(specificuv)
                if specificuvmap is not None:
                    obj.data.uv_layers.remove(specificuvmap)

        self.report({"INFO"}, "Specific UVs Removed")

        return {"FINISHED"}


class N_OT_RemoveUV_NonRender_Op(Operator):
    bl_idname = "object.remove_nonrender_uv"
    bl_label = "Remove NonRender UV"
    bl_description = "Remove UV map who are not in active render for active object"

    def execute(self, context):
        obj = context.object

        for obj in context.selected_editable_objects:
            if obj.type == "MESH":
                uvs = [uv for uv in obj.data.uv_layers if not uv.active_render]
                while uvs:
                    obj.data.uv_layers.remove(uvs.pop())

        self.report({"INFO"}, "Non active UVs Removed")

        return {"FINISHED"}
