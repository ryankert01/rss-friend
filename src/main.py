"""Main entry point for RSS Friend aggregator."""

from pathlib import Path
from rss_aggregator import aggregate_rss_feeds

# Constants
ASSETS_DIR = Path(__file__).parent / 'assets'
MAX_POSTS = 30
FRIENDS_JSON_PATH = Path(__file__).parent.parent / '_data' / 'friends.json'


def main():
    """Main entry point."""
    try:
        aggregate_rss_feeds(FRIENDS_JSON_PATH, ASSETS_DIR, MAX_POSTS)
    except Exception as e:
        print(f"Main process failed: {e}")


if __name__ == "__main__":
    main()
