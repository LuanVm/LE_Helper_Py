import colorsys
from pathlib import Path
import random
from functools import partial

from PyQt6.QtCore import (Qt, QPropertyAnimation, pyqtSignal,
                          QParallelAnimationGroup, QEasingCurve, QSize,
                          QEvent, QVariantAnimation, QRect)
from PyQt6.QtGui import QPixmap, QMovie, QFont
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout,
                             QPushButton, QGraphicsOpacityEffect, QHBoxLayout)

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
            # Container para o botão com tamanho fixo que comporta o botão no tamanho máximo (1.1x)
            container = QWidget()
            container.setFixedSize(int(self.base_boxes_width * 1.1), int(self.base_boxes_height * 1.1))
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Botão principal
            btn = QPushButton("", container)
            # Define tamanho mínimo e máximo para permitir animação
            btn.setMinimumSize(self.base_boxes_width, self.base_boxes_height)
            btn.setMaximumSize(self.base_boxes_width * 2, self.base_boxes_height * 2)
            btn.setObjectName("sector_button")
            
            # Layout do botão
            layout = QHBoxLayout(btn)
            layout.setContentsMargins(10, 0, 15, 0)
            layout.setSpacing(5)

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
                    text-align: center;
                    margin: 0;
                    padding: 0;
                }
            """)

            layout.addWidget(img_label)
            layout.addWidget(text_label, 1)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Efeito de opacidade
            btn_opacity = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(btn_opacity)
            btn_opacity.setOpacity(0)
            self.button_effects.append(btn_opacity)

            # Gradiente dinâmico
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
                    border: 0;
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
            container_layout.addWidget(btn)
            self.boxes_containers.append(container)

        # Configurar grid layout com os containers
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        for idx, container in enumerate(self.boxes_containers):
            row, col = divmod(idx, 3)
            self.grid_layout.addWidget(container, row, col)

        self.boxes_container = QWidget()
        self.boxes_container.setLayout(self.grid_layout)

    def eventFilter(self, obj, event):
        """Controla os eventos de hover para animação dos GIFs e redimensionamento do botão."""
        if event.type() == QEvent.Type.Enter:
            if obj in self.boxes:
                # Parar animações anteriores
                if hasattr(obj, 'enter_anim'):
                    obj.enter_anim.stop()
                if hasattr(obj, 'leave_anim'):
                    obj.leave_anim.stop()

                # Iniciar animação do GIF
                obj.movie.loopCount = -1
                obj.movie.stopAfterCurrentLoop = False
                obj.movie.start()

                # Salva a geometria original se ainda não estiver salva
                if not hasattr(obj, '_orig_geom'):
                    obj._orig_geom = obj.geometry()

                orig_geom = obj._orig_geom

                # Calcula o tamanho ampliado (1.1x) usando os valores da base
                enlarged_width = int(self.base_boxes_width * 1.1)
                enlarged_height = int(self.base_boxes_height * 1.1)
                delta_w = enlarged_width - orig_geom.width()
                delta_h = enlarged_height - orig_geom.height()
                new_geom = QRect(orig_geom.x() - delta_w // 2,
                                orig_geom.y() - delta_h // 2,
                                enlarged_width,
                                enlarged_height)

                obj.enter_anim = QPropertyAnimation(obj, b"geometry")
                obj.enter_anim.setDuration(200)
                obj.enter_anim.setStartValue(obj.geometry())
                obj.enter_anim.setEndValue(new_geom)
                obj.enter_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
                obj.enter_anim.start()
            return True

        elif event.type() == QEvent.Type.Leave:
            if obj in self.boxes:
                # Parar animações anteriores
                if hasattr(obj, 'leave_anim'):
                    obj.leave_anim.stop()
                if hasattr(obj, 'enter_anim'):
                    obj.enter_anim.stop()

                # Parar animação do GIF
                obj.movie.stopAfterCurrentLoop = True
                obj.movie.frameChanged.connect(self.handleFrameChanged)

                # Em vez de recalcular a geometria com base em self.base_boxes_width,
                # usa a geometria original salva
                if hasattr(obj, '_orig_geom'):
                    original_geom = obj._orig_geom
                else:
                    original_geom = QRect(obj.geometry().x() + (obj.geometry().width() - self.base_boxes_width) // 2,
                                        obj.geometry().y() + (obj.geometry().height() - self.base_boxes_height) // 2,
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
        """Pausa o QMovie após o último frame, se solicitado."""
        movie = self.sender()
        if getattr(movie, 'stopAfterCurrentLoop', False) and frameNumber == movie.frameCount() - 1:
            movie.stop()
            movie.frameChanged.disconnect(self.handleFrameChanged)
            movie.stopAfterCurrentLoop = False

    def setup_layout(self) -> None:
        """Configura o layout principal."""
        main_layout = QVBoxLayout(self)
        # Spacer no topo para animação de subida
        self.top_spacer = QWidget(self)
        self.top_spacer.setFixedHeight(60)
        main_layout.addWidget(self.top_spacer)
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(60)
        main_layout.addWidget(self.boxes_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

    def setup_animations(self) -> None:
        """Configura animações de entrada para opacidade e posição."""
        duration = 2000  # duração em ms

        # Animação de opacidade para o logo
        self.logo_anim = QPropertyAnimation(self.logo_opacity_effect, b"opacity")
        self.logo_anim.setDuration(duration)
        self.logo_anim.setStartValue(0)
        self.logo_anim.setEndValue(1)
        self.logo_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Animação de opacidade para os botões
        self.button_anims = [self.create_button_animation(effect, duration)
                             for effect in self.button_effects]

        # Animação do spacer: altura de 60 para 0
        self.spacer_anim = QPropertyAnimation(self.top_spacer, b"maximumHeight")
        self.spacer_anim.setDuration(duration)
        self.spacer_anim.setStartValue(60)
        self.spacer_anim.setEndValue(0)
        self.spacer_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Grupo de animações paralelas
        self.parallel_anim = QParallelAnimationGroup()
        self.parallel_anim.addAnimation(self.logo_anim)
        self.parallel_anim.addAnimation(self.spacer_anim)
        for anim in self.button_anims:
            self.parallel_anim.addAnimation(anim)

        self.parallel_anim.start()

    def create_button_animation(self, effect, duration):
        """Cria animação de opacidade para botões com duração especificada."""
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
        """
        Configura o QLabel que exibirá a mensagem inspiradora
        no canto inferior direito com efeito de digitação.
        """
        messages_file = Path(__file__).resolve().parent.parent / "resources" / "misc" / "messages.txt"
        if messages_file.exists():
            # Remove aspas e vírgulas se necessário:
            with open(messages_file, encoding="utf-8") as f:
                self.messages = [line.strip().strip('",') for line in f if line.strip()]

        self.message_label = QLabel(self)
        self.message_label.setFixedWidth(400)
        self.message_label.setWordWrap(True)

        writing_font = QFont("Script MT", 13)
        self.message_label.setFont(writing_font)
        self.message_label.setStyleSheet("color: #8C8C8C;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.message_label.setText("")
        self.message_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.current_message = random.choice(self.messages)
        duration_per_char = 30  # duração em ms para cada caractere
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
        """Reposiciona o label da mensagem no canto inferior direito ao redimensionar."""
        super().resizeEvent(event)
        margin = 5  # margem em pixels
        x = self.width() - self.message_label.width() - margin
        y = self.height() - self.message_label.height() - margin
        self.message_label.move(x, y)