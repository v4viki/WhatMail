#!/usr/bin/env python3
"""
WhatMail GUI - Enhanced interface with status monitoring and error handling
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys
from dotenv import load_dotenv, set_key
import time

# Import our main application
from whatmail_app import WhatMailApp

# Load environment
load_dotenv()

class WhatMailGUI:
    """Enhanced GUI for WhatMail application"""

    def __init__(self):
        self.root = tk.Tk()
        self.app = WhatMailApp()
        self.status_monitor_active = False
        self.log_monitor_active = False

        self.setup_gui()
        self.load_config()
        self.start_status_monitor()

    def setup_gui(self):
        """Setup the GUI interface"""
        self.root.title("📧 WhatMail - Email to WhatsApp Notifier v2.0")
        self.root.geometry("600x750")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f2f5")

        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weight
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, 
            text="📧 WhatMail - Email to WhatsApp Notifier",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky='w')

        # Status Section
        self.create_status_section(main_frame, 1)

        # Configuration Section
        self.create_config_section(main_frame, 2)

        # Control Section
        self.create_control_section(main_frame, 3)

        # Log Section
        self.create_log_section(main_frame, 4)

        # Configure row weights for resizing
        for i in range(5):
            main_frame.rowconfigure(i, weight=0)
        main_frame.rowconfigure(4, weight=1)  # Log section expands

    def create_status_section(self, parent, row):
        """Create status monitoring section"""
        status_frame = ttk.LabelFrame(parent, text="📊 System Status", padding="10")
        status_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)

        # Status indicators
        ttk.Label(status_frame, text="Application:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.app_status_var = tk.StringVar(value="🔴 Stopped")
        self.app_status_label = ttk.Label(status_frame, textvariable=self.app_status_var, font=('Segoe UI', 10, 'bold'))
        self.app_status_label.grid(row=0, column=1, sticky='w')

        ttk.Label(status_frame, text="WhatsApp:").grid(row=1, column=0, sticky='w', padx=(0, 10))
        self.whatsapp_status_var = tk.StringVar(value="🔴 Disconnected")
        self.whatsapp_status_label = ttk.Label(status_frame, textvariable=self.whatsapp_status_var)
        self.whatsapp_status_label.grid(row=1, column=1, sticky='w')

        ttk.Label(status_frame, text="Email Config:").grid(row=2, column=0, sticky='w', padx=(0, 10))
        self.email_status_var = tk.StringVar(value="🔴 Not Configured")
        self.email_status_label = ttk.Label(status_frame, textvariable=self.email_status_var)
        self.email_status_label.grid(row=2, column=1, sticky='w')

    def create_config_section(self, parent, row):
        """Create configuration section"""
        config_frame = ttk.LabelFrame(parent, text="⚙️ Configuration", padding="10")
        config_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)

        # Configuration fields
        self.config_vars = {}
        configs = [
            ("EMAIL", "Gmail Address:", "your-email@gmail.com"),
            ("PASSWORD", "App Password:", ""),
            ("WHATSAPP", "WhatsApp Number:", "+919876543210"),
            ("FILTERS", "Keywords (comma-separated):", "urgent,otp,job,offer,interview")
        ]

        for i, (key, label, placeholder) in enumerate(configs):
            ttk.Label(config_frame, text=label).grid(row=i, column=0, sticky='w', padx=(0, 10), pady=2)

            if key == "PASSWORD":
                entry = ttk.Entry(config_frame, show="*", width=40)
            else:
                entry = ttk.Entry(config_frame, width=40)

            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)

            if placeholder:
                entry.insert(0, "")  # Will be loaded from config

            self.config_vars[key] = entry

        # Config buttons
        config_btn_frame = ttk.Frame(config_frame)
        config_btn_frame.grid(row=len(configs), column=0, columnspan=2, pady=(10, 0))

        ttk.Button(config_btn_frame, text="💾 Save Config", command=self.save_config).pack(side='left', padx=(0, 5))
        ttk.Button(config_btn_frame, text="🔄 Reload", command=self.load_config).pack(side='left', padx=5)
        ttk.Button(config_btn_frame, text="🧪 Test Connections", command=self.test_connections).pack(side='left', padx=5)

    def create_control_section(self, parent, row):
        """Create control buttons section"""
        control_frame = ttk.LabelFrame(parent, text="🎮 Controls", padding="10")
        control_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack()

        self.start_btn = ttk.Button(btn_frame, text="▶️ Start Monitoring", command=self.start_monitoring, width=20)
        self.start_btn.pack(side='left', padx=(0, 10))

        self.stop_btn = ttk.Button(btn_frame, text="⏹️ Stop Monitoring", command=self.stop_monitoring, width=20, state='disabled')
        self.stop_btn.pack(side='left', padx=10)

        ttk.Button(btn_frame, text="📋 View Logs", command=self.open_log_folder, width=15).pack(side='left', padx=(10, 0))

    def create_log_section(self, parent, row):
        """Create log monitoring section"""
        log_frame = ttk.LabelFrame(parent, text="📋 Activity Log", padding="10")
        log_frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=15, 
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Log controls
        log_ctrl_frame = ttk.Frame(log_frame)
        log_ctrl_frame.grid(row=1, column=0, sticky='w', pady=(5, 0))

        ttk.Button(log_ctrl_frame, text="🗑️ Clear Log", command=self.clear_log).pack(side='left', padx=(0, 5))
        ttk.Button(log_ctrl_frame, text="💾 Save Log", command=self.save_log).pack(side='left')

        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            log_ctrl_frame, 
            text="Auto-scroll", 
            variable=self.auto_scroll_var
        ).pack(side='right')

    def load_config(self):
        """Load configuration from environment"""
        for key, entry in self.config_vars.items():
            value = os.getenv(key, "")
            entry.delete(0, tk.END)
            entry.insert(0, value)

        self.log_message("🔄 Configuration reloaded")

    def save_config(self):
        """Save configuration to .env file"""
        try:
            # Ensure .env file exists
            if not os.path.exists('.env'):
                with open('.env', 'w') as f:
                    f.write("# WhatMail Configuration\n")

            # Save each configuration
            for key, entry in self.config_vars.items():
                value = entry.get().strip()
                set_key('.env', key, value)
                os.environ[key] = value

            self.log_message("✅ Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully!")

        except Exception as e:
            error_msg = f"Failed to save configuration: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

    def start_monitoring(self):
        """Start email monitoring"""
        self.log_message("🚀 Starting email monitoring...")

        # Save config first
        self.save_config()

        # Start monitoring in background thread
        def start_thread():
            try:
                if self.app.start_monitoring():
                    self.root.after(0, lambda: self.log_message("✅ Monitoring started successfully"))
                    self.root.after(0, self.update_control_buttons)
                else:
                    self.root.after(0, lambda: self.log_message("❌ Failed to start monitoring"))
            except Exception as e:
                error_msg = f"Error starting monitoring: {str(e)}"
                self.root.after(0, lambda: self.log_message(f"❌ {error_msg}"))

        threading.Thread(target=start_thread, daemon=True).start()

    def stop_monitoring(self):
        """Stop email monitoring"""
        self.log_message("🛑 Stopping email monitoring...")

        def stop_thread():
            try:
                self.app.stop_monitoring()
                self.root.after(0, lambda: self.log_message("✅ Monitoring stopped"))
                self.root.after(0, self.update_control_buttons)
            except Exception as e:
                error_msg = f"Error stopping monitoring: {str(e)}"
                self.root.after(0, lambda: self.log_message(f"❌ {error_msg}"))

        threading.Thread(target=stop_thread, daemon=True).start()

    def test_connections(self):
        """Test email and WhatsApp connections"""
        self.log_message("🧪 Testing connections...")

        def test_thread():
            try:
                results = self.app.test_connection()

                email_status = "✅" if results['email'] else "❌"
                whatsapp_status = "✅" if results['whatsapp'] else "❌"

                self.root.after(0, lambda: self.log_message(f"📧 Email connection: {email_status}"))
                self.root.after(0, lambda: self.log_message(f"📱 WhatsApp connection: {whatsapp_status}"))

                if results['errors']:
                    for error in results['errors']:
                        self.root.after(0, lambda e=error: self.log_message(f"❌ {e}"))

                # Show results dialog
                message = f"Email: {email_status}\nWhatsApp: {whatsapp_status}"
                if results['errors']:
                    message += "\n\nErrors:\n" + "\n".join(results['errors'])

                self.root.after(0, lambda: messagebox.showinfo("Connection Test Results", message))

            except Exception as e:
                error_msg = f"Error testing connections: {str(e)}"
                self.root.after(0, lambda: self.log_message(f"❌ {error_msg}"))

        threading.Thread(target=test_thread, daemon=True).start()

    def start_status_monitor(self):
        """Start status monitoring in background"""
        self.status_monitor_active = True

        def monitor():
            while self.status_monitor_active:
                try:
                    status = self.app.get_status()

                    # Update status labels
                    app_status = "🟢 Running" if status['is_running'] else "🔴 Stopped"
                    whatsapp_status = "🟢 Connected" if status['whatsapp_active'] else "🔴 Disconnected"
                    email_status = "🟢 Configured" if status['email_configured'] else "🔴 Not Configured"

                    self.root.after(0, lambda: self.app_status_var.set(app_status))
                    self.root.after(0, lambda: self.whatsapp_status_var.set(whatsapp_status))
                    self.root.after(0, lambda: self.email_status_var.set(email_status))

                    # Update button states
                    self.root.after(0, self.update_control_buttons)

                except Exception as e:
                    print(f"Status monitor error: {e}")

                time.sleep(2)  # Update every 2 seconds

        threading.Thread(target=monitor, daemon=True).start()

    def update_control_buttons(self):
        """Update control button states"""
        if self.app.is_running:
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
        else:
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')

    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_entry)

        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)

        # Limit log size (keep last 1000 lines)
        lines = self.log_text.get('1.0', tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete('1.0', f'{len(lines)-1000}.0')

    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete('1.0', tk.END)
        self.log_message("🗑️ Log cleared")

    def save_log(self):
        """Save log to file"""
        try:
            os.makedirs("logs", exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"logs/gui_log_{timestamp}.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get('1.0', tk.END))

            self.log_message(f"💾 Log saved to {filename}")
            messagebox.showinfo("Saved", f"Log saved to {filename}")

        except Exception as e:
            error_msg = f"Failed to save log: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

    def open_log_folder(self):
        """Open the logs folder"""
        try:
            import subprocess
            import platform

            log_path = os.path.abspath("logs")
            os.makedirs(log_path, exist_ok=True)

            if platform.system() == "Windows":
                subprocess.run(f'explorer "{log_path}"', shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(f'open "{log_path}"', shell=True)
            else:  # Linux
                subprocess.run(f'xdg-open "{log_path}"', shell=True)

        except Exception as e:
            error_msg = f"Failed to open log folder: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

    def on_closing(self):
        """Handle application closing"""
        self.status_monitor_active = False

        if self.app.is_running:
            if messagebox.askquestion("Confirm Exit", "Monitoring is active. Stop and exit?") == 'yes':
                self.app.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.log_message("🚀 WhatMail GUI started")
        self.log_message("💡 Configure your settings and click 'Start Monitoring'")
        self.root.mainloop()


if __name__ == "__main__":
    try:
        gui = WhatMailGUI()
        gui.run()
    except Exception as e:
        print(f"GUI Error: {e}")
        messagebox.showerror("Fatal Error", f"Failed to start GUI: {e}")
