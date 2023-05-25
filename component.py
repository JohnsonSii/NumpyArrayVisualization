from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLabel, QSizePolicy


class VisualizationFrameworkLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setScaledContents(True)
        self.pixmap = None
        self.scale_factor = 1.0
        self.last_mouse_position = QPoint()
        self.image_pos = QPoint()

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        pixmap_size = pixmap.size()
        label_size = self.size()
        scale_factor_w = label_size.width() / pixmap_size.width()
        scale_factor_h = label_size.height() / pixmap_size.height()
        self.scale_factor = min(scale_factor_w, scale_factor_h)
        self.image_pos = QPointF((label_size.width() - pixmap_size.width() * self.scale_factor) / 2.0,
                                 (label_size.height() - pixmap_size.height() * self.scale_factor) / 2.0)
        self.update()

    def wheelEvent(self, event):
        if self.pixmap:
            # Compute the scale factor based on the direction and speed of mouse wheel rotation
            scale_factor_delta = event.angleDelta().y() / 1200.0
            # Adjust the denominator to get a comfortable zoom speed
            old_scale_factor = self.scale_factor
            # self.scale_factor += scale_factor_delta
            if scale_factor_delta > 0:  # Zooming in
                self.scale_factor *= 1.1
            elif scale_factor_delta < 0:  # Zooming out
                self.scale_factor /= 1.1

            self.scale_factor = max(0.1, self.scale_factor)  # Prevent from zooming out too much

            # Compute the position of the mouse in the image coordinates
            mouse_pos = event.posF()
            image_mouse_pos = (mouse_pos - self.image_pos) / old_scale_factor

            # Compute the new size of the scaled pixmap
            pixmap_size = self.pixmap.size() * self.scale_factor

            # Compute the adjusted position of the image based on the scaling and centering
            self.image_pos = mouse_pos - image_mouse_pos * self.scale_factor

            # Trigger a repaint of the widget
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Record the mouse position in global coordinates
            self.last_mouse_position = self.mapToGlobal(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            # Compute the offset of the mouse position relative to the last position
            offset = self.mapToGlobal(event.pos()) - self.last_mouse_position

            # Update the last position to the current position of the mouse
            self.last_mouse_position = self.mapToGlobal(event.pos())

            # Compute the new position of the pixmap based on the offset
            new_image_pos = self.image_pos + offset

            # Update the position of the pixmap and trigger a repaint
            self.image_pos = new_image_pos
            self.update()

    def paintEvent(self, event):
        if self.pixmap:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            # Configure the painter to draw at the correct scale and position
            painter.scale(self.scale_factor, self.scale_factor)
            painter.translate(self.image_pos / self.scale_factor)
            painter.drawPixmap(0, 0, self.pixmap)
