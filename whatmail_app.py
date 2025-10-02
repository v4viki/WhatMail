#!/usr/bin/env python3
"""
WhatMail - Email to WhatsApp Notifier
Main Application Controller - Fixed imports
"""

import os
import sys
import time
import logging
import threading
from dotenv import load_dotenv

# Import our enhanced modules (fixed imports)
from whatsapp_client import WhatsAppClient  # Fixed import
from email_processor_optimized import EmailProcessor

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/whatmail.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class WhatMailApp:
    """Main application controller for WhatMail"""

    def __init__(self):
        self.whatsapp_client = None
        self.email_processor = None
        self.monitoring_thread = None
        self.is_running = False

        # Application state
        self.stop_event = threading.Event()

        logger.info("🚀 WhatMail Application initialized")

    def validate_environment(self) -> bool:
        """Validate required environment variables"""
        required_vars = ['EMAIL', 'PASSWORD', 'WHATSAPP']
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.info("Please set these variables in your .env file:")
            logger.info("EMAIL=your-gmail@gmail.com")
            logger.info("PASSWORD=your-app-password")
            logger.info("WHATSAPP=your-phone-number-with-country-code")
            return False

        # Validate email format
        email = os.getenv('EMAIL')
        if '@' not in email:
            logger.error("❌ Invalid email format")
            return False

        # Validate phone number format
        phone = os.getenv('WHATSAPP')
        if not phone.startswith('+') and not phone.isdigit():
            logger.warning("⚠️ WhatsApp number should include country code (e.g., +911234567890)")

        logger.info("✅ Environment validation passed")
        return True

    def initialize_components(self) -> bool:
        """Initialize WhatsApp client and email processor"""
        try:
            # Initialize WhatsApp client
            logger.info("📱 Initializing WhatsApp client...")
            self.whatsapp_client = WhatsAppClient(headless=False)

            # Initialize email processor
            logger.info("📧 Initializing email processor...")
            self.email_processor = EmailProcessor()

            logger.info("✅ Components initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            return False

    def start_whatsapp_session(self) -> bool:
        """Start WhatsApp Web session"""
        try:
            logger.info("📱 Starting WhatsApp Web session...")

            if self.whatsapp_client.start_session(timeout=120):
                logger.info("✅ WhatsApp session started successfully")
                return True
            else:
                logger.error("❌ Failed to start WhatsApp session")
                return False

        except Exception as e:
            logger.error(f"❌ Error starting WhatsApp session: {e}")
            return False

    def start_monitoring(self) -> bool:
        """Start email monitoring in background thread"""
        if self.is_running:
            logger.warning("⚠️ Monitoring is already running")
            return True

        try:
            logger.info("🚀 Starting email monitoring...")

            # Validate environment
            if not self.validate_environment():
                return False

            # Initialize components
            if not self.initialize_components():
                return False

            # Start WhatsApp session
            if not self.start_whatsapp_session():
                return False

            # Start monitoring in background thread
            self.stop_event.clear()
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_worker,
                daemon=True,
                name="EmailMonitor"
            )
            self.monitoring_thread.start()

            self.is_running = True
            logger.info("✅ Email monitoring started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")
            return False

    def _monitoring_worker(self):
        """Background worker for email monitoring"""
        try:
            check_interval = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes default

            while not self.stop_event.is_set():
                try:
                    # Check if WhatsApp is still active
                    if not self.whatsapp_client.is_session_active():
                        logger.warning("⚠️ WhatsApp session lost, attempting to reconnect...")
                        if not self.whatsapp_client.start_session():
                            logger.error("❌ Failed to reconnect WhatsApp, stopping monitoring")
                            break

                    # Process emails
                    processed_count = self.email_processor.process_emails(self.whatsapp_client)
                    logger.info(f"📊 Processed {processed_count} emails in this cycle")

                    # Wait for next check or stop signal
                    if self.stop_event.wait(check_interval):
                        break  # Stop event was set

                except Exception as e:
                    logger.error(f"❌ Error in monitoring cycle: {e}")
                    # Wait a bit before retrying
                    if self.stop_event.wait(60):
                        break

        except Exception as e:
            logger.error(f"❌ Fatal error in monitoring worker: {e}")
        finally:
            logger.info("🛑 Monitoring worker stopped")
            self.is_running = False

    def stop_monitoring(self):
        """Stop email monitoring"""
        if not self.is_running:
            logger.info("ℹ️ Monitoring is not running")
            return

        logger.info("🛑 Stopping email monitoring...")

        # Signal stop
        self.stop_event.set()

        # Wait for monitoring thread to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.info("⏳ Waiting for monitoring thread to finish...")
            self.monitoring_thread.join(timeout=10)

            if self.monitoring_thread.is_alive():
                logger.warning("⚠️ Monitoring thread did not stop gracefully")

        # Clean up components
        self._cleanup()

        self.is_running = False
        logger.info("✅ Monitoring stopped successfully")

    def _cleanup(self):
        """Clean up resources"""
        try:
            if self.whatsapp_client:
                self.whatsapp_client.stop_session()

            if self.email_processor:
                self.email_processor.stop_monitoring()

            logger.info("✅ Resources cleaned up")

        except Exception as e:
            logger.warning(f"⚠️ Error during cleanup: {e}")

    def get_status(self) -> dict:
        """Get application status"""
        return {
            'is_running': self.is_running,
            'whatsapp_active': self.whatsapp_client.is_session_active() if self.whatsapp_client else False,
            'email_configured': bool(os.getenv('EMAIL') and os.getenv('PASSWORD')),
            'whatsapp_configured': bool(os.getenv('WHATSAPP'))
        }

    def test_connection(self) -> dict:
        """Test email and WhatsApp connections"""
        results = {
            'email': False,
            'whatsapp': False,
            'errors': []
        }

        try:
            # Test email connection
            logger.info("🧪 Testing email connection...")
            test_processor = EmailProcessor()
            mail = test_processor.connect_to_email()
            if mail:
                mail.close()
                mail.logout()
                results['email'] = True
                logger.info("✅ Email connection test passed")
            else:
                results['errors'].append("Email connection failed")

        except Exception as e:
            results['errors'].append(f"Email test error: {str(e)}")

        try:
            # Test WhatsApp connection
            logger.info("🧪 Testing WhatsApp connection...")
            test_client = WhatsAppClient()
            if test_client.start_session(timeout=30):
                results['whatsapp'] = True
                logger.info("✅ WhatsApp connection test passed")
            else:
                results['errors'].append("WhatsApp session failed")
            test_client.stop_session()

        except Exception as e:
            results['errors'].append(f"WhatsApp test error: {str(e)}")

        return results


# Global app instance
app = WhatMailApp()

def start_monitoring():
    """Start monitoring (for GUI integration)"""
    return app.start_monitoring()

def stop_monitoring():
    """Stop monitoring (for GUI integration)"""
    app.stop_monitoring()

def get_status():
    """Get status (for GUI integration)"""
    return app.get_status()

def test_connections():
    """Test connections (for GUI integration)"""
    return app.test_connection()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='WhatMail - Email to WhatsApp Notifier')
    parser.add_argument('--start', action='store_true', help='Start monitoring')
    parser.add_argument('--test', action='store_true', help='Test connections')
    parser.add_argument('--status', action='store_true', help='Show status')

    args = parser.parse_args()

    try:
        if args.test:
            print("🧪 Testing connections...")
            results = app.test_connection()
            print(f"Email: {'✅' if results['email'] else '❌'}")
            print(f"WhatsApp: {'✅' if results['whatsapp'] else '❌'}")
            if results['errors']:
                print("Errors:")
                for error in results['errors']:
                    print(f"  - {error}")

        elif args.status:
            status = app.get_status()
            print("📊 Status:")
            print(f"  Running: {'✅' if status['is_running'] else '❌'}")
            print(f"  WhatsApp: {'✅' if status['whatsapp_active'] else '❌'}")
            print(f"  Email Config: {'✅' if status['email_configured'] else '❌'}")
            print(f"  WhatsApp Config: {'✅' if status['whatsapp_configured'] else '❌'}")

        elif args.start:
            if app.start_monitoring():
                print("✅ Monitoring started successfully!")
                print("Press Ctrl+C to stop...")

                try:
                    while app.is_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping...")
            else:
                print("❌ Failed to start monitoring")

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
    finally:
        app.stop_monitoring()
        print("👋 Goodbye!")
