# Main
import cv2
from parking_statue import select_points, check_parking_status

# Global değişkenler
SCALE_FACTOR = 0.6  # Ekran küçültme oranı
image_copy = None

if __name__ == "__main__":
    """
    Kullanıcıdan park alanlarını seçmesini istemek için bir pencere aç
    """
    image_path = "C:/Users/Nurum/Downloads/IMG_4343.JPEG"  # Görüntü yolunu yazın
    image = cv2.imread(image_path)
    if image is None:
        print("Görüntü yüklenemedi. Lütfen doğru bir yol belirtin.")
        exit()

    image_copy = image.copy()

    cv2.namedWindow("Park Alanlarini Sec")
    cv2.setMouseCallback("Park Alanlarini Sec", select_points, image_copy)

    # Görüntüyü %60 ölçekle göster
    scaled_image = cv2.resize(image_copy, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR, interpolation=cv2.INTER_AREA)
    cv2.imshow("Park Alanlarini Sec", scaled_image)

    print("Park alanlarını seçmek için 4 nokta tıklayın. Seçimi tamamlamak için 'Enter' tuşuna basın.")
    print("Çıkmak için 'Q' tuşuna basın.")
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter tuşu ile park alanı seçimini tamamla
            break
        elif key == ord('q') or key == ord('Q'):  # Q tuşu ile çıkış yap
            print("Çıkılıyor...")
            cv2.destroyAllWindows()
            exit()

    cv2.destroyAllWindows()

    # Seçilen park alanlarının durumunu kontrol et
    check_parking_status(image_path)


# park Cakisma sorunu coz
# Ek featurlari uzerinde calis

