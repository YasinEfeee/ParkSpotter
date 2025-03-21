# firebase_operations.py
import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv
import os
import json
import cv2


class FirebaseOperations:
    def __init__(self):
        """
        Firebase Storage bağlantısını başlatır.
        """
        try:
            # Ortam değişkenlerini yükle
            load_dotenv()
            bucket_name = os.getenv("FIREBASE_BUCKET")
            service_account_path = os.getenv("SERVICE_ACCOUNT_KEY_PATH", "serviceAccountKey.json")

            if not bucket_name:
                raise ValueError("FIREBASE_BUCKET .env dosyasında tanımlı değil.")

            if not os.path.exists(service_account_path):
                raise FileNotFoundError(f"Service account key dosyası bulunamadı: {service_account_path}")

            # Firebase başlat
            if not firebase_admin._apps:  # Eğer Firebase zaten başlatılmadıysa
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {"storageBucket": bucket_name})

            self.bucket = storage.bucket()
            print(f"Firebase Storage bağlantısı kuruldu: {bucket_name}")

        except Exception as e:
            print(f"Hata oluştu: {e}")


    def save_raw_image_to_firebase(self, image, parking_lot_name):
        """
        Ham görüntüyü Firebase'e kaydeder.

        Args:
            image (numpy.ndarray): İşlenmemiş görüntü (OpenCV formatında).
            parking_lot_name (str): Park alanı adı.

        Returns:
            bool: İşlem başarılıysa True, aksi halde False.
        """
        try:
            # Firebase depolama yolu
            blob_name = f"parking_lots/{parking_lot_name}/raw_image.jpg"
            blob = self.bucket.blob(blob_name)

            # Önce park alanının zaten var olup olmadığını kontrol edin
            if self.check_parking_lot_exists(parking_lot_name):
                print(f"Park alanı zaten mevcut: {parking_lot_name}. Ham görüntü üzerine yazılıyor.")

            # Geçici olarak görüntüyü bir dosyaya kaydet
            temp_file = f"temp_{parking_lot_name}_raw_image.jpg"
            cv2.imwrite(temp_file, image)

            # Firebase'e yükle
            blob.upload_from_filename(temp_file, content_type="image/jpeg")

            # Geçici dosyayı sil
            os.remove(temp_file)

            print(f"Ham görüntü Firebase'e başarıyla kaydedildi: {blob_name}")
            return True

        except Exception as e:
            import traceback
            print(f"Hata oluştu: {e}\n{traceback.format_exc()}")
            return False


    def upload_file(self, local_file_path, cloud_file_path):
        """
        Dosyayı Firebase Storage'a yükler.
        :param local_file_path: Yerel dosya yolu.
        :param cloud_file_path: Firebase Storage içindeki hedef dosya yolu.
        """
        try:
            if not os.path.exists(local_file_path):
                raise FileNotFoundError(f"Yerel dosya bulunamadı: {local_file_path}")

            blob = self.bucket.blob(cloud_file_path)
            blob.upload_from_filename(local_file_path)
            print(f"Yükleme başarılı: {local_file_path} → {cloud_file_path}")

        except Exception as e:
            print(f"Hata: {e}")


    def upload_analysis_result(self, analysis_image, parking_lot_name):
        """
        Analiz sonucunu Firebase'e yükler.
        :param analysis_image: OpenCV tarafından oluşturulan analiz görseli.
        :param parking_lot_name: Firebase'de kullanılacak park alanı klasör adı.
        """
        try:
            # Analiz görselini geçici bir dosyaya kaydet
            temp_analysis_path = "temp_analysis_result.jpg"
            cv2.imwrite(temp_analysis_path, analysis_image)

            # Firebase'e yükle
            self.upload_file(
                temp_analysis_path,
                f"parking_lots/{parking_lot_name}/analysis_result.jpg"
            )

            # Geçici dosyayı temizle
            if os.path.exists(temp_analysis_path):
                os.remove(temp_analysis_path)
                print("Geçici analiz dosyası silindi.")

        except Exception as e:
            print(f"Analiz sonuç yükleme hatası: {e}")


    def fetch_parking_lots(self):
        """
        Firebase Storage'dan kayıtlı park alanlarını çeker.
        """
        try:
            blobs = self.bucket.list_blobs(prefix="parking_lots/")
            parking_lots = {}

            for blob in blobs:
                if "original_image.jpg" in blob.name:
                    parking_lot_name = blob.name.split("/")[1]
                    parking_lots[parking_lot_name] = {"image_url": blob.public_url, "spots": []}

                elif "parking_spot_" in blob.name:
                    parking_lot_name = blob.name.split("/")[1]
                    if parking_lot_name in parking_lots:
                        spot_data = blob.download_as_text()
                        parking_lots[parking_lot_name]["spots"].append(json.loads(spot_data))

            return parking_lots

        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


    def check_parking_lot_exists(self, parking_lot_name):
        """
        Kayıt Esnasında Firebase'de belirtilen park alanının var olup olmadığını kontrol eder.
        :param parking_lot_name: Kontrol edilecek park alanının adı.
        :return: True (var) veya False (yok).
        """

        try:
            blobs = list(self.bucket.list_blobs(prefix=f"parking_lots/{parking_lot_name}/"))
            if blobs:
                return True
            return False
        except Exception as e:
            import traceback
            error_message = f"Hata oluştu: {e}\n{traceback.format_exc()}"
            print(error_message)


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

    def download_file(self, firebase_path, local_path):
        """
        Firebase'den bir dosyayı indirir.
        :param firebase_path: Firebase üzerindeki dosya yolu
        :param local_path: İndirilecek yerel dosya yolu
        :return: Yerel dosya yolu
        """
        try:
            blob = self.bucket.blob(firebase_path)
            blob.download_to_filename(local_path)
            print(f"{firebase_path} dosyası {local_path} konumuna indirildi.")
            return local_path
        except Exception as e:
            import traceback
            error_message = f"Dosya indirme hatası: {e}\n{traceback.format_exc()}"
            print(error_message)
            return None
