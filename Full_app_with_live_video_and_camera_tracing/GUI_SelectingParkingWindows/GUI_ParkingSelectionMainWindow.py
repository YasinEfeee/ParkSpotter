# GUI_ParkingSelectionMainWindow.py

import cv2
import sys
import os

from PyQt5.QtWidgets import QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QMessageBox, QInputDialog
from PyQt5.QtGui import QPixmap, QFont, QImage, QIcon
from PyQt5.QtCore import Qt, QTimer

from Full_app_with_live_video_and_camera_tracing.parking_manager import ParkingManager
from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_BaseWindow import BaseWindow


class ParkingSelectionMainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Park Alanı Seçimi - Ana Pencere")
        # Pencere boyutlarını sabitle
        self.setFixedSize(800, 700)  # Genişlik ve yükseklik sabitleniyor

        # Ana widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Durum bayrakları
        self.capture = None
        self.timer = None
        self.current_frame = None
        self.camera_index = 0  # Varsayılan kamera kaynağı
        self.flag_for_GUI = False

        # 'ParkingManger' Sınıfını yükleme
        self.manager = ParkingManager()

        # QSS ile Flat Tasarım
        main_widget.setStyleSheet("""
                    QWidget {
                        color: #D8DEE9;
                        background-color: #242423;
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
                    QLabel {
                        color: #D8DEE9;
                        font-size: 14px;
                    }
                    QLabel#credits_label {
                        font-size: 13px;  /* Sadece credits_label için geçerli */
                        color: #D8DEE9;
                    }
                    QLabel#header {
                        font-size: 18px;
                        color: #ECEFF4;
                    }                 
                """)

        # Pop-up'lar için varsayılan stil uygulaması
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                color: black;
            }
        """)

        # Başlık
        self.header_label = QLabel("Park Alanı Seçimi", main_widget)
        self.header_label.setObjectName("header")
        self.header_label.setFont(QFont("Open Sans", 10, QFont.Bold))
        self.header_label.setGeometry(50, 20, 700, 40)
        self.header_label.setAlignment(Qt.AlignCenter)

        # Ok simgesi ile geri butonu
        self.back_button = QPushButton("", main_widget)

        # Proje kök dizinini belirle
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Bu dosyanın bulunduğu dizin
        project_root = os.path.dirname(base_dir)  # Ana proje kök dizini

        # Logonun yolu
        icon_path = os.path.join(project_root, "ImagesForGUI/back-arrow-icon.png")  # Ana dizine göre yol

        self.back_button.setIcon(QIcon(icon_path))  # Burada bir resim dosyası kullanabilirsiniz
        self.back_button.setGeometry(10, 10, 40, 40)  # Küçük bir buton
        self.back_button.setStyleSheet("border: none;")  # Kenarlıkları kaldır
        self.back_button.clicked.connect(self.go_back)

        # Görüntü Gösterimi İçin QLabel
        self.image_label = QLabel(main_widget)
        self.image_label.setGeometry(50, 70, 700, 350)
        self.image_label.setStyleSheet("border: 2px solid #333533;")
        self.image_label.setAlignment(Qt.AlignCenter)

        # Kamera Düğmeleri
        self.start_camera_button = QPushButton("Kamerayı Başlat (Varsayılan Kamera Kaynağını Açar)", main_widget)
        self.start_camera_button.setFont(QFont("Open Sans", 10))
        self.start_camera_button.setGeometry(50, 440, 700, 40)
        self.start_camera_button.clicked.connect(self.start_camera)

        self.change_camera_button = QPushButton("Kamera Kaynağını Değiştir", main_widget)
        self.change_camera_button.setFont(QFont("Open Sans", 10))
        self.change_camera_button.setGeometry(50, 490, 700, 40)
        self.change_camera_button.clicked.connect(self.show_camera_selection)

        # 'Ekran Görüntüsü Al ve Park Alanını Düzenle' Butonu
        self.capture_screenshot_button = QPushButton("Ekran Görüntüsü Al ve Park Alanını Düzenle", main_widget)
        self.capture_screenshot_button.setFont(QFont("Open Sans", 10))
        self.capture_screenshot_button.setGeometry(50, 540, 700, 40)
        self.capture_screenshot_button.setEnabled(False)
        self.capture_screenshot_button.clicked.connect(self.capture_screenshot_and_open_editor)

        # QSS ile butonun görünümünü ayarla
        self.capture_screenshot_button.setStyleSheet("""
            QPushButton {
                background-color: #333533;
                        color: #ECEFF4;
                        border: 0.5px solid #717271;
                        border-radius: 5px;
                        padding: 8px 15px;
                        font-size: 13px;
                        font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #262626;
                color: #575454;
                border: 1px solid #717271;
            }
            QPushButton:hover:!disabled {
                background-color: #4E504E;
            }
        """)

        # Goruntu uzerinden park alani sec
        self.upload_from_image = QPushButton("Görüntü Üzerinden Park Alanı Seç", main_widget)
        self.upload_from_image.setFont(QFont("Open Sans", 10))
        self.upload_from_image.setGeometry(50, 590, 340, 40)
        self.upload_from_image.clicked.connect(self.from_image)

        # Videodan Park alani sec
        self.upload_from_video = QPushButton("Video Üzerinden Park Alanı Seç", main_widget)
        self.upload_from_video.setFont(QFont("Open Sans", 10))
        self.upload_from_video.setGeometry(410, 590, 340, 40)
        self.upload_from_video.clicked.connect(self.from_video)

        # Sağ alt köşeye yapımcı adı
        self.credits_label = QLabel("Created by - YasinEfeee", main_widget)
        self.credits_label.setObjectName("credits_label")
        self.credits_label.setFont(QFont("Open Sans", 8))
        self.credits_label.setGeometry(600, 670, 180, 20)
        self.credits_label.setAlignment(Qt.AlignRight)


    def show_camera_selection(self):
        """Kamera seçimi için kullanıcıya bir pencere açar."""
        try:
            if self.capture and self.capture.isOpened():
                self.stop_camera()  # Mevcut kamerayı durdur

            # Kamera seçimi için diyalog aç
            camera_index, ok = QInputDialog.getInt(
                self,
                "Kamera Seçimi",
                "Kullanmak istediğiniz kamera numarasını (0-5) girin:",
                value=self.camera_index,
                min=0,
                max=5
            )
            if ok:
                if camera_index == self.camera_index:
                    QMessageBox.information(self, "Bilgi", f"Kamera {camera_index} zaten aktif.")
                    return
                self.camera_index = camera_index
                self.start_camera()

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata", f"Kamera seçimi sırasında bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.format_exc()}")


    def start_camera(self):
        """Seçilen kamerayı başlatır ve QLabel üzerinde görüntü gösterir."""
        try:
            # Mevcut kamera kontrolü
            if self.capture and self.capture.isOpened():
                reply = QMessageBox.question(
                    self,
                    "Kamera Zaten Aktif",
                    f"Şu anda {self.camera_index} numaralı kamera aktif. Tekrar başlatmak ister misiniz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return  # Kullanıcı "Hayır" derse işlem yapılmaz

                # Mevcut kamerayı düzgün şekilde kapat
                self.stop_camera()

            # Yeni kamera başlatma
            self.capture = cv2.VideoCapture(self.camera_index)
            if not self.capture.isOpened():
                QMessageBox.critical(self, "Hata",
                                     f"Kamera {self.camera_index} açılamadı. Lütfen kameranızı kontrol edin.")
                return

            # Kameranın çözünürlüğünü ayarla
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)  # Genişlik
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)  # Yükseklik

            # Kamera çözünürlük oranını kontrol et
            if not self.validate_camera_resolution():
                self.stop_camera()
                return

            self.capture_screenshot_button.setEnabled(True)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # 30 ms'de bir kare güncelle

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata", f"Kamera başlatılırken bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.format_exc()}")


    def validate_camera_resolution(self):
        """
        Kameradan gelen görüntünün çözünürlüğünü kontrol eder.
        Minimum 1700x700 çözünürlüğünde olup olmadığını doğrular.
        """
        if not self.capture.isOpened():
            QMessageBox.critical(None, "Hata", "Kamera açılamadı.")
            return False

        # Kamera çözünürlüğünü al
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Çözünürlüğü kontrol et
        if width < 1280 or height < 720:  # Minimum olması gereken çözünürlük
            QMessageBox.critical(None, "Hata",
                                 f"Kameradan alınan çözünürlük çok düşük ({width}x{height}). "
                                 f"Lütfen minimum 1700x700 çözünürlüğe sahip bir kamera bağlayın.")
            return False

        return True


    def update_frame(self):
        """Kameradan alınan görüntüyü QLabel üzerinde gösterir."""
        try:
            ret, frame = self.capture.read()
            if not ret:
                QMessageBox.critical(self, "Hata", "Kamera görüntüsü alınamadı.")
                self.stop_camera()
                return

            # Orijinal çözünürlükte kareyi kaydet
            self.current_frame = frame

            # QLabel üzerinde göstermek için boyutları koruyarak ölçekle
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # QPixmap'e dönüştür ve QLabel üzerinde göster
            pixmap = QPixmap.fromImage(qt_image).scaled(self.image_label.width(), self.image_label.height(),
                                                        Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata", f"Kamera başlatılırken bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.format_exc()}")

    def capture_screenshot_and_open_editor(self):
        """Ekran görüntüsü alır ve doğrudan park alanı seçimine geçer."""
        if self.current_frame is not None:
            # Görüntüyü direkt olarak park seçimi işlemine aktar
            self.open_park_selection(self.current_frame)
        else:
            QMessageBox.warning(self, "Uyarı", "Herhangi bir görüntü alınamadı.")


    def open_park_selection(self, image):
        """Park alanı seçimi için görüntüyü doğrudan işler."""
        try:

            from Full_app_with_live_video_and_camera_tracing.GUI_SelectingParkingWindows.GUI_CameraParkSelectionWindow import ParkSelection  # Lazy import

            self.park_selection = ParkSelection()
            self.park_selection.load_image(image)  # Görüntüyü doğrudan yükle
            self.park_selection.show()
            self.close()

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata", f"ParkSelection açılırken bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.format_exc()}")


    def stop_camera(self):
        """Kamerayı durdurur ve kaynakları serbest bırakır."""
        if self.capture and self.capture.isOpened():
            self.capture.release()
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.capture_screenshot_button.setEnabled(False)


    def from_video(self):
        """
        Kullanıcının bir video yüklemesine izin verir, videodan bir kesit seçer ve park alanı seçimi için işler.
        """
        try:
            file_dialog = QFileDialog()
            video_path, _ = file_dialog.getOpenFileName(self, "Video Yükle", "", "Video Dosyaları (*.mp4 *.avi *.mkv)")

            if not video_path:
                QMessageBox.warning(self, "Uyarı", "Bir video seçmediniz.")
                return

            # Video boyutunu ve süresini kontrol et
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                QMessageBox.critical(self, "Hata", "Video açılamadı. Lütfen geçerli bir video dosyası seçin.")
                return

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            duration = frame_count / fps  # Videonun süresi saniye cinsinden

            # Maksimum video süresi ve boyutu kontrolü
            max_duration = 60  # saniye
            if duration > max_duration:
                QMessageBox.warning(
                    self,
                    "Video Çok Uzun",
                    f"Seçilen video çok uzun ({int(duration)} saniye). Lütfen {max_duration} saniyeden kısa bir video seçin."
                )
                cap.release()
                return

            # Kullanıcıdan bir başlangıç ve bitiş zamanı seçmesini iste
            start_time, ok_start = QInputDialog.getInt(self, "Başlangıç Zamanı", "Başlangıç zamanı (saniye):", min=0,
                                                       max=int(duration))
            if not ok_start:
                cap.release()
                return

            end_time, ok_end = QInputDialog.getInt(self, "Bitiş Zamanı", "Bitiş zamanı (saniye):", value=start_time + 5,
                                                   min=start_time, max=int(duration))
            if not ok_end:
                cap.release()
                return

            # Seçilen zaman aralığını doğrula
            if start_time >= end_time:
                QMessageBox.warning(self, "Uyarı", "Başlangıç zamanı, bitiş zamanından büyük veya eşit olamaz.")
                cap.release()
                return

            # Belirtilen aralıktan bir kare al
            cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
            ret, frame = cap.read()
            if not ret:
                QMessageBox.critical(self, "Hata", "Videodan kare alınamadı. Lütfen başka bir video seçin.")
                cap.release()
                return

            cap.release()

            # Alınan kareyi işleme gönder
            self.image = frame  # Alınan kareyi doğrudan `image` olarak ayarla
            self.manager.set_image(self.image)  # Park alanı seçim süreci için görüntüyü ayarla

            # Park alanı seçimi için open_park_selection() çağrısı
            self.open_park_selection_from_frame(self.image)

            QMessageBox.information(self, "Başarılı", "Video başarıyla işlendi. Şimdi park alanı seçimi yapabilirsiniz.")

        except Exception as e:
            import traceback
            print(f"Analiz sırasında bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.print_exc()} ")


    def open_park_selection_from_frame(self, frame):
        """
        Alınan kareyi doğrudan park alanı seçimi için işler.
        """
        try:
            from Full_app_with_live_video_and_camera_tracing.GUI_SelectingParkingWindows.GUI_CameraParkSelectionWindow import ParkSelection  # Lazy import

            self.park_selection = ParkSelection()
            self.park_selection.image = frame
            self.park_selection.load_image(frame)
            self.park_selection.show()
            self.close()

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata", f"ParkSelection açılırken bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.format_exc()}")


    def from_image(self):
        """Görüntü üzerinden park alanları seçmeye izin verir."""
        try:
            from Full_app_with_live_video_and_camera_tracing.GUI_SelectingParkingWindows.GUI_ImageParkingSelectionWindow import ImageParkingSelection
            self.image_window = ImageParkingSelection()
            self.image_window.show()
            self.close()

        except Exception as e:
            import traceback
            print(f"Analiz sırasında bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.print_exc()} ")
        return None


    def closeEvent(self, event):
        """Pencere kapatıldığında kamerayı düzgün şekilde durdurur."""
        if self.flag_for_GUI:
            self.stop_camera()
            reply = QMessageBox.question(
                self,
                "Çıkış Onayı",
                "dönmek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_SelectionWindow import SelectionWindow

            if reply == QMessageBox.Yes:
                self.flag_for_GUI = True
                self.selection_window = SelectionWindow()
                self.selection_window.show()
                self.close()
            pass


    def go_back(self):
        """Ana menüye geri döner."""
        from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_SelectionWindow import \
            SelectionWindow
        self.selection_window = SelectionWindow()
        self.selection_window.show()
        self.close()
