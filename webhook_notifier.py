import requests
import logging
import json
import hmac
import hashlib
import time
from datetime import datetime

import config
import utils

logger = logging.getLogger('api_spec_monitor.webhook')

class WebhookNotifier:
    """Sends webhook notifications when API specification changes are detected."""
    
    def __init__(self, webhook_url=None, webhook_secret=None):
        self.webhook_url = webhook_url or config.WEBHOOK_URL
        self.webhook_secret = webhook_secret or config.WEBHOOK_SECRET
    
    def send_notification(self, changes):
        """Send a webhook notification with details about API specification changes."""
        if not changes:
            logger.warning("No changes to notify about")
            return False
        
        logger.info(f"Preparing to send webhook notification to {self.webhook_url}")
        
        try:
            # Prepare the payload
            payload = self._prepare_payload(changes)
            
            # Add signature to headers for security verification
            headers = self._generate_headers(payload)
            
            # Send the webhook request
            response = requests.post(
                self.webhook_url,
                json=payload,
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
    
    def _prepare_payload(self, changes):
        """Prepare the webhook payload with change details."""
        # Generate a human-readable summary for the changes
        summary = utils.generate_change_summary(changes)
        
        payload = {
            "event_type": "api_spec_change",
            "timestamp": datetime.now().isoformat(),
            "source": "github_api_spec_monitor",
            "summary": summary,
            "changes": changes,
            # Include metadata about the specification source
            "metadata": {
                "spec_source": config.GITHUB_API_SPEC_URL,
                "monitor_version": "1.0.0"
            }
        }
        
        return payload
    
    def _generate_headers(self, payload):
        """Generate headers for the webhook request including a security signature."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "GitHub-API-Spec-Monitor/1.0"
        }
        
        # Add signature for webhook security verification
        if self.webhook_secret:
            timestamp = str(int(time.time()))
            payload_str = json.dumps(payload)
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