## Context

The current `pi-inference` and `pi-vdk` modules rely on a pre-trained `yolo11n_ncnn_model` which has no knowledge of the specific objects the robot is designed to pick up in its actual environment. We must establish a full Data Engine loop. The first part is `data-collection` running on the Pi to gather raw `.jpg` frames of the objects on the actual track. After external annotation (e.g., via Roboflow), the second part, `model-training`, runs on a powerful PC or Colab to train a custom YOLO11n model and export it to NCNN for deployment back to the Pi.

## Goals / Non-Goals

**Goals:**
- Provide a standalone Python script for the Raspberry Pi to capture images at a fixed, configurable interval without running the heavy YOLO model.
- Provide a training script structure for a PC that downloads/loads the dataset, trains a YOLO11n model for 100 epochs, and exports the `best.pt` weights to the NCNN format.
- Ensure the image sizes (e.g., 320x240) and configurations match perfectly between the collection phase, the training phase, and the final inference phase.

**Non-Goals:**
- Building a custom annotation tool. (We will assume standard tools like CVAT, LabelImg, or Roboflow will be used externally).
- Setting up cloud GPU infrastructure. (The scripts will assume a local Python environment or Google Colab with Ultralytics installed).

## Decisions

- **Data Collection Resolution**: The camera capture resolution in `data-collection` will be explicitly set to 320x240. Rationale: Training on images of the exact same resolution and aspect ratio as the target inference environment minimizes scaling distortions and improves small object detection.
- **Collection Interval**: Implement a time-based interval (e.g., 1 frame every 0.5 seconds) using `time.time()`. Rationale: Simpler and more reliable than frame-counting, especially if camera FPS fluctuates.
- **Max Image Cap**: Implement a hard limit on the number of images to collect per session (e.g., 1000). Rationale: Prevents the script from silently filling up the Raspberry Pi's SD card if left running accidentally.
- **Training Model Architecture**: We will strictly use `yolo11n.pt` (the Nano version). Rationale: It is the only variant that will realistically hit the 10-15 FPS target on the Raspberry Pi 5's CPU after NCNN optimization. Larger models (s, m, l) will cause unacceptable latency.
- **Export Format**: Use the Ultralytics built-in `model.export(format='ncnn')`.

## Risks / Trade-offs

- **[Risk] Blurry Images during Collection**: Because the robot is moving, capturing frames at low light might result in motion blur, ruining the dataset.
  - *Mitigation*: The collection script should aim for a high framerate. We will recommend running the collection phase in well-lit environments or manually tuning the camera's exposure settings.
- **[Risk] Overfitting on Backgrounds**: If all collected images have the exact same floor texture, the model will fail on a different floor.
  - *Mitigation*: The training documentation/readme must emphasize capturing images in varied environments and intentionally including "background-only" images in the dataset to reduce False Positives.