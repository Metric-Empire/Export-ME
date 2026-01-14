from __future__ import annotations

from typing import Tuple
import bpy
from pathlib import Path
from bpy.props import StringProperty, BoolProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup, AddonPreferences, Context

from .. import __package__ as base_package

assert base_package is not None


def get_preferences(context: Context) -> ExportMEPreferences:
    return context.preferences.addons[base_package].preferences


def get_custom_paths(context: Context) -> bpy.types.bpy_prop_collection:
    return get_preferences(context).custom_project_paths


def get_subpath(context: Context) -> Path:
    path = str(get_preferences(context).project_subpath)
    return Path(path.lstrip("\\/"))


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


class ExportMEPreferences(AddonPreferences):
    bl_idname = base_package

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

    def draw(self, context: Context) -> None:
        layout = self.layout

        # Project Path Section
        col = layout.column(align=True)
        col.label(text="Project Paths:")

        layout.operator("preferences.add_custom_path", text="Add New Path", icon="ADD")

        for index, path in enumerate(self.custom_project_paths):
            box = layout.box()
            box.prop(path, "project_name", text="Name")
            box.prop(path, "filepath", text="Path")

            row = box.row()
            row.prop(path, "icon", text="Icon")
            row.operator("iv.icons_show", text="Browse")
            row.operator("preferences.remove_custom_path", text="", icon="X").index = index

        # Project Subpath Section
        if self.custom_project_paths:
            box = layout.box()
            box.prop(self, "use_project")

            if self.use_project:
                box.prop(self, "project_subpath")

                # Validate path existence
                if self.custom_project_paths:
                    first_project = Path(self.custom_project_paths[0].filepath)
                    subpath = get_subpath(context)
                    full_path = first_project / subpath

                    if not full_path.exists():
                        row = box.row()
                        row.label(
                            text="Path does not exist, ensure the subpath is correct",
                            icon="ERROR",
                        )


class N_OT_AddCustomPath(bpy.types.Operator):
    bl_idname = "preferences.add_custom_path"
    bl_label = "Add Custom Path"

    def execute(self, context: Context) -> set[str]:
        context.preferences.addons[base_package].preferences.custom_project_paths.add()
        return {"FINISHED"}


class N_OT_RemoveCustomPath(bpy.types.Operator):
    bl_idname = "preferences.remove_custom_path"
    bl_label = "Remove Custom Path"

    index: IntProperty()

    def execute(self, context: Context) -> set[str]:
        prefs: ExportMEPreferences = context.preferences.addons[base_package].preferences
        prefs.custom_project_paths.remove(self.index)
        return {"FINISHED"}


PREFERENCE_CLASSES: Tuple[type, ...] = (
    CustomProjectPath,
    ExportMEPreferences,
    N_OT_AddCustomPath,
    N_OT_RemoveCustomPath,
)
