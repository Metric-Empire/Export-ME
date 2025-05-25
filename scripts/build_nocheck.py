import re
import tomllib
import fnmatch

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def zip_files(dir: Path, zip_name: str, export_dir: Path) -> None:
    manifest_path = dir / "blender_manifest.toml"
    try:
        with open(manifest_path, "rb") as mf:
            manifest = tomllib.load(mf)
        patterns = manifest.get("build", {}).get("paths_exclude_pattern", [])
    except FileNotFoundError:
        patterns = []

    export_dir.mkdir(parents=True, exist_ok=True)
    zip_path = export_dir / zip_name

    def is_excluded(rel: Path) -> bool:
        rel_str = rel.as_posix()
        for pat in patterns:
            p = pat.lstrip("/")
            if p.endswith("/"):
                dirname = p.rstrip("/")
                if dirname in rel.parts:
                    return True
            else:
                if fnmatch.fnmatch(rel_str, p):
                    return True
        return False

    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zf:
        for f in dir.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(dir)
            if is_excluded(rel):
                continue
            zf.write(f, arcname=rel.as_posix())


def get_version():
    with open("./pyproject.toml", "r") as file:
        pyproject_content = file.read()
        old_version = re.search(r'(?<!_)version = "([0-9]+\.[0-9]+\.[0-9]+)"', pyproject_content).group(1)

    return old_version


if __name__ == "__main__":
    dir_to_zip = Path("./source")
    export_dir = Path("./dist")
    version = get_version()
    zip_files(dir_to_zip, f"Export-ME-{version}.zip", export_dir)
    print("Created .zip")
