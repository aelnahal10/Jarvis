import webbrowser

def youtube_search(query):
    """Searches YouTube and opens the first result."""
    webbrowser.open(f'https://www.youtube.com/results?search_query={query}')
