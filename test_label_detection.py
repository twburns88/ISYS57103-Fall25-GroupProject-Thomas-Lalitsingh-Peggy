#!/usr/bin/env python3
"""
Test script for shelf label detection.
Processes images and visualizes detected labels.
"""

import cv2
import os
import sys
import time
from pathlib import Path
from models.label_detector import LabelDetector


def draw_labels_on_image(image_path: str, labels: list, output_path: str):
    """Draw bounding boxes on image for detected labels."""
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    for i, label in enumerate(labels):
        x, y, w, h = label['bbox']
        confidence = label['confidence']

        # Color code by confidence: green (high) to yellow (medium) to red (low)
        if confidence > 0.7:
            color = (0, 255, 0)  # Green
        elif confidence > 0.5:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 165, 255)  # Orange

        # Draw rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 3)

        # Draw label with confidence and rank
        label_text = f"#{i+1} ({confidence:.2f})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2

        # Background for text
        (text_w, text_h), _ = cv2.getTextSize(label_text, font, font_scale, thickness)
        cv2.rectangle(image, (x, y - text_h - 10), (x + text_w + 10, y), color, -1)

        # Text
        cv2.putText(image, label_text, (x + 5, y - 5), font, font_scale, (0, 0, 0), thickness)

    cv2.imwrite(output_path, image)
    print(f"  Saved annotated image: {output_path}")


def test_single_image(image_path: str, detector: LabelDetector, output_dir: str):
    """Test label detection on a single image."""
    print(f"\n{'='*60}")
    print(f"Testing: {image_path}")
    print(f"{'='*60}")

    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return

    # Detect labels
    start_time = time.time()
    labels = detector.detect_shelf_labels(image_path, debug=False)
    elapsed_time = time.time() - start_time

    # Print results
    print(f"\nDetection Results:")
    print(f"  Processing time: {elapsed_time:.3f} seconds")
    print(f"  Labels detected: {len(labels)}")

    if labels:
        print(f"\n  Detected Labels (sorted by confidence):")
        for i, label in enumerate(labels):
            x, y, w, h = label['bbox']
            conf = label['confidence']
            area = label['area']
            cx, cy = label['center']
            aspect = label['aspect_ratio']

            print(f"    #{i+1}:")
            print(f"      Confidence: {conf:.3f}")
            print(f"      Bbox: x={x}, y={y}, w={w}, h={h}")
            print(f"      Area: {area} pixels")
            print(f"      Center: ({cx}, {cy})")
            print(f"      Aspect Ratio: {aspect:.2f}")

        # Save annotated image
        filename = Path(image_path).stem
        output_path = os.path.join(output_dir, f"{filename}_annotated.jpg")
        draw_labels_on_image(image_path, labels, output_path)

        # Save cropped best label
        best_label = detector.get_best_label(labels, strategy='most_confident')
        if best_label:
            crop_path = os.path.join(output_dir, f"{filename}_cropped_best.jpg")
            detector.crop_to_label(image_path, best_label['bbox'], crop_path)
            print(f"  Saved best label crop: {crop_path}")

    else:
        print("  No labels detected!")


def test_directory(input_dir: str, output_dir: str):
    """Test label detection on all images in a directory."""
    detector = LabelDetector()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif'}

    # Find all images
    image_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                image_files.append(os.path.join(root, file))

    if not image_files:
        print(f"No images found in {input_dir}")
        return

    print(f"Found {len(image_files)} images to process")

    # Statistics
    total_labels = 0
    images_with_labels = 0
    total_time = 0

    # Process each image
    for image_path in image_files:
        test_single_image(image_path, detector, output_dir)

        # Update statistics
        labels = detector.detect_shelf_labels(image_path)
        if labels:
            images_with_labels += 1
            total_labels += len(labels)

    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total images processed: {len(image_files)}")
    print(f"Images with labels detected: {images_with_labels} ({images_with_labels/len(image_files)*100:.1f}%)")
    print(f"Total labels detected: {total_labels}")
    print(f"Average labels per image: {total_labels/len(image_files):.2f}")
    print(f"\nResults saved to: {output_dir}")


def main():
    """Main test function."""
    print("=" * 60)
    print("Shelf Label Detection Test")
    print("=" * 60)

    # Default paths
    default_input = "ui/uploads"
    default_output = "test_results"

    # Check command line arguments
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = default_input

    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = default_output

    # Test if input is file or directory
    if os.path.isfile(input_path):
        # Single file test
        os.makedirs(output_dir, exist_ok=True)
        detector = LabelDetector()
        test_single_image(input_path, detector, output_dir)
    elif os.path.isdir(input_path):
        # Directory test
        test_directory(input_path, output_dir)
    else:
        print(f"\nUsage: python test_label_detection.py [image_or_directory] [output_directory]")
        print(f"\nExamples:")
        print(f"  python test_label_detection.py                          # Test all images in ui/uploads/")
        print(f"  python test_label_detection.py my_image.jpg             # Test single image")
        print(f"  python test_label_detection.py test_images/             # Test directory")
        print(f"  python test_label_detection.py image.jpg results/       # Custom output dir")
        print(f"\nError: Path not found: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
