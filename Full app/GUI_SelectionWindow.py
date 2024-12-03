import sys
import cv2

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class SelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Park Alanı Yönetimi")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # "Görsel Yükle" butonu
        self.load_image_button = QPushButton("Görsel Yükle")
        self.load_image_button.clicked.connect(self.open_image_window)
        layout.addWidget(self.load_image_button)

        # "Kaydedilmiş Park Alanını Kullan" butonu
        self.use_saved_parking_button = QPushButton("Kaydedilmiş Park Alanını Kullan")
        self.use_saved_parking_button.clicked.connect(self.open_saved_parking_window)
        layout.addWidget(self.use_saved_parking_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_image_window(self):
        """Görsel yükleme ve park alanı seçimi için pencereyi aç."""
        try:
            from GUI_MainWindow import MainWindow
            self.image_window = MainWindow()
            self.image_window.show()
            self.close()
        except Exception as e:
            import traceback
            print(f"Analiz sırasında bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.print_exc()} ")


    def open_saved_parking_window(self):
        """Kaydedilmiş park alanı kullanma penceresini aç."""
        from GUI_SavedParkingWindow import SavedParkingWindow
        self.saved_parking_window = SavedParkingWindow()
        self.saved_parking_window.show()
        self.close()
