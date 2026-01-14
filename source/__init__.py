import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup
from pathlib import Path

from .ui import N_PT_Panel
from .operators import (
    N_OT_BatchExport,
    N_OT_OpenFolder,
    N_OT_SelectFolder,
    N_OT_ParentFolder,
    N_OT_NewFolder,
    N_OT_SetProjectPath,
    N_OT_SetCustomProjectPath,
    N_OT_FixColliderName,
    N_OT_SmartDecal,
    N_OT_IconShow,
)


SCENE_PROPERTIES = {
    "export_folder": StringProperty(
        name="Export folder",
        subtype="DIR_PATH",
        description="Directory to export the FBX files into",
    ),
    "custom_name": StringProperty(
        name="Custom Name",
        subtype="FILE_NAME",
        description="Custom name for FBX export (uses object name if empty)",
    ),
    "center_transform": BoolProperty(
        name="Center transform",
        default=True,
        description="Set the pivot point of the object to the center",
    ),
    "apply_transform": BoolProperty(
        name="Apply transform",
        default=True,
        description="Apply scale and transform (Experimental)",
    ),
    "export_smoothing": EnumProperty(
        name="Smoothing",
        description="Export smoothing information mode",
        items=(
            ("EDGE", "Edge", "Write edge smoothing", 0),
            ("FACE", "Face", "Write face smoothing", 1),
            ("OFF", "Normals Only", "Write normals only", 2),
        ),
        default="OFF",
    ),
    "export_animations": BoolProperty(
        name="Export Rig & Animations",
        default=False,
        description="Export rig and animations",
    ),
    "one_material_id": BoolProperty(
        name="One material ID",
        default=False,
        description="Export just one material per object",
    ),
    "no_decal_uv": BoolProperty(
        name="Remove Decal UV",
        default=True,
        description="Remove the Decal UV channel on decal meshes",
    ),
    "rename_dot": BoolProperty(
        name="Replace Dot",
        default=True,
        description="Replace dots with underscores in names",
    ),
    "purge_data": BoolProperty(
        name="Remove Orphans Data",
        default=False,
        description="Remove all orphan data blocks",
    ),
    "triangulate": BoolProperty(
        name="Triangulate",
        default=True,
        description="Triangulate meshes before exporting",
    ),
    "black_vertex": BoolProperty(
        name="Set Vertex Color",
        default=True,
        description="Set vertex paint color to black",
    ),
    "fix_collider": BoolProperty(
        name="Fix Collider",
        default=True,
        description="Fix collider names and ensure they are convex",
    ),
    "new_folder_name": StringProperty(
        name="New Folder Name",
        subtype="FILE_NAME",
        description="Name for new folder to create",
    ),
}


class CustomProjectPath(PropertyGroup):
    filepath: StringProperty(
        name="Custom Project Path",
        subtype="FILE_PATH",
        description="Project root path",
    )
    project_name: StringProperty(
        name="Project Name",
        description="Display name for this project",
    )
    icon: StringProperty(
        name="Icon",
        description="Icon identifier for this project",
        default="BLENDER",
    )


class ExportMEPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    custom_project_paths: CollectionProperty(type=CustomProjectPath)

    use_project: BoolProperty(
        name="Use Project Path",
        description="Use the project path for FBX export",
        default=True,
    )

    project_subpath: StringProperty(
        name="Project Subpath",
        subtype="FILE_PATH",
        description="Subpath to the FBX folder within project",
        default="Content/_GraphicBank/Asset/Mesh",
    )

    def draw(self, context):
        layout = self.layout

        layout.label(text="Project Paths:")
        layout.operator("preferences.add_custom_path", text="Add New Path", icon="ADD")

        for index, path in enumerate(self.custom_project_paths):
            box = layout.box()
            box.prop(path, "project_name", text="Name")
            box.prop(path, "filepath", text="Path")

            row = box.row()
            row.prop(path, "icon", text="Icon")
            row.operator("iv.icons_show", text="Browse")
            row.operator("preferences.remove_custom_path", text="", icon="X").index = index


class N_OT_AddCustomPath(bpy.types.Operator):
    bl_idname = "preferences.add_custom_path"
    bl_label = "Add Custom Path"

    def execute(self, context):
        context.preferences.addons[__package__].preferences.custom_project_paths.add()
        return {"FINISHED"}


class N_OT_RemoveCustomPath(bpy.types.Operator):
    bl_idname = "preferences.remove_custom_path"
    bl_label = "Remove Custom Path"

    index: IntProperty()

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.custom_project_paths.remove(self.index)
        return {"FINISHED"}


CLASSES = (
    CustomProjectPath,
    ExportMEPreferences,
    N_OT_AddCustomPath,
    N_OT_RemoveCustomPath,
    N_PT_Panel,
    N_OT_BatchExport,
    N_OT_OpenFolder,
    N_OT_SelectFolder,
    N_OT_ParentFolder,
    N_OT_NewFolder,
    N_OT_SetProjectPath,
    N_OT_SetCustomProjectPath,
    N_OT_FixColliderName,
    N_OT_SmartDecal,
    N_OT_IconShow,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    for name, prop in SCENE_PROPERTIES.items():
        setattr(bpy.types.Scene, name, prop)


def unregister():
    for name in SCENE_PROPERTIES:
        delattr(bpy.types.Scene, name)

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
