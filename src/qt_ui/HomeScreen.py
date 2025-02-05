import colorsys
from pathlib import Path
import random
from functools import partial

from PyQt6.QtCore import (Qt, QPropertyAnimation, pyqtSignal,
                          QParallelAnimationGroup, QEasingCurve, QSize,
                          QEvent)
from PyQt6.QtGui import QPixmap, QMovie, QColor
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout,
                             QPushButton, QGraphicsOpacityEffect, QHBoxLayout)

class HomeScreen(QWidget):
    """Tela inicial com logo e botões animados."""
    boxes_clicked = pyqtSignal(int)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.base_logo_size = (480, 240)
        self.base_boxes_width = 190
        self.base_boxes_height = 75
        self.boxes = []
        self.button_effects = []
        self.setup_ui()

    def setup_ui(self) -> None:
        """Configura a interface do usuário."""
        self.setup_logo()
        self.setup_boxes()
        self.setup_layout()
        self.setup_animations()

    def update_geometry(self) -> None:
        """Atualiza a geometria dos componentes."""
        self.boxes_container.updateGeometry()
        for box in self.boxes:
            box.updateGeometry()
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
                random.randint(220, 255),  # componente vermelho forte
                random.randint(120, 180),  # componente verde moderado
                random.randint(0, 50)      # componente azul baixo
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

        for i, setor in enumerate(setores):
            btn = QPushButton("", self)
            btn.setFixedSize(self.base_boxes_width, self.base_boxes_height)
            btn.setObjectName("sector_button")
            
            # Layout compacto
            layout = QHBoxLayout(btn)
            layout.setContentsMargins(15, 0, 25, 0)
            layout.setSpacing(0)

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

            # Texto centralizado
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

            # Efeito de opacidade para o botão
            btn_opacity = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(btn_opacity)
            btn_opacity.setOpacity(0)
            self.button_effects.append(btn_opacity)

            # Gradiente dinâmico em tons alaranjados com saturação um pouco mais forte
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

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        for idx, btn in enumerate(self.boxes):
            row, col = divmod(idx, 3)
            self.grid_layout.addWidget(btn, row, col)

        self.boxes_container = QWidget()
        self.boxes_container.setLayout(self.grid_layout)

    def eventFilter(self, obj, event):
        """Controla os eventos de hover para animação dos GIFs."""
        if event.type() == QEvent.Type.Enter:
            if obj in self.boxes:
                obj.movie.loopCount = -1
                obj.movie.stopAfterCurrentLoop = False
                obj.movie.start()
            return True

        elif event.type() == QEvent.Type.Leave:
            if obj in self.boxes:
                obj.movie.stopAfterCurrentLoop = True
                obj.movie.frameChanged.connect(self.handleFrameChanged)
            return True

        return super().eventFilter(obj, event)

    def handleFrameChanged(self, frameNumber):
        """Verifica se o último frame foi atingido e, se a flag estiver ativa, pausa o QMovie."""
        movie = self.sender()
        if getattr(movie, 'stopAfterCurrentLoop', False) and frameNumber == movie.frameCount() - 1:
            movie.stop()
            movie.frameChanged.disconnect(self.handleFrameChanged)
            movie.stopAfterCurrentLoop = False

    def setup_layout(self) -> None:
        """Configura o layout principal."""
        main_layout = QVBoxLayout(self)
        # Cria um spacer no topo para animar a subida dos elementos
        self.top_spacer = QWidget(self)
        self.top_spacer.setFixedHeight(60)
        main_layout.addWidget(self.top_spacer)
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(60)
        main_layout.addWidget(self.boxes_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

    def setup_animations(self) -> None:
        """Configura animações de entrada para opacidade e posição (simulada via spacer)."""
        duration = 2000  # 3 segundos

        # --- Animação de opacidade para o logo ---
        self.logo_anim = QPropertyAnimation(self.logo_opacity_effect, b"opacity")
        self.logo_anim.setDuration(duration)
        self.logo_anim.setStartValue(0)
        self.logo_anim.setEndValue(1)
        self.logo_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # --- Animação de opacidade para os botões ---
        self.button_anims = [self.create_button_animation(effect, duration)
                             for effect in self.button_effects]

        # --- Animação do spacer: diminui a altura de 60 para 0 ---
        self.spacer_anim = QPropertyAnimation(self.top_spacer, b"maximumHeight")
        self.spacer_anim.setDuration(duration)
        self.spacer_anim.setStartValue(60)
        self.spacer_anim.setEndValue(0)
        self.spacer_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # --- Grupo de animações paralelas ---
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
