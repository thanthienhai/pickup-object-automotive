## Context

We have raw image patches of objects saved as `.png` files (e.g., `bong-ban-01.png`, `khoi-vuong-02.png`) from our previous extraction step. Currently, we lack a formal dataset with annotated `.txt` files to train our YOLO11n model. Manually annotating hundreds of images is tedious. We need an automatic pipeline that pastes these object patches onto various background images and mathematically calculates the exact bounding box coordinates, automatically generating a YOLO-compatible dataset ready for training.

## Goals / Non-Goals

**Goals:**
- Read object patch images from an `objects/` directory.
- Read background images from a `backgrounds/` directory.
- Parse the object's filename to automatically determine its class name (e.g., extracting "bong-ban" from "bong-ban-1.png").
- Maintain an internal dictionary mapping class names to integer IDs (e.g., `{"bong-ban": 0, "khoi-vuong": 1}`).
- Overlay one or more objects onto a randomly selected background at a random (x, y) position.
- Calculate the new bounding box coordinates of the pasted object in YOLO format (normalized `x_center`, `y_center`, `width`, `height`).
- Output the generated images to a `dataset/images/train/` structure and the corresponding `.txt` labels to `dataset/labels/train/`.

**Non-Goals:**
- Creating complex, physically accurate 3D scene generation. This will be simple 2D image overlaying (pasting rectangles onto rectangles).
- Complex augmentation like lighting or blurring (this can be handled by YOLO's native augmentations during training).

## Decisions

- **Image Composition Method**: We will use basic OpenCV and Numpy slicing to paste the object patch onto the background. Since the extracted objects are not perfectly transparent (they retain some original background due to the bounding box crop), they will look like small rectangles pasted on the new background.
  - *Rationale*: Simple bounding box pasting is computationally cheap and surprisingly effective for training object detection models, known as "Cut-and-Paste" or "Mosaic-like" augmentation. The model learns to focus on the object features inside the rectangle rather than the surrounding context.
- **Label Generation**: YOLO requires coordinates in the format `[class_id x_center y_center width height]`, normalized to `0.0 - 1.0`. We will calculate this precisely based on the top-left coordinate `(x, y)` where we choose to paste the object, and its `width` and `height`.
- **Output Structure**: The script will create a complete `yolo_dataset` directory containing the `images` and `labels` folders, alongside a generated `dataset.yaml` file so it is instantly ready for `train.py`.

## Risks / Trade-offs

- **[Trade-off] Bounding Box Background Artifacts**: Because the source patches are not transparent shapes but solid rectangles (from the `extract_objects.py` detection step), the generated images will literally look like photos pasted on top of other photos. 
  - *Mitigation*: While it looks unnatural to humans, Convolutional Neural Networks (CNNs) often handle this well and still learn the core features of the object. We will ensure the YOLO training script uses heavy native augmentations (like Mosaic, MixUp, HSV shifting) to further blend these artifacts during the actual training phase.
- **[Risk] Objects Pasted Outside Bounds**: If an object is pasted too close to the edge of the background, it might get cut off or crash the numpy slicing operation.
  - *Mitigation*: The random `(x, y)` generation logic will explicitly constrain the maximum `x` to `background_width - object_width`, and similarly for `y`, ensuring the object always fits entirely inside the frame.