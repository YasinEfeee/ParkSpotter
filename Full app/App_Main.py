#App_Main.py
import sys
from PyQt5.QtWidgets import QApplication
from GUI_SelectionWindow import SelectionWindow
from GUI_MainWindow import MainWindow
from GUI_SavedParkingWindow import SavedParkingWindow

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = SelectionWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Analiz sırasında bir hata oluştu: {e}")
