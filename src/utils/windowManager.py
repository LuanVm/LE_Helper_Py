# windowManager.py
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication
from enum import Enum, auto

class ResizeDirection(Enum):
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()

class ResizableWindow(QMainWindow):
    RESIZE_MARGIN = 15
    MIN_WINDOW_SIZE = 50
    DEFAULT_SIZE = QSize(980, 740)
    DEFAULT_POSITION = QPoint(100, 100)

    CURSOR_MAPPING = {
        ResizeDirection.LEFT: Qt.CursorShape.SizeHorCursor,
        ResizeDirection.RIGHT: Qt.CursorShape.SizeHorCursor,
        ResizeDirection.TOP: Qt.CursorShape.SizeVerCursor,
        ResizeDirection.BOTTOM: Qt.CursorShape.SizeVerCursor,
        ResizeDirection.TOP_LEFT: Qt.CursorShape.SizeFDiagCursor,
        ResizeDirection.BOTTOM_RIGHT: Qt.CursorShape.SizeFDiagCursor,
        ResizeDirection.TOP_RIGHT: Qt.CursorShape.SizeBDiagCursor,
        ResizeDirection.BOTTOM_LEFT: Qt.CursorShape.SizeBDiagCursor,
    }

    def __init__(self, title_bar: QWidget = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dragging = False
        self._drag_start_global = QPoint()
        self._drag_start_window_pos = QPoint()
        self._resizing = False
        self._resize_direction = None
        self._title_bar = title_bar
        self._resize_start_geometry = QRect()
        self._resize_start_global = QPoint()

        self.normal_geometry = QRect(self.DEFAULT_POSITION, self.DEFAULT_SIZE)
        self.setGeometry(self.normal_geometry)

    def toggle_maximize(self):
        if self.isMaximized():
            self.setWindowState(Qt.WindowState.WindowNoState)
            self.setGeometry(self.normal_geometry)
        else:
            self.normal_geometry = self.geometry()
            self.showMaximized()
        self._sync_interface_refresh()

    def setWindowState(self, state):
        super().setWindowState(state)
        self._sync_interface_refresh()

    def _sync_interface_refresh(self):
        self.updateGeometry()
        self.update()
        if self.centralWidget():
            self.centralWidget().updateGeometry()

    def resizeEvent(self, event):
        if not self.isMaximized():
            self.normal_geometry = self.geometry()
        super().resizeEvent(event)
        self._sync_interface_refresh()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_title_bar_click(event):
                self._start_dragging(event)
            else:
                self._start_resizing(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._handle_dragging(event)
        elif self._resizing:
            self._handle_resizing(event)
        else:
            self._update_cursor(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._reset_state()

    def _is_title_bar_click(self, event) -> bool:
        if self._title_bar:
            local_pos = event.pos() - self._title_bar.pos()
            return self._title_bar.rect().contains(local_pos)
        return False

    def _start_dragging(self, event):
        self._dragging = True
        self._drag_start_global = event.globalPosition().toPoint()
        self._drag_start_window_pos = self.pos()

    def _start_resizing(self, event):
        self._resize_direction = self._get_resize_direction(event.pos())
        if self._resize_direction:
            self._resizing = True
            self._resize_start_geometry = self.geometry()
            self._resize_start_global = event.globalPosition().toPoint()

    def _handle_dragging(self, event):
        delta = event.globalPosition().toPoint() - self._drag_start_global
        self.move(self._drag_start_window_pos + delta)

    def _handle_resizing(self, event):
        new_geometry = self._calculate_new_geometry(event.globalPosition().toPoint())
        self._apply_new_geometry(new_geometry)

    def _reset_state(self):
        self._dragging = False
        self._resizing = False
        self.unsetCursor()

    def _get_resize_direction(self, pos: QPoint):
        rect = self.rect()
        m = self.RESIZE_MARGIN
        if pos.x() <= m and pos.y() <= m:
            return ResizeDirection.TOP_LEFT
        if pos.x() >= rect.width() - m and pos.y() <= m:
            return ResizeDirection.TOP_RIGHT
        if pos.x() <= m and pos.y() >= rect.height() - m:
            return ResizeDirection.BOTTOM_LEFT
        if pos.x() >= rect.width() - m and pos.y() >= rect.height() - m:
            return ResizeDirection.BOTTOM_RIGHT
        if pos.x() <= m:
            return ResizeDirection.LEFT
        if pos.x() >= rect.width() - m:
            return ResizeDirection.RIGHT
        if pos.y() <= m:
            return ResizeDirection.TOP
        if pos.y() >= rect.height() - m:
            return ResizeDirection.BOTTOM
        return None

    def _calculate_new_geometry(self, global_pos: QPoint):
        delta = global_pos - self._resize_start_global
        rect = self._resize_start_geometry
        x, y = rect.x(), rect.y()
        w, h = rect.width(), rect.height()

        match self._resize_direction:
            case ResizeDirection.TOP_LEFT:
                x += delta.x(); y += delta.y()
                w -= delta.x(); h -= delta.y()
            case ResizeDirection.TOP_RIGHT:
                y += delta.y()
                w += delta.x(); h -= delta.y()
            case ResizeDirection.BOTTOM_LEFT:
                x += delta.x()
                w -= delta.x(); h += delta.y()
            case ResizeDirection.BOTTOM_RIGHT:
                w += delta.x(); h += delta.y()
            case ResizeDirection.LEFT:
                x += delta.x(); w -= delta.x()
            case ResizeDirection.RIGHT:
                w += delta.x()
            case ResizeDirection.TOP:
                y += delta.y(); h -= delta.y()
            case ResizeDirection.BOTTOM:
                h += delta.y()

        w = max(w, self.MIN_WINDOW_SIZE)
        h = max(h, self.MIN_WINDOW_SIZE)

        return x, y, w, h

    def _apply_new_geometry(self, geometry):
        x, y, w, h = geometry
        self.setGeometry(QRect(x, y, w, h))
        if self.centralWidget():
            self.centralWidget().updateGeometry()

    def _update_cursor(self, pos: QPoint):
        direction = self._get_resize_direction(pos)
        self.setCursor(self.CURSOR_MAPPING.get(direction, Qt.CursorShape.ArrowCursor))
