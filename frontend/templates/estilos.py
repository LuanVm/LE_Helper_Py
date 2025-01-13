def estilo_sheet():
    return """  
        background-color: #f4f4f4;  /* Cor de fundo principal da aplicação */
        QGroupBox {
            background-color: rgba(255, 255, 255, 0.9);  /* Fundo semi-transparente */
            border: 1px solid #E0E0E0;  /* Borda sutil */
            border-radius: 8px;  /* Cantos arredondados */
            margin-top: 20px;  /* Margem superior */
        }
        QGroupBox:title {
            padding: 10px;  /* Espaçamento interno do título */
            font-weight: bold;  /* Texto em negrito */
            font-size: 14px;  /* Tamanho da fonte */
            color: #1c1c1c;  /* Cor do texto */
        }
    """

def qLine():
    return """
        QLineEdit {
            font-family: 'Open Sans', sans-serif;  /* Fonte padrão */
            font-size: 12px;  /* Tamanho da fonte */
            color: #1c1c1c;  /* Cor do texto */
            background-color: #ffffff;  /* Fundo branco */
            border: 1px solid #cccccc;  /* Borda cinza */
            border-radius: 5px;  /* Cantos arredondados */
            padding: 5px 10px;  /* Espaçamento interno */
            selection-background-color: #ffa500;  /* Cor de fundo da seleção (laranja) */
            selection-color: #ffffff;  /* Cor do texto selecionado (branco) */
        }

        QLineEdit:focus {
            border: 1px solid #ff8c00;  /* Borda laranja ao focar */
            background-color: #fff3e0;  /* Fundo laranja claro ao focar */
        }

        QLineEdit::placeholder {
            color: #a0a0a0;  /* Cor do texto de placeholder */
            font-style: italic;  /* Texto em itálico */
        }

        QLineEdit:hover {
            border: 1px solid #ff8c00;  /* Borda laranja ao passar o mouse */
        }

        QLineEdit:disabled {
            background-color: #f0f0f0;  /* Fundo cinza quando desabilitado */
            color: #a0a0a0;  /* Texto cinza quando desabilitado */
            border: 1px solid #cccccc;  /* Borda cinza quando desabilitado */
        }
    """

def estilo_label():
    return """
        QLabel {
            font-family: 'Open Sans';  /* Fonte padrão */
            padding-left: 0.5em;  /* Espaçamento à esquerda */
            font-size: 13px;  /* Tamanho da fonte */
            color: #1c1c1c;  /* Cor do texto */
        }
    """

def estilo_combo_box():
    return """
        QComboBox {
            background-color: #ffffff;  /* Fundo branco */
            color: #1c1c1c;  /* Cor do texto */
            border: 1px solid #cccccc;  /* Borda cinza */
            padding: 5px 10px;  /* Espaçamento interno */
            border-radius: 5px;  /* Cantos arredondados */
            font-family: 'Open Sans', sans-serif;  /* Fonte padrão */
            font-size: 12px;  /* Tamanho da fonte */
            selection-background-color: #ffd699;  /* Laranja suave para seleção */
            selection-color: #1c1c1c;  /* Texto escuro quando selecionado */
        }

        QComboBox:hover {
            border: 1px solid #ff8c00;  /* Borda laranja ao passar o mouse */
        }

        QComboBox:focus {
            border: 1px solid #ff8c00;  /* Borda laranja ao focar */
            background-color: #fff3e0;  /* Fundo laranja claro ao focar */
        }

        QComboBox::drop-down {
            border: none;  /* Remove a borda do botão de dropdown */
            background-color: transparent;  /* Fundo transparente */
            width: 30px;  /* Largura do botão de dropdown */
            padding-right: 5px;  /* Espaçamento interno à direita */
        }

        QComboBox::down-arrow {
            image: url("frontend/static/images/down_arrow.png");  /* Ícone personalizado */
            width: 14px;  /* Largura do ícone */
            height: 14px;  /* Altura do ícone */
        }

        QComboBox QAbstractItemView {
            border: 1px solid #cccccc;  /* Borda cinza para a lista suspensa */
            border-radius: 5px;  /* Cantos arredondados */
            padding: 5px;  /* Espaçamento interno */
            background-color: #ffffff;  /* Fundo branco */
            selection-background-color: #ffd699;  /* Laranja suave para seleção */
            selection-color: #1c1c1c;  /* Texto escuro quando selecionado */
        }

        QComboBox QAbstractItemView::item {
            padding: 8px 10px;  /* Espaçamento interno dos itens */
            color: #1c1c1c;  /* Cor do texto */
            border-radius: 3px;  /* Cantos arredondados para os itens */
        }

        QComboBox QAbstractItemView::item:hover {
            background-color: #fff3e0;  /* Fundo laranja claro ao passar o mouse */
            color: #1c1c1c;  /* Cor do texto */
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: #ffd699;  /* Laranja suave para item selecionado */
            color: #1c1c1c;  /* Cor do texto */
        }

        QComboBox:disabled {
            background-color: #f0f0f0;  /* Fundo cinza quando desabilitado */
            color: #a0a0a0;  /* Texto cinza quando desabilitado */
            border: 1px solid #cccccc;  /* Borda cinza quando desabilitado */
        }
    """

def estilo_group_box():
    return """
        QGroupBox {
            background-color: rgba(255, 255, 255, 0.9);  /* Fundo semi-transparente */
            border: 1px solid #E0E0E0;  /* Borda sutil */
            border-radius: 8px;  /* Cantos arredondados */
            margin-top: 20px;  /* Margem superior */
            font-size: 14px;  /* Tamanho da fonte */
            color: #1c1c1c;  /* Cor do texto */
        }
        QGroupBox:title {
            padding: 10px;  /* Espaçamento interno do título */
            font-weight: bold;  /* Texto em negrito */
            font-size: 14px;  /* Tamanho da fonte */
            color: #1c1c1c;  /* Cor do texto */
        }
    """

def estilo_log():
    return """
        background-color: #f4f4f4;  /* Cor de fundo */
        border: 1px solid #cccccc;  /* Borda cinza */
        border-radius: 8px;  /* Cantos arredondados */
        padding: 10px;  /* Espaçamento interno */
        font-family: 'Open Sans', sans-serif;  /* Fonte padrão */
        font-size: 12px;  /* Tamanho da fonte */
        color: #333333;  /* Cor do texto */
    """

def estilo_hover(button):
    """Aplica o estilo de hover a um QPushButton."""
    button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #EF4765, stop:1 #f58634);  /* Gradiente laranja */
            border: 0;  /* Sem borda */
            border-radius: 12px;  /* Cantos arredondados */
            color: #FFFFFF;  /* Texto branco */
            font-family: 'Segoe UI Black', Roboto, Helvetica, Arial, sans-serif;  /* Fonte */
            font-size: 12px;  /* Tamanho da fonte */
            font-weight: 500;  /* Peso da fonte */
            padding: 8px 24px;  /* Espaçamento interno */
            text-align: center;  /* Alinhamento do texto */
        }
        QPushButton:hover {
            background: qlineargradient(spread:pad, x1:0.5, y1:0.5, x2:1, y2:1, stop:0 #FF9A5A, stop:1 #e66f34);  /* Gradiente laranja ao passar o mouse */
            border: 1px solid rgba(255, 255, 255, 0.6);  /* Borda sutil */
        }
        QPushButton:focus {
            outline: none;  /* Remove o contorno ao focar */
        }
    """)