#GUI_SavedParkingWindow.py
import sys
import cv2

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QMessageBox, QListWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from firebase_operations import FirebaseOperations
from GUI_BaseWindow import BaseWindow


class SavedParkingWindow(BaseWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Kaydedilmiş Park Alanları")
            self.setGeometry(100, 100, 800, 600)

            layout = QVBoxLayout()

            # FirebaseOperations örneği oluşturuluyor
            self.firebase_operations = FirebaseOperations()
            self.parking_lots = {}  # Firebase'den çekilen veriler

            # Park alanlarını listeleme
            self.parking_list = QListWidget()
            self.parking_list.itemClicked.connect(self.display_parking_details)
            layout.addWidget(self.parking_list)

            # Park alanı görselini gösterme
            self.image_label = QLabel("Park Alanı Görseli")
            self.image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.image_label)

            # Park alanı düzenleme ve analiz sonuçları butonları
            self.edit_button = QPushButton("Park Alanını Düzenle")
            self.edit_button.clicked.connect(self.edit_parking_lot)
            self.edit_button.setEnabled(False)
            layout.addWidget(self.edit_button)

            self.show_analysis_button = QPushButton("Analiz Sonuçlarını Göster")
            self.show_analysis_button.clicked.connect(self.show_analysis_results)
            self.show_analysis_button.setEnabled(False)
            layout.addWidget(self.show_analysis_button)

            # Geri Butonu
            self.back_button = QPushButton("Geri")
            self.back_button.clicked.connect(self.go_back)
            layout.addWidget(self.back_button)


            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

            self.load_parking_lots()
        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)

    def load_parking_lots(self):
        """
        Firebase'den park alanlarını çeker ve listeye ekler.
        """
        try:
            self.parking_lots = self.firebase_operations.fetch_parking_lots()
            for lot_name in self.parking_lots:
                self.parking_list.addItem(lot_name)
        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)

    def display_parking_details(self, item):
        """
        Seçilen park alanının detaylarını gösterir.
        """
        try:
            lot_name = item.text()
            lot_data = self.parking_lots.get(lot_name, {})
            blob_name = f"parking_lots/{lot_name}/original_image.jpg"  # Doğru blob adı

            # Blob'dan veriyi indir
            blob = self.firebase_operations.bucket.blob(blob_name)
            if not blob.exists():
                QMessageBox.warning(self, "Hata", f"Görsel bulunamadı: {blob_name}")
                return

            image_data = blob.download_as_bytes()

            # Görseli göster
            pixmap = QPixmap()
            if not pixmap.loadFromData(image_data):
                QMessageBox.warning(self, "Hata", "Görsel yüklenemedi.")
                return

            self.image_label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio))

            self.edit_button.setEnabled(True)
            self.show_analysis_button.setEnabled(True)

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


    def edit_parking_lot(self):
        """
        Park alanını düzenlemek için mevcut verileri düzenleme ekranına aktarır.
        """
        QMessageBox.information(self, "Düzenleme", "Park alanı düzenleme işlevi yakında eklenecek.")


    def show_analysis_results(self):
        """
        Park alanının analiz sonuçlarını gösterir.
        """
        selected_item = self.parking_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Hata", "Analiz sonuçlarını göstermek için bir park alanı seçmelisiniz.")
            return

        lot_name = selected_item.text()
        analysis_blob_name = f"parking_lots/{lot_name}/analysis_result.jpg"

        # Firebase'den analiz görselini indir ve göster
        try:
            blob = self.firebase_operations.bucket.blob(analysis_blob_name)
            if not blob.exists():
                QMessageBox.warning(self, "Hata", f"Analiz sonucu bulunamadı: {analysis_blob_name}")
                return

            analysis_image_data = blob.download_as_bytes()
            pixmap = QPixmap()
            if not pixmap.loadFromData(analysis_image_data):
                QMessageBox.warning(self, "Hata", "Analiz görseli yüklenemedi.")
                return

            # Analiz görselini ekranda göster
            self.image_label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio))
            QMessageBox.information(self, "Analiz", f"{lot_name} analiz sonuçları gösteriliyor.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Analiz sonuçlarını gösterirken bir hata oluştu: {e}")

    def save_changes(self):
        """
        Değiştirilen park alanı verilerini Firebase'e kaydeder.
        """


    def go_back(self):
        """
        Geri butonuna basıldığında ana menüye döner.
        """
        reply = QMessageBox.question(
            self,
            "Çıkış Onayı",
            "Ayrılmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            from GUI_SelectionWindow import SelectionWindow  # Lazy import
            self.selection_window = SelectionWindow()
            self.selection_window.show()
            self.close()
        else:
            pass