# get_files_info.py

import os
from google.genai import types

# Tests to ensure the given directory is within our working directory 
# before returning the contents of the given directory
# TODO - What about symlinks? 
def get_files_info(working_directory, directory=None): 

    working_directory_path = os.path.abspath(working_directory)

    if not directory:
        directory_path = working_directory_path
    else:
        directory_path = os.path.abspath(os.path.join(working_directory_path, directory))

    if not directory_path.startswith(working_directory_path):
        print(f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
        return
    elif not os.path.isdir(directory_path):
        print(f'Error: "{directory}" is not a directory')
        return

    try:
        files_info = []
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            file_size = 0
            file_size = os.path.getsize(file_path)
            is_dir = os.path.isdir(file_path)
            files_info.append(f"- {file_name}: file_size={file_size} bytes, is_dir={is_dir}")
        return "\n".join(files_info)
    except Exception as e: 
        return f"Error listing files: {e}"


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
