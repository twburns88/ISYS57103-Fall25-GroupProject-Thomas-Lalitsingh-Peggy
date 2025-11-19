# YOLO Label Detection Training Data

This directory contains training data for the YOLO shelf label detector model.

## Directory Structure

```
training_data/
├── images/
│   ├── train/          # Training images
│   ├── val/            # Validation images
│   └── test/           # Test images (optional)
├── labels/
│   ├── train/          # Training labels (YOLO format)
│   ├── val/            # Validation labels (YOLO format)
│   └── test/           # Test labels (optional)
└── dataset.yaml        # Auto-generated during training
```

## Data Requirements

- **Minimum recommended**: 100+ labeled images
- **Image format**: JPG, PNG
- **Label format**: YOLO format (one .txt file per image)
- **Train/Val split**: Typically 80/20 or 70/30

## YOLO Label Format

Each image needs a corresponding `.txt` file with the same name in the `labels/` directory.

**Format**: `<class_id> <x_center> <y_center> <width> <height>`

- All values are normalized (0-1) relative to image dimensions
- `class_id`: 0 for "shelf_label"
- `x_center`, `y_center`: Center of bounding box
- `width`, `height`: Box dimensions

**Example** (`labels/train/shelf_001.txt`):
```
0 0.5 0.75 0.4 0.08
```

This represents a shelf label:
- Class 0 (shelf_label)
- Centered horizontally at 50% of image width
- Centered vertically at 75% of image height
- 40% of image width
- 8% of image height

## Annotation Tools

### Recommended: Label Studio

[Label Studio](https://labelstud.io/) is a free, open-source annotation tool with YOLO export.

**Installation**:
```bash
pip install label-studio
```

**Usage**:
```bash
label-studio start
```

Then:
1. Create a new project
2. Import your images
3. Configure labeling interface for object detection
4. Add label: "shelf_label"
5. Annotate images by drawing bounding boxes
6. Export in YOLO format

### Alternative: Roboflow

[Roboflow](https://roboflow.com/) offers free tier with:
- Web-based annotation
- Automatic train/val/test split
- Data augmentation
- Direct YOLO export

### Alternative: LabelImg

[LabelImg](https://github.com/HumanSignal/labelImg) is a simple desktop tool.

**Installation**:
```bash
pip install labelImg
```

**Usage**:
```bash
labelImg
```

**Note**: LabelImg exports in Pascal VOC format by default. You'll need to convert to YOLO format or switch the save format in preferences.

## Collecting Training Images

### Tips for Good Training Data:

1. **Variety is key**:
   - Different shelf types
   - Different lighting conditions
   - Different label sizes and orientations
   - Various products and arrangements

2. **Quality matters**:
   - Clear, focused images
   - Full label visible
   - Realistic retail shelf angles

3. **Consistency**:
   - Similar image resolution (e.g., all 640x640 or 1280x720)
   - Consistent labeling criteria

### Example Workflow:

1. Take photos of retail shelves with your phone
2. Transfer images to `training_data/images/train/`
3. Use Label Studio to annotate:
   - Draw bounding boxes around shelf price labels
   - Export labels to `training_data/labels/train/`
4. Manually move 20-30% of images/labels to `val/` directories
5. Verify structure: `python models/train_yolo_detector.py --data-dir training_data --validate-only`
6. Train: `python models/train_yolo_detector.py --data-dir training_data --epochs 100`

## Training the Model

Once you have 100+ annotated images:

```bash
# Validate dataset structure
python models/train_yolo_detector.py --data-dir training_data --validate-only

# Train with default settings (YOLOv8 nano, 100 epochs)
python models/train_yolo_detector.py --data-dir training_data

# Train with custom settings
python models/train_yolo_detector.py \
    --data-dir training_data \
    --model-size s \
    --epochs 200 \
    --batch-size 16 \
    --device cuda  # or 'mps' for Apple Silicon
```

### Model Sizes:

- **n (nano)**: Fastest, smallest, good for CPU/mobile
- **s (small)**: Good balance of speed/accuracy
- **m (medium)**: More accurate, slower
- **l (large)**: High accuracy, requires GPU
- **x (xlarge)**: Best accuracy, slow, requires powerful GPU

For this use case, **nano** or **small** is recommended.

## Using the Trained Model

After training, the best model is automatically saved to `models/weights/label_detector.pt`.

Test it:
```python
from models.yolo_label_detector import YOLOLabelDetector

detector = YOLOLabelDetector()  # Loads models/weights/label_detector.pt
labels = detector.detect_labels('path/to/shelf/image.jpg', visualize=True)

for label in labels:
    print(f"Detected label at {label['bbox']} with confidence {label['confidence']:.2f}")
```

## Troubleshooting

**"No module named 'ultralytics'"**
```bash
pip install ultralytics
```

**"Model not found"**
- Make sure you've trained a model first
- Check that `models/weights/label_detector.pt` exists

**Poor detection performance**
- Need more training data (aim for 200+ images)
- More variety in training data
- Train for more epochs
- Try a larger model size

**Training is too slow**
- Use a smaller model (nano)
- Reduce batch size
- Use GPU if available (`--device cuda` or `--device mps`)

## Next Steps

1. Collect and annotate 100+ shelf images
2. Validate dataset structure
3. Train initial model
4. Test on new images
5. Identify failure cases
6. Add more training data for those cases
7. Retrain and iterate
