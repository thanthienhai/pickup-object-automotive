## 1. Setup

- [x] 1.1 Create `create-data-v1` directory.
- [x] 1.2 Create `create-data-v1/input` directory to place raw images.
- [x] 1.3 Create `create-data-v1/output` directory for saving extracted object `.png` files.
- [x] 1.4 Add `ultralytics` and `opencv-python` to a local `requirements.txt` inside `create-data-v1`.

## 2. Core Implementation

- [x] 2.1 Create `create-data-v1/extract_objects.py`. Import necessary libraries (`cv2`, `numpy`, `os`, `ultralytics`).
- [x] 2.2 Initialize YOLO with `yolo11m.pt` (Detection model).
- [x] 2.3 Implement directory iteration logic to load every image from `input/`.
- [x] 2.4 Run model inference `model.predict(img)` to get bounding boxes.

## 3. Image Cropping Processing

- [x] 3.1 Extract bounding boxes `.xyxy` from the YOLO `Results` object.
- [x] 3.2 Iterate through bounding boxes and extract `[x1, y1, x2, y2]`.
- [x] 3.3 Ensure crop coordinates are within image boundaries.
- [x] 3.4 Slice the original BGR numpy array using the coordinates to obtain the cropped object patch.

## 4. Output Generation

- [x] 4.1 Construct a unique filename for each extracted object using the original filename and an index (e.g., `original_obj_0.png`).
- [x] 4.2 Save the cropped BGR image to the `output/` directory using `cv2.imwrite`.
- [x] 4.3 Add a summary print statement displaying the total number of images processed and total objects extracted.
