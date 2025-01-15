# parking_manager.py

import cv2
from PyQt5.QtWidgets import QMessageBox
import numpy as np
import os
import json
from dotenv import load_dotenv

from Full_app_with_live_video_and_camera_tracing.firebase_operations import FirebaseOperations


class ParkingManager:
    def __init__(self):
        self.points = []
        self.rectangles = []
        self.image = None
        self.original_image = None  # Orijinal görüntüyü saklamak için
        self.scaled_image = None
        self.SCALE_FACTOR = 0.6
        self.opencv_window_open = False # 'Park Alanlarini Sec' pencresi için bayrak
        self.analysis_image = None  # Analiz sonucunu saklamak için
        self.firebase_operations = FirebaseOperations()
        self.flag = 1 # Görüntü boyutu doğruluğu için bayrak (1 = Olumlu, 0 = Olumsuz),
        self.current_parking_type = "normal"  # Varsayılan park alanı türü

        self.analysis_results = {  # Analiz sonuçları için varsayılan değerler
            "disabled_total": 0,
            "disabled_occupied": 0,
            "outside_vehicles": 0
        }

    def validate_image_size(self):
        """
        Görüntünün boyutlarını kontrol eder ve minimum 1700x700 boyutunda olup olmadığını doğrular.
        Eğer görüntü boyutu uygun değilse bir hata mesajı gösterir ve False döner.
        """
        if self.image is None:
            QMessageBox.critical(None, "Hata", "Görüntü yüklenemedi.")
            return False

        height, width, _ = self.image.shape
        if width < 1200 or height < 700: # Minimum olması gereken görüntü boyutları
            QMessageBox.critical(None, "Hata", f"Görüntü boyutları ({width}x{height}) çok küçük. "
                                               f"Lütfen minimum 1700x700 boyutlarında bir görüntü yükleyin.")
            return False

        return True


    def set_image(self, image):
        self.image = image.copy()
        self.original_image = image.copy()

        if not self.validate_image_size():
            self.image = None
            self.original_image = None
            self.flag = 0
            return

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

        for rectangle, rect_type in self.rectangles:
            color = (255, 0, 0)  # Normal park alanı rengi (kırmızı)
            if rect_type == "disabled":
                color = (0, 255, 255)  # Engelli park alanı rengi (mavi)

            for i in range(4):
                cv2.line(display_image, rectangle[i], rectangle[(i + 1) % 4], color, 2)

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
        for rect, _ in self.rectangles:
            if self.is_point_inside_rectangle(point, rect):
                return True
        return False


    def is_point_inside_rectangle(self, point, rect):
        """
            Bir noktanın bir dikdörtgenin içinde olup olmadığını kontrol eder.
            :param point: Kontrol edilecek nokta (x, y)
            :param rect: Dikdörtgenin köşe noktaları [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        """
        x, y = point
        rect_x = [p[0] for p in rect]
        rect_y = [p[1] for p in rect]

        return min(rect_x) <= x <= max(rect_x) and min(rect_y) <= y <= max(rect_y)


    def order_rectangle_points(self, points):
        """
        Dört noktanın sırasını düzenler (sol üst, sağ üst, sağ alt, sol alt).
        """
        points = sorted(points, key=lambda p: p[1])  # Y koordinatına göre sırala
        top_points = sorted(points[:2], key=lambda p: p[0])  # Üst noktaları x'e göre sırala
        bottom_points = sorted(points[2:], key=lambda p: p[0])  # Alt noktaları x'e göre sırala
        return [top_points[0], top_points[1], bottom_points[1], bottom_points[0]]


    def start_disabled_parking_selection(self):
        """Engelli park alanı seçimini başlatır."""
        self.current_parking_type = "disabled"

        if self.image is None:
            QMessageBox.critical(None, "Hata", "Görüntü yüklenemedi.")
            return

        # Tür değiştiği için sadece `current_parking_type` güncelleniyor
        QMessageBox.information(None, "Bilgi", "Engelli park alanı seçimi aktif hale getirildi.")


    def start_parking_selection(self):
        """Park alanı seçimini başlatır."""
        self.current_parking_type = "normal"

        # Tür değiştiği için sadece `current_parking_type` güncelleniyor
        QMessageBox.information(None, "Bilgi", "Normal park alanı seçimi aktif hale getirildi.")

        if self.image is None:
            QMessageBox.critical(None, "Hata", "Görüntü yüklenemedi.")
            return

        if cv2.getWindowProperty("Park Alanlarini Sec", cv2.WND_PROP_VISIBLE) >= 1:
            #QMessageBox.information(None, "Hata", "'Park Alanlarini Sec' penceresi zaten açık.")
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

            if self.is_point_inside_any_rectangle(new_point):
                QMessageBox.warning(None, "Hata", "Bu noktaya park alanı çizilemez! Başka bir park alanının içinde.")
                return

            self.points.append(new_point)

            # Noktanın rengi park alanı türüne göre belirleniyor
            color = (0, 0, 255) if self.current_parking_type == "normal" else (255, 255, 0)
            cv2.circle(self.image, new_point, 5, color, -1)

            self.scaled_image = cv2.resize(self.image, None, fx=self.SCALE_FACTOR, fy=self.SCALE_FACTOR,
                                           interpolation=cv2.INTER_AREA)

            if len(self.points) == 4:
                self.draw_rectangle()


    def draw_rectangle(self):
        try:
            if len(self.points) == 4:
                ordered_points = self.order_rectangle_points(self.points)

                if not (ordered_points[0][1] < ordered_points[2][1] and ordered_points[0][0] < ordered_points[1][0]):
                    QMessageBox.warning(None, "Hata", "Hatalı dikdörtgen sıralaması.")
                    self.points = []
                    return

                # Dikdörtgeni park alanı türüne göre kaydet
                self.rectangles.append((ordered_points, self.current_parking_type))

                # Renk türüne göre belirleniyor
                color = (255, 0, 0) if self.current_parking_type == "normal" else (0, 255, 255)
                for i in range(4):
                    cv2.line(self.image, ordered_points[i], ordered_points[(i + 1) % 4], color, 2)

                self.points = []
                self.update_display()

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


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

            # Görüntüyü Firebase'e yükle
            if self.image is not None:
                temp_image_path = "temp_image.jpg"  # Geçici bir dosya oluşturulur
                cv2.imwrite(temp_image_path, self.image)
                self.firebase_operations.upload_file(temp_image_path, f"parking_lots/{parking_lot_name}/original_image.jpg")
                os.remove(temp_image_path)  # Geçici dosyayı kaldır

                # JSON dosyalarını Firebase'e yükle
                for i, (rectangle, rect_type) in enumerate(self.rectangles):
                    parking_spot_data = {
                        "rectangle": rectangle,
                        "type": rect_type  # "normal" veya "disabled"
                    }
                    temp_json_path = f"temp_parking_spot_{i + 1}.json"
                    with open(temp_json_path, "w") as f:
                        json.dump(parking_spot_data, f)

                    # Firebase'e yükle
                    self.firebase_operations.upload_file(temp_json_path, f"parking_lots/{parking_lot_name}/parking_spot_{i + 1}.json")
                    os.remove(temp_json_path)  # Geçici JSON dosyasını kaldır

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


    def check_parking_status(self, image=None):
        try:
            from Full_app_with_live_video_and_camera_tracing.model_and_prediciton import get_vehicle_detections, \
                is_inside_rectangle_for_cars

            if self.image is None:
                QMessageBox.critical(None, "Hata", "Görüntü yüklenemedi.")
                return

            # Analiz için görüntü seç
            image_to_process = image if image is not None else self.image.copy()

            vehicles = get_vehicle_detections(image_to_process)
            parking_status = ["Empty"] * len(self.rectangles)
            detection_image = self.image.copy()
            outside_vehicles = []  # Park alanı tanımlanmamış araçlar
            disabled_total = 0  # Engelli park alanlarının toplam sayısı
            disabled_occupied = 0  # Dolu engelli park alanlarının sayısı

            for vehicle in vehicles:
                x1, y1, x2, y2 = vehicle[:4]
                vehicle_center = ((x1 + x2) / 2, (y1 + y2) / 2)
                cv2.rectangle(detection_image, (int(vehicle_center[0] - 10), int(vehicle_center[1] - 10)),
                              (int(vehicle_center[0] + 10), int(vehicle_center[1] + 10)), (255, 0, 0), 2)

                inside_any_rectangle = False
                for i, (points, rect_type) in enumerate(self.rectangles):
                    if parking_status[i] == "Empty" and is_inside_rectangle_for_cars(vehicle_center, points):
                        parking_status[i] = "Not Empty"
                        if rect_type == "disabled":
                            disabled_occupied += 1
                        inside_any_rectangle = True
                        break

                if not inside_any_rectangle:
                    outside_vehicles.append(vehicle_center)

            # Engelli park alanlarının toplamını hesapla
            disabled_total = sum(1 for _, rect_type in self.rectangles if rect_type == "disabled")

            # Park alanlarını çizer ve durumlarını belirtir
            for i, (points, rect_type) in enumerate(self.rectangles):
                color = (0, 255, 0) if parking_status[i] == "Empty" else (0, 0, 255)
                if rect_type == "disabled":
                    color = (255, 255, 0) if parking_status[i] == "Empty" else (0, 165, 255)

                for j in range(4):
                    cv2.line(detection_image, points[j], points[(j + 1) % 4], color, 2)
                text_position = points[0]
                cv2.putText(detection_image, f"Spot {i + 1}: {parking_status[i]}",
                            text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Dışarıda kalan araçları işaretle
            for vehicle_center in outside_vehicles:
                cv2.circle(detection_image, (int(vehicle_center[0]), int(vehicle_center[1])), 10, (255, 255, 0), -1)
                cv2.putText(detection_image, "Outside", (int(vehicle_center[0]), int(vehicle_center[1] - 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            self.analysis_image = detection_image
            self.analysis_results = {
                "disabled_total": disabled_total,
                "disabled_occupied": disabled_occupied,
                "outside_vehicles": len(outside_vehicles)
            }

            # Sonuçları ekranda göster
            scaled_image = cv2.resize(detection_image, None, fx=self.SCALE_FACTOR, fy=self.SCALE_FACTOR,
                                      interpolation=cv2.INTER_AREA)
            cv2.imshow("Park Durumu", scaled_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        except Exception as e:
            import traceback
            print(f"Analiz sırasında bir hata oluştu: {traceback.format_exc()}")


    def get_analysis_result(self):
        """
        Analiz sonucu görselini döndürür.
        """
        if self.analysis_image is None:
            raise ValueError("Analiz sonucu henüz oluşturulmadı.")
        return self.analysis_image
