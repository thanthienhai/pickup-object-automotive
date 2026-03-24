## Why

This change introduces a dedicated, highly optimized YOLO11 NCNN inference program tailored for a headless Raspberry Pi 5 (8GB) without a Hailo AI accelerator. Running the standard PC inference script on a Raspberry Pi can be inefficient and lacks the ability to visually verify results on a NO GUI (headless) setup. This change solves the problem by providing a streamlined inference loop optimized for CPU execution using NCNN, and adds functionality to save processed frames to disk for post-execution review.

## What Changes

- Create a new directory `pi-inference` to contain the Raspberry Pi specific inference code.
- Develop a highly optimized inference script for Raspberry Pi 5 using the Ultralytics YOLO NCNN format.
- Implement a headless mode operation that bypasses GUI requirements (e.g., `cv2.imshow`, `cv2.waitKey`).
- Add a feature to save annotated output frames to a specified directory for later inspection.
- Optimize camera capture and inference loop specifically for the Raspberry Pi environment.

## Capabilities

### New Capabilities
- `pi-inference-headless`: A highly optimized headless object detection inference pipeline tailored for Raspberry Pi 5 using NCNN models, including frame saving capabilities for result verification without a GUI.

### Modified Capabilities

## Impact

- **New Code**: Adds `pi-inference/run_model_pi.py` (or similar).
- **Dependencies**: Requires OpenCV (headless version recommended) and Ultralytics library on the Raspberry Pi.
- **System**: Designed specifically for Raspberry Pi OS (Bookworm) running in a headless (CLI only) environment.
