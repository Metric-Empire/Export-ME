from typing import Dict, Tuple, Any
import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .ui import N_PT_Panel
from .operators import (
    N_OT_BatchExport,
    N_OT_SelectFolder,
    N_OT_ParentFolder,
    N_OT_NewFolder,
    N_OT_SetProjectPath,
    N_OT_SetCustomProjectPath,
    N_OT_SetProjectSubpath,
    N_OT_FixColliderName,
    N_OT_SmartDecal,
    N_OT_IconShow,
)
from .core.preferences import PREFERENCE_CLASSES


def get_project_enum_items(self, context):
    """Generate enum items for project dropdown"""
    from .core.preferences import get_preferences

    prefs = get_preferences(context)

    items = []
    for index, project in enumerate(prefs.custom_project_paths):
        name = project.project_name or f"Project {index + 1}"
        items.append((str(index), name, f"Select {name}", index))

    return items if items else [("0", "No Projects", "No projects available", 0)]


def update_smoothing_on_project_change(self, context):
    """Update smoothing setting when project selection changes"""
    from .core.preferences import get_preferences, get_recommended_smoothing
    
    try:
        selected_index = int(context.scene.selected_project_enum)
        prefs = get_preferences(context)
        
        if selected_index < len(prefs.custom_project_paths):
            project = prefs.custom_project_paths[selected_index]
            context.scene.export_smoothing = get_recommended_smoothing(project.game_engine)
    except (ValueError, AttributeError, IndexError):
        pass


SCENE_PROPERTIES: Dict[str, Any] = {
    "selected_project_enum": EnumProperty(
        name="Selected Project",
        description="Currently selected project",
        items=get_project_enum_items,
        update=update_smoothing_on_project_change,
    ),
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


CLASSES: Tuple[type, ...] = (
    *PREFERENCE_CLASSES,
    N_PT_Panel,
    N_OT_BatchExport,
    N_OT_SelectFolder,
    N_OT_ParentFolder,
    N_OT_NewFolder,
    N_OT_SetProjectPath,
    N_OT_SetCustomProjectPath,
    N_OT_SetProjectSubpath,
    N_OT_FixColliderName,
    N_OT_SmartDecal,
    N_OT_IconShow,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    for name, prop in SCENE_PROPERTIES.items():
        setattr(bpy.types.Scene, name, prop)


def unregister() -> None:
    for name in SCENE_PROPERTIES:
        delattr(bpy.types.Scene, name)

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
