from datetime import datetime

import pytz
import toml


def generate_date_version_string(timezone="UTC"):
    # Get the timezone object
    tz = pytz.timezone(timezone)
    # Get the current date and time in the specified timezone
    current_date = datetime.now(tz)
    # Format the date as YYYY.MM.DD
    version_string = current_date.strftime("%Y.%m.%d")
    return version_string


def update_version_in_pyproject(version_string, file_path="pyproject.toml"):
    # Read the pyproject.toml file
    with open(file_path, "r") as file:
        pyproject_data = toml.load(file)

    # Update the version field
    if "tool" in pyproject_data and "poetry" in pyproject_data["tool"]:
        pyproject_data["tool"]["poetry"]["version"] = version_string
    else:
        raise KeyError("Version key not found in pyproject.toml structure")

    # Write the updated data back to the pyproject.toml file
    with open(file_path, "w") as file:
        toml.dump(pyproject_data, file)


def write_version_to_file(version_string, file_path):
    with open(file_path, "w") as file:
        file.write(f'__version__ = "{version_string}"\n')


# Example usage
if __name__ == "__main__":
    # Specify the timezone you want
    timezone = "UTC"
    version_string = generate_date_version_string(timezone)
    print(f"Generated Version: {version_string}")

    # Update the version in pyproject.toml
    pyproject_file_path = "pyproject.toml"  # Update this path if needed
    try:
        update_version_in_pyproject(version_string, pyproject_file_path)
        print(f"Updated pyproject.toml with version: {version_string}")
    except Exception as e:
        print(f"An error occurred while updating pyproject.toml: {e}")

    # Write the version to __version__.py
    version_file_path = "src/git_inquisitor/__init__.py"  # Update this path if needed
    try:
        write_version_to_file(version_string, version_file_path)
        print(f"Wrote version to {version_file_path}: {version_string}")
    except Exception as e:
        print(f"An error occurred while writing to {version_file_path}: {e}")
