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


class ProjectSubpath(PropertyGroup):
    name: StringProperty(
        name="Subpath Name",
        description="Display name for this subpath",
        default="New Subpath",
    )
    relative_path: StringProperty(
        name="Relative Path",
        description="Path relative to project root (e.g., Content/Assets)",
        default="",
    )
    icon: StringProperty(
        name="Icon",
        description="Icon identifier for this subpath",
        default="FILE_FOLDER",
    )


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
    show_root_button: BoolProperty(
        name="Show Root Folder Button",
        description="Show the project root button in the N panel",
        default=True,
    )
    subpaths: CollectionProperty(
        type=ProjectSubpath,
        name="Subpaths",
        description="List of subpaths for this project",
    )


class ExportMEPreferences(AddonPreferences):
    bl_idname = base_package

    custom_project_paths: CollectionProperty(type=CustomProjectPath)

    def draw(self, context: Context) -> None:
        layout = self.layout

        # Project Path Section
        col = layout.column(align=True)
        col.label(text="Projects:")

        layout.operator("preferences.add_custom_path", text="Add New Project", icon="ADD")

        for project_index, project in enumerate(self.custom_project_paths):
            box = layout.box()

            # Project header
            row = box.row()
            row.prop(project, "project_name", text="Project Name")
            row.operator("preferences.remove_custom_path", text="", icon="X").index = project_index

            box.prop(project, "filepath", text="Path")
            box.prop(project, "show_root_button", text="Show Root Folder Button")

            # Subpaths section
            box.label(text="Subpaths:")

            for subpath_index, subpath in enumerate(project.subpaths):
                subbox = box.box()
                row = subbox.row()
                row.prop(subpath, "name", text="Name")

                op = row.operator("preferences.remove_project_subpath", text="", icon="X")
                op.project_index = project_index
                op.subpath_index = subpath_index

                row = subbox.row(align=True)
                row.prop(subpath, "relative_path", text="Path")
                op = row.operator("preferences.browse_project_subpath", text="", icon="FILEBROWSER")
                op.project_index = project_index
                op.subpath_index = subpath_index

                row = subbox.row()
                row.prop(subpath, "icon", text="Icon")
                op = row.operator("iv.icons_show", text="Browse Icons")
                op.project_index = project_index
                op.subpath_index = subpath_index

            # Add subpath button
            op = box.operator("preferences.add_project_subpath", text="Add Subpath", icon="ADD")
            op.project_index = project_index


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


class N_OT_AddProjectSubpath(bpy.types.Operator):
    bl_idname = "preferences.add_project_subpath"
    bl_label = "Add Project Subpath"
    bl_description = "Add a new subpath to this project"

    project_index: IntProperty()

    def execute(self, context: Context) -> set[str]:
        prefs = get_preferences(context)

        if self.project_index >= len(prefs.custom_project_paths):
            self.report({"ERROR"}, "Invalid project index")
            return {"CANCELLED"}

        project = prefs.custom_project_paths[self.project_index]
        project.subpaths.add()

        return {"FINISHED"}


class N_OT_RemoveProjectSubpath(bpy.types.Operator):
    bl_idname = "preferences.remove_project_subpath"
    bl_label = "Remove Project Subpath"
    bl_description = "Remove this subpath from the project"

    project_index: IntProperty()
    subpath_index: IntProperty()

    def execute(self, context: Context) -> set[str]:
        prefs = get_preferences(context)

        if self.project_index >= len(prefs.custom_project_paths):
            self.report({"ERROR"}, "Invalid project index")
            return {"CANCELLED"}

        project = prefs.custom_project_paths[self.project_index]

        if self.subpath_index >= len(project.subpaths):
            self.report({"ERROR"}, "Invalid subpath index")
            return {"CANCELLED"}

        project.subpaths.remove(self.subpath_index)

        return {"FINISHED"}


class N_OT_BrowseProjectSubpath(bpy.types.Operator):
    bl_idname = "preferences.browse_project_subpath"
    bl_label = "Browse Project Subpath"
    bl_description = "Browse for a subpath relative to the project root"

    directory: StringProperty(subtype="DIR_PATH")
    project_index: IntProperty()
    subpath_index: IntProperty()

    def execute(self, context: Context) -> set[str]:
        prefs = get_preferences(context)

        if self.project_index >= len(prefs.custom_project_paths):
            self.report({"ERROR"}, "Invalid project index")
            return {"CANCELLED"}

        project = prefs.custom_project_paths[self.project_index]

        if self.subpath_index >= len(project.subpaths):
            self.report({"ERROR"}, "Invalid subpath index")
            return {"CANCELLED"}

        project_root = Path(project.filepath).resolve()
        selected_path = Path(self.directory).resolve()

        # Calculate relative path
        try:
            relative = selected_path.relative_to(project_root)
            project.subpaths[self.subpath_index].relative_path = str(relative)
        except ValueError:
            # If path is not relative to project root, show error
            self.report({"ERROR"}, "Selected path must be within the project root")
            return {"CANCELLED"}

        return {"FINISHED"}

    def invoke(self, context: Context, event) -> set[str]:
        prefs = get_preferences(context)

        if self.project_index >= len(prefs.custom_project_paths):
            self.report({"ERROR"}, "Invalid project index")
            return {"CANCELLED"}

        project = prefs.custom_project_paths[self.project_index]
        project_root = Path(project.filepath)

        # Set initial directory
        if self.subpath_index < len(project.subpaths):
            subpath = project.subpaths[self.subpath_index]
            if subpath.relative_path:
                self.directory = str(project_root / subpath.relative_path)
            else:
                self.directory = str(project_root)
        else:
            self.directory = str(project_root)

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class N_OT_OpenAddonPreferences(bpy.types.Operator):
    bl_idname = "preferences.open_addon_preferences"
    bl_label = "Open Export ME Preferences"
    bl_description = "Open addon preferences to create a new project"

    def execute(self, context: Context) -> set[str]:
        bpy.ops.preferences.addon_show(module=base_package)
        return {"FINISHED"}


PREFERENCE_CLASSES: Tuple[type, ...] = (
    ProjectSubpath,
    CustomProjectPath,
    ExportMEPreferences,
    N_OT_AddCustomPath,
    N_OT_RemoveCustomPath,
    N_OT_AddProjectSubpath,
    N_OT_RemoveProjectSubpath,
    N_OT_BrowseProjectSubpath,
    N_OT_OpenAddonPreferences,
)
