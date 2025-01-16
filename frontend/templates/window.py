from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QMainWindow

class ResizableWindow(QMainWindow):
    def __init__(self, barra_titulo=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dragging = False
        self.offset = QPoint()
        self.resizing = False
        self.resize_direction = None
        self.barra_titulo = barra_titulo  # Recebe a barra de título personalizada

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.barra_titulo and self.barra_titulo.geometry().contains(event.pos()):
                self.dragging = True
                self.offset = event.pos()  # Usa event.pos() em vez de event.position().toPoint()
            else:
                self.resizing = True
                self.resize_direction = self.get_resize_direction(event.pos())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.pos() + event.pos() - self.offset)
        elif self.resizing and self.resize_direction:
            self.resize_window(event.pos())
        else:
            self.update_cursor(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.unsetCursor()  # Restaura o cursor padrão

    def get_resize_direction(self, pos):
        """Determina a direção do redimensionamento com base na posição do mouse."""
        margin = 10
        rect = self.rect()

        if pos.x() <= margin and pos.y() <= margin:
            return "top-left"
        elif pos.x() >= rect.width() - margin and pos.y() <= margin:
            return "top-right"
        elif pos.x() <= margin and pos.y() >= rect.height() - margin:
            return "bottom-left"
        elif pos.x() >= rect.width() - margin and pos.y() >= rect.height() - margin:
            return "bottom-right"
        elif pos.x() <= margin:
            return "left"
        elif pos.x() >= rect.width() - margin:
            return "right"
        elif pos.y() <= margin:
            return "top"
        elif pos.y() >= rect.height() - margin:
            return "bottom"
        else:
            return None

    def resize_window(self, pos):
        """Redimensiona a janela com base na direção do redimensionamento."""
        rect = self.rect()
        global_pos = self.mapToGlobal(pos)

        if self.resize_direction == "top-left":
            self.setGeometry(
                global_pos.x(), global_pos.y(),
                rect.width() + (self.pos().x() - global_pos.x()),
                rect.height() + (self.pos().y() - global_pos.y())
            )
        elif self.resize_direction == "top-right":
            self.setGeometry(
                self.pos().x(), global_pos.y(),
                global_pos.x() - self.pos().x(),
                rect.height() + (self.pos().y() - global_pos.y())
            )
        elif self.resize_direction == "bottom-left":
            self.setGeometry(
                global_pos.x(), self.pos().y(),
                rect.width() + (self.pos().x() - global_pos.x()),
                global_pos.y() - self.pos().y()
            )
        elif self.resize_direction == "bottom-right":
            self.resize(global_pos.x() - self.pos().x(), global_pos.y() - self.pos().y())
        elif self.resize_direction == "left":
            self.setGeometry(
                global_pos.x(), self.pos().y(),
                rect.width() + (self.pos().x() - global_pos.x()),
                rect.height()
            )
        elif self.resize_direction == "right":
            self.resize(global_pos.x() - self.pos().x(), rect.height())
        elif self.resize_direction == "top":
            self.setGeometry(
                self.pos().x(), global_pos.y(),
                rect.width(),
                rect.height() + (self.pos().y() - global_pos.y())
            )
        elif self.resize_direction == "bottom":
            self.resize(rect.width(), global_pos.y() - self.pos().y())

    def update_cursor(self, pos):
        """Atualiza o cursor do mouse com base na posição."""
        direction = self.get_resize_direction(pos)
        if direction:
            self.setCursor(self.resize_cursor)  # Usa o cursor personalizado
        else:
            self.unsetCursor()  # Restaura o cursor padrão