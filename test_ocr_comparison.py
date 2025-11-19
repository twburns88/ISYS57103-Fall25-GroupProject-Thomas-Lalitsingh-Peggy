#!/usr/bin/env python3
"""
Compare OCR results with and without label detection.
Requires Google Cloud Vision API key.
"""

import sys
import os
from dotenv import load_dotenv
from models.ocr_with_label_detection import compare_ocr_methods

# Load environment variables
load_dotenv()


def main():
    """Main comparison test function."""
    print("=" * 60)
    print("OCR Comparison: With vs Without Label Detection")
    print("=" * 60)
    print()

    # Get API key
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    if not api_key:
        print("Error: GOOGLE_CLOUD_API_KEY not found in environment")
        print("Please set it in your .env file or export it:")
        print("  export GOOGLE_CLOUD_API_KEY='your-key-here'")
        sys.exit(1)

    # Get image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Usage: python test_ocr_comparison.py <image_path>")
        print("\nExample:")
        print("  python test_ocr_comparison.py ui/uploads/yourimage.jpg")
        print("\nTesting with first available image in uploads/...")

        # Find first image in uploads
        uploads_dir = "ui/uploads"
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

        for file in os.listdir(uploads_dir):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                if file != '.gitkeep':
                    image_path = os.path.join(uploads_dir, file)
                    print(f"Using: {image_path}\n")
                    break
        else:
            print("No images found in uploads directory")
            sys.exit(1)

    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)

    # Run comparison
    print(f"Processing: {image_path}")
    print("=" * 60)
    print()

    result_with, result_without = compare_ocr_methods(image_path, api_key, debug=True)

    # Print final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    if result_with['success'] and result_without['success']:
        print("\nBoth methods succeeded!")

        if result_with['label_found']:
            print(f"\nLabel Detection:")
            print(f"  Confidence: {result_with['confidence']:.1%}")
            print(f"  Bounding Box: {result_with['bbox']}")

        chars_with = len(result_with['text'])
        chars_without = len(result_without['text'])

        print(f"\nText Extracted:")
        print(f"  With detection:    {chars_with:4d} characters")
        print(f"  Without detection: {chars_without:4d} characters")

        if chars_without > 0:
            reduction = chars_without - chars_with
            reduction_pct = (reduction / chars_without) * 100
            print(f"  Reduction:         {reduction:4d} characters ({reduction_pct:.1f}%)")

            if reduction > 0:
                print(f"\n✓ Label detection reduced OCR noise by {reduction_pct:.1f}%")
            elif reduction < 0:
                print(f"\n! Label detection resulted in {abs(reduction_pct):.1f}% more text")
            else:
                print("\n≈ No difference in text length")

    else:
        print("\nOne or both methods failed:")
        if not result_with['success']:
            print(f"  With detection: {result_with['error']}")
        if not result_without['success']:
            print(f"  Without detection: {result_without['error']}")


if __name__ == "__main__":
    main()
