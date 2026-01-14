from typing import List, TYPE_CHECKING
from pathlib import Path
import bpy
from bpy.types import Object

if TYPE_CHECKING:
    from mathutils import Vector


def resolve_export_path(path_str: str) -> Path:
    if path_str.startswith("//"):
        return Path(bpy.path.abspath(path_str)).resolve()
    return Path(path_str).resolve()


def get_children(obj: Object) -> List[Object]:
    return [ob for ob in bpy.data.objects if ob.parent == obj]


def get_object_location(obj: Object) -> Vector:
    return obj.location.copy()


def set_object_location(obj: Object, loc: tuple[float, float, float] | Vector) -> None:
    obj.location = loc
