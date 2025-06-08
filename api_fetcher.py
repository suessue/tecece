import requests
import os
import logging
from openapi_spec_validator import validate_spec

import config
import utils

logger = logging.getLogger('api_spec_monitor.fetcher')

class APISpecificationFetcher:
    """Fetches API specifications from a remote source and stores them locally."""
    
    def __init__(self, api_url=None):
        self.api_url = api_url or config.GITHUB_API_SPEC_URL
        utils.ensure_directory_exists(config.SPEC_STORAGE_DIR)
    
    def fetch_current_spec(self):
        """Fetch the current API specification from the remote source."""
        logger.info(f"Fetching API specification from {self.api_url}")
        
        try:
            response = requests.get(self.api_url, timeout=30)
            response.raise_for_status()
            
            spec_data = response.json()
            
            # Validate the specification
            if self._validate_spec(spec_data):
                logger.info("API specification successfully fetched and validated")
                return spec_data
            else:
                logger.error("Invalid API specification")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error fetching API specification: {str(e)}")
            return None
    
    def _validate_spec(self, spec_data):
        """Validate that the fetched data is a valid OpenAPI specification."""
        try:
            validate_spec(spec_data)
            return True
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False
    
    def update_stored_specs(self, new_spec):
        """Update the stored API specifications (current becomes previous, new becomes current)."""
        if new_spec is None:
            logger.warning("Cannot update stored specs with None")
            return False
        
        # If a current specification exists, move it to previous
        current_spec = utils.load_json_from_file(config.CURRENT_SPEC_PATH)
        if current_spec:
            utils.save_json_to_file(current_spec, config.PREVIOUS_SPEC_PATH)
            logger.info("Current specification moved to previous")
        
        # Save the new specification as current
        utils.save_json_to_file(new_spec, config.CURRENT_SPEC_PATH)
        logger.info("New specification saved as current")
        
        return True
    
    def get_stored_specs(self):
        """Get the stored current and previous API specifications."""
        current_spec = utils.load_json_from_file(config.CURRENT_SPEC_PATH)
        previous_spec = utils.load_json_from_file(config.PREVIOUS_SPEC_PATH)
        
        return current_spec, previous_spec 