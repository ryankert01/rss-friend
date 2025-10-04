
import json
import os
import time
from pathlib import Path
import feedparser
import requests

# Constants
ASSETS_DIR = Path(__file__).parent / 'assets'
MAX_POSTS = 30
FRIENDS_JSON_PATH = Path(__file__).parent.parent / '_data' / 'friends.json'

def ensure_directory_exists(dir_path: Path):
    """Ensures a directory exists, creating it if necessary."""
    dir_path.mkdir(parents=True, exist_ok=True)

def write_json_file(file_path: Path, data):
    """Writes data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_rss_feed(friend: dict) -> list:
    """Parses a single RSS feed."""
    friend_name = friend.get("title", "")
    friend_link = friend.get("link", "")
    rss_url = friend.get("feed", "")
    posts = []

    if not rss_url or not rss_url.startswith('http'):
        print(f"Invalid RSS URL: {rss_url} (from: {friend_name})")
        return []

    try:
        # Use requests to fetch the feed with a timeout and user-agent
        response = requests.get(rss_url, timeout=10, headers={'User-Agent': 'RSS Aggregator Bot'})
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the feed content using feedparser
        feed = feedparser.parse(response.content)

        for entry in feed.entries:
            # Get date
            date_tuple = entry.get("published_parsed") or entry.get("updated_parsed") or time.gmtime()
            date = time.strftime('%Y-%m-%dT%H:%M:%SZ', date_tuple)

            posts.append({
                "title": entry.get("title", "No Title"),
                "link": entry.get("link", friend_link),
                "date": date,
                "author": {
                    "name": friend_name,
                    "link": friend_link
                }
            })
    except Exception as e:
        print(f"Failed to parse RSS feed ({friend_name} - {rss_url}): {e}")

    return posts

def aggregate_rss_feeds():
    """Aggregates RSS feeds from a list of friends."""
    try:
        ensure_directory_exists(ASSETS_DIR)

        with open(FRIENDS_JSON_PATH, 'r', encoding='utf-8') as f:
            friends = json.load(f)

        if not isinstance(friends, list) or not friends:
            print("No valid friends data found.")
            return

        all_posts = []
        for friend in friends:
            all_posts.extend(parse_rss_feed(friend))

        write_json_file(ASSETS_DIR / 'unsort.json', all_posts)

        # Sort posts by date (newest first)
        sorted_posts = sorted(all_posts, key=lambda x: x['date'], reverse=True)[:MAX_POSTS]
        write_json_file(ASSETS_DIR / 'sorted.json', sorted_posts)

        # Format posts
        formatted_posts = []
        for post in sorted_posts:
            t = time.strptime(post['date'], '%Y-%m-%dT%H:%M:%SZ')
            formatted_posts.append({
                "title": post["title"],
                "link": post["link"],
                "year": t.tm_year,
                "month": t.tm_mon,
                "day": t.tm_mday,
                "author": post["author"]
            })

        write_json_file(ASSETS_DIR / 'rss.json', formatted_posts)

        print(f"Processing complete - Aggregated {len(all_posts)} posts, saved the top {len(sorted_posts)}.")

    except Exception as e:
        print(f"Main process failed: {e}")

if __name__ == "__main__":
    aggregate_rss_feeds()
