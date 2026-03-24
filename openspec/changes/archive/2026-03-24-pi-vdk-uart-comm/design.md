## Context

The system consists of a Raspberry Pi 5 acting as the "eyes" (running YOLO11n object detection via NCNN) and a separate microcontroller (Arduino/STM32) acting as the "muscles" (driving motors and servos). We need a bridge between them. According to the specification in `pi-vdk.md`, the Pi must send a specific ASCII string format containing object detection details (status, class ID, x-center, y-max, and area) over a serial UART connection to instruct the microcontroller when and where to pick up an object.

## Goals / Non-Goals

**Goals:**
- Establish a reliable Serial connection via Python (`pyserial`).
- Extract the largest `Y_MAX` bounding box from YOLO results.
- Format the extracted data into the `$<STATUS>,<CLASS_ID>,<X_CENTER>,<Y_MAX>,<AREA>#\n` string.
- Transmit the packet over UART at a standard baud rate (115200) without blocking the camera's FPS.

**Non-Goals:**
- Writing the C++ receiving code for the microcontroller (this change is strictly for the Pi-side Python code in `pi-vdk/`).
- Two-way communication (currently only Pi -> VĐK telemetry is needed).

## Decisions

- **Protocol Format**: ASCII strings using start (`$`) and end (`#\n`) delimiters, comma-separated values. Rationale: Extremely easy to parse on low-memory 8-bit microcontrollers using `Serial.readStringUntil()` or `strtok()`, avoiding complex binary struct serialization issues across different architectures.
- **Data Filtering**: If multiple objects are detected, the Python script will sort them by their `y_max` value (calculated as `y_center + height/2`) and only transmit data for the object with the highest `y_max`. Rationale: The object lowest on the screen (highest Y value) is physically closest to the robot's gripper.
- **Library**: Use the standard `pyserial` library in Python. It's robust, cross-platform, and the industry standard for serial communication.
- **Port Flexibility**: The serial port (e.g., `/dev/ttyUSB0` or `/dev/serial0`) and baud rate will be configurable variables at the top of the script to allow easy switching between USB-Serial adapters and direct GPIO UART pins.
- **Keep-alive**: The script will continuously send empty packets (`$0,0,0,0,0#\n`) when no objects are detected. Rationale: This acts as a heartbeat, letting the microcontroller know the Pi is still running and hasn't crashed.

## Risks / Trade-offs

- **[Risk] Serial Buffer Overflow**: If the Pi sends data faster than the microcontroller can process it, the microcontroller's serial buffer might overflow, leading to corrupted packets or missed detections.
  - *Mitigation*: The Pi will send data at the same rate as the camera FPS (e.g., 15Hz), which is slow enough for a 115200 baud connection. The newline character `\n` allows the microcontroller to quickly flush and read discrete packets.
- **[Risk] Incorrect Port Configuration**: `pyserial` will crash if the specified port doesn't exist (e.g., unplugged USB).
  - *Mitigation*: Wrap the serial initialization in a `try...except` block and implement an automatic reconnection mechanism or a fallback mode (e.g., just print to console if no serial device is found).