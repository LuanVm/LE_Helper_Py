def campo_qline_dark():
    return """
        QLineEdit {
            font-family: 'Segoe UI';
            font-size: 12px;
            color: #e6e3e3;
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
            background-color: #242323;
            color: #808080;
            border: 1px solid #444444;
        }
    """

def campo_qline_light():
    return """
        QLineEdit {
            font-family: 'Segoe UI';
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
            font-family: 'Segoe UI';
            font-size: 13px;
            color: #f0f0f0;
            spacing: 8px;
        }
        QCheckBox:disabled {
            color: #808080;
        }
        QCheckBox::indicator {
            width: 14px;
            height: 14px;
            border: 2px solid #606060;
            border-radius: 4px;
            background: #404040;
        }
        QCheckBox::indicator:hover {
            border-color: #ff9e3d;
            background: #484848;
        }
        QCheckBox::indicator:pressed {
            border-color: #ff6d00;
            background: #505050;
        }
        QCheckBox::indicator:checked {
            background-color: #ff8c00;
            border-color: #ff8c00;
        }
        QCheckBox::indicator:checked:hover {
            background-color: #ff9e3d;
            border-color: #ff9e3d;
        }
        QCheckBox::indicator:checked:pressed {
            background-color: #ff6d00;
            border-color: #ff6d00;
        }
        QCheckBox::indicator:checked:disabled {
            background-color: #806040;
            border-color: #604830;
        }
        QCheckBox::indicator:disabled {
            border-color: #505050;
            background: #303030;
        }
    """

def estilo_check_box_light():
    return """
        QCheckBox {
            font-family: 'Segoe UI';
            font-size: 13px;
            color: #1a1a1a;
            spacing: 8px;
        }
        QCheckBox:disabled {
            color: #a0a0a0;
        }
        QCheckBox::indicator {
            width: 14px;
            height: 14px;
            border: 2px solid #909090;
            border-radius: 4px;
            background: #ffffff;
        }
        QCheckBox::indicator:hover {
            border-color: #ff9e3d;
            background: #f8f8f8;
        }
        QCheckBox::indicator:pressed {
            border-color: #ff6d00;
            background: #f0f0f0;
        }
        QCheckBox::indicator:checked {
            background-color: #ff8c00;
            border-color: #ff8c00;
        }
        QCheckBox::indicator:checked:hover {
            background-color: #ff9e3d;
            border-color: #ff9e3d;
        }
        QCheckBox::indicator:checked:pressed {
            background-color: #ff6d00;
            border-color: #ff6d00;
        }
        QCheckBox::indicator:checked:disabled {
            background-color: #ffd8a8;
            border-color: #e0e0e0;
        }
        QCheckBox::indicator:disabled {
            border-color: #d0d0d0;
            background: #f8f8f8;
        }
    """

def estilo_combo_box_dark():
    return """
        QComboBox {
            background-color: #3d3d3d;
            color: #e6e3e3;
            border: 1px solid #555555;
            padding: 6px 10px;
            border-radius: 6px;
            font-family: 'Segoe UI';
            font-size: 13px;
            text-align: center;
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
            image: url("src/resources/ui/ui_drop_down_dark.png");
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
            color: #e6e3e3;
            border-radius: 4px;
        }

        QComboBox QAbstractItemView::item:hover {
            background-color: #4d4d4d;
            color: #e6e3e3;
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: #ff8c00;
            color: #ffffff;
        }

        QComboBox:disabled {
            background-color: #242323;
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
            font-family: 'Segoe UI';
            font-size: 13px;
            text-align: center;
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
            image: url("src/resources/ui/ui_drop_down_light.png");
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

def estilo_hover(button, dark_mode=False):
    from PyQt6.QtWidgets import QGraphicsDropShadowEffect
    from PyQt6.QtCore import QPropertyAnimation
    from PyQt6.QtGui import QColor

    # Definição das cores de acordo com o modo (dark/light)
    cor_base       = "#2D2D2D" if dark_mode else "#EF4765"
    cor_secundaria = "#404040" if dark_mode else "#f58634"
    cor_hover      = "#606060" if dark_mode else "#FFC2A3"
    cor_texto      = "#FFFFFF"

    # Aplica o estilo básico via stylesheet, incluindo estados hover e pressed
    button.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                stop:0 {cor_base}, 
                stop:1 {cor_secundaria});
            border: none;
            border-radius: 12px;
            color: {cor_texto};
            font-family: 'Segoe UI Black', Roboto, Helvetica, Arial, sans-serif;
            font-size: 12px;
            font-weight: bold;
            padding: 8px 24px;
        }}
        QPushButton:hover {{
            background: qlineargradient(spread:pad, x1:0.5, y1:0.5, x2:1, y2:1, 
                stop:0 {cor_hover}, 
                stop:1 {cor_secundaria});
        }}
        QPushButton:pressed {{
            background: qlineargradient(spread:pad, x1:0.5, y1:0.5, x2:1, y2:1, 
                stop:0 {cor_secundaria}, 
                stop:1 {cor_hover});
            /* Ajuste de padding para simular o efeito de clique */
            padding: 9px 25px;
        }}
        QPushButton:focus {{
            outline: none;
        }}
    """)

    # Cria um efeito de sombra que será usado para simular o brilho animado na borda
    efeito = QGraphicsDropShadowEffect(button)
    efeito.setBlurRadius(20)
    efeito.setOffset(0)  # Para centralizar o brilho ao redor do botão
    efeito.setColor(QColor(255, 255, 255, 0))  # Inicia sem brilho (transparente)
    button.setGraphicsEffect(efeito)

    # Animação na propriedade 'color' do efeito para criar o brilho pulsante
    anim = QPropertyAnimation(efeito, b"color")
    anim.setDuration(2000)  # Duração do ciclo de animação (em milissegundos)
    anim.setStartValue(QColor(255, 255, 255, 0))
    # No meio do ciclo aumenta a opacidade para gerar o brilho
    anim.setKeyValueAt(0.5, QColor(255, 255, 255, 200))
    anim.setEndValue(QColor(255, 255, 255, 0))
    anim.setLoopCount(-1)  # Loop infinito
    anim.start()

def estilo_label_dark():
    return """
        QLabel {
            font-family: 'Segoe UI';
            padding-left: 0.5em;
            font-size: 13px;
            color: #e6e3e3;
        }
    """

def estilo_label_light():
    return """
        QLabel {
            font-family: 'Segoe UI';
            padding-left: 0.5em;
            font-size: 13px;
            color: #1c1c1c;
        }
    """

def estilo_log_light():
    return """
        QTextEdit {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Consolas';
            font-size: 12px;
        }
    """

def estilo_log_dark():
    return """
        QTextEdit {
            background-color: #2d2d2d;
            color: #e6e3e3;
            border: 1px solid #404040;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Consolas';
            font-size: 12px;
        }
    """

def estilo_progress_bar_dark():
    return """
        QProgressBar {
            background-color: #3d3d3d;
            border: 1px solid #555555;
            border-radius: 6px;
            text-align: center;
            font-family: 'Segoe UI';
            font-size: 12px;
            color: #e6e3e3;
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
            font-family: 'Segoe UI';
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
            border: none;
        }

        QWidget#central_widget {
            background-color: #242323;
            border-radius: 12px;
            border: 1px solid #444444;
            margin: 1px;  /* Adiciona margem para evitar artefatos */
        }

        QWidget#barra_titulo {
            background-color: #242323;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            margin: 0px 1px 0px 1px;  /* Alinhamento com a borda arredondada */
        }

        QLabel#titulo {
            font-size: 16px;
            font-family: 'Segoe UI';
            color: #e6e3e3;
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
            border: none;
        }

        QWidget#central_widget {
            background-color: #f4f4f4;
            border-radius: 12px;
            border: 1px solid #cccccc;
            margin: 1px;  /* Adiciona margem para evitar artefatos */
        }

        QWidget#barra_titulo {
            background-color: #f4f4f4;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            margin: 0px 1px 0px 1px;  /* Alinhamento com a borda arredondada */
        }

        QLabel#titulo {
            font-size: 16px;
            font-family: 'Segoe UI';
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
            background-color: #e6e3e3;
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
            color: #e6e3e3;
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

def estilo_tabela_dark():
    return """
        QTableWidget {
            background-color: #2d2d2d;
            color: #e6e3e3;
            border: 1px solid #444444;
            border-radius: 5px;
            gridline-color: #444444;
            font-family: 'Segoe UI';
            font-size: 12px;
        }

        QTableWidget::item {
            border-bottom: 1px solid #444444;
            padding: 5px;
        }

        QTableWidget::item:selected {
            background-color: #ff8c00;
            color: #ffffff;
        }

        QHeaderView::section {
            background-color: #3d3d3d;
            color: #e6e3e3;
            border: 1px solid #444444;
            padding: 5px;
            font-weight: bold;
        }

        QHeaderView::section:hover {
            background-color: #4d4d4d;
        }

        QHeaderView::section:checked {
            background-color: #ff8c00;
        }

        QTableCornerButton::section {
            background-color: #3d3d3d;
            border: 1px solid #444444;
        }
    """

def estilo_tabela_light():
    return """
        QTableWidget {
            background-color: #ffffff;
            color: #1c1c1c;
            border: 1px solid #cccccc;
            border-radius: 5px;
            gridline-color: #e6e3e3;
            font-family: 'Segoe UI';
            font-size: 12px;
        }

        QTableWidget::item {
            border-bottom: 1px solid #e6e3e3;
            padding: 5px;
        }

        QTableWidget::item:selected {
            background-color: #ffd699;
            color: #1c1c1c;
        }

        QHeaderView::section {
            background-color: #f4f4f4;
            color: #1c1c1c;
            border: 1px solid #cccccc;
            padding: 5px;
            font-weight: bold;
        }

        QHeaderView::section:hover {
            background-color: #fff3e0;
        }

        QHeaderView::section:checked {
            background-color: #ffd699;
        }

        QTableCornerButton::section {
            background-color: #f4f4f4;
            border: 1px solid #cccccc;
        }
    """