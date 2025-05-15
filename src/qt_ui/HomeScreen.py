import sys, random, colorsys
from pathlib import Path
from functools import partial

from PyQt6.QtCore import (Qt, QPropertyAnimation, pyqtSignal,
                          QParallelAnimationGroup, QEasingCurve, QSize,
                          QEvent, QVariantAnimation, QRect)
from PyQt6.QtGui import QPixmap, QMovie, QFont
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout,
                             QPushButton, QGraphicsOpacityEffect, QHBoxLayout, QApplication)

class HomeScreen(QWidget):
    boxes_clicked = pyqtSignal(int)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.base_logo_size = (400, 200)
        self.base_boxes_width = 190
        self.base_boxes_height = 75
        self.boxes = []
        self.boxes_containers = []
        self.button_effects = []
        self.setup_ui()
        self.setup_inspirational_message()

    def setup_ui(self) -> None:
        """Configura a interface do usuário."""
        self.setup_logo()
        self.setup_boxes()
        self.setup_layout()
        self.setup_animations()
        self.messages = []

    def update_geometry(self) -> None:
        """Atualiza a geometria dos componentes."""
        self.boxes_container.updateGeometry()
        for container in self.boxes_containers:
            container.updateGeometry()
        self.update()

    def setup_logo(self) -> None:
        """Configura o logo com efeito de opacidade."""
        self.logo_label = QLabel(self)
        logo_path = Path(__file__).resolve().parent.parent / "resources" / "images" / "logo_completa.png"
        if pixmap := QPixmap(str(logo_path)):
            scaled_pixmap = pixmap.scaled(self.base_logo_size[0], self.base_logo_size[1],
                                          Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            self.logo_label.setFixedSize(scaled_pixmap.size())
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.logo_opacity_effect = QGraphicsOpacityEffect(self.logo_label)
            self.logo_label.setGraphicsEffect(self.logo_opacity_effect)
            self.logo_opacity_effect.setOpacity(0)

    def setup_boxes(self) -> None:
        """Cria os botões com GIFs e efeitos."""
        def get_base_orange():
            return (
                random.randint(220, 255),
                random.randint(120, 180),
                random.randint(0, 50)
            )

        def adjust_hsl(rgb, h_delta=0, s_delta=0, l_delta=0):
            r, g, b = (x/255.0 for x in rgb)
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            h = (h + h_delta) % 1.0
            s = max(min(s + s_delta, 1.0), 0.4)
            l = max(min(l + l_delta, 1.0), 0.3)
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return (int(r*255), int(g*255), int(b*255))

        setores = [
            "Coleta de faturas", "Planilhamento", "Financeiro",
            "Diretoria", "Indisponível", "Indisponível"
        ]
        gif_mapping = {
            0: "coleta.gif",
            1: "planilha.gif",
            2: "financeiro.gif",
            3: "indisponivel.gif",
            4: "indisponivel.gif",
            5: "indisponivel.gif"
        }

        self.boxes = []
        self.button_effects = []
        self.boxes_containers = []

        for i, setor in enumerate(setores):
            # Container com tamanho fixo de 1.1x (para que o botão expanda até preencher)
            container = QWidget()
            container.setFixedSize(int(self.base_boxes_width * 1.1),
                                   int(self.base_boxes_height * 1.1))
            # NÃO usamos layout interno no container para que o botão não seja reposicionado automaticamente
            # Cria o botão como filho direto do container e o centraliza manualmente:
            btn = QPushButton("", container)
            btn.setMinimumSize(self.base_boxes_width, self.base_boxes_height)
            btn.setMaximumSize(self.base_boxes_width * 2, self.base_boxes_height * 2)
            init_x = (container.width() - self.base_boxes_width) // 2
            init_y = (container.height() - self.base_boxes_height) // 2
            btn.setGeometry(init_x, init_y, self.base_boxes_width, self.base_boxes_height)
            btn.setObjectName("sector_button")
            
            # Layout interno do botão (para imagem e texto) – não altera a geometria externa
            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(10, 0, 10, 0)
            btn_layout.setSpacing(5)

            # Configuração do GIF
            img_label = QLabel(btn)
            img_label.setFixedSize(50, 50)
            img_path = Path(__file__).resolve().parent.parent / "resources" / "icons" / gif_mapping[i]
            movie = QMovie(str(img_path))
            movie.setScaledSize(QSize(50, 50))
            movie.setCacheMode(QMovie.CacheMode.CacheAll)
            movie.jumpToFrame(0)
            img_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            img_label.setStyleSheet("background: transparent; border: none;")
            img_label.setMovie(movie)
            btn.movie = movie
            btn.img_label = img_label
            movie.finished.connect(lambda m=movie: m.jumpToFrame(0))
            btn.installEventFilter(self)

            # Texto do botão
            text_label = QLabel(setor, btn)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-family: 'Segoe UI Black', Roboto, Helvetica, Arial, sans-serif;
                    font-size: 12px;
                    font-weight: 500;
                    font-weight: bold;
                    margin: 0;
                    padding: 0;
                }
            """)
            btn_layout.addWidget(img_label)
            btn_layout.addWidget(text_label, 1)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Efeito de opacidade
            btn_opacity = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(btn_opacity)
            btn_opacity.setOpacity(0)
            self.button_effects.append(btn_opacity)

            # Gradiente dinâmico para visual
            base_orange = get_base_orange()
            start_color = f"#{adjust_hsl(base_orange, s_delta=-0.1, l_delta=0.1)[0]:02x}" \
                          f"{adjust_hsl(base_orange, s_delta=-0.1, l_delta=0.1)[1]:02x}" \
                          f"{adjust_hsl(base_orange, s_delta=-0.1, l_delta=0.1)[2]:02x}"
            end_color = f"#{adjust_hsl(base_orange, s_delta=-0.1, l_delta=-0.05)[0]:02x}" \
                        f"{adjust_hsl(base_orange, s_delta=-0.1, l_delta=-0.05)[1]:02x}" \
                        f"{adjust_hsl(base_orange, s_delta=-0.1, l_delta=-0.05)[2]:02x}"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 {start_color}, stop:1 {end_color});
                    border: none;
                    border-radius: 12px;
                    padding: 0;
                }}
                QPushButton:hover {{
                    border: 1px solid rgba(255, 255, 255, 0.8);
                }}
                QPushButton:focus {{ outline: none; }}
            """)
            
            btn.clicked.connect(partial(self.boxes_clicked.emit, i))
            self.boxes.append(btn)
            self.boxes_containers.append(container)

        # Configura o grid layout para os containers com espaçamentos reduzidos
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)  # Espaçamento entre células
        self.grid_layout.setContentsMargins(5, 5, 5, 5)  # Margens menores
        for idx, container in enumerate(self.boxes_containers):
            row, col = divmod(idx, 3)
            self.grid_layout.addWidget(container, row, col)
        self.boxes_container = QWidget()
        self.boxes_container.setLayout(self.grid_layout)

    def eventFilter(self, obj, event):
        """Anima a geometria do botão ao ocorrer hover."""
        if event.type() == QEvent.Type.Enter:
            if obj in self.boxes:
                if hasattr(obj, 'enter_anim'):
                    obj.enter_anim.stop()
                if hasattr(obj, 'leave_anim'):
                    obj.leave_anim.stop()
                obj.movie.loopCount = -1
                obj.movie.stopAfterCurrentLoop = False
                obj.movie.start()
                if not hasattr(obj, '_orig_geom'):
                    obj._orig_geom = obj.geometry()
                orig_geom = obj._orig_geom
                new_width = int(self.base_boxes_width * 1.1)
                new_height = int(self.base_boxes_height * 1.1)
                delta_w = new_width - orig_geom.width()
                delta_h = new_height - orig_geom.height()
                new_geom = QRect(orig_geom.x() - delta_w // 2,
                                 orig_geom.y() - delta_h // 2,
                                 new_width,
                                 new_height)
                obj.enter_anim = QPropertyAnimation(obj, b"geometry")
                obj.enter_anim.setDuration(200)
                obj.enter_anim.setStartValue(obj.geometry())
                obj.enter_anim.setEndValue(new_geom)
                obj.enter_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
                obj.enter_anim.start()
            return True
        elif event.type() == QEvent.Type.Leave:
            if obj in self.boxes:
                if hasattr(obj, 'leave_anim'):
                    obj.leave_anim.stop()
                if hasattr(obj, 'enter_anim'):
                    obj.enter_anim.stop()
                obj.movie.stopAfterCurrentLoop = True
                obj.movie.frameChanged.connect(self.handleFrameChanged)
                if hasattr(obj, '_orig_geom'):
                    original_geom = obj._orig_geom
                else:
                    original_geom = QRect(obj.geometry().x(),
                                          obj.geometry().y(),
                                          self.base_boxes_width,
                                          self.base_boxes_height)
                current_geom = obj.geometry()
                obj.leave_anim = QPropertyAnimation(obj, b"geometry")
                obj.leave_anim.setDuration(200)
                obj.leave_anim.setStartValue(current_geom)
                obj.leave_anim.setEndValue(original_geom)
                obj.leave_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
                obj.leave_anim.start()
            return True
        return super().eventFilter(obj, event)

    def handleFrameChanged(self, frameNumber):
        """Pausa o QMovie após o último frame, se necessário."""
        movie = self.sender()
        if getattr(movie, 'stopAfterCurrentLoop', False) and frameNumber == movie.frameCount() - 1:
            movie.stop()
            movie.frameChanged.disconnect(self.handleFrameChanged)
            movie.stopAfterCurrentLoop = False

    def setup_layout(self) -> None:
        """Configura o layout principal."""
        main_layout = QVBoxLayout(self)
        self.top_spacer = QWidget(self)
        self.top_spacer.setFixedHeight(60)
        main_layout.addWidget(self.top_spacer)
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(60)
        main_layout.addWidget(self.boxes_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

    def setup_animations(self) -> None:
        """Animação de entrada para logo e botões."""
        duration = 2000  # ms
        self.logo_anim = QPropertyAnimation(self.logo_opacity_effect, b"opacity")
        self.logo_anim.setDuration(duration)
        self.logo_anim.setStartValue(0)
        self.logo_anim.setEndValue(1)
        self.logo_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.button_anims = [self.create_button_animation(effect, duration)
                             for effect in self.button_effects]
        self.spacer_anim = QPropertyAnimation(self.top_spacer, b"maximumHeight")
        self.spacer_anim.setDuration(duration)
        self.spacer_anim.setStartValue(60)
        self.spacer_anim.setEndValue(0)
        self.spacer_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.parallel_anim = QParallelAnimationGroup()
        self.parallel_anim.addAnimation(self.logo_anim)
        self.parallel_anim.addAnimation(self.spacer_anim)
        for anim in self.button_anims:
            self.parallel_anim.addAnimation(anim)
        self.parallel_anim.start()

    def create_button_animation(self, effect, duration):
        """Anima a opacidade dos botões."""
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        return anim

    def apply_styles(self, dark_mode: bool):
        for btn in self.boxes:
            if dark_mode:
                cor_base = "#2D2D2D"
                cor_secundaria = "#404040"
                cor_hover = "#606060"
            else:
                cor_base = "#F05A70"
                cor_secundaria = "#FF8C42"
                cor_hover = "#FFA07A"
            cor_texto = "#FFFFFF"
            btn.setStyleSheet(f"""
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
                    padding: 9px 25px;
                }}
                QPushButton:focus {{
                    outline: none;
                }}
            """)

    def setup_inspirational_message(self):
        """Configura o QLabel com efeito de digitação no canto inferior direito."""
        messages_file = Path(__file__).resolve().parent.parent / "resources" / "misc" / "messages.txt"
        if messages_file.exists():
            with open(messages_file, encoding="utf-8") as f:
                self.messages = [line.strip().strip('",') for line in f if line.strip()]
        self.message_label = QLabel(self)
        self.message_label.setFixedWidth(420)
        self.message_label.setWordWrap(True)
        writing_font = QFont("Script MT", 10)
        self.message_label.setFont(writing_font)
        self.message_label.setStyleSheet("color: #8C8C8C;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.message_label.setText("")
        self.message_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.current_message = random.choice(self.messages)
        duration_per_char = 30  # ms por caractere
        total_duration = len(self.current_message) * duration_per_char
        self.typing_anim = QVariantAnimation(self)
        self.typing_anim.setStartValue(0)
        self.typing_anim.setEndValue(len(self.current_message))
        self.typing_anim.setDuration(total_duration)
        self.typing_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self.typing_anim.valueChanged.connect(self.update_typing_effect)
        self.typing_anim.start()

    def update_typing_effect(self, value):
        """Atualiza o texto do label com efeito de digitação."""
        chars_to_show = int(value)
        self.message_label.setText(self.current_message[:chars_to_show])

    def resizeEvent(self, event):
        """Reposiciona o label da mensagem no canto inferior direito."""
        super().resizeEvent(event)
        margin = 5
        x = self.width() - self.message_label.width() - margin
        y = self.height() - self.message_label.height() - margin
        self.message_label.move(x, y)