from pathlib import Path
import bpy


def resolve_export_path(path_str: str) -> Path:
    if path_str.startswith("//"):
        return Path(bpy.path.abspath(path_str)).resolve()
    return Path(path_str).resolve()


def get_children(obj) -> list:
    return [ob for ob in bpy.data.objects if ob.parent == obj]


def get_object_location(obj):
    return obj.location.copy()


def set_object_location(obj, loc):
    obj.location = loc
