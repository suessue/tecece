import requests
import logging
import json
import hmac
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, Optional

import config
import utils

logger = logging.getLogger('api_spec_monitor.webhook')

class WebhookNotifier:
    """Sends webhook notifications when API specification changes are detected."""
    
    def __init__(self, webhook_url: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.webhook_url = webhook_url or config.WEBHOOK_URL
        self.webhook_secret = webhook_secret or config.WEBHOOK_SECRET
    
    def send_notification(self, diff_result: Dict[str, Any]) -> bool:
        """
        Send a webhook notification with details about API specification changes.
        
        Args:
            diff_result: The diff result from oasdiff containing:
                - breaking_changes: List of breaking changes
                - changelog: Full changelog text
                - current_spec: Current API specification
                - has_breaking_changes: Boolean indicating if there are breaking changes
                - summary: Human-readable summary
                
        Returns:
            True if notification was sent successfully, False otherwise
        """
        if not diff_result:
            logger.warning("No changes to notify about")
            return False
        
        logger.info(f"Preparing to send webhook notification to {self.webhook_url}")
        
        try:
            # Prepare the payload with the new structure
            payload = self._prepare_payload(diff_result)
            
            # Serialize payload to exact JSON string (must be done ONCE for signature verification)
            payload_str = json.dumps(payload, sort_keys=True)
            
            # Add signature to headers for security verification using the exact payload string
            headers = self._generate_headers_with_payload(payload_str)
            
            # Send the webhook request with the exact JSON string that was signed
            # IMPORTANT: Use 'data' parameter, not 'json', to ensure the exact bytes are sent
            response = requests.post(
                self.webhook_url,
                data=payload_str,
                headers=headers,
                timeout=10
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook notification sent successfully: {response.status_code}")
                return True
            else:
                logger.error(f"Failed to send webhook notification: {response.status_code}, {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
            return False
    
    def _prepare_payload(self, diff_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the webhook payload with structured change details.
        
        Args:
            diff_result: The diff result from oasdiff
            
        Returns:
            Structured webhook payload
        """
        payload = {
            "event_type": "api_spec_change",
            "timestamp": datetime.now().isoformat(),
            "source": "github_api_spec_monitor",
            
            # Summary information
            "summary": diff_result.get('summary', 'API specification changes detected'),
            "has_breaking_changes": diff_result.get('has_breaking_changes', False),
            
            # Breaking changes section
            "breaking_changes": {
                "count": len(diff_result.get('breaking_changes', [])),
                "changes": diff_result.get('breaking_changes', [])
            },
            
            # Full changelog section
            "changelog": {
                "text": diff_result.get('changelog', ''),
                "lines": self._parse_changelog_lines(diff_result.get('changelog', ''))
            },
            
            # Current specification
            "current_spec": {
                "content": diff_result.get('current_spec', {}),
                "info": self._extract_spec_info(diff_result.get('current_spec', {}))
            },
            
            # Metadata about the specification source
            "metadata": {
                "spec_source": config.GITHUB_API_SPEC_URL,
                "monitor_version": "2.0.0",
                "diff_tool": "oasdiff",
                "notification_id": self._generate_notification_id()
            }
        }
        
        return payload
    
    def _parse_changelog_lines(self, changelog: str) -> list:
        """
        Parse changelog text into structured lines.
        
        Args:
            changelog: Raw changelog text
            
        Returns:
            List of structured changelog entries
        """
        if not changelog:
            return []
        
        lines = []
        for line in changelog.split('\n'):
            line = line.strip()
            if line:
                # Categorize changelog entries
                if line.startswith('###'):
                    lines.append({'type': 'heading', 'text': line.replace('###', '').strip()})
                elif line.startswith('- '):
                    lines.append({'type': 'item', 'text': line[2:].strip()})
                elif line.startswith('* '):
                    lines.append({'type': 'item', 'text': line[2:].strip()})
                else:
                    lines.append({'type': 'text', 'text': line})
        
        return lines
    
    def _extract_spec_info(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key information from the API specification.
        
        Args:
            spec: OpenAPI specification
            
        Returns:
            Dictionary with key spec information
        """
        if not spec:
            return {}
        
        info = {}
        
        # Basic info
        spec_info = spec.get('info', {})
        info['title'] = spec_info.get('title', 'Unknown')
        info['version'] = spec_info.get('version', 'Unknown')
        info['description'] = spec_info.get('description', '')
        
        # Count paths and operations
        paths = spec.get('paths', {})
        info['paths_count'] = len(paths)
        
        operations_count = 0
        operations_by_method = {}
        
        for path, path_obj in paths.items():
            for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']:
                if method in path_obj:
                    operations_count += 1
                    operations_by_method[method.upper()] = operations_by_method.get(method.upper(), 0) + 1
        
        info['operations_count'] = operations_count
        info['operations_by_method'] = operations_by_method
        
        # Component counts
        components = spec.get('components', {})
        component_info = {}
        for comp_type in ['schemas', 'parameters', 'responses', 'requestBodies', 'headers', 'securitySchemes']:
            comp_data = components.get(comp_type, {})
            if isinstance(comp_data, dict):
                component_info[comp_type] = len(comp_data)
        
        info['components'] = component_info
        
        # Security schemes
        security_schemes = components.get('securitySchemes', {})
        info['security_schemes'] = list(security_schemes.keys()) if security_schemes else []
        
        # Servers
        servers = spec.get('servers', [])
        info['servers'] = [server.get('url', '') for server in servers] if servers else []
        
        return info
    
    def _generate_notification_id(self) -> str:
        """
        Generate a unique notification ID.
        
        Returns:
            Unique notification ID string
        """
        return f"notify_{int(time.time())}_{hash(str(datetime.now())) % 10000:04d}"
    
    def _generate_headers_with_payload(self, payload_str: str) -> Dict[str, str]:
        """
        Generate headers for the webhook request including a security signature.
        
        Args:
            payload_str: The exact JSON string that will be sent (already serialized)
            
        Returns:
            Headers dict with security headers
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "GitHub-API-Spec-Monitor/2.0-oasdiff"
        }
        
        # Add signature for webhook security verification
        if self.webhook_secret:
            timestamp = str(int(time.time()))
            # Use the exact payload string that will be sent
            signature_message = f"{timestamp}.{payload_str}"
            
            # Create HMAC SHA256 signature
            signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                signature_message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Add security headers
            headers["X-Webhook-Timestamp"] = timestamp
            headers["X-Webhook-Signature"] = signature
        
        return headers 