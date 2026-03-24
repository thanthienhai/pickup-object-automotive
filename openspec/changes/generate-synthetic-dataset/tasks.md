## 1. Setup

- [ ] 1.1 Ensure the `create-data-v1/` directory structure exists (it should from previous work).
- [ ] 1.2 Create `create-data-v1/objects/` subdirectory to store extracted patches from `extract_objects.py`.
- [ ] 1.3 Create `create-data-v1/backgrounds/` subdirectory to store background images.
- [ ] 1.4 Create `create-data-v1/output_dataset/` directory as the root for the generated YOLO dataset.

## 2. Core Implementation

- [ ] 2.1 Create `create-data-v1/generate_dataset.py`. Import `cv2`, `numpy`, `os`, `random`.
- [ ] 2.2 Implement `parse_class_from_filename(filename)` to extract the label (e.g., "bong-ban" from "bong-ban-1.png").
- [ ] 2.3 Implement `get_or_create_class_id(class_name, class_map)` to maintain a dictionary mapping string names to integer IDs.

## 3. Image Processing

- [ ] 3.1 Implement `load_image(path)` using `cv2.imread`.
- [ ] 3.2 Implement `paste_object(background, object_img, x, y)` to overlay the object onto the background using numpy slicing.
- [ ] 3.3 Implement `calculate_yolo_bbox(x, y, obj_w, obj_h, bg_w, bg_h)` to return normalized `(x_center, y_center, width, height)`.

## 4. Generation Loop

- [ ] 4.1 Implement the main loop to iterate `NUM_SAMPLES` times (e.g., 1000).
- [ ] 4.2 Inside the loop: randomly pick a background and an object.
- [ ] 4.3 Calculate a valid random `(x, y)` coordinate ensuring the object fits inside the background.
- [ ] 4.4 Call the paste function and the bbox calculation function.

## 5. Output

- [ ] 5.1 Save the composed image to `output_dataset/images/train/frame_XXXX.jpg`.
- [ ] 5.2 Save the corresponding label `.txt` file to `output_dataset/labels/train/frame_XXXX.txt` in YOLO format: `<class_id> <x_center> <y_center> <width> <height>`.
- [ ] 5.3 Generate `output_dataset/dataset.yaml` with the discovered class names and IDs at the end of the script.

## 6. Verification

- [ ] 6.1 Add a final print summary showing: Total images generated, Total classes discovered, Output folder location.