#!/usr/bin/env python3
"""
Improved Email Processor - Clean HTML-to-text conversion for WhatsApp
"""

import imaplib
import email
import os
import re
import time
import logging
import sys
from datetime import datetime
from typing import List, Optional, Set, Tuple
from email.header import decode_header
from dotenv import load_dotenv
import threading

# Import our HTML converter
try:
    from html_text_converter import convert_html_to_text
except ImportError:
    # Fallback simple converter
    def convert_html_to_text(html_content: str, max_length: int = 800) -> str:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        text = re.sub(r'\n+', '\n', text)
        return text[:max_length] + "..." if len(text) > max_length else text

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_processor.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ImprovedEmailProcessor:
    """Email processor with clean HTML-to-text conversion"""

    def __init__(self):
        # Email configuration
        self.email = os.getenv("EMAIL", "").strip()
        self.password = os.getenv("PASSWORD", "").strip()
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.mailbox = os.getenv("MAILBOX", "INBOX")

        # Processing configuration
        self.filters = self._load_filters()
        self.max_emails_per_run = int(os.getenv("MAX_EMAILS_PER_RUN", "3"))
        self.message_truncate = int(os.getenv("MESSAGE_TRUNCATE", "800"))

        # State management
        self.processed_ids = self._load_processed_ids()
        self.stop_flag = threading.Event()

        # Validate configuration
        self._validate_config()

        # Ensure directories exist
        os.makedirs("logs", exist_ok=True)

        logger.info("✅ Improved Email Processor initialized")

    def _validate_config(self):
        """Validate email configuration"""
        if not self.email or not self.password:
            raise ValueError("❌ EMAIL and PASSWORD environment variables are required")

        if "@" not in self.email:
            raise ValueError("❌ Invalid email format")

        logger.info(f"✅ Email processor configured for: {self.email}")

    def _load_filters(self) -> List[str]:
        """Load email filters"""
        env_filters = os.getenv("FILTERS", "").strip()
        if env_filters:
            filters = [f.strip().lower() for f in env_filters.split(',') if f.strip()]
            logger.info(f"Using filters: {filters}")
            return filters

        # Default filters
        default_filters = ["urgent", "important", "otp", "job", "offer", "interview", "verification"]
        logger.info(f"Using default filters: {default_filters}")
        return default_filters

    def _load_processed_ids(self) -> Set[str]:
        """Load processed email IDs"""
        try:
            with open("logs/processed_emails.txt", "r", encoding="utf-8") as f:
                ids = set()
                for line in f:
                    parts = line.strip().split(",", 1)
                    if len(parts) >= 2:
                        ids.add(parts[1])
                return ids
        except FileNotFoundError:
            return set()

    def _mark_processed(self, email_id: str):
        """Mark email as processed"""
        try:
            with open("logs/processed_emails.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()},{email_id}\n")
            self.processed_ids.add(email_id)
        except Exception as e:
            logger.warning(f"Could not mark email as processed: {e}")

    def _log_sent_message(self, sender: str, subject: str, message: str, success: bool):
        """Log sent message details"""
        status = "SUCCESS" if success else "FAILED"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        log_entry = (
            f"\n[{timestamp}] {status}\n"
            f"From: {sender}\n"
            f"Subject: {subject}\n"
            f"Message Preview: {message[:100]}...\n"
            f"{'=' * 60}\n"
        )

        try:
            with open("logs/sent_messages.log", "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            logger.warning(f"Could not log message: {e}")

    def decode_mime_words(self, text: str) -> str:
        """Decode MIME encoded words in headers"""
        if not text:
            return ""

        try:
            decoded_parts = decode_header(text)
            result = []

            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    try:
                        if encoding:
                            part = part.decode(encoding, errors='replace')
                        else:
                            # Try common encodings
                            for enc in ['utf-8', 'iso-8859-1', 'windows-1252']:
                                try:
                                    part = part.decode(enc)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                part = part.decode('utf-8', errors='replace')
                    except (LookupError, UnicodeDecodeError):
                        part = part.decode('utf-8', errors='replace')

                result.append(str(part))

            return ''.join(result)

        except Exception as e:
            logger.warning(f"Failed to decode MIME header: {e}")
            return str(text)

    def extract_email_body(self, msg: email.message.Message) -> str:
        """Extract clean text from email body using improved HTML conversion"""
        try:
            if msg.is_multipart():
                # Look for text/plain first (clean text)
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))

                    if "attachment" in content_disposition:
                        continue

                    if content_type == "text/plain":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                plain_text = payload.decode('utf-8', errors='replace')
                                # Clean and truncate
                                plain_text = re.sub(r'\s+', ' ', plain_text).strip()
                                if len(plain_text) > self.message_truncate:
                                    plain_text = plain_text[:self.message_truncate] + "..."
                                return plain_text
                        except Exception as e:
                            logger.debug(f"Error decoding plain text: {e}")
                            continue

                # If no plain text, look for HTML and convert it
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))

                    if "attachment" in content_disposition:
                        continue

                    if content_type == "text/html":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                html_content = payload.decode('utf-8', errors='replace')

                                # Use our improved HTML converter
                                clean_text = convert_html_to_text(html_content, self.message_truncate)

                                logger.debug("Successfully converted HTML to clean text")
                                return clean_text

                        except Exception as e:
                            logger.debug(f"Error converting HTML: {e}")
                            continue
            else:
                # Single part message
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        content_type = msg.get_content_type()

                        if content_type == "text/html":
                            # HTML content - convert to clean text
                            html_content = payload.decode('utf-8', errors='replace')
                            clean_text = convert_html_to_text(html_content, self.message_truncate)
                            return clean_text
                        else:
                            # Plain text content
                            plain_text = payload.decode('utf-8', errors='replace')
                            plain_text = re.sub(r'\s+', ' ', plain_text).strip()
                            if len(plain_text) > self.message_truncate:
                                plain_text = plain_text[:self.message_truncate] + "..."
                            return plain_text

                except Exception as e:
                    logger.debug(f"Error decoding single message: {e}")

        except Exception as e:
            logger.warning(f"Error extracting email body: {e}")

        return "Email content could not be extracted"

    def is_important_email(self, subject: str, body: str, sender: str) -> bool:
        """Check if email matches importance criteria"""
        if not self.filters:
            return True

        search_text = f"{subject} {body} {sender}".lower()

        for filter_keyword in self.filters:
            if re.search(rf'\b{re.escape(filter_keyword)}\b', search_text):
                logger.debug(f"Email matches filter: {filter_keyword}")
                return True

        return False

    def connect_to_email(self) -> Optional[imaplib.IMAP4_SSL]:
        """Establish IMAP connection with retry logic"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                logger.info(f"📧 Connecting to {self.imap_server}... (attempt {attempt + 1})")

                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
                mail.login(self.email, self.password)
                mail.select(self.mailbox)

                logger.info("✅ Successfully connected to email server")
                return mail

            except imaplib.IMAP4.error as e:
                logger.error(f"❌ IMAP error: {e}")
                if "authentication failed" in str(e).lower():
                    logger.error("❌ Authentication failed. Check email credentials.")
                    break
            except Exception as e:
                logger.error(f"❌ Connection error: {e}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        return None

    def process_emails(self, whatsapp_client) -> int:
        """Process unread emails and send clean notifications"""
        mail = None
        processed_count = 0

        try:
            mail = self.connect_to_email()
            if not mail:
                logger.error("❌ Failed to connect to email server")
                return 0

            logger.info("🔍 Searching for unread emails...")
            status, messages = mail.search(None, 'UNSEEN')

            if status != 'OK':
                logger.error(f"❌ Email search failed: {status}")
                return 0

            message_ids = messages[0].split()
            if not message_ids:
                logger.info("📭 No unread emails found")
                return 0

            # Limit emails for better performance
            message_ids = message_ids[-self.max_emails_per_run:]
            logger.info(f"📬 Processing {len(message_ids)} unread emails")

            for msg_id in reversed(message_ids):
                if self.stop_flag.is_set():
                    logger.info("🛑 Stop flag set, halting processing")
                    break

                try:
                    msg_id_str = msg_id.decode()

                    if msg_id_str in self.processed_ids:
                        logger.debug(f"⏭️ Skipping processed email: {msg_id_str}")
                        continue

                    # Fetch email
                    status, data = mail.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        logger.error(f"❌ Failed to fetch email {msg_id_str}")
                        continue

                    # Parse email
                    email_message = email.message_from_bytes(data[0][1])

                    subject = self.decode_mime_words(email_message.get('Subject', 'No Subject'))
                    from_header = email_message.get('From', 'Unknown Sender')
                    sender_email = email.utils.parseaddr(from_header)[1]

                    logger.info(f"📩 Processing: {subject[:50]}... from {sender_email}")

                    # Extract clean body text
                    body = self.extract_email_body(email_message)

                    # Check importance
                    is_important = self.is_important_email(subject, body, sender_email)

                    if is_important:
                        priority = "[IMPORTANT EMAIL]"
                        logger.info("🎯 Marked as important")
                    else:
                        priority = "[Email Notification]"

                    # Prepare clean WhatsApp message
                    whatsapp_message = (
                        f"{priority}\n"
                        f"From: {sender_email}\n"
                        f"Subject: {subject}\n\n"
                        f"{body}"
                    )

                    # Send WhatsApp notification
                    logger.info(f"📱 Sending clean WhatsApp notification...")
                    success = whatsapp_client.send_to_saved_number(whatsapp_message)

                    # Log the attempt
                    self._log_sent_message(sender_email, subject, whatsapp_message, success)

                    if success:
                        self._mark_processed(msg_id_str)
                        processed_count += 1
                        logger.info(f"✅ Sent clean notification: {subject[:30]}...")

                        # Wait between messages
                        delay = int(os.getenv('MESSAGE_DELAY', '10'))
                        if not self.stop_flag.wait(delay):
                            continue
                        else:
                            break
                    else:
                        logger.error(f"❌ Failed to send notification for: {subject[:30]}...")
                        break

                except Exception as e:
                    logger.error(f"❌ Error processing email {msg_id}: {e}")
                    continue

            logger.info(f"✅ Processed {processed_count} emails with clean formatting")
            return processed_count

        except Exception as e:
            logger.error(f"❌ Error in email processing: {e}")
            return processed_count

        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                    logger.debug("📧 Email connection closed")
                except Exception as e:
                    logger.warning(f"⚠️ Error closing email connection: {e}")

    def stop_monitoring(self):
        """Stop email monitoring"""
        logger.info("🛑 Stopping email monitoring...")
        self.stop_flag.set()

# For compatibility with existing code
EmailProcessor = ImprovedEmailProcessor

if __name__ == "__main__":
    from whatsapp_client import WhatsAppClient

    processor = ImprovedEmailProcessor()
    whatsapp_client = WhatsAppClient()

    try:
        if whatsapp_client.start_session():
            print("Testing improved email processing with clean HTML conversion...")
            count = processor.process_emails(whatsapp_client)
            print(f"Processed {count} emails with clean formatting")
        else:
            print("Failed to start WhatsApp session")
    finally:
        whatsapp_client.stop_session()
