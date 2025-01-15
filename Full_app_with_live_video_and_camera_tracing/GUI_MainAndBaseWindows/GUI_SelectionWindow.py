# GUI_SelectionWindow.py
import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from sympy.codegen.ast import continue_


class SelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Park Alanı Yönetimi - Ana Menü")

        # Pencere boyutlarını sabitle
        self.setFixedSize(780, 585)  # Genişlik ve yükseklik sabitleniyor

        # QSS ile Flat Tasarım
        self.setStyleSheet("""
            QMainWindow {
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
            QLabel#credits_label {
                font-size: 13px;  /* Sadece credits_label için geçerli */
                color: #D8DEE9;
            }
        """)

        # Ana widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Logo
        self.logo_label = QLabel(main_widget)
        self.logo_label.setPixmap(QPixmap("../ImagesForGUI/Logo.png").scaled(1100, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setGeometry(220, 50, 330, 165)  # (x, y, genişlik, yükseklik)
        self.logo_label.setAlignment(Qt.AlignCenter)

        # "Görsel Yükle" butonu
        self.new_parking_lot_button = QPushButton("Yeni Park Alanı Yükle/Seç", main_widget)
        self.new_parking_lot_button.setFont(QFont("Open Sans", 10, QFont.Bold))
        self.new_parking_lot_button.setGeometry(190, 250, 400, 50)  # (x, y, genişlik, yükseklik)
        self.new_parking_lot_button.clicked.connect(self.choose_new_parking_lot)

        # "Kaydedilmiş Park Alanını Kullan" butonu
        self.use_saved_parking_button = QPushButton("Kaydedilmiş Park Alanını Kullan", main_widget)
        self.use_saved_parking_button.setGeometry(190, 330, 400, 50)  # (x, y, genişlik, yükseklik)
        self.use_saved_parking_button.clicked.connect(self.analayze_parking_status)

        # "Proje Hakkında Daha Fazla Bilgi" butonu
        self.more_info_button = QPushButton("- Proje Hakkında Daha Fazla Bilgi -", main_widget)
        self.more_info_button.setGeometry(190, 410, 400, 50)  # (x, y, genişlik, yükseklik)
        self.more_info_button.clicked.connect(self.more_info)

        # Sağ alt köşeye yapımcı adı
        self.credits_label = QLabel("Created by - YasinEfeee", main_widget)
        self.credits_label.setFont(QFont("Arial", 8))
        self.credits_label.setObjectName("credits_label")  # Özel bir ad belirliyoruz
        self.credits_label.setAlignment(Qt.AlignRight)
        self.credits_label.setGeometry(580, 555, 180, 20)  # (x, y, genişlik, yükseklik)

    def choose_new_parking_lot(self):
        """
        Park seçme ekranı penceresini aç.
        """
        try:
            # Modülü import edin
            from Full_app_with_live_video_and_camera_tracing.GUI_SelectingParkingWindows.GUI_ParkingSelectionMainWindow import \
                ParkingSelectionMainWindow  # Lazy import

            self.parking_selection_main = ParkingSelectionMainWindow()
            self.parking_selection_main.show()
            self.close()

        except Exception as e:
            import traceback
            print(f"Detaylı İzleme: {traceback.format_exc()}")

    def analayze_parking_status(self):
        """
        Park alanlarının durmunu kontrol eden pencereyi açar.
        """
        try:
            # Modülü import edin
            from Full_app_with_live_video_and_camera_tracing.GUI_Displaying_Parking_Status.GUI_CheckParkingStatus import \
                CheckParkingStatus

            self.parking_status = CheckParkingStatus()
            self.parking_status.show()
            self.close()

        except Exception as e:
            import traceback
            print(f"Detaylı İzleme: {traceback.format_exc()}")
            print(e)

    def more_info(self):
        """
        Geliştiricinin açılmasını istediği bilgilerini açar / gösterir.
        """
        import webbrowser

        try:
            github_url = "https://github.com/YasinEfeee/ParkSpotter"  # GitHub projenizin tam URL'si
            webbrowser.open(github_url)  # Tarayıcıda URL'yi aç
        except Exception as e:
            print(f"GitHub bağlantısı açılamadı. Hata: {e}")

