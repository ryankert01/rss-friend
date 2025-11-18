# Contributing to RSS Friend

Thank you for your interest in contributing to RSS Friend!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ryankert01/rss-friend.git
   cd rss-friend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage report:
```bash
pytest --cov=src --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_rss_aggregator.py
```

Run specific test:
```bash
pytest tests/test_rss_aggregator.py::TestParseRssFeed::test_parses_valid_rss_feed
```

## Code Style

- Follow PEP 8 style guidelines
- Write descriptive docstrings for all functions
- Add type hints where appropriate
- Keep functions small and focused

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass locally
5. Update documentation as needed
6. Submit a pull request

The CI will automatically:
- Run tests on Python 3.11
- Generate coverage reports
- Check code quality

## Testing Guidelines

- Write tests for all new functions
- Test edge cases and error conditions
- Use mocking for external dependencies (HTTP requests, etc.)
- Aim for high code coverage (>90%)

## Questions?

Feel free to open an issue if you have questions or need help!
