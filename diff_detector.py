import logging
import subprocess
import json
import tempfile
import os
from typing import Dict, List, Optional, Any

import config

logger = logging.getLogger('api_spec_monitor.diff')

class APISpecDiffDetector:
    """Detects differences between API specifications using oasdiff."""
    
    def __init__(self, oasdiff_path: str = None):
        """
        Initialize the diff detector.
        
        Args:
            oasdiff_path: Path to the oasdiff binary (default: from config.OASDIFF_PATH)
        """
        self.oasdiff_path = oasdiff_path or config.OASDIFF_PATH
        self.timeout = config.OASDIFF_TIMEOUT
        self._validate_oasdiff_installation()
    
    def _validate_oasdiff_installation(self):
        """Validate that oasdiff is installed and accessible."""
        try:
            result = subprocess.run(
                [self.oasdiff_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"oasdiff found: {result.stdout.strip()}")
            else:
                logger.warning(f"oasdiff validation failed with return code {result.returncode}")
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"oasdiff not found or not accessible: {e}")
            logger.error("Please install oasdiff: https://github.com/oasdiff/oasdiff#installation")
            logger.error("Or run: python install_oasdiff.py")
            raise RuntimeError("oasdiff is required but not available")
    
    def detect_changes(self, current_spec: Dict[str, Any], previous_spec: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Detect changes between current and previous API specifications using oasdiff.
        
        Args:
            current_spec: The current API specification
            previous_spec: The previous API specification (None for initial version)
            
        Returns:
            Dictionary with structured diff results including:
            - breaking_changes: List of breaking changes
            - changelog: Full changelog
            - current_spec: The current API specification
            - has_breaking_changes: Boolean indicating if there are breaking changes
            - summary: Human-readable summary
        """
        if not current_spec:
            logger.warning("Current specification is not available for comparison")
            return None
            
        if not previous_spec:
            logger.info("No previous specification available for comparison. Treating as initial version.")
            return {
                'breaking_changes': [],
                'changelog': self._generate_initial_changelog(current_spec),
                'current_spec': current_spec,
                'has_breaking_changes': False,
                'summary': "Initial API specification version"
            }
        
        try:
            # Create temporary files for the specifications
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as prev_file, \
                 tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as curr_file:
                
                # Write specifications to temporary files
                json.dump(previous_spec, prev_file, indent=2)
                json.dump(current_spec, curr_file, indent=2)
                prev_file.flush()
                curr_file.flush()
                
                try:
                    # Get breaking changes
                    breaking_changes = self._get_breaking_changes(prev_file.name, curr_file.name)
                    
                    # Get full changelog
                    changelog = self._get_changelog(prev_file.name, curr_file.name)
                    
                    # Determine if there are actual changes
                    has_changes = bool(breaking_changes or (changelog and changelog.strip()))
                    
                    if has_changes:
                        logger.info("Changes detected in API specification")
                        return {
                            'breaking_changes': breaking_changes,
                            'changelog': changelog,
                            'current_spec': current_spec,
                            'has_breaking_changes': bool(breaking_changes),
                            'summary': self._generate_summary(breaking_changes, changelog)
                        }
                    else:
                        logger.info("No significant changes detected in API specification")
                        return None
                        
                finally:
                    # Clean up temporary files
                    try:
                        os.unlink(prev_file.name)
                        os.unlink(curr_file.name)
                    except OSError:
                        pass  # Files may have been already deleted
                        
        except Exception as e:
            logger.error(f"Error comparing API specifications: {str(e)}")
            return None
    
    def _get_breaking_changes(self, prev_file_path: str, curr_file_path: str) -> List[Dict[str, Any]]:
        """
        Get breaking changes using oasdiff breaking command.
        
        Args:
            prev_file_path: Path to previous specification file
            curr_file_path: Path to current specification file
            
        Returns:
            List of breaking changes
        """
        try:
            result = subprocess.run(
                [self.oasdiff_path, "breaking", prev_file_path, curr_file_path, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                # Check if there's JSON output indicating breaking changes
                if result.stdout.strip():
                    try:
                        breaking_changes_data = json.loads(result.stdout)
                        return self._parse_breaking_changes(breaking_changes_data)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse breaking changes JSON: {result.stdout}")
                        return [{"description": result.stdout.strip()}] if result.stdout.strip() else []
                else:
                    # No output means no breaking changes
                    return []
            else:
                logger.error(f"oasdiff breaking command failed with return code {result.returncode}: {result.stderr}")
                return []
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.error(f"Error running oasdiff breaking command: {e}")
            return []
    
    def _get_changelog(self, prev_file_path: str, curr_file_path: str) -> str:
        """
        Get full changelog using oasdiff changelog command.
        
        Args:
            prev_file_path: Path to previous specification file
            curr_file_path: Path to current specification file
            
        Returns:
            Changelog as string
        """
        try:
            result = subprocess.run(
                [self.oasdiff_path, "changelog", prev_file_path, curr_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning(f"oasdiff changelog command returned {result.returncode}: {result.stderr}")
                return result.stdout.strip() if result.stdout.strip() else ""
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.error(f"Error running oasdiff changelog command: {e}")
            return ""
    
    def _parse_breaking_changes(self, breaking_changes_data: Any) -> List[Dict[str, Any]]:
        """
        Parse breaking changes data from oasdiff JSON output.
        
        Args:
            breaking_changes_data: Raw breaking changes data from oasdiff
            
        Returns:
            List of structured breaking changes
        """
        breaking_changes = []
        
        if isinstance(breaking_changes_data, list):
            # Handle array format
            for change in breaking_changes_data:
                if isinstance(change, dict):
                    breaking_changes.append({
                        'id': change.get('id', ''),
                        'text': change.get('text', ''),
                        'level': change.get('level', 'error'),
                        'operation': change.get('operation', ''),
                        'path': change.get('path', ''),
                        'source': change.get('source', '')
                    })
                else:
                    breaking_changes.append({'description': str(change)})
        elif isinstance(breaking_changes_data, dict):
            # Handle object format
            if 'breakingChanges' in breaking_changes_data:
                for change in breaking_changes_data['breakingChanges']:
                    breaking_changes.append({
                        'id': change.get('id', ''),
                        'text': change.get('text', ''),
                        'level': change.get('level', 'error'),
                        'operation': change.get('operation', ''),
                        'path': change.get('path', ''),
                        'source': change.get('source', '')
                    })
            else:
                # Fallback for other formats
                breaking_changes.append({'description': str(breaking_changes_data)})
        else:
            breaking_changes.append({'description': str(breaking_changes_data)})
        
        return breaking_changes
    
    def _generate_initial_changelog(self, current_spec: Dict[str, Any]) -> str:
        """
        Generate a changelog for the initial API specification.
        
        Args:
            current_spec: The current API specification
            
        Returns:
            Initial changelog as string
        """
        lines = ["Initial API specification version\n"]
        
        # Count paths and operations
        paths = current_spec.get('paths', {})
        total_paths = len(paths)
        total_operations = sum(
            len([key for key in path_obj.keys() if key.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']])
            for path_obj in paths.values()
        )
        
        lines.append(f"- {total_paths} API paths")
        lines.append(f"- {total_operations} operations")
        
        # List components
        components = current_spec.get('components', {})
        for comp_type, comp_data in components.items():
            if isinstance(comp_data, dict) and comp_data:
                lines.append(f"- {len(comp_data)} {comp_type}")
        
        return "\n".join(lines)
    
    def _generate_summary(self, breaking_changes: List[Dict[str, Any]], changelog: str) -> str:
        """
        Generate a human-readable summary of changes.
        
        Args:
            breaking_changes: List of breaking changes
            changelog: Full changelog
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        if breaking_changes:
            summary_parts.append(f"⚠️ {len(breaking_changes)} breaking change(s) detected")
        
        if changelog and changelog.strip():
            changelog_lines = [line.strip() for line in changelog.split('\n') if line.strip()]
            summary_parts.append(f"📝 {len(changelog_lines)} total changes")
        
        if not summary_parts:
            return "No significant changes detected"
        
        return " | ".join(summary_parts) 