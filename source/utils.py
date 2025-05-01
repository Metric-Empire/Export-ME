import bpy
from . import __package__ as base_package
from pathlib import Path


# Get a copy of an object's location
def get_object_loc(obj):
    return obj.location.copy()


# Set the location of an object
def set_object_to_loc(obj, loc):
    obj.location = loc


def get_children(obj):
    children = []
    for ob in bpy.data.objects:
        if ob.parent == obj:
            children.append(ob)
    return children


def get_cursor_loc(context):
    return context.scene.cursor.location.copy()


def selected_to_cursor():
    bpy.ops.view3d.snap_selected_to_cursor()


def set_cursor_loc(context, loc: tuple):
    context.scene.cursor.location = loc


def get_custom_path_prefs(context):
    return context.preferences.addons[base_package].preferences.custom_project_paths


def get_subpath_prefs(context) -> Path:
    path = str(context.preferences.addons[base_package].preferences.project_subpath)
    if path.startswith("\\"):
        return path.lstrip("\\")
    elif path.startswith("/"):
        return path.lstrip("/")

    return Path(path)
