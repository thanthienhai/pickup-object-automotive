## Why

Need to test YOLO11n object detection model accuracy in real-world conditions using webcam input on PC, before deploying to Raspberry Pi 5. The NCNN format export allows testing the exact model that will run on the target hardware.

## What Changes

- Create Python inference script using OpenCV to capture webcam frames
- Implement YOLO11n NCNN model loading and inference pipeline
- Create requirements.txt with necessary dependencies (opencv-python, numpy, ultralytics)
- Add model files (YOLO11n.pt for training reference, NCNN files for inference)
- Create visualization overlay for detection results

## Capabilities

### New Capabilities

- `yolo-ncnn-inference`: Real-time object detection using YOLO11n model in NCNN format with webcam input

### Modified Capabilities

- None

## Impact

- New directory: `pc-inference/` with Python scripts and model files
- Dependencies: opencv-python, numpy, ultralytics
- Output: Real-time detection visualization with bounding boxes and confidence scores
