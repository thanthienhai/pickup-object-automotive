## ADDED Requirements

### Requirement: Filename Parsing and Class Mapping
The tool SHALL parse the filename of extracted object images to derive a class label. Specifically, it SHALL split the filename by the hyphen (`-`) and take the first part as the class name.

#### Scenario: Parsing filename
- **WHEN** the script encounters a file named `bong-ban-1.png`
- **THEN** it extracts the string `bong-ban` as the class name and maps it to an integer ID (e.g., 0) in the internal class list.

### Requirement: Image Composition
The tool SHALL paste an object patch onto a randomly selected background image at a random (x, y) coordinate, ensuring the entire object fits within the background boundaries.

#### Scenario: Pasting object
- **WHEN** a background of size 640x480 and an object of size 50x50 are selected
- **THEN** the object is pasted at a random `x` between 0 and 590, and random `y` between 0 and 430.

### Requirement: YOLO Label Generation
The tool SHALL calculate the bounding box of the pasted object in YOLO format (normalized x_center, y_center, width, height) and save it as a `.txt` file corresponding to the generated image.

#### Scenario: Generating label file
- **WHEN** an object of size 50x40 is pasted at x=100, y=120 on a 640x480 background
- **THEN** a `.txt` file is created containing the line: `<class_id> 0.117 0.167 0.078 0.083` (normalized values).

### Requirement: Dataset Directory Structure
The tool SHALL save the generated images into a `dataset/images/train/` folder and the corresponding label files into `dataset/labels/train/` folder, adhering strictly to the YOLO directory structure.

#### Scenario: Output verification
- **WHEN** the script finishes generating 100 synthetic images
- **THEN** the folder structure contains exactly `dataset/images/train/` (with 100 images) and `dataset/labels/train/` (with 100 .txt files).

### Requirement: Configuration Persistence
The tool SHALL generate a `dataset.yaml` file listing the class names and their integer IDs (e.g., `names: ['bong-ban', 'khoi-vuong']`) for immediate use in training.

#### Scenario: Creating dataset yaml
- **WHEN** the script finishes processing
- **THEN** a `dataset.yaml` file is created in the root of the output directory, ready to be used by `train.py`.