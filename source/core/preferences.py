from pathlib import Path
from .. import __package__ as base_package


def get_preferences(context):
    return context.preferences.addons[base_package].preferences


def get_custom_paths(context):
    return get_preferences(context).custom_project_paths


def get_subpath(context) -> Path:
    path = str(get_preferences(context).project_subpath)
    return Path(path.lstrip("\\/"))
