from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Scene


@dataclass
class ExportSettings:
    export_folder: Path
    custom_name: str
    center_transform: bool
    apply_transform: bool
    one_material_id: bool
    no_decal_uv: bool
    rename_dot: bool
    purge_data: bool
    triangulate: bool
    fix_collider: bool
    black_vertex: bool
    export_animations: bool
    smoothing: str

    @classmethod
    def from_scene(cls, scene: Scene) -> ExportSettings:
        import bpy

        export_folder = scene.export_folder
        if export_folder.startswith("//"):
            export_folder = Path(bpy.path.abspath(export_folder)).resolve()
        else:
            export_folder = Path(export_folder)

        return cls(
            export_folder=export_folder,
            custom_name=scene.custom_name,
            center_transform=scene.center_transform,
            apply_transform=scene.apply_transform,
            one_material_id=scene.one_material_id,
            no_decal_uv=scene.no_decal_uv,
            rename_dot=scene.rename_dot,
            purge_data=scene.purge_data,
            triangulate=scene.triangulate,
            fix_collider=scene.fix_collider,
            black_vertex=scene.black_vertex,
            export_animations=scene.export_animations,
            smoothing=scene.export_smoothing,
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import PropertyGroup


@dataclass
class ProjectPath:
    filepath: Path
    project_name: str
    icon: str

    @classmethod
    def from_property(cls, prop: PropertyGroup) -> ProjectPath:
        return cls(
            filepath=Path(prop.filepath),
            project_name=prop.project_name,
            icon=prop.icon,
        )
