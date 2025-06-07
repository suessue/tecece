import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub API specification URL
# GitHub OpenAPI specification is available at: https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json
GITHUB_API_SPEC_URL = os.getenv('GITHUB_API_SPEC_URL', 'https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json')

# Local storage for API specifications
SPEC_STORAGE_DIR = os.getenv('SPEC_STORAGE_DIR', 'api_specs')
CURRENT_SPEC_PATH = os.path.join(SPEC_STORAGE_DIR, 'current_spec.json')
PREVIOUS_SPEC_PATH = os.path.join(SPEC_STORAGE_DIR, 'previous_spec.json')

# Webhook configuration
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:8000/webhook')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your_webhook_secret')

# Scheduler configuration
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '60'))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'api_spec_monitor.log')

# Application configuration
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Webhook Server configuration (for demo purposes)
WEBHOOK_SERVER_HOST = os.getenv('WEBHOOK_SERVER_HOST', '127.0.0.1')
WEBHOOK_SERVER_PORT = int(os.getenv('WEBHOOK_SERVER_PORT', '8000')) 