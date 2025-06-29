#!/usr/bin/env python3
"""
Reset script to clean up files generated by the demo.
This script deletes all files in the api_specs directory.
"""

import os
import shutil
import config

def reset_demo():
    """Delete all generated files from the demo."""
    print("Resetting demo...")
    
    # Check if api_specs directory exists
    if os.path.exists(config.SPEC_STORAGE_DIR):
        # Remove all files in the directory
        for filename in os.listdir(config.SPEC_STORAGE_DIR):
            file_path = os.path.join(config.SPEC_STORAGE_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
        print("\nDemo reset completed successfully.")
    else:
        print("No files to clean up. The api_specs directory doesn't exist.")

if __name__ == "__main__":
    reset_demo() 