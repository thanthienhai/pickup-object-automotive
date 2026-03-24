## 1. Setup

- [x] 1.1 Add `pyserial` to `pi-inference/requirements.txt` to enable serial communication.
- [x] 1.2 Import `serial` and handle connection configuration in `pi-inference/run_model_pi.py`. Set default port to `/dev/ttyUSB0` and baud rate to `115200`.

## 2. Detection Processing

- [x] 2.1 Update the inference loop to parse detection results. Extract the class ID, `x_center`, `y_center`, width, and height.
- [x] 2.2 Calculate `y_max = y_center + height / 2` for each bounding box.
- [x] 2.3 Implement sorting/filtering logic to identify the single detected object with the largest `y_max` (the object closest to the camera).

## 3. Telemetry Transmission

- [x] 3.1 Implement a `send_telemetry(serial_conn, status, class_id, x_center, y_max, area)` function to construct the ASCII packet `$status,class_id,x,y,area#\n`.
- [x] 3.2 Ensure the telemetry function handles string encoding (UTF-8) before transmitting over the serial connection.
- [x] 3.3 Call the telemetry function with the selected object's data if an object is found.
- [x] 3.4 Call the telemetry function with a status of `0` (`$0,0,0,0,0#\n`) as a heartbeat if no objects are detected in the current frame.

## 4. Refactoring & Error Handling

- [x] 4.1 Wrap serial connection initialization in a `try...except` block to allow the script to run without crashing if the microcontroller is unplugged.
- [x] 4.2 Close the serial connection cleanly in the `finally` block or `KeyboardInterrupt` handler.
- [x] 4.3 Update console logging to optionally print the transmitted string for easy debugging.