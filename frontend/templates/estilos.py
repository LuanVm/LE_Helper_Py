def estilo_sheet():
    return """  
            background-color: #f4f4f4;
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
                color: #1c1c1c;
            }
        """

def estilo_texto_padrao():
    return """
        QLineEdit {
            font-family: 'Open Sans', sans-serif;
            font-size: 12px;
            color: #1c1c1c;
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
            background-color: #f4f4f4;
            color: #ffffff;
            border: 1px solid #ccc;
            padding-left: 0.8em;
            border-radius: 0.25em;
            font-family: 'Open Sans', sans-serif;
            font-size: 12px;
            color: #1c1c1c;
            selection-background-color: rgba(255, 255, 255, 0.3);
        }
        
        QComboBox::drop-down {
            border: none;
            background-color: rgba(255, 255, 255, 0.3);
            width: 2em;
            padding-right: 0.5em;
            border-left: 1px solid #ccc;
        }
        
        QComboBox::down-arrow {
            image: url("frontend/static/images/down_arrow.png");
            width: 14px;
            height: 14px;
            margin-left: auto;
            margin-right: 1.8em;
        }
        
        QComboBox QAbstractItemView {
            border: 1px solid #ccc;
            border-radius: 0.25em;
            padding: 1rem;
            background-color: white;
        }
        
        QComboBox QAbstractItemView::item {
            padding: 0.5em 1em;
            color: #1c1c1c;
        }

        /* Adicionando um pequeno padding-left no texto da ComboBox */
        QComboBox QAbstractItemView::item {
            padding-left: 0.5em;  /* Ajuste para afastar o texto */
        }
    """

def estilo_group_box():
    return """
        QGroupBox {
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
            color: #1c1c1c;
        }
        QGroupBox:title {
            padding: 10px;
            font-weight: bold;
            font-size: 14px;
            color: #1c1c1c;
        }
    """

def estilo_log():
    return """
        background-color: #f4f4f4;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Open Sans', sans-serif;
        font-size: 10px;
        color: #333333;
    """

def estilo_log():
    return """
        background-color: #f4f4f4;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Open Sans', sans-serif;
        font-size: 14px;
        color: #333333;
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
