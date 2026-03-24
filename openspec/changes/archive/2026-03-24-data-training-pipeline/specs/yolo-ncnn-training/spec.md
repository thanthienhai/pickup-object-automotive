## ADDED Requirements

### Requirement: Pre-configured Dataset Structure
The system SHALL provide a `dataset.yaml` file defining the exact folder structure required by YOLO11 (`train`, `val`, `images`, `labels`).

#### Scenario: Running YOLO training
- **WHEN** the `train.py` script starts and calls `ultralytics YOLO`
- **THEN** it successfully references `dataset.yaml` and finds the appropriate train/val directories.

### Requirement: YOLO11n Model Training
The training script SHALL train the `yolo11n.pt` model (nano architecture) for a predefined number of epochs and image size, specifically setting `imgsz=320`.

#### Scenario: Running `train.py`
- **WHEN** the `train.py` script is executed on a PC/Colab environment
- **THEN** it downloads the base `yolo11n.pt` weights, trains for the specified epochs, and outputs best weights in `runs/detect/train/weights/best.pt`.

### Requirement: NCNN Model Export
The export script SHALL convert the final `best.pt` PyTorch weights into the optimized NCNN format suitable for the Raspberry Pi 5 CPU.

#### Scenario: Running `export.py`
- **WHEN** the `export.py` script is executed pointing to `best.pt`
- **THEN** it calls the Ultralytics export function with `format='ncnn'` and generates a new directory containing `.bin` and `.param` files.