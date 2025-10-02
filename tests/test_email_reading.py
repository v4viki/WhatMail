#!/usr/bin/env python3
"""
Quick Email Reading Test
Check if Gmail credentials and email reading is working
"""

import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import sys

load_dotenv()

def decode_mime_words(text):
    """Decode MIME encoded words in headers"""
    if not text:
        return ""
    try:
        decoded_parts = decode_header(text)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    part = part.decode(encoding, errors='replace')
                else:
                    part = part.decode('utf-8', errors='replace')
            result.append(str(part))
        return ''.join(result)
    except:
        return str(text)

def test_email_reading():
    """Test email reading functionality"""
    print("🧪 Testing Email Reading...")
    print("=" * 50)

    # Get credentials
    email_addr = os.getenv("EMAIL", "").strip()
    password = os.getenv("PASSWORD", "").strip()

    if not email_addr or not password:
        print("❌ Email credentials not found in .env file")
        print("💡 Make sure your .env file contains:")
        print("   EMAIL=your-email@gmail.com")
        print("   PASSWORD=your-app-password")
        return False

    print(f"📧 Email: {email_addr}")
    print(f"🔑 Password: {'*' * len(password)} (length: {len(password)})")

    try:
        # Connect to Gmail
        print("\n🔌 Connecting to Gmail...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        print("✅ Connected to IMAP server")

        # Login
        print("🔐 Authenticating...")
        mail.login(email_addr, password)
        print("✅ Authentication successful")

        # Select inbox
        mail.select("INBOX")
        print("✅ Selected INBOX")

        # Search for unread emails
        print("\n🔍 Searching for unread emails...")
        status, messages = mail.search(None, 'UNSEEN')

        if status != 'OK':
            print("❌ Failed to search emails")
            return False

        message_ids = messages[0].split()
        unread_count = len(message_ids)

        print(f"📬 Found {unread_count} unread emails")

        if unread_count == 0:
            # Search for recent emails instead
            print("\n🔍 Searching for recent emails...")
            status, messages = mail.search(None, 'ALL')
            message_ids = messages[0].split()
            total_count = len(message_ids)
            print(f"📧 Found {total_count} total emails")

            if total_count > 0:
                # Get last 3 emails
                recent_ids = message_ids[-3:] if len(message_ids) >= 3 else message_ids
                print(f"\n📋 Reading last {len(recent_ids)} emails:")

                for i, msg_id in enumerate(recent_ids, 1):
                    try:
                        status, data = mail.fetch(msg_id, '(RFC822)')
                        if status == 'OK':
                            email_message = email.message_from_bytes(data[0][1])
                            subject = decode_mime_words(email_message.get('Subject', 'No Subject'))
                            from_addr = email_message.get('From', 'Unknown')
                            date = email_message.get('Date', 'Unknown')

                            print(f"\n📨 Email {i}:")
                            print(f"   Subject: {subject[:80]}...")
                            print(f"   From: {from_addr}")
                            print(f"   Date: {date}")

                    except Exception as e:
                        print(f"❌ Error reading email {i}: {e}")
        else:
            print(f"\n📋 Reading unread emails:")

            # Limit to first 5 unread emails
            test_ids = message_ids[:5] if len(message_ids) > 5 else message_ids

            for i, msg_id in enumerate(test_ids, 1):
                try:
                    status, data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        email_message = email.message_from_bytes(data[0][1])
                        subject = decode_mime_words(email_message.get('Subject', 'No Subject'))
                        from_addr = email_message.get('From', 'Unknown')

                        print(f"\n📨 Unread Email {i}:")
                        print(f"   Subject: {subject[:80]}...")
                        print(f"   From: {from_addr}")

                        # Check if it matches filters
                        filters = os.getenv("FILTERS", "urgent,otp,important").split(',')
                        subject_lower = subject.lower()
                        matches = [f.strip() for f in filters if f.strip().lower() in subject_lower]

                        if matches:
                            print(f"   🎯 Matches filter: {matches[0]}")
                        else:
                            print(f"   ⚪ No filter match")

                except Exception as e:
                    print(f"❌ Error reading unread email {i}: {e}")

        # Clean up
        mail.close()
        mail.logout()

        print("\n✅ Email reading test completed successfully!")
        print("\n💡 If you saw emails above, your email reading is working fine.")
        print("   The issue might be in WhatsApp sending or filtering.")

        return True

    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        if "authentication failed" in str(e).lower():
            print("\n🔧 Gmail Authentication Issue:")
            print("1. Make sure 2-Factor Authentication is enabled")
            print("2. Generate Gmail App Password:")
            print("   - Go to Google Account Settings")
            print("   - Security → App Passwords")
            print("   - Generate password for 'Mail'")
            print("   - Use that 16-character password in .env file")
            print("3. Make sure 'Less secure app access' is NOT used")
        return False

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    try:
        test_email_reading()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
