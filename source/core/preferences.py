from __future__ import annotations

from typing import Tuple
import bpy
from pathlib import Path
from bpy.props import StringProperty, BoolProperty, CollectionProperty, IntProperty, EnumProperty
from bpy.types import PropertyGroup, AddonPreferences, Context

from .. import __package__ as base_package

assert base_package is not None


def get_preferences(context: Context) -> ExportMEPreferences:
    return context.preferences.addons[base_package].preferences


def get_custom_paths(context: Context) -> bpy.types.bpy_prop_collection:
    return get_preferences(context).custom_project_paths


def get_game_engine_for_path(context: Context, export_path: Path) -> str:
    """Get the game engine setting for the project containing the export path"""
    prefs = get_preferences(context)
    export_path_resolved = export_path.resolve()

    for project in prefs.custom_project_paths:
        if not project.filepath:
            continue
        project_path = Path(project.filepath).resolve()
        try:
            export_path_resolved.relative_to(project_path)
            return project.game_engine
        except ValueError:
            continue

    return "UNREAL"


def add_recent_export_path(context: Context, export_path: str) -> None:
    """Add an export path to recent history, avoiding duplicates and respecting max limit"""
    prefs = get_preferences(context)

    # Skip if file history is disabled
    if prefs.disable_file_history:
        return

    # Remove duplicate if it exists
    for index, recent_path in enumerate(prefs.recent_export_paths):
        if recent_path.filepath == export_path:
            prefs.recent_export_paths.remove(index)
            break

    # Add new path at the beginning
    new_recent = prefs.recent_export_paths.add()
    new_recent.filepath = export_path
    prefs.recent_export_paths.move(len(prefs.recent_export_paths) - 1, 0)

    # Remove excess items beyond max_recent_paths
    while len(prefs.recent_export_paths) > prefs.max_recent_paths:
        prefs.recent_export_paths.remove(len(prefs.recent_export_paths) - 1)


class RecentExportPath(PropertyGroup):
    filepath: StringProperty(
        name="Recent Export Path",
        subtype="DIR_PATH",
        description="Recently used export folder path",
    )


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
    game_engine: EnumProperty(
        name="Target Game Engine",
        description="Select the target game engine for FBX export settings",
        items=[
            ("UNREAL", "Unreal Engine", "Unreal Engine 4/5 - Forward: X, Up: Z, Scale: 1.0"),
            ("UNITY", "Unity", "Unity - Forward: Z, Up: Y, Scale: 1.0"),
            ("GODOT", "Godot", "Godot - Forward: -Z, Up: Y, Scale: 1.0"),
        ],
        default="UNREAL",
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
    recent_export_paths: CollectionProperty(type=RecentExportPath)
    max_recent_paths: IntProperty(
        name="Max Recent Paths",
        description="Maximum number of recent export paths to remember",
        default=5,
        min=1,
        max=20,
    )
    disable_file_history: BoolProperty(
        name="Disable File History",
        description="Disable tracking of recent export paths",
        default=False,
    )
    hide_folder_navigation: BoolProperty(
        name="Hide Folder Navigation",
        description="Hide the folder navigation section in the N panel",
        default=True,
    )

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
            box.prop(project, "game_engine", text="Game Engine")
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
                row.label(text="Icon:")
                icon_to_display = subpath.icon if subpath.icon else "QUESTION"
                op = row.operator("export_me.icons_show", text="", icon=icon_to_display)
                op.project_index = project_index
                op.subpath_index = subpath_index
                op = row.operator("export_me.icons_show", text="Select Icon")
                op.project_index = project_index
                op.subpath_index = subpath_index

            # Add subpath button
            op = box.operator("preferences.add_project_subpath", text="Add Subpath", icon="ADD")
            op.project_index = project_index

        # UI Options Section
        layout.separator()
        col = layout.column(align=True)
        col.label(text="UI Options:")
        col.prop(self, "hide_folder_navigation")

        # Recent Export Paths Section
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Recent Export Paths:")

        col.prop(self, "disable_file_history")

        row = col.row(align=True)
        row.enabled = not self.disable_file_history
        row.prop(self, "max_recent_paths", text="Max History")
        row.operator("preferences.clear_recent_paths", text="Clear History", icon="X")

        # Hide recent paths list if file history is disabled
        if not self.disable_file_history:
            if self.recent_export_paths:
                box = layout.box()
                for index, recent_path in enumerate(self.recent_export_paths):
                    box.row().label(text=f"{index + 1}. {recent_path.filepath}", icon="FOLDER_REDIRECT")
            else:
                layout.label(text="No recent export paths", icon="INFO")


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


class N_OT_SetRecentPath(bpy.types.Operator):
    bl_idname = "os.set_recent_path"
    bl_label = "Set Recent Export Path"
    bl_description = "Set export folder to this recent path"

    index: IntProperty()

    def execute(self, context: Context) -> set[str]:
        prefs = get_preferences(context)

        if self.index >= len(prefs.recent_export_paths):
            self.report({"ERROR"}, "Invalid recent path index")
            return {"CANCELLED"}

        recent_path = prefs.recent_export_paths[self.index]
        context.scene.export_folder = recent_path.filepath

        return {"FINISHED"}


class N_OT_ClearRecentPaths(bpy.types.Operator):
    bl_idname = "preferences.clear_recent_paths"
    bl_label = "Clear Recent Paths"
    bl_description = "Clear all recent export paths"

    def execute(self, context: Context) -> set[str]:
        prefs = get_preferences(context)
        prefs.recent_export_paths.clear()
        self.report({"INFO"}, "Recent export paths cleared")
        return {"FINISHED"}


PREFERENCE_CLASSES: Tuple[type, ...] = (
    RecentExportPath,
    ProjectSubpath,
    CustomProjectPath,
    ExportMEPreferences,
    N_OT_AddCustomPath,
    N_OT_RemoveCustomPath,
    N_OT_AddProjectSubpath,
    N_OT_RemoveProjectSubpath,
    N_OT_BrowseProjectSubpath,
    N_OT_OpenAddonPreferences,
    N_OT_SetRecentPath,
    N_OT_ClearRecentPaths,
)
