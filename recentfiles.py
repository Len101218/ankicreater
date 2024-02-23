import os
from urllib.parse import quote
from datetime import datetime
import subprocess
import xml.etree.ElementTree as ET
from urllib.parse import quote

def add_to_recent_files(file_path):
    xbel_path = os.path.expanduser('~/.local/share/recently-used.xbel')
    file_uri = 'file://' + quote(file_path)
    timestamp = datetime.now().isoformat()

    # Construct the raw XML entry string
    raw_entry = f'''
  <bookmark href="{file_uri}" added="{timestamp}Z" modified="{timestamp}Z" visited="{timestamp}Z">
    <info>
      <metadata owner="http://freedesktop.org">
        <mime:mime-type type="application/x-custom"/>
      </metadata>
    </info>
  </bookmark>'''

    # Check if the file exists, create it if it does not
    if not os.path.exists(xbel_path):
        with open(xbel_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<xbel version="1.0">\n</xbel>')

    # Append the new entry to the file
    with open(xbel_path, 'r+') as f:
        try:
            tree = ET.parse(xbel_path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"An error occurred while parsing the XBEL file: {e}")
            return False
        except FileNotFoundError:
            print(f"XBEL file not found at {xbel_path}")
        for bookmark in root.findall(".//bookmark[@href]"):
            if bookmark.get('href') == file_uri:
                touch(file_path)
                return
        content = f.read()
        position = content.rfind('</xbel>')
        if position != -1:
            # Move the file pointer to right before '</xbel>', then write the raw entry and close '</xbel>'
            f.seek(position)
            f.write(raw_entry + '\n</xbel>')
        else:
            # If '</xbel>' not found for some reason, append the entry anyway
            f.write(raw_entry)
        touch(file_path)

def touch(file_path):
    # Use subprocess.call to execute the touch command
    return_code = subprocess.call(['touch', file_path])

    if return_code == 0:
        print("File touched successfully.")
    else:
        print("Error touching file.")

