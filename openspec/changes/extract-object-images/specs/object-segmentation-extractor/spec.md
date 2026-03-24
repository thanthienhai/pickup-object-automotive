## MODIFIED Requirements

### Requirement: Image Batch Processing
The tool SHALL iterate over all image files within an input directory (e.g., `.jpg`, `.png`) and process them sequentially without manual intervention.

#### Scenario: Running the script on a folder
- **WHEN** the script `extract_objects.py` is executed with an input folder containing 10 images
- **THEN** it iterates through all 10 images and completes the process for each.

### Requirement: Detection Model Loading
The tool SHALL explicitly load the YOLO11 medium detection model (`yolo11m.pt`) to generate bounding boxes of objects.

#### Scenario: Script initialization
- **WHEN** the script starts
- **THEN** it initializes an Ultralytics YOLO object using the `yolo11m.pt` weights, instead of the segmentation version.

### Requirement: Object Cropping
The tool SHALL crop the image tightly to the bounding box of the detected object, using the `[xmin, ymin, xmax, ymax]` coordinates.

#### Scenario: Saving an object
- **WHEN** a bounding box is returned by the YOLO model
- **THEN** the original image is sliced to the boundaries of the box and prepared for saving.

### Requirement: Unique Output Naming
The tool SHALL save each extracted and cropped object as a separate `.png` file in an output directory. If an input image contains multiple objects, each object SHALL receive a uniquely identifiable filename (e.g., `original_name_obj1.png`, `original_name_obj2.png`).

#### Scenario: Saving multiple objects from one image
- **WHEN** the script processes `photo1.jpg` which contains 3 distinct objects
- **THEN** it generates and saves 3 files in the output folder: `photo1_obj_0.png`, `photo1_obj_1.png`, and `photo1_obj_2.png`.

## REMOVED Requirements

### Requirement: Transparent Background Application
**Reason**: Replaced by simpler bounding box cropping using a Detection model.
**Migration**: Transparency logic using masks is deleted entirely.
