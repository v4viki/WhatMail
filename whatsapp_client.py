#!/usr/bin/env python3
"""
WhatsApp Web Client - Unified Final Version
Class name: WhatsAppClient (for compatibility with existing code)
"""

import os
import time
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class WhatsAppClient:
    """
    WhatsApp Web Client - Final Fixed Version with correct class name
    """

    def __init__(self, headless: bool = False, user_data_dir: str = None):
        self.driver = None
        self.session_active = False
        self.headless = headless
        self.user_data_dir = user_data_dir or os.path.join(os.getcwd(), "chrome_profile")
        self.whatsapp_number = os.getenv("WHATSAPP", "").strip()

        # UPDATED WhatsApp Web selectors for October 2024
        self.selectors = {
            "chat_list": [
                "[data-testid='chat-list']",
                "[aria-label='Chat list']", 
                "#pane-side",
                "div[role='grid']",
                "div[aria-label*='conversation']"
            ],
            "message_box": [
                # Primary selectors for message input (updated for 2024)
                "div[contenteditable='true'][data-tab='10']",
                "[data-testid='conversation-compose-box-input']",
                "div[contenteditable='true'][role='textbox']",
                "div[title='Type a message']",
                "div[aria-placeholder*='message']",
                "div[data-lexical-editor='true']",  # New Lexical editor
                "p[data-lexical-text='true']",     # Lexical text node
                "div[contenteditable='true']:not([aria-label])",
                "div._lexical_editor",            # Alternative class
                "footer div[contenteditable='true']",
                "div[spellcheck='true'][contenteditable='true']"
            ],
            "send_button": [
                # Primary send button selectors  
                "[data-testid='compose-btn-send']",
                "button[aria-label='Send']",
                "[data-testid='send']",
                "span[data-testid='send']",
                "button[type='submit']",
                "[role='button'][aria-label*='Send']",
                "div[role='button'][aria-label*='Send']",
                "button:has(svg[viewBox*='0 0 24 24'])",
                "[aria-label*='send' i]",
                "span[aria-label='Send']"
            ]
        }

    def _clean_message_text(self, message: str) -> str:
        """Clean message text for WhatsApp compatibility"""
        if not message:
            return ""

        # Remove problematic characters and emojis
        emoji_replacements = {
            '🧪': '[TEST]', '🤖': '[BOT]', '✅': '[OK]', '❌': '[ERROR]',
            '📧': '[EMAIL]', '📱': '[PHONE]', '🚨': '[URGENT]', '💬': '[MSG]',
            '🔔': '[ALERT]', '⏰': '[TIME]', '📊': '[DATA]', '🎯': '[TARGET]'
        }

        cleaned = message
        for emoji, replacement in emoji_replacements.items():
            cleaned = cleaned.replace(emoji, replacement)

        # Keep only BMP characters
        result = ""
        for char in cleaned:
            if ord(char) <= 0xFFFF:
                result += char
            else:
                result += "?"

        return result.strip()

    def _setup_driver(self):
        """Initialize Chrome driver"""
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)

            options = Options()
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
            options.add_argument("--profile-directory=Default")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")

            # Add debugging flags
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")

            # Anti-detection
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")

            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")
            else:
                options.add_argument("--window-size=1400,900")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

            # Anti-detection script
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            # Set timeouts
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)

            logger.info("✅ Chrome driver initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize driver: {str(e)}")
            return False

    def _wait_for_element(self, selectors: list, timeout: int = 15, clickable: bool = False) -> Optional[object]:
        """Wait for element with multiple selectors"""
        wait = WebDriverWait(self.driver, timeout)

        for i, selector in enumerate(selectors):
            try:
                if clickable:
                    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                else:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

                if element.is_displayed():
                    logger.debug(f"Found element with selector {i+1}: {selector}")
                    return element

            except TimeoutException:
                continue

        return None

    def start_session(self, timeout: int = 120) -> bool:
        """Start WhatsApp Web session"""
        if self.session_active:
            return True

        logger.info("🚀 Starting WhatsApp Web session...")

        if not self._setup_driver():
            return False

        try:
            self.driver.get("https://web.whatsapp.com")
            logger.info("📱 Opened WhatsApp Web")

            # Wait for WhatsApp to load
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check if authenticated (chat list visible)
                if self._wait_for_element(self.selectors["chat_list"], timeout=3):
                    logger.info("✅ WhatsApp Web loaded and authenticated")
                    self.session_active = True
                    return True

                # Check for QR code
                qr_selectors = ["canvas", "[data-ref] canvas", "div[role='img'] canvas"]
                if self._wait_for_element(qr_selectors, timeout=3):
                    logger.info("📱 QR code detected - please scan")

                time.sleep(3)

            logger.error("❌ WhatsApp session failed to start")
            return False

        except Exception as e:
            logger.error(f"❌ Error starting session: {str(e)}")
            return False

    def send_message(self, phone_number: str, message: str, max_retries: int = 3) -> bool:
        """Enhanced message sending with better error handling"""
        if not self.session_active or not self.driver:
            logger.error("❌ Session not active")
            return False

        if not phone_number or not message:
            logger.error("❌ Phone number and message required")
            return False

        # Clean message
        clean_message = self._clean_message_text(message)
        logger.info(f"💬 Sending to {phone_number}: {clean_message[:50]}...")

        for attempt in range(max_retries):
            try:
                # Navigate to chat
                chat_url = f"https://web.whatsapp.com/send?phone={phone_number}"
                logger.debug(f"Opening chat URL: {chat_url}")

                self.driver.get(chat_url)
                time.sleep(8)  # Wait for page load

                # Check for any error messages
                try:
                    error_selectors = [
                        "[data-testid*='error']", 
                        ".error", 
                        "[role='alert']",
                        "div:contains('Phone number')"
                    ]

                    for selector in error_selectors:
                        try:
                            error_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if error_elem.is_displayed():
                                logger.error(f"WhatsApp Error: {error_elem.text}")
                                return False
                        except:
                            continue
                except:
                    pass

                # Find message input box
                logger.debug("Looking for message input...")
                message_input = self._wait_for_element(
                    self.selectors["message_box"], 
                    timeout=20, 
                    clickable=True
                )

                if not message_input:
                    logger.warning(f"❌ Message input not found (attempt {attempt + 1})")

                    # Take screenshot for debugging
                    screenshot_path = f"logs/screenshots/no_input_{int(time.time())}.png"
                    os.makedirs("logs/screenshots", exist_ok=True)
                    self.driver.save_screenshot(screenshot_path)
                    logger.debug(f"Screenshot saved: {screenshot_path}")

                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    return False

                # Clear and type message
                logger.debug("Typing message...")

                # Method 1: Click and clear
                try:
                    message_input.click()
                    time.sleep(1)

                    # Clear existing content
                    message_input.send_keys(Keys.CONTROL + "a")
                    time.sleep(0.5)
                    message_input.send_keys(Keys.DELETE)
                    time.sleep(1)

                except Exception as e:
                    logger.debug(f"Clear method failed: {e}")

                # Method 2: Type message
                success = False

                try:
                    # Type the message
                    message_input.send_keys(clean_message)
                    time.sleep(2)
                    success = True
                    logger.debug("Message typed successfully")

                except Exception as e:
                    logger.warning(f"Typing failed: {e}")

                    # Fallback: JavaScript injection
                    try:
                        logger.debug("Trying JavaScript method...")
                        js_script = """
                        var input = arguments[0];
                        var message = arguments[1];

                        // Focus and set content
                        input.focus();
                        input.innerHTML = '';
                        input.textContent = message;
                        input.innerText = message;

                        // Dispatch events
                        var inputEvent = new Event('input', {bubbles: true});
                        input.dispatchEvent(inputEvent);

                        var changeEvent = new Event('change', {bubbles: true});
                        input.dispatchEvent(changeEvent);
                        """

                        self.driver.execute_script(js_script, message_input, clean_message)
                        time.sleep(2)
                        success = True
                        logger.debug("JavaScript injection successful")

                    except Exception as js_error:
                        logger.error(f"JavaScript method also failed: {js_error}")

                if not success:
                    logger.error("❌ Could not input message")
                    continue

                # Send message
                logger.debug("Sending message...")
                sent = False

                # Method 1: Find and click send button
                send_button = self._wait_for_element(
                    self.selectors["send_button"], 
                    timeout=10, 
                    clickable=True
                )

                if send_button:
                    try:
                        # Scroll into view and click
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
                        time.sleep(1)
                        send_button.click()
                        logger.info("✅ Send button clicked")
                        sent = True
                    except Exception as e:
                        logger.warning(f"Send button click failed: {e}")

                # Method 2: Enter key fallback
                if not sent:
                    try:
                        message_input.send_keys(Keys.ENTER)
                        logger.info("✅ Enter key used")
                        sent = True
                    except Exception as e:
                        logger.warning(f"Enter key failed: {e}")

                if not sent:
                    logger.error("❌ Could not send message")
                    continue

                # Wait and verify message was sent
                time.sleep(5)

                # Look for message in chat (optional verification)
                try:
                    message_containers = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        "div[data-testid*='msg'], .message-out, [role='row']"
                    )

                    if message_containers:
                        logger.debug(f"Found {len(message_containers)} message containers")

                except Exception as e:
                    logger.debug(f"Could not verify message: {e}")

                # Consider it successful
                logger.info("✅ Message sent successfully")
                return True

            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ Failed after {max_retries} attempts")

                    # Final screenshot
                    screenshot_path = f"logs/screenshots/send_failed_{int(time.time())}.png"
                    os.makedirs("logs/screenshots", exist_ok=True)
                    self.driver.save_screenshot(screenshot_path)
                    logger.debug(f"Error screenshot: {screenshot_path}")

                    return False
                time.sleep(3)

        return False

    def send_to_saved_number(self, message: str) -> bool:
        """Send to configured WhatsApp number"""
        if not self.whatsapp_number:
            logger.error("❌ No WhatsApp number configured")
            return False
        return self.send_message(self.whatsapp_number, message)

    def is_session_active(self) -> bool:
        """Check if session is active"""
        if not self.driver:
            self.session_active = False
            return False

        try:
            is_active = bool(self._wait_for_element(self.selectors["chat_list"], timeout=5))
            self.session_active = is_active
            return is_active
        except:
            self.session_active = False
            return False

    def stop_session(self):
        """Stop WhatsApp session"""
        logger.info("🛑 Stopping WhatsApp session...")
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        finally:
            self.driver = None
            self.session_active = False

# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client = WhatsAppClient()

    try:
        if client.start_session():
            test_msg = f"UNIFIED CLIENT TEST - {time.strftime('%H:%M:%S')}"
            if client.send_to_saved_number(test_msg):
                print("✅ Test message sent!")
            else:
                print("❌ Test failed")
        input("Press Enter to close...")
    finally:
        client.stop_session()
