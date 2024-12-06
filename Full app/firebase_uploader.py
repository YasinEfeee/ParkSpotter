# fire_base_uploder
import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv
import os
import json


class FirebaseUploader:
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
