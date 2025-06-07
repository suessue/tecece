# TECECE - API Specification Change Detector

A Python application that automatically detects changes in GitHub API specifications and triggers webhook notifications to external systems.

## Features

- Periodically fetches the GitHub API specification
- Detects changes between specification versions
- Sends webhook notifications when changes are detected
- Logs all activities for monitoring

## Setup and Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with the following settings:
```
# GitHub API Specification URL
GITHUB_API_SPEC_URL=https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json

# Storage Directory for API Specifications
SPEC_STORAGE_DIR=api_specs

# Webhook Configuration
WEBHOOK_URL=http://localhost:8000/webhook
WEBHOOK_SECRET=your_webhook_secret_here

# Scheduler Configuration (check interval in minutes)
CHECK_INTERVAL_MINUTES=60

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/api_spec_monitor.log

# Application Configuration
DEBUG_MODE=False

# Webhook Server Configuration (for demo purposes)
WEBHOOK_SERVER_HOST=127.0.0.1
WEBHOOK_SERVER_PORT=8000
```
4. Run the application: `python main.py`

## Usage

You can run the application in various modes:

```bash
# Run with continuous monitoring
python main.py

# Run with continuous monitoring and a demo webhook server
python main.py --webhook-server

# Perform a single check and exit
python main.py --check-now

# Run with a custom check interval
python main.py --interval 15
```

## Demo

For quick demonstration purposes, run the included demo script:

```bash
python demo.py
```

This script will:
1. Start a webhook server to receive notifications
2. Create a sample API specification (or use an existing one)
3. Simulate changes to the specification
4. Trigger the notification process
5. Display the results

The demo is useful for testing that everything is set up correctly without having to wait for actual GitHub API changes.

## Testing

Run the unit tests to verify the application is working correctly:

```bash
# Run all tests
python run_tests.py

# Or run specific test files
python -m unittest test_diff_detector.py

# Run tests with more verbose output
python -m unittest -v test_diff_detector.py
```

The test suite includes:
- Unit tests for the `APISpecDiffDetector` class
- Edge case handling tests
- Mock-based tests for external dependencies
- Coverage of all major functionality

## How It Works

1. The application fetches the GitHub API specification from the specified URL
2. It compares the fetched specification with the previously stored version
3. If changes are detected, it sends a webhook notification to the specified endpoint
4. The external system can process the notification to update its services

## Project Structure

- `main.py`: Application entry point
- `api_fetcher.py`: Fetches API specifications
- `diff_detector.py`: Detects differences between specifications
- `webhook_notifier.py`: Sends webhook notifications
- `webhook_server.py`: Demo server to receive notifications
- `config.py`: Configuration settings
- `utils.py`: Utility functions
- `demo.py`: Demonstration script
- `test_diff_detector.py`: Unit tests for diff detection
- `run_tests.py`: Test runner script