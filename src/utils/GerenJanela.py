from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QMainWindow
from enum import Enum, auto

class ResizeDirection(Enum):
    """Enumeração para direções de redimensionamento válidas"""
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
    Janela personalizável com capacidades de redimensionamento e arrasto.
    
    Atributos:
        RESIZE_MARGIN (int): Margem de sensibilidade para redimensionamento (px)
        MIN_WINDOW_SIZE (int): Tamanho mínimo permitido para a janela (px)
    """

    RESIZE_MARGIN = 15  # Sensibilidade para redimensionamento nas bordas
    MIN_WINDOW_SIZE = 50  # Previne redimensionamento abaixo deste tamanho

    # Mapeamento de cursores pré-definido
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
        self._offset = QPoint()
        self._resizing = False
        self._resize_direction = None
        self._title_bar = title_bar

    def mousePressEvent(self, event):
        """Inicia interação com base na posição do clique do mouse"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

            if self._is_title_bar_click(event):
                self._start_dragging(event)
            else:
                self._start_resizing(event)

    def mouseMoveEvent(self, event):
        """Gerencia movimento contínuo do mouse durante interações"""
        if self._dragging:
            self._handle_dragging(event)
        elif self._resizing:
            self._handle_resizing(event)
        else:
            self._update_cursor(event.pos())

    def mouseReleaseEvent(self, event):
        """Finaliza todas as interações ao liberar o botão do mouse"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._reset_state()

    def _is_title_bar_click(self, event):
        """Verifica se o clique ocorreu na barra de título"""
        if self._title_bar:
            local_pos = self._title_bar.mapFromParent(event.pos())
            return self._title_bar.rect().contains(local_pos)
        return False

    def _start_dragging(self, event):
        """Inicia processo de arrastar a janela"""
        self._dragging = True
        self._offset = event.pos()

    def _start_resizing(self, event):
        """Inicia processo de redimensionamento"""
        self._resize_direction = self._get_resize_direction(event.pos())
        self._resizing = bool(self._resize_direction)

    def _handle_dragging(self, event):
        """Atualiza posição da janela durante o arrasto"""
        self.move(self.pos() + event.pos() - self._offset)

    def _handle_resizing(self, event):
        """Executa cálculo e aplicação do redimensionamento"""
        new_geometry = self._calculate_new_geometry(event.pos())
        self._apply_new_geometry(new_geometry)

    def _reset_state(self):
        """Reinicia todos os estados de interação"""
        self._dragging = False
        self._resizing = False
        self.unsetCursor()

    def _get_resize_direction(self, pos):
        """Determina a direção do redimensionamento baseado na posição"""
        rect = self.rect()
        margin = self.RESIZE_MARGIN

        # Verificação de regiões usando early return
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

    def _calculate_new_geometry(self, pos):
        """Calcula nova geometria da janela de forma segura"""
        global_pos = self.mapToGlobal(pos)
        current_geometry = self.geometry()
        new_x, new_y = current_geometry.x(), current_geometry.y()
        new_width, new_height = current_geometry.width(), current_geometry.height()

        # Cálculos baseados na direção usando Enum
        match self._resize_direction:
            case ResizeDirection.TOP_LEFT:
                new_x = global_pos.x()
                new_y = global_pos.y()
                new_width += (current_geometry.x() - new_x)
                new_height += (current_geometry.y() - new_y)
            case ResizeDirection.TOP_RIGHT:
                new_y = global_pos.y()
                new_width = global_pos.x() - current_geometry.x()
                new_height += (current_geometry.y() - new_y)
            case ResizeDirection.BOTTOM_LEFT:
                new_x = global_pos.x()
                new_width += (current_geometry.x() - new_x)
                new_height = global_pos.y() - current_geometry.y()
            case ResizeDirection.BOTTOM_RIGHT:
                new_width = global_pos.x() - current_geometry.x()
                new_height = global_pos.y() - current_geometry.y()
            case ResizeDirection.LEFT:
                new_x = global_pos.x()
                new_width += (current_geometry.x() - new_x)
            case ResizeDirection.RIGHT:
                new_width = global_pos.x() - current_geometry.x()
            case ResizeDirection.TOP:
                new_y = global_pos.y()
                new_height += (current_geometry.y() - new_y)
            case ResizeDirection.BOTTOM:
                new_height = global_pos.y() - current_geometry.y()

        # Garante tamanho mínimo
        return self._enforce_min_size(new_x, new_y, new_width, new_height)

    def _enforce_min_size(self, x, y, width, height):
        """Ajusta geometria para respeitar tamanho mínimo"""
        width = max(width, self.MIN_WINDOW_SIZE)
        height = max(height, self.MIN_WINDOW_SIZE)
        
        # Ajuste de posição para redimensionamentos à esquerda/topo
        if self._resize_direction in (ResizeDirection.TOP_LEFT, ResizeDirection.LEFT, ResizeDirection.BOTTOM_LEFT):
            x = self.geometry().right() - width
        if self._resize_direction in (ResizeDirection.TOP_LEFT, ResizeDirection.TOP, ResizeDirection.TOP_RIGHT):
            y = self.geometry().bottom() - height
            
        return (x, y, width, height)

    def _apply_new_geometry(self, geometry):
        """Aplica nova geometria e atualiza elementos visuais"""
        x, y, width, height = geometry
        self.setGeometry(x, y, width, height)
        
        # Atualiza widgets internos se existirem
        if central := self.centralWidget():
            central.updateGeometry()
            central.repaint()

    def _update_cursor(self, pos):
        """Atualiza cursor de acordo com a posição na borda"""
        direction = self._get_resize_direction(pos)
        new_cursor = self.CURSOR_MAPPING.get(direction, Qt.CursorShape.ArrowCursor)
        self.setCursor(new_cursor)