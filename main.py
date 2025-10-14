# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "textual",
# ]
# ///

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Markdown, Input, Placeholder, Header, Footer


class Prompt(Markdown):

    def compose(self) -> ComposeResult: 
        yield Header()
        with VerticalScroll(id="chat-view"):
            yield Response("can a robot learn to love?")
        yield Input(placeholder="What can I help you with?")
        yield Footer()


class Response(Markdown): 
    BORDER_TITLE = "Agent TUI"


class ModelDetails(Placeholder):
    pass


class AgentApp(App): 

    def compose(self) -> ComposeResult:
        yield Prompt()


def main():
    app = AgentApp()
    app.run()


if __name__ == "__main__":
    main()
