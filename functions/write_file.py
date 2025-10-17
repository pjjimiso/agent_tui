# write_file.py

import os
from google.genai import types

def write_file(working_directory, file_path, content):
    
    working_directory_path = os.path.abspath(working_directory)
    file_abs_path = os.path.abspath(os.path.join(working_directory_path, file_path))

    if not file_abs_path.startswith(working_directory_path): 
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(file_abs_path): 
        os.makedirs(os.path.dirname(file_abs_path), exist_ok=True)

    try:
        with open(file_abs_path, "w") as f: 
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except IOError as e:
        return f"File write failed: {e}"



schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file within the working directory. Creates the file if it doesn't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
        required=["file_path", "content"]
    ),
)
