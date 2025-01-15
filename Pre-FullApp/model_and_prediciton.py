#model_and_prediction.py
from ultralytics import YOLO
import numpy as np
import cv2


def get_vehicle_detections(image_path):
    """
    YOLOv8 modelinden araç bounding box'larını alır.
    """
    model = YOLO('.venv/yolov8n.pt')
    model.fuse()  # Modeli fuse ederek optimizasyonu etkinleştir

    class_car = [2, 3, 5, 7]  # Araçları temsil eden COCO sınıf ID'leri
    results = model(image_path, classes=class_car)
    result = results[0]
    return result.boxes.xyxy.cpu().numpy()


def is_inside_rectangle_for_cars(point, rectangle):
    """
    Bir noktanın bir dörtgenin içinde olup olmadığını kontrol eder.
    """
    x, y = point
    rect_pts = np.array(rectangle, dtype=np.int32)  # Dikdörtgen köşe noktaları
    if rect_pts.shape[0] != 4:
        raise ValueError("Dikdörtgenin 4 köşe noktasına sahip olması gerekir.")

    # cv2.pointPolygonTest kullanarak noktanın dörtgenin içinde olup olmadığını kontrol et
    result = cv2.pointPolygonTest(rect_pts, (x, y), False)
    return result >= 0  # Bu, bir boolean değer döndürür
