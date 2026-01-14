from typing import Dict, List, Optional, Literal, TYPE_CHECKING
import bpy
import bmesh
from pathlib import Path
from dataclasses import dataclass, field
from bpy.types import Context, Object, Modifier, Mesh

from ..core.types import ExportSettings
from ..core.paths import get_children, get_object_location, set_object_location
from .tools import fix_colliders

if TYPE_CHECKING:
    from mathutils import Vector


@dataclass
class MaterialBackup:
    mat_faces: Dict[int, int] = field(default_factory=dict)
    materials: List[bpy.types.Material] = field(default_factory=list)


class FBXExporter:
    def __init__(self, context: Context) -> None:
        self.context = context
        self.settings = ExportSettings.from_scene(context.scene)
        self.export_objects: List[Object] = list(context.selected_objects)
        self._material_backup = MaterialBackup()

    def export(self) -> Optional[Path]:
        bpy.ops.object.mode_set(mode="OBJECT")

        if self.settings.purge_data:
            self._purge_orphans()

        exported_path: Optional[Path] = None
        for obj in self.export_objects:
            exported_path = self._export_object(obj)

        return exported_path

    def _export_object(self, obj: Object) -> Path:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(state=True)

        original_location: Optional["Vector"] = self._center_object(obj) if self.settings.center_transform else None

        for child in get_children(obj):
            child.select_set(state=True)

        materials_removed: Optional[bool] = self._remove_materials(obj) if self.settings.one_material_id else None

        if self.settings.triangulate:
            self._add_triangulate(obj)

        if self.settings.black_vertex:
            self._set_vertex_colors(obj)

        if self.settings.fix_collider:
            fix_colliders(obj)

        if self.settings.no_decal_uv:
            self._remove_decal_uvs(obj)

        if self.settings.rename_dot:
            self._rename_dots(obj)

        export_path = self._write_fbx(obj)

        self._restore_object(obj, original_location, materials_removed)

        return export_path

    def _center_object(self, obj: Object) -> "Vector":
        loc = get_object_location(obj)
        set_object_location(obj, (0, 0, 0))
        return loc

    def _remove_materials(self, obj: Object) -> Optional[bool]:
        if obj.type == "ARMATURE" or len(obj.data.materials) <= 1:
            return None

        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)

        self._material_backup.mat_faces = {face.index: face.material_index for face in bm.faces}

        bpy.ops.object.mode_set(mode="OBJECT")
        self._material_backup.materials.clear()

        mat_count = len(obj.data.materials)
        for idx in range(mat_count):
            self._material_backup.materials.append(obj.data.materials[0])
            if idx < mat_count - 1:
                obj.data.materials.pop(index=0)

        return True

    def _restore_materials(self, obj: Object) -> None:
        obj.data.materials.clear()
        for mat in self._material_backup.materials:
            obj.data.materials.append(mat)

        obj.data.update()

        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)

        for face in bm.faces:
            face.material_index = self._material_backup.mat_faces[face.index]

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode="OBJECT")

    def _add_triangulate(self, obj: Object) -> None:
        for child in get_children(obj):
            mod: Modifier = child.modifiers.new(name="ME_Triangulate", type="TRIANGULATE")
            mod.min_vertices = 5
            mod.keep_custom_normals = True

    def _remove_triangulate(self, obj: Object) -> None:
        for child in get_children(obj):
            mod = child.modifiers.get("ME_Triangulate")
            if mod:
                child.modifiers.remove(mod)

    def _set_vertex_colors(self, obj: Object) -> None:
        def apply_black_vertex_color(mesh_obj: Object) -> None:
            if mesh_obj.type != "MESH" or not mesh_obj.data:
                return
            mesh: Mesh = mesh_obj.data
            if mesh.vertex_colors or mesh.color_attributes:
                return

            mesh.vertex_colors.new(name="Col")
            color_layer = mesh.vertex_colors.active
            if not color_layer:
                return

            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    color_layer.data[loop_index].color = (0.0, 0.0, 0.0, 0.0)

        apply_black_vertex_color(obj)
        for child in get_children(obj):
            apply_black_vertex_color(child)

    def _remove_decal_uvs(self, obj: Object) -> None:
        uvs_to_remove = {"Decal UVs"}

        for child in get_children(obj):
            if child.type != "MESH" or not child.data:
                continue
            mesh: Mesh = child.data
            for uv in list(mesh.uv_layers):
                if uv.name in uvs_to_remove:
                    mesh.uv_layers.remove(uv)

    def _rename_dots(self, obj: Object) -> None:
        if "." in obj.name:
            obj.name = obj.name.replace(".", "_")

        for child in get_children(obj):
            if "." in child.name:
                child.name = child.name.replace(".", "_")

    def _write_fbx(self, obj: Object) -> Path:
        object_types: set[Literal["MESH", "ARMATURE"]] = {"MESH"}
        if self.settings.export_animations:
            object_types.add("ARMATURE")

        object_name = self.settings.custom_name or obj.name
        filepath = self.settings.export_folder / f"{object_name}.fbx"

        smoothing: Literal["OFF", "FACE", "EDGE"] = self.settings.smoothing

        bpy.ops.export_scene.fbx(
            check_existing=False,
            filepath=filepath.as_posix(),
            filter_glob="*.fbx",
            use_selection=True,
            object_types=object_types,
            bake_anim=self.settings.export_animations,
            bake_anim_use_all_bones=self.settings.export_animations,
            bake_anim_use_all_actions=self.settings.export_animations,
            use_armature_deform_only=True,
            bake_space_transform=self.settings.apply_transform,
            mesh_smooth_type=smoothing,
            add_leaf_bones=True,
            path_mode="ABSOLUTE",
            axis_up="Z",
            axis_forward="X",
        )

        return filepath

    def _restore_object(
        self,
        obj: Object,
        original_location: Optional["Vector"],
        materials_removed: Optional[bool],
    ) -> None:
        if materials_removed:
            self._restore_materials(obj)

        if original_location is not None:
            set_object_location(obj, original_location)

        if self.settings.triangulate:
            self._remove_triangulate(obj)

    def _purge_orphans(self) -> None:
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
