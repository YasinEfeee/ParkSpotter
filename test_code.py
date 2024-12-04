import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage


class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.rectangles = []
        self.points = []

    def set_image(self, image):
        self.image = image
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QPixmap.fromImage(
            QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        )
        self.setPixmap(q_image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.points.append((self.start_point.x(), self.start_point.y()))
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rectangles.append((self.start_point, self.end_point))
            self.start_point = QPoint()
            self.end_point = QPoint()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.image is not None:
            painter = QPainter(self)
            pen = QPen(Qt.red, 2)
            painter.setPen(pen)

            # Çizilen dikdörtgenler
            for rect in self.rectangles:
                start, end = rect
                painter.drawRect(start.x(), start.y(), end.x() - start.x(), end.y() - start.y())

            # Çizilen noktalar
            for point in self.points:
                painter.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)

            # Aktif dikdörtgen
            if not self.start_point.isNull() and not self.end_point.isNull():
                painter.drawRect(
                    self.start_point.x(),
                    self.start_point.y(),
                    self.end_point.x() - self.start_point.x(),
                    self.end_point.y() - self.start_point.y()
                )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Dikdörtgen ve Nokta Seçimi")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.image_label = ImageLabel()
        layout.addWidget(self.image_label)

        # OpenCV ile bir görüntü yükleyelim
        image = cv2.imread('C:/Users/Nurum/PycharmProjects/2204 ParkSpotter/Full app/Images/IMG_4343.JPEG')
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image_label.set_image(image)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
