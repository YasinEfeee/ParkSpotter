import cv2
import sys
import os
import json
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox, QComboBox, QInputDialog
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon
from PyQt5.QtCore import QTimer, Qt

from Full_app_with_live_video_and_camera_tracing.firebase_operations import FirebaseOperations
from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_BaseWindow import BaseWindow


class CameraParkingStatusWindow(BaseWindow):
    # Sınıf düzeyinde değişken tanımı
    parking_data = None

    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Kamera Üzerinden Park Alanı Analizi")
            self.setFixedSize(1100, 700)

            # Ana widget
            main_widget = QWidget(self)
            self.setCentralWidget(main_widget)

            # Firebase bağlantısı
            self.firebase = FirebaseOperations()
            self.parking_data = {}
            self.current_parking_spots = []
            self.cap = None
            self.flag_for_GUI = False

            self.analysis_results = { # Analiz sonuçları için varsayılan değerler
                "disabled_total": 0,
                "disabled_occupied": 0,
                "outside_vehicles": 0,
                "total_parking_spots": 0,
                "total_occupied": 0,
                "parking_status": 0
            }

            # Ana pencere ve alt widget'lara stil uygulama
            main_widget.setStyleSheet("""
                QWidget {
                    background-color: #242423;
                    color: #D8DEE9;
                }
                QPushButton {
                    background-color: #333533;
                    color: #ECEFF4;
                    border: 0.5px solid #717271;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4E504E;
                    color: #ECEFF4;
                }
                QPushButton:disabled {
                    background-color: #1C1C1C;
                    color: #5A5A5A;
                    border: 0.5px solid #717271;
                }
                QLabel {
                    color: #D8DEE9;
                    font-size: 14px;
                }
                QLabel#title {
                    font-size: 20px;  
                    color: #D8DEE9;
                }
            """)

            # Pop-up'lar için varsayılan stil uygulaması
            self.setStyleSheet("""
                QDialog {
                    background-color: #f0f0f0;
                    color: black;
                }
            """)

            # Ok simgesi ile geri butonu
            self.back_button = QPushButton("", main_widget)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(base_dir)
            icon_path = os.path.join(project_root, "ImagesForGUI/back-arrow-icon.png")
            self.back_button.setIcon(QIcon(icon_path))
            self.back_button.setGeometry(10, 10, 40, 40)
            self.back_button.setStyleSheet("border: none;")
            self.back_button.clicked.connect(self.go_back)

            # Başlık
            self.title_label = QLabel("- Kamera Üzerinden Park Alanı Analizi -", main_widget)
            self.title_label.setFont(QFont("Open Sans", 12, QFont.Bold))
            self.title_label.setObjectName("title")
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setGeometry(300, 20, 500, 40)

            # Kamera görüntüleme QLabel (sağ tarafa taşındı)
            self.camera_label = QLabel(main_widget)
            self.camera_label.setGeometry(400, 100, 650, 500)
            self.camera_label.setAlignment(Qt.AlignCenter)
            self.camera_label.setStyleSheet("border: 2px solid #333533;")

            # Butonlar (sol tarafa hizalandı)
            self.select_camera_button = QPushButton("Kamera Seç", main_widget)
            self.select_camera_button.setFont(QFont("Open Sans", 10))
            self.select_camera_button.setGeometry(50, 100, 300, 40)
            self.select_camera_button.clicked.connect(self.select_camera)

            self.camera_status_label = QLabel("Henüz bir kamera seçilmedi.", main_widget)
            self.camera_status_label.setGeometry(50, 160, 300, 40)
            self.camera_status_label.setAlignment(Qt.AlignCenter)

            self.parking_lot_combo = QComboBox(main_widget)
            self.parking_lot_combo.setGeometry(50, 220, 300, 40)
            self.parking_lot_combo.addItem("Park Alanı Seçin")
            self.parking_lot_combo.setEnabled(False)

            self.load_parking_button = QPushButton("Park Alanlarını Yükle", main_widget)
            self.load_parking_button.setFont(QFont("Open Sans", 10))
            self.load_parking_button.setGeometry(50, 280, 300, 40)
            self.load_parking_button.clicked.connect(self.load_parking_data)
            self.load_parking_button.setEnabled(False)

            self.start_analysis_button = QPushButton("Analizi Başlat", main_widget)
            self.start_analysis_button.setFont(QFont("Open Sans", 10))
            self.start_analysis_button.setGeometry(50, 340, 300, 40)
            self.start_analysis_button.clicked.connect(self.start_analysis)
            self.start_analysis_button.setEnabled(False)

            # Engelli park alanındaki araç sayısını gösteren kutu
            self.disabled_count_label = QLabel("Engelli Park Doluluk: 0/0", main_widget)
            self.disabled_count_label.setFont(QFont("Open Sans", 10))
            self.disabled_count_label.setGeometry(50, 400, 300, 40)
            self.disabled_count_label.setAlignment(Qt.AlignCenter)
            self.disabled_count_label.setStyleSheet("""
                border: 2px solid #333533;
                color: #ECEFF4;
                background-color: #242423;
                font-size: 14px;
                font-weight: bold;
            """)

            # Dışarıda kalan araç sayısını gösteren kutu
            self.outside_count_label = QLabel("Dışarıda Kalan Araç: 0", main_widget)
            self.outside_count_label.setFont(QFont("Open Sans", 10))
            self.outside_count_label.setGeometry(50, 450, 300, 40)
            self.outside_count_label.setAlignment(Qt.AlignCenter)
            self.outside_count_label.setStyleSheet("""
                border: 2px solid #333533;
                color: #ECEFF4;
                background-color: #242423;
                font-size: 14px;
                font-weight: bold;
            """)

            # Toplam park alanı doluluğu sayısını gösteren kutu
            self.total_car_label = QLabel("Park Alanları Doluluk: 0/0", main_widget)
            self.total_car_label.setFont(QFont("Open Sans", 10))
            self.total_car_label.setGeometry(50, 500, 300, 40)
            self.total_car_label.setAlignment(Qt.AlignCenter)
            self.total_car_label.setStyleSheet("""
                            border: 2px solid #333533;
                            color: #ECEFF4;
                            background-color: #242423;
                            font-size: 14px;
                            font-weight: bold;
                        """)

            self.finish_analyse_button = QPushButton("Analizi Bitir", main_widget)
            self.finish_analyse_button.setFont(QFont("Open Sans", 10))
            self.finish_analyse_button.setGeometry(50, 560, 300, 40)
            self.finish_analyse_button.clicked.connect(self.finish_analyse)
            self.finish_analyse_button.setEnabled(False)

            # Sağ alt köşeye yapımcı adı
            self.credits_label = QLabel("Created by - YasinEfeee", main_widget)
            self.credits_label.setFont(QFont("Arial", 8))
            self.credits_label.setAlignment(Qt.AlignRight)
            self.credits_label.setGeometry(900, 670, 180, 20)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_camera_frame)

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


    def update_parking_info(self):
        """
        Engelli park alanlarının doluluk oranını, dışarıda kalan araçların sayısını ve toplam park alanı doluluğunu günceller.
        """
        try:
            # Analiz sonuçlarını alın
            results = self.analysis_results
            if not isinstance(results, dict):
                raise ValueError("self.analysis_results bir dict olmalıdır.")

            # Gerekli bilgileri alın
            disabled_total = results.get("disabled_total", 0)
            disabled_occupied = results.get("disabled_occupied", 0)
            outside_vehicles = results.get("outside_vehicles", 0)
            total_parking_spots = results.get("total_parking_spots", 0)
            total_occupied = results.get("total_occupied", 0)

            # QLabel'leri güncelleyin
            self.disabled_count_label.setText(f"Engelli Park Doluluk: {disabled_occupied}/{disabled_total}")
            self.outside_count_label.setText(f"Dışarıda Kalan Araç: {outside_vehicles}")
            self.total_car_label.setText(f"Park Alanları Doluluk: {total_occupied}/{total_parking_spots}")

            # Konsola çıktı
            print(f"Engelli Park Doluluk: {disabled_occupied}/{disabled_total}")
            print(f"Dışarıda Kalan Araç: {outside_vehicles}")
            print(f"Park Alanları Doluluk: {total_occupied}/{total_parking_spots}")

        except Exception as e:
            print(f"Parking info update failed: {e}")


    def validate_camera_aspect_ratio(self, selected_lot):
        """
        Kameranın genişlik-yükseklik oranını kontrol eder ve seçilen park alanının oranlarıyla uyumluluğunu doğrular.
        Büyük bir uyuşmazlık varsa kullanıcıya devam etme seçeneği sunar.
        """
        try:
            # Orijinal park alanı çözünürlüğünü Firebase'den al
            original_width, original_height = self.get_original_image_resolution(selected_lot)
            if original_width is None or original_height is None:
                QMessageBox.critical(self, "Hata", "Orijinal park alanı çözünürlüğü alınamadı.")
                return False

            # Kamera çözünürlüğünü al
            if self.cap is None or not self.cap.isOpened():
                QMessageBox.critical(self, "Hata", "Kamera açık değil.")
                return False

            camera_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            camera_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Çözünürlükleri kontrol et
            print(
                f"Original Resolution: {original_width}x{original_height}, Camera Resolution: {camera_width}x{camera_height}")


            if original_width != camera_width or original_height != camera_height:
                QMessageBox.critical(
                    self,
                    "Çözünürlük Uyumsuzluğu",
                    f"Seçilen Kamera çözünürlüğü ({camera_width}x{camera_height}), park alanı çözünürlüğü ({original_width}x{original_height}) ile eşleşmiyor. Lütfen uygun bir video seçin."
                )
                return False

            return True

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)
            QMessageBox.critical(self, "Hata", "Oran kontrolü sırasında bir hata oluştu.")
            return False


    def select_camera(self):
        """
        Kullanıcıdan bir kamera seçmesini ister.
        """
        try:
            camera_index, ok = QInputDialog.getInt(self, "Kamera Seçimi", "Kamera numarasını girin (0-5):", min=0, max=5)
            if ok:
                self.cap = cv2.VideoCapture(camera_index)
                if not self.cap.isOpened():
                    QMessageBox.critical(self, "Hata", "Kamera açılamadı.")
                    return
                self.camera_status_label.setText(f"Seçilen Kamera: {camera_index}")
                self.load_parking_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kamera seçimi sırasında bir hata oluştu:\n{e}")


    def load_parking_data(self):
        """
        Firebase'den park alanı verilerini yükler ve ComboBox'a ekler.
        """
        try:
            if CameraParkingStatusWindow.parking_data is None:
                # Firebase'den verileri yükleyin
                CameraParkingStatusWindow.parking_data = self.firebase.fetch_parking_lots()

            # ComboBox'u doldur
            self.parking_lot_combo.clear()
            self.parking_lot_combo.addItem("Park Alanı Seçin")
            for lot_name in CameraParkingStatusWindow.parking_data:
                self.parking_lot_combo.addItem(lot_name)

            self.parking_lot_combo.setEnabled(True)
            self.start_analysis_button.setEnabled(True)
            QMessageBox.information(self, "Başarılı", "Park alanları başarıyla yüklendi.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Park alanları yüklenirken hata oluştu:\n{e}")
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


    def get_original_image_resolution(self, selected_lot):
        """
        Firebase'den orijinal park alanı görüntüsünün çözünürlüğünü alır.
        """
        try:
            # Firebase'den blob adı
            blob_name = f"parking_lots/{selected_lot}/original_image.jpg"
            blob = self.firebase.bucket.blob(blob_name)

            if not blob.exists():
                raise FileNotFoundError(f"Firebase'de {blob_name} bulunamadı.")

            # Geçici olarak dosyayı indir
            temp_file = "temp_original_image.jpg"
            blob.download_to_filename(temp_file)

            # OpenCV ile çözünürlüğü al
            image = cv2.imread(temp_file)
            if image is None:
                raise ValueError("İndirilen görüntü okunamadı.")

            height, width, _ = image.shape

            # Geçici dosyayı temizle
            os.remove(temp_file)

            return width, height

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)
            return None, None


    def start_analysis(self):
        """
        Kameradan gelen görüntüde park alanlarını analiz eder.
        """
        try:
            selected_lot = self.parking_lot_combo.currentText()

            # Kullanıcının park alanı seçip seçmediğini kontrol edin
            if selected_lot == "Park Alanı Seçin":
                QMessageBox.warning(self, "Uyarı", "Lütfen bir park alanı seçin.")
                return

            # Seçilen park alanının `parking_data` içinde olup olmadığını kontrol edin
            if selected_lot not in CameraParkingStatusWindow.parking_data:
                QMessageBox.critical(self, "Hata", "Seçilen park alanı bulunamadı. Verileri yeniden yükleyin.")
                return

            # Kamera kontrolü
            if self.cap is None or not self.cap.isOpened():
                QMessageBox.critical(self, "Hata", "Kamera açık değil.")
                return

            # Park alanı bilgilerini `current_parking_spots` değişkenine atayın
            self.current_parking_spots = CameraParkingStatusWindow.parking_data[selected_lot].get("spots", [])

            # Eğer `spots` boşsa kullanıcıya bilgi verin
            if not self.current_parking_spots:
                QMessageBox.warning(self, "Uyarı", "Seçilen park alanı için koordinat bulunamadı.")
                return

            # Kamera oranlarının doğrulanması
            if not self.validate_camera_aspect_ratio(selected_lot):
                return

            QMessageBox.information(self, "Başarılı", f"'{selected_lot}' park alanı seçildi.")

            self.timer.start(30)
            self.start_analysis_button.setEnabled(False)
            self.select_camera_button.setEnabled(False)
            self.load_parking_button.setEnabled(False)
            self.finish_analyse_button.setEnabled(True)

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


    def update_camera_frame(self):
        """
        Kameradan gelen görüntüyü günceller ve analiz eder.
        """
        try:
            ret, frame = self.cap.read()
            if not ret:
                QMessageBox.information(self, "Bilgi", "Kamera bağlantısı sona erdi.")
                self.timer.stop()
                return

            # QLabel boyutlarını al
            label_width = self.camera_label.width()
            label_height = self.camera_label.height()

            # Kamera oranlarını koruyarak yeniden boyutlandır
            frame_height, frame_width, _ = frame.shape
            scale = min(label_width / frame_width, label_height / frame_height)
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

            # Araç tanıma ve analiz işlemi
            self.analyze_parking_status(resized_frame, frame_width, frame_height, new_width, new_height)

            # QLabel üzerinde görüntüyü göster
            rgb_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image).scaled(label_width, label_height, Qt.KeepAspectRatio)
            self.camera_label.setPixmap(pixmap)

            self.update_parking_info()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kamera görüntüsü güncellenirken bir hata oluştu:\n{e}")


    def finish_analyse(self):
        """
        Analizi sonlandırır ve yeni analiz icin hazir hale getirir.
        """
        try:
            # Eğer bir kamera açıksa, durdur ve kaynakları serbest bırak
            if self.cap and self.cap.isOpened():
                self.timer.stop()
                self.cap.release()

            # Video ve QLabel temizliği
            self.camera_label.clear()
            self.camera_status_label.setText("Henüz bir kamera seçilmedi.")

            # Butonların durumlarını yeniden ayarla
            self.load_parking_button.setEnabled(False)
            self.start_analysis_button.setEnabled(False)
            self.parking_lot_combo.setEnabled(False)
            self.select_camera_button.setEnabled(True)

            # Kullanıcıya bilgi mesajı
            QMessageBox.information(self, "Bilgi", "Analiz sona erdi. Yeni bir kamera ve park alanı seçebilirsiniz.")

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)
            QMessageBox.critical(self, "Hata", "Analizi sonlandırırken bir hata oluştu.")


    def analyze_parking_status(self, frame, original_width, original_height, new_width, new_height):
        """
        Araçları tanır ve park alanlarının durumlarını analiz eder.
        Kamera çerçevesi QLabel boyutlarına ölçeklenir.
        """
        try:
            from Full_app_with_live_video_and_camera_tracing.model_and_prediciton import (
                get_vehicle_detections, is_inside_rectangle_for_cars
            )

            # Ölçek faktörlerini hesapla
            scale_x = new_width / original_width
            scale_y = new_height / original_height

            # YOLOv8 ile araç algıla
            detections = get_vehicle_detections(frame)

            # Park alanı durumları
            parking_status = ["Empty"] * len(self.current_parking_spots)
            outside_vehicles = []
            disabled_total = 0
            disabled_occupied = 0
            total_parking_spots = len(self.current_parking_spots)
            total_occupied = 0

            for detection in detections:
                x1, y1, x2, y2 = map(int, detection[:4])  # Bounding box
                vehicle_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                cv2.circle(frame, vehicle_center, 5, (255, 0, 0), -1)  # Araç merkezine işaret koy

                inside_any_rectangle = False
                for i, spot in enumerate(self.current_parking_spots):
                    rectangle = [
                        (int(pt[0] * scale_x), int(pt[1] * scale_y)) for pt in spot["rectangle"]
                    ]
                    rect_type = spot.get("type", "normal")  # Normal veya engelli park alanı

                    # Araç park alanı içindeyse
                    if is_inside_rectangle_for_cars(vehicle_center, rectangle):
                        if parking_status[i] == "Empty":
                            parking_status[i] = "Not Empty"
                            total_occupied += 1  # Doluluk sayısını artır
                            if rect_type == "disabled":
                                disabled_occupied += 1
                            inside_any_rectangle = True
                            break

                if not inside_any_rectangle:
                    outside_vehicles.append(vehicle_center)

            # Engelli park alanlarının toplamını hesapla
            disabled_total = sum(1 for spot in self.current_parking_spots if spot.get("type") == "disabled")

            # Park alanlarını çiz ve durumları ekle
            for i, spot in enumerate(self.current_parking_spots):
                rectangle = [
                    (int(pt[0] * scale_x), int(pt[1] * scale_y)) for pt in spot["rectangle"]
                ]
                rect_type = spot.get("type", "normal")
                color = (0, 255, 0) if parking_status[i] == "Empty" else (0, 0, 255)
                if rect_type == "disabled":
                    color = (255, 255, 0) if parking_status[i] == "Empty" else (0, 165, 255)

                for j in range(4):
                    cv2.line(frame, rectangle[j], rectangle[(j + 1) % 4], color, 2)
                cv2.putText(frame, f"Spot {i + 1}: {parking_status[i]}", rectangle[0],
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Dışarıda kalan araçları işaretle
            for vehicle_center in outside_vehicles:
                cv2.circle(frame, (int(vehicle_center[0]), int(vehicle_center[1])), 10, (255, 255, 0), -1)
                cv2.putText(frame, "Outside", (int(vehicle_center[0]), int(vehicle_center[1] - 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            # Analiz sonuçlarını kaydet
            self.analysis_results = {
                "disabled_total": disabled_total,
                "disabled_occupied": disabled_occupied,
                "outside_vehicles": len(outside_vehicles),
                "total_parking_spots": total_parking_spots,
                "total_occupied": total_occupied,
                "parking_status": parking_status
            }

        except Exception as e:
            import traceback
            print(f"Hata oluştu: {e}\n{traceback.format_exc()}")


    def go_back(self):
        """
        Geri butonuna basıldığında ana menüye döner.
        """
        try:
            reply = QMessageBox.question(
                self,
                "Çıkış Onayı",
                "Park alanı yönetim menüsüne dönmek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.flag_for_GUI = True
                # Ana menüye geçiş
                from Full_app_with_live_video_and_camera_tracing.GUI_Displaying_Parking_Status.GUI_CheckParkingStatus import CheckParkingStatus  # Lazy import
                self.CheckParkingStatus = CheckParkingStatus()

                # Yeni pencereyi göster ve mevcut pencereyi kapat
                self.CheckParkingStatus.show()
                self.close()

            else:
                # Hiçbir işlem yapılmaz
                pass

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)
            QMessageBox.critical(self, "Hata", "Geri dönüş işlemi sırasında bir hata oluştu.")


    def closeEvent(self, event):
        """
        Pencere kapatılmadan önce yapılacak işlemler.
        """
        try:
            if self.flag_for_GUI:
                if self.cap and self.cap.isOpened():
                    self.cap.release()
                if self.timer.isActive():
                    self.timer.stop()

            else:
                if self.cap and self.cap.isOpened():
                    self.cap.release()
                if self.timer.isActive():
                    self.timer.stop()
                # Kullanıcıdan kapatma onayı alın
                reply = QMessageBox.question(
                    self,
                    "Çıkış Onayı",
                    "Pencereyi kapatmak istediğinize emin misiniz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:

                    # Kapatma işlemini onayla
                    event.accept()

                    from Full_app_with_live_video_and_camera_tracing.GUI_Displaying_Parking_Status.GUI_CheckParkingStatus import \
                        CheckParkingStatus  # Lazy import

                    self.checkParking_status = CheckParkingStatus()
                    # Yeni pencereyi göster ve mevcut pencereyi kapat
                    self.checkParking_status.show()
                    self.close()

                else:
                    # Kapatma işlemini iptal et
                    event.ignore()

        except Exception as e:
            import traceback
            print(f"Hata oluştu: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Hata", "Kapatma işlemi sırasında bir hata oluştu.")
            event.ignore()
