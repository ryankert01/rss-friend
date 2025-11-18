"""RSS Feed Aggregation Module."""

import json
import time
from pathlib import Path
import feedparser
import requests


def ensure_directory_exists(dir_path: Path):
    """Ensures a directory exists, creating it if necessary."""
    dir_path.mkdir(parents=True, exist_ok=True)


def write_json_file(file_path: Path, data):
    """Writes data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_rss_feed(friend: dict) -> list:
    """Parses a single RSS feed.
    
    Args:
        friend: Dictionary containing 'title', 'link', and 'feed' keys
        
    Returns:
        List of post dictionaries with title, link, date, and author
    """
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


def load_friends(friends_json_path: Path) -> list:
    """Loads friends data from JSON file.
    
    Args:
        friends_json_path: Path to friends.json file
        
    Returns:
        List of friend dictionaries
    """
    with open(friends_json_path, 'r', encoding='utf-8') as f:
        friends = json.load(f)
    
    if not isinstance(friends, list):
        raise ValueError("Friends data must be a list")
    
    return friends


def sort_posts_by_date(posts: list, max_posts: int = None) -> list:
    """Sorts posts by date (newest first).
    
    Args:
        posts: List of post dictionaries
        max_posts: Maximum number of posts to return (optional)
        
    Returns:
        Sorted list of posts
    """
    sorted_posts = sorted(posts, key=lambda x: x['date'], reverse=True)
    if max_posts:
        return sorted_posts[:max_posts]
    return sorted_posts


def format_posts_with_date_parts(posts: list) -> list:
    """Formats posts with separate year, month, day fields.
    
    Args:
        posts: List of post dictionaries with 'date' field
        
    Returns:
        List of formatted posts with year, month, day fields
    """
    formatted_posts = []
    for post in posts:
        t = time.strptime(post['date'], '%Y-%m-%dT%H:%M:%SZ')
        formatted_posts.append({
            "title": post["title"],
            "link": post["link"],
            "year": t.tm_year,
            "month": t.tm_mon,
            "day": t.tm_mday,
            "author": post["author"]
        })
    return formatted_posts


def aggregate_rss_feeds(friends_json_path: Path, assets_dir: Path, max_posts: int = 30):
    """Aggregates RSS feeds from a list of friends.
    
    Args:
        friends_json_path: Path to friends.json file
        assets_dir: Directory to save output files
        max_posts: Maximum number of posts to save in sorted output
    """
    ensure_directory_exists(assets_dir)

    friends = load_friends(friends_json_path)

    if not friends:
        print("No valid friends data found.")
        return

    all_posts = []
    for friend in friends:
        all_posts.extend(parse_rss_feed(friend))

    write_json_file(assets_dir / 'unsort.json', all_posts)

    # Sort posts by date (newest first)
    sorted_posts = sort_posts_by_date(all_posts, max_posts)
    write_json_file(assets_dir / 'sorted.json', sorted_posts)

    # Format posts
    formatted_posts = format_posts_with_date_parts(sorted_posts)
    write_json_file(assets_dir / 'rss.json', formatted_posts)

    print(f"Processing complete - Aggregated {len(all_posts)} posts, saved the top {len(sorted_posts)}.")
