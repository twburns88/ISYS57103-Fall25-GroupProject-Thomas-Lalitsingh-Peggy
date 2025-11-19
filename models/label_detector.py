"""
Shelf Label Detection using OpenCV
Detects rectangular shelf price tags/labels in retail shelf images.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import os


class LabelDetector:
    """Detects shelf labels in retail images using computer vision techniques."""

    def __init__(self,
                 min_aspect_ratio: float = 2.5,
                 max_aspect_ratio: float = 10.0,
                 min_width: int = 100,
                 min_height: int = 20,
                 max_width_ratio: float = 0.9,
                 bottom_region_ratio: float = 0.6,
                 confidence_threshold: float = 0.5):
        """
        Initialize label detector with configurable parameters.

        Args:
            min_aspect_ratio: Minimum width/height ratio for labels (default 2.5)
            max_aspect_ratio: Maximum width/height ratio for labels (default 10.0)
            min_width: Minimum label width in pixels (default 100)
            min_height: Minimum label height in pixels (default 20)
            max_width_ratio: Maximum label width as ratio of image width (default 0.9)
            bottom_region_ratio: Focus on bottom portion of image (default 0.6)
            confidence_threshold: Minimum confidence score (default 0.5)
        """
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio
        self.min_width = min_width
        self.min_height = min_height
        self.max_width_ratio = max_width_ratio
        self.bottom_region_ratio = bottom_region_ratio
        self.confidence_threshold = confidence_threshold

    def detect_shelf_labels(self, image_path: str, debug: bool = False) -> List[dict]:
        """
        Detect shelf labels in an image.

        Args:
            image_path: Path to the image file
            debug: If True, saves intermediate processing steps

        Returns:
            List of detected labels, each containing:
                - bbox: (x, y, w, h) bounding box
                - confidence: detection confidence score (0-1)
                - area: pixel area of the label
                - center: (cx, cy) center coordinates
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        height, width = image.shape[:2]

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge detection using Canny
        edges = cv2.Canny(blurred, 50, 150)

        # Dilate edges to connect broken lines
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)

        if debug:
            self._save_debug_image(edges, "01_edges.jpg")
            self._save_debug_image(dilated, "02_dilated.jpg")

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter and score label candidates
        label_candidates = []

        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)

            # Calculate features
            aspect_ratio = w / h if h > 0 else 0
            area = w * h
            center_x = x + w // 2
            center_y = y + h // 2

            # Apply filters
            if not self._is_valid_label(x, y, w, h, aspect_ratio, width, height):
                continue

            # Calculate confidence score based on multiple factors
            confidence = self._calculate_confidence(
                image, gray, x, y, w, h, aspect_ratio, width, height
            )

            if confidence < self.confidence_threshold:
                continue

            label_candidates.append({
                'bbox': (x, y, w, h),
                'confidence': confidence,
                'area': area,
                'center': (center_x, center_y),
                'aspect_ratio': aspect_ratio
            })

        # Sort by confidence (highest first)
        label_candidates.sort(key=lambda x: x['confidence'], reverse=True)

        return label_candidates

    def _is_valid_label(self, x: int, y: int, w: int, h: int,
                        aspect_ratio: float, img_width: int, img_height: int) -> bool:
        """Check if bounding box matches shelf label characteristics."""

        # Size filters
        if w < self.min_width or h < self.min_height:
            return False

        # Aspect ratio filter (labels are wide rectangles)
        if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
            return False

        # Not too wide (shouldn't span entire image)
        if w > img_width * self.max_width_ratio:
            return False

        # Position filter: prefer labels in bottom portion of image
        # (shelf labels are typically at bottom of shelf)
        label_top = y
        bottom_region_start = img_height * (1 - self.bottom_region_ratio)

        # More lenient - just not in top 20% of image
        if label_top < img_height * 0.2:
            return False

        return True

    def _calculate_confidence(self, image: np.ndarray, gray: np.ndarray,
                             x: int, y: int, w: int, h: int,
                             aspect_ratio: float, img_width: int, img_height: int) -> float:
        """Calculate confidence score for label detection."""

        confidence = 0.0

        # Extract region of interest
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = image[y:y+h, x:x+w]

        # Factor 1: Aspect ratio (prefer 3:1 to 7:1)
        ideal_ratio = 5.0
        ratio_score = 1.0 - min(abs(aspect_ratio - ideal_ratio) / ideal_ratio, 1.0)
        confidence += ratio_score * 0.3

        # Factor 2: Brightness (labels are often white/light colored)
        mean_brightness = np.mean(roi_gray)
        brightness_score = min(mean_brightness / 200.0, 1.0)
        confidence += brightness_score * 0.2

        # Factor 3: Edge density (labels have text, so moderate edges)
        edges_roi = cv2.Canny(roi_gray, 50, 150)
        edge_density = np.sum(edges_roi > 0) / (w * h)
        # Prefer moderate edge density (0.05 - 0.3)
        edge_score = 1.0 - abs(edge_density - 0.15) / 0.15
        edge_score = max(0, min(edge_score, 1.0))
        confidence += edge_score * 0.2

        # Factor 4: Position (prefer middle-bottom of image)
        center_y = y + h // 2
        vertical_position = center_y / img_height
        # Prefer 0.5 to 0.9 vertical position
        if 0.5 <= vertical_position <= 0.9:
            position_score = 1.0
        else:
            position_score = 0.5
        confidence += position_score * 0.15

        # Factor 5: Horizontal positioning (prefer not at extreme edges)
        center_x = x + w // 2
        horizontal_position = center_x / img_width
        if 0.1 <= horizontal_position <= 0.9:
            h_position_score = 1.0
        else:
            h_position_score = 0.5
        confidence += h_position_score * 0.15

        return min(confidence, 1.0)

    def _save_debug_image(self, image: np.ndarray, filename: str):
        """Save debug image to test_results directory."""
        debug_dir = "test_results/debug"
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, filename), image)

    def crop_to_label(self, image_path: str, bbox: Tuple[int, int, int, int],
                     output_path: Optional[str] = None) -> np.ndarray:
        """
        Crop image to label bounding box.

        Args:
            image_path: Path to source image
            bbox: (x, y, w, h) bounding box
            output_path: Optional path to save cropped image

        Returns:
            Cropped image as numpy array
        """
        image = cv2.imread(image_path)
        x, y, w, h = bbox

        # Add small padding (5%)
        padding_w = int(w * 0.05)
        padding_h = int(h * 0.05)

        x = max(0, x - padding_w)
        y = max(0, y - padding_h)
        w = min(image.shape[1] - x, w + 2 * padding_w)
        h = min(image.shape[0] - y, h + 2 * padding_h)

        cropped = image[y:y+h, x:x+w]

        if output_path:
            cv2.imwrite(output_path, cropped)

        return cropped

    def get_best_label(self, labels: List[dict], strategy: str = 'largest') -> Optional[dict]:
        """
        Select the best label from detected candidates.

        Args:
            labels: List of detected labels
            strategy: Selection strategy ('largest', 'most_confident', 'center')

        Returns:
            Best label dict or None if no labels
        """
        if not labels:
            return None

        if strategy == 'largest':
            return max(labels, key=lambda x: x['area'])
        elif strategy == 'most_confident':
            return labels[0]  # Already sorted by confidence
        elif strategy == 'center':
            # Get label closest to center of image
            img_center_x = labels[0]['center'][0]  # Approximate
            return min(labels, key=lambda x: abs(x['center'][0] - img_center_x))
        else:
            return labels[0]


def detect_labels(image_path: str, debug: bool = False) -> List[dict]:
    """
    Convenience function to detect shelf labels.

    Args:
        image_path: Path to image file
        debug: Enable debug output

    Returns:
        List of detected labels
    """
    detector = LabelDetector()
    return detector.detect_shelf_labels(image_path, debug=debug)


def get_label_crop(image_path: str, output_path: Optional[str] = None,
                   strategy: str = 'largest') -> Optional[np.ndarray]:
    """
    Detect and crop to best shelf label.

    Args:
        image_path: Path to image file
        output_path: Optional path to save cropped image
        strategy: Label selection strategy

    Returns:
        Cropped image array or None if no labels detected
    """
    detector = LabelDetector()
    labels = detector.detect_shelf_labels(image_path)

    if not labels:
        return None

    best_label = detector.get_best_label(labels, strategy=strategy)
    return detector.crop_to_label(image_path, best_label['bbox'], output_path)
