#!/usr/bin/env python3
"""
WhatsApp Only Test Script
Test WhatsApp message sending functionality separately
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_whatsapp_sending():
    """Test WhatsApp sending only"""
    print("📱 Testing WhatsApp Sending...")
    print("=" * 50)

    # Check WhatsApp number
    whatsapp_number = os.getenv("WHATSAPP", "").strip()

    if not whatsapp_number:
        print("❌ WhatsApp number not configured")
        print("💡 Add WHATSAPP=+919876543210 to your .env file")
        return False

    print(f"📞 WhatsApp Number: {whatsapp_number}")

    try:
        # Import WhatsApp client
        from whatsapp_client_unicode_fixed import WhatsAppClient
        print("✅ WhatsApp client imported successfully")

        # Initialize client
        client = WhatsAppClient(headless=False)  # Keep visible for debugging
        print("✅ WhatsApp client initialized")

        # Start session
        print("\n🚀 Starting WhatsApp Web session...")
        print("📱 Chrome will open - scan QR code if needed...")

        if client.start_session(timeout=90):
            print("✅ WhatsApp session started successfully")

            # Wait a bit for session to stabilize
            print("⏳ Waiting for session to stabilize...")
            time.sleep(5)

            # Test message sending
            test_messages = [
                f"🧪 Test Message 1\nTime: {datetime.now().strftime('%H:%M:%S')}",
                f"🤖 WhatMail Test\nThis is an automated test from your email bot.",
                f"✅ Integration Test\nIf you receive this, WhatsApp sending works!"
            ]

            success_count = 0

            for i, message in enumerate(test_messages, 1):
                print(f"\n📤 Sending test message {i}/3...")
                print(f"Message: {message[:50]}...")

                if client.send_to_saved_number(message):
                    print(f"✅ Message {i} sent successfully!")
                    success_count += 1

                    # Wait between messages
                    if i < len(test_messages):
                        print("⏳ Waiting 10 seconds before next message...")
                        time.sleep(10)
                else:
                    print(f"❌ Message {i} failed to send")

                    # Take screenshot for debugging
                    try:
                        screenshot_path = f"logs/screenshots/whatsapp_test_fail_{int(time.time())}.png"
                        os.makedirs("logs/screenshots", exist_ok=True)
                        client.driver.save_screenshot(screenshot_path)
                        print(f"📸 Screenshot saved: {screenshot_path}")
                    except:
                        pass

                    break

            print(f"\n📊 Results: {success_count}/{len(test_messages)} messages sent successfully")

            if success_count > 0:
                print("\n🎉 WhatsApp sending is working!")
                print("📱 Check your WhatsApp to confirm messages received")
            else:
                print("\n❌ WhatsApp sending failed")
                print("🔧 Troubleshooting tips:")
                print("   1. Make sure you scanned QR code")
                print("   2. Check if WhatsApp Web works manually in browser")
                print("   3. Try different phone number format")
                print("   4. Check Chrome console for errors")

            # Keep session open for inspection
            input("\n⏸️ Press Enter to close WhatsApp session...")

            # Clean up
            client.stop_session()
            return success_count > 0

        else:
            print("❌ Failed to start WhatsApp session")
            print("🔧 Troubleshooting:")
            print("   1. Make sure Chrome is installed")
            print("   2. Try clearing chrome_profile folder")
            print("   3. Check if WhatsApp Web works in your browser")
            print("   4. Disable antivirus/firewall temporarily")
            return False

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure whatsapp_client.py is in your project folder")
        return False
    except Exception as e:
        print(f"❌ WhatsApp Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_whatsapp_web_manually():
    """Guide for manual WhatsApp Web testing"""
    print("\n📱 Manual WhatsApp Web Test Guide:")
    print("-" * 50)
    print("1. Open Chrome browser")
    print("2. Go to https://web.whatsapp.com")
    print("3. Scan QR code with your phone")
    print("4. Try sending a message manually")
    print("5. If this works, the issue is with our automation")
    print("6. If this doesn't work, check your internet/WhatsApp account")

if __name__ == "__main__":
    try:
        print("🧪 WhatsApp Sending Test")
        print("=" * 50)

        # Test WhatsApp sending
        success = test_whatsapp_sending()

        if not success:
            test_whatsapp_web_manually()

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
