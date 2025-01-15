# GUI_EditingParkSelection.py
import cv2
import os

from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox,  QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon
from PyQt5.QtCore import Qt

from Full_app_with_live_video_and_camera_tracing.parking_manager import ParkingManager
from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_BaseWindow import BaseWindow
from Full_app_with_live_video_and_camera_tracing.firebase_operations import FirebaseOperations


class EditingParkSelection(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Park Alanı Düzenleme")
        self.setFixedSize(800, 800)

        # Ana widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        self.image = None
        self.analysis_done = False
        self.manager = ParkingManager()
        self.firebase_operations = FirebaseOperations()
        self.flag_for_saving = True
        self.current_parking_type = "normal"
        self.saved_callback = None

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
            QLabel#header {
                font-size: 18px;
                color: #ECEFF4;
            }
            QLabel#credits_label {
                font-size: 13px;
                color: #D8DEE9;
            }
            QPushButton:disabled {
                background-color: #1C1C1C;
                color: #5A5A5A;
                border: 0.5px solid #717271;
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
        self.header_label = QLabel("Park Alanı Düzenleme", main_widget)
        self.header_label.setObjectName("header")
        self.header_label.setFont(QFont("Open Sans", 10, QFont.Bold))
        self.header_label.setGeometry(50, 20, 700, 40)
        self.header_label.setAlignment(Qt.AlignCenter)

        # Görüntü gösterimi QLabel
        self.image_label = QLabel(main_widget)
        self.image_label.setGeometry(50, 70, 700, 350)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #333533;")

        # Butonlar
        self.save_and_analyze_button = QPushButton("Kaydet ve Analiz Et", main_widget)
        self.save_and_analyze_button.setFont(QFont("Open Sans", 10))
        self.save_and_analyze_button.setGeometry(50, 440, 700, 40)
        self.save_and_analyze_button.clicked.connect(self.save_and_analyze)
        self.save_and_analyze_button.setEnabled(False)

        self.select_parking_button = QPushButton("Park Alanı Seç", main_widget)
        self.select_parking_button.setFont(QFont("Open Sans", 10))
        self.select_parking_button.setGeometry(50, 490, 700, 40)
        self.select_parking_button.clicked.connect(self.select_parking)
        self.select_parking_button.setEnabled(False)

        self.disabled_parking_button = QPushButton("Engelli Park Alanı Seç", main_widget)
        self.disabled_parking_button.setFont(QFont("Open Sans", 10))
        self.disabled_parking_button.setGeometry(50, 540, 700, 40)
        self.disabled_parking_button.clicked.connect(self.select_disabled_parking)
        self.disabled_parking_button.setEnabled(False)

        self.finish_selection_button = QPushButton("Park Alanı Seçimini Bitir", main_widget)
        self.finish_selection_button.setFont(QFont("Open Sans", 10))
        self.finish_selection_button.setGeometry(50, 590, 700, 40)
        self.finish_selection_button.clicked.connect(self.finish_selection)
        self.finish_selection_button.setEnabled(False)

        self.remove_rectangle_button = QPushButton("Son Park Alanını Sil", main_widget)
        self.remove_rectangle_button.setFont(QFont("Open Sans", 10))
        self.remove_rectangle_button.setGeometry(50, 640, 340, 40)
        self.remove_rectangle_button.clicked.connect(self.remove_last_rectangle)
        self.remove_rectangle_button.setEnabled(False)

        self.remove_point_button = QPushButton("Son Noktayı Sil", main_widget)
        self.remove_point_button.setFont(QFont("Open Sans", 10))
        self.remove_point_button.setGeometry(410, 640, 340, 40)
        self.remove_point_button.clicked.connect(self.remove_last_point)
        self.remove_point_button.setEnabled(False)

        self.cancel_button = QPushButton("Park Alanı Seçimini İptal Et / Sıfırla", main_widget)
        self.cancel_button.setFont(QFont("Open Sans", 10))
        self.cancel_button.setGeometry(50, 690, 700, 40)
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setEnabled(False)

        # Sağ alt köşeye yapımcı adı
        self.credits_label = QLabel("Created by - YasinEfeee", main_widget)
        self.credits_label.setObjectName("credits_label")
        self.credits_label.setFont(QFont("Open Sans", 8))
        self.credits_label.setGeometry(600, 770, 180, 20)
        self.credits_label.setAlignment(Qt.AlignRight)


    def load_image(self, image):
        """Görüntüyü yükler ve işleme hazırlar."""
        self.image = image
        if self.image is None:
            QMessageBox.critical(self, "Hata", "Görüntü yüklenemedi.")
            return

        # Park alanlarını ve noktaları sıfırla
        self.manager.reset()

        # Yeni görüntüyü ayarla ve QLabel üzerinde göster
        self.manager.set_image(self.image)

        # OpenCV görüntüsünü QLabel için QPixmap'e dönüştür
        rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # BGR'den RGB'ye dönüştür
        height, width, _ = rgb_image.shape
        qt_image = QImage(rgb_image.data, width, height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(self.image_label.width(), self.image_label.height(),
                                                    Qt.KeepAspectRatio)

        # QLabel üzerinde görüntüyü ayarla
        self.image_label.setPixmap(pixmap)

        # Butonları etkinleştir
        self.select_parking_button.setEnabled(True)
        self.disabled_parking_button.setEnabled(False)
        self.remove_rectangle_button.setEnabled(False)
        self.remove_point_button.setEnabled(False)
        self.save_and_analyze_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.finish_selection_button.setEnabled(True)

        QMessageBox.information(self, "Başarılı", "Görüntü başarıyla yüklendi.")


    def finish_selection(self):
        """Park alanı seçimini bitirir ve analiz işlemini etkinleştirir."""
        if len(self.manager.rectangles) < 1:
            QMessageBox.warning(self, "Uyarı", "En az bir park alanı seçmelisiniz!")
            return

        if cv2.getWindowProperty("Park Alanlarini Sec", cv2.WND_PROP_VISIBLE) >= 1:
            self.manager.opencv_window_open = False
            cv2.destroyWindow("Park Alanlarini Sec")

        self.disabled_parking_button.setEnabled(False)
        self.save_and_analyze_button.setEnabled(True)
        self.remove_point_button.setEnabled(False)
        self.remove_rectangle_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.finish_selection_button.setEnabled(False)

        QMessageBox.information(self, "Bilgi", "Park alanı seçimini tamamladınız."
                                               "Şimdi analiz yapıp park alanlarını kaydedebilirsiniz.")


    def save_and_analyze(self):
        """
        Park alanlarını analiz eder ve kullanıcıya kaydetmek isteyip istemediğini sorar.
        """
        # Görüntü ve park alanı kontrolü
        if self.image is None:
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

        if len(self.manager.rectangles) < 1:
            QMessageBox.warning(self, "Uyarı", "Analiz yapmak için en az bir park alanı seçmelisiniz!")
            return

        # Eğer "Park Durumu" penceresi zaten açık ise uyarı ver
        if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
            QMessageBox.information(
                self,
                "Uyarı",
                "Park Durumu ekranı zaten açık."
            )
            return

        # Eğer "Park Alanlarını Seç" açık ise kapat
        if cv2.getWindowProperty("Park Alanlarini Sec", cv2.WND_PROP_VISIBLE) >= 1:
            self.manager.opencv_window_open = False
            cv2.destroyWindow("Park Alanlarini Sec")


        # Park durumu analizini başlat
        try:
            self.select_parking_button.setEnabled(False)
            self.disabled_parking_button.setEnabled(False)
            print("Analiz ediliyor...")
            self.manager.check_parking_status(image=self.image)
        except Exception as e:
            print(f"Analiz sırasında bir hata oluştu: {e}")
            QMessageBox.critical(self, "Hata", f"Analiz sırasında bir hata oluştu:\n{e}")
            return

        if self.flag_for_saving:
            # Kullanıcıya kaydetmek isteyip istemediğini sor
            reply = QMessageBox.question(
                self,
                "Kaydetme Onayı",
                "Analiz tamamlandı. Kaydetmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                while True:
                    # Kullanıcıdan park alanı ismi al
                    parking_lot_name, ok = QInputDialog.getText(self, "Kaydet",
                                                                "Park alanını kaydetmek için bir isim girin:")
                    if not ok:  # Kullanıcı iptal ettiyse döngüden çık
                        QMessageBox.information(self, "Bilgi", "Kaydetme işlemi iptal edildi.")
                        self.select_parking_button.setEnabled(True)
                        break

                    if not parking_lot_name.strip():  # Boş isim girildiyse uyarı ver ve tekrar sor
                        QMessageBox.warning(self, "Uyarı", "Park alanı ismi boş bırakılamaz!")
                        continue

                    try:
                        # Park alanı adı kontrolü
                        if self.firebase_operations.check_parking_lot_exists(parking_lot_name):
                            QMessageBox.warning(None, "Başarısız",
                                                f"{parking_lot_name} adlı bir park alanı zaten mevcut.")
                            continue  # Tekrar isim sormak için döngüye dön

                        # Geçerli bir isim girildiyse işlemi tamamla
                        self.manager.upload_to_firebase(parking_lot_name)

                        # Analiz işlemleri sonucunda oluşturulan görsel (OpenCV penceresinde gösterilen görsel)
                        analysis_image = self.manager.get_analysis_result()

                        # Firebase'e yükleme
                        uploader = FirebaseOperations()
                        uploader.upload_analysis_result(analysis_image, parking_lot_name)
                        uploader.save_raw_image_to_firebase(self.image, parking_lot_name)

                        # Eski park alanını sil
                        self.firebase_operations.delete_parking_lot(self.previous_parking_lot_name)

                        # `cv2` penceresini kapat
                        cv2.destroyAllWindows()

                        QMessageBox.information(self, "Başarılı",
                                                f"Park alanı {parking_lot_name} ve analiz sonuçları Firebase'e başarıyla yüklendi ve eski park alanı silindi.")

                        # Kaydetme işlemi tamamlandığında GUI'yi kapat
                        self.close()

                        break

                    except Exception as e:
                        QMessageBox.critical(self, "Hata", f"Kaydetme işlemi sırasında bir hata oluştu: {e}")
                        break

            else:
                QMessageBox.information(self, "Bilgi", "Veriler kaydedilmedi.")
                self.select_parking_button.setEnabled(True)

        else:
            QMessageBox.information(self, "Bilgi", "Veriler kaydedilmedi.")
            self.select_parking_button.setEnabled(True)


    def delete_parking_lot(self, parking_lot_name):
        """
        Firebase'den bir park alanını siler.
        :param parking_lot_name: Silinecek park alanının adı.
        """
        try:
            blobs = self.bucket.list_blobs(prefix=f"parking_lots/{parking_lot_name}/")
            for blob in blobs:
                blob.delete()
            print(f"{parking_lot_name} park alanı başarıyla silindi.")
        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)
            raise RuntimeError(f"Park alanı silinirken hata oluştu: {e}")


    def select_disabled_parking(self):
        try:
            if self.image is not None:
                # "Park Durumu" penceresi açıksa kapat
                if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow("Park Durumu")

                self.current_parking_type = "disabled"
                self.finish_selection_button.setEnabled(True)
                self.remove_rectangle_button.setEnabled(True)
                self.remove_point_button.setEnabled(True)
                self.cancel_button.setEnabled(True)
                self.save_and_analyze_button.setEnabled(False)

                self.manager.start_disabled_parking_selection()

        except Exception as e:
            import traceback
            print(f"Analiz sırasında bir hata oluştu: {traceback.format_exc()}")


    def select_parking(self):
        if self.image is not None:
            # "Park Durumu" penceresi açıksa kapat
            if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
                cv2.destroyWindow("Park Durumu")

            self.current_parking_type = "normal"
            self.finish_selection_button.setEnabled(True)
            self.disabled_parking_button.setEnabled(True)
            self.remove_rectangle_button.setEnabled(True)
            self.remove_point_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
            self.save_and_analyze_button.setEnabled(False)

            self.manager.start_parking_selection()


    def cancel_operation(self):
        """İşlemi iptal eder."""

        reply = QMessageBox.question(
            self,
            "Çıkış Onayı",
            "Çıkış yapmak istediğinize emin misiniz? Bütün seçimler sıfırlanacktır.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.manager.opencv_window_open:
                self.manager.opencv_window_open = False
                cv2.destroyWindow("Park Alanlarini Sec")
                self.manager.reset()
                QMessageBox.information(self, "İptal Edildi", "İşlem iptal edildi ve tüm seçimler silindi.")

            self.disabled_parking_button.setEnabled(False)
            self.save_and_analyze_button.setEnabled(False)
            self.remove_rectangle_button.setEnabled(False)
            self.remove_point_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
        else:
            pass


    def remove_last_rectangle(self):
        """Son park alanını silmek için butona bağlı metot."""
        self.manager.remove_last_rectangle()


    def remove_last_point(self):
        """Son noktayı silmek için butona bağlı metot."""
        self.manager.remove_last_point()


    def closeEvent(self, event):
        """
        Düzenleme ekranı kapatılırken yapılacak işlemler.
        """
        try:
            # Eğer park alanı seçme işlemi devam ediyorsa
            if self.manager.opencv_window_open:
                reply = QMessageBox.question(
                    self,
                    "Park Alanı Seçme Ekranı Açık",
                    "Park alanı seçme işlemi devam ediyor. Kapatmak istiyor musunuz? İşlem iptal edilecek.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # Park alanı seçme işlemini iptal et ve pencereyi kapat
                    self.manager.opencv_window_open = False
                    cv2.destroyAllWindows()
                    QMessageBox.information(self, "İşlem İptal Edildi", "Park alanı seçme işlemi iptal edildi.")
                    self.manager.reset()
                    self.flag_for_saving = False
                    event.accept()
                else:
                    # Kapatma işlemini iptal et
                    event.ignore()
                    return

            # Eğer "Park Durumu" penceresi açık ise kapatılacak
            if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
                reply_2 = QMessageBox.question(
                    self,
                    "Park Durumu Görüntüleme Açık",
                    "Park Durumu ekranı açık. Kapatmak istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply_2 == QMessageBox.Yes:
                    cv2.destroyAllWindows()
                    QMessageBox.information(self, "İşlem Tamamlandı", "Park Durumu ekranı kapatıldı.")
                    event.accept()
                else:
                    event.ignore()
                    return

            # Eğer callback tanımlıysa ana pencereyi yeniden açar
            if hasattr(self, "saved_callback") and self.saved_callback:
                self.saved_callback()

            # Pencereyi kapatma işlemini onayla
            event.accept()

        except Exception as e:
            import traceback
            error_message = f"Bir hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)
            QMessageBox.critical(self, "Hata", error_message)
            event.ignore()