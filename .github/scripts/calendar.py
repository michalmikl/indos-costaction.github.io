#!/usr/bin/env python3
"""
Downloads an ICS file and replaces online meeting URLs in LOCATION fields with
"announced via the mailing list" to prevent public visibility of meeting links.
"""

import urllib.request
import urllib.error
import ssl
import sys
import re


def download_ics(url):
    """Download ICS file from URL (ignores SSL certificate errors)."""
    print(f"Downloading from: {url}")
    
    # Disable SSL verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl_context)
    )
    urllib.request.install_opener(opener)
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read().decode('utf-8')
            print(f"Downloaded {len(content)} bytes")
            return content
    except Exception as e:
        raise Exception(f"Download failed: {e}")


def replace_locations(ics_content, new_location="announced via the mailing list"):
    """Replace LOCATION fields containing http:// or https:// with new text."""
    lines = ics_content.splitlines()
    modified_lines = []
    modified_count = 0
    
    location_pattern = re.compile(r'^(LOCATION):(.*)$', re.IGNORECASE)
    
    for line in lines:
        match = location_pattern.match(line)
        if match and re.search(r'https?://', match.group(2), re.IGNORECASE):
            modified_lines.append(f"LOCATION:{new_location}")
            modified_count += 1
        else:
            modified_lines.append(line)
    
    print(f"Modified {modified_count} LOCATION entries containing URLs")
    return '\n'.join(modified_lines)


def main():
    # Get command line arguments or use defaults
    url = sys.argv[1] if len(sys.argv) > 1 else "https://ics.calendarlabs.com/101/ff3c16d4/Netherlands_Holidays.ics"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "calendar.ics"
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)
    
    try:
        print("\n=== Downloading ===")
        ics_content = download_ics(url)
        
        print("\n=== Processing ===")
        modified_content = replace_locations(ics_content)
        
        print("\n=== Saving ===")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"Saved to: {output_file}")
        
        print("\n✅ Success!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()