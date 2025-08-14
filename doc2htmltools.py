import os
import re
import json
import requests
import sys
from bs4 import BeautifulSoup
import chardet

# ============ CONFIG LOADING ============
CONFIG_DIR = os.path.expanduser("~/.d2htools")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config(config_path=CONFIG_FILE):
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        sample_config = {
            "api_url": "https://example.com/api/upload-image",
            "api_token": "your_api_token_here"
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(sample_config, f, indent=4)
        
        print(f"A sample config file was created at {config_path}. Please edit it with your API details.")
        exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ============ FROM SCRIPT 1 ============

def upload_to_custom_api(image_path, api_url, api_token):
    try:
        with open(image_path, "rb") as file:
            files = {"image": file}
            headers = {"Authorization": f"Bearer {api_token}"}

            response = requests.post(api_url, headers=headers, files=files)
            if response.status_code == 200:
                json_data = response.json()
                if "url" in json_data:
                    return json_data["url"]
                else:
                    print(f"Unexpected response: {json_data}")
            else:
                print(f"Upload failed ({response.status_code}): {response.text}")
        return None
    except Exception as e:
        print(f"Error uploading {image_path}: {str(e)}")
        return None

def detect_encoding(file_path):
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    except Exception as e:
        print(f"Error detecting encoding: {str(e)}")
        return 'utf-8'

def process_html_file(html_file_path, api_url, api_token, base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(html_file_path))

    encoding = detect_encoding(html_file_path)
    print(f"Detected encoding: {encoding}")

    with open(html_file_path, "rb") as file:
        raw_html_bytes = file.read()

    try:
        html_content = raw_html_bytes.decode(encoding)
    except UnicodeDecodeError:
        for fallback in ["windows-1252", "utf-8", "iso-8859-1"]:
            try:
                encoding = fallback
                html_content = raw_html_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                pass

    soup = BeautifulSoup(html_content, "html.parser")
    img_tags = soup.find_all("img")

    for img in img_tags:
        src = img.get("src")
        if not src:
            continue

        if src.startswith(("http://", "https://", "data:")):
            pass
        else:
            if os.path.isabs(src):
                image_path = src
            else:
                image_path = os.path.join(base_dir, src)

            if not os.path.exists(image_path):
                print(f"Warning: Image not found at {image_path}")
                continue

            print(f"Uploading: {image_path}")
            uploaded_url = upload_to_custom_api(image_path, api_url, api_token)

            if uploaded_url:
                print(f"Successfully uploaded to: {uploaded_url}")
                img["src"] = uploaded_url
            else:
                print(f"Failed to upload: {image_path}")

        # --- NEW width/height removal + style addition ---
        original_width = img.get("width")
        img.attrs.pop("width", None)
        img.attrs.pop("height", None)

        # Build new style string
        style_parts = ["max-width: 95%", "text-align: center"]
        if original_width:
            try:
                style_parts.append(f"width:{int(original_width)}px")
            except ValueError:
                pass  # if width wasn't numeric, skip it
        style_parts.append("height: auto")

        new_styles = "; ".join(style_parts) + ";"

        # Merge with any existing style
        current_style = img.get("style", "").strip()
        if current_style:
            if not current_style.endswith(";"):
                current_style += ";"
            img["style"] = f"{current_style} {new_styles}"
        else:
            img["style"] = new_styles

    return str(soup), encoding, raw_html_bytes

def save_modified_html(html_file_path, modified_content, original_encoding, raw_html_bytes, suffix="_uploaded"):
    base_name, ext = os.path.splitext(html_file_path)
    new_file_path = f"{base_name}{suffix}{ext}"

    print("\nChoose encoding for saving the file:")
    print(f"1. Use original detected encoding ({original_encoding})")
    print("2. Use UTF-8 (recommended)")
    print("3. Use Windows-1252")
    print("4. Use ISO-8859-1")

    choice = input("Enter your choice (1-4, default is 2): ").strip() or "2"
    encoding_map = {"1": original_encoding, "2": "utf-8", "3": "cp1252", "4": "iso-8859-1"}
    save_encoding = encoding_map.get(choice, "utf-8")

    modified_content = modified_content.replace("õ", "ő").replace("û", "ű")

    try:
        with open(new_file_path, "w", encoding=save_encoding) as file:
            file.write(modified_content)
        print(f"Modified HTML saved to: {new_file_path} with encoding {save_encoding}")
    except UnicodeEncodeError:
        with open(new_file_path, "w", encoding="utf-8", errors="replace") as file:
            file.write(modified_content)
        print(f"Modified HTML saved to: {new_file_path} with utf-8 (with replacements)")

# ============ FROM SCRIPT 2 ============

def modify_margin_left(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    elements_with_style = soup.find_all(lambda tag: tag.has_attr('style'))
    
    for element in elements_with_style:
        style = element['style']
        pattern = r'margin-left\s*:\s*(\d+(?:\.\d+)?)(px|em|rem|%|pt|vh|vw|cm|mm|in|pc|ex|ch)?'
        
        def replace_margin(match):
            value = float(match.group(1))
            unit = match.group(2) or ''
            half_value = value / 2
            if half_value.is_integer():
                half_value = int(half_value)
            return f"margin-left: {half_value}{unit}"
        
        modified_style = re.sub(pattern, replace_margin, style)
        if style != modified_style:
            element['style'] = modified_style
    
    return str(soup)

# ============ NEW FUNCTION FOR TEXT-INDENT ============

def modify_text_indent(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    elements_with_style = soup.find_all(lambda tag: tag.has_attr('style'))
    
    for element in elements_with_style:
        style = element['style']
        pattern = r'text-indent\s*:\s*(-?\d+(?:\.\d+)?)(px|em|rem|%|pt|vh|vw|cm|mm|in|pc|ex|ch)?'
        
        def replace_indent(match):
            value = float(match.group(1))
            unit = match.group(2) or ''
            
            # If negative, multiply by 2 (make it more negative)
            if value < 0:
                new_value = value * 2
                if new_value.is_integer():
                    new_value = int(new_value)
                return f"text-indent: {new_value}{unit}"
            else:
                # If positive, do nothing (return original)
                return match.group(0)
        
        modified_style = re.sub(pattern, replace_indent, style)
        if style != modified_style:
            element['style'] = modified_style
    
    return str(soup)

# ============ COMBINED MAIN ============

def main():
    config = load_config()
    api_url = config.get("api_url")
    api_token = config.get("api_token")

    if not api_url or not api_token:
        raise ValueError("api_url and api_token must be set in config.json")

    if len(sys.argv) < 2:
        print("Usage: python script.py <html_file> [-m] [-i]")
        print("  -m: Halve margin-left values")
        print("  -i: Double negative text-indent values")
        sys.exit(1)

    html_file_path = sys.argv[1]
    margin_flag = "-m" in sys.argv
    indent_flag = "-i" in sys.argv

    modified_content, detected_encoding, raw_html_bytes = process_html_file(html_file_path, api_url, api_token)

    if margin_flag:
        modified_content = modify_margin_left(modified_content)

    if indent_flag:
        modified_content = modify_text_indent(modified_content)

    save_modified_html(html_file_path, modified_content, detected_encoding, raw_html_bytes)

if __name__ == "__main__":
    main()