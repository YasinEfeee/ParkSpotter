# GUI_BaseWindow.py
from PyQt5.QtWidgets import QMainWindow
from Full_app_with_live_video_and_camera_tracing.GUI_MainAndBaseWindows.GUI_SelectionWindow import SelectionWindow


class BaseWindow(QMainWindow):
    def closeEvent(self, event):
        """
        Tüm pencereler kapatıldığında SelectionWindow'u yeniden başlatır.
        """
        if not isinstance(self, SelectionWindow):
            self.selection_window = SelectionWindow()
            self.selection_window.show()

        super().closeEvent(event)  # Varsayılan kapatma işlemini çalıştır
