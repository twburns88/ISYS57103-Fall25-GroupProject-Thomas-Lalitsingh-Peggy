"""
Training script for YOLO shelf label detector
Trains a YOLOv8 model to detect price labels on retail shelves
"""

import argparse
from pathlib import Path
import yaml
import os


def create_dataset_yaml(data_dir: Path, output_path: Path):
    """
    Create dataset.yaml configuration for YOLO training.

    Args:
        data_dir: Directory containing train/val/test splits
        output_path: Where to save dataset.yaml
    """
    dataset_config = {
        'path': str(data_dir.absolute()),  # Dataset root
        'train': 'images/train',  # Train images (relative to 'path')
        'val': 'images/val',      # Validation images (relative to 'path')
        'test': 'images/test',    # Test images (optional, relative to 'path')
        'names': {
            0: 'shelf_label'  # Class names (can add more classes if needed)
        },
        'nc': 1  # Number of classes
    }

    with open(output_path, 'w') as f:
        yaml.dump(dataset_config, f, default_flow_style=False)

    print(f"Dataset configuration saved to: {output_path}")
    return dataset_config


def train_yolo_model(
    data_yaml: str,
    model_size: str = 'n',
    epochs: int = 100,
    img_size: int = 640,
    batch_size: int = 16,
    device: str = 'cpu',
    project: str = 'runs/detect',
    name: str = 'shelf_label_detector',
    pretrained: bool = True,
    patience: int = 50,
    save_period: int = 10
):
    """
    Train YOLO model for label detection.

    Args:
        data_yaml: Path to dataset YAML configuration
        model_size: YOLO model size: 'n' (nano), 's' (small), 'm' (medium), 'l' (large), 'x' (xlarge)
        epochs: Number of training epochs
        img_size: Input image size
        batch_size: Batch size for training
        device: Device to use ('cpu', 'cuda', 'mps', or device number)
        project: Project directory for saving results
        name: Name of the training run
        pretrained: Whether to use pretrained COCO weights
        patience: Early stopping patience (epochs without improvement)
        save_period: Save checkpoint every N epochs
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Error: ultralytics package not installed.")
        print("Install with: pip install ultralytics")
        return

    # Select model
    model_name = f"yolov8{model_size}.pt" if pretrained else f"yolov8{model_size}.yaml"
    print(f"Initializing model: {model_name}")

    model = YOLO(model_name)

    # Train the model
    print("\n" + "="*60)
    print("Starting YOLO Training")
    print("="*60)
    print(f"Data config: {data_yaml}")
    print(f"Model: YOLOv8{model_size}")
    print(f"Epochs: {epochs}")
    print(f"Image size: {img_size}")
    print(f"Batch size: {batch_size}")
    print(f"Device: {device}")
    print("="*60 + "\n")

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        device=device,
        project=project,
        name=name,
        patience=patience,
        save_period=save_period,
        verbose=True,
        plots=True
    )

    print("\n" + "="*60)
    print("Training completed!")
    print("="*60)

    # Save the best model to models/weights/
    weights_dir = Path(__file__).parent.parent / "models" / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)

    # Copy best weights
    best_weights = Path(project) / name / "weights" / "best.pt"
    if best_weights.exists():
        final_path = weights_dir / "label_detector.pt"
        import shutil
        shutil.copy(best_weights, final_path)
        print(f"\nBest model saved to: {final_path}")
        print(f"Training results saved to: {Path(project) / name}")
    else:
        print(f"\nWarning: Could not find best weights at {best_weights}")

    return results


def validate_dataset_structure(data_dir: Path) -> bool:
    """
    Validate that dataset has the correct structure.

    Expected structure:
        data_dir/
            images/
                train/
                    image1.jpg
                    image2.jpg
                val/
                    image3.jpg
            labels/
                train/
                    image1.txt
                    image2.txt
                val/
                    image3.txt

    Returns:
        True if valid, False otherwise
    """
    required_dirs = [
        data_dir / "images" / "train",
        data_dir / "images" / "val",
        data_dir / "labels" / "train",
        data_dir / "labels" / "val"
    ]

    all_exist = True
    for dir_path in required_dirs:
        if not dir_path.exists():
            print(f"Error: Required directory not found: {dir_path}")
            all_exist = False
        else:
            # Count files
            files = list(dir_path.glob("*"))
            print(f"✓ Found {len(files)} files in {dir_path}")

    return all_exist


def main():
    parser = argparse.ArgumentParser(description="Train YOLO model for shelf label detection")

    parser.add_argument('--data-dir', type=str, required=True,
                       help='Path to dataset directory (contains images/ and labels/)')
    parser.add_argument('--model-size', type=str, default='n',
                       choices=['n', 's', 'm', 'l', 'x'],
                       help='YOLO model size (n=nano, s=small, m=medium, l=large, x=xlarge)')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--img-size', type=int, default=640,
                       help='Input image size')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size for training')
    parser.add_argument('--device', type=str, default='cpu',
                       help='Device to use (cpu, cuda, mps, or device number)')
    parser.add_argument('--no-pretrained', action='store_true',
                       help='Train from scratch (no pretrained weights)')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate dataset structure, do not train')

    args = parser.parse_args()

    data_dir = Path(args.data_dir)

    if not data_dir.exists():
        print(f"Error: Data directory does not exist: {data_dir}")
        return

    print("\nValidating dataset structure...")
    print("="*60)
    if not validate_dataset_structure(data_dir):
        print("\nDataset validation failed!")
        print("Please ensure your dataset follows the YOLO format.")
        print("\nSee: training_data/README.md for instructions")
        return

    print("\n✓ Dataset structure is valid!")

    if args.validate_only:
        print("\nValidation complete. Exiting (--validate-only flag set)")
        return

    # Create dataset YAML
    dataset_yaml = data_dir / "dataset.yaml"
    create_dataset_yaml(data_dir, dataset_yaml)

    # Train model
    train_yolo_model(
        data_yaml=str(dataset_yaml),
        model_size=args.model_size,
        epochs=args.epochs,
        img_size=args.img_size,
        batch_size=args.batch_size,
        device=args.device,
        pretrained=not args.no_pretrained
    )


if __name__ == "__main__":
    main()
