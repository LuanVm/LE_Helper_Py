from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QLineEdit, QPushButton

def estilo_label():
    return """
        QLabel {
            font-family: 'Open Sans';
            font-size: 12px;
            color: white;
        }
    """

def estilo_group_box():
    return """
        QGroupBox {
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            margin-top: 20px;
        }
        QGroupBox:title {
            padding: 10px;
            font-weight: bold;
            font-size: 14px;
        }
    """

def estilo_text_edit():
    return """
        QTextEdit {
            border: 1px solid #CCCCCC;
            border-radius: 8px;
            background-color: #262525;
            padding: 5px;
        }
    """

def estilo_hover(button):
    """Aplica o estilo de hover a um QPushButton."""
    button.setStyleSheet("""
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
