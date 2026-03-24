## Why

The current AI system relies on pre-trained models that lack domain-specific data (e.g., the specific objects the robot needs to pick up, the specific lighting, and floor textures). To achieve high accuracy on the Raspberry Pi 5, we need a complete pipeline to automatically collect real-world image data from the robot's camera and a separate pipeline to train a YOLO11 model and export it to the highly optimized NCNN format.

## What Changes

- Create a `data-collection` module designed to run on the Raspberry Pi. This module will connect to the camera and automatically save images at a set interval without running any heavy AI inference, maximizing frame rate and stability during data gathering runs.
- Create a `model-training` module designed to run on a PC or Cloud environment. This will include scripts to train a YOLO11 model on the annotated dataset and export the best resulting model to the NCNN format required by the Pi.

## Capabilities

### New Capabilities
- `auto-data-collection`: A lightweight script for the Raspberry Pi to automatically capture and save camera frames at specific intervals for dataset creation.
- `yolo-ncnn-training`: A pipeline to train a YOLO11 model using a custom dataset and export the trained weights to the NCNN format.

### Modified Capabilities

## Impact

- **New Code**: Introduces scripts in `data-collection/` and `model-training/` directories.
- **Dependencies**: The training module will require the full `ultralytics` package (which includes PyTorch), unlike the Pi which only needs the headless inference version.
- **Workflow**: Establishes a formal workflow for continuously improving the robot's vision system through iterative data collection and retraining.