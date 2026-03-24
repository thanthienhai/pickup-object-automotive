## ADDED Requirements

### Requirement: Serial Initialization
The system SHALL attempt to open a serial connection to the microcontroller at startup. If the configured port is unavailable, it SHALL log a warning but continue running inference without crashing.

#### Scenario: Valid Serial Port
- **WHEN** the script is started with a valid, connected serial port (e.g., `/dev/ttyUSB0`)
- **THEN** it successfully connects at the specified baud rate (e.g., 115200) and prepares to transmit.

#### Scenario: Missing Serial Port
- **WHEN** the script is started but the serial device is not plugged in
- **THEN** it catches the exception, prints a warning to the console, and continues running the camera inference loop.

### Requirement: Detection Filtering
When multiple objects are detected in a single frame, the system SHALL filter the results and select the object with the highest `Y_MAX` value (physically closest to the robot).

#### Scenario: Multiple Objects Detected
- **WHEN** YOLO returns multiple bounding boxes in one frame
- **THEN** the system iterates through them, calculates `y_center + height/2` for each, and selects the single bounding box with the highest resulting value.

### Requirement: Packet Formatting
The system SHALL format the selected bounding box data into an ASCII string exactly matching the format `$<STATUS>,<CLASS_ID>,<X_CENTER>,<Y_MAX>,<AREA>#\n`. All numerical values SHALL be integers.

#### Scenario: Object Data Formatting
- **WHEN** an object is selected (e.g., class 2, x=158, y_max=120, area=4500)
- **THEN** the resulting string is exactly `$1,2,158,120,4500#\n`.

### Requirement: Heartbeat Transmission
When no objects are detected in the current frame, the system SHALL transmit an empty packet to signal that it is still running and "blind."

#### Scenario: No Objects Detected
- **WHEN** YOLO returns an empty list of detections for the current frame
- **THEN** the system transmits exactly `$0,0,0,0,0#\n` over the serial connection.
