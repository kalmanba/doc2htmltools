#!/usr/bin/env python3

import re
import sys
from bs4 import BeautifulSoup

def modify_margin_left(html_content):
    """
    Process HTML content and halve all margin-left values in style attributes.
    
    Args:
        html_content (str): The HTML content to modify
        
    Returns:
        str: The modified HTML content
    """
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all elements with style attribute
    elements_with_style = soup.find_all(lambda tag: tag.has_attr('style'))
    
    for element in elements_with_style:
        style = element['style']
        
        # Use regex to find margin-left values
        pattern = r'margin-left\s*:\s*(\d+(?:\.\d+)?)(px|em|rem|%|pt|vh|vw|cm|mm|in|pc|ex|ch)?'
        
        def replace_margin(match):
            value = float(match.group(1))
            unit = match.group(2) or ''  # If no unit specified, use empty string
            half_value = value / 2
            
            # Format the new value properly (avoid .0 for whole numbers)
            if half_value.is_integer():
                half_value = int(half_value)
            
            return f"margin-left: {half_value}{unit}"
        
        # Replace margin-left values with half their original value
        modified_style = re.sub(pattern, replace_margin, style)
        
        # Update the style attribute
        if style != modified_style:
            element['style'] = modified_style
    
    # Return the modified HTML as string
    return str(soup)

def process_html_file(input_file, output_file=None):
    """
    Process an HTML file, halving all margin-left values.
    
    Args:
        input_file (str): Path to the input HTML file
        output_file (str, optional): Path to the output HTML file. If not provided,
                                     will print to stdout.
    """
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Modify the content
        modified_content = modify_margin_left(html_content)
        
        # Write to output file or print to stdout
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"Modified HTML saved to {output_file}")
        else:
            print(modified_content)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python margin_modifier.py input.html [output.html]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_html_file(input_file, output_file)

