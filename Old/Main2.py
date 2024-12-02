from ultralytics import YOLO
import cv2

# Global değişkenler
points = []  # Geçici nokta listesi
rectangles = []  # Park alanlarını saklayan liste
image_copy = None
resize_scale = 60  # Görüntüyü yeniden boyutlandırma ölçeği (%)


def resize_image(image, scale_percent):
    """
    Verilen yüzdeyle görüntüyü yeniden boyutlandırır.
    """
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    return cv2.resize(image, (width, height))


def select_points(event, x, y, flags, param):
    """
    Kullanıcıdan fare ile park alanları için noktalar seçmesini sağlar.
    """
    global points, image_copy

    if event == cv2.EVENT_LBUTTONDOWN:  # Sol tık ile nokta ekle
        points.append((x, y))
        cv2.circle(image_copy, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Park Alanlarini Sec", image_copy)

        # 4 nokta seçildiyse bir dikdörtgen oluştur
        if len(points) == 4:
            draw_rectangle()


def draw_rectangle():
    """
    Seçilen dört noktadan bir dikdörtgen çizer ve park alanı listesine ekler.
    """
    global points, image_copy, rectangles

    # Dört nokta ile bir dikdörtgen oluştur ve görüntüye çiz
    for i in range(4):
        cv2.line(image_copy, points[i], points[(i + 1) % 4], (255, 0, 0), 2)

    # Park alanını kaydet (orijinal boyutlara geri döndürerek)
    scale_factor = 100 / resize_scale
    original_rectangle = [(int(p[0] * scale_factor), int(p[1] * scale_factor)) for p in points]
    rectangles.append(original_rectangle)
    points.clear()  # Yeni dikdörtgen için geçici noktaları temizle

    # Güncellenmiş görüntüyü göster
    cv2.imshow("Park Alanlarini Sec", image_copy)


def is_inside_rectangle(point, rectangle):
    """
    Bir noktanın bir dikdörtgenin içinde olup olmadığını kontrol eder.
    """
    x, y = point
    rect_x = [p[0] for p in rectangle]
    rect_y = [p[1] for p in rectangle]
    return min(rect_x) <= x <= max(rect_x) and min(rect_y) <= y <= max(rect_y)


def check_parking_status(image_path):
    """
    YOLOv8 modelinden gelen tahminlere göre park alanlarının doluluk durumunu kontrol eder.
    """
    global rectangles

    # YOLOv8 modelini yükle
    model = YOLO('../.venv/yolov8n.pt')
    class_car = [2, 3, 5, 7]  # Araçları temsil eden COCO sınıf ID'leri
    results = model(image_path, classes=class_car)
    result = results[0]
    vehicles = result.boxes.xyxy.cpu().numpy()  # Araçların bounding box'ları

    # Doluluk durumu
    parking_status = ["Empty"] * len(rectangles)

    # Görüntü üzerine bounding box'ları çiz ve kontrol yap
    detection_image = cv2.imread(image_path)

    for vehicle in vehicles:
        x1, y1, x2, y2 = vehicle[:4]
        vehicle_center = ((x1 + x2) / 2, (y1 + y2) / 2)  # Araç merkez noktası

        # Küçük bir kutucuk çiz (merkez odaklı)
        center_box_size = 20  # Küçük kutucuk boyutu
        cv2.rectangle(
            detection_image,
            (int(vehicle_center[0] - center_box_size / 2), int(vehicle_center[1] - center_box_size / 2)),
            (int(vehicle_center[0] + center_box_size / 2), int(vehicle_center[1] + center_box_size / 2)),
            (255, 0, 0),
            2,
        )

        for i, rectangle in enumerate(rectangles):
            if is_inside_rectangle(vehicle_center, rectangle):
                parking_status[i] = "Not Empty"
                break  # Bir araç sadece bir park alanını işgal edebilir

    # Dikdörtgenleri ve durumlarını görüntüye ekle
    for i, rectangle in enumerate(rectangles):
        color = (0, 255, 0) if parking_status[i] == "Empty" else (0, 0, 255)
        for j in range(4):
            cv2.line(detection_image, rectangle[j], rectangle[(j + 1) % 4], color, 2)
        text_position = rectangle[0]
        cv2.putText(detection_image, f"Spot {i + 1}: {parking_status[i]}",
                    text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Sonuçları göster
    cv2.imshow("Park Durumu", detection_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Kullanıcıdan park alanlarını seçmesini istemek için bir pencere aç
    image_path = "C:/Users/Nurum/Downloads/IMG_4343.jpeg"  # Görüntü yolunu yazın
    image = cv2.imread(image_path)
    if image is None:
        print("Görüntü yüklenemedi. Lütfen doğru bir yol belirtin.")
        exit()

    # İlk pencere için yeniden boyutlandırılmış görüntü
    image_resized = resize_image(image, resize_scale)
    image_copy = image_resized.copy()

    cv2.namedWindow("Park Alanlarini Sec")
    cv2.setMouseCallback("Park Alanlarini Sec", select_points)
    cv2.imshow("Park Alanlarini Sec", image_copy)

    print("Park alanlarını seçmek için 4 nokta tıklayın. Seçimi tamamlamak için 'Enter' tuşuna basın.")
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter tuşu ile park alanı seçimini tamamla
            break

    cv2.destroyAllWindows()

    # Seçilen park alanlarının durumunu kontrol et
    check_parking_status(image_path)




