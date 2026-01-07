# /// script
# dependencies = [
#   "requests",
#   "textual",
# ]
# ///

import subprocess
import requests
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ListItem, ListView, Static, Label
from textual.containers import Container


class SearchResult(ListItem):
    """A custom widget to display search results."""

    def __init__(self, title, url, snippet):
        super().__init__()
        self.title = title
        self.url = url
        self.snippet = snippet

    def compose(self) -> ComposeResult:
        yield Label(f"[b][orange]{self.title}[/orange][/b]")
        yield Label(f"[i]{self.url}[/i]")
        yield Label(f"{self.snippet[:100]}...", variant="dim")


class SearxTUI(App):
    # Standard CSS with valid border types
    CSS = """
    ListView { 
        margin: 1 2; 
        border: solid $accent; 
        height: 1fr; 
    }
    Input { 
        margin: 1 2; 
        border: tall $accent; 
    }
    SearchResult { 
        padding: 1; 
        border-bottom: solid $primary-darken-1; 
    }
    """

    # Updated Bindings: Added 'escape' and 'q' for quitting
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("l", "open_link", "Open"),
        ("/", "focus_search", "Search")
    ]

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def action_focus_search(self) -> None:
        search_input = self.query_one("#search_input", Input)
        search_input.focus()
        search_input.value = ""

    def _handle_selection(self, selected_item):
        """Unified logic for Enter and 'l' key."""
        if isinstance(selected_item, SearchResult):
            # Copy to Linux clipboard (requires xclip)
            subprocess.run(['xclip', '-selection', 'clipboard'],
                           input=selected_item.url.encode())
            # Fast open on Mint using xdg-open
            subprocess.Popen(['xdg-open', selected_item.url])
            self.notify(f"Opened & Copied: {selected_item.title}")

    def action_open_link(self) -> None:
        """Called when 'l' is pressed."""
        list_view = self.query_one("#results_list", ListView)
        if list_view.highlighted_child:
            self._handle_selection(list_view.highlighted_child)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when 'Enter' is pressed or item is clicked."""
        self._handle_selection(event.item)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search your local SearXNG...", id="search_input")
        yield ListView(id="results_list")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value
        results_list = self.query_one("#results_list", ListView)
        results_list.clear()

        try:
            response = requests.get("http://localhost:8888/search",
                                    params={'q': query, 'format': 'json'})
            results = response.json().get('results', [])

            for res in results[:10]:
                results_list.append(SearchResult(
                    res.get('title', 'No Title'),
                    res.get('url', ''),
                    res.get('content', '').replace(
                        '<b>', '').replace('</b>', '')
                ))
        except Exception as e:
            results_list.append(ListItem(Label(f"Error: {e}")))


if __name__ == "__main__":
    app = SearxTUI()
    app.run()
