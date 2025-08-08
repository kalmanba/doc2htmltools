import os
import re
import requests
from bs4 import BeautifulSoup
import chardet

def upload_to_custom_api(image_path, api_url, api_token):
    """
    Uploads an image to a custom Laravel API and returns the public URL.

    Args:
        image_path (str): Path to the image file
        api_url (str): Laravel API endpoint for uploading
        api_token (str): Bearer token for authentication

    Returns:
        str: Public URL of the uploaded image or None if upload fails
    """
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
            pass  # Keep existing URLs, but still style
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

        # Remove height attribute
        img.attrs.pop("height", None)

        # Keep width if it exists
        current_style = img.get("style", "")
        new_styles = "max-width: 95%; height: auto;"
        if current_style:
            if not current_style.strip().endswith(";"):
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

    # 🔹 Character replacements
    modified_content = modified_content.replace("õ", "ő").replace("û", "ű")

    try:
        with open(new_file_path, "w", encoding=save_encoding) as file:
            file.write(modified_content)
        print(f"Modified HTML saved to: {new_file_path} with encoding {save_encoding}")
    except UnicodeEncodeError:
        with open(new_file_path, "w", encoding="utf-8", errors="replace") as file:
            file.write(modified_content)
        print(f"Modified HTML saved to: {new_file_path} with utf-8 (with replacements)")

def main():
    html_file_path = input("Enter the path to your HTML file: ").strip()
    #api_url = input("Enter your Laravel API upload URL (e.g. https://example.com/api/upload-image): ").strip()
    api_url = "https://learn.honaphire.net/api/upload-image"
    #api_token = input("Enter your Laravel API token: ").strip()
    api_token = "1|7wEVHJ0i6B4l4Yk0Eh8L9hX9MebjrrswXDfLG6Ta7dad5b3b"

    modified_content, detected_encoding, raw_html_bytes = process_html_file(html_file_path, api_url, api_token)
    save_modified_html(html_file_path, modified_content, detected_encoding, raw_html_bytes)

if __name__ == "__main__":
    main()

