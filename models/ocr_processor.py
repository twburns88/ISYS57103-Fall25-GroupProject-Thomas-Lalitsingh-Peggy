
import base64
import requests
import sys
import os
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
        # Read and encode image to base64
        with open(image_path, 'rb') as image_file:
            image_content = image_file.read()
        
        base64_image = base64.b64encode(image_content).decode('utf-8')
        
        # Prepare API request
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
        
        # Send request to Google Cloud Vision API
        response = requests.post(url, json=payload)
        result = response.json()
        
        # Parse response
        if response.status_code != 200:
            return {
                'success': False,
                'text': '',
                'error': f'API request failed with status code {response.status_code}'
            }
        
        if 'responses' in result and result['responses']:
            response_data = result['responses'][0]
            
            # Check for errors
            if 'error' in response_data:
                return {
                    'success': False,
                    'text': '',
                    'error': response_data['error'].get('message', 'Unknown API error')
                }
            
            # Extract text
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
    print("Google Cloud Vision OCR - Text Extraction")
    print("=" * 60)
    print()
    
    # Get API key from environment variable or command line
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    
    if not api_key:
        print("Please enter your Google Cloud Vision API key:")
        api_key = input("> ").strip()
        
        if not api_key:
            print("Error: API key is required")
            print("\nSetup instructions:")
            print("1. Go to https://console.cloud.google.com")
            print("2. Create a new project or select existing one")
            print("3. Enable Cloud Vision API")
            print("4. Go to 'Credentials' and create an API key")
            print("5. Set environment variable: export GOOGLE_CLOUD_API_KEY='your-key'")
            sys.exit(1)
    
    # Get image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Enter the path to your image:")
        image_path = input("> ").strip()
    
    if not image_path:
        print("Error: Image path is required")
        sys.exit(1)
    
    # Check if file exists
    if not Path(image_path).exists():
        print(f"Error: Image file '{image_path}' not found")
        sys.exit(1)
    
    print(f"\nProcessing: {image_path}")
    print("Please wait...")
    print()
    
    # Extract text from image
    result = extract_text_from_image(image_path, api_key)
    
    if result['success']:
        if result['text']:
            print("=" * 60)
            print("EXTRACTED TEXT:")
            print("=" * 60)
            print(result['text'])
            print("=" * 60)
            print()
            
            # Save to file
            output_filename = Path(image_path).stem + '_extracted_text.txt'
            if save_text_to_file(result['text'], output_filename):
                print(f"Text saved to: {output_filename}")
            
            # Show character count
            print(f"Total characters: {len(result['text'])}")
            print(f"Total lines: {len(result['text'].splitlines())}")
        else:
            print(f"Warning: {result['error']}")
    else:
        print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()