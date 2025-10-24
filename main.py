# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "textual",
#   "google-genai",
#   "dotenv",
# ]
# ///

import os
import re

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Markdown, Input, Placeholder, Header, Footer, Log

from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from models import gemini
from functions.call_function import available_functions, call_function


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API Key could not be provided from GEMINI_API_KEY environment variable")


class Prompt(Markdown):
    pass


class Response(Markdown): 
    BORDER_TITLE = "Agent TUI"


class FunctionCalls(Log):
    BORDER_TITLE = "Function Calls"


# TODO - implement widget with details about the model we're using
#   (i.e. model, prompt tokens, response tokens, prompt count, etc.)
class ModelMetrics(Log):
    pass


class AgentApp(App): 
    CSS_PATH = "grid_layout.tcss"
    AUTO_FOCUS = "Input"


    def compose(self) -> ComposeResult: 
        yield Header()
        with Container(id="app-grid"):
            with VerticalScroll(id="func-view"):
                yield FunctionCalls("No function calls")
            with Container(id="model-metrics"):
                yield ModelMetrics("Model metrics go here")
            with VerticalScroll(id="chat-view"):
                yield Response("Agent TUI at your service!")
        yield Input(placeholder="What can I help you with?")
        yield Footer()


    def on_mount(self) -> None: 
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
        messages = [
            types.Content(role="user", parts=[types.Part(text=prompt)]),
        ]
        prompt_count = 1
        while (prompt_count < 5):
            response_content = self.client.models.generate_content(
                model=gemini,
                contents=messages,
                config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
            )

            functions_called = []

            if not response_content.function_calls:
                self.call_from_thread(response.update, response_content.text)
                return

            # Call the functions
            function_responses = []
            for function_call_part in response_content.function_calls:
                function_response_part = call_function(function_call_part)
                # Update function call log widget
                self.update_function_call_log(f"calling function: {function_call_part}")

                if not function_response_part.parts[0].function_response.response:
                    self.update_function_call_log("empty function call response")
                    raise Exception("empty function call response")

                function_responses.append(function_response_part.parts[0])

            if not function_responses:
                self.update_function_call_log("no function responses generated")
                raise Exception("no function responses generated, exiting.")

            if not response_content.candidates:
                self.update_function_call_log("no response candidates received from the model")
                raise Exception("no response candidates received from the model")
            else:
                # Append function response candidates back to the prompt
                for function_response_candidate in response_content.candidates:
                    # Append content from the model's response
                    messages.append(function_response_candidate.content)
                    # Append function responses
                    messages.append(types.Content(role="tool", parts=function_responses))

            prompt_count += 1


    def update_function_call_log(self, function_calls: str) -> None:
        func_log = self.query_one(FunctionCalls)
        #func_log.clear()
        func_log.write_line(function_calls)





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
