#!/usr/bin/env python3
"""
WhatsApp Delivery Fix - For when messages show "sent" but don't deliver
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def advanced_whatsapp_test():
    """Advanced test to identify delivery issues"""
    print("🔧 WhatsApp Advanced Delivery Test")
    print("=" * 50)

    try:
        from whatsapp_client_unicode_fixed import WhatsAppClient

        client = WhatsAppClient(headless=False)  # Keep visible

        print("Starting WhatsApp session...")
        if not client.start_session(timeout=60):
            print("❌ Failed to start session")
            return False

        print("✅ Session started")

        # Get phone number
        phone = os.getenv("WHATSAPP", "").strip()
        print(f"Target: {phone}")

        # Navigate to chat
        chat_url = f"https://web.whatsapp.com/send?phone={phone}"
        print(f"\nNavigating to: {chat_url}")
        client.driver.get(chat_url)

        # Wait and check what happens
        print("\nWaiting 15 seconds for page to fully load...")
        time.sleep(15)

        # Check current URL
        current_url = client.driver.current_url
        print(f"Current URL: {current_url}")

        # Critical check: Are we on the right page?
        if "web.whatsapp.com/send" in current_url:
            print("⚠️ Still on send page - contact may not exist")
        elif "chat" in current_url or "web.whatsapp.com" in current_url:
            print("✅ Successfully navigated to chat")
        else:
            print(f"❌ Unexpected URL: {current_url}")

        # Look for any error messages or warnings
        try:
            # Check for common WhatsApp error indicators
            error_selectors = [
                "[data-testid='alert-phone-number-invalid']",
                ".error",
                "[role='alert']",
                "div:contains('Phone number shared')",
                "div:contains('Invalid')",
                "div:contains('not found')"
            ]

            for selector in error_selectors:
                try:
                    elements = client.driver.find_elements("css selector", selector)
                    if elements and elements[0].is_displayed():
                        error_text = elements[0].text
                        print(f"🚨 ERROR FOUND: {error_text}")
                        return False
                except:
                    continue

        except Exception as e:
            print(f"Could not check for errors: {e}")

        # Look for message input
        print("\nLooking for message input...")
        message_input = None

        # Try multiple selectors
        input_selectors = [
            "div[contenteditable='true'][data-tab='10']",
            "div[data-testid='conversation-compose-box-input']",
            "div[title='Type a message']",
            "div[role='textbox'][contenteditable='true']",
            "div[contenteditable='true']"
        ]

        for i, selector in enumerate(input_selectors):
            try:
                elements = client.driver.find_elements("css selector", selector)
                if elements and elements[0].is_displayed():
                    message_input = elements[0]
                    print(f"✅ Found input with selector {i+1}")
                    break
            except:
                continue

        if not message_input:
            print("❌ CRITICAL: No message input found")
            print("\nThis means:")
            print("1. Phone number doesn't have WhatsApp")
            print("2. Contact blocked you")
            print("3. WhatsApp interface changed")

            # Take screenshot
            screenshot_path = f"logs/screenshots/no_input_{int(time.time())}.png"
            os.makedirs("logs/screenshots", exist_ok=True)
            client.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")

            input("Press Enter to close...")
            return False

        # Try enhanced message sending
        test_message = f"DELIVERY TEST {datetime.now().strftime('%H:%M:%S')} - Reply if received"

        print(f"\nSending message: {test_message}")

        # Method 1: Direct click and type
        try:
            print("Method 1: Direct typing...")
            message_input.click()
            time.sleep(2)
            message_input.clear()
            time.sleep(1)

            # Type character by character to avoid issues
            for char in test_message:
                message_input.send_keys(char)
                time.sleep(0.05)  # Small delay between characters

            time.sleep(2)

            # Check if text is there
            input_text = message_input.get_attribute("innerText") or message_input.get_attribute("textContent") or ""
            print(f"Text in input: '{input_text[:50]}...'")

            if test_message[:10] not in input_text:
                print("⚠️ Text didn't appear correctly, trying JavaScript method...")

                # Method 2: JavaScript injection
                js_script = """
                arguments[0].focus();
                arguments[0].innerHTML = '';
                arguments[0].innerText = arguments[1];
                arguments[0].textContent = arguments[1];

                // Trigger events
                var event = new Event('input', {bubbles: true});
                arguments[0].dispatchEvent(event);
                """
                client.driver.execute_script(js_script, message_input, test_message)
                time.sleep(2)
                print("JavaScript injection completed")

        except Exception as e:
            print(f"Error in message input: {e}")
            return False

        # Look for send button
        print("\nLooking for send button...")
        send_button = None

        send_selectors = [
            "button[data-testid='compose-btn-send']",
            "button[aria-label='Send']",
            "span[data-testid='send']",
            "button[type='submit']",
            "div[role='button'][aria-label*='Send']"
        ]

        for i, selector in enumerate(send_selectors):
            try:
                elements = client.driver.find_elements("css selector", selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        send_button = element
                        print(f"✅ Found send button with selector {i+1}")
                        break
                if send_button:
                    break
            except:
                continue

        # Send the message
        sent_successfully = False

        if send_button:
            try:
                print("Clicking send button...")
                # Scroll send button into view
                client.driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
                time.sleep(1)

                # Click send button
                send_button.click()
                print("✅ Send button clicked")
                sent_successfully = True

            except Exception as e:
                print(f"Send button click failed: {e}")

        if not sent_successfully:
            try:
                print("Trying Enter key...")
                from selenium.webdriver.common.keys import Keys
                message_input.send_keys(Keys.ENTER)
                print("✅ Enter key pressed")
                sent_successfully = True
            except Exception as e:
                print(f"Enter key failed: {e}")

        if not sent_successfully:
            print("❌ Could not send message")
            return False

        # Wait and check for message delivery indicators
        print("\nWaiting 10 seconds to check delivery status...")
        time.sleep(10)

        # Look for delivery indicators
        try:
            # Check for sent message in chat
            message_containers = client.driver.find_elements("css selector", 
                "div[data-testid='msg-container'], .message-out, [role='row']")

            print(f"Found {len(message_containers)} message containers")

            # Check the most recent message
            if message_containers:
                recent_msg = message_containers[-1]
                msg_text = recent_msg.get_attribute("innerText") or recent_msg.get_attribute("textContent") or ""

                if test_message[:15] in msg_text:
                    print("✅ Message appears in chat interface")

                    # Check for delivery status indicators
                    status_indicators = recent_msg.find_elements("css selector", 
                        "[data-testid*='msg-dblcheck'], [data-testid*='msg-check'], svg")

                    if status_indicators:
                        print(f"✅ Found {len(status_indicators)} delivery status indicators")
                        print("Message has delivery status - should be delivered")
                    else:
                        print("⚠️ No delivery status indicators found")

                else:
                    print("⚠️ Recent message doesn't match our text")
                    print(f"Recent message: '{msg_text[:100]}...'")
            else:
                print("❌ No message containers found - message may not have been sent")

        except Exception as e:
            print(f"Error checking delivery status: {e}")

        # Final screenshot
        screenshot_path = f"logs/screenshots/final_test_{int(time.time())}.png"
        client.driver.save_screenshot(screenshot_path)
        print(f"\n📸 Final screenshot: {screenshot_path}")

        print("\n" + "="*60)
        print("CRITICAL TEST:")
        print("="*60)
        print("1. Look at your WhatsApp on phone RIGHT NOW")
        print("2. Check if you received the test message")
        print(f"3. Message should contain: 'DELIVERY TEST'")
        print("4. If you see it in WhatsApp Web but not on phone = sync issue")
        print("5. If you don't see it anywhere = sending failed")

        # Manual verification
        received = input("\nDid you receive the message on your PHONE? (y/n): ").strip().lower()

        if received == 'y':
            print("\n🎉 SUCCESS! Message delivery is working!")
            print("Your WhatsApp automation is functioning correctly.")
            return True
        else:
            print("\n🔧 DELIVERY ISSUE CONFIRMED")
            print("\nPossible causes:")
            print("1. WhatsApp Web sync delay (wait 2-3 more minutes)")
            print("2. Phone not connected to internet")
            print("3. WhatsApp on phone is logged out/inactive")
            print("4. WhatsApp Web automation detection")

            # Additional checks
            web_visible = input("Do you see the message in WhatsApp Web interface? (y/n): ").strip().lower()

            if web_visible == 'y':
                print("\n📱 SYNC ISSUE:")
                print("- Message sent successfully to WhatsApp Web")
                print("- Not syncing to phone")
                print("- Check phone internet connection")
                print("- Wait 2-3 minutes and check again")
                print("- Restart WhatsApp on phone")
            else:
                print("\n🚨 SENDING ISSUE:")
                print("- Message not appearing in WhatsApp Web")
                print("- Automation may be detected/blocked")
                print("- Try different approach or contact")

            return False

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            input("\nPress Enter to close...")
            client.stop_session()
        except:
            pass

if __name__ == "__main__":
    advanced_whatsapp_test()
