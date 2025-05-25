import bpy
from bpy.types import Panel
from . import __package__ as base_package

from pathlib import Path


class N_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Fbx export"
    bl_category = "Metric"
    bl_idname = "N_PT_Panel"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        project_name = ""
        prefs = context.preferences.addons[base_package].preferences

        def hasMultipleUVSets(obj):
            uv_map_count = len(obj.data.uv_layers)
            if uv_map_count > 1:
                for uv_layer in obj.data.uv_layers:
                    if uv_layer.name != "Decal UVs" and uv_layer.name != "UVMap" and uv_layer.name != "Atlas UVs":
                        return True

        def anyChildHasMultipleUVSets(obj):
            for child in obj.children:
                if child.type == "MESH" and hasMultipleUVSets(child):
                    return True

        layout = self.layout

        row = layout.row()
        col = layout.column()

        if prefs.use_project or prefs.custom_project_paths:
            row.label(text="Projects:")

        if prefs.use_project:
            if project_name != "":
                col.operator(
                    "os.set_project_path",
                    icon="OUTLINER_OB_ARMATURE",
                    text="Set {} Path".format(project_name),
                )
        if prefs.custom_project_paths:
            for index, path in enumerate(prefs.custom_project_paths):
                project_name = "Untitled"
                if path.project_name != "":
                    project_name = path.project_name
                row = col.row(align=True)
                row.operator(
                    "os.set_custom_project_path",
                    icon="BOOKMARKS",
                    text=project_name,
                ).index = index

        if prefs.use_project or prefs.custom_project_paths:
            row = layout.row()

        row.label(text="Export folder:")

        row = layout.row()
        col = row.column()
        col.prop(context.scene, "export_folder", text="")

        col = row.column()
        col.operator("object.openfolder", text="", icon="FILE_TICK")

        # Project navigation
        directory_path = Path(context.scene.export_folder)
        blend_dir = directory_path.parent
        child_folder_name = blend_dir.name
        current_folder_name = directory_path.name

        col = layout.column(align=True)
        row = layout.row(align=True)
        col.label(text="Curent Folder: " + current_folder_name)

        row = layout.row(align=True)
        row.operator(
            "os.parent_folder",
            icon="BACK",
            text="Previous Folder: " + child_folder_name,
        )

        col = layout.column(align=True)

        if directory_path.is_dir():
            box = layout.box()
            split = box.split()
            col = split.column(align=True)

            folders = [
                folder
                for folder in directory_path.iterdir()
                if folder.is_dir() and not (folder.name.startswith("__") and folder.name.endswith("__"))
            ]
            folders.sort(key=lambda f: not f.name.startswith("_"))

            if not folders:
                col.label(text="No Subfolder")

            for folder in folders:
                button = col.operator("os.select_folder", text=folder.name)
                button.folder_path = str(folder)

        row = layout.row(align=True)
        col = row.column(align=True)
        col.operator("os.new_folder", icon="NEWFOLDER", text="New Folder")
        row.prop(context.scene, "new_folder_name", text="")

        col = layout.column(align=True)
        row = layout.row(align=True)
        col.label(text="Export Options:")

        box = layout.box()

        row = box.row()
        row.prop(context.scene, "center_transform", text="Center transform")

        row = box.row()
        row.prop(context.scene, "apply_transform", text="Apply transform")

        row = box.row()
        row.prop(context.scene, "no_decal_uv")

        row = box.row()
        row.prop(context.scene, "rename_dot")

        row = box.row()
        row.prop(context.scene, "triangulate", text="Triangulate")

        row = box.row()
        row.prop(context.scene, "black_vertex", text="Set vertex color")

        row = box.row()
        row.prop(context.scene, "fix_collider", text="Fix Collider")

        row = layout.row()
        row.label(text="Advanced option:")

        box = layout.box()

        row = box.row()
        row.prop(context.scene, "one_material_id")

        row = box.row()
        row.prop(context.scene, "purge_data")

        row_smooth = layout.row()
        col_smooth_lbl = row_smooth.column()
        col_smooth_lbl.label(text="Smoothing:")

        col_smooth = row_smooth.column()
        col_smooth.alignment = "EXPAND"
        col_smooth.prop(context.scene, "export_smoothing", text="")

        row = layout.row()
        row.prop(context.scene, "export_animations")

        row = layout.row()
        row.label(text="Custom Name:")

        row = layout.row()
        col = row.column()
        col.prop(context.scene, "custom_name", text="")

        raw = layout.row()
        col = raw.column()
        col.scale_y = 2.0
        col.operator("object.bat_export", text="Export")

        # obj = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            if (obj.type == "MESH" and hasMultipleUVSets(obj)) or anyChildHasMultipleUVSets(obj):
                row_warninguv = layout.row()
                col_warninguv_lbl = row_warninguv.column()
                col_warninguv_lbl.label(
                    icon="ERROR",
                    text="Selected objects or their children have more than one UV set",
                )
                break


class N_PT_material(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Material & UV"
    bl_category = "Metric"
    bl_idname = "N_PT_material"
    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[base_package].preferences
        clpe = prefs.material_panel_enable
        return clpe

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        column.label(text="Remove:")

        row = layout.row(align=True)
        col = row.column(align=True)
        col.operator("object.remove_all_material", text="Material")
        row = layout.row(align=True)
        col = row.column(align=True)
        col.operator("object.remove_all_uv", text="UV Map")
        col.operator("object.remove_nonrender_uv", text="Non Render UV Map")
        row = layout.row(align=True)
        col = row.column(align=True)
        col.operator("object.remove_specific_uv", text="Specific UV Map")
        row.prop(context.scene, "specific_uv", text="")

        column = layout.column(align=True)
        column.label(text="Rename:")
        layout.operator("object.uv_rename", text="UV Map")


class N_PT_Tools(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Tools"
    bl_category = "Metric"
    bl_idname = "N_PT_Tools"
    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[base_package].preferences
        clpe = prefs.tool_panel_enable
        return clpe

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        column.label(text="Add Collider:")

        row = layout.row(align=True)
        col = row.column(align=True)
        col.operator("object.set_box_collider", icon="META_CUBE", text="Box")
        col.operator("object.set_capsule_collider", icon="META_CAPSULE", text="Capsule")
        col.operator("object.set_sphere_collider", icon="MATSPHERE", text="Sphere")
        col.operator("object.set_cylinder_collider", icon="MESH_CYLINDER", text="Cylinder")
        col.operator("object.set_convex_collider", icon="MOD_LINEART", text="Convex")

        row = layout.row(align=True)
        row.operator("object.fix_collider_name", icon="MODIFIER", text="Fix Collider")

        column = layout.column(align=True)
        column.label(text="Asset:")

        row = layout.row(align=True)
        row.operator("object.save_asset_to_library", text="Save to Library")

        column = layout.column(align=True)
        column.label(text="Rotation:")

        box = layout.box()
        row_affectonly = box.row()

        row_affectonly.prop(context.scene, "rand_x", text="X")
        row_affectonly.prop(context.scene, "rand_y", text="Y")
        row_affectonly.prop(context.scene, "rand_z", text="Z")

        row = layout.row(align=True)
        row.operator("object.random_rotation", text="Random Rotation")

        column = layout.column(align=True)
        column.label(text="Decals:")

        raw = layout.row()
        col = raw.column()
        col.scale_y = 2.0
        col.operator("object.smart_decal", text="Combine Decal")

        row = layout.row(align=True)
        row.operator("object.use_atlases", text="Use Atlases")

        column = layout.column(align=True)
        column.label(text="Other:")

        row = layout.row(align=True)
        row.operator("object.assign_vcolor", icon="VPAINT_HLT", text="Vertex Color")
        row = layout.row(align=True)
        row.operator("object.wireframe_modifier", icon="MOD_WIREFRAME", text="Wireframe Modifier")
        row.operator("object.wireframe_modifier", icon="MOD_WIREFRAME", text="Wireframe Modifier")
        row = layout.row(align=True)
        row.operator("object.clean_mesh", icon="BRUSH_DATA", text="Clean Mesh")
