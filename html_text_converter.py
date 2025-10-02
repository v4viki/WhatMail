#!/usr/bin/env python3
"""
Enhanced HTML to Text Converter for WhatsApp Messages
Clean, readable text extraction from HTML emails
"""

import re
import html
from bs4 import BeautifulSoup
from typing import Optional

class HTMLToTextConverter:
    """Enhanced HTML to text converter for clean WhatsApp messages"""

    def __init__(self):
        # Patterns for common email elements
        self.css_pattern = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)
        self.script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
        self.comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)

        # WhatsApp formatting characters to avoid
        self.whatsapp_special_chars = ['*', '_', '~', '```']

    def clean_html_email(self, html_content: str, max_length: int = 800) -> str:
        """Convert HTML email to clean, readable text for WhatsApp"""
        if not html_content:
            return "No content available"

        try:
            # Step 1: Basic HTML cleaning
            clean_content = self._remove_html_noise(html_content)

            # Step 2: Parse with BeautifulSoup
            soup = BeautifulSoup(clean_content, 'html.parser')

            # Step 3: Extract meaningful content
            extracted_text = self._extract_meaningful_content(soup)

            # Step 4: Clean and format text
            final_text = self._format_for_whatsapp(extracted_text, max_length)

            return final_text or "Email content could not be extracted"

        except Exception as e:
            print(f"Error converting HTML: {e}")
            return "Error extracting email content"

    def _remove_html_noise(self, html_content: str) -> str:
        """Remove CSS, scripts, and other noise from HTML"""
        # Remove CSS styles
        html_content = self.css_pattern.sub('', html_content)

        # Remove JavaScript
        html_content = self.script_pattern.sub('', html_content)

        # Remove HTML comments
        html_content = self.comment_pattern.sub('', html_content)

        # Remove common tracking pixels and images
        html_content = re.sub(r'<img[^>]*tracking[^>]*>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<img[^>]*pixel[^>]*>', '', html_content, flags=re.IGNORECASE)

        return html_content

    def _extract_meaningful_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful content from parsed HTML"""
        # Remove unwanted elements
        unwanted_tags = [
            'style', 'script', 'meta', 'link', 'head', 'title',
            'noscript', 'iframe', 'embed', 'object'
        ]

        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove elements with specific classes/ids (common email cruft)
        unwanted_selectors = [
            'div[style*="display:none"]',
            'div[style*="visibility:hidden"]',
            '.email-footer',
            '.unsubscribe',
            '.social-links',
            '.preheader'
        ]

        for selector in unwanted_selectors:
            try:
                for element in soup.select(selector):
                    element.decompose()
            except:
                continue

        # Extract text with better formatting
        content_parts = []

        # Look for main content areas first
        main_content = self._find_main_content(soup)

        if main_content:
            content_parts.append(self._process_element(main_content))
        else:
            # Fallback: process body content
            body = soup.find('body') or soup
            content_parts.append(self._process_element(body))

        return '\n'.join(filter(None, content_parts))

    def _find_main_content(self, soup: BeautifulSoup) -> Optional:
        """Find the main content area of the email"""
        # Common selectors for email main content
        main_selectors = [
            'main',
            '.main-content',
            '.email-content',
            '.content',
            'article',
            '[role="main"]',
            '.message-body',
            'td[class*="content"]',
            'div[class*="content"]'
        ]

        for selector in main_selectors:
            try:
                main = soup.select_one(selector)
                if main:
                    return main
            except:
                continue

        return None

    def _process_element(self, element) -> str:
        """Process an element and extract clean text"""
        if not element:
            return ""

        # Handle different element types
        text_parts = []

        for child in element.children:
            if hasattr(child, 'name') and child.name:
                # It's a tag
                tag_name = child.name.lower()

                if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # Headers
                    header_text = child.get_text(strip=True)
                    if header_text:
                        text_parts.append(f"\n{header_text.upper()}\n")

                elif tag_name in ['p', 'div']:
                    # Paragraphs and divs
                    para_text = child.get_text(strip=True)
                    if para_text and len(para_text) > 5:  # Skip very short divs
                        text_parts.append(f"{para_text}\n")

                elif tag_name in ['ul', 'ol']:
                    # Lists
                    list_items = []
                    for li in child.find_all('li'):
                        li_text = li.get_text(strip=True)
                        if li_text:
                            list_items.append(f"• {li_text}")

                    if list_items:
                        text_parts.append('\n'.join(list_items) + '\n')

                elif tag_name == 'br':
                    text_parts.append('\n')

                elif tag_name in ['strong', 'b']:
                    strong_text = child.get_text(strip=True)
                    if strong_text:
                        text_parts.append(f"{strong_text}")

                elif tag_name == 'a':
                    # Links
                    link_text = child.get_text(strip=True)
                    href = child.get('href', '')

                    if link_text:
                        if href and href.startswith('http') and len(href) < 50:
                            text_parts.append(f"{link_text} ({href})")
                        else:
                            text_parts.append(link_text)

                elif tag_name in ['table']:
                    # Tables - simplified
                    table_text = child.get_text(separator=' | ', strip=True)
                    if table_text:
                        text_parts.append(f"{table_text}\n")

                else:
                    # Other elements, just get text
                    other_text = child.get_text(strip=True)
                    if other_text and len(other_text) > 3:
                        text_parts.append(other_text)

            else:
                # It's text content
                text_content = str(child).strip()
                if text_content and len(text_content) > 2:
                    text_parts.append(text_content)

        return ' '.join(text_parts)

    def _format_for_whatsapp(self, text: str, max_length: int) -> str:
        """Format text for WhatsApp compatibility"""
        if not text:
            return ""

        # Step 1: Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove empty lines with spaces
        text = re.sub(r'\n{3,}', '\n\n', text)     # Max 2 consecutive newlines
        text = re.sub(r'[ \t]+', ' ', text)          # Multiple spaces to single space

        # Step 2: Remove WhatsApp formatting characters that might interfere
        for char in self.whatsapp_special_chars:
            text = text.replace(char, '')

        # Step 3: Clean up common email artifacts
        artifacts_to_remove = [
            r'View in browser.*?\n',
            r'Unsubscribe.*?\n', 
            r'This email was sent to.*?\n',
            r'<!DOCTYPE.*?>',
            r'<html.*?>',
            r'<head.*?</head>',
            r'<meta.*?>',
            r'<title.*?</title>',
            r'<style.*?</style>',
            r'<script.*?</script>',
            r'\s*{[^}]*}\s*',  # CSS rules
            r'font-size:\s*\d+px[^;]*;?',
            r'line-height:[^;]*;?',
            r'color:[^;]*;?',
            r'margin:[^;]*;?',
            r'padding:[^;]*;?'
        ]

        for pattern in artifacts_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

        # Step 4: Remove URLs that are too long
        text = re.sub(r'https?://[^\s]{50,}', '[LINK]', text)

        # Step 5: Clean HTML entities
        text = html.unescape(text)

        # Step 6: Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Step 7: Clean up remaining artifacts
        text = re.sub(r'\s*[{}|]+\s*', ' ', text)  # Remove CSS artifacts
        text = re.sub(r'\s*[;:]+\s*$', '', text, flags=re.MULTILINE)  # Remove trailing punctuation

        # Step 8: Truncate if too long
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + "...\n\n[Message truncated]"

        # Step 9: Final cleanup
        text = text.strip()

        # Step 10: Ensure it's not too short or meaningless
        if len(text) < 10 or not re.search(r'[a-zA-Z]', text):
            return "Email content could not be extracted properly"

        return text

# Global instance for easy import
html_converter = HTMLToTextConverter()

# Convenience function
def convert_html_to_text(html_content: str, max_length: int = 800) -> str:
    """Convert HTML email content to clean WhatsApp text"""
    return html_converter.clean_html_email(html_content, max_length)

# Test function
if __name__ == "__main__":
    # Test with sample HTML
    sample_html = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Resume Edge</title>
        <style>
        .desktop-only { display:block !important; }
        .mobile-only { display:none !important; }
        </style>
    </head>
    <body>
        <h1>New Job Opportunities</h1>
        <p>Dear candidate,</p>
        <p>We found <strong>3 new positions</strong> matching your profile:</p>
        <ul>
            <li>Software Engineer at Google - $120k</li>
            <li>Data Scientist at Microsoft - $110k</li>
            <li>Product Manager at Amazon - $130k</li>
        </ul>
        <p>Click <a href="https://example.com/apply">here to apply</a>.</p>
        <div style="display:none">Tracking pixel</div>
    </body>
    </html>
    """

    result = convert_html_to_text(sample_html)
    print("Original HTML:")
    print("-" * 40)
    print(sample_html[:200] + "...")
    print("-" * 40)
    print("Converted text:")
    print("-" * 40)
    print(result)
    print("-" * 40)
