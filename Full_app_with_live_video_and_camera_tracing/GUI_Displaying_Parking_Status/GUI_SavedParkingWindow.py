#GUI_SavedParkingWindow.py

import os
import cv2
from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QListWidget
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt
from Full_app_with_live_video_and_camera_tracing.firebase_operations import FirebaseOperations
from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_BaseWindow import BaseWindow
from Full_app_with_live_video_and_camera_tracing.GUI_SelectingParkingWindows.GUI_EditingParkSelectionWindow import EditingParkSelection


class SavedParkingWindow(BaseWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Kaydedilmiş Park Alanları")
            self.setFixedSize(1100, 660)

            # Ana widget
            main_widget = QWidget(self)
            self.setCentralWidget(main_widget)

            self.flag_for_GUI = False
            self.saved_callback = None

            # QSS ile modern tasarım (ana widget için)
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
                        QPushButton:disabled {
                            background-color: #1C1C1C;
                            color: #5A5A5A;
                            border: 0.5px solid #717271;
                        }
                        QLabel#credits_label {
                            font-size: 13px;
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

            # Başlık
            self.title_label = QLabel("- Park Alanı Analiz Ekranı -", main_widget)
            self.title_label.setFont(QFont("Open Sans", 12, QFont.Bold))
            self.title_label.setObjectName("title")
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setGeometry(450, 20, 500, 40)

            # Park alanlarını listeleme
            self.parking_list = QListWidget(main_widget)
            self.parking_list.setGeometry(50, 80, 300, 400)
            self.parking_list.itemClicked.connect(self.display_parking_details)

            # Park alanı görselini gösterme
            self.image_label = QLabel("Park Alanı Görseli", main_widget)
            self.image_label.setGeometry(400, 80, 600, 400)
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setStyleSheet("border: 2px solid #333533;")

            # Park alanı düzenleme butonu
            self.edit_button = QPushButton("Park Alanını Düzenle", main_widget)
            self.edit_button.setGeometry(400, 500, 290, 40)
            self.edit_button.clicked.connect(self.edit_parking_lot)
            self.edit_button.setEnabled(False)

            # Park alanını silme butonu
            self.remove_parking_lot_button = QPushButton("Park Alanını Sil", main_widget)
            self.remove_parking_lot_button.setGeometry(710, 500, 290, 40)
            self.remove_parking_lot_button.clicked.connect(self.remove_parking_lot)
            self.remove_parking_lot_button.setEnabled(False)

            # Analiz sonuçlarını gösterme butonu
            self.show_analysis_button = QPushButton("Analiz Sonuçlarını Göster", main_widget)
            self.show_analysis_button.setGeometry(400, 550, 600, 40)
            self.show_analysis_button.clicked.connect(self.show_analysis_results)
            self.show_analysis_button.setEnabled(False)

            # Sağ alt köşeye yapımcı adı
            self.credits_label = QLabel("Created by - YasinEfeee", main_widget)
            self.credits_label.setFont(QFont("Open Sans", 8))
            self.credits_label.setAlignment(Qt.AlignRight)
            self.credits_label.setObjectName("credits_label")
            self.credits_label.setGeometry(900, 630, 180, 20)

            # Firebase'den park alanlarını yükle
            self.firebase_operations = FirebaseOperations()
            self.parking_lots = {}
            self.load_parking_lots()

            self.reset_image_label() # Qlabel üzerindeki görüntüyü sıfırlar

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


    def reset_image_label(self):
        """
        QLabel üzerindeki görüntüyü sıfırlar ve varsayılan metni ayarlar.
        """
        try:
            self.image_label.clear()  # Görseli kaldır
            self.image_label.setPixmap(QPixmap())  # Her ihtimale karşı boş bir Pixmap ayarla
            self.image_label.setText("Park Alanı Görseli")  # Varsayılan metni ayarla
            self.image_label.setAlignment(Qt.AlignCenter)  # Hizalamayı yeniden ayarla

            self.edit_button.setEnabled(False)
            self.remove_parking_lot_button.setEnabled(False)
            self.show_analysis_button.setEnabled(False)

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
            self.reset_image_label()  # QLabel'i sıfırla

            lot_name = item.text()
            blob_name = f"parking_lots/{lot_name}/raw_image.jpg"  # Doğru blob adı

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
            self.remove_parking_lot_button.setEnabled(True)
            self.show_analysis_button.setEnabled(True)

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


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


    def remove_parking_lot(self):
        """
        QLabel'de seçilen park alanını siler.
        """
        try:
            # Kullanıcının seçtiği park alanı adı
            selected_item = self.parking_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Hata", "Lütfen silmek istediğiniz park alanını seçin.")
                return

            parking_lot_name = selected_item.text()

            # Firebase'den silme işlemi
            reply = QMessageBox.question(self, "Silme Onayı",
                                         f"{parking_lot_name} adlı park alanını silmek istediğinize emin misiniz?",
                                         QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.firebase_operations.delete_parking_lot(parking_lot_name)  # Firebase silme işlemi
                self.parking_list.takeItem(self.parking_list.row(selected_item))  # Listeden kaldır
                self.image_label.clear()  # Görseli kaldır
                QMessageBox.information(self, "Başarılı", f"{parking_lot_name} park alanı silindi.")

                self.edit_button.setEnabled(False)
                self.remove_parking_lot_button.setEnabled(False)
                self.show_analysis_button.setEnabled(False)

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


    def edit_parking_lot(self):
        """
        Park alanını düzenlemek için verileri düzenleme ekranına aktarır ve ana pencereyi kapatır.
        """
        try:
            # Kullanıcının seçtiği park alanı adı
            selected_item = self.parking_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Hata", "Lütfen düzenlemek istediğiniz park alanını seçin.")
                return

            parking_lot_name = selected_item.text()

            # Firebase'den ham görüntüyü al
            raw_image_path = self.firebase_operations.download_file(
                f"parking_lots/{parking_lot_name}/raw_image.jpg", "temp_image.jpg"
            )
            if not raw_image_path:
                QMessageBox.critical(self, "Hata", "Görüntü Firebase'den indirilemedi.")
                return

            raw_image = cv2.imread(raw_image_path)

            if raw_image is None:
                QMessageBox.critical(self, "Hata", "Firebase'den indirilen görüntü okunamadı.")
                return

            # Ana pencereyi gizle
            self.hide()

            # Düzenleme ekranına geçiş
            self.park_selection_window = EditingParkSelection()
            self.park_selection_window.previous_parking_lot_name = parking_lot_name  # Eski adı kaydet
            self.park_selection_window.firebase_operations = self.firebase_operations  # Firebase işlemleri aktar
            self.park_selection_window.load_image(raw_image)  # Görüntüyü yükle ve QLabel'e aktar
            self.park_selection_window.setWindowTitle(f"{parking_lot_name} - Park Alanı Düzenleme")

            # Düzenleme ekranı kapandığında ana pencereyi yeniden göster
            self.park_selection_window.saved_callback = self.refresh_and_show_main_window
            self.park_selection_window.show()

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Hata", error_message)


    def refresh_and_show_main_window(self):
        """
        Ana pencereyi yeniden gösterir ve park alanları listesini Firebase'den yeniler.
        """
        try:
            self.reset_image_label()  # QLabel'i sıfırla
            self.parking_list.clear()  # Mevcut listeyi temizle

            # Park alanları listesini temizle ve Firebase'den güncelle
            self.parking_list.clear()  # Mevcut listeyi temizle
            parking_lots = self.firebase_operations.fetch_parking_lots()  # Firebase'den park alanlarını al

            for parking_lot_name in parking_lots.keys():
                self.parking_list.addItem(parking_lot_name)  # Listeye yeni park alanlarını ekle

            # Ana pencereyi yeniden göster
            self.show()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ana pencere yenilenirken bir hata oluştu: {e}")


    def closeEvent(self, event):
        """
        Düzenleme ekranı kapatıldığında yapılacak işlemler.
        """
        try:
            if self.saved_callback:
                self.saved_callback()  # Ana pencereyi yeniden göster ve listeyi yenile
            event.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Düzenleme ekranı kapatılırken hata oluştu: {e}")
            event.ignore()


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
            self.flag_for_GUI = True
            from Full_app_with_live_video_and_camera_tracing.GUI_Displaying_Parking_Status.GUI_CheckParkingStatus import \
                CheckParkingStatus  # Lazy import
            self.check_parking_status = CheckParkingStatus()
            self.check_parking_status.show()
            self.close()
        else:
            pass
