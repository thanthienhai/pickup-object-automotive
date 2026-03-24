## 1. Setup
- [x] 1.3 Create `requirements.txt` with `opencv-python-headless`, `ultralytics`, and `ncnn` optimized for Raspberry Pi 5 headless environment.

- [x] 1.1 Create `pi-inference` directory and initialize empty Python script `run_model_pi.py`.
- [x] 1.2 Create `output_frames` subfolder within `pi-inference` for saving images.

## 2. Core Implementation

- [x] 2.1 Copy structure from `run_model_base.py` but remove all GUI components (e.g., `cv2.imshow`, `cv2.waitKey`, window management).
- [x] 2.2 Initialize the USB camera without using `cv2.CAP_DSHOW` (use default V4L2 for Raspberry Pi OS).
- [x] 2.3 Load the NCNN exported YOLO11n model.
- [x] 2.4 Implement the core inference loop with retry logic for reading frames.

## 3. Frame Saving Feature

- [x] 3.1 Implement a mechanism to periodically save annotated frames (e.g., using `cv2.imwrite` every `N` frames or seconds).
- [x] 3.2 Ensure filenames include timestamps for easy review and to avoid overwriting (e.g., `frame_20260324_153022.jpg`).

## 4. Optimization & Logging

- [x] 4.1 Apply resolution and FPS limits directly to the camera capture object (`cv2.CAP_PROP_FRAME_WIDTH`, `cv2.CAP_PROP_FRAME_HEIGHT`, `cv2.CAP_PROP_FPS`).
- [x] 4.2 Add precise console logging for inference time and FPS to monitor performance on the CPU.
- [x] 4.3 Add graceful shutdown handling for `KeyboardInterrupt` (Ctrl+C).
