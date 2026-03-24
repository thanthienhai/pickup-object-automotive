## Why

To improve the object detection model, we need to generate more diverse and robust training data. By extracting individual objects from raw images, we can create a clean dataset of isolated objects. These isolated images can later be used for advanced data augmentation, which significantly improves the model's ability to generalize across different environments. We will use a standard object detection model to achieve this simply by cropping bounding boxes.

## What Changes

- Create a new directory `create-data-v1` to house the data processing scripts.
- Develop a script to load a set of raw input images and run them through a pre-trained detection model (`yolo11m.pt`).
- Implement a processing pipeline that uses the bounding boxes from YOLO to crop out individual object patches.
- Save each extracted object patch as a separate `.png` file in a dedicated output folder.

## Capabilities

### New Capabilities
- `object-segmentation-extractor`: A capability to process a batch of images, identify objects using YOLO11 detection, crop out the bounding boxes containing the object, and save each isolated patch as a new image file. (Note: name retained from original proposal for continuity).

### Modified Capabilities

## Impact

- **New Code**: Introduces a new Python script in the `create-data-v1/` directory.
- **Dependencies**: Requires `ultralytics` for running the `yolo11m.pt` model, and `opencv-python` / `numpy` for image cropping.
- **System**: This is an offline data processing tool meant to run on a PC/Laptop, not on the Raspberry Pi. It will consume input images from a folder and generate output images in another.
