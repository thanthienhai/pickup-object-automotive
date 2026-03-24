## Context

To generate additional training data for the object picking robot, we need a dataset of isolated objects. Previously, a segmentation approach was considered to remove backgrounds entirely. However, to simplify the process and focus on object localization, we will use a standard object detection model (`yolo11m.pt`). This tool will run on a standard PC to process batches of images, detecting objects and cropping their bounding boxes into separate image files.

## Goals / Non-Goals

**Goals:**
- Load an input folder of images.
- Use the `yolo11m.pt` model to perform object detection.
- For every object detected in an image, use its bounding box to crop the object.
- Save the cropped object as a `.png` file.
- Handle images with multiple objects by saving each cropped box as a separate file.

**Non-Goals:**
- Removing the background perfectly (no alpha channel transparency). This change ONLY crops rectangular bounding boxes.
- Creating the actual synthetic data (e.g., pasting these objects onto new backgrounds). 
- Running this process on the Raspberry Pi. This is a heavy preprocessing step meant for the development PC.

## Decisions

- **Model Choice**: Use `yolo11m.pt` (Detection) instead of `-seg` (Segmentation). Rationale: Standard detection models are faster, easier to work with, and sufficient if the goal is just to gather cropped image patches of objects. It avoids the complexity of mask handling and alpha channel creation.
- **Image Format**: Output files will be `.png` (though `.jpg` could also be used since there is no transparency anymore, `.png` avoids compression artifacts).
- **Extraction Method**: Use the `[xmin, ymin, xmax, ymax]` coordinates from YOLO's bounding boxes to perform a simple numpy array slice on the original image, then save the slice.
- **Directory Structure**: Create `create-data-v1/input` and `create-data-v1/output` folders. Rationale: Keeps the workflow organized and prevents overwriting original data.

## Risks / Trade-offs

- **[Trade-off] Retained Background**: Unlike segmentation, cropping bounding boxes will retain some original floor/track background around the object inside the rectangle. This means these patches cannot be cleanly pasted onto new synthetic backgrounds without manual editing.
  - *Mitigation*: Ensure the YOLO bounding boxes are tight, or accept that the synthetic augmentation pipeline will involve rectangular patches rather than perfectly isolated shapes.
- **[Risk] Processing Time**: Running a medium detection model over thousands of images can take time on a CPU.
  - *Mitigation*: Rely on PyTorch/Ultralytics GPU acceleration if available on the PC. Since this is an offline batch job, processing time is less critical than inference time on the robot.
