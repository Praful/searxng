# /// script
# dependencies = [
#   "requests",
#   "textual",
# ]
# ///
import os
import webbrowser
import subprocess
import requests
import sys
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ListItem, ListView, Label
from textual.containers import Container

class SearchResult(ListItem):

    """Widget to display numbered search results."""
    def __init__(self, title, url, snippet):
        super().__init__()
        self.title = title
        self.url = url
        self.snippet = snippet

    def compose(self) -> ComposeResult:
        yield Label(f"[b][orange]{self.title}[/orange][/b]")
        yield Label(f"[gray]{self.url}[/gray]")
        yield Label(f"{self.snippet[:120]}...", variant="dim")

class SearxTUI(App):
    # Port set to 8888 as requested
    SEARX_URL = "http://localhost:8888/search"

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

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("l", "open_link", "Open"),
        ("/", "focus_search", "Search"),
    ]

    def quick_notify(self, message: str, severity: str = "information"):
        self.notify(message, severity=severity, timeout=1.5)

    def __init__(self):
        super().__init__()
        self.current_urls = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search SearXNG (Port 8888)...", id="search_input")
        yield ListView(id="results_list")
        yield Footer()

    def on_key(self, event) -> None:
        """Handle 1-9 hotkeys for instant opening."""
        if event.key in "123456789":
            index = int(event.key) - 1
            if index < len(self.current_urls):
                self._handle_selection(self.current_urls[index], "Hotkey")

    def _handle_selection(self, data):
        """Handles selection whether 'data' is a string URL or a SearchResult object."""
        # If data is a SearchResult object, get its url; otherwise assume data is the url
        url = getattr(data, 'url', data)
        title = getattr(data, 'title', "Link")

        if isinstance(url, str) and url.startswith("http"):
            # 1. Copy to clipboard
            subprocess.run(['xclip', '-selection', 'clipboard'], input=url.encode())
            
            # 2. Open via xdg-open but silence the Flatpak/GTK errors
            # We use Popen with DEVNULL to kill the terminal chatter
            subprocess.Popen(
                ['xdg-open', url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.quick_notify(f"Opened: {title}")
        else:
            self.notify(f"Invalid selection: {type(data).__name__}", severity="error")


    def action_open_link(self) -> None:
        """Triggered by the 'l' key."""
        list_view = self.query_one("#results_list", ListView)
        if list_view.highlighted_child:
            # Pass the highlighted child to our selection handler
            self._handle_selection(list_view.highlighted_child)

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def action_focus_search(self) -> None:
        input_widget = self.query_one("#search_input", Input)
        input_widget.value = ""
        input_widget.focus()


    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Logic for 'Enter' key."""
        if isinstance(event.item, SearchResult):
            self._handle_selection(event.item.url)
    # Updated Search Logic with safety checks
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value
        if not query:
            return

        results_list = self.query_one("#results_list", ListView)
        results_list.clear()
        self.current_urls = []

        # Show a loading notification
        # comment out: stays too long
        #  self.notify(f"Searching for: {query}...", title="SearXNG")

        try:
            # Reduced timeout for snappier feedback
            response = requests.get(
                self.SEARX_URL, 
                params={'q': query, 'format': 'json'}, 
                timeout=5
            )
            response.raise_for_status()
            results = response.json().get('results', [])

            if not results:
                self.notify("No results found.", severity="warning")
                return

            for i, res in enumerate(results[:9]):
                url = res.get('url', '')
                self.current_urls.append(url)
                
                display_title = f"[{i+1}] {res.get('title', 'No Title')}"
                # Clean up HTML tags from SearXNG snippets
                snippet = res.get('content', '').replace('<b>', '').replace('</b>', '')
                
                results_list.append(SearchResult(display_title, url, snippet))
            
            results_list.focus()

        except requests.exceptions.ConnectionError:
            self.notify("Could not connect to SearXNG. Is the container running on port 8888?", severity="error")
        except Exception as e:
            self.notify(f"Search failed: {str(e)}", severity="error")

if __name__ == "__main__":
    app = SearxTUI()
    app.run()

