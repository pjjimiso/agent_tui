# run_python.py

import os
import subprocess
from config import PROCESS_TIMEOUT
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):

    working_directory_path = os.path.abspath(working_directory)
    file_abs_path = os.path.abspath(os.path.join(working_directory_path, file_path))

    if not file_abs_path.startswith(working_directory_path): 
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(file_abs_path): 
        return f'Error: File "{file_path}" not found.'
    if not file_abs_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    try: 
        # Run the command using 'uv run' instead of calling python directly
        command = "uv run " + file_path
        for arg in args: 
            command = command + " " + arg
        result = subprocess.run(command, shell=True, cwd=working_directory_path, capture_output=True, check=True, text=True, timeout=PROCESS_TIMEOUT)

        output = []

        if result.stdout: 
            output.append(f'STDOUT:\n{result.stdout}')
        if result.stderr:
            #output.append(f'STDERR:\n{result.stderr}')
            output.append(f'STDOUT:\n{result.stderr}')

        if result.returncode != 0: 
            output.append(f'Process exited with code {result.returncode}')
        
        return "\n".join(output) if output else "No output produced."

    except subprocess.TimeoutExpired as e: 
        return f'Error: The process has exceeded the timeout threshold of {PROCESS_TIMEOUT} seconds and will be killed (this threshold can be changed in config.py)'
    except subprocess.Exception as e: 
        return f"Error: executing Python file: {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file within the working directory and returns the output from the interpreter.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Optional arguments to pass to the python file executable.",
                ),
                description="Optional arguments to pass to the python file executable.",
            ),
        },
        required=["file_path"],
    ),
)
