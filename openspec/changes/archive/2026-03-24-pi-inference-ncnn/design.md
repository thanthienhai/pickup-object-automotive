## Context

The current `pc-inference/run_model_base.py` is designed for a desktop environment with a graphical user interface (GUI) and more computational power. The new target is a Raspberry Pi 5 (8GB) running a headless OS (Bookworm) without a dedicated Hailo AI accelerator. Running standard PyTorch models or GUI-dependent OpenCV code on this environment is inefficient and error-prone. We need a dedicated script (`pi-inference/run_model_pi.py`) that uses the NCNN optimized YOLO model, processes frames from a USB camera, and saves annotated output frames to disk for asynchronous verification, ensuring the highest possible frame rate (FPS) on the Pi's CPU.

## Goals / Non-Goals

**Goals:**
- Implement a stable inference loop using NCNN optimization on a Raspberry Pi 5.
- Achieve a steady frame rate (target: 10-15 FPS) at 320x240 resolution.
- Ensure the script runs entirely without a GUI (headless mode).
- Save processed and annotated frames periodically or based on detection events to a designated folder for later review.

**Non-Goals:**
- Implementing Hailo accelerator support (explicitly excluded).
- Adding complex object tracking or advanced analytics beyond basic bounding box detection.
- Building a web dashboard or real-time streaming server (only local file saving is required).

## Decisions

- **Framework & Model Format**: Use Ultralytics YOLO with an `ncnn` exported model (`yolo11n_ncnn_model`). NCNN is highly optimized for mobile and edge CPUs, making it the best choice for the Pi 5 without external accelerators.
- **Headless Execution**: Remove all `cv2.imshow()` and `cv2.waitKey()` calls. The script will run as a pure background process.
- **Image Saving Strategy**: Instead of streaming video, the script will save annotated frames using `cv2.imwrite()`. To prevent disk I/O bottlenecks and SD card wear, we will implement a frame-skipping mechanism (e.g., save 1 frame every second) or only save frames when an object of interest is detected with high confidence.
- **Camera Backend**: Use the default V4L2 backend on Linux (`/dev/video0`) instead of `cv2.CAP_DSHOW` (which is Windows-only).
- **Directory Structure**: Create a new folder `pi-inference` to isolate Pi-specific code, avoiding clutter in the existing PC inference code. Output frames will be saved in `pi-inference/output_frames`.

## Risks / Trade-offs

- **Disk I/O Bottleneck**: Saving every single frame as a JPEG image to an SD card will cause severe I/O bottlenecks and drastically lower the FPS.
  - *Mitigation*: Only save frames periodically (e.g., 1 FPS) or conditionally (only when objects are detected). Implement async saving if necessary, though simple conditional saving is usually sufficient.
- **CPU Thermal Throttling**: NCNN inference on all 4 cores of the Pi 5 can generate significant heat.
  - *Mitigation*: Limit the number of threads used by NCNN or rely on the OS thermal management. Ensure the Pi 5 has adequate cooling (active cooler recommended).
- **Camera Initialization Issues**: USB cameras on Linux can sometimes fail to initialize immediately.
  - *Mitigation*: Retain and enhance the retry logic from the base script to ensure robust camera connection handling.