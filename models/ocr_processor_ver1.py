"""
Google Cloud Vision OCR - Item Description Extractor
Extracts only product descriptions from price labels, filtering out prices, barcodes, etc.
"""

import base64
import requests
import sys
import os
import re
from pathlib import Path


def extract_text_from_image(image_path, api_key):
    """
    Extract text from an image using Google Cloud Vision API
    
    Args:
        image_path: Path to the image file (jpg, png, gif, etc.)
        api_key: Your Google Cloud Vision API key
    
    Returns:
        Dictionary with 'success' (bool), 'text' (str), and 'error' (str) keys
    """
    try:
        with open(image_path, 'rb') as image_file:
            image_content = image_file.read()
        
        base64_image = base64.b64encode(image_content).decode('utf-8')
        
        url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
        
        payload = {
            'requests': [{
                'image': {
                    'content': base64_image
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': 1
                }]
            }]
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if response.status_code != 200:
            return {
                'success': False,
                'text': '',
                'error': f'API request failed with status code {response.status_code}'
            }
        
        if 'responses' in result and result['responses']:
            response_data = result['responses'][0]
            
            if 'error' in response_data:
                return {
                    'success': False,
                    'text': '',
                    'error': response_data['error'].get('message', 'Unknown API error')
                }
            
            text_annotations = response_data.get('textAnnotations', [])
            if text_annotations:
                extracted_text = text_annotations[0]['description']
                return {
                    'success': True,
                    'text': extracted_text,
                    'error': ''
                }
            else:
                return {
                    'success': True,
                    'text': '',
                    'error': 'No text detected in image'
                }
        else:
            return {
                'success': False,
                'text': '',
                'error': 'Invalid API response'
            }
            
    except FileNotFoundError:
        return {
            'success': False,
            'text': '',
            'error': f'Image file not found: {image_path}'
        }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'error': f'Error: {str(e)}'
        }


def filter_item_description(full_text):
    """
    Extract only the item/product description from OCR text
    Filters out prices, barcodes, store info, etc.
    
    Args:
        full_text: Complete OCR text from image
    
    Returns:
        Dictionary with filtered results
    """
    lines = full_text.split('\n')
    
    exclude_patterns = [
        r'\$\d+\.?\d*',
        r'ROLLBACK',
        r'CLEARANCE',
        r'SALE',
        r'WAS\s+\$',
        r'UNIT PRICE',
        r'PER\s+(OZ|LB|EA|CT)',
        r'UPC\s+\d+',
        r'FAC\s+\d+',
        r'CAP\s+\d+',
        r'\d{12,}',
        r'^\d+$',
        r'PRICE',
        r'TOTAL',
        r'SUBTOTAL',
        r'TAX',
        r'^\s*$',
        r'WALMART|TARGET|KROGER',
    ]
    
    combined_exclude = '|'.join(exclude_patterns)
    exclude_regex = re.compile(combined_exclude, re.IGNORECASE)
    
    filtered_lines = []
    for line in lines:
        line = line.strip()
        
        if exclude_regex.search(line):
            continue
        
        if len(line) < 3:
            continue
        
        if sum(c.isdigit() for c in line) / len(line) > 0.5:
            continue
        
        filtered_lines.append(line)
    
    item_description = None
    if filtered_lines:
        for line in filtered_lines:
            if len(line) >= 5:
                item_description = line
                break
    
    return {
        'item_description': item_description,
        'all_filtered_lines': filtered_lines,
        'original_text': full_text
    }


def extract_item_description_from_image(image_path, api_key):
    """
    Complete workflow: Extract text from image and filter for item description only
    
    Args:
        image_path: Path to the image file
        api_key: Google Cloud Vision API key
    
    Returns:
        Dictionary with item description and metadata
    """
    ocr_result = extract_text_from_image(image_path, api_key)
    
    if not ocr_result['success']:
        return {
            'success': False,
            'item_description': None,
            'error': ocr_result['error']
        }
    
    if not ocr_result['text']:
        return {
            'success': False,
            'item_description': None,
            'error': 'No text detected in image'
        }
    
    filtered_result = filter_item_description(ocr_result['text'])
    
    if not filtered_result['item_description']:
        return {
            'success': False,
            'item_description': None,
            'error': 'Could not identify item description',
            'full_text': ocr_result['text']
        }
    
    return {
        'success': True,
        'item_description': filtered_result['item_description'],
        'all_filtered_lines': filtered_result['all_filtered_lines'],
        'full_ocr_text': ocr_result['text']
    }


def save_text_to_file(text, output_path):
    """Save extracted text to a file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


def main():
    """Main function for command line usage"""
    
    print("=" * 60)
    print("Item Description Extractor - Google Cloud Vision OCR")
    print("=" * 60)
    print()
    
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    
    if not api_key:
        print("Please enter your Google Cloud Vision API key:")
        api_key = input("> ").strip()
        
        if not api_key:
            print("Error: API key is required")
            sys.exit(1)
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Enter the path to your image:")
        image_path = input("> ").strip()
    
    if not image_path:
        print("Error: Image path is required")
        sys.exit(1)
    
    if not Path(image_path).exists():
        print(f"Error: Image file '{image_path}' not found")
        sys.exit(1)
    
    print(f"\nProcessing: {image_path}")
    print("Please wait...")
    print()
    
    result = extract_item_description_from_image(image_path, api_key)
    
    if result['success']:
        print("=" * 60)
        print("ITEM DESCRIPTION FOUND:")
        print("=" * 60)
        print(f"\n{result['item_description']}\n")
        print("=" * 60)
        print()
        
        if len(result.get('all_filtered_lines', [])) > 1:
            print("Other filtered text lines:")
            for i, line in enumerate(result['all_filtered_lines'][1:], 1):
                print(f"  {i}. {line}")
            print()
        
        output_filename = Path(image_path).stem + '_item_description.txt'
        if save_text_to_file(result['item_description'], output_filename):
            print(f"Item description saved to: {output_filename}")
        
        full_output_filename = Path(image_path).stem + '_full_ocr.txt'
        if save_text_to_file(result['full_ocr_text'], full_output_filename):
            print(f"Full OCR text saved to: {full_output_filename}")
        
    else:
        print(f"Error: {result['error']}")
        if 'full_text' in result:
            print("\nFull extracted text:")
            print("-" * 60)
            print(result['full_text'])
            print("-" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()