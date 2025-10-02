#!/usr/bin/env python3
"""
Final WhatsApp Fix Test Script
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_final_whatsapp_fix():
    """Test the final WhatsApp fix"""
    print("🔧 Testing Final WhatsApp Fix")
    print("=" * 50)

    try:
        from whatsapp_client_unicode_fixed import WhatsAppClientFixed

        print("✅ Importing fixed client...")
        client = WhatsAppClientFixed(headless=False)

        print("🚀 Starting session with updated selectors...")
        if client.start_session(timeout=60):
            print("✅ Session started successfully!")

            # Test message
            test_message = f"FINAL FIX TEST - {datetime.now().strftime('%H:%M:%S')} - This should work now!"

            print(f"📤 Sending test message...")
            print(f"Message: {test_message}")

            if client.send_to_saved_number(test_message):
                print("\n🎉 SUCCESS! Message sent with final fix!")
                print("📱 Check your WhatsApp now - this should work!")

                # Wait for user confirmation
                received = input("\nDid you receive the message on your phone? (y/n): ").strip().lower()

                if received == 'y':
                    print("\n🎉 EXCELLENT! Final fix is working!")
                    print("Your WhatsApp automation is now functional!")
                    return True
                else:
                    print("\n🔧 Still having issues...")
                    print("Let me create one more diagnostic tool...")
                    return False
            else:
                print("\n❌ Message sending failed even with final fix")
                print("This might be a deeper WhatsApp Web issue")
                return False

        else:
            print("❌ Could not start WhatsApp session")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
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
    test_final_whatsapp_fix()
