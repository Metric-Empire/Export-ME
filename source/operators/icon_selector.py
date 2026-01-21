from typing import List
import bpy
import math
import re
from bpy.types import Operator, Context, Event
from bpy.props import StringProperty, IntProperty


DPI = 72
POPUP_PADDING = 10
WIN_PADDING = 32
ICON_SIZE = 20


def ui_scale():
    prefs = bpy.context.preferences.system
    return prefs.dpi / DPI


# Icon blacklist patterns - icons matching these patterns will be hidden
ICON_BLACKLIST_PATTERNS = [
    r"^EVENT_.{3,}$",  # Icons starting with "EVENT_" followed by 3 or more characters
    r"^IPO_",  # Icons starting with "IPO_"
    r"^NONE$",  # Icon named "NONE
    r"^BLANK1$",  # Icon named "BLANK1"
    r".*CURVE.*",  # Icons containing "CURVE"
    r"^BLENDER_LOGO_LARGE$",  # Icon named "BLENDER_LOGO_LARGE"
    r"^COLORSET_",  # Icons starting with "COLORSET_"
    r"^KEY_EMPTY",  # Icons starting with "KEY_EMPTY1_"
    r"^KEY_BACKSPACE",  # Icons starting with "KEY_BACKSPACE_"
]


def get_all_icons() -> List[str]:
    """Get all Blender icons filtered by blacklist patterns."""
    all_icons = [
        item.identifier for item in bpy.types.UILayout.bl_rna.functions["operator"].parameters["icon"].enum_items
    ]
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in ICON_BLACKLIST_PATTERNS]
    filtered_icons = [icon for icon in all_icons if not any(pattern.match(icon) for pattern in compiled_patterns)]

    return filtered_icons


class N_OT_IconShow(Operator):
    bl_idname = "export_me.icons_show"
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
            num_cols = round(1.3 * math.sqrt(len(icons)))
            width = int(min(ui_scale() * (num_cols * ICON_SIZE + POPUP_PADDING), context.window.width - WIN_PADDING))
            return context.window_manager.invoke_props_dialog(self, width=width)
        return self.execute(context)

    def draw(self, context: Context) -> None:
        icons = get_all_icons()
        num_cols = round(1.3 * math.sqrt(len(icons)))

        column = self.layout.column(align=True)
        row = column.row(align=True)
        row.alignment = "CENTER"

        for i, icon_name in enumerate(icons):
            op = row.operator(self.bl_idname, text="", icon=icon_name, emboss=False)
            op.icon = icon_name
            op.project_index = self.project_index
            op.subpath_index = self.subpath_index

            if (i + 1) % num_cols == 0 and i < len(icons) - 1:
                row = column.row(align=True)
                row.alignment = "CENTER"
