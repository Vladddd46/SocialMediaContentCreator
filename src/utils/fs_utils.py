import glob
import json
import os
import shutil
from typing import Dict


def remove_directory(path: str) -> bool:
    """
    Removes the specified directory and all its contents.

    Parameters:
    - path (str): The path to the directory to be removed.

    Returns:
    - bool: True if the directory was removed successfully, False otherwise.
    """
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)  # Removes the directory and all its contents
            return True
        else:
            return False
    except FileNotFoundError:
        return False
    except Exception as e:
        return False
    return False


def remove_recursive(pattern: str, start_path: str = ".") -> bool:
    """
    Recursively removes all files or directories matching the specified pattern
    from the given start path and its subdirectories.

    Parameters:
    - pattern (str): The pattern to match (e.g., '__pycache__' or '*.tmp').
    - start_path (str): The path to start the search from (default is the current directory).

    Returns:
    - bool: True if at least one file or directory was removed, False otherwise.
    """
    found = False

    for root, dirs, files in os.walk(start_path):
        # Check for directories matching the pattern
        for dir_name in dirs:
            if glob.fnmatch.fnmatch(dir_name, pattern):
                dir_path = os.path.join(root, dir_name)
                shutil.rmtree(dir_path)
                found = True

        # Check for files matching the pattern
        for file_name in files:
            if glob.fnmatch.fnmatch(file_name, pattern):
                file_path = os.path.join(root, file_name)
                os.remove(file_path)
                found = True

    return found


def read_json_file(file_path: str) -> Dict:
    """
    Reads a JSON file and returns its contents as a dictionary.

    Parameters:
    - file_path (str): The path to the JSON file.

    Returns:
    - Dict: The JSON content as a Python dictionary.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    return {}


def is_path_exists(path):
    if os.path.exists(path):
        return True
    return False


def create_directory_if_not_exist(path):
    try:
        # Create all directories in the specified path if they don't exist
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        # print(f"Error creating directory: {e}")
        return False


def remove_file(file_path: str) -> bool:
    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        pass
    except PermissionError:
        pass
    except Exception as e:
        pass
    return False


def remove_files(pattern):
    try:
        # Find all files matching the pattern
        files = glob.glob(pattern)

        # Check if any files match the pattern
        if not files:
            return False

        # Remove each file that matches the pattern
        for file_path in files:
            if os.path.isfile(file_path):
                os.remove(file_path)
        return True
    except Exception as e:
        # print(f"An error occurred: {e}")
        return False


def is_directory_empty(directory_path):
    try:
        visible_files = [f for f in os.listdir(directory_path) if not f.startswith(".")]
        return len(visible_files) == 0
    except FileNotFoundError:
        return False
    except Exception as e:
        return False


def get_first_file_path(directory_path):
    try:
        # List all items in the directory
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            # Check if the item is a file
            if os.path.isfile(item_path):
                return os.path.abspath(
                    item_path
                )  # Return the full path to the first file found
        return None  # Return None if no files are found
    except Exception as e:
        return None


def create_file(filename, path=".", data=""):
    # Ensure the directory exists; if not, create it
    os.makedirs(path, exist_ok=True)

    # Full file path
    file_path = os.path.join(path, filename)

    # Create an empty file at the specified path
    with open(file_path, "w") as file:
        file.write(data)
    return file_path


def create_file_if_not_exists(filename, path=".", data=""):
    # Full file path
    file_path = os.path.join(path, filename)

    # Check if the file already exists
    if not os.path.isfile(file_path):
        # Use the create_file function to create the file
        return create_file(filename, path, data)
    return file_path


def read_json(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        # print(f"Error: The file {file_path} was not found.")
        pass
    except json.JSONDecodeError:
        # print(f"Error: Failed to decode JSON in the file {file_path}.")
        pass
    except Exception as e:
        # print(f"An error occurred: {e}")
        pass
    return None


def save_json(data, file_path: str) -> None:
    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        pass
    return False


def list_non_hidden_files(folder_path):
    """
    Returns a list of paths to all non-hidden files in the specified folder.

    Parameters:
        folder_path (str): Path to the folder.

    Returns:
        list: List of paths to all non-hidden files in the folder.
    """
    if not os.path.isdir(folder_path):
        return []

    # List all non-hidden files in the folder
    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if not f.startswith(".") and os.path.isfile(os.path.join(folder_path, f))
    ]

    return files
