"""Unit tests for RSS aggregator module."""

import json
import time
from unittest.mock import Mock, patch
import pytest

from src.rss_aggregator import (
    ensure_directory_exists,
    write_json_file,
    parse_rss_feed,
    load_friends,
    sort_posts_by_date,
    format_posts_with_date_parts,
    aggregate_rss_feeds
)


class TestEnsureDirectoryExists:
    """Tests for ensure_directory_exists function."""
    
    def test_creates_directory_if_not_exists(self, tmp_path):
        """Test that directory is created if it doesn't exist."""
        test_dir = tmp_path / "new_dir" / "nested"
        assert not test_dir.exists()
        
        ensure_directory_exists(test_dir)
        
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    def test_does_not_fail_if_directory_exists(self, tmp_path):
        """Test that function doesn't fail if directory already exists."""
        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()
        
        # Should not raise an exception
        ensure_directory_exists(test_dir)
        
        assert test_dir.exists()


class TestWriteJsonFile:
    """Tests for write_json_file function."""
    
    def test_writes_json_data_correctly(self, tmp_path):
        """Test that JSON data is written correctly."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        
        write_json_file(test_file, test_data)
        
        assert test_file.exists()
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    
    def test_writes_unicode_correctly(self, tmp_path):
        """Test that unicode characters are written correctly."""
        test_file = tmp_path / "unicode.json"
        test_data = {"chinese": "中文", "emoji": "🎉"}
        
        write_json_file(test_file, test_data)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "中文" in content
        assert "🎉" in content


class TestLoadFriends:
    """Tests for load_friends function."""
    
    def test_loads_valid_friends_json(self, tmp_path):
        """Test loading valid friends JSON file."""
        friends_file = tmp_path / "friends.json"
        friends_data = [
            {"title": "Blog 1", "link": "http://blog1.com", "feed": "http://blog1.com/feed"},
            {"title": "Blog 2", "link": "http://blog2.com", "feed": "http://blog2.com/feed"}
        ]
        
        with open(friends_file, 'w', encoding='utf-8') as f:
            json.dump(friends_data, f)
        
        result = load_friends(friends_file)
        
        assert result == friends_data
        assert len(result) == 2
    
    def test_raises_error_for_non_list(self, tmp_path):
        """Test that error is raised if friends data is not a list."""
        friends_file = tmp_path / "friends.json"
        
        with open(friends_file, 'w', encoding='utf-8') as f:
            json.dump({"not": "a list"}, f)
        
        with pytest.raises(ValueError, match="Friends data must be a list"):
            load_friends(friends_file)


class TestSortPostsByDate:
    """Tests for sort_posts_by_date function."""
    
    def test_sorts_posts_by_date_descending(self):
        """Test that posts are sorted by date in descending order."""
        posts = [
            {"title": "Old Post", "date": "2022-01-01T00:00:00Z"},
            {"title": "New Post", "date": "2023-01-01T00:00:00Z"},
            {"title": "Mid Post", "date": "2022-06-01T00:00:00Z"}
        ]
        
        result = sort_posts_by_date(posts)
        
        assert len(result) == 3
        assert result[0]["title"] == "New Post"
        assert result[1]["title"] == "Mid Post"
        assert result[2]["title"] == "Old Post"
    
    def test_limits_posts_when_max_posts_specified(self):
        """Test that max_posts parameter limits the number of returned posts."""
        posts = [
            {"title": f"Post {i}", "date": f"2023-{i:02d}-01T00:00:00Z"}
            for i in range(1, 11)
        ]
        
        result = sort_posts_by_date(posts, max_posts=5)
        
        assert len(result) == 5
    
    def test_handles_empty_list(self):
        """Test that empty list is handled correctly."""
        result = sort_posts_by_date([])
        
        assert result == []


class TestFormatPostsWithDateParts:
    """Tests for format_posts_with_date_parts function."""
    
    def test_formats_posts_correctly(self):
        """Test that posts are formatted with date parts."""
        posts = [
            {
                "title": "Test Post",
                "link": "http://example.com/post",
                "date": "2023-05-15T12:30:00Z",
                "author": {"name": "Author", "link": "http://example.com"}
            }
        ]
        
        result = format_posts_with_date_parts(posts)
        
        assert len(result) == 1
        assert result[0]["title"] == "Test Post"
        assert result[0]["link"] == "http://example.com/post"
        assert result[0]["year"] == 2023
        assert result[0]["month"] == 5
        assert result[0]["day"] == 15
        assert result[0]["author"] == {"name": "Author", "link": "http://example.com"}
        assert "date" not in result[0]
    
    def test_handles_multiple_posts(self):
        """Test formatting multiple posts."""
        posts = [
            {
                "title": f"Post {i}",
                "link": f"http://example.com/post{i}",
                "date": f"2023-{i:02d}-01T00:00:00Z",
                "author": {"name": "Author", "link": "http://example.com"}
            }
            for i in range(1, 4)
        ]
        
        result = format_posts_with_date_parts(posts)
        
        assert len(result) == 3
        for i, post in enumerate(result, 1):
            assert post["month"] == i


class TestParseRssFeed:
    """Tests for parse_rss_feed function."""
    
    def test_returns_empty_list_for_invalid_url(self, capsys):
        """Test that invalid URL returns empty list."""
        friend = {"title": "Test Blog", "link": "http://test.com", "feed": "not-a-url"}
        
        result = parse_rss_feed(friend)
        
        assert result == []
        captured = capsys.readouterr()
        assert "Invalid RSS URL" in captured.out
    
    def test_returns_empty_list_for_missing_feed(self):
        """Test that missing feed URL returns empty list."""
        friend = {"title": "Test Blog", "link": "http://test.com"}
        
        result = parse_rss_feed(friend)
        
        assert result == []
    
    @patch('src.rss_aggregator.requests.get')
    @patch('src.rss_aggregator.feedparser.parse')
    def test_parses_valid_rss_feed(self, mock_parse, mock_get):
        """Test parsing a valid RSS feed."""
        # Mock response
        mock_response = Mock()
        mock_response.content = b"<rss>...</rss>"
        mock_get.return_value = mock_response
        
        # Mock feed parser
        mock_entry = Mock()
        mock_entry.get.side_effect = lambda key, default=None: {
            "title": "Test Post",
            "link": "http://test.com/post1",
            "published_parsed": time.strptime("2023-05-15T12:00:00Z", '%Y-%m-%dT%H:%M:%SZ')
        }.get(key, default)
        
        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed
        
        friend = {
            "title": "Test Blog",
            "link": "http://test.com",
            "feed": "http://test.com/feed"
        }
        
        result = parse_rss_feed(friend)
        
        assert len(result) == 1
        assert result[0]["title"] == "Test Post"
        assert result[0]["link"] == "http://test.com/post1"
        assert result[0]["author"]["name"] == "Test Blog"
        assert result[0]["author"]["link"] == "http://test.com"
        assert "date" in result[0]
    
    @patch('src.rss_aggregator.requests.get')
    def test_handles_request_exception(self, mock_get, capsys):
        """Test handling of request exceptions."""
        mock_get.side_effect = Exception("Network error")
        
        friend = {
            "title": "Test Blog",
            "link": "http://test.com",
            "feed": "http://test.com/feed"
        }
        
        result = parse_rss_feed(friend)
        
        assert result == []
        captured = capsys.readouterr()
        assert "Failed to parse RSS feed" in captured.out


class TestAggregateRssFeeds:
    """Tests for aggregate_rss_feeds function."""
    
    @patch('src.rss_aggregator.parse_rss_feed')
    def test_aggregates_feeds_successfully(self, mock_parse, tmp_path):
        """Test successful aggregation of RSS feeds."""
        # Setup
        friends_file = tmp_path / "friends.json"
        assets_dir = tmp_path / "assets"
        
        friends_data = [
            {"title": "Blog 1", "link": "http://blog1.com", "feed": "http://blog1.com/feed"}
        ]
        
        with open(friends_file, 'w', encoding='utf-8') as f:
            json.dump(friends_data, f)
        
        # Mock RSS feed parsing
        mock_parse.return_value = [
            {
                "title": "Post 1",
                "link": "http://blog1.com/post1",
                "date": "2023-05-15T12:00:00Z",
                "author": {"name": "Blog 1", "link": "http://blog1.com"}
            }
        ]
        
        # Execute
        aggregate_rss_feeds(friends_file, assets_dir, max_posts=30)
        
        # Verify
        assert (assets_dir / "unsort.json").exists()
        assert (assets_dir / "sorted.json").exists()
        assert (assets_dir / "rss.json").exists()
        
        # Check content
        with open(assets_dir / "sorted.json", 'r', encoding='utf-8') as f:
            sorted_data = json.load(f)
        assert len(sorted_data) == 1
        assert sorted_data[0]["title"] == "Post 1"
        
        with open(assets_dir / "rss.json", 'r', encoding='utf-8') as f:
            rss_data = json.load(f)
        assert len(rss_data) == 1
        assert rss_data[0]["year"] == 2023
        assert rss_data[0]["month"] == 5
        assert rss_data[0]["day"] == 15
    
    def test_handles_empty_friends_list(self, tmp_path, capsys):
        """Test handling of empty friends list."""
        friends_file = tmp_path / "friends.json"
        assets_dir = tmp_path / "assets"
        
        with open(friends_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        aggregate_rss_feeds(friends_file, assets_dir, max_posts=30)
        
        captured = capsys.readouterr()
        assert "No valid friends data found" in captured.out
