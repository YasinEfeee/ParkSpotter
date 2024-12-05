#parking_manager.py
import cv2
from PyQt5.QtWidgets import QMessageBox
import numpy as np
import os
import json
from firebase_uploader import FirebaseUploader
from dotenv import load_dotenv


class ParkingManager:
    def __init__(self):
        self.points = []
        self.rectangles = []
        self.image = None
        self.original_image = None  # Orijinal görüntüyü saklamak için
        self.scaled_image = None
        self.SCALE_FACTOR = 0.6
        self.opencv_window_open = False

    def set_image(self, image):
        self.image = image.copy()
        self.original_image = image.copy()
        self.scaled_image = cv2.resize(self.image, None, fx=self.SCALE_FACTOR, fy=self.SCALE_FACTOR,
                                       interpolation=cv2.INTER_AREA)


    def reset(self):
        """Tüm park alanlarını ve noktaları sıfırlar."""
        self.points = []
        self.rectangles = []
        if self.original_image is not None:
            self.image = self.original_image.copy()
            self.scaled_image = cv2.resize(self.image, None, fx=self.SCALE_FACTOR, fy=self.SCALE_FACTOR,
                                           interpolation=cv2.INTER_AREA)


    def update_display(self):
        """OpenCV penceresini günceller."""
        display_image = self.image.copy()
        for rectangle in self.rectangles:
            for i in range(4):
                cv2.line(display_image, rectangle[i], rectangle[(i + 1) % 4], (255, 0, 0), 2)
        for point in self.points:
            cv2.circle(display_image, point, 5, (0, 0, 255), -1)

        self.scaled_image = cv2.resize(display_image, None, fx=self.SCALE_FACTOR, fy=self.SCALE_FACTOR,
                                       interpolation=cv2.INTER_AREA)
        cv2.imshow("Park Alanlarini Sec", self.scaled_image)


    def remove_last_point(self):
        """Son eklenen noktayı siler ve görüntüyü günceller."""
        if self.points:
            self.points.pop()
            print("Son nokta silindi.")
            # Görüntüyü yeniden işleyerek noktayı kaldır
            self.image = self.original_image.copy()
            self.update_display()
        else:
            print("Silinecek nokta yok.")


    def remove_last_rectangle(self):
        """Son eklenen park alanını siler ve görüntüyü günceller."""
        if self.rectangles:
            self.rectangles.pop()
            print("Son park alanı silindi.")
            # Görüntüyü yeniden işleyerek park alanını kaldır
            self.image = self.original_image.copy()
            self.update_display()
        else:
            print("Silinecek park alanı yok.")


    def is_point_inside_any_rectangle(self, point):
        """Bir noktanın mevcut dikdörtgenlerin herhangi birinin içinde olup olmadığını kontrol eder."""
        for rect in self.rectangles:
            if self.is_point_inside_rectangle(point, rect):
                return True
        return False


    def is_point_inside_rectangle(self, point, rectangle):
        """Bir noktanın belirli bir dikdörtgenin içinde olup olmadığını kontrol eder."""
        x, y = point
        rect_x = [p[0] for p in rectangle]
        rect_y = [p[1] for p in rectangle]
        return min(rect_x) <= x <= max(rect_x) and min(rect_y) <= y <= max(rect_y)


    def order_rectangle_points(self, points):
        """
        Dört noktanın sırasını düzenler (sol üst, sağ üst, sağ alt, sol alt).
        """
        points = sorted(points, key=lambda p: p[1])  # Y koordinatına göre sırala
        top_points = sorted(points[:2], key=lambda p: p[0])  # Üst noktaları x'e göre sırala
        bottom_points = sorted(points[2:], key=lambda p: p[0])  # Alt noktaları x'e göre sırala
        return [top_points[0], top_points[1], bottom_points[1], bottom_points[0]]


    def start_parking_selection(self):
        if self.image is None:
            QMessageBox.critical(None, "Hata", "Görüntü yüklenemedi.")
            return

        if cv2.getWindowProperty("Park Alanlarini Sec", cv2.WND_PROP_VISIBLE) >= 1:
            QMessageBox.information(None, "Hata", "'Park Alanlarini Sec' penceresi zaten açık.")
            return

        cv2.namedWindow("Park Alanlarini Sec")
        cv2.setMouseCallback("Park Alanlarini Sec", self.select_points)

        self.opencv_window_open = True  # Pencerenin açık olduğunu işaretle

        while self.opencv_window_open:
            self.update_display()
            key = cv2.waitKey(1) & 0xFF
            if not self.opencv_window_open:
                break

        cv2.destroyAllWindows()
        self.opencv_window_open = False  # Pencerenin kapandığını işaretle


    def select_points(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            real_x = int(x / self.SCALE_FACTOR)
            real_y = int(y / self.SCALE_FACTOR)
            new_point = (real_x, real_y)

            # Noktanın başka bir dikdörtgenin içinde olup olmadığını kontrol et
            if self.is_point_inside_any_rectangle(new_point):
                QMessageBox.warning(None, "Hata", "Bu noktaya park alanı çizilemez! Başka bir park alanının içinde.")
                return

            # Noktayı ekle ve güncelle
            self.points.append(new_point)
            cv2.circle(self.image, new_point, 5, (0, 0, 255), -1)
            self.scaled_image = cv2.resize(self.image, None, fx=self.SCALE_FACTOR, fy=self.SCALE_FACTOR,
                                           interpolation=cv2.INTER_AREA)

            if len(self.points) == 4:
                self.draw_rectangle()


    def draw_rectangle(self):
        if len(self.points) == 4:
            # Noktaları sırala ve dikdörtgen oluştur
            ordered_points = self.order_rectangle_points(self.points)

            # Geçerlilik kontrolü
            if not (ordered_points[0][1] < ordered_points[2][1] and ordered_points[0][0] < ordered_points[1][0]):
                QMessageBox.warning(None, "Hata", "Hatalı dikdörtgen sıralaması.")
                self.points = []
                return

            self.rectangles.append(ordered_points)
            for i in range(4):
                cv2.line(self.image, ordered_points[i], ordered_points[(i + 1) % 4], (255, 0, 0), 2)

            self.points = []
            self.update_display()


    '''def save_parking_data(self, image_path):
        """
        Park alanlarını ve seçilen dikdörtgenleri belirtilen klasör yapısında kaydeder.
        """
        try:
            if len(self.rectangles) < 1:
                QMessageBox.warning(None, "Uyarı", "En az bir park alanı seçmelisiniz.")
                return

            # Ana klasörü oluştur
            base_dir = "data_base"
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)

            # Yeni bir park alanı için klasör oluştur
            parking_lot_count = len(os.listdir(base_dir)) + 1
            parking_lot_dir = os.path.join(base_dir, f"parking_lot_{parking_lot_count}")
            os.makedirs(parking_lot_dir, exist_ok=True)

            # Görüntüyü kaydet
            image_name = "original_image.jpg"
            saved_image_path = os.path.join(parking_lot_dir, image_name)
            if not cv2.imwrite(saved_image_path, self.image):
                raise Exception(f"Görüntü {saved_image_path} yoluna kaydedilemedi.")

            # Her dikdörtgeni ayrı bir JSON dosyası olarak kaydet
            for i, rect in enumerate(self.rectangles):
                spot_dir = os.path.join(parking_lot_dir, f"parking_spot_{i + 1}.json")
                parking_spot_data = {
                    "spot_id": i + 1,
                    "coordinates": rect
                }
                with open(spot_dir, "w") as json_file:
                    json.dump(parking_spot_data, json_file, indent=4)

            QMessageBox.information(None, "Başarılı", f"Park alanı {parking_lot_dir} klasörüne kaydedildi.")
        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)
            QMessageBox.critical(None, "Kaydetme Hatası", error_message)'''

    def upload_to_firebase(self, parking_lot_name):
        """
        Park alanlarını sadece Firebase'e yükler.
        :param parking_lot_name: Firebase'de kullanılacak park alanı klasör adı.
        """
        try:
            # Ortam değişkeninden bucket_name alınır
            load_dotenv()  # .env dosyasını yükle
            bucket_name = os.getenv("FIREBASE_BUCKET")

            if not bucket_name:
                raise ValueError("Firebase bucket adı belirtilmemiş.")

            uploader = FirebaseUploader(bucket_name)

            # Görüntüyü Firebase'e yükle
            if self.image is not None:
                temp_image_path = "temp_image.jpg"  # Geçici bir dosya oluşturulur
                cv2.imwrite(temp_image_path, self.image)
                uploader.upload_file(temp_image_path, f"parking_lots/{parking_lot_name}/original_image.jpg")
                os.remove(temp_image_path)  # Geçici dosyayı kaldır

            # JSON dosyalarını Firebase'e yükle
            for i, rect in enumerate(self.rectangles):
                parking_spot_data = {"rectangle": rect}
                temp_json_path = f"temp_parking_spot_{i + 1}.json"
                with open(temp_json_path, "w") as f:
                    json.dump(parking_spot_data, f)

                uploader.upload_file(temp_json_path, f"parking_lots/{parking_lot_name}/parking_spot_{i + 1}.json")
                os.remove(temp_json_path)  # Geçici JSON dosyasını kaldır

            QMessageBox.Information(None, Başarılı, "Park alanı {parking_lot_name}, Firebase'e başarıyla yüklendi.")

        except Exception as e:
            print(f"Hata: {e}")


    def check_parking_status(self, image_path):
        from model_and_prediciton import get_vehicle_detections, is_inside_rectangle_for_cars

        if self.image is None:
            QMessageBox.critical(None, "Hata", "Görüntü yüklenemedi.")
            return

        vehicles = get_vehicle_detections(image_path)
        parking_status = ["Empty"] * len(self.rectangles)
        detection_image = self.image.copy()
        outside_vehicles = []  # Park alanı tanımlanmamış araçlar

        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle[:4]
            vehicle_center = ((x1 + x2) / 2, (y1 + y2) / 2)
            cv2.rectangle(detection_image, (int(vehicle_center[0] - 10), int(vehicle_center[1] - 10)),
                          (int(vehicle_center[0] + 10), int(vehicle_center[1] + 10)), (255, 0, 0), 2)

            inside_any_rectangle = False  # Araç herhangi bir park alanında mı?
            for i, rectangle in enumerate(self.rectangles):
                if parking_status[i] == "Empty" and is_inside_rectangle_for_cars(vehicle_center, rectangle):
                    parking_status[i] = "Not Empty"
                    inside_any_rectangle = True
                    break

            if not inside_any_rectangle:
                outside_vehicles.append(vehicle_center)

        # Park alanlarını çizer ve durumlarını belirtir
        for i, rectangle in enumerate(self.rectangles):
            color = (0, 255, 0) if parking_status[i] == "Empty" else (0, 0, 255)
            for j in range(4):
                cv2.line(detection_image, rectangle[j], rectangle[(j + 1) % 4], color, 2)
            text_position = rectangle[0]
            cv2.putText(detection_image, f"Spot {i + 1}: {parking_status[i]}",
                        text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Dışarıda kalan araçları işaretle
        for vehicle_center in outside_vehicles:
            cv2.circle(detection_image, (int(vehicle_center[0]), int(vehicle_center[1])), 10, (255, 255, 0), -1)
            cv2.putText(detection_image, "Outside", (int(vehicle_center[0]), int(vehicle_center[1] - 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        # Sonuçları ekranda göster
        scaled_image = cv2.resize(detection_image, None, fx=self.SCALE_FACTOR, fy=self.SCALE_FACTOR,
                                  interpolation=cv2.INTER_AREA)

        cv2.imshow("Park Durumu", scaled_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
