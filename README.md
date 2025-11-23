# TECECE - API Specification Change Detector

A Python application that automatically detects changes in GitHub API specifications using [oasdiff](https://github.com/oasdiff/oasdiff) and triggers webhook notifications to external systems.

## Features

- **Powered by oasdiff**: Uses the industry-standard oasdiff tool for OpenAPI diff detection
- **Breaking Changes Detection**: Automatically identifies breaking changes vs non-breaking changes
- **Comprehensive Change Analysis**: Generates detailed changelogs with structured reporting
- **Rich Webhook Notifications**: Sends detailed notifications including:
  - Breaking changes with severity levels
  - Full changelog text and structured entries
  - Complete current API specification
  - Summary statistics and metadata
- **Secure Webhook Delivery**: HMAC signature verification for webhook security
- **Flexible Scheduling**: Configurable monitoring intervals
- **Comprehensive Logging**: Detailed activity logs for monitoring and debugging

## Prerequisites

### Required Dependencies

1. **Python 3.7+** with pip
2. **oasdiff** - The OpenAPI diff tool that powers change detection

### Installing oasdiff

Choose one of the following installation methods:

**For Go users:**
```bash
go install github.com/oasdiff/oasdiff@latest
```

**For macOS users with Homebrew:**
```bash
brew tap oasdiff/homebrew-oasdiff
brew install oasdiff
```

**For Linux/macOS users with curl:**
```bash
curl -fsSL https://raw.githubusercontent.com/oasdiff/oasdiff/main/install.sh | sh
```

**Manual installation:**
Download binaries from the [oasdiff releases page](https://github.com/oasdiff/oasdiff/releases)

Verify installation:
```bash
oasdiff --version
```

## Setup and Installation

1. **Clone this repository**
   ```bash
   git clone <repository-url>
   cd tecece
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** with the following settings:
   ```env
   # GitHub API Specification URL
   GITHUB_API_SPEC_URL=https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json

   # Storage Directory for API Specifications
   SPEC_STORAGE_DIR=api_specs

   # Webhook Configuration
   WEBHOOK_URL=http://localhost:8001/webhook
   WEBHOOK_SECRET=your_webhook_secret_here

   # Scheduler Configuration (check interval in minutes)
   CHECK_INTERVAL_MINUTES=60

   # oasdiff Configuration
   OASDIFF_PATH=oasdiff
   OASDIFF_TIMEOUT=30

   # Logging Configuration
   LOG_LEVEL=INFO
   LOG_FILE=logs/api_spec_monitor.log

   # Application Configuration
   DEBUG_MODE=False

   # Webhook Server Configuration (for demo purposes)
   WEBHOOK_SERVER_HOST=127.0.0.1
   WEBHOOK_SERVER_PORT=8001
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

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
1. Check if oasdiff is properly installed
2. Start a webhook server to receive notifications
3. Create a sample API specification (or use an existing one)
4. Simulate realistic changes including breaking changes
5. Trigger the notification process using oasdiff
6. Display the structured webhook payload

The demo creates realistic breaking changes such as:
- Making optional parameters required
- Removing properties from schemas
- Adding new required properties

## Webhook Notification Format

The application sends webhook notifications with a rich, structured format:

```json
{
  "event_type": "api_spec_change",
  "timestamp": "2024-01-15T10:30:00.123456",
  "source": "github_api_spec_monitor",
  
  "summary": "⚠️ 3 breaking change(s) detected | 📝 7 total changes",
  "has_breaking_changes": true,
  
  "breaking_changes": {
    "count": 3,
    "changes": [
      {
        "id": "request-parameter-became-required",
        "text": "added required request parameter 'status'",
        "level": "error",
        "operation": "GET /users",
        "path": "/users",
        "source": "request.parameter.required"
      }
    ]
  },
  
  "changelog": {
    "text": "### What's Changed\n- Added new endpoint\n- Breaking change in user schema",
    "lines": [
      {"type": "heading", "text": "What's Changed"},
      {"type": "item", "text": "Added new endpoint"},
      {"type": "item", "text": "Breaking change in user schema"}
    ]
  },
  
  "current_spec": {
    "content": { /* Complete OpenAPI specification */ },
    "info": {
      "title": "GitHub API",
      "version": "1.1.4",
      "paths_count": 150,
      "operations_count": 800,
      "operations_by_method": {"GET": 400, "POST": 200, "PUT": 100, "DELETE": 100},
      "components": {"schemas": 200, "parameters": 50, "responses": 30},
      "security_schemes": ["bearer", "oauth2"],
      "servers": ["https://api.github.com"]
    }
  },
  
  "metadata": {
    "spec_source": "https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json",
    "monitor_version": "2.0.0",
    "diff_tool": "oasdiff",
    "notification_id": "notify_1642248600_1234"
  }
}
```

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
- Unit tests for the `APISpecDiffDetector` class with mocked oasdiff calls
- Integration tests that use real oasdiff (if available)
- Edge case handling tests
- Mock-based tests for external dependencies
- Coverage of all major functionality

## How It Works

1. **Fetching**: The application fetches the GitHub API specification from the specified URL
2. **Comparison**: It uses oasdiff to compare the fetched specification with the previously stored version
3. **Analysis**: oasdiff identifies breaking changes and generates comprehensive changelogs
4. **Notification**: If changes are detected, it sends a structured webhook notification
5. **Processing**: The external system can process the rich notification data to update its services

## Architecture

The application follows a modular architecture:

- `main.py`: Application entry point and scheduler
- `api_fetcher.py`: Fetches and stores API specifications
- `diff_detector.py`: Uses oasdiff to detect changes and breaking changes
- `webhook_notifier.py`: Sends structured webhook notifications
- `webhook_server.py`: Demo server to receive notifications
- `config.py`: Configuration settings
- `utils.py`: Utility functions
- `demo.py`: Comprehensive demonstration script
- `test_diff_detector.py`: Unit and integration tests

## Benefits of Using oasdiff

- **Industry Standard**: oasdiff is the leading tool for OpenAPI change detection
- **Comprehensive Analysis**: Detects all types of breaking changes according to OpenAPI best practices
- **Structured Output**: Provides machine-readable change descriptions
- **Active Development**: Continuously updated with new change detection capabilities
- **Proven Reliability**: Used by major API providers and platforms

## Troubleshooting

**oasdiff not found error:**
- Ensure oasdiff is installed and available in your PATH
- Try specifying the full path in the `OASDIFF_PATH` environment variable
- Verify installation with `oasdiff --version`

**No changes detected:**
- Check that the API specification URL is accessible
- Verify the oasdiff timeout setting if dealing with large specifications
- Enable DEBUG_MODE for more detailed logging

For more information about oasdiff capabilities, visit: https://github.com/oasdiff/oasdiff