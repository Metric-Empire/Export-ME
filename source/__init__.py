import bpy
import os

from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup
from pathlib import Path

from .panel import *
from .bat_export_ot import *
from .folder_ot import *
from .tools_ot import *
from .project_path_ot import *
from .smart_decal_apply_ot import *
from .icon_selector import *


bpy.types.Scene.export_folder = StringProperty(
    name="Export folder",
    subtype="DIR_PATH",
    description="Directory to export the fbx files into",
)

bpy.types.Scene.custom_name = StringProperty(
    name="Custom Name",
    subtype="FILE_NAME",
    description="Add a custom name for FBX, if empty the parent object name will be used as the name, this do not support bulk export yet",
)

bpy.types.Scene.center_transform = BoolProperty(
    name="Center transform",
    default=True,
    description="Set the pivot point of the object to the center",
)

bpy.types.Scene.apply_transform = BoolProperty(
    name="Apply transform",
    default=True,
    description="Applies scale and transform (Experimental)",
)

bpy.types.Scene.export_smoothing = EnumProperty(
    name="Smoothing",
    description="Defines the export smoothing information",
    items=(
        ("EDGE", "Edge", "Write edge smoothing", 0),
        ("FACE", "Face", "Write face smoothing", 1),
        ("OFF", "Normals Only", "Write normals only", 2),
    ),
    default="OFF",
)

bpy.types.Scene.export_animations = BoolProperty(
    name="Export Rig & Animations",
    default=False,
    description="Export rig and animations",
)

bpy.types.Scene.one_material_id = BoolProperty(
    name="One material ID",
    default=False,
    description="Export just one material per object",
)

bpy.types.Scene.no_decal_uv = BoolProperty(
    name="Remove Decal UV",
    default=True,
    description="remove the second UV chanel on decal mesh",
)

bpy.types.Scene.rename_dot = BoolProperty(name="Replace Dot", default=True, description="Replace dot by underscore")

bpy.types.Scene.purge_data = BoolProperty(
    name="Remove Orphans Data",
    default=False,
    description="Remove all the Orphans Data",
)

bpy.types.Scene.triangulate = BoolProperty(
    name="Triangulate", default=True, description="Triangulate meshes before exporting"
)

bpy.types.Scene.black_vertex = BoolProperty(
    name="Set Vertex Color", default=True, description="Set vertex paint color to black"
)

bpy.types.Scene.fix_collider = BoolProperty(
    name="Fix Collider", default=True, description="Fix Collider Name and make sure they are convex"
)


bpy.types.Scene.new_folder_name = StringProperty(
    name="New Folder Name",
    subtype="FILE_NAME",
    description="Create a new folder in the current directory",
)


class N_GlobalProperties:
    # TODO: Implementation of the addon API for project management
    path = ""
    project_name = ""


class CustomProjectPath(PropertyGroup):
    filepath: StringProperty(  # type: ignore
        name="Custom Project Path",
        subtype="FILE_PATH",
        description="Set Custom Project Path",
    )
    project_name: StringProperty(  # type: ignore
        name="",
        description="Name of the project associated with this path",
    )
    icon: StringProperty(  # type: ignore
        name="Icon",
        description="Icon to display for this project path",
        default="BLENDER",
    )


class N_Preferences(bpy.types.AddonPreferences, N_GlobalProperties):
    bl_idname = __package__

    # List of custom project paths
    custom_project_paths: CollectionProperty(type=CustomProjectPath)  # type: ignore

    use_project: BoolProperty(  # type: ignore
        name="Use " + N_GlobalProperties.project_name + " Project Path",
        description="Use the project path to export the FBX",
        default=True,
    )

    project_subpath: StringProperty(  # type: ignore
        name="Project Subpath",
        subtype="FILE_PATH",
        description="Subpath to the FBX folder",
        default=str(Path("Content/_GraphicBank/Asset/Mesh")),
    )

    material_panel_enable: BoolProperty(  # type: ignore
        name="Material and UV",
        description="Show the material and UV panel",
        default=True,
    )

    viewport_panel_enable: BoolProperty(name="Viewport", description="Show the viewport panel", default=True)  # type: ignore

    tool_panel_enable: BoolProperty(name="Tools", description="Show the tool panel", default=True)  # type: ignore

    def draw(self, context):
        layout = self.layout

        # Project Path Section
        col = layout.column(align=True)
        col.label(text="Project Path:")

        # Button to add a new custom path
        col = layout.column()
        row = col.row()
        row.operator("preferences.add_custom_path", text="Add New Custom Path", icon="ADD")

        # Display all custom project paths dynamically
        for index, custom_path in enumerate(self.custom_project_paths):
            box = layout.box()
            row = box.row()

            row.prop(custom_path, "project_name", text="Project Name")
            row = box.row()
            row.prop(custom_path, "filepath", text=f"Project Path {index + 1}")
            row = box.row()
            row.prop(custom_path, "icon", text="Icon")
            row = box.row()
            row.operator("iv.icons_show", text="Browse Icons")

            row.operator("preferences.remove_custom_path", text="Remove", icon="X").index = index

        if N_GlobalProperties.path != "":
            box = layout.box()
            row = box.row()
            row.prop(self, "use_project")

            if self.use_project:
                row = box.row()
                row.prop(self, "project_subpath")

                subpath = self.project_subpath

                if str(N_GlobalProperties.path) in subpath:
                    subpath = subpath.replace(N_GlobalProperties.path, "")
                if subpath and subpath[0] == "/":
                    subpath = subpath[1:]

                full_path = os.path.join(N_GlobalProperties.path, subpath)

                if not os.path.exists(full_path):
                    row = box.row()
                    row.label(
                        text="The path does not exist, make sur the sub path exist",
                        icon="ERROR",
                    )


class N_OT_SelectAndApplyIcon(bpy.types.Operator):
    bl_idname = "preferences.select_and_apply_icon"
    bl_label = "Select Icon"

    index: IntProperty()  # type: ignore

    def execute(self, context):
        # First show the icon selector
        bpy.ops.iv.icons_show()

        # Get the clipboard content (where iv.icons_show puts the selected icon name)
        clipboard = context.window_manager.clipboard

        # Update the icon property if the clipboard contains valid data
        if clipboard:
            prefs = context.preferences.addons[__package__].preferences
            if self.index < len(prefs.custom_project_paths):
                prefs.custom_project_paths[self.index].icon = clipboard

        return {"FINISHED"}


# Operator to add a new custom path
class AddCustomPathOperator(bpy.types.Operator):
    bl_idname = "preferences.add_custom_path"
    bl_label = "Add Custom Project Path"

    def execute(self, context):
        context.preferences.addons[__package__].preferences.custom_project_paths.add()
        return {"FINISHED"}


# Operator to remove a custom path
class RemoveCustomPathOperator(bpy.types.Operator):
    bl_idname = "preferences.remove_custom_path"
    bl_label = "Remove Custom Project Path"

    index: IntProperty()  # type: ignore

    def execute(self, context):
        context.preferences.addons[__package__].preferences.custom_project_paths.remove(self.index)
        return {"FINISHED"}


classes = (
    N_PT_Panel,
    N_OT_bat_export,
    N_OT_OpenFolder,
    N_OT_SmartDecal_Op,
    N_OT_FixColliderName_Op,
    N_OT_NewFolder,
    N_OT_ParentFolder,
    N_OT_SetProjectPath,
    N_OT_SetCustomProjectPath,
    N_OT_SelectFolder,
    CustomProjectPath,
    N_Preferences,
    AddCustomPathOperator,
    RemoveCustomPathOperator,
    N_OT_icons_show,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
