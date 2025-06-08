#!/usr/bin/env python3
"""
Demo script to demonstrate the API Specification Change Monitor using oasdiff.
This script simulates a change in the API specification and triggers the notification process.
"""

import os

# Set up demo environment variables BEFORE importing other modules
# This prevents authorization issues by ensuring consistent webhook secrets
def setup_demo_environment():
    """Set up environment variables for demo to avoid configuration issues."""
    demo_env = {
        'WEBHOOK_SECRET': 'demo_webhook_secret_12345',
        'WEBHOOK_URL': 'http://localhost:8000/webhook',
        'WEBHOOK_SERVER_HOST': '127.0.0.1',
        'WEBHOOK_SERVER_PORT': '8000',
        'SPEC_STORAGE_DIR': 'api_specs'
    }
    
    print("Setting up demo environment...")
    for key, value in demo_env.items():
        os.environ[key] = value
        print(f"  {key} = {value}")
    
    return demo_env

# Set up environment BEFORE importing other modules
demo_env = setup_demo_environment()

import json
import time
import threading

from main import APISpecMonitor
from webhook_server import start_server
import utils
import config

def start_webhook_server():
    """Start the webhook server in a separate thread."""
    print("Starting webhook server...")
    try:
        webhook_thread = threading.Thread(target=start_server)
        webhook_thread.daemon = True
        webhook_thread.start()
        
        # Give the server time to start
        time.sleep(2)
        print("✓ Webhook server is running.")
        return webhook_thread
    except Exception as e:
        print(f"✗ Error starting webhook server: {e}")
        print("Continuing with demo, but webhook notifications may not be received.")
        return None

def simulate_api_spec_change():
    """Simulate a change in the API specification that includes breaking changes."""
    print("\nSimulating API specification change...")
    
    # Ensure the API specs directory exists
    utils.ensure_directory_exists(config.SPEC_STORAGE_DIR)
    
    # Check if we already have a current spec file
    current_spec_exists = os.path.exists(config.CURRENT_SPEC_PATH)
    
    if not current_spec_exists:
        print("No current specification found. Creating a sample specification...")
        # Create a simple API spec
        sample_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Sample API",
                "version": "1.0.0",
                "description": "A sample API for demonstration purposes"
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get all users",
                        "parameters": [
                            {
                                "name": "page",
                                "in": "query",
                                "required": False,
                                "schema": {
                                    "type": "integer",
                                    "default": 1
                                },
                                "description": "Page number"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "users": {
                                                    "type": "array",
                                                    "items": {
                                                        "$ref": "#/components/schemas/User"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "required": ["id", "name"],
                        "properties": {
                            "id": {
                                "type": "integer",
                                "format": "int64"
                            },
                            "name": {
                                "type": "string"
                            },
                            "email": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }
        
        # Save it as the current spec
        utils.save_json_to_file(sample_spec, config.CURRENT_SPEC_PATH)
        print("Sample specification created.")
        
        # Create a copy for modification
        modified_spec = json.loads(json.dumps(sample_spec))
    else:
        print("Loading existing specification...")
        # Load the current spec
        with open(config.CURRENT_SPEC_PATH, 'r') as f:
            sample_spec = json.load(f)
        
        # Create a copy for modification
        modified_spec = json.loads(json.dumps(sample_spec))
    
    print("Creating specification with breaking changes for demo...")
    
    # Simulate BREAKING CHANGES that oasdiff will detect:
    
    # 1. Make an optional parameter required (breaking change)
    if "paths" in modified_spec and "/users" in modified_spec["paths"]:
        if "get" in modified_spec["paths"]["/users"]:
            for param in modified_spec["paths"]["/users"]["get"].get("parameters", []):
                if param["name"] == "page":
                    param["required"] = True  # This is a breaking change
                    print("  - Made 'page' parameter required (BREAKING)")
    
    # 2. Remove a property from response schema (breaking change)
    if "components" in modified_spec and "schemas" in modified_spec["components"]:
        if "User" in modified_spec["components"]["schemas"]:
            user_schema = modified_spec["components"]["schemas"]["User"]
            if "email" in user_schema.get("properties", {}):
                del user_schema["properties"]["email"]
                print("  - Removed 'email' property from User schema (BREAKING)")
    
    # 3. Add a new required property (breaking change)
    if "components" in modified_spec and "schemas" in modified_spec["components"]:
        if "User" in modified_spec["components"]["schemas"]:
            user_schema = modified_spec["components"]["schemas"]["User"]
            user_schema["properties"]["status"] = {
                "type": "string",
                "enum": ["active", "inactive"]
            }
            user_schema["required"].append("status")
            print("  - Added required 'status' property to User schema (BREAKING)")
    
    # 4. Add new non-breaking changes
    
    # Add a new endpoint (non-breaking)
    modified_spec["paths"]["/products"] = {
        "get": {
            "summary": "Get all products",
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "products": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Product"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    print("  - Added new /products endpoint (non-breaking)")
    
    # Add new schema for Product
    modified_spec["components"]["schemas"]["Product"] = {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64"
            },
            "name": {
                "type": "string"
            },
            "price": {
                "type": "number",
                "format": "float"
            }
        }
    }
    print("  - Added Product schema (non-breaking)")
    
    # Add POST endpoint to users (non-breaking)
    modified_spec["paths"]["/users"]["post"] = {
        "summary": "Create a new user",
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/User"
                    }
                }
            }
        },
        "responses": {
            "201": {
                "description": "User created successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/User"
                        }
                    }
                }
            },
            "400": {
                "description": "Bad Request"
            }
        }
    }
    print("  - Added POST /users endpoint (non-breaking)")
    
    # Update the info version
    if "info" in modified_spec:
        modified_spec["info"]["version"] = "2.0.0"
        modified_spec["info"]["description"] = "A sample API for demonstration purposes (updated with breaking changes)"
    
    # Save the modified spec to a temporary file
    temp_spec_path = os.path.join(config.SPEC_STORAGE_DIR, "temp_modified_spec.json")
    utils.save_json_to_file(modified_spec, temp_spec_path)
    
    print("Specification modification completed with breaking and non-breaking changes.")
    return temp_spec_path

def run_demo():
    """Run the complete demo process."""
    print("=== API Specification Change Monitor Demo (using oasdiff) ===")
    print()
    
    # Demo environment was already set up during module import
    print(f"✓ Demo environment configured with webhook secret: {demo_env['WEBHOOK_SECRET']}")
    print(f"✓ Config module webhook secret: {config.WEBHOOK_SECRET}")
    
    # Double-check that the configuration is properly loaded
    if config.WEBHOOK_SECRET != demo_env['WEBHOOK_SECRET']:
        print(f"⚠ Warning: Config mismatch detected. Overriding...")
        config.WEBHOOK_SECRET = demo_env['WEBHOOK_SECRET']
    
    # Check if oasdiff is available
    try:
        from diff_detector import APISpecDiffDetector
        detector = APISpecDiffDetector()
        print("✓ oasdiff is available and ready to use")
    except RuntimeError as e:
        print(f"✗ Error: {e}")
        print("\nPlease install oasdiff first:")
        print("  Go users: go install github.com/oasdiff/oasdiff@latest")
        print("  macOS users: brew tap oasdiff/homebrew-oasdiff && brew install oasdiff")
        print("  Or see: https://github.com/oasdiff/oasdiff#installation")
        return
    
    # Start the webhook server
    webhook_thread = start_webhook_server()
    
    # Create an instance of the API monitor
    monitor = APISpecMonitor()
    
    # Ensure the webhook notifier uses the correct webhook secret
    monitor.notifier.webhook_secret = demo_env['WEBHOOK_SECRET']
    print(f"✓ Monitor webhook notifier secret set to: {monitor.notifier.webhook_secret}")
    
    # Simulate a change in the API specification
    modified_spec_path = simulate_api_spec_change()
    
    # Override the fetch_current_spec method to return our modified spec
    original_fetch = monitor.fetcher.fetch_current_spec
    
    def mocked_fetch():
        print("Fetching 'remote' API specification (mocked)...")
        with open(modified_spec_path, 'r') as f:
            return json.load(f)
    
    # Replace the fetch method with our mock
    monitor.fetcher.fetch_current_spec = mocked_fetch
    
    # Run the check for changes
    print("\nChecking for changes using oasdiff...")
    monitor.check_for_changes()
    
    # Restore the original fetch method
    monitor.fetcher.fetch_current_spec = original_fetch
    
    print("\n=== Demo completed ===")
    print("Check the webhook server output above for notification details.")
    print("The notification should show:")
    print("  • Breaking changes detected")
    print("  • Full changelog with all changes")
    print("  • Complete API specification content")
    print("\nIf you encountered any 'unauthorized' errors, they should now be resolved")
    print("with the consistent webhook secret configuration.")
    print("\nPress Ctrl+C to exit.")
    
    # Clean up temporary file
    try:
        os.remove(modified_spec_path)
    except:
        pass
    
    # Keep the main thread alive until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDemo stopped by user.")

if __name__ == "__main__":
    run_demo() 