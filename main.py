# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "textual",
#   "google-genai",
#    "dotenv",
# ]
# ///

import os
import re

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Markdown, Input, Placeholder, Header, Footer, TextArea

from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from models import gemini
from functions.call_function import available_functions, call_function




class Prompt(Markdown):
    pass


class Response(Markdown): 
    BORDER_TITLE = "Agent TUI"


class FunctionCalls(Markdown):
    BORDER_TITLE = "Function Calls"


# TODO - implement widget with details about the model we're using
class ModelDetails(Placeholder):
    pass


# TODO - implement tracking of model metadata in a separate widget
#   (i.e. prompt tokens, response tokens, prompt count, etc.)
class ModelMetaData(Placeholder):
    pass


class AgentApp(App): 
    AUTO_FOCUS = "Input"


    def compose(self) -> ComposeResult: 
        yield Header()
        with VerticalScroll(id="func-view"):
            yield FunctionCalls("No Function Calls")
        with VerticalScroll(id="chat-view"):
            yield Response("Agent TUI at your service!")
        yield Input(placeholder="What can I help you with?")
        yield Footer()


    def on_mount(self) -> None: 
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API Key could not be provided from GEMINI_API_KEY environment variable")
        self.client = genai.Client(api_key=api_key)


    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted) -> None:
        chat_view = self.query_one("#chat-view")
        event.input.clear()
        await chat_view.mount(Prompt(event.value))
        await chat_view.mount(response := Response())
        response.anchor()
        self.send_prompt(event.value, response)


    @work(thread=True)
    def send_prompt(self, prompt: str, response: Response) -> None: 
        response_content = ""
        notify_function_calls = ""
        messages = [
            types.Content(role="user", parts=[types.Part(text=prompt)]),
        ]
        response_stream = self.client.models.generate_content_stream(
            model=gemini,
            contents=messages,
            config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        )
        functions_called = []
        for chunk in response_stream:
            if chunk.function_calls:
                functions_called.extend(chunk.function_calls)
            response_content += chunk.text
            self.call_from_thread(response.update, response_content)
        # TODO - fix function call parsing
        #if functions_called:
        #    notify_function_calls = f"We called the following functions:\n\t{functions_called}"
        #    update_function_calls(notify_function_calls)


    async def update_function_calls(self, functions_calls: str) -> None:
        func_view = self.query_one("#func-view")
        await func_view.mount(FunctionCalls(function_calls))





def main():
    #response.usage_metadata = str(response.usage_metadata) 
    #
    ## Extract candidates_token_count and prompt_token_count from response metadata
    #prompt_match = re.search(r'prompt_token_count=(\d+)', response.usage_metadata) 
    #response_match = re.search(r'candidates_token_count=(\d+)', response.usage_metadata) 

    #prompt_token_count = prompt_match.group(1) if prompt_match else None
    #response_token_count = response_match.group(1) if response_match else None

    #print(f"User prompt: {user_prompt}")
    #print(f"Prompt tokens: {prompt_token_count}")
    #print(f"Response tokens: {response_token_count}")

    app = AgentApp()
    app.run()


if __name__ == "__main__":
    main()
