import bpy
import bmesh
from .utils import *
from .tools_ot import fix_colliders
from pathlib import Path


class N_export:
    def __init__(self, context):
        self.context = context
        self.export_folder = context.scene.export_folder
        if self.export_folder.startswith("//"):
            self.export_folder = bpy.path.abspath(context.scene.export_folder).resolve()
        print(f"Export to: {self.export_folder}")
        self.custom_name = context.scene.custom_name
        self.center_transform = context.scene.center_transform
        self.apply_transform = context.scene.apply_transform
        self.one_material_id = context.scene.one_material_id
        self.no_decal_uv = context.scene.no_decal_uv
        self.rename_dot = context.scene.rename_dot
        self.purge_data = context.scene.purge_data
        self.triangulate = context.scene.triangulate
        self.fix_collider = context.scene.fix_collider
        self.export_objects = context.selected_objects
        self.black_vertex = context.scene.black_vertex
        self.export_animations = context.scene.export_animations
        self.mat_faces = {}
        self.materials = []

    def do_center(self, obj):
        loc = get_object_loc(obj)
        set_object_to_loc(obj, (0, 0, 0))
        return loc

    def remove_materials(self, obj):
        if obj.type == "ARMATURE":
            return None

        mat_count = len(obj.data.materials)

        if mat_count > 1:
            # Save material ids for faces
            bpy.ops.object.mode_set(mode="EDIT")
            bm = bmesh.from_edit_mesh(obj.data)

            for face in bm.faces:
                self.mat_faces[face.index] = face.material_index

            # Save and remove materials except the last one
            # so that we keep this as material id
            bpy.ops.object.mode_set(mode="OBJECT")
            self.materials.clear()

            for idx in range(mat_count):
                self.materials.append(obj.data.materials[0])
                if idx < mat_count - 1:
                    obj.data.materials.pop(index=0)

            return True
        else:
            return None

    # Remove all the orphans data before exporting
    def purge_file_data(self):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    # Remove decal uv
    def remove_decal_uv(self, obj):
        uvs_to_rem = ["Decal UVs"]

        def remove_uv(obj):
            if obj.type == "MESH":
                for uv in obj.data.uv_layers:
                    if uv.name in uvs_to_rem:
                        obj.data.uv_layers[uv.name].active = True
                        obj.data.uv_layers.remove(uv)

        for child in get_children(obj):
            remove_uv(child)

    # Replace dot by underscore
    def rename_dot_in_name(self, obj):
        if any("." in child.name for child in get_children(obj)):
            for child in get_children(obj):
                child.name = child.name.replace(".", "_")
        if "." in obj.name:
            obj.name = obj.name.replace(".", "_")

    # Add triangulate
    def add_triangulate(self, obj):
        def add_triangulate_modifier(obj):
            obj.modifiers.new(name="ME_Triangulate", type="TRIANGULATE")
            obj.modifiers["ME_Triangulate"].min_vertices = 5
            obj.modifiers["ME_Triangulate"].keep_custom_normals = True

        for child in get_children(obj):
            add_triangulate_modifier(child)

        return True

    # Set vertex color to black
    def set_vertex_color(self, obj):
        def set_vertex_color_black(obj):
            mesh = obj.data
            if mesh.vertex_colors or mesh.color_attributes:
                return

            mesh.vertex_colors.new(name="Col")
            color_layer = mesh.vertex_colors.active

            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    color_layer.data[loop_index].color = (0.0, 0.0, 0.0, 0.0)

        set_vertex_color_black(obj)
        for child in get_children(obj):
            set_vertex_color_black(child)

    # Undo function
    # Remove Triangulate
    def remove_triangulate(self, obj):
        def remove_triangulate_modifier(obj):
            mod = obj.modifiers.get("ME_Triangulate")
            if mod:
                obj.modifiers.remove(mod)

        for child in get_children(obj):
            remove_triangulate_modifier(child)

    # Restore the materials for the object
    def restore_materials(self, obj):
        obj.data.materials.clear()
        for mat in self.materials:
            obj.data.materials.append(mat)

        obj.data.update()

        # Reassign the material ids to the faces of the mesh
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)

        for face in bm.faces:
            mat_index = self.mat_faces[face.index]
            face.material_index = mat_index

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode="OBJECT")

    # Export FBX
    def do_export(self, context) -> Path:
        materials_removed = None
        triangulate_modif = None
        old_pos = None

        bpy.ops.object.mode_set(mode="OBJECT")

        # File processing before exporting
        if self.purge_data:
            self.purge_file_data()

        # Asset Processing before exporting
        for obj in self.export_objects:
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(state=True)

            # Center selected object
            old_pos = self.do_center(obj)

            # Select children if exist
            for child in get_children(obj):
                child.select_set(state=True)

            # Remove materials except the last one
            if self.one_material_id:
                materials_removed = self.remove_materials(obj)

            # Add triangulate modifier
            if self.triangulate:
                triangulate_modif = self.add_triangulate(obj)

            # Set vertex color to black
            if self.black_vertex:
                self.set_vertex_color(obj)

            # Fix colliders name and make sure they are convex
            if self.fix_collider:
                fix_colliders(obj)

            # Remove Decal UV
            if self.no_decal_uv:
                self.remove_decal_uv(obj)

            # Replace dot by underscore
            if self.rename_dot:
                self.rename_dot_in_name(obj)

            ex_object_types = {"MESH"}

            if self.export_animations:
                ex_object_types.add("ARMATURE")

            object_name = obj.name

            if self.custom_name:
                object_name = self.custom_name

            # Export the selected object as fbx
            bpy.ops.export_scene.fbx(
                check_existing=False,
                filepath=str(Path(self.export_folder) / Path(f"{object_name}.fbx")),
                filter_glob="*.fbx",
                use_selection=True,
                object_types=ex_object_types,
                bake_anim=self.export_animations,
                bake_anim_use_all_bones=self.export_animations,
                bake_anim_use_all_actions=self.export_animations,
                use_armature_deform_only=True,
                bake_space_transform=self.apply_transform,
                mesh_smooth_type=self.context.scene.export_smoothing,
                add_leaf_bones=True,
                path_mode="ABSOLUTE",
                axis_up="Z",
                axis_forward="X",
            )

            if materials_removed is not None:
                self.restore_materials(obj)

            if old_pos is not None:
                set_object_to_loc(obj, old_pos)

            if triangulate_modif is not None:
                self.remove_triangulate(obj)

        return Path(self.export_folder) / Path(f"{object_name}.fbx")
