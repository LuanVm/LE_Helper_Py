from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QCursor, QPixmap
import os

class ResizableWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dragging = False
        self.offset = QPoint()
        self.resizing = False
        self.resize_direction = None

        # Carrega o ícone de redimensionamento personalizado
        caminho_base_cursor = os.path.join(os.path.dirname(__file__), "..", "frontend", "static", "icons")
        caminho_icone = os.path.join(caminho_base_cursor, "resize.png")
        self.resize_cursor = self.load_custom_cursor(caminho_icone)

    def load_custom_cursor(self, path):
        """Carrega um cursor personalizado a partir de uma imagem."""
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                return QCursor(pixmap, hotX=8, hotY=8)  # Define o ponto de hotspot do cursor
        return QCursor(Qt.CursorShape.ArrowCursor)  # Retorna o cursor padrão se a imagem não for carregada

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.barra_titulo.geometry().contains(event.pos()):
                self.dragging = True
                self.offset = event.position().toPoint()
            else:
                self.resizing = True
                self.resize_direction = self.get_resize_direction(event.position().toPoint())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.pos() + event.position().toPoint() - self.offset)
        elif self.resizing and self.resize_direction:
            self.resize_window(event.position().toPoint())
        else:
            self.update_cursor(event.position().toPoint())

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