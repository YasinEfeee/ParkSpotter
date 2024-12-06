# GUI_BaseWindow.py
from PyQt5.QtWidgets import QMainWindow
from GUI_SelectionWindow import SelectionWindow


class BaseWindow(QMainWindow):
    def closeEvent(self, event):
        """
        Tüm pencereler kapatıldığında SelectionWindow'u yeniden başlatır.
        """
        if not isinstance(self, SelectionWindow):
            self.selection_window = SelectionWindow()
            self.selection_window.show()

        super().closeEvent(event)  # Varsayılan kapatma işlemini çalıştır
