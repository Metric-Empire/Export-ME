import bpy
from bpy.types import Operator


class N_OT_SmartDecal_Op(Operator):
    bl_idname = "object.smart_decal"
    bl_label = "Combine Decal"
    bl_description = "Automatically combine and transfer to atlas decals"

    def execute(self, context):
        selected_objs = context.selected_objects
        original_cursor_location = context.scene.cursor.location.copy()

        for selected_obj in selected_objs:
            # get all child objects starting with "ME"
            child_objs = [
                obj for obj in selected_obj.children if obj.name.startswith("ME")
            ]

            # combine the child objects into a single object
            if len(child_objs) >= 1:
                bpy.ops.object.select_all(action="DESELECT")
                for obj in child_objs:
                    obj.select_set(True)
                context.view_layer.objects.active = child_objs[0]
                bpy.ops.machin3.use_atlas()

            material_objs = {}

            # iterate through child objects and group them by material
            for obj in selected_obj.children:
                for slot in obj.material_slots:
                    if slot.material:
                        if slot.material.name in material_objs:
                            material_objs[slot.material.name].append(obj)
                        else:
                            material_objs[slot.material.name] = [obj]

            # iterate through groups of objects and join them
            for material_name, objs in material_objs.items():
                if len(objs) >= 1:
                    # combine the child objects into a single object
                    bpy.ops.object.select_all(action="DESELECT")
                    for obj in objs:
                        obj.select_set(True)
                    context.view_layer.objects.active = objs[0]
                    bpy.ops.object.join()

                    new_obj = bpy.context.object

                    bpy.ops.object.transform_apply(
                        location=True, rotation=True, scale=True
                    )

                    small_material_name = material_name.lstrip("ME_")

                    # Rename new mesh
                    parent_name = selected_obj.name
                    new_name = f"{parent_name}_{small_material_name}"
                    new_obj.name = new_name

                    # Set Pivot point
                    bpy.ops.object.select_all(action="DESELECT")
                    selected_obj.select_set(True)
                    bpy.context.view_layer.objects.active = selected_obj
                    bpy.ops.view3d.snap_cursor_to_selected()
                    bpy.ops.object.select_all(action="DESELECT")
                    new_obj.select_set(True)
                    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

            bpy.ops.object.select_all(action="DESELECT")
            selected_obj.select_set(True)
            bpy.context.view_layer.objects.active = selected_obj

        context.scene.cursor.location = original_cursor_location

        self.report({"INFO"}, "Decal Mesh Created")
        return {"FINISHED"}
