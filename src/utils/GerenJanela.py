from PyQt6.QtCore import Qt, QPoint, QRect, QSize, QTimer
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

    def __init__(self, title_bar=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dragging = False
        self._drag_start_global = QPoint()
        self._drag_start_window_pos = QPoint()
        self._resizing = False
        self._resize_direction = None
        self._title_bar = title_bar
        self._resize_start_geometry = QRect()
        self._resize_start_global = QPoint()
        
        self.normal_size = self.DEFAULT_SIZE
        self.normal_position = self.DEFAULT_POSITION
        self.setGeometry(
            self.normal_position.x(),
            self.normal_position.y(),
            self.normal_size.width(),
            self.normal_size.height()
        )

    def toggle_maximize(self):
        if self.windowState() == Qt.WindowState.WindowMaximized:
            self.setWindowState(Qt.WindowState.WindowNoState)
            self.setGeometry(QRect(self.normal_position, self.normal_size))
        else:
            self._preserve_normal_state()
            self.setWindowState(Qt.WindowState.WindowMaximized)
        
        self._sync_interface_refresh()
        QApplication.processEvents()

    def windowState(self):
        return super().windowState()

    def setWindowState(self, state):
        super().setWindowState(state)
        self._sync_interface_refresh()

    def _preserve_normal_state(self):
        self.normal_size = self.size()
        self.normal_position = self.pos()

    def _deep_layout_refresh(self):
        for widget in self.findChildren(QWidget):
            widget.updateGeometry()
            if widget.layout() is not None:
                widget.layout().activate()
        
        QApplication.sendPostedEvents()
        QApplication.processEvents()

    def _sync_interface_refresh(self):
        self.updateGeometry()
        self.update()

    def resizeEvent(self, event):
        # Mantém o tamanho normal atualizado
        if not self.isMaximized() and not self.isMinimized():
            self.normal_size = event.size()
            self.normal_position = self.pos()
        
        super().resizeEvent(event)
        # Atualiza elementos da interface
        self._sync_interface_refresh()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
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

    def _is_title_bar_click(self, event):
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
        new_geo = self._calculate_new_geometry(event.globalPosition().toPoint())
        self._apply_new_geometry(new_geo)

    def _reset_state(self):
        self._dragging = False
        self._resizing = False
        self.unsetCursor()

    def _get_resize_direction(self, pos):
        rect = self.rect()
        margin = self.RESIZE_MARGIN
        if pos.x() <= margin and pos.y() <= margin:
            return ResizeDirection.TOP_LEFT
        if pos.x() >= rect.width() - margin and pos.y() <= margin:
            return ResizeDirection.TOP_RIGHT
        if pos.x() <= margin and pos.y() >= rect.height() - margin:
            return ResizeDirection.BOTTOM_LEFT
        if pos.x() >= rect.width() - margin and pos.y() >= rect.height() - margin:
            return ResizeDirection.BOTTOM_RIGHT
        if pos.x() <= margin:
            return ResizeDirection.LEFT
        if pos.x() >= rect.width() - margin:
            return ResizeDirection.RIGHT
        if pos.y() <= margin:
            return ResizeDirection.TOP
        if pos.y() >= rect.height() - margin:
            return ResizeDirection.BOTTOM
        return None

    def _calculate_new_geometry(self, global_pos):
        start_geo = self._resize_start_geometry
        delta = global_pos - self._resize_start_global
        new_x, new_y = start_geo.x(), start_geo.y()
        new_width, new_height = start_geo.width(), start_geo.height()

        match self._resize_direction:
            case ResizeDirection.TOP_LEFT:
                new_x += delta.x()
                new_y += delta.y()
                new_width -= delta.x()
                new_height -= delta.y()
            case ResizeDirection.TOP_RIGHT:
                new_y += delta.y()
                new_width += delta.x()
                new_height -= delta.y()
            case ResizeDirection.BOTTOM_LEFT:
                new_x += delta.x()
                new_width -= delta.x()
                new_height += delta.y()
            case ResizeDirection.BOTTOM_RIGHT:
                new_width += delta.x()
                new_height += delta.y()
            case ResizeDirection.LEFT:
                new_x += delta.x()
                new_width -= delta.x()
            case ResizeDirection.RIGHT:
                new_width += delta.x()
            case ResizeDirection.TOP:
                new_y += delta.y()
                new_height -= delta.y()
            case ResizeDirection.BOTTOM:
                new_height += delta.y()

        return self._enforce_min_size(new_x, new_y, new_width, new_height)

    def _enforce_min_size(self, x, y, width, height):
        new_width = max(width, self.MIN_WINDOW_SIZE)
        new_height = max(height, self.MIN_WINDOW_SIZE)
        original_right = self._resize_start_geometry.right()
        original_bottom = self._resize_start_geometry.bottom()

        if self._resize_direction in (ResizeDirection.LEFT, ResizeDirection.TOP_LEFT, ResizeDirection.BOTTOM_LEFT):
            x = original_right - new_width
        if self._resize_direction in (ResizeDirection.TOP, ResizeDirection.TOP_LEFT, ResizeDirection.TOP_RIGHT):
            y = original_bottom - new_height

        return (x, y, new_width, new_height)

    def _apply_new_geometry(self, geometry):
        x, y, width, height = geometry
        self.setGeometry(QRect(x, y, width, height))
        if central := self.centralWidget():
            central.updateGeometry()
            central.repaint()

    def _update_cursor(self, pos):
        direction = self._get_resize_direction(pos)
        self.setCursor(self.CURSOR_MAPPING.get(direction, Qt.CursorShape.ArrowCursor))