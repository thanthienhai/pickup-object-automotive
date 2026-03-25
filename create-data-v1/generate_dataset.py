import cv2
import numpy as np
import os
import random
import shutil

NUM_SAMPLES = 1000
OUTPUT_DIR = "../model-training/output_dataset"
BACKGROUNDS_DIR = "backgrounds"
OBJECTS_DIR = "output"

# Standard Background Size
BG_WIDTH = 640
BG_HEIGHT = 480

# Object Size Constraints (in pixels relative to BG_WIDTH/BG_HEIGHT)
# This prevents objects from being 2 pixels wide or 1000 pixels wide.
OBJ_MIN_SIZE = 50   # Smallest dimension allowed
OBJ_MAX_SIZE = 250  # Largest dimension allowed

def get_classes_from_folders(base_path):
    classes = []
    if os.path.exists(base_path):
        for item in os.listdir(base_path):
            if os.path.isdir(os.path.join(base_path, item)):
                classes.append(item)
    return sorted(classes)

def get_or_create_class_id(class_name, class_map):
    if class_name not in class_map:
        class_map[class_name] = len(class_map)
    return class_map[class_name]

def load_image(path):
    return cv2.imread(path)

def load_backgrounds(background_dir):
    backgrounds = []
    if not os.path.exists(background_dir):
        return backgrounds
        
    for f in os.listdir(background_dir):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            backgrounds.append(os.path.join(background_dir, f))
    return backgrounds

def load_objects_from_class(output_base_path, class_name):
    objects = []
    class_dir = os.path.join(output_base_path, class_name)
    if os.path.exists(class_dir):
        for f in os.listdir(class_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                objects.append(os.path.join(class_dir, f))
    return objects

def resize_object_relative(obj_img, min_size=50, max_size=250):
    """
    Thay vì resize dựa trên scale (như 0.2 hay 1.0) của ảnh gốc (có thể làm ảnh to 4k thành 400px, 
    nhưng làm ảnh 100px thành 20px). Chúng ta sẽ resize dựa trên kích thước THỰC TẾ mong muốn
    so với khung hình 640x480.
    """
    h, w = obj_img.shape[:2]
    max_dim = max(h, w)
    
    if max_dim == 0:
        return obj_img
        
    # Chọn ngẫu nhiên độ dài lớn nhất (max_dim) mong muốn của vật thể trong khung hình
    target_max_dim = random.randint(min_size, max_size)
    
    # Tính toán tỷ lệ scale
    scale = target_max_dim / max_dim
    
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    
    return cv2.resize(obj_img, (new_w, new_h), interpolation=cv2.INTER_AREA)

def paste_object(background, object_img, x, y):
    h, w = object_img.shape[:2]
    bg_h, bg_w = background.shape[:2]
    
    # Ensure it fits (just a safety check, logic should prevent this)
    if x + w > bg_w or y + h > bg_h or x < 0 or y < 0:
        return background
        
    # Simple paste
    background[y:y+h, x:x+w] = object_img
    return background

def calculate_yolo_bbox(x, y, obj_w, obj_h, bg_w, bg_h):
    x_center = (x + obj_w / 2.0) / bg_w
    y_center = (y + obj_h / 2.0) / bg_h
    width = obj_w / bg_w
    height = obj_h / bg_h
    return x_center, y_center, width, height

def generate_dataset():
    # Setup directories
    images_dir = os.path.join(OUTPUT_DIR, "images", "train")
    labels_dir = os.path.join(OUTPUT_DIR, "labels", "train")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)
    
    # Load available backgrounds
    bg_paths = load_backgrounds(BACKGROUNDS_DIR)
    if not bg_paths:
        print(f"Error: No backgrounds found in '{BACKGROUNDS_DIR}'. Please add some images.")
        return

    # Scan classes
    classes = get_classes_from_folders(OBJECTS_DIR)
    if not classes:
        print(f"Error: No object classes found in '{OBJECTS_DIR}'.")
        return
        
    class_map = {}
    objects_by_class = {}
    
    for c in classes:
        get_or_create_class_id(c, class_map)
        objs = load_objects_from_class(OBJECTS_DIR, c)
        if objs:
            objects_by_class[c] = objs
    
    if not objects_by_class:
        print("Error: No object images found in any class folder.")
        return

    print("Generating dataset...")
    generated_count = 0
    
    for i in range(NUM_SAMPLES):
        # Pick background
        bg_path = random.choice(bg_paths)
        bg = load_image(bg_path)
        if bg is None:
            continue
            
        # Chuẩn hóa ảnh nền về cố định 640x480
        bg = cv2.resize(bg, (BG_WIDTH, BG_HEIGHT))
        bg_h, bg_w = BG_HEIGHT, BG_WIDTH
        
        # Pick random class and object
        class_name = random.choice(list(objects_by_class.keys()))
        obj_path = random.choice(objects_by_class[class_name])
        
        obj = load_image(obj_path)
        if obj is None:
            continue
            
        # Resize object dựa trên kích thước thực tế so với 640x480
        # Một vật thể sẽ có cạnh lớn nhất từ 50px đến 250px (tức là khoảng 10% đến 40% màn hình 640px)
        obj = resize_object_relative(obj, min_size=OBJ_MIN_SIZE, max_size=OBJ_MAX_SIZE)
        obj_h, obj_w = obj.shape[:2]
        
        # Ensure background is larger than object
        if obj_w >= bg_w or obj_h >= bg_h:
            continue
            
        # Pick random x, y
        max_x = bg_w - obj_w
        max_y = bg_h - obj_h
        
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)
        
        # Paste object
        composed_bg = paste_object(bg.copy(), obj, x, y)
        
        # Calculate BBox
        x_c, y_c, w_n, h_n = calculate_yolo_bbox(x, y, obj_w, obj_h, bg_w, bg_h)
        class_id = class_map[class_name]
        
        # Save image
        frame_name = f"frame_{i:04d}"
        img_out_path = os.path.join(images_dir, f"{frame_name}.jpg")
        cv2.imwrite(img_out_path, composed_bg)
        
        # Save label
        label_out_path = os.path.join(labels_dir, f"{frame_name}.txt")
        with open(label_out_path, 'w') as f:
            f.write(f"{class_id} {x_c:.6f} {y_c:.6f} {w_n:.6f} {h_n:.6f}\n")
            
        generated_count += 1
        if generated_count % 100 == 0:
            print(f"Generated {generated_count}/{NUM_SAMPLES} images...")
            
    # Generate yaml
    yaml_path = os.path.join(OUTPUT_DIR, "dataset.yaml")
    with open(yaml_path, 'w') as f:
        f.write(f"path: {os.path.abspath(OUTPUT_DIR)}\n")
        f.write("train: images/train\n")
        f.write("val: images/train\n\n")  # using train as val for simplicity in this synthetic data
        f.write("names:\n")
        for cls_name, cls_id in sorted(class_map.items(), key=lambda item: item[1]):
            f.write(f"  {cls_id}: {cls_name}\n")
            
    print("\n--- Summary ---")
    print(f"Total images generated: {generated_count}")
    print(f"Total classes discovered: {len(class_map)}")
    print(f"Class mapping: {class_map}")
    print(f"Dataset saved to: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    generate_dataset()