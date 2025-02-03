import colorsys
from pathlib import Path
import random
from functools import partial

from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtSignal, QParallelAnimationGroup, QEasingCurve
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton, QGraphicsOpacityEffect


class HomeScreen(QWidget):
    """Tela inicial com logo e botões de seleção animados para setores."""
    square_clicked = pyqtSignal(int)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        # Tamanhos base dos elementos
        self.base_logo_size = (480, 240)
        self.base_square_size = 150
        self.squares = []
        self.button_effects = []
        self.setup_ui()

    def setup_ui(self) -> None:
        """Configura a interface do usuário."""
        self.setup_logo()
        self.setup_squares()
        self.setup_layout()
        self.setup_animations()

    def update_geometry(self) -> None:
        """Força a atualização completa da geometria dos componentes."""
        self.squares_container.updateGeometry()
        for square in self.squares:
            square.updateGeometry()
        self.update()

    def setup_logo(self) -> None:
        """Configura e exibe o logo da aplicação com efeito de opacidade."""
        self.logo_label = QLabel(self)
        logo_path = Path(__file__).resolve().parent.parent / "resources" / "icons" / "logo_completa.png"
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            # Usa os tamanhos base
            scaled_pixmap = pixmap.scaled(self.base_logo_size[0], self.base_logo_size[1],
                                          Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            self.logo_label.setFixedSize(scaled_pixmap.size())
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Aplica efeito de opacidade ao logo
        self.logo_opacity_effect = QGraphicsOpacityEffect(self.logo_label)
        self.logo_label.setGraphicsEffect(self.logo_opacity_effect)
        self.logo_opacity_effect.setOpacity(0)

    def setup_squares(self) -> None:
        """Cria os botões quadrados com gradientes personalizados e registra os efeitos de opacidade para animação."""
        def get_base_orange() -> tuple[int, int, int]:
            return (
                random.randint(200, 255),
                random.randint(50, 150),
                random.randint(0, 50)
            )

        def adjust_hsl(rgb: tuple[int, int, int], h_delta: float = 0, s_delta: float = 0, l_delta: float = 0) -> tuple[int, int, int]:
            r, g, b = [x / 255.0 for x in rgb]
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            h = (h + h_delta) % 1.0
            s = max(min(s + s_delta, 1.0), 0.4)
            l = max(min(l + l_delta, 1.0), 0.3)
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return (int(r * 255), int(g * 255), int(b * 255))

        def create_gradient(base_rgb: tuple[int, int, int]) -> tuple[str, str]:
            color1 = adjust_hsl(base_rgb, h_delta=0.02, s_delta=-0.1, l_delta=0.05)
            color2 = adjust_hsl(base_rgb, h_delta=-0.02, s_delta=0.1, l_delta=-0.05)
            return (
                f"#{color1[0]:02x}{color1[1]:02x}{color1[2]:02x}",
                f"#{color2[0]:02x}{color2[1]:02x}{color2[2]:02x}"
            )

        def create_hover_gradient(base_rgb: tuple[int, int, int]) -> tuple[str, str]:
            base_h = colorsys.rgb_to_hls(*(x / 255.0 for x in base_rgb))[0]
            complement_h = (base_h + 0.1) % 1.0
            r1, g1, b1 = colorsys.hls_to_rgb(complement_h, 0.7, 0.6)
            r2, g2, b2 = colorsys.hls_to_rgb(base_h, 0.8, 0.4)
            return (
                f"#{int(r1 * 255):02x}{int(g1 * 255):02x}{int(b1 * 255):02x}",
                f"#{int(r2 * 255):02x}{int(g2 * 255):02x}{int(b2 * 255):02x}"
            )

        setores = [
            "Coleta de faturas", "Planilhamento", "Financeiro",
            "Indisponível", "Indisponível", "Indisponível"
        ]

        self.squares = []
        self.button_effects = []

        for i, setor in enumerate(setores):
            btn = QPushButton(setor, self)
            btn.setFixedSize(self.base_square_size, self.base_square_size)
            btn.setObjectName("sector_button")
            btn_opacity = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(btn_opacity)
            btn_opacity.setOpacity(0)
            self.button_effects.append(btn_opacity)

            base_orange = get_base_orange()
            start_color, end_color = create_gradient(base_orange)
            hover_start, hover_end = create_hover_gradient(base_orange)

            style = f"""
                QPushButton {{
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 {start_color}, stop:1 {end_color});
                    border: 0;
                    border-radius: 12px;
                    color: #FFFFFF;
                    font-family: 'Segoe UI Black', Roboto, Helvetica, Arial, sans-serif;
                    font-size: 12px;
                    font-weight: 500;
                    padding: 8px 24px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: qlineargradient(spread:pad, x1:0.5, y1:0.5, x2:1, y2:1,
                        stop:0 {hover_start}, stop:1 {hover_end});
                    border: 1px solid rgba(255, 255, 255, 0.8);
                }}
                QPushButton:focus {{
                    outline: none;
                }}
            """
            btn.setStyleSheet(style)
            btn.clicked.connect(partial(self.square_clicked.emit, i))
            self.squares.append(btn)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        for idx, btn in enumerate(self.squares):
            row, col = divmod(idx, 3)
            self.grid_layout.addWidget(btn, row, col)

        self.squares_container = QWidget()
        self.squares_container.setLayout(self.grid_layout)

    def setup_layout(self) -> None:
        """Configura o layout principal da tela inicial."""
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.squares_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

    def setup_animations(self) -> None:
        """Configura as animações para o logo e para os botões."""
        self.logo_anim = QPropertyAnimation(self.logo_opacity_effect, b"opacity")
        self.logo_anim.setDuration(1500)
        self.logo_anim.setStartValue(0)
        self.logo_anim.setEndValue(1)
        self.button_anims = [self._create_animation(effect) for effect in self.button_effects]
        self.parallel_anim = QParallelAnimationGroup()
        self.parallel_anim.addAnimation(self.logo_anim)
        for anim in self.button_anims:
            self.parallel_anim.addAnimation(anim)
        self.parallel_anim.start()

    def _create_animation(self, effect: QGraphicsOpacityEffect) -> QPropertyAnimation:
        """Cria uma animação de opacidade para o efeito especificado."""
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(1500)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        return anim