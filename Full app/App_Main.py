import sys
from PyQt5.QtWidgets import QApplication
from GUI import MainWindow, SelectionWindow, SavedParkingWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SelectionWindow()
    window.show()
    sys.exit(app.exec_())
