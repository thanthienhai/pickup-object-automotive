## 1. Setup

- [x] 1.1 Ensure the `create-data-v1/output/` directory structure exists with subfolders for each object class.
- [x] 1.2 Create `create-data-v1/backgrounds/` subdirectory to store background images.
- [x] 1.3 Create `create-data-v1/output_dataset/` directory as the root for the generated YOLO dataset.

## 2. Core Implementation

- [x] 2.1 Create `create-data-v1/generate_dataset.py`. Import `cv2`, `numpy`, `os`, `random`, `shutil`.
- [x] 2.2 Implement `get_classes_from_folders(base_path)` to scan `output/` subdirectories and get folder names as class labels (e.g., "bong", "bangdinh", "tenis").
- [x] 2.3 Implement `get_or_create_class_id(class_name, class_map)` to maintain a dictionary mapping string names to integer IDs.

## 3. Image Processing

- [x] 3.1 Implement `load_image(path)` using `cv2.imread`.
- [x] 3.2 Implement `load_backgrounds(background_dir)` to load all background images.
- [x] 3.3 Implement `load_objects_from_class(output_base_path, class_name)` to load all images from a specific class folder.
- [x] 3.4 Implement `paste_object(background, object_img, x, y)` to overlay the object onto the background using numpy slicing.
- [x] 3.5 Implement `calculate_yolo_bbox(x, y, obj_w, obj_h, bg_w, bg_h)` to return normalized `(x_center, y_center, width, height)`.

## 4. Generation Loop - Various Sizes

- [x] 4.1 Implement `resize_object(obj_img, scale_min, scale_max)` to randomly resize object to various scales.
- [x] 4.2 Implement the main loop to iterate `NUM_SAMPLES` times (e.g., 1000).
- [x] 4.3 Inside the loop: randomly pick a background and an object from random class.
- [x] 4.4 Apply random resize to the object (scale between 0.2 to 1.0 of original size).
- [x] 4.5 Calculate a valid random `(x, y)` coordinate ensuring the object fits inside the background.
- [x] 4.6 Call the paste function and the bbox calculation function.

## 5. Output

- [x] 5.1 Save the composed image to `output_dataset/images/train/frame_XXXX.jpg`.
- [x] 5.2 Save the corresponding label `.txt` file to `output_dataset/labels/train/frame_XXXX.txt` in YOLO format: `<class_id> <x_center> <y_center> <width> <height>`.
- [x] 5.3 Generate `output_dataset/dataset.yaml` with the discovered class names and IDs at the end of the script.

## 6. Verification

- [x] 6.1 Add a final print summary showing: Total images generated, Total classes discovered, Class list, Output folder location.