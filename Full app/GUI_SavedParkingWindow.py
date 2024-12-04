#GUI_SavedParkingWindow.py
import sys
import cv2

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class SavedParkingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kaydedilmiş Park Alanını Kullan")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Geri Butonu
        self.back_button = QPushButton("Geri")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        # Kaydedilmiş park alanlarını yükleme
        self.load_saved_button = QPushButton("Kaydedilmiş Park Alanını Yükle")
        layout.addWidget(self.load_saved_button)

        # Park alanı durumu gösterme
        self.show_status_button = QPushButton("Park Alanı Durumunu Göster")
        layout.addWidget(self.show_status_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def go_back(self):
        """Geri butonuna basıldığında Görsel Yükle ekranına döner."""
        from GUI_SelectionWindow import SelectionWindow
        self.image_window = SelectionWindow()
        self.image_window.show()
        self.close()
