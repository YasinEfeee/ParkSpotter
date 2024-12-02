# Parking Statues

import cv2

points = []  # Geçici nokta listesi
rectangles = []  # Park alanlarını saklayan liste
SCALE_FACTOR = 0.6  # Ekran küçültme oranı


def is_point_inside_any_rectangle(point):
    """
    Bir noktanın mevcut dikdörtgenlerin herhangi birinin içinde olup olmadığını kontrol eder.
    """
    global rectangles
    for rect in rectangles:
        if is_inside_rectangle_for_points(point, rect):
            return True
    return False


def is_inside_rectangle_for_points(point, rectangle):
    """
    Bir noktanın bir dikdörtgenin içinde olup olmadığını kontrol eder.
    """
    x, y = point
    rect_x = [p[0] for p in rectangle]
    rect_y = [p[1] for p in rectangle]
    return min(rect_x) <= x <= max(rect_x) and min(rect_y) <= y <= max(rect_y)


def select_points(event, x, y, flags, param):
    """
    Kullanıcıdan fare ile park alanları için noktalar seçmesini sağlar.
    """
    global points, rectangles
    image_copy = param

    if event == cv2.EVENT_LBUTTONDOWN:  # Sol tık ile nokta ekle
        # Tıklanan noktaları gerçek boyutlara dönüştür
        real_x = int(x / SCALE_FACTOR)
        real_y = int(y / SCALE_FACTOR)

        # Eğer nokta başka bir dikdörtgenin içindeyse eklenmesin ve uyarı verilsin
        if is_point_inside_any_rectangle((real_x, real_y)):
            print("Bu noktaya park alanı çizilemez! Başka bir park alanının içinde.")
            return

        # Noktayı geçici listeye ekle
        points.append((real_x, real_y))
        cv2.circle(image_copy, (real_x, real_y), 5, (0, 0, 255), -1)

        # Küçük pencere boyutunda güncellenmiş görüntü göster
        scaled_image = cv2.resize(image_copy, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR, interpolation=cv2.INTER_AREA)
        cv2.imshow("Park Alanlarini Sec", scaled_image)

        # Eğer 4 nokta seçildiyse
        if len(points) == 4:
            # Seçilen noktalar bir dikdörtgen oluşturuyor mu?
            rect_x = [p[0] for p in points]
            rect_y = [p[1] for p in points]

            if not (min(rect_x) < max(rect_x) and min(rect_y) < max(rect_y)):
                print("Geçersiz dikdörtgen seçimi. Lütfen noktaları düzgün bir sırada seçin.")
                points.clear()  # Hatalı seçimleri temizle
                return

            # Geçerliyse dikdörtgeni oluştur
            draw_rectangle(image_copy)


def order_rectangle_points(points):
    """
    Dört noktanın sırasını düzenler (sol üst, sağ üst, sağ alt, sol alt).
    """
    points = sorted(points, key=lambda p: p[1])  # Önce y koordinatına göre sırala
    top_points = sorted(points[:2], key=lambda p: p[0])  # Üst noktaları x'e göre sırala
    bottom_points = sorted(points[2:], key=lambda p: p[0])  # Alt noktaları x'e göre sırala
    return [top_points[0], top_points[1], bottom_points[1], bottom_points[0]]


def draw_rectangle(image_copy):
    """
    Seçilen dört noktadan bir dikdörtgen çizer ve park alanı listesine ekler.
    """
    global points, rectangles

    # Dört nokta sırasını düzenle
    ordered_points = order_rectangle_points(points)

    # Dikdörtgeni çiz
    for i in range(4):
        cv2.line(image_copy, ordered_points[i], ordered_points[(i + 1) % 4], (255, 0, 0), 2)

    # Park alanını kaydet
    rectangles.append(ordered_points.copy())
    points.clear()  # Yeni dikdörtgen için geçici noktaları temizle

    # Güncellenmiş görüntüyü %60 küçült ve göster
    scaled_image = cv2.resize(image_copy, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
    cv2.imshow("Park Alanlarini Sec", scaled_image)



def check_parking_status(image_path):
    """
    YOLOv8 modelinden gelen tahminlere göre park alanlarının doluluk durumunu kontrol eder.
    """
    from model_and_prediction import get_vehicle_detections, is_inside_rectangle_for_cars

    global rectangles

    # Araçların bounding box'larını al
    vehicles = get_vehicle_detections(image_path)
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

        assigned = False  # Aracın bir park alanına atanıp atanmadığını kontrol et
        for i, rectangle in enumerate(rectangles):
            if not assigned and parking_status[i] == "Empty" and is_inside_rectangle_for_cars(vehicle_center, rectangle):
                parking_status[i] = "Not Empty"
                assigned = True  # Aracı yalnızca bir park alanına ata

        # Eğer araç hiçbir park alanına atanamadıysa, durum yazdır (debug için)
        if not assigned:
            print(f"Bu araç hiçbir park alanına atanamadı: {vehicle_center}")

    # Dikdörtgenleri ve durumlarını görüntüye ekle
    for i, rectangle in enumerate(rectangles):
        color = (0, 255, 0) if parking_status[i] == "Empty" else (0, 0, 255)
        for j in range(4):
            cv2.line(detection_image, rectangle[j], rectangle[(j + 1) % 4], color, 2)
        text_position = rectangle[0]
        cv2.putText(detection_image, f"Spot {i + 1}: {parking_status[i]}",
                    text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Sonuçları %60 küçültülmüş şekilde göster
    scaled_image = cv2.resize(detection_image, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR, interpolation=cv2.INTER_AREA)
    cv2.imshow("Park Durumu", scaled_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()