from typing import List
import bpy
import math
from bpy.types import Operator, Context, Event
from bpy.props import StringProperty, IntProperty


def get_all_icons() -> List[str]:
    # Dynamic access to Blender icon list
    return [item.identifier for item in bpy.types.UILayout.bl_rna.functions["operator"].parameters["icon"].enum_items]


class N_OT_IconShow(Operator):
    bl_idname = "iv.icons_show"
    bl_label = "Icon Viewer"
    bl_description = "Browse and select an icon"

    icon: StringProperty(default="")
    project_index: IntProperty(default=-1)
    subpath_index: IntProperty(default=-1)

    def execute(self, context: Context) -> set[str]:
        if self.icon and self.project_index >= 0 and self.subpath_index >= 0:
            from ..core.preferences import get_preferences
            prefs = get_preferences(context)
            
            if self.project_index < len(prefs.custom_project_paths):
                project = prefs.custom_project_paths[self.project_index]
                if self.subpath_index < len(project.subpaths):
                    project.subpaths[self.subpath_index].icon = self.icon
                    self.report({"INFO"}, f"Icon '{self.icon}' set for subpath")
        return {"FINISHED"}

    def invoke(self, context: Context, event: Event) -> set[str]:
        if not self.icon:
            icons = get_all_icons()
            num_cols = round(math.sqrt(len(icons)))
            width = min(context.region.width - 32, num_cols * 35)
            return context.window_manager.invoke_props_dialog(self, width=width)
        return self.execute(context)

    def draw(self, context: Context) -> None:
        icons = get_all_icons()
        num_cols = round(math.sqrt(len(icons)))
        flow = self.layout.grid_flow(columns=num_cols, even_columns=True, even_rows=True, row_major=True)

        for icon_name in icons:
            op = flow.operator(self.bl_idname, text="", icon=icon_name, emboss=False)
            op.icon = icon_name
            op.project_index = self.project_index
            op.subpath_index = self.subpath_index
