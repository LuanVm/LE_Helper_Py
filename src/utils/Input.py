from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QPushButton


def estilo_input(tipo=None):
    """Retorna o estilo para QLineEdit baseado no tipo."""
    base_style = """
        QLineEdit {
            border: 1px solid #ccc;
            border-radius: 12px;
            padding: 8px;
            font-size: 13px;
            font-family: 'Open Sans';
            background-color: transparent;
            color: #3C3D37;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            min-height: 26px;
            min-width: 280px;
        }
        QLineEdit:focus {
            border: 1px solid #F3740C;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
        }
    """

    if tipo == "Email":
        # Adapte o estilo para Email se necessário
        return base_style
    elif tipo == "Senha":
        # Adapte o estilo para Senha se necessário
        return base_style
    # Adapte o estilo para outros tipos se necessário
    return base_style


class HoverButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        # Define o estilo inicial do botão
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #EF4765, stop:1 #f58634);
                border: 0;
                border-radius: 12px;
                color: #FFFFFF;
                font-family: 'Segoe UI Black', Roboto, Helvetica, Arial, sans-serif;
                font-size: 12px;
                font-weight: 500;
                padding: 8px 24px;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0.5, y1:0.5, x2:1, y2:1, stop:0 #FF9A5A, stop:1 #e66f34);
                border: 1px solid rgba(255, 255, 255, 0.6);
            }
            QPushButton:focus {
                outline: none;
            }
        """)

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Type.Enter:
            # Quando o mouse entra no botão
            self.setStyleSheet(self.styleSheet().replace("12px", "17px"))
        elif event.type() == QEvent.Type.Leave:
            # Quando o mouse sai do botão
            self.setStyleSheet(self.styleSheet().replace("17px", "12px"))  # Volta ao tamanho original
        return super().eventFilter(obj, event)