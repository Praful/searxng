This repo runs SearXNG in a Docker container.

## Installation

1. Start your terminal.
2. `cd projects` or wherever you store your projects.
3. `git clone https://github.com/Praful/searxng.git`
4. `cd searxng`
5. `run.sh`
6. Go to http://localhost:8888 in browser

Scripts:

- run.sh - Start SearXNG in a Docker container.
- search.py - Search SearXNG from terminal: `python ./search.py "query"`
- tui_search.py - Search SearXNG from terminal using TUI: `python ./tui_search.py`

If you're using `uv` ([installation guide](https://docs.astral.sh/uv/getting-started/installation/)), the dependencies will be installed automatically:

```
uv run search.py "query"
```

and

```
uv run tui_search.py
```

If you're not using `uv`, you'll need to install the dependencies manually:

```
pip install -r requirements.txt
```

For more information see SearXNG [website](https://docs.searxng.org/admin/installation-docker.html).
