def estilo_sheet():
    return """
        QMainWindow {
            background-color: transparent;
        }

        QWidget#central_widget {
            background-color: #f4f4f4;
            border-radius: 12px;
            border: 1px solid #cccccc;
        }

        /* Barra de título personalizada */
        QWidget#barra_titulo {
            background-color: #f4f4f4;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }

        /* Estilo moderno para o título */
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

def campo_qline():
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

def estilo_label():
    return """
        QLabel {
            font-family: 'Open Sans';
            padding-left: 0.5em;
            font-size: 13px;
            color: #1c1c1c;
        }
    """

def estilo_combo_box():
    return """
        QComboBox {
            background-color: #ffffff;
            color: #1c1c1c;
            border: 1px solid #cccccc;
            padding: 5px 10px;
            border-radius: 5px;
            font-family: 'Open Sans', sans-serif;
            font-size: 12px;
            selection-background-color: #ffd699;
            selection-color: #1c1c1c;
        }

        QComboBox:hover {
            border: 1px solid #ff8c00;
        }

        QComboBox:focus {
            border: 1px solid #ff8c00;
            background-color: #fff3e0;
        }

        QComboBox::drop-down {
            border: none;
            background-color: transparent;
            width: 30px;
            padding-right: 5px;
        }

        QComboBox::down-arrow {
            image: url("frontend/static/icons/down_arrow.png");
            width: 14px;
            height: 14px;
        }

        QComboBox QAbstractItemView {
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 5px;
            background-color: #ffffff;
            selection-background-color: #ffd699;
            selection-color: #1c1c1c;
        }

        QComboBox QAbstractItemView::item {
            padding: 8px 10px;
            color: #1c1c1c;
            border-radius: 3px;
        }

        QComboBox QAbstractItemView::item:hover {
            background-color: #fff3e0;
            color: #1c1c1c;
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: #ffd699;
            color: #1c1c1c;
        }

        QComboBox:disabled {
            background-color: #f0f0f0;
            color: #a0a0a0;
            border: 1px solid #cccccc;
        }
    """

def estilo_log():
    return """
        background-color: #f4f4f4;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Open Sans', sans-serif;
        font-size: 12px;
        color: #333333;
    """

def estilo_hover(button):
    """Aplica o estilo de hover a um QPushButton."""
    button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #EF4765, stop:1 #f58634);  /* Gradiente laranja principal */
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
            background: qlineargradient(spread:pad, x1:0.5, y1:0.5, x2:1, y2:1, stop:0 #FFC2A3, stop:1 #FFB089);  /* Gradiente laranja mais claro */
            border: 1px solid rgba(255, 255, 255, 0.6);
        }
        QPushButton:focus {
            outline: none;
        }
    """)