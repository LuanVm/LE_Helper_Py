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
    """
    QMainWindow personalizado que permite redimensionamento da janela
    ao arrastar as bordas e canto, simulando comportamento nativo.
    """
    RESIZE_MARGIN: int = 15
    MIN_WINDOW_SIZE: int = 50
    DEFAULT_SIZE: QSize = QSize(980, 740)
    DEFAULT_POSITION: QPoint = QPoint(100, 100)

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

    def __init__(self, title_bar: QWidget = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Estados de arrastar e redimensionamento
        self._dragging: bool = False
        self._drag_start_global: QPoint = QPoint()
        self._drag_start_window_pos: QPoint = QPoint()
        self._resizing: bool = False
        self._resize_direction: ResizeDirection | None = None
        self._title_bar: QWidget = title_bar
        self._resize_start_geometry: QRect = QRect()
        self._resize_start_global: QPoint = QPoint()

        # Armazena a geometria normal (não maximizada)
        self.normal_geometry: QRect = QRect(self.DEFAULT_POSITION, self.DEFAULT_SIZE)
        self.setGeometry(
            self.DEFAULT_POSITION.x(),
            self.DEFAULT_POSITION.y(),
            self.DEFAULT_SIZE.width(),
            self.DEFAULT_SIZE.height()
        )

    def toggle_maximize(self) -> None:
        """
        Alterna entre o estado maximizado e o estado normal.
        Ao restaurar, a geometria anterior é utilizada.
        """
        if self.isMaximized():
            self.setWindowState(Qt.WindowState.WindowNoState)
            self.setGeometry(self.normal_geometry)
        else:
            self.normal_geometry = self.geometry()
            self.showMaximized()
        self._sync_interface_refresh()

    def windowState(self):
        return super().windowState()

    def setWindowState(self, state) -> None:
        super().setWindowState(state)
        self._sync_interface_refresh()

    def _preserve_normal_state(self) -> None:
        """
        Salva a geometria atual da janela para posterior restauração.
        """
        self.normal_geometry = self.geometry()

    def _deep_layout_refresh(self) -> None:
        """
        Força a atualização de geometria e layout de todos os widgets filhos.
        """
        for widget in self.findChildren(QWidget):
            widget.updateGeometry()
            if widget.layout() is not None:
                widget.layout().activate()
        QApplication.sendPostedEvents()
        QApplication.processEvents()

    def _sync_interface_refresh(self) -> None:
        """
        Atualiza a interface, garantindo que a geometria esteja sincronizada.
        """
        self.updateGeometry()
        self.update()
        if self.centralWidget():
            self.centralWidget().updateGeometry()

    def resizeEvent(self, event) -> None:
        """
        Atualiza a geometria normal sempre que a janela for redimensionada,
        se não estiver maximizada.
        """
        if not self.isMaximized():
            self.normal_geometry = self.geometry()
        super().resizeEvent(event)
        self._sync_interface_refresh()

    def mousePressEvent(self, event) -> None:
        """
        Inicia a operação de arrastar ou redimensionar com base na posição do clique.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
            if self._is_title_bar_click(event):
                self._start_dragging(event)
            else:
                self._start_resizing(event)

    def mouseMoveEvent(self, event) -> None:
        """
        Durante o movimento do mouse, realiza a operação de arrastar ou redimensionar.
        """
        if self._dragging:
            self._handle_dragging(event)
        elif self._resizing:
            self._handle_resizing(event)
        else:
            self._update_cursor(event.pos())

    def mouseReleaseEvent(self, event) -> None:
        """
        Finaliza as operações de arrastar ou redimensionar.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._reset_state()

    def _is_title_bar_click(self, event) -> bool:
        """
        Verifica se o clique ocorreu na área da barra de título.
        """
        if self._title_bar:
            local_pos = event.pos() - self._title_bar.pos()
            return self._title_bar.rect().contains(local_pos)
        return False

    def _start_dragging(self, event) -> None:
        """
        Inicia o processo de arrastar a janela.
        """
        self._dragging = True
        self._drag_start_global = event.globalPosition().toPoint()
        self._drag_start_window_pos = self.pos()

    def _start_resizing(self, event) -> None:
        """
        Inicia o redimensionamento da janela definindo a direção apropriada.
        """
        self._resize_direction = self._get_resize_direction(event.pos())
        if self._resize_direction:
            self._resizing = True
            self._resize_start_geometry = self.geometry()
            self._resize_start_global = event.globalPosition().toPoint()

    def _handle_dragging(self, event) -> None:
        """
        Atualiza a posição da janela durante o arrasto.
        """
        delta = event.globalPosition().toPoint() - self._drag_start_global
        self.move(self._drag_start_window_pos + delta)

    def _handle_resizing(self, event) -> None:
        """
        Calcula e aplica a nova geometria durante o redimensionamento.
        """
        new_geo = self._calculate_new_geometry(event.globalPosition().toPoint())
        self._apply_new_geometry(new_geo)

    def _reset_state(self) -> None:
        """
        Reseta os estados de arrastar e redimensionar e redefine o cursor.
        """
        self._dragging = False
        self._resizing = False
        self.unsetCursor()

    def _get_resize_direction(self, pos: QPoint) -> ResizeDirection | None:
        """
        Determina a direção de redimensionamento com base na posição do mouse.
        """
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

    def _calculate_new_geometry(self, global_pos: QPoint) -> tuple[int, int, int, int]:
        """
        Calcula a nova geometria da janela com base na posição global do mouse.
        """
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

    def _enforce_min_size(self, x: int, y: int, width: int, height: int) -> tuple[int, int, int, int]:
        """
        Garante que a nova geometria respeite o tamanho mínimo da janela.
        """
        new_width = max(width, self.MIN_WINDOW_SIZE)
        new_height = max(height, self.MIN_WINDOW_SIZE)
        original_right = self._resize_start_geometry.right()
        original_bottom = self._resize_start_geometry.bottom()

        if self._resize_direction in (ResizeDirection.LEFT, ResizeDirection.TOP_LEFT, ResizeDirection.BOTTOM_LEFT):
            x = original_right - new_width
        if self._resize_direction in (ResizeDirection.TOP, ResizeDirection.TOP_LEFT, ResizeDirection.TOP_RIGHT):
            y = original_bottom - new_height

        return (x, y, new_width, new_height)

    def _apply_new_geometry(self, geometry: tuple[int, int, int, int]) -> None:
        """
        Aplica a nova geometria calculada à janela e atualiza o widget central.
        """
        x, y, width, height = geometry
        self.setGeometry(QRect(x, y, width, height))
        if self.centralWidget() is not None:
            self.centralWidget().updateGeometry()
            self.centralWidget().repaint()

    def _update_cursor(self, pos: QPoint) -> None:
        """
        Atualiza o cursor do mouse com base na direção de redimensionamento.
        """
        direction = self._get_resize_direction(pos)
        self.setCursor(self.CURSOR_MAPPING.get(direction, Qt.CursorShape.ArrowCursor))