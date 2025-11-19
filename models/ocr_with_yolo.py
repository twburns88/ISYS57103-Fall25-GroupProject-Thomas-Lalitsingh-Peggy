"""
OCR Processor with YOLO Label Detection
Combines YOLO-based label detection with Google Cloud Vision OCR
"""

import base64
import requests
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict
from models.yolo_label_detector import YOLOLabelDetector


def extract_text_with_yolo(
    image_path: str,
    api_key: str,
    model_path: Optional[str] = None,
    use_detection: bool = True,
    confidence_threshold: float = 0.5,
    strategy: str = 'most_confident',
    save_cropped: bool = False,
    visualize: bool = False
) -> Dict:
    """
    Extract text from image using YOLO label detection + OCR.

    Args:
        image_path: Path to the image file
        api_key: Google Cloud Vision API key
        model_path: Path to YOLO model weights (uses default if None)
        use_detection: If True, detect labels first. If False, use full image
        confidence_threshold: Minimum confidence for YOLO detections (0-1)
        strategy: Label selection strategy ('most_confident', 'largest', 'center')
        save_cropped: If True, save the cropped label region
        visualize: If True, save visualization of YOLO detections

    Returns:
        Dictionary with:
            - success (bool): Whether OCR succeeded
            - text (str): Extracted text
            - error (str): Error message if any
            - detection_used (bool): Whether YOLO detection was used
            - label_found (bool): Whether a label was detected
            - bbox (tuple): Bounding box if label detected (x1, y1, x2, y2)
            - confidence (float): Detection confidence if applicable
            - num_detections (int): Total number of labels detected
    """
    result = {
        'success': False,
        'text': '',
        'error': '',
        'detection_used': use_detection,
        'label_found': False,
        'bbox': None,
        'confidence': None,
        'num_detections': 0
    }

    try:
        # If detection is disabled, use original OCR
        if not use_detection:
            return _extract_text_from_image(image_path, api_key)

        # Initialize YOLO detector
        detector = YOLOLabelDetector(model_path, confidence_threshold)

        # Check if model is ready
        if not detector.is_ready():
            result['error'] = 'YOLO model not loaded. Train a model first or disable detection.'
            result['detection_used'] = False
            # Fallback to full image OCR
            return _extract_text_from_image(image_path, api_key)

        # Step 1: Detect shelf labels
        detections = detector.detect_labels(image_path, visualize=visualize)
        result['num_detections'] = len(detections)

        # Step 2: Select best label or fallback to full image
        if detections:
            best_label = detector.get_best_label(detections, strategy=strategy)
            result['label_found'] = True
            result['bbox'] = best_label['bbox']
            result['confidence'] = best_label['confidence']

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
                    crop_save_path = Path(image_path).stem + '_yolo_crop.jpg'
                    detector.crop_to_label(image_path, best_label['bbox'], crop_save_path)

                # Step 4: Run OCR on cropped region
                ocr_result = _extract_text_from_image(temp_crop_path, api_key)

                # Merge results
                result['success'] = ocr_result['success']
                result['text'] = ocr_result['text']
                result['error'] = ocr_result['error']

            finally:
                # Clean up temporary file
                if temp_crop_path and os.path.exists(temp_crop_path):
                    os.remove(temp_crop_path)

        else:
            # No labels detected - fallback to full image OCR
            result['label_found'] = False
            ocr_result = _extract_text_from_image(image_path, api_key)

            result['success'] = ocr_result['success']
            result['text'] = ocr_result['text']
            result['error'] = ocr_result['error']

        return result

    except Exception as e:
        result['success'] = False
        result['error'] = f'YOLO detection error: {str(e)}'
        return result


def _extract_text_from_image(image_path: str, api_key: str) -> Dict:
    """
    Internal function: Extract text using Google Cloud Vision API.
    """
    result = {
        'success': False,
        'text': '',
        'error': '',
        'detection_used': False,
        'label_found': False,
        'bbox': None,
        'confidence': None,
        'num_detections': 0
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


# Backward compatibility wrapper
def extract_text_from_image(image_path: str, api_key: str, model_path: Optional[str] = None) -> Dict:
    """
    Simple function for backward compatibility.
    Uses YOLO detection if model is available, otherwise uses full image.
    """
    result = extract_text_with_yolo(
        image_path, api_key, model_path=model_path, use_detection=True
    )

    # Return simplified format for compatibility
    return {
        'success': result['success'],
        'text': result['text'],
        'error': result['error']
    }
