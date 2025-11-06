# AI Agent TUI

This is a Terminal User Interface (TUI) built using [Textual](https://textual.textualize.io/) around my previous [AI Agent](https://github.com/pjjimiso/ai_agent) for a more interactive, terminal-based agent experience similar to Claude Code. Prompts are sent to Google's Gemini LLM, but it can also use function calling to perform basic actions such as: listing directory contents, reading and writing files, and running python scripts. 

Some other enhancements over the previous AI agent include: multi-turn chat conversations which remember context about previous messages that you have sent, model metrics showing total token consumption and a sparkline displayng tokens used over time, and a function call log that gets updated in real-time for more visibility into what the LLM is running.

## Features

- **Interactive Terminal UI**: Functional TUI built with the Textual framework for interacting with LLM 
- **Multi-Turn Conversations**: Chat with the AI agent while maintaining full conversation context
- **Function Call Log**: Real-time display of function calls requested by the model
- **Model Metrics**:
  - Specific model being used
  - Total prompt tokens consumed this session
  - Total response tokens consumed this session
  - Sparkline showing token usage over time
- **File System Operations**: The agent can interact with your file system through function calls:
  - List files and directories
  - Read file contents
  - Execute Python files
  - Write or overwrite files

## Prerequisites

- Python 3.14 or higher
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pjjimiso/agent_tui
cd agent_tui
```

2. Install dependencies using `uv` (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install textual google-genai dotenv
```

3. Create a `.env` file in the project root:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Configuration

The project uses the following configuration files:

- **`config.py`**: Contains the working directory configuration
- **`models.py`**: Specifies the Gemini model to use (default: `gemini-2.5-flash`)
- **`prompts.py`**: Contains the system prompt that defines the agent's behavior

## Usage

Run with `uv`:
```bash
uv run main.py
```

or run manually:
```bash
python main.py
```

Once running, you can interact with the agent through the input field at the bottom of the terminal. The interface is divided into three main sections:

1. **Function Calls Panel** (top left): Real-time view of function calls and arguments requested by the LLM
2. **Model Metrics Panel** (top right): Displays model information and token usage statistics
3. **Chat Panel** (middle): Shows the conversation between you and the agent

## Available Functions

The AI agent has access to the following functions:

- **`get_files_info`**: List files and directories in the working directory
- **`get_file_content`**: Read the contents of a specific file
- **`run_python_file`**: Execute a Python script
- **`write_file`**: Create or overwrite a file with new content

All file operations are restricted to the configured working directory for security.

## How It Works

1. User enters a prompt through the input field
2. The prompt is sent to the Gemini model along with available function definitions
3. The model responds with either:
   - A text response (displayed in the chat panel)
   - Function calls to execute (displayed in the function calls panel)
4. Function calls are executed and results are sent back to the model
5. The model uses function results to formulate a final response
6. Token usage is tracked and visualized in real-time

The agent follows an iterative loop (max 20 iterations) to handle complex multi-step tasks that require multiple function calls.

