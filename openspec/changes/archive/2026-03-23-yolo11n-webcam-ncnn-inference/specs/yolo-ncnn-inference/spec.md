## ADDED Requirements

### Requirement: Webcam frame capture
The system SHALL capture frames from the default webcam using OpenCV.

#### Scenario: Successful webcam initialization
- **WHEN** the application starts with a connected webcam
- **THEN** the webcam is opened and ready to capture frames

#### Scenario: Webcam not available
- **WHEN** no webcam is connected or webcam is in use
- **THEN** the application SHALL display an error message and exit gracefully

### Requirement: NCNN model loading
The system SHALL load the YOLO11n model from NCNN format files.

#### Scenario: Model loads successfully
- **WHEN** the NCNN model files (.param and .bin) are present
- **THEN** the model is loaded into memory and ready for inference

#### Scenario: Model files missing
- **WHEN** NCNN model files are not found
- **THEN** the application SHALL display an error message and exit

### Requirement: Real-time object detection
The system SHALL perform object detection on each webcam frame.

#### Scenario: Detection runs at runtime
- **WHEN** a frame is captured from the webcam
- **THEN** the model processes the frame and returns detected objects with bounding boxes and confidence scores

### Requirement: Detection visualization
The system SHALL display detection results overlaid on the video feed.

#### Scenario: Visualize detections
- **WHEN** objects are detected in a frame
- **THEN** bounding boxes are drawn with class labels and confidence scores

#### Scenario: No detections
- **WHEN** no objects are detected in a frame
- **THEN** the original frame is displayed without modifications
