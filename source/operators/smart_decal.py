from typing import List, Dict
import bpy
from bpy.types import Operator, Context, Object, Material, MaterialSlot


class N_OT_SmartDecal(Operator):
    bl_idname = "object.smart_decal"
    bl_label = "Combine Decal"
    bl_description = "Automatically combine and transfer decals to atlas"

    def execute(self, context: Context) -> set[str]:
        original_cursor = context.scene.cursor.location.copy()

        for obj in context.selected_objects:
            self._process_object(context, obj)

        context.scene.cursor.location = original_cursor
        self.report({"INFO"}, "Decal mesh created")
        return {"FINISHED"}

    def _process_object(self, context: Context, obj: Object) -> None:
        me_children: List[Object] = [child for child in obj.children if child.name.startswith("ME")]

        if me_children:
            bpy.ops.object.select_all(action="DESELECT")
            for child in me_children:
                child.select_set(True)
            context.view_layer.objects.active = me_children[0]
            bpy.ops.machin3.use_atlas()

        material_groups = self._group_by_material(obj)

        for material_name, objects in material_groups.items():
            if not objects:
                continue

            bpy.ops.object.select_all(action="DESELECT")
            for child in objects:
                child.select_set(True)
            context.view_layer.objects.active = objects[0]
            bpy.ops.object.join()

            new_obj = context.object
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            clean_name = material_name.lstrip("ME_")
            if new_obj:
                new_obj.name = f"{obj.name}_{clean_name}"
                self._set_origin_to_parent(context, obj, new_obj)

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        context.view_layer.objects.active = obj

    def _group_by_material(self, obj: Object) -> Dict[str, List[Object]]:
        groups: Dict[str, List[Object]] = {}
        for child in obj.children:
            slot: MaterialSlot
            for slot in child.material_slots:
                mat: Material = slot.material
                if mat:
                    groups.setdefault(mat.name, []).append(child)
        return groups

    def _set_origin_to_parent(self, context: Context, parent: Object, child: Object) -> None:
        bpy.ops.object.select_all(action="DESELECT")
        parent.select_set(True)
        context.view_layer.objects.active = parent
        bpy.ops.view3d.snap_cursor_to_selected()

        bpy.ops.object.select_all(action="DESELECT")
        child.select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
