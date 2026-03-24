## ADDED Requirements

### Requirement: Headless Inference Loop Execution
The system SHALL run the inference loop continuously without requiring or attempting to open any graphical user interface (GUI) windows.

#### Scenario: Script initiation on headless OS
- **WHEN** the script is executed on an OS without a display server (e.g., Raspberry Pi OS Lite)
- **THEN** it completes initialization and starts processing frames without throwing GUI-related errors.

### Requirement: Camera Capture Initialization
The system SHALL initialize the USB camera using the default V4L2 backend on Linux, bypassing the Windows-specific DSHOW backend.

#### Scenario: Camera startup
- **WHEN** the inference script starts
- **THEN** it successfully connects to `/dev/video0` (or specified index) and applies the configured width, height, and FPS limits.

### Requirement: NCNN Model Optimization
The system SHALL use the NCNN format of the YOLO11n model to perform object detection, optimizing performance for the CPU on the Raspberry Pi 5.

#### Scenario: Loading the model
- **WHEN** the model is loaded during initialization
- **THEN** it explicitly loads the NCNN exported format from the designated path.

### Requirement: Annotated Frame Saving
The system SHALL save processed frames with bounding box annotations to a specified local directory to allow for asynchronous verification.

#### Scenario: Saving a detected frame
- **WHEN** an object is detected and the frame saving condition is met (e.g., once every N seconds or when confidence is above a threshold)
- **THEN** an annotated JPEG image is written to the `pi-inference/output_frames` directory.

### Requirement: Inference Performance Logging
The system SHALL log the inference time and FPS to the standard output (console) for performance monitoring.

#### Scenario: Console output during inference
- **WHEN** a frame is processed
- **THEN** the system prints a log message containing the camera ID, inference time in milliseconds, and the calculated FPS.
