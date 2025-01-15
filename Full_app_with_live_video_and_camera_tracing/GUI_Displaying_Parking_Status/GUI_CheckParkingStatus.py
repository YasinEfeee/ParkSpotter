#GUI_CheckParkingStatus.py

from PyQt5.QtWidgets import QPushButton, QLabel, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_BaseWindow import BaseWindow
import os


class CheckParkingStatus(BaseWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Park Alanı Yönetimi")
            self.setFixedSize(780, 585)  # Pencere boyutları sabitleniyor

            # Ana widget
            main_widget = QWidget(self)
            self.setCentralWidget(main_widget)

            # QSS ile modern tasarım
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

            # Proje kök dizinini belirle
            base_dir = os.path.dirname(os.path.abspath(__file__))  # Bu dosyanın bulunduğu dizin
            project_root = os.path.dirname(base_dir)  # Ana proje kök dizini

            # Logonun yolu
            icon_path = os.path.join(project_root, "ImagesForGUI/back-arrow-icon.png")  # Ana dizine göre yol

            self.back_button.setIcon(QIcon(icon_path))  # Burada bir resim dosyası kullanabilirsiniz
            self.back_button.setGeometry(10, 10, 40, 40)  # Küçük bir buton
            self.back_button.setStyleSheet("border: none;")  # Kenarlıkları kaldır
            self.back_button.clicked.connect(self.go_back)

            # Logo
            self.logo_label = QLabel(main_widget)

            # Proje kök dizinini belirle
            base_dir = os.path.dirname(os.path.abspath(__file__))  # Bu dosyanın bulunduğu dizin
            project_root = os.path.dirname(base_dir)  # Ana proje kök dizini

            # Logonun yolu
            logo_path = os.path.join(project_root, "ImagesForGUI/Logo.png")  # Ana dizine göre yol

            self.logo_label.setPixmap(QPixmap(logo_path).scaled(1000, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setGeometry(240, 40, 300, 120)
            self.logo_label.setAlignment(Qt.AlignCenter)

            # Başlık
            self.title_label = QLabel("- Park Alanı Analiz Ekranı -", main_widget)
            self.title_label.setFont(QFont("Open Sans", 12, QFont.Bold))
            self.title_label.setObjectName("title")
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setGeometry(190, 205, 400, 30)

            # "Park Alanı Analizini Göster" butonu
            self.show_analysis_image_button = QPushButton("Park Alanı Analizini Göster / Düzenle", main_widget)
            self.show_analysis_image_button.setFont(QFont("Open Sans", 10, QFont.Bold))
            self.show_analysis_image_button.setGeometry(190, 250, 400, 50)
            self.show_analysis_image_button.clicked.connect(self.show_analysis_results)

            # "Kamera Üzerinden Park Alanı Analiz Et" butonu
            self.show_analysis_camera_button = QPushButton("Kamera Üzerinden Park Alanı Analiz Et", main_widget)
            self.show_analysis_camera_button.setFont(QFont("Open Sans", 10, QFont.Bold))
            self.show_analysis_camera_button.setGeometry(190, 320, 400, 50)
            self.show_analysis_camera_button.clicked.connect(self.show_analysis_from_camera)

            # "Video Üzerinden Park Alanı Analiz Et" butonu
            self.show_analysis_video_button = QPushButton("Video Üzerinden Park Alanı Analiz Et", main_widget)
            self.show_analysis_video_button.setFont(QFont("Open Sans", 10, QFont.Bold))
            self.show_analysis_video_button.setGeometry(190, 390, 400, 50)
            self.show_analysis_video_button.clicked.connect(self.show_analysis_from_video)

            # Sağ alt köşeye yapımcı adı
            self.credits_label = QLabel("Created by - YasinEfeee", main_widget)
            self.credits_label.setFont(QFont("Open Sans", 8))
            self.credits_label.setAlignment(Qt.AlignRight)
            self.credits_label.setGeometry(580, 550, 180, 20)

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)

    def show_analysis_results(self):
        """Park alanının analiz sonuçlarını gösterir."""
        try:
            from Full_app_with_live_video_and_camera_tracing.GUI_Displaying_Parking_Status.GUI_SavedParkingWindow import SavedParkingWindow

            self.parking_analyze = SavedParkingWindow()
            self.parking_analyze.show()
            self.close()

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)

    def show_analysis_from_video(self):
        """Video üzerinden park alanının anlık analiz sonuçlarını gösterir."""
        try:
            from Full_app_with_live_video_and_camera_tracing.GUI_Displaying_Parking_Status.GUI_VideoParkingStatusWindow import VideoParkingStatusWindow

            self.video_parking_window = VideoParkingStatusWindow()
            self.video_parking_window.show()
            self.close()

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)

    def show_analysis_from_camera(self):
        """Kamera üzerinden park alanının anlık analiz sonuçlarını gösterir."""
        try:
            from Full_app_with_live_video_and_camera_tracing.GUI_Displaying_Parking_Status.GUI_CameraParkingStatusWindow import CameraParkingStatusWindow

            self.camera_status = CameraParkingStatusWindow()
            self.camera_status.show()
            self.close()

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)

    def go_back(self):
        """Geri butonuna basıldığında ana menüye döner."""

        from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_SelectionWindow import SelectionWindow
        self.selection_window = SelectionWindow()
        self.selection_window.show()
        self.close()

    def closeEvent(self, event):
        """
        Pencere kapatılmadan önce yapılacak işlemler.
        """
        pass  # Üst üste pencere açılmasının önlenmesi için pass geç
