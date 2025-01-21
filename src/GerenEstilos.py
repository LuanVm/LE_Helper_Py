def campo_qline_dark():
    return """
        QLineEdit {
            font-family: 'Open Sans', sans-serif;
            font-size: 12px;
            color: #e0e0e0;
            background-color: #3d3d3d;
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 5px 10px;
            selection-background-color: #ff8c00;
            selection-color: #ffffff;
        }

        QLineEdit:focus {
            border: 1px solid #ff8c00;
            background-color: #4d4d4d;
        }

        QLineEdit::placeholder {
            color: #a0a0a0;
            font-style: italic;
        }

        QLineEdit:hover {
            border: 1px solid #ff8c00;
        }

        QLineEdit:disabled {
            background-color: #2d2d2d;
            color: #808080;
            border: 1px solid #444444;
        }
    """

def campo_qline_light():
    return """
        QLineEdit {
            font-family: 'Open Sans', sans-serif;
            font-size: 12px;
            color: #1c1c1c;
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 5px 10px;
            selection-background-color: #ffa500;
            selection-color: #ffffff;
        }

        QLineEdit:focus {
            border: 1px solid #ff8c00;
            background-color: #fff3e0;
        }

        QLineEdit::placeholder {
            color: #a0a0a0;
            font-style: italic;
        }

        QLineEdit:hover {
            border: 1px solid #ff8c00;
        }

        QLineEdit:disabled {
            background-color: #f0f0f0;
            color: #a0a0a0;
            border: 1px solid #cccccc;
        }
    """

def estilo_check_box_dark():
    return """
        QCheckBox {
            font-family: 'Open Sans', sans-serif;
            font-size: 13px;
            color: #e0e0e0;
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }
        QCheckBox::indicator:hover {
            background-color: #ff8c00;
        }
        QCheckBox::indicator:checked {
            image: url("src/resources/checkbox_checked.png");
        }
        QCheckBox::indicator:unchecked {
            image: url("src/resources/checkbox_unchecked.png");
        }
    """

def estilo_check_box_light():
    return """
        QCheckBox {
            font-family: 'Open Sans', sans-serif;
            font-size: 13px;
            color: #1c1c1c;
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }
        QCheckBox::indicator:hover {
            background-color: #ff8c00;
        }
        QCheckBox::indicator:checked {
            image: url("src/resources/checkbox_checked.png");
        }
        QCheckBox::indicator:unchecked {
            image: url("src/resources/checkbox_unchecked.png");
        }
    """

def estilo_combo_box_dark():
    return """
        QComboBox {
            background-color: #3d3d3d;
            color: #e0e0e0;
            border: 1px solid #555555;
            padding: 6px 10px;
            border-radius: 6px;
            font-family: 'Open Sans', sans-serif;
            font-size: 13px;
            selection-background-color: #ff8c00;
            selection-color: #ffffff;
        }

        QComboBox:hover {
            border: 1px solid #ff8c00;
        }

        QComboBox:focus {
            border: 1px solid #ff8c00;
            background-color: #4d4d4d;
        }

        QComboBox::drop-down {
            border: none;
            background-color: transparent;
            width: 30px;
            padding-right: 6px;
        }

        QComboBox::down-arrow {
            image: url("src/resources/ui_drop_down_dark.png");
            width: 16px;
            height: 16px;
        }

        QComboBox QAbstractItemView {
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 1px;
            background-color: #3d3d3d;
            selection-background-color: #ff8c00;
            selection-color: #ffffff;
            outline: none;
            margin: 0;
        }

        QComboBox QAbstractItemView::item {
            padding: 4px 8px;
            color: #e0e0e0;
            border-radius: 4px;
        }

        QComboBox QAbstractItemView::item:hover {
            background-color: #4d4d4d;
            color: #e0e0e0;
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: #ff8c00;
            color: #ffffff;
        }

        QComboBox:disabled {
            background-color: #2d2d2d;
            color: #808080;
            border: 1px solid #444444;
        }
    """

def estilo_combo_box_light():
    return """
        QComboBox {
            background-color: #FFFFFF;
            color: #1C1C1C;
            border: 1px solid #CCCCCC;
            padding: 6px 10px;
            border-radius: 6px;
            font-family: 'Open Sans', sans-serif;
            font-size: 13px;
            selection-background-color: #FFD699;
            selection-color: #1C1C1C;
        }

        QComboBox:hover {
            border: 1px solid #FF8C00;
        }

        QComboBox:focus {
            border: 1px solid #FF8C00;
            background-color: #FFF3E0;
        }

        QComboBox::drop-down {
            border: none;
            background-color: transparent;
            width: 30px;
            padding-right: 6px;
        }

        QComboBox::down-arrow {
            image: url("src/resources/ui_drop_down_light.png");
            width: 16px;
            height: 16px;
        }

        QComboBox QAbstractItemView {
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 1px;
            background-color: #FFFFFF;
            selection-background-color: #FFD699;
            selection-color: #1C1C1C;
            outline: none;
            margin: 0;
        }

        QComboBox QAbstractItemView::item {
            padding: 4px 8px;
            color: #1C1C1C;
            border-radius: 4px;
        }

        QComboBox QAbstractItemView::item:hover {
            background-color: #FFF3E0;
            color: #1C1C1C;
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: #FFD699;
            color: #1C1C1C;
        }

        QComboBox:disabled {
            background-color: #F0F0F0;
            color: #A0A0A0;
            border: 1px solid #CCCCCC;
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
            background: qlineargradient(spread:pad, x1:0.5, y1:0.5, x2:1, y2:1, stop:0 #FFC2A3, stop:1 #FFB089);
            border: 1px solid rgba(255, 255, 255, 0.6);
        }
        QPushButton:focus {
            outline: none;
        }
    """)

def estilo_label_dark():
    return """
        QLabel {
            font-family: 'Open Sans';
            padding-left: 0.5em;
            font-size: 13px;
            color: #e0e0e0;
        }
    """

def estilo_label_light():
    return """
        QLabel {
            font-family: 'Open Sans';
            padding-left: 0.5em;
            font-size: 13px;
            color: #1c1c1c;
        }
    """

def estilo_log_dark():
    return """
        background-color: #3d3d3d;
        border: 1px solid #555555;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Open Sans', sans-serif;
        font-size: 12px;
        color: #e0e0e0;
    """

def estilo_log_light():
    return """
        background-color: #f4f4f4;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Open Sans', sans-serif;
        font-size: 12px;
        color: #333333;
    """

def estilo_progress_bar_dark():
    return """
        QProgressBar {
            background-color: #3d3d3d;
            border: 1px solid #555555;
            border-radius: 6px;
            text-align: center;
            font-family: 'Open Sans', sans-serif;
            font-size: 12px;
            color: #e0e0e0;
        }

        QProgressBar::chunk {
            background-color: #ff8c00;
            border-radius: 5px;
            border: 1px solid #e67e00;
        }
    """

def estilo_progress_bar_light():
    return """
        QProgressBar {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            border-radius: 6px;
            text-align: center;
            font-family: 'Open Sans', sans-serif;
            font-size: 12px;
            color: #333333;
        }

        QProgressBar::chunk {
            background-color: #ff8c00;
            border-radius: 5px;
            border: 1px solid #e67e00;
        }
    """

def estilo_sheet_dark():
    return """
        QMainWindow {
            background-color: transparent;
        }

        QWidget#central_widget {
            background-color: #2d2d2d;
            border-radius: 12px;
            border: 1px solid #444444;
        }

        QWidget#barra_titulo {
            background-color: #2d2d2d;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }

        QLabel#titulo {
            font-size: 16px;
            font-family: 'Segoe UI', sans-serif;
            color: #e0e0e0;
            font-weight: bold;
            padding-left: 4px;
            background-color: transparent;
        }

        QPushButton#botao_minimizar, QPushButton#botao_maximizar, QPushButton#botao_fechar {
            background-color: transparent;
            border: none;
            padding: 5px;
        }

        QPushButton#botao_minimizar:hover, QPushButton#botao_maximizar:hover {
            background-color: #444444;
            border-radius: 5px;
        }

        QPushButton#botao_fechar:hover {
            background-color: #ff6b6b;
            border-radius: 5px;
        }
    """

def estilo_sheet_light():
    return """
        QMainWindow {
            background-color: transparent;
        }

        QWidget#central_widget {
            background-color: #f4f4f4;
            border-radius: 12px;
            border: 1px solid #cccccc;
        }

        QWidget#barra_titulo {
            background-color: #f4f4f4;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }

        QLabel#titulo {
            font-size: 16px;
            font-family: 'Segoe UI', sans-serif;
            color: #474746;
            font-weight: bold;
            padding-left: 4px;
            background-color: transparent;
        }

        QPushButton#botao_minimizar, QPushButton#botao_maximizar, QPushButton#botao_fechar {
            background-color: transparent;
            border: none;
            padding: 5px;
        }

        QPushButton#botao_minimizar:hover, QPushButton#botao_maximizar:hover {
            background-color: #e0e0e0;
            border-radius: 5px;
        }

        QPushButton#botao_fechar:hover {
            background-color: #ff9494;
            border-radius: 5px;
        }
    """

def estilo_sector_button_dark():
    return """
        QPushButton {
            background-color: #3d3d3d;
            border: 2px solid #555555;
            color: #e0e0e0;
        }
        QPushButton:hover {
            background-color: #4d4d4d;
        }
    """

def estilo_sector_button_light():
    return """
        QPushButton {
            background-color: #FFFFFF;
            border: 2px solid #CCCCCC;
            color: #333333;
        }
        QPushButton:hover {
            background-color: #FFF3E0;
        }
    """