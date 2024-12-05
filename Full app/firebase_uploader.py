import firebase_admin
from firebase_admin import credentials, storage
import os


class FirebaseUploader:
    def __init__(self, bucket_name):
        """
        Firebase Storage bağlantısını başlatır.
        :param bucket_name: Firebase Storage bucket adı.
        """
        if not firebase_admin._apps:  # Eğer Firebase zaten başlatılmadıysa
            cred = credentials.Certificate("serviceAccountKey.json")  # Service Account Key dosyasının yolu
            firebase_admin.initialize_app(cred, {"storageBucket": bucket_name})
        self.bucket = storage.bucket()

    def upload_file(self, local_file_path, cloud_file_path):
        """
        Bir dosyayı Firebase Storage'a yükler.
        :param local_file_path: Yerel dosya yolu.
        :param cloud_file_path: Firebase Storage'daki hedef dosya yolu.
        """
        try:
            if not os.path.exists(local_file_path):
                raise FileNotFoundError(f"Yerel dosya bulunamadı: {local_file_path}")

            blob = self.bucket.blob(cloud_file_path)
            blob.upload_from_filename(local_file_path)
            print(f"Yükleme başarılı: {local_file_path} → {cloud_file_path}")
        except Exception as e:
            print(f"Yükleme sırasında hata oluştu: {e}")
