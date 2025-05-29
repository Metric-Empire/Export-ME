import bpy
import math
from bpy.props import StringProperty


def get_all_icons():
    return [item.identifier for item in bpy.types.UILayout.bl_rna.functions["operator"].parameters["icon"].enum_items]


def get_num_cols(n_icons: int) -> int:
    return round(1 * math.sqrt(n_icons))


class N_OT_icons_show(bpy.types.Operator):
    bl_idname = "iv.icons_show"
    bl_label = "Icon Viewer"
    bl_description = "Browse and select an icon"

    icon: StringProperty(default="")  # type: ignore

    def execute(self, context):
        if self.icon:
            context.window_manager.clipboard = self.icon
            self.report({"INFO"}, f"Icon '{self.icon}' copied to clipboard")
        return {"FINISHED"}

    def invoke(self, context, event):
        if not self.icon:
            icons = get_all_icons()
            num_cols = get_num_cols(len(icons))
            width = min(context.region.width - 32, num_cols * 35)
            return context.window_manager.invoke_props_dialog(self, width=width)
        return self.execute(context)

    def draw(self, context):
        icons = get_all_icons()
        num_cols = get_num_cols(len(icons))
        flow = self.layout.grid_flow(columns=num_cols, even_columns=True, even_rows=True, row_major=True)
        for icon_name in icons:
            op = flow.operator(self.bl_idname, text="", icon=icon_name, emboss=False)
            op.icon = icon_name
