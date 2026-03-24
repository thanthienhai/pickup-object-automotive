## ADDED Requirements

### Requirement: Automated Headless Image Capture
The script SHALL capture images from the specified USB camera automatically without opening a graphical window (headless), to maximize speed on the Raspberry Pi Lite OS.

#### Scenario: Running the script on Pi
- **WHEN** the `collect_data.py` script is executed via terminal
- **THEN** it connects to the camera (e.g., ID 0) and begins capturing frames internally without any display output.

### Requirement: Configurable Capture Interval
The script SHALL save an image to disk exactly once every `X` seconds, where `X` is a configurable variable (e.g., `SAVE_INTERVAL = 0.5`).

#### Scenario: Timing the captures
- **WHEN** the script is running with a 0.5-second interval
- **THEN** it generates and saves exactly 2 frames per second to the target directory.

### Requirement: Target Resolution Matching
The script SHALL configure the camera hardware to capture images at exactly 320x240 resolution.

#### Scenario: Verifying image output
- **WHEN** the user inspects the saved `.jpg` files
- **THEN** the dimensions of every file are exactly 320 pixels wide and 240 pixels high.

### Requirement: Capture Limit Protection
The script SHALL stop automatically after saving `MAX_IMAGES` to prevent filling the SD card.

#### Scenario: Reaching the limit
- **WHEN** the script saves its 1000th image (if `MAX_IMAGES=1000`)
- **THEN** it cleanly releases the camera, prints a completion message, and exits.

### Requirement: Filename Uniqueness
The script SHALL name the saved files using a high-precision timestamp to ensure alphabetical sorting and prevent accidental overwrites.

#### Scenario: Inspecting filenames
- **WHEN** multiple files are saved
- **THEN** the filenames match the format `dataset/raw_images/frame_YYYYMMDD_HHMMSS_mmm.jpg` (or similar).