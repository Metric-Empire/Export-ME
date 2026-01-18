from typing import List
from bpy.types import Panel, Context, UILayout
from pathlib import Path

from ..core.preferences import get_preferences, ExportMEPreferences
from ..operators.batch_export import has_multiple_uv_sets, any_child_has_multiple_uvs


class N_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "FBX Export"
    bl_category = "ME"
    bl_idname = "N_PT_Panel"

    def draw(self, context: Context) -> None:
        layout = self.layout
        if not layout:
            return
        prefs = get_preferences(context)

        self._draw_projects_section(layout, prefs)
        self._draw_folder_navigation(layout, context)
        self._draw_export_options(layout, context)
        self._draw_advanced_options(layout, context)
        self._draw_export_button(layout)
        self._draw_uv_warnings(layout, context)

    def _draw_projects_section(self, layout: UILayout, prefs: ExportMEPreferences) -> None:
        if not (prefs.use_project or prefs.custom_project_paths):
            return

        layout.label(text="Projects:")
        
        if not prefs.custom_project_paths:
            # Show "Create Project" button when no projects exist
            layout.operator("preferences.open_addon_preferences", text="Create Project", icon="ADD")
            layout.separator()
            return

        col = layout.column()

        for index, path in enumerate(prefs.custom_project_paths):
            name = path.project_name or "Untitled"
            row = col.row(align=True)
            op = row.operator("os.set_custom_project_path", icon="BOOKMARKS", text=name)
            op.index = index

        layout.separator()

    def _draw_folder_navigation(self, layout: UILayout, context: Context) -> None:
        layout.label(text="Export folder:")

        row = layout.row()
        row.prop(context.scene, "export_folder", text="")
        row.operator("object.openfolder", text="", icon="FILE_TICK")

        directory = Path(context.scene.export_folder)
        parent_name = directory.parent.name
        current_name = directory.name

        layout.label(text=f"Current Folder: {current_name}")

        row = layout.row(align=True)
        row.operator("os.parent_folder", icon="BACK", text=f"Previous: {parent_name}")

        self._draw_subfolder_list(layout, directory)

        row = layout.row(align=True)
        row.operator("os.new_folder", icon="NEWFOLDER", text="New Folder")
        row.prop(context.scene, "new_folder_name", text="")

    def _draw_subfolder_list(self, layout: UILayout, directory: Path) -> None:
        if not directory.is_dir():
            return

        box = layout.box()
        col = box.column(align=True)

        folders: List[Path] = sorted(
            (f for f in directory.iterdir() if f.is_dir() and not (f.name.startswith("__") and f.name.endswith("__"))),
            key=lambda f: not f.name.startswith("_"),
        )

        if not folders:
            col.label(text="No Subfolder")
            return

        for folder in folders:
            op = col.operator("os.select_folder", text=folder.name)
            op.folder_path = folder.as_posix()

    def _draw_export_options(self, layout: UILayout, context: Context) -> None:
        layout.label(text="Export Options:")
        box = layout.box()

        options: List[tuple[str, str | None]] = [
            ("center_transform", "Center transform"),
            ("apply_transform", "Apply transform"),
            ("no_decal_uv", None),
            ("rename_dot", None),
            ("triangulate", "Triangulate"),
            ("black_vertex", "Set vertex color"),
            ("fix_collider", "Fix Collider"),
        ]

        for prop_name, label in options:
            row = box.row()
            if label:
                row.prop(context.scene, prop_name, text=label)
            else:
                row.prop(context.scene, prop_name)

    def _draw_advanced_options(self, layout: UILayout, context: Context) -> None:
        layout.label(text="Advanced Options:")
        box = layout.box()

        box.row().prop(context.scene, "one_material_id")
        box.row().prop(context.scene, "purge_data")

        row = layout.row()
        row.label(text="Smoothing:")
        row.prop(context.scene, "export_smoothing", text="")

        layout.row().prop(context.scene, "export_animations")

        layout.label(text="Custom Name:")
        layout.row().prop(context.scene, "custom_name", text="")

    def _draw_export_button(self, layout: UILayout) -> None:
        col = layout.column()
        col.scale_y = 2.0
        col.operator("object.bat_export", text="Export")

    def _draw_uv_warnings(self, layout: UILayout, context: Context) -> None:
        for obj in context.selected_objects:
            if (obj.type == "MESH" and has_multiple_uv_sets(obj)) or any_child_has_multiple_uvs(obj):
                row = layout.row()
                row.label(icon="ERROR", text="Objects have multiple UV sets")
                break
