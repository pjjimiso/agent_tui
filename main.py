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
from textual.reactive import reactive
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Markdown, Input, Header, Footer, Log, Sparkline, Pretty

from dotenv import load_dotenv
from google import genai
from google.genai import types
from models import gemini

from prompts import system_prompt
from functions.call_function import available_functions, call_function


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API Key could not be provided from GEMINI_API_KEY environment variable")


class Prompt(Markdown):
    pass


class Response(Markdown):
    pass


class ChatView(VerticalScroll):
    BORDER_TITLE = "Agent Chat"


class FunctionCalls(Log):
    BORDER_TITLE = "Function Calls"


class ModelMetadata(Container):
    BORDER_TITLE = "Model Metadata"

    metadata = reactive(
        {
            "Model": gemini,
            "Prompt Tokens Consumed": 0, 
            "Response Tokens Consumed": 0
        },
        recompose = True
    )

    def compose(self) -> ComposeResult:
        self.model_metadata = Pretty(self.metadata)
        yield self.model_metadata

    def update_prompt_token_count(self, token_count: int) -> None:
        self.metadata["Prompt Tokens Consumed"] += token_count
        self.model_metadata.update(self.metadata)

    def update_response_token_count(self, token_count: int) -> None:
        self.metadata["Response Tokens Consumed"] += token_count
        self.model_metadata.update(self.metadata)


class ModelTokenUsage(Container):
    BORDER_TITLE = "Prompt Tokens Used"
    sparkline_length = 30 # 60 seconds (30 datapoints @ 2sec intervals)
    tokens_this_interval = 0

    def compose(self) -> ComposeResult:
        """
        Initialize sparkline to 0's so we have a fixed
        number of columns with even width from the start
        """
        self.sparkline = Sparkline(
            [0 for _ in range(30)],
            summary_function=max,
        )
        yield self.sparkline

    def on_mount(self) -> None: 
        self.set_interval(2, self.update_token_count)

    def update_token_count(self) -> None:
        current_data = list(self.sparkline.data)
        if len(current_data) >= 30:
            current_data.pop(0)
        current_data.append(self.tokens_this_interval)
        self.sparkline.data = current_data
        self.tokens_this_interval = 0



class AgentApp(App): 
    CSS_PATH = "app-layout.tcss"
    AUTO_FOCUS = "Input"


    def compose(self) -> ComposeResult: 
        yield Header()
        with Container(id="app-grid"):
            with VerticalScroll(id="func-view"):
                self.func_calls = FunctionCalls()
                yield self.func_calls
            with Container(id="model-metrics"):
                yield ModelMetadata(id="model-metadata")
                yield ModelTokenUsage()
            with ChatView(id="chat-view"):
                yield Response("What can I help you with?")
        yield Input(placeholder="What functions can you perform?")
        yield Footer()

    def on_mount(self) -> None:
        self.client = genai.Client(api_key=api_key)
        self.chat = self.client.chats.create(model=gemini)

    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted) -> None:
        chat_view = self.query_one("#chat-view")
        event.input.clear()
        await chat_view.mount(Prompt(event.value))
        await chat_view.mount(response := Response())
        chat_view.scroll_end(animate=False)
        self.send_prompt(event.value, response)

    @work(thread=True)
    def send_prompt(self, prompt: str, response: Response) -> None: 
        response_content = self.chat.send_message(
            types.Part(text=prompt),
            config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        )

        prompt_count = 1
        while (prompt_count < 20):

            if response_content.usage_metadata:
                self.action_update_token_counts(str(response_content.usage_metadata))

            if not response_content.function_calls:
                self.call_from_thread(response.update, response_content.text)
                self.scroll_chat_to_bottom()
                return

            # Call the functions
            function_responses = []
            for function_call_part in response_content.function_calls:
                # Update function call log widget
                if function_call_part.args:
                    self.update_function_call_log(f"{function_call_part.name}({function_call_part.args})")
                else:
                    self.update_function_call_log(f"{function_call_part.name}()")
                
                # Call the functions
                function_response_part = call_function(function_call_part)

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
                #for function_response_candidate in response_content.candidates:
                    # messages.append(function_response_candidate.content)
                response_content = self.chat.send_message(function_responses)

            prompt_count += 1

    def scroll_chat_to_bottom(self) -> None:
        chat_view = self.query_one("#chat-view")
        chat_view.scroll_end(animate=False)

    def update_function_call_log(self, function_calls: str) -> None:
        func_log = self.query_one(FunctionCalls)
        #func_log.clear()
        func_log.write_line(function_calls)

    def action_update_token_counts(self, response_metadata: str) -> None:
        # Parse prompt and response token count from response_metadata
        prompt_match = re.search(r'prompt_token_count=(\d+)', response_metadata)
        prompt_token_count = int(prompt_match.group(1)) if prompt_match else 0
        response_match = re.search(r'candidates_token_count=(\d+)', response_metadata)
        response_token_count = int(response_match.group(1)) if response_match else 0

        # Update our tracked token counts in ModelMetrics widget 
        model_metadata = self.query_one(ModelMetadata)
        model_metadata.update_prompt_token_count(prompt_token_count)
        model_metadata.update_response_token_count(response_token_count)

        # Update ModelTokenUsage sparkline with this interval's combined token usage
        model_token_usage = self.query_one(ModelTokenUsage)
        model_token_usage.tokens_this_interval = prompt_token_count + response_token_count


def main():

    app = AgentApp()
    app.run()


if __name__ == "__main__":
    main()
