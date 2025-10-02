#!/usr/bin/env python3
"""
Simple WhatsApp Test - No Emojis (Unicode Fix Test)
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_simple_whatsapp():
    """Test WhatsApp with simple text only"""
    print("Simple WhatsApp Test (No Emojis)")
    print("=" * 50)

    whatsapp_number = os.getenv("WHATSAPP", "").strip()
    if not whatsapp_number:
        print("ERROR: WhatsApp number not configured")
        return False

    print(f"WhatsApp Number: {whatsapp_number}")

    try:
        # Use the fixed client
        from whatsapp_client_unicode_fixed import WhatsAppClient
        print("SUCCESS: Fixed WhatsApp client imported")

        # Initialize client
        client = WhatsAppClient(headless=False)
        print("SUCCESS: Client initialized")

        # Start session
        print("\nStarting WhatsApp session...")
        print("Please scan QR code if needed...")

        if client.start_session(timeout=60):
            print("SUCCESS: WhatsApp session started")

            # Wait for session to stabilize
            time.sleep(3)

            # Test messages (simple text only)
            test_messages = [
                f"TEST MESSAGE 1: WhatMail is working! Time: {datetime.now().strftime('%H:%M:%S')}",
                "TEST MESSAGE 2: This is your email automation bot. No emojis, just plain text.",
                "TEST MESSAGE 3: If you receive this, WhatsApp integration is successful!"
            ]

            success_count = 0

            for i, message in enumerate(test_messages, 1):
                print(f"\nSending message {i}/3...")
                print(f"Content: {message[:50]}...")

                if client.send_to_saved_number(message):
                    print(f"SUCCESS: Message {i} sent!")
                    success_count += 1

                    if i < len(test_messages):
                        print("Waiting 5 seconds...")
                        time.sleep(5)
                else:
                    print(f"FAILED: Message {i} failed")
                    break

            print(f"\nResults: {success_count}/{len(test_messages)} messages sent")

            if success_count > 0:
                print("\nSUCCESS: WhatsApp sending is working!")
                print("Check your WhatsApp to confirm messages")
            else:
                print("\nFAILED: No messages were sent")

            input("\nPress Enter to close...")
            client.stop_session()
            return success_count > 0

        else:
            print("FAILED: Could not start WhatsApp session")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        test_simple_whatsapp()
    except KeyboardInterrupt:
        print("\nTest interrupted")
