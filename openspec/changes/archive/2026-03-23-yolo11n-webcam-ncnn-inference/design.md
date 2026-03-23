## Context

Build a PC-based testing environment for YOLO11n object detection model using NCNN format. This enables real-world accuracy testing before Raspberry Pi 5 deployment.

## Goals / Non-Goals

**Goals:**
- Load YOLO11n model in NCNN format for inference
- Capture webcam frames using OpenCV
- Perform real-time object detection with visualization
- Achieve accurate representation of Pi 5 performance

**Non-Goals:**
- Training or model optimization (only inference)
- Multi-camera support
- Recording/saving outputs
- Integration with existing pickup-object-automotive system

## Decisions

| Decision | Rationale | Alternatives |
|----------|-----------|---------------|
| OpenCV for webcam | Cross-platform, well-documented, supports NCNN backend | cv2.direct (limited), V4L2 (Linux only) |
| NCNN format | Lightweight, CPU-efficient, matches Pi 5 deployment | ONNX (larger), TensorFlow Lite (different optimization) |
| Python script | Rapid prototyping, easy debugging, ultralytics ecosystem | C++ (faster but slower development) |
| Visualization overlay | Immediate feedback for testing | Save to file (slower iteration) |

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| NCNN model loading failure | Cannot test inference | Fallback to ONNX if NCNN fails |
| Webcam not available | Cannot capture input | Add error handling with user-friendly message |
| Low FPS on PC | Unrealistic performance expectation | Document actual PC performance vs Pi 5 expected |
| Model format mismatch | Accuracy differences between formats | Use same NCNN files as target deployment |
