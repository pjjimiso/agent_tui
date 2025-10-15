# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "textual",
# ]
# ///

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Markdown, Input, Placeholder, Header, Footer


class Prompt(Markdown):
    pass



class Response(Markdown): 
    BORDER_TITLE = "Agent TUI"


# TODO - implement widget with details about the model we're using
class ModelDetails(Placeholder):
    pass


class AgentApp(App): 
    AUTO_FOCUS = "Input"

    def compose(self) -> ComposeResult: 
        yield Header()
        with VerticalScroll(id="chat-view"):
            yield Response("Hello there")
        yield Input(placeholder="What can I help you with?")
        yield Footer()

    def on_mount(self) -> None: 
        pass

    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted) -> None:
        chat_view = self.query_one("#chat-view")
        event.input.clear()
        await chat_view.mount(Prompt(event.value))
        await chat_view.mount(response := Response())
        response.anchor()
        self.send_prompt(event.value, response)

    # TODO - chunk llm response and update response_content
    @work(thread=True)
    def send_prompt(self, prompt: str, response: Response) -> None: 
        response_content = "can a robot learn to love?"
        self.call_from_thread(response.update, response_content)


def main():
    app = AgentApp()
    app.run()


if __name__ == "__main__":
    main()
