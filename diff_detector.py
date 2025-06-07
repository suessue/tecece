import logging
from deepdiff import DeepDiff

logger = logging.getLogger('api_spec_monitor.diff')

class APISpecDiffDetector:
    """Detects differences between API specifications."""
    
    def __init__(self):
        # HTTP methods supported by OpenAPI
        self.http_methods = ['get', 'post', 'put', 'delete', 'options', 'head', 'patch', 'trace']
    
    def detect_changes(self, current_spec, previous_spec):
        """
        Detect changes between current and previous API specifications.
        Returns a dictionary with categorized changes or None if no comparison could be made.
        """
        if not current_spec:
            logger.warning("Current specification is not available for comparison")
            return None
            
        if not previous_spec:
            logger.info("No previous specification available for comparison. Treating as initial version.")
            paths = list(current_spec.get('paths', {}).keys())
            return {
                'added': {
                    'paths': paths,
                    'security_schemes': list(current_spec.get('components', {}).get('securitySchemes', {}).keys())
                },
                'changed': {},
                'removed': {}
            }
        
        try:
            # Use DeepDiff to find differences
            diff = DeepDiff(previous_spec, current_spec, ignore_order=True)
            
            # Extract relevant changes from the diff
            changes = self._categorize_changes(diff, previous_spec, current_spec)
            
            if changes and any(changes.values()):
                logger.info("Changes detected in API specification")
                return changes
            else:
                logger.info("No significant changes detected in API specification")
                return None
                
        except Exception as e:
            logger.error(f"Error comparing API specifications: {str(e)}")
            return None
    
    def _categorize_changes(self, diff, previous_spec, current_spec):
        """Categorize changes into added, changed, and removed items."""
        changes = {
            'added': {},
            'changed': {},
            'removed': {}
        }
        
        # Process path-level changes
        self._process_path_changes(diff, changes, previous_spec, current_spec)
        
        # Process operation-level changes (new HTTP methods on existing/new paths)
        self._process_operation_changes(diff, changes, previous_spec, current_spec)
        
        # Process parameter changes (including required parameter changes)
        self._process_parameter_changes(diff, changes, previous_spec, current_spec)
        
        # Process request/response format changes
        self._process_request_response_changes(diff, changes, previous_spec, current_spec)
        
        # Process authentication/security changes
        self._process_security_changes(diff, changes, previous_spec, current_spec)
        
        # Process component changes
        self._process_component_changes(diff, changes)
        
        return changes
    
    def _process_path_changes(self, diff, changes, previous_spec, current_spec):
        """Process changes at the path level."""
        # Process added paths
        added_paths = self._extract_paths(diff.get('dictionary_item_added', set()), 'paths')
        if added_paths:
            changes['added']['paths'] = added_paths
            
        # Process modified paths
        changed_paths = self._extract_paths(diff.get('values_changed', {}), 'paths')
        if changed_paths:
            changes['changed']['paths'] = changed_paths
            
        # Process removed paths
        removed_paths = self._extract_paths(diff.get('dictionary_item_removed', set()), 'paths')
        if removed_paths:
            changes['removed']['paths'] = removed_paths
    
    def _process_operation_changes(self, diff, changes, previous_spec, current_spec):
        """Process changes at the operation level (HTTP methods within paths)."""
        added_operations = []
        removed_operations = []
        changed_operations = []
        
        # Track paths that have been processed
        processed_paths = set()

        # First, identify truly new paths and operations
        for item in diff.get('dictionary_item_added', set()):
            item_str = str(item)
            path, method = self._extract_operation_info(item_str)
            if path and method:
                operation = f"{method.upper()} {path}"
                if path not in previous_spec.get('paths', {}):
                    # This is a completely new path
                    added_operations.append(operation)
                else:
                    # This is a modification to an existing path
                    changed_operations.append(operation)
                processed_paths.add(path)

        # Check for removed operations
        for item in diff.get('dictionary_item_removed', set()):
            item_str = str(item)
            path, method = self._extract_operation_info(item_str)
            if path and method:
                removed_operations.append(f"{method.upper()} {path}")

        # Check for changes to existing operations
        for key in diff.get('values_changed', {}):
            key_str = str(key)
            path, method = self._extract_operation_info(key_str)
            if path and method:
                operation = f"{method.upper()} {path}"
                if operation not in changed_operations and path in processed_paths:
                    changed_operations.append(operation)

        if added_operations:
            changes['added']['operations'] = added_operations
        if removed_operations:
            changes['removed']['operations'] = removed_operations
        if changed_operations:
            changes['changed']['operations'] = changed_operations
    
    def _process_parameter_changes(self, diff, changes, previous_spec, current_spec):
        """Process parameter changes, especially required parameter changes."""
        required_params_added = []
        required_params_removed = []
        
        # Check for parameters becoming required
        for key, change_info in diff.get('values_changed', {}).items():
            key_str = str(key)
            if 'required' in key_str and 'parameters' in key_str:
                old_value = change_info.get('old_value')
                new_value = change_info.get('new_value')
                
                if old_value == False and new_value == True:
                    param_info = self._extract_parameter_info(key_str)
                    if param_info:
                        required_params_added.append(param_info)
                elif old_value == True and new_value == False:
                    param_info = self._extract_parameter_info(key_str)
                    if param_info:
                        required_params_removed.append(param_info)
        
        # Check for new required parameters
        for item in diff.get('dictionary_item_added', set()):
            item_str = str(item)
            if 'parameters' in item_str:
                param_info = self._check_if_required_parameter(item_str, current_spec)
                if param_info:
                    required_params_added.append(param_info)
        
        if required_params_added:
            changes['added']['required_parameters'] = required_params_added
        if required_params_removed:
            changes['removed']['required_parameters'] = required_params_removed
    
    def _process_request_response_changes(self, diff, changes, previous_spec, current_spec):
        """Process changes in request and response formats."""
        request_format_changes = []
        response_format_changes = []
        
        for key in diff.get('values_changed', {}):
            key_str = str(key)
            
            # Check for request body schema changes
            if 'requestBody' in key_str and ('schema' in key_str or 'content' in key_str):
                operation_info = self._extract_operation_from_key(key_str)
                if operation_info:
                    request_format_changes.append(operation_info)
            
            # Check for response schema changes
            if 'responses' in key_str and ('schema' in key_str or 'content' in key_str):
                operation_info = self._extract_operation_from_key(key_str)
                if operation_info:
                    response_format_changes.append(operation_info)
        
        # Check for added/removed request/response content types
        for item in diff.get('dictionary_item_added', set()):
            item_str = str(item)
            if 'requestBody' in item_str and 'content' in item_str:
                operation_info = self._extract_operation_from_key(item_str)
                if operation_info:
                    request_format_changes.append(f"{operation_info} (new content type)")
            elif 'responses' in item_str and 'content' in item_str:
                operation_info = self._extract_operation_from_key(item_str)
                if operation_info:
                    response_format_changes.append(f"{operation_info} (new content type)")
        
        if request_format_changes:
            changes['changed']['request_formats'] = list(set(request_format_changes))
        if response_format_changes:
            changes['changed']['response_formats'] = list(set(response_format_changes))
    
    def _process_security_changes(self, diff, changes, previous_spec, current_spec):
        """Process authentication and security changes."""
        # Global security changes
        global_security_changes = []
        operation_security_changes = []
        
        # Check for global security changes
        for key in diff.get('values_changed', {}):
            key_str = str(key)
            if key_str == "root['security']":
                global_security_changes.append("Global security requirements changed")
        
        # Check for operation-level security changes
        for key in diff.get('values_changed', {}):
            key_str = str(key)
            if 'security' in key_str and 'paths' in key_str:
                operation_info = self._extract_operation_from_key(key_str)
                if operation_info:
                    operation_security_changes.append(f"{operation_info} security changed")
        
        # Check for new security schemes
        security_schemes_added = self._extract_components(diff.get('dictionary_item_added', set()), 'components.securitySchemes')
        security_schemes_removed = self._extract_components(diff.get('dictionary_item_removed', set()), 'components.securitySchemes')
        
        if global_security_changes:
            changes['changed']['global_security'] = global_security_changes
        if operation_security_changes:
            changes['changed']['operation_security'] = operation_security_changes
        if security_schemes_added:
            changes['added']['security_schemes'] = security_schemes_added
        if security_schemes_removed:
            changes['removed']['security_schemes'] = security_schemes_removed
    
    def _process_component_changes(self, diff, changes):
        """Process changes in reusable components."""
        components_types = ['schemas', 'parameters', 'responses', 'requestBodies', 'headers']
        for comp_type in components_types:
            comp_path = f"components.{comp_type}"
            
            added = self._extract_components(diff.get('dictionary_item_added', set()), comp_path)
            if added:
                changes['added'][comp_type] = added
                
            changed = self._extract_components(diff.get('values_changed', {}), comp_path)
            if changed:
                changes['changed'][comp_type] = changed
                
            removed = self._extract_components(diff.get('dictionary_item_removed', set()), comp_path)
            if removed:
                changes['removed'][comp_type] = removed
    
    def _is_operation_change(self, item_str):
        """Check if the change is at the operation level."""
        if 'root[\'paths\']' not in item_str:
            return False
        
        for method in self.http_methods:
            if f"['{method}']" in item_str:
                return True
        return False
    
    def _extract_operation_info(self, item_str):
        """Extract path and method from operation change."""
        try:
            # Parse something like "root['paths']['/users']['get']"
            parts = item_str.split("']")
            if len(parts) >= 3:
                path = parts[1].split("['")[1] if "['/" in parts[1] else None
                method = parts[2].split("['")[1] if "['" in parts[2] else None
                return path, method
        except (IndexError, AttributeError):
            pass
        return None, None
    
    def _extract_operation_from_key(self, key_str):
        """Extract operation info from a nested key."""
        try:
            if 'paths' in key_str:
                # Find path and method in the key
                parts = key_str.split("']")
                path = None
                method = None
                
                for i, part in enumerate(parts):
                    if "['/" in part:  # This is a path
                        path = part.split("['")[1]
                    elif any(f"['{m}']" in part for m in self.http_methods):
                        for m in self.http_methods:
                            if f"['{m}']" in part:
                                method = m
                                break
                
                if path and method:
                    return f"{method.upper()} {path}"
        except (IndexError, AttributeError):
            pass
        return None
    
    def _extract_parameter_info(self, key_str):
        """Extract parameter information from key."""
        try:
            operation_info = self._extract_operation_from_key(key_str)
            if operation_info and 'parameters' in key_str:
                # Try to extract parameter name/index
                param_match = key_str.split('parameters')[1]
                return f"{operation_info} parameter"
        except (IndexError, AttributeError):
            pass
        return None
    
    def _check_if_required_parameter(self, item_str, current_spec):
        """Check if a newly added parameter is required."""
        try:
            operation_info = self._extract_operation_from_key(item_str)
            if operation_info:
                # This is a simplified check - in a real implementation,
                # you'd want to parse the actual parameter definition
                return f"{operation_info} new parameter"
        except:
            pass
        return None
    
    def _get_all_operations(self, spec):
        """Get all operations from a spec for initial comparison."""
        operations = []
        paths = spec.get('paths', {})
        for path, path_obj in paths.items():
            for method in self.http_methods:
                if method in path_obj:
                    operations.append(f"{method.upper()} {path}")
        return operations
    
    def _extract_paths(self, diff_set, key_prefix):
        """Extract path changes from the diff set."""
        if not diff_set:
            return []
            
        results = []
        prefix = f"root['{key_prefix}']"
        
        for item in diff_set:
            item_str = str(item)
            if isinstance(item, str) and item.startswith(prefix):
                # Format: root['paths']['/path/endpoint']
                parts = item_str.split(']')
                if len(parts) >= 3:
                    path = parts[1].strip("['")
                    results.append(path)
            elif isinstance(item, dict) and prefix in item_str:
                # For values_changed format
                path_part = item_str.split(prefix)[1].split("'")[1] if "'" in item_str else ""
                if path_part:
                    results.append(path_part)
                    
        return results
    
    def _extract_components(self, diff_set, key_prefix):
        """Extract component changes from the diff set."""
        if not diff_set:
            return []
            
        results = []
        prefix = f"root['{key_prefix.split('.')[0]}']['{key_prefix.split('.')[1]}']"
        
        for item in diff_set:
            item_str = str(item)
            if isinstance(item, str) and prefix in item_str:
                # Extract component name
                parts = item_str.split(prefix)[1].split("'")
                if len(parts) >= 3:
                    component = parts[1]
                    results.append(component)
            elif isinstance(item, dict) and prefix in item_str:
                # For values_changed format
                comp_part = item_str.split(prefix)[1].split("'")[1] if "'" in item_str else ""
                if comp_part:
                    results.append(comp_part)
                    
        return results 