import os
import time
import logging
import argparse
from apscheduler.schedulers.background import BackgroundScheduler
import threading

import config
import utils
from api_fetcher import APISpecificationFetcher
from diff_detector import APISpecDiffDetector
from webhook_notifier import WebhookNotifier

# Set up logging
logger = utils.setup_logging()

class APISpecMonitor:
    """Main application that monitors API specifications for changes."""
    
    def __init__(self):
        self.fetcher = APISpecificationFetcher()
        self.diff_detector = APISpecDiffDetector()
        self.notifier = WebhookNotifier()
        self.scheduler = BackgroundScheduler()
        
        # Ensure storage directory exists
        utils.ensure_directory_exists(config.SPEC_STORAGE_DIR)
    
    def check_for_changes(self):
        """Check for changes in the API specification and send notifications if needed."""
        logger.info("Checking for API specification changes...")
        
        # Fetch the current API specification
        current_spec = self.fetcher.fetch_current_spec()
        if not current_spec:
            logger.error("Failed to fetch current API specification")
            return
        
        # Get the stored specifications
        stored_current, stored_previous = self.fetcher.get_stored_specs()
        
        # Detect changes between the fetched spec and the stored current spec
        diff_result = self.diff_detector.detect_changes(current_spec, stored_current)
        
        if diff_result:
            logger.info("Changes detected in API specification, sending notification")
            
            # Log summary of changes
            if diff_result.get('has_breaking_changes'):
                logger.warning(f"Breaking changes detected: {len(diff_result.get('breaking_changes', []))} breaking change(s)")
            
            # Send webhook notification
            notification_sent = self.notifier.send_notification(diff_result)
            
            if notification_sent:
                logger.info("Notification sent successfully")
                # Update stored specifications only if notification was sent successfully
                self.fetcher.update_stored_specs(current_spec)
            else:
                logger.warning("Failed to send notification, not updating stored specifications")
        else:
            logger.info("No changes detected, or there was an error comparing specifications")
    
    def start(self, initial_run=True, run_webhook_server=False):
        """Start the API specification monitoring process."""
        logger.info("Starting API specification monitor")
        
        # If this is the first run and we don't have a stored specification, fetch and save it
        if initial_run:
            stored_current, _ = self.fetcher.get_stored_specs()
            if not stored_current:
                logger.info("No stored API specification found, fetching initial version")
                current_spec = self.fetcher.fetch_current_spec()
                if current_spec:
                    self.fetcher.update_stored_specs(current_spec)
                    logger.info("Initial API specification stored")
                else:
                    logger.error("Failed to fetch initial API specification")
            else:
                logger.info("Using existing stored API specification")
        
        # Schedule regular checks
        self.scheduler.add_job(
            self.check_for_changes,
            'interval',
            minutes=config.CHECK_INTERVAL_MINUTES,
            id='api_spec_check'
        )
        
        # Start the scheduler
        self.scheduler.start()
        logger.info(f"Scheduler started, checking every {config.CHECK_INTERVAL_MINUTES} minutes")
        
        # Optionally start the webhook server in a separate thread (for demo purposes)
        if run_webhook_server:
            webhook_thread = threading.Thread(target=self._start_webhook_server)
            webhook_thread.daemon = True
            webhook_thread.start()
    
    def _start_webhook_server(self):
        """Start the webhook server for demo purposes."""
        try:
            # Import here to avoid circular imports
            from webhook_server import start_server
            start_server()
        except Exception as e:
            logger.error(f"Error starting webhook server: {str(e)}")
    
    def stop(self):
        """Stop the API specification monitor."""
        self.scheduler.shutdown()
        logger.info("API specification monitor stopped")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='API Specification Change Monitor')
    parser.add_argument('--webhook-server', action='store_true', help='Run webhook server alongside the monitor')
    parser.add_argument('--check-now', action='store_true', help='Perform a check immediately, then exit')
    parser.add_argument('--interval', type=int, help=f'Check interval in minutes (default: {config.CHECK_INTERVAL_MINUTES})')
    
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Update configuration based on arguments
    if args.interval:
        config.CHECK_INTERVAL_MINUTES = args.interval
    
    # Initialize the monitor
    monitor = APISpecMonitor()
    
    # Handle one-time check mode
    if args.check_now:
        logger.info("Performing one-time check...")
        monitor.check_for_changes()
        logger.info("Check complete")
    else:
        # Start the monitor
        try:
            monitor.start(run_webhook_server=args.webhook_server)
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
        finally:
            monitor.stop() 