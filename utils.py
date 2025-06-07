import json
import logging
import os
from datetime import datetime
import config

def setup_logging():
    """Set up logging configuration."""
    log_dir = os.path.dirname(config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('api_spec_monitor')

def ensure_directory_exists(directory):
    """Ensure the specified directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json_to_file(data, file_path):
    """Save JSON data to a file."""
    directory = os.path.dirname(file_path)
    ensure_directory_exists(directory)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_json_from_file(file_path):
    """Load JSON data from a file."""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_change_summary(diff_result):
    """Generate a human-readable summary of API specification changes."""
    if not diff_result:
        return "No changes detected."
    
    summary = []
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary.append(f"API Specification Changes Detected at {timestamp}\n")
    
    # Summarize additions
    if 'added' in diff_result:
        summary.append("ADDITIONS:")
        for category, items in diff_result['added'].items():
            summary.append(f"  {category.upper()}:")
            for item in items:
                summary.append(f"    - {item}")
        summary.append("")
    
    # Summarize modifications
    if 'changed' in diff_result:
        summary.append("MODIFICATIONS:")
        for category, items in diff_result['changed'].items():
            summary.append(f"  {category.upper()}:")
            for item in items:
                summary.append(f"    - {item}")
        summary.append("")
    
    # Summarize removals
    if 'removed' in diff_result:
        summary.append("REMOVALS:")
        for category, items in diff_result['removed'].items():
            summary.append(f"  {category.upper()}:")
            for item in items:
                summary.append(f"    - {item}")
    
    return "\n".join(summary) 