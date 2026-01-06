import requests
import sys
import subprocess
from urllib.parse import quote

def copy_to_clipboard(text):
    try:
        process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
    except FileNotFoundError:
        print("\n\033[1;31m[!] xclip not found. Run: sudo apt install xclip\033[0m")

def searx_query(query, copy_first=False):
    base_url = "http://localhost:8888/search"
    params = {'q': query, 'format': 'json'}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json().get('results', [])

        if not results:
            print("No results found.")
            return

        print(f"\n--- Results for: {query} ---")
        
        # Copy the top URL if requested
        if copy_first:
            first_url = results[0].get('url')
            copy_to_clipboard(first_url)
            print(f"\033[1;34m[Clip] Copied top URL: {first_url}\033[0m\n")

        for i, res in enumerate(results[:5], 1):
            title = res.get('title')
            url = res.get('url')
            print(f"{i}. \033[1;32m{title}\033[0m\n   {url}\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ? <query> [--copy]")
    else:
        # Check if '--copy' is in the arguments
        args = sys.argv[1:]
        do_copy = "--copy" in args
        search_term = " ".join([a for a in args if a != "--copy"])
        searx_query(search_term, copy_first=do_copy)
