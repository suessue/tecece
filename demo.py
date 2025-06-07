#!/usr/bin/env python3
"""
Demo script to demonstrate the API Specification Change Monitor.
This script simulates a change in the API specification and triggers the notification process.
"""

import os
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
    webhook_thread = threading.Thread(target=start_server)
    webhook_thread.daemon = True
    webhook_thread.start()
    
    # Give the server time to start
    time.sleep(2)
    print("Webhook server is running.")
    return webhook_thread

def simulate_api_spec_change():
    """Simulate a change in the API specification."""
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
                        "responses": {
                            "200": {
                                "description": "Success"
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
    
    # Modify the spec to simulate a change
    if "paths" in modified_spec:
        # Add a new endpoint
        modified_spec["paths"]["/products"] = {
            "get": {
                "summary": "Get all products",
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Modify an existing endpoint
        if "/users" in modified_spec["paths"]:
            # Add 400 response to GET endpoint
            modified_spec["paths"]["/users"]["get"]["responses"]["400"] = {
                "description": "Bad Request"
            }
            # Add POST endpoint
            modified_spec["paths"]["/users"]["post"] = {
                "summary": "Create a new user",
                "responses": {
                    "201": {
                        "description": "Created"
                    },
                    "400": {
                        "description": "Bad Request"
                    }
                }
            }
    
    # Update the info version
    if "info" in modified_spec:
        modified_spec["info"]["version"] = "1.1.0"
    
    # Save the modified spec to a temporary file
    temp_spec_path = os.path.join(config.SPEC_STORAGE_DIR, "temp_modified_spec.json")
    utils.save_json_to_file(modified_spec, temp_spec_path)
    
    print("Specification modification completed.")
    return temp_spec_path

def run_demo():
    """Run the complete demo process."""
    # Start the webhook server
    webhook_thread = start_webhook_server()
    
    # Create an instance of the API monitor
    monitor = APISpecMonitor()
    
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
    print("\nChecking for changes...")
    monitor.check_for_changes()
    
    # Restore the original fetch method
    monitor.fetcher.fetch_current_spec = original_fetch
    
    print("\nDemo completed. Check the webhook server output for notification details.")
    print("Press Ctrl+C to exit.")
    
    # Keep the main thread alive until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDemo stopped by user.")

if __name__ == "__main__":
    run_demo() 