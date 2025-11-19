"""
OCR Processor with Shelf Label Detection
Combines OpenCV label detection with Google Cloud Vision OCR
"""

import base64
import requests
import cv2
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Tuple
from models.label_detector import LabelDetector


def extract_text_with_label_detection(
    image_path: str,
    api_key: str,
    use_detection: bool = True,
    strategy: str = 'most_confident',
    save_cropped: bool = False,
    debug: bool = False
) -> Dict:
    """
    Extract text from image using label detection + OCR.

    Args:
        image_path: Path to the image file
        api_key: Google Cloud Vision API key
        use_detection: If True, detect labels first. If False, use full image
        strategy: Label selection strategy ('most_confident', 'largest', 'center')
        save_cropped: If True, save the cropped label region
        debug: Enable debug output

    Returns:
        Dictionary with:
            - success (bool): Whether OCR succeeded
            - text (str): Extracted text
            - error (str): Error message if any
            - detection_used (bool): Whether label detection was used
            - label_found (bool): Whether a label was detected
            - bbox (tuple): Bounding box if label detected (x, y, w, h)
            - confidence (float): Detection confidence if applicable
    """
    result = {
        'success': False,
        'text': '',
        'error': '',
        'detection_used': use_detection,
        'label_found': False,
        'bbox': None,
        'confidence': None
    }

    try:
        # If detection is disabled, use original OCR
        if not use_detection:
            return _extract_text_from_image(image_path, api_key)

        # Step 1: Detect shelf labels
        detector = LabelDetector()
        labels = detector.detect_shelf_labels(image_path, debug=debug)

        if debug:
            print(f"[DEBUG] Found {len(labels)} label candidates")

        # Step 2: Select best label or fallback to full image
        if labels:
            best_label = detector.get_best_label(labels, strategy=strategy)
            result['label_found'] = True
            result['bbox'] = best_label['bbox']
            result['confidence'] = best_label['confidence']

            if debug:
                print(f"[DEBUG] Selected label: bbox={best_label['bbox']}, confidence={best_label['confidence']:.3f}")

            # Step 3: Crop to label region
            temp_crop_path = None
            try:
                # Create temporary file for cropped image
                temp_dir = os.path.dirname(image_path)
                temp_fd, temp_crop_path = tempfile.mkstemp(suffix='.jpg', dir=temp_dir)
                os.close(temp_fd)  # Close file descriptor

                # Crop and save
                detector.crop_to_label(image_path, best_label['bbox'], temp_crop_path)

                # Optionally save cropped image permanently
                if save_cropped:
                    crop_save_path = Path(image_path).stem + '_label_crop.jpg'
                    detector.crop_to_label(image_path, best_label['bbox'], crop_save_path)
                    if debug:
                        print(f"[DEBUG] Saved cropped label to: {crop_save_path}")

                # Step 4: Run OCR on cropped region
                ocr_result = _extract_text_from_image(temp_crop_path, api_key)

                # Merge results
                result['success'] = ocr_result['success']
                result['text'] = ocr_result['text']
                result['error'] = ocr_result['error']

                if debug:
                    print(f"[DEBUG] OCR on cropped region: {len(result['text'])} characters extracted")

            finally:
                # Clean up temporary file
                if temp_crop_path and os.path.exists(temp_crop_path):
                    os.remove(temp_crop_path)

        else:
            # No labels detected - fallback to full image OCR
            if debug:
                print(f"[DEBUG] No labels detected, using full image OCR")

            result['label_found'] = False
            ocr_result = _extract_text_from_image(image_path, api_key)

            result['success'] = ocr_result['success']
            result['text'] = ocr_result['text']
            result['error'] = ocr_result['error']

        return result

    except Exception as e:
        result['success'] = False
        result['error'] = f'Label detection error: {str(e)}'
        return result


def _extract_text_from_image(image_path: str, api_key: str) -> Dict:
    """
    Internal function: Extract text using Google Cloud Vision API.
    Same as ocr_processor.py but returns additional metadata.
    """
    result = {
        'success': False,
        'text': '',
        'error': '',
        'detection_used': False,
        'label_found': False,
        'bbox': None,
        'confidence': None
    }

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
        api_result = response.json()

        # Parse response
        if response.status_code != 200:
            result['error'] = f'API request failed with status code {response.status_code}'
            return result

        if 'responses' in api_result and api_result['responses']:
            response_data = api_result['responses'][0]

            # Check for errors
            if 'error' in response_data:
                result['error'] = response_data['error'].get('message', 'Unknown API error')
                return result

            # Extract text
            text_annotations = response_data.get('textAnnotations', [])
            if text_annotations:
                result['success'] = True
                result['text'] = text_annotations[0]['description']
            else:
                result['success'] = True
                result['text'] = ''
                result['error'] = 'No text detected in image'
        else:
            result['error'] = 'Invalid API response'

        return result

    except FileNotFoundError:
        result['error'] = f'Image file not found: {image_path}'
        return result
    except Exception as e:
        result['error'] = f'OCR error: {str(e)}'
        return result


def compare_ocr_methods(image_path: str, api_key: str, debug: bool = True) -> Tuple[Dict, Dict]:
    """
    Compare OCR results with and without label detection.

    Args:
        image_path: Path to image file
        api_key: Google Cloud Vision API key
        debug: Enable debug output

    Returns:
        Tuple of (result_with_detection, result_without_detection)
    """
    print("Testing WITH label detection:")
    print("-" * 60)
    result_with = extract_text_with_label_detection(
        image_path, api_key, use_detection=True, debug=debug
    )

    print("\n" + "=" * 60)
    print("Testing WITHOUT label detection (full image):")
    print("-" * 60)
    result_without = extract_text_with_label_detection(
        image_path, api_key, use_detection=False, debug=debug
    )

    # Print comparison
    print("\n" + "=" * 60)
    print("COMPARISON:")
    print("=" * 60)

    if result_with['label_found']:
        print(f"Label detected: Yes (confidence: {result_with['confidence']:.3f})")
        print(f"Bounding box: {result_with['bbox']}")
    else:
        print("Label detected: No")

    print(f"\nText extracted (WITH detection): {len(result_with['text'])} characters")
    print(f"Text extracted (WITHOUT detection): {len(result_without['text'])} characters")

    if result_with['success'] and result_without['success']:
        # Calculate reduction in text
        reduction = len(result_without['text']) - len(result_with['text'])
        reduction_pct = (reduction / len(result_without['text']) * 100) if result_without['text'] else 0

        print(f"\nText reduction: {reduction} characters ({reduction_pct:.1f}%)")

        print("\n--- WITH DETECTION ---")
        print(result_with['text'][:500])  # First 500 chars

        print("\n--- WITHOUT DETECTION ---")
        print(result_without['text'][:500])  # First 500 chars

    return result_with, result_without


# For backward compatibility: simple function signature
def extract_text_from_image(image_path: str, api_key: str) -> Dict:
    """
    Simple function for backward compatibility.
    Uses label detection by default.
    """
    result = extract_text_with_label_detection(
        image_path, api_key, use_detection=True
    )

    # Return simplified format matching original ocr_processor.py
    return {
        'success': result['success'],
        'text': result['text'],
        'error': result['error']
    }
