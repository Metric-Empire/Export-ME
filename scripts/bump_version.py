import re


def update_toml_version(file_path, new_version):
    with open(file_path, "r") as file:
        content = file.read()

    new_content = re.sub(r'(?<!_)version = "[0-9]+\.[0-9]+\.[0-9]+"', f'version = "{new_version}"', content)

    with open(file_path, "w") as file:
        file.write(new_content)


def old_version():
    with open(pyproject_toml_path, "r") as file:
        pyproject_content = file.read()
        old_version = re.search(r'(?<!_)version = "([0-9]+\.[0-9]+\.[0-9]+)"', pyproject_content).group(1)

    return old_version


def update_program_version(new_version):
    update_toml_version(pyproject_toml_path, new_version)
    update_toml_version(blender_manifest_path, new_version)
    print(f"Version updated to: {new_version}")


# Path
pyproject_toml_path = "./pyproject.toml"
blender_manifest_path = "./source/blender_manifest.toml"


print("Current version is: ", old_version())
new_version = input("Enter the new version: ")
update_program_version(new_version)
