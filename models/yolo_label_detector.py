"""
YOLO-based Shelf Label Detection
Uses YOLOv8 for detecting shelf price labels in retail images
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import os


class YOLOLabelDetector:
    """Detects shelf labels using a trained YOLO model."""

    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        """
        Initialize YOLO label detector.

        Args:
            model_path: Path to trained YOLO model weights (.pt file)
                       If None, uses default path: models/weights/label_detector.pt
            confidence_threshold: Minimum confidence score for detections (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_loaded = False

        # Determine model path
        if model_path is None:
            # Default to models/weights/label_detector.pt
            base_dir = Path(__file__).parent.parent
            model_path = base_dir / "models" / "weights" / "label_detector.pt"

        self.model_path = Path(model_path)

        # Try to load model if it exists
        if self.model_path.exists():
            self._load_model()
        else:
            print(f"Warning: Model not found at {self.model_path}")
            print("You can train a model using train_yolo_detector.py")

    def _load_model(self):
        """Load the YOLO model from disk."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(str(self.model_path))
            self.model_loaded = True
            print(f"YOLO model loaded from {self.model_path}")
        except ImportError:
            print("Error: ultralytics package not installed.")
            print("Install with: pip install ultralytics")
            self.model_loaded = False
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model_loaded = False

    def is_ready(self) -> bool:
        """Check if model is loaded and ready for inference."""
        return self.model_loaded and self.model is not None

    def detect_labels(self, image_path: str, visualize: bool = False) -> List[Dict]:
        """
        Detect shelf labels in an image.

        Args:
            image_path: Path to the image file
            visualize: If True, saves visualization of detections

        Returns:
            List of detected labels, each containing:
                - bbox: (x1, y1, x2, y2) bounding box coordinates
                - confidence: detection confidence score (0-1)
                - class_name: detected class name
                - center: (cx, cy) center coordinates
                - area: pixel area of the detection
        """
        if not self.is_ready():
            raise RuntimeError("YOLO model is not loaded. Cannot perform detection.")

        # Read image to verify it exists
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Run inference
        results = self.model(image_path, conf=self.confidence_threshold, verbose=False)

        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates (xyxy format)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = result.names[class_id]

                # Calculate center and area
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                area = int((x2 - x1) * (y2 - y1))

                detections.append({
                    'bbox': (int(x1), int(y1), int(x2), int(y2)),
                    'confidence': confidence,
                    'class_name': class_name,
                    'center': (center_x, center_y),
                    'area': area
                })

        # Sort by confidence (highest first)
        detections.sort(key=lambda x: x['confidence'], reverse=True)

        # Optionally save visualization
        if visualize and detections:
            self._save_visualization(image_path, detections)

        return detections

    def get_best_label(self, detections: List[Dict], strategy: str = 'most_confident') -> Optional[Dict]:
        """
        Select the best label from detected candidates.

        Args:
            detections: List of detected labels from detect_labels()
            strategy: Selection strategy:
                - 'most_confident': Highest confidence score
                - 'largest': Largest area
                - 'center': Closest to image center

        Returns:
            Best label dict or None if no detections
        """
        if not detections:
            return None

        if strategy == 'most_confident':
            return detections[0]  # Already sorted by confidence
        elif strategy == 'largest':
            return max(detections, key=lambda x: x['area'])
        elif strategy == 'center':
            # Assume image dimensions from first detection center
            # (This is approximate - ideally we'd pass image dimensions)
            avg_x = sum(d['center'][0] for d in detections) / len(detections)
            avg_y = sum(d['center'][1] for d in detections) / len(detections)
            return min(detections, key=lambda x:
                      (x['center'][0] - avg_x)**2 + (x['center'][1] - avg_y)**2)
        else:
            return detections[0]

    def crop_to_label(self, image_path: str, bbox: Tuple[int, int, int, int],
                     output_path: Optional[str] = None, padding: float = 0.05) -> np.ndarray:
        """
        Crop image to label bounding box.

        Args:
            image_path: Path to source image
            bbox: (x1, y1, x2, y2) bounding box coordinates
            output_path: Optional path to save cropped image
            padding: Padding around bbox as fraction of box dimensions (default 5%)

        Returns:
            Cropped image as numpy array
        """
        image = cv2.imread(image_path)
        x1, y1, x2, y2 = bbox

        # Calculate padding
        w = x2 - x1
        h = y2 - y1
        pad_w = int(w * padding)
        pad_h = int(h * padding)

        # Apply padding with bounds checking
        x1 = max(0, x1 - pad_w)
        y1 = max(0, y1 - pad_h)
        x2 = min(image.shape[1], x2 + pad_w)
        y2 = min(image.shape[0], y2 + pad_h)

        # Crop
        cropped = image[y1:y2, x1:x2]

        if output_path:
            cv2.imwrite(output_path, cropped)

        return cropped

    def _save_visualization(self, image_path: str, detections: List[Dict]):
        """Save image with bounding boxes drawn."""
        image = cv2.imread(image_path)

        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_name = det.get('class_name', 'label')

            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(image, (x1, y1 - label_h - 10), (x1 + label_w, y1), (0, 255, 0), -1)
            cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Save visualization
        output_dir = Path("test_results/yolo_detections")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{Path(image_path).stem}_detected.jpg"
        cv2.imwrite(str(output_path), image)
        print(f"Visualization saved to: {output_path}")


# Convenience functions
def detect_labels(image_path: str, model_path: Optional[str] = None,
                 confidence_threshold: float = 0.5) -> List[Dict]:
    """
    Convenience function to detect shelf labels.

    Args:
        image_path: Path to image file
        model_path: Path to YOLO model weights
        confidence_threshold: Minimum confidence score

    Returns:
        List of detected labels
    """
    detector = YOLOLabelDetector(model_path, confidence_threshold)
    return detector.detect_labels(image_path)


def get_label_crop(image_path: str, model_path: Optional[str] = None,
                   strategy: str = 'most_confident', output_path: Optional[str] = None) -> Optional[np.ndarray]:
    """
    Detect and crop to best shelf label.

    Args:
        image_path: Path to image file
        model_path: Path to YOLO model weights
        strategy: Label selection strategy
        output_path: Optional path to save cropped image

    Returns:
        Cropped image array or None if no labels detected
    """
    detector = YOLOLabelDetector(model_path)

    if not detector.is_ready():
        print("Warning: Model not loaded. Cannot detect labels.")
        return None

    detections = detector.detect_labels(image_path)

    if not detections:
        return None

    best_label = detector.get_best_label(detections, strategy=strategy)
    return detector.crop_to_label(image_path, best_label['bbox'], output_path)
