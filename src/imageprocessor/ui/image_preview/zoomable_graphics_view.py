from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor, QKeyEvent, QPainter, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QSizePolicy,
)


class ZoomableGraphicsView(QGraphicsView):
    pointClicked = Signal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self._zoom = 1.0
        self._zoom_step = 1.25
        self._fitted = True
        self._point_selection_enabled = False

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizeAdjustPolicy(QGraphicsView.SizeAdjustPolicy.AdjustIgnored)
        self.setMinimumSize(0, 0)

        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setBackgroundBrush(Qt.BrushStyle.NoBrush)
        self.setStyleSheet("QGraphicsView { border: 0; background: transparent; }")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )

        self._zoom_cursor = _make_zoom_cursor()

    def setPointSelectionEnabled(self, enabled: bool):
        """Enable or disable image point selection."""

        self._point_selection_enabled = enabled

        if enabled:
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.viewport().setCursor(self._zoom_cursor)

    # ------------------------------------------------------------------
    # region: Image Handling

    def setPixmap(self, pixmap: QPixmap):
        self._pixmap_item.setPixmap(pixmap)

        if pixmap.isNull():
            self.resetTransform()
            self.scene().setSceneRect(0, 0, 0, 0)
            self._zoom = 1.0
            self._fitted = True
            return

        self.scene().setSceneRect(self._pixmap_item.boundingRect())
        self._zoom = 1.0
        self._fitted = True
        self._fit()

    def _fit(self):
        if self._pixmap_item.pixmap().isNull():
            return

        if self.viewport().size().isEmpty():
            return

        self.resetTransform()
        self.fitInView(
            self._pixmap_item,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self._zoom = self.transform().m11()
        self._fitted = True

    def _zoomBy(self, factor: float):
        if self._pixmap_item.pixmap().isNull():
            return

        center = self.viewport().rect().center()
        scene_center = self.mapToScene(center)

        self._fitted = False
        self._zoom *= factor
        self.scale(factor, factor)
        self.centerOn(scene_center)

    # endregion
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # region: Event Handling

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                self._zoomBy(self._zoom_step)
                event.accept()
                return

            if event.key() in (Qt.Key.Key_Minus, Qt.Key.Key_Underscore):
                self._zoomBy(1.0 / self._zoom_step)
                event.accept()
                return

        super().keyPressEvent(event)

    def enterEvent(self, event):
        if self._point_selection_enabled:
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.viewport().setCursor(self._zoom_cursor)

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.viewport().unsetCursor()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._point_selection_enabled and event.button() == Qt.MouseButton.LeftButton:
            scene_position = self.mapToScene(event.position().toPoint())

            self.setPointSelectionEnabled(False)
            self.pointClicked.emit(scene_position.x(), scene_position.y())

            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton and not self._pixmap_item.pixmap().isNull():
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._zoomBy(1.0 / self._zoom_step)
            else:
                self._zoomBy(self._zoom_step)

            event.accept()
            return

        super().mousePressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta()

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if delta.y() > 0:
                self._zoomBy(self._zoom_step)
            elif delta.y() < 0:
                self._zoomBy(1.0 / self._zoom_step)

            event.accept()
            return

        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            horizontal = self.horizontalScrollBar()

            amount = delta.y() or delta.x()
            horizontal.setValue(horizontal.value() - amount)

            event.accept()
            return

        super().wheelEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self._fitted:
            self._fit()

    # endregion
    # ----------------------------------------------------------------


def _make_zoom_cursor() -> QCursor:
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = painter.pen()
    pen.setWidth(2)
    painter.setPen(pen)

    painter.drawEllipse(2, 2, 13, 13)
    painter.drawLine(13, 13, 21, 21)

    # Plus.
    painter.drawLine(8, 5, 8, 12)
    painter.drawLine(5, 8, 11, 8)

    painter.end()

    return QCursor(pixmap, 0, 0)
