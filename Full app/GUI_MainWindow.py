import sys
import cv2

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from parking_manager import ParkingManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Park Alanı Tespiti")
        self.setGeometry(100, 100, 800, 600)

        self.manager = ParkingManager()

        # Layout oluştur
        layout = QVBoxLayout()

        # Geri Butonu
        self.back_button = QPushButton("Geri")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        # Görüntü gösterimi için QLabel
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # "Görüntü Yükle" butonu
        self.load_image_button = QPushButton("Görüntü Yükle")
        self.load_image_button.clicked.connect(self.load_image)
        layout.addWidget(self.load_image_button)

        # "Park Alanı Seç" butonu
        self.select_parking_button = QPushButton("Park Alanı Seç")
        self.select_parking_button.clicked.connect(self.select_parking)
        self.select_parking_button.setEnabled(False)  # Başlangıçta devre dışı
        layout.addWidget(self.select_parking_button)

        # "Son Park Alanını Sil" butonu
        self.remove_rectangle_button = QPushButton("Son Park Alanını Sil")
        self.remove_rectangle_button.clicked.connect(self.remove_last_rectangle)
        self.remove_rectangle_button.setEnabled(False)
        layout.addWidget(self.remove_rectangle_button)

        # "Son Noktayı Sil" butonu
        self.remove_point_button = QPushButton("Son Noktayı Sil")
        self.remove_point_button.clicked.connect(self.remove_last_point)
        self.remove_point_button.setEnabled(False)
        layout.addWidget(self.remove_point_button)

        # "Analiz" butonu
        self.analyze_button = QPushButton("Analiz")
        self.analyze_button.clicked.connect(self.analyze)
        self.analyze_button.setEnabled(False)  # Başlangıçta devre dışı
        layout.addWidget(self.analyze_button)

        # "Park Alanı Seçimini İptal Et" butonu
        self.cancel_button = QPushButton("Park Alanı Seçimini İptal Et")
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button)

        # Ana widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.image_path = None
        self.image = None


    def closeEvent(self, event):
        """
        Ana pencere kapatılmadan önce yapılacak işlemler.
        """
        # Eğer park alanı seçme işlemi devam ediyorsa
        if self.manager.opencv_window_open:
            reply = QMessageBox.question(
                self,
                "Park Alanı Seçme Ekranı Açık",
                "Park alanı seçme işlemi açık. Kapatmak istiyor musunuz? İşlem iptal edilecek.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Park alanı seçme işlemini iptal et ve pencereyi kapat
                self.manager.opencv_window_open = False  # Döngüyü sonlandırmak için
                cv2.destroyAllWindows()
                self.manager.reset()  # İşlemleri sıfırla

                self.remove_rectangle_button.setEnabled(False)
                self.remove_point_button.setEnabled(False)
                self.analyze_button.setEnabled(False)
                self.cancel_button.setEnabled(False)

                QMessageBox.information(self, "İşlem İptal Edildi", "'Park Alanı Seçme' işlemi iptal edildi.")
                # Pencere kapatma işlemini onayla
                event.accept()
            else:
                # Kapatma işlemini iptal et
                event.ignore()
                return

        # Eğer Park Durumu seçme işlemi devam ediyorsa
        if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
            reply_2 = QMessageBox.question(
                self,
                "Park Durumu Seçme Ekranı Açık",
                "Park Durumu seçme işlemi açık. Kapatmak istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply_2 == QMessageBox.Yes:
                # Park Durumu seçme işlemini iptal et ve pencereyi kapat
                cv2.destroyAllWindows()
                QMessageBox.information(self, "İşlem İptal Edildi", "'Park Alanı Seçme' işlemi iptal edildi.")
                # Pencere kapatma işlemini onayla
                event.accept()
            else:
                # Kapatma işlemini iptal et
                event.ignore()
                return

        # Genel bir onay mesajı göster
        reply = QMessageBox.question(
            self,
            "Onay",
            "Programı kapatmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Pencere kapatma işlemini kabul et
            event.accept()
        else:
            # Kapatma işlemini iptal et
            event.ignore()
            return


    def load_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Görüntü Yükle", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            self.image = cv2.imread(file_path)
            if self.image is None:
                QMessageBox.critical(self, "Hata", "Görüntü yüklenemedi.")
                return

            # Park alanlarını ve noktaları sıfırla
            self.manager.reset()

            # Yeni görüntüyü ayarla ve QLabel üzerinde göster
            self.manager.set_image(self.image)
            pixmap = QPixmap(file_path).scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

            # Butonları etkinleştir
            self.select_parking_button.setEnabled(True)
            self.remove_rectangle_button.setEnabled(False)
            self.remove_point_button.setEnabled(False)
            self.analyze_button.setEnabled(False)  # Eski analizleri engelle
            self.cancel_button.setEnabled(False)
            QMessageBox.information(self, "Başarılı", "Görüntü başarıyla yüklendi.")


    def select_parking(self):
        if self.image is not None:
            # "Park Durumu" penceresi açıksa kapat
            if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
                cv2.destroyWindow("Park Durumu")


            self.analyze_button.setEnabled(True)
            self.remove_rectangle_button.setEnabled(True)
            self.remove_point_button.setEnabled(True)
            self.cancel_button.setEnabled(True)

            self.manager.start_parking_selection()


    def analyze(self):
        """
            Park alanlarını analiz eden metot.
        """
        print("deneme")
        # Görüntü ve park alanı kontrolü
        if not self.image_path:
            QMessageBox.warning(
                self,
                "Uyarı",
                "Hiçbir görüntü yüklenmedi. Analiz yapılabilmesi için önce bir görüntü yüklemelisiniz."
            )
            return

        # Park alanı seçilip seçilmediğini kontrol et
        if not self.manager.rectangles:
            QMessageBox.warning(
                self,
                "Uyarı",
                "Hiçbir park alanı seçilmedi. Analiz yapılabilmesi için önce park alanı seçmelisiniz."
            )
            return

        # Eğer "Park Durumu" penceresi zaten açık ise uyarı ver
        if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
            QMessageBox.information(
                self,
                "Uyarı",
                "Park Durumu ekranı zaten açık."
            )
            return

        print("Analiz ediliyor...")

        self.remove_rectangle_button.setEnabled(False)
        self.remove_point_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        # Eğer "Park Alanlarını Seç" açık ise kapat
        if cv2.getWindowProperty("Park Alanlarini Sec", cv2.WND_PROP_VISIBLE) >= 1:
            self.manager.opencv_window_open = False
            cv2.destroyWindow("Park Alanlarini Sec")

        # Park durumu analizini başlat
        try:
            self.manager.check_parking_status(self.image_path)
        except Exception as e:
            print(f"Analiz sırasında bir hata oluştu: {e}")


    def cancel_operation(self):
        """İşlemi iptal eder."""
        if self.manager.opencv_window_open:
            self.manager.opencv_window_open = False
            cv2.destroyWindow("Park Alanlarini Sec")
            self.manager.reset()
            QMessageBox.information(self, "İptal Edildi", "İşlem iptal edildi ve tüm seçimler silindi.")
        self.analyze_button.setEnabled(False)
        self.remove_rectangle_button.setEnabled(False)
        self.remove_point_button.setEnabled(False)
        self.cancel_button.setEnabled(False)


    def remove_last_rectangle(self):
        """Son park alanını silmek için butona bağlı metot."""
        self.manager.remove_last_rectangle()


    def remove_last_point(self):
        """Son noktayı silmek için butona bağlı metot."""
        self.manager.remove_last_point()


    def go_back(self):
        """Geri butonuna basıldığında ana menüye döner."""
        from GUI_SelectionWindow import SelectionWindow # Lazy import
        self.selection_window = SelectionWindow()
        self.selection_window.show()
        self.close()
