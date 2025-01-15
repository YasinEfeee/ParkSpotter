# GUI_ImageParkSelectionWindow.py
import cv2
import os

from PyQt5.QtWidgets import QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QMessageBox,  QInputDialog
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt

from Full_app_with_live_video_and_camera_tracing.parking_manager import ParkingManager
from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_BaseWindow import BaseWindow
from Full_app_with_live_video_and_camera_tracing.firebase_operations import FirebaseOperations


class ImageParkingSelection(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Park Alanı Tespiti")
        self.setFixedSize(800, 850)

        # Ana widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        self.current_parking_type = "normal"
        self.analysis_done = False
        self.manager = ParkingManager()
        self.firebase_operations = FirebaseOperations()
        self.flag_for_saving = True
        self.flag_for_GUI = False

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
        self.header_label = QLabel("Park Alanı Seçimi - Görüntü Seçim Ekranı", main_widget)
        self.header_label.setObjectName("header")
        self.header_label.setFont(QFont("Open Sans", 10, QFont.Bold))
        self.header_label.setGeometry(50, 20, 700, 40)
        self.header_label.setAlignment(Qt.AlignCenter)

        # Geri butonu
        self.back_button = QPushButton("", main_widget)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        icon_path = os.path.join(project_root, "ImagesForGUI/back-arrow-icon.png")
        self.back_button.setIcon(QIcon(icon_path))
        self.back_button.setGeometry(10, 10, 40, 40)
        self.back_button.setStyleSheet("border: none;")
        self.back_button.clicked.connect(self.go_back)

        # Görüntü gösterimi QLabel
        self.image_label = QLabel(main_widget)
        self.image_label.setGeometry(50, 70, 700, 350)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #333533;")

        # Butonlar
        self.load_image_button = QPushButton("Görüntü Yükle", main_widget)
        self.load_image_button.setFont(QFont("Open Sans", 10))
        self.load_image_button.setGeometry(50, 440, 700, 40)
        self.load_image_button.clicked.connect(self.load_image)

        self.save_and_analyze_button = QPushButton("Kaydet ve Analiz Et", main_widget)
        self.save_and_analyze_button.setFont(QFont("Open Sans", 10))
        self.save_and_analyze_button.setGeometry(50, 490, 700, 40)
        self.save_and_analyze_button.clicked.connect(self.save_and_analyze)
        self.save_and_analyze_button.setEnabled(False)

        self.select_parking_button = QPushButton("Park Alanı Seç", main_widget)
        self.select_parking_button.setFont(QFont("Open Sans", 10))
        self.select_parking_button.setGeometry(50, 540, 700, 40)
        self.select_parking_button.clicked.connect(self.select_parking)
        self.select_parking_button.setEnabled(False)

        self.disabled_parking_button = QPushButton("Engelli Park Alanı Seç", main_widget)
        self.disabled_parking_button.setFont(QFont("Open Sans", 10))
        self.disabled_parking_button.setGeometry(50, 590, 700, 40)
        self.disabled_parking_button.clicked.connect(self.select_disabled_parking)
        self.disabled_parking_button.setEnabled(False)

        self.finish_selection_button = QPushButton("Park Alanı Seçimini Bitir", main_widget)
        self.finish_selection_button.setFont(QFont("Open Sans", 10))
        self.finish_selection_button.setGeometry(50, 640, 700, 40)
        self.finish_selection_button.clicked.connect(self.finish_selection)
        self.finish_selection_button.setEnabled(False)

        self.remove_rectangle_button = QPushButton("Son Park Alanını Sil", main_widget)
        self.remove_rectangle_button.setFont(QFont("Open Sans", 10))
        self.remove_rectangle_button.setGeometry(50, 690, 340, 40)
        self.remove_rectangle_button.clicked.connect(self.remove_last_rectangle)
        self.remove_rectangle_button.setEnabled(False)

        self.remove_point_button = QPushButton("Son Noktayı Sil", main_widget)
        self.remove_point_button.setFont(QFont("Open Sans", 10))
        self.remove_point_button.setGeometry(410, 690, 340, 40)
        self.remove_point_button.clicked.connect(self.remove_last_point)
        self.remove_point_button.setEnabled(False)

        self.cancel_button = QPushButton("Park Alanı Seçimini İptal Et / Sıfırla", main_widget)
        self.cancel_button.setFont(QFont("Open Sans", 10))
        self.cancel_button.setGeometry(50, 740, 700, 40)
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setEnabled(False)

        # Sağ alt köşeye yapımcı adı
        self.credits_label = QLabel("Created by - YasinEfeee", main_widget)
        self.credits_label.setObjectName("credits_label")
        self.credits_label.setFont(QFont("Open Sans", 8))
        self.credits_label.setGeometry(600, 830, 180, 20)
        self.credits_label.setAlignment(Qt.AlignRight)

        self.image_path = None
        self.image = None


    def load_image(self):
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Görüntü Yükle", "", "Full_app_with_live_video_and_camera_tracing (*.png *.jpg *.jpeg)")
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
                if self.manager.flag == 1:
                    pixmap = QPixmap(file_path).scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
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
                else:
                    from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_SelectionWindow import SelectionWindow
                    self.selection_window = SelectionWindow()
                    self.selection_window.show()
                    self.close()

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata", f"Kamera başlatılırken bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.format_exc()}")


    def finish_selection(self):
        """Park alanı seçimini bitirir ve analiz işlemini etkinleştirir."""
        if len(self.manager.rectangles) < 1:
            QMessageBox.warning(self, "Uyarı", "En az bir park alanı seçmelisiniz!")
            return

        if cv2.getWindowProperty("Park Alanlarini Sec", cv2.WND_PROP_VISIBLE) >= 1:
            self.manager.opencv_window_open = False
            cv2.destroyWindow("Park Alanlarini Sec")

        self.disabled_parking_button.setEnabled(False)
        self.load_image_button.setEnabled(True)
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
            self.load_image_button.setEnabled(False)
            print("Analiz ediliyor...")
            self.manager.check_parking_status(self.image_path)
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

                        # `cv2` penceresini kapat
                        cv2.destroyAllWindows()

                        QMessageBox.information(self, "Başarılı",
                                                f"Park alanı {parking_lot_name} ve analiz sonuçları Firebase'e başarıyla yüklendi.")

                        if not self.flag_for_GUI:
                            from Full_app_with_live_video_and_camera_tracing.GUI_SelectingParkingWindows.GUI_ParkingSelectionMainWindow import \
                                ParkingSelectionMainWindow
                            self.parking_selection_main_window = ParkingSelectionMainWindow()
                            self.parking_selection_main_window.show()
                            self.close()
                            break # Donguyu kirmak icin

                    except Exception as e:
                        QMessageBox.critical(self, "Hata", f"Kaydetme işlemi sırasında bir hata oluştu: {e}")
                        break
        else:
            QMessageBox.information(self, "Bilgi", "Veriler kaydedilmedi.")
            self.select_parking_button.setEnabled(True)
            self.load_image_button.setEnabled(True)


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
        try:
            if self.image is not None:
                # "Park Durumu" penceresi açıksa kapat
                if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow("Park Durumu")

                self.current_parking_type = "normal"
                self.disabled_parking_button.setEnabled(True)
                self.finish_selection_button.setEnabled(True)
                self.load_image_button.setEnabled(False)
                self.remove_rectangle_button.setEnabled(True)
                self.remove_point_button.setEnabled(True)
                self.cancel_button.setEnabled(True)
                self.save_and_analyze_button.setEnabled(False)

                self.manager.start_parking_selection()

        except Exception as e:
            import traceback
            print(f"Analiz sırasında bir hata oluştu: {traceback.format_exc()}")


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

            self.save_and_analyze_button.setEnabled(False)
            self.disabled_parking_button.setEnabled(False)
            self.remove_rectangle_button.setEnabled(False)
            self.remove_point_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            self.load_image_button.setEnabled(True)
        else:
            pass


    def remove_last_rectangle(self):
        """Son park alanını silmek için butona bağlı metot."""
        self.manager.remove_last_rectangle()


    def remove_last_point(self):
        """Son noktayı silmek için butona bağlı metot."""
        self.manager.remove_last_point()


    def go_back(self):
        """
        Geri butonuna basıldığında ana menüye döner.
        """
        try:
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
                    QMessageBox.information(self, "İşlem İptal Edildi", "'Park Alanı Seçme' işlemi iptal edildi.")
                    self.manager.reset()  # İşlemleri sıfırla
                    self.flag_for_saving = False  # Kaydetme işlemi gerçekleşmemesi için False
                    self.flag_for_GUI = True

            # Eğer Park Durumu işlemi devam ediyorsa
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
                    self.flag_for_saving = False  # Kaydetme işlemi gerçekleşmemesi için False
                    self.flag_for_GUI = True

            from Full_app_with_live_video_and_camera_tracing.GUI_SelectingParkingWindows.GUI_ParkingSelectionMainWindow import \
                ParkingSelectionMainWindow
            self.parking_selection_main_window = ParkingSelectionMainWindow()
            self.parking_selection_main_window.show()
            self.close()

        except Exception as e:
            import traceback
            print(f"Analiz sırasında bir hata oluştu: {e}")
            print(f"Detaylı İzleme: {traceback.print_exc()} ")


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
                QMessageBox.information(self, "İşlem İptal Edildi", "'Park Alanı Seçme' işlemi iptal edildi.")
                self.manager.reset()  # İşlemleri sıfırla
                self.flag_for_saving = False # Kaydetme işlemi gerçekleşmemesi için False
                self.flag_for_GUI = True
                # Pencere kapatma işlemini onayla
                event.accept()
            else:
                # Kapatma işlemini iptal et
                event.ignore()
                return

        # Eğer Park Durumu işlemi devam ediyorsa
        if cv2.getWindowProperty("Park Durumu", cv2.WND_PROP_VISIBLE) >= 1:
            reply_2 = QMessageBox.question(
                self,
                "Park Durumu Seçme Ekranı Açık",
                "Park Durumu Görüntüleme işlemi açık. Kapatmak istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply_2 == QMessageBox.Yes:
                # Park Durumu seçme işlemini iptal et ve pencereyi kapat
                cv2.destroyAllWindows()
                QMessageBox.information(self, "İşlem İptal Edildi", "'Park Alanı Seçme' işlemi iptal edildi.")
                # Pencere kapatma işlemini onayla
                self.flag_for_saving = False  # Kaydetme işlemi gerçekleşmemesi için False
                self.flag_for_GUI = True
                event.accept()
            else:
                # Kapatma işlemini iptal et
                event.ignore()
                return

        from Full_app_with_live_video_and_camera_tracing.GUI_SelectingParkingWindows.GUI_ParkingSelectionMainWindow import ParkingSelectionMainWindow
        self.parking_selection_main_window = ParkingSelectionMainWindow()
        self.parking_selection_main_window.show()
        self.close()