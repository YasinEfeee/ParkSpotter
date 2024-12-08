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
        Firebase'de belirtilen park alanının var olup olmadığını kontrol eder.
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
