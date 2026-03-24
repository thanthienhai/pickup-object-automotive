## 1. Setup

- [x] 1.1 Create `data-collection` directory for Raspberry Pi capture scripts.
- [x] 1.2 Create `model-training` directory for PC/Colab training scripts.
- [x] 1.3 Create `dataset.yaml` skeleton in `model-training` with empty classes.

## 2. Implement Data Collection Module

- [x] 2.1 Create `data-collection/collect_data.py` to initialize the camera (ID 0) without any YOLO/AI models loaded.
- [x] 2.2 Configure the camera in `collect_data.py` to exactly 320x240 resolution.
- [x] 2.3 Implement the main loop using `time.time()` to save a `.jpg` frame every `0.5` seconds.
- [x] 2.4 Add `MAX_IMAGES` counter logic (e.g., 1000) to gracefully exit when the limit is reached.
- [x] 2.5 Ensure filenames use precise timestamps (e.g., `frame_20260324_153022_123.jpg`) and save to a `dataset/raw_images` folder.
- [x] 2.6 Add a specific `requirements.txt` for `data-collection` containing only `opencv-python-headless`.

## 3. Implement Training & Export Module

- [x] 3.1 Create `model-training/train.py` using the `ultralytics` package to train `yolo11n.pt` on the custom `dataset.yaml`.
- [x] 3.2 Ensure `train.py` explicitly sets `imgsz=320` and `epochs=100`.
- [x] 3.3 Create `model-training/export.py` to convert the resulting `best.pt` file to `ncnn` format.
- [x] 3.4 Add a `requirements.txt` for `model-training` containing `ultralytics` (the full version, not headless).
- [x] 3.5 Create a `README.md` in `model-training` outlining the steps from Roboflow export to NCNN deployment on Pi.