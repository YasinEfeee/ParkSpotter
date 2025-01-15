# App_Main.py
import sys
import os
from PyQt5.QtWidgets import QApplication

from dotenv import load_dotenv
# .env dosyasını yükle ve PYTHONPATH'i sys.path'e ekle
load_dotenv()
project_path = os.getenv("PYTHONPATH")
if project_path:
    sys.path.insert(0, project_path)
else:
    raise EnvironmentError("PYTHONPATH çevresel değişkeni .env dosyasında tanımlı değil!")

from GUI_SelectionWindow import SelectionWindow


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = SelectionWindow()
        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        import traceback
        print(f"Analiz sırasında bir hata oluştu: {traceback.format_exc()}")
