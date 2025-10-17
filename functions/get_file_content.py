# get_file_content.py

import os
from config import MAX_CHARS
from google.genai import types

def get_file_content(working_directory, file_path): 

    working_directory_path = os.path.abspath(working_directory)
    file_abs_path = os.path.abspath(os.path.join(working_directory_path, file_path))

    if not file_abs_path.startswith(working_directory_path): 
        return f'Error: Cannot list "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(file_abs_path): 
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(file_abs_path, "r") as f: 
            file_content_string = f.read(MAX_CHARS)
        return file_content_string
    except Exeption as e: 
        return f"Failed to read file: {e}"



schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=f"Reads and returns the first {MAX_CHARS} characters of the content from a specified file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose content should be read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)
