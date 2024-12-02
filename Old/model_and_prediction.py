# Model and prediction

from ultralytics import YOLO


def get_vehicle_detections(image_path):
    """
    YOLOv8 modelinden araç bounding box'larını alır.
    """
    model = YOLO('../.venv/yolov8n.pt')
    model.fuse()  # Modeli fuse ederek optimizasyonu etkinleştir

    class_car = [2, 3, 5, 7]  # Araçları temsil eden COCO sınıf ID'leri
    results = model(image_path, classes=class_car)
    result = results[0]
    return result.boxes.xyxy.cpu().numpy()


def is_inside_rectangle_for_cars(point, rectangle):
    """
    Bir noktanın bir dikdörtgenin içinde olup olmadığını kontrol eder.
    """
    x, y = point
    rect_x = [p[0] for p in rectangle]
    rect_y = [p[1] for p in rectangle]
    return min(rect_x) <= x <= max(rect_x) and min(rect_y) <= y <= max(rect_y)
