## Why

The Raspberry Pi 5 runs a YOLO11 NCNN object detection model but currently lacks a mechanism to communicate its findings (like object class and position) to the motor-controlling microcontroller (VĐK). To enable the robot to actually pick up objects, we need a robust UART communication protocol to send real-time bounding box data from the Pi to the VĐK.

## What Changes

- Create a new directory `pi-vdk` to house the communication code.
- Develop a Python script (`pi-vdk/uart_sender.py` or integrated into inference) to format and send detection data via UART (TX/RX or USB Serial).
- Implement the specific ASCII packet protocol defined in `pi-vdk.md` (`$<STATUS>,<CLASS_ID>,<X_CENTER>,<Y_MAX>,<AREA>#\n`).
- Implement logic to filter detections and only send the object closest to the robot (largest `Y_MAX`).

## Capabilities

### New Capabilities
- `uart-telemetry`: A capability to parse YOLO bounding boxes, format them into a lightweight ASCII string, and transmit them over a serial connection at a defined baud rate to a microcontroller.

### Modified Capabilities

## Impact

- **New Code**: Introduces new Python scripts in the `pi-vdk/` directory utilizing the `pyserial` library.
- **Dependencies**: Requires `pyserial` to be installed on the Raspberry Pi.
- **System**: Requires hardware connection (USB or GPIO TX/RX) between the Raspberry Pi 5 and the target microcontroller, with matched baud rates (e.g., 115200).