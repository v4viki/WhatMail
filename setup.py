#!/usr/bin/env python3
"""
WhatMail Setup Script
Automated setup for the Email to WhatsApp Notifier
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🚀 WhatMail - Email to WhatsApp Notifier Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])

        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])

        print("✅ All packages installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")

    directories = [
        "logs",
        "logs/screenshots",
        "chrome_profile"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

def create_env_template():
    """Create .env template file"""
    print("⚙️ Creating configuration template...")

    env_template = """# WhatMail Configuration
# Fill in your details below

# Gmail Configuration
EMAIL=your-email@gmail.com
PASSWORD=your-gmail-app-password

# WhatsApp Configuration (include country code)
WHATSAPP=+919876543210

# Email Filters (comma-separated keywords)
FILTERS=urgent,important,otp,job,offer,interview,verification

# Optional Settings
CHECK_INTERVAL=300
MAX_EMAILS_PER_RUN=10
MESSAGE_TRUNCATE=2000
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
"""

    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ Created .env configuration file")
    else:
        print("ℹ️ .env file already exists")

def check_chrome():
    """Check if Chrome is installed"""
    print("🌐 Checking Chrome installation...")

    system = platform.system()
    chrome_paths = {
        'Windows': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        ],
        'Darwin': [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        ],
        'Linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium-browser'
        ]
    }

    if system in chrome_paths:
        for path in chrome_paths[system]:
            if os.path.exists(path):
                print("✅ Chrome found")
                return True

    print("⚠️ Chrome not found - you may need to install Google Chrome")
    print("   Download from: https://www.google.com/chrome/")
    return False

def create_launcher_scripts():
    """Create launcher scripts"""
    print("🚀 Creating launcher scripts...")

    if platform.system() == 'Windows':
        # Windows batch file
        bat_content = """@echo off
title WhatMail - Email to WhatsApp Notifier
echo Starting WhatMail GUI...
python whatmail_gui.py
pause
"""
        with open('start_whatmail.bat', 'w') as f:
            f.write(bat_content)
        print("✅ Created start_whatmail.bat")

    else:
        # Unix shell script
        sh_content = """#!/bin/bash
echo "Starting WhatMail GUI..."
python3 whatmail_gui.py
"""
        with open('start_whatmail.sh', 'w') as f:
            f.write(sh_content)
        os.chmod('start_whatmail.sh', 0o755)
        print("✅ Created start_whatmail.sh")

def print_setup_complete():
    """Print setup completion message"""
    print()
    print("=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. 📝 Edit the .env file with your credentials:")
    print("   - Gmail address and app password")
    print("   - WhatsApp number (with country code)")
    print()
    print("2. 🔐 Enable Gmail App Passwords:")
    print("   - Go to Google Account settings")
    print("   - Enable 2-Factor Authentication")
    print("   - Generate an App Password for 'Mail'")
    print()
    print("3. 🚀 Start the application:")
    if platform.system() == 'Windows':
        print("   - Double-click: start_whatmail.bat")
    else:
        print("   - Run: ./start_whatmail.sh")
    print("   - Or run: python whatmail_gui.py")
    print()
    print("📚 For detailed setup instructions, see README.md")
    print()

def main():
    """Main setup function"""
    print_banner()

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Create directories
    create_directories()

    # Install requirements
    if not install_requirements():
        print("❌ Setup failed - could not install required packages")
        sys.exit(1)

    # Create configuration
    create_env_template()

    # Check Chrome
    check_chrome()

    # Create launcher scripts
    create_launcher_scripts()

    # Print completion message
    print_setup_complete()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
