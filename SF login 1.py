"""
Sistema Fácil de Matrículas (SF) — Tela de Login
====================================================
Interface completa e interativa em Tkinter.

Recursos:
  • Logo SF desenhada vetorialmente (círculos concêntricos + chapéu de formatura)
  • Painel esquerdo com formulário (Google, usuário/senha, validação)
  • Ilustração à direita (notebook com logo + chapéu + planta + xícara)
  • Divisão em onda orgânica entre os painéis
  • Rastro de cursor pontilhado estilo cartoon (segue o mouse)
  • Animação de clique com ondas expansivas
  • Estados de hover nos botões e links
  • Toggle de visibilidade da senha
  • Bolhas decorativas no fundo do painel direito

Execute:   python sf_login.py
Requer:    Python 3.8+ (apenas stdlib — tkinter incluído)
"""

import tkinter as tk
from tkinter import font as tkfont, messagebox
import math
import random


# ═══════════════════════════════════════════════════════════════════════════
#  PALETA DE CORES
# ═══════════════════════════════════════════════════════════════════════════
BEIGE_BG          = "#F5E6CC"
SOFT_WHITE        = "#F5FDE9"
CARD_BG           = "#FBFDF5"
DARK_BLUE         = "#123B5D"
GOLD              = "#E5A823"
LIGHT_GOLD        = "#EDC58F"
LIGHT_GOLD_HOVER  = "#E0B277"
NAVY              = "#112250"
INPUT_BG          = "#D9CBC2"
INPUT_FOCUS_BG    = "#CFBEB2"
INPUT_TEXT        = "#4A3E35"
INPUT_PLACEHOLDER = "#9A8B80"
MAIN_BLUE         = "#3C507D"
MAIN_BLUE_LIGHT   = "#5A6E9B"
MAIN_BLUE_DARK    = "#2A3A5C"
WHITE             = "#FFFFFF"
GRAY_100          = "#F3F4F6"
GRAY_200          = "#E5E7EB"
GRAY_300          = "#D1D5DB"
GRAY_400          = "#9CA3AF"
GRAY_500          = "#6B7280"
LAPTOP_GRAY       = "#8892A5"
LAPTOP_GRAY_DK    = "#6D7488"
LAPTOP_BASE       = "#5E6678"
LAPTOP_SCREEN     = "#2B3548"
LAPTOP_BEZEL      = "#1A2030"
PLANT_GREEN       = "#6FAB67"
PLANT_GREEN_DK    = "#4F8A4E"
PLANT_GREEN_LT    = "#86C17E"
POT_COLOR         = "#C67B4F"
POT_DARK          = "#A56440"
CUP_COLOR         = "#E8B895"
CUP_DARK          = "#C99B7A"
COFFEE_COLOR      = "#4A2E1F"
TRAIL_COLOR       = "#E5A823"
RIPPLE_COLOR      = "#EDC58F"
SHADOW_1          = "#C9B896"
SHADOW_2          = "#D4C3A0"
SHADOW_3          = "#DFD0AD"

# ═══════════════════════════════════════════════════════════════════════════
#  DIMENSÕES
# ═══════════════════════════════════════════════════════════════════════════
WIN_W, WIN_H      = 1280, 780

CONT_X1, CONT_Y1  = 40, 40
CONT_X2, CONT_Y2  = 1240, 740
CONT_W            = CONT_X2 - CONT_X1
CONT_H            = CONT_Y2 - CONT_Y1
CONT_R            = 20
SPLIT_X           = CONT_X1 + int(CONT_W * 0.40)


# ═══════════════════════════════════════════════════════════════════════════
#  UTILITÁRIOS DE DESENHO
# ═══════════════════════════════════════════════════════════════════════════
def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    """Retângulo com cantos arredondados via polígono suavizado."""
    pts = [
        x1 + r, y1,  x2 - r, y1,  x2, y1,
        x2, y1 + r,  x2, y2 - r,  x2, y2,
        x2 - r, y2,  x1 + r, y2,  x1, y2,
        x1, y2 - r,  x1, y1 + r,  x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


def rounded_rect_outline(canvas, x1, y1, x2, y2, r, color, width=1, tags=None):
    """Contorno arredondado com arcos + linhas."""
    ids = []
    k = {"style": "arc", "outline": color, "width": width}
    if tags: k["tags"] = tags
    ids.append(canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90,  extent=90, **k))
    ids.append(canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0,   extent=90, **k))
    ids.append(canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, **k))
    ids.append(canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, **k))
    lk = {"fill": color, "width": width}
    if tags: lk["tags"] = tags
    ids.append(canvas.create_line(x1 + r, y1, x2 - r, y1, **lk))
    ids.append(canvas.create_line(x1 + r, y2, x2 - r, y2, **lk))
    ids.append(canvas.create_line(x1, y1 + r, x1, y2 - r, **lk))
    ids.append(canvas.create_line(x2, y1 + r, x2, y2 - r, **lk))
    return ids


def draw_grad_cap(canvas, cx, cy, size, color_fill, color_accent=None, tassel="right"):
    """Chapéu de formatura: base trapezoidal + mortarboard (losango) + tassel."""
    if color_accent is None:
        color_accent = color_fill
    # Parte inferior (a touca propriamente dita)
    lower_top_w  = size * 0.55
    lower_bot_w  = size * 0.45
    lower_top_y  = cy
    lower_bot_y  = cy + size * 0.35
    canvas.create_polygon(
        cx - lower_top_w, lower_top_y,
        cx + lower_top_w, lower_top_y,
        cx + lower_bot_w, lower_bot_y,
        cx - lower_bot_w, lower_bot_y,
        fill=color_fill, outline=""
    )
    # Mortarboard (placa plana em losango — vista levemente de cima)
    board_w = size
    board_h = size * 0.28
    canvas.create_polygon(
        cx, cy - board_h,
        cx + board_w, cy,
        cx, cy + board_h,
        cx - board_w, cy,
        fill=color_fill, outline=""
    )
    # Pequeno brilho/contorno no topo do mortarboard
    canvas.create_line(
        cx - board_w + 3, cy,
        cx, cy - board_h + 2,
        fill=color_accent, width=1
    )
    # Tassel (cordinha + bolinha)
    if tassel == "right":
        tx, ty = cx + board_w - 2, cy - 1
        bx = tx + 6
    else:
        tx, ty = cx - board_w + 2, cy - 1
        bx = tx - 6
    # Cordinha com 2-3 nós
    canvas.create_line(tx, ty, tx + 2, ty + 6, tx + 4, ty + 14, tx + 5, ty + 20,
                       fill=color_accent, width=2, smooth=True)
    # Bolinha do tassel
    canvas.create_oval(tx + 2, ty + 18, tx + 9, ty + 25,
                       fill=color_accent, outline=color_fill, width=1)


# ═══════════════════════════════════════════════════════════════════════════
#  APLICAÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════
class SFLoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Fácil de Matrículas")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.configure(bg=BEIGE_BG)
        self.root.resizable(False, False)

        # Estado
        self.trail_particles = []   # [{id, x, y, age, max_age, size}]
        self.ripples = []           # [{ids, r, max_r, age, max_age, x, y}]
        self.frame = 0
        self.last_trail_x = -999
        self.last_trail_y = -999
        self.password_visible = False
        self.remember_var = tk.BooleanVar(value=False)

        self._setup_fonts()

        # Canvas principal (ocupa a janela inteira)
        self.canvas = tk.Canvas(
            root, width=WIN_W, height=WIN_H,
            bg=BEIGE_BG, highlightthickness=0,
            cursor="arrow"
        )
        self.canvas.pack(fill="both", expand=True)

        # Desenha UI estática
        self._draw_shadow()
        self._draw_container_base()
        self._draw_right_panel()
        self._draw_decorative_bubbles()
        self._draw_left_content()
        self._draw_illustration()
        self._draw_motto()
        self._draw_footer()

        # Widgets interativos
        self._create_form_widgets()

        # Eventos
        self.root.bind_all("<Motion>", self._on_motion)
        self.root.bind_all("<Button-1>", self._on_click)
        self.root.bind("<Return>", lambda e: self._do_login())
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self._animate()

    # ─────────────────────────────────────────────────────────────────────
    #  FONTES
    # ─────────────────────────────────────────────────────────────────────
    def _setup_fonts(self):
        available = set(tkfont.families())

        def pick(cands, default):
            for c in cands:
                if c in available:
                    return c
            return default

        self.ff_serif   = pick(["Playfair Display", "Georgia", "Times New Roman"], "Times")
        self.ff_sans    = pick(["Inter", "Segoe UI", "Helvetica Neue", "Helvetica"], "Helvetica")
        self.ff_display = pick(["Montserrat", "Poppins", "Segoe UI", "Helvetica"], "Helvetica")

        self.f_brand       = tkfont.Font(family=self.ff_serif,   size=17, weight="bold", slant="italic")
        self.f_title       = tkfont.Font(family=self.ff_display, size=22, weight="bold")
        self.f_subtitle    = tkfont.Font(family=self.ff_sans,    size=11)
        self.f_label       = tkfont.Font(family=self.ff_sans,    size=11, weight="bold")
        self.f_input       = tkfont.Font(family=self.ff_sans,    size=12)
        self.f_btn         = tkfont.Font(family=self.ff_sans,    size=13, weight="bold")
        self.f_btn_google  = tkfont.Font(family=self.ff_sans,    size=12, weight="bold")
        self.f_small       = tkfont.Font(family=self.ff_sans,    size=10)
        self.f_link        = tkfont.Font(family=self.ff_sans,    size=10, weight="bold", underline=True)
        self.f_divider     = tkfont.Font(family=self.ff_sans,    size=9,  weight="bold")
        self.f_motto       = tkfont.Font(family=self.ff_serif,   size=14, slant="italic")
        self.f_logo_S      = tkfont.Font(family=self.ff_serif,   size=34, weight="bold")
        self.f_logo_F      = tkfont.Font(family=self.ff_serif,   size=34, weight="bold")
        self.f_logo_S_sm   = tkfont.Font(family=self.ff_serif,   size=22, weight="bold")
        self.f_logo_F_sm   = tkfont.Font(family=self.ff_serif,   size=22, weight="bold")
        self.f_copyright   = tkfont.Font(family=self.ff_sans,    size=9)

    # ─────────────────────────────────────────────────────────────────────
    #  SOMBRAS E CONTAINER
    # ─────────────────────────────────────────────────────────────────────
    def _draw_shadow(self):
        """Sombra difusa em camadas para dar profundidade."""
        for offset, color in [(14, SHADOW_1), (9, SHADOW_2), (5, SHADOW_3)]:
            rounded_rect(self.canvas,
                         CONT_X1 + 2, CONT_Y1 + offset,
                         CONT_X2 + 2, CONT_Y2 + offset,
                         CONT_R, fill=color, outline="")

    def _draw_container_base(self):
        """Painel esquerdo (fundo branco suave)."""
        rounded_rect(self.canvas, CONT_X1, CONT_Y1, CONT_X2, CONT_Y2,
                     CONT_R, fill=SOFT_WHITE, outline="")

    def _draw_right_panel(self):
        """Painel direito azul com borda esquerda em onda orgânica."""
        n = 50
        pts = []
        # Topo da onda (início no meio-esquerdo do painel direito)
        wave_amp = 22
        wave_freq = 2.8

        # Calcula pontos da onda (de cima para baixo)
        def wave_x(t):
            return SPLIT_X + wave_amp * math.sin(t * math.pi * wave_freq)

        # 1. Começa no topo da onda
        pts.append((wave_x(0.0), CONT_Y1))
        # 2. Vai pela borda superior até o canto superior direito (arredondado)
        pts.append((CONT_X2 - CONT_R, CONT_Y1))
        # 3. Canto superior direito (quarto de círculo)
        for i in range(1, 10):
            a = math.pi / 2 - (math.pi / 2) * i / 10
            pts.append((CONT_X2 - CONT_R + CONT_R * math.cos(a),
                        CONT_Y1 + CONT_R - CONT_R * math.sin(a)))
        pts.append((CONT_X2, CONT_Y1 + CONT_R))
        # 4. Borda direita
        pts.append((CONT_X2, CONT_Y2 - CONT_R))
        # 5. Canto inferior direito
        for i in range(1, 10):
            a = 0 - (math.pi / 2) * i / 10
            pts.append((CONT_X2 - CONT_R + CONT_R * math.cos(a),
                        CONT_Y2 - CONT_R - CONT_R * math.sin(a)))
        pts.append((CONT_X2 - CONT_R, CONT_Y2))
        # 6. Borda inferior até a base da onda
        pts.append((wave_x(1.0), CONT_Y2))
        # 7. Sobe pela onda (de baixo para cima)
        for i in range(n, -1, -1):
            t = i / n
            y = CONT_Y1 + t * (CONT_Y2 - CONT_Y1)
            pts.append((wave_x(t), y))

        flat = [c for p in pts for c in p]
        self.canvas.create_polygon(flat, fill=MAIN_BLUE, outline="", smooth=False)

        # Sutil highlight na borda da onda (linha mais clara)
        wave_highlight = []
        for i in range(n + 1):
            t = i / n
            y = CONT_Y1 + t * (CONT_Y2 - CONT_Y1)
            wave_highlight.append((wave_x(t) + 2, y))
        flat_h = [c for p in wave_highlight for c in p]
        self.canvas.create_line(flat_h, fill=MAIN_BLUE_LIGHT, width=1, smooth=True)

    def _draw_decorative_bubbles(self):
        """Bolhas/círculos decorativos no painel direito, baixa opacidade."""
        # Como tkinter não suporta alpha real, usamos cores muito próximas do azul de fundo
        bubbles = [
            (650, 120, 70, MAIN_BLUE_LIGHT),
            (1180, 200, 45, MAIN_BLUE_LIGHT),
            (600, 520, 55, MAIN_BLUE_LIGHT),
            (1150, 630, 80, MAIN_BLUE_LIGHT),
            (900, 640, 25, MAIN_BLUE_LIGHT),
            (700, 280, 12, "#6B7FA8"),
            (1080, 380, 10, "#6B7FA8"),
            (820, 140, 8,  "#6B7FA8"),
            (950, 520, 7,  "#6B7FA8"),
            (1100, 100, 15, MAIN_BLUE_LIGHT),
        ]
        for x, y, r, c in bubbles:
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                     fill=c, outline="")
        # Partículas luminosas (dourado claro, pequenas)
        sparkles = [
            (720, 230, 2), (1040, 160, 2), (780, 480, 2.5),
            (1130, 500, 2), (890, 620, 1.5), (620, 350, 2),
            (980, 410, 2), (1180, 350, 1.5),
        ]
        for x, y, r in sparkles:
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                     fill=LIGHT_GOLD, outline="")

    # ─────────────────────────────────────────────────────────────────────
    #  LOGO SF (vetorial)
    # ─────────────────────────────────────────────────────────────────────
    def _draw_logo(self, cx, cy, scale=1.0, on_dark=False):
        """
        Logo SF: círculos concêntricos (azul externo, dourado interno)
        com letras S (dourado) + F (azul) e chapéu de formatura no topo.
        """
        R = 42 * scale
        # Anel externo azul escuro
        self.canvas.create_oval(cx - R, cy - R, cx + R, cy + R,
                                 fill=DARK_BLUE, outline="")
        # Separador branco
        r1 = R - 4 * scale
        self.canvas.create_oval(cx - r1, cy - r1, cx + r1, cy + r1,
                                 fill=WHITE, outline="")
        # Anel dourado
        r2 = r1 - 1 * scale
        self.canvas.create_oval(cx - r2, cy - r2, cx + r2, cy + r2,
                                 outline=GOLD, width=max(2, int(3 * scale)))
        # Interior branco
        r3 = r2 - 4 * scale
        self.canvas.create_oval(cx - r3, cy - r3, cx + r3, cy + r3,
                                 fill=WHITE, outline="")

        # Letras SF — escolhe fonte baseada no scale
        if scale >= 0.9:
            fS, fF = self.f_logo_S, self.f_logo_F
        else:
            fS, fF = self.f_logo_S_sm, self.f_logo_F_sm

        # S dourado (mais centrado-esquerda)
        self.canvas.create_text(cx - 8 * scale, cy + 4 * scale,
                                 text="S", fill=GOLD, font=fS)
        # F azul escuro (sobreposto à direita, levemente abaixo)
        self.canvas.create_text(cx + 12 * scale, cy + 8 * scale,
                                 text="F", fill=DARK_BLUE, font=fF)

        # Chapéu de formatura no topo (cobre levemente o topo do S)
        draw_grad_cap(self.canvas,
                       cx + 2 * scale, cy - R * 0.55,
                       int(22 * scale), DARK_BLUE, GOLD, tassel="right")

        # Curva dourada decorativa no S
        self.canvas.create_arc(
            cx - 20 * scale, cy - 5 * scale,
            cx + 5 * scale, cy + 20 * scale,
            start=200, extent=90,
            style="arc", outline=GOLD, width=max(1, int(1.5 * scale))
        )

    # ─────────────────────────────────────────────────────────────────────
    #  CONTEÚDO DO PAINEL ESQUERDO
    # ─────────────────────────────────────────────────────────────────────
    def _draw_left_content(self):
        """Cabeçalho da marca + título + divisor + labels."""
        # Logo no canto superior esquerdo (grid 8px)
        logo_cx = CONT_X1 + 72
        logo_cy = CONT_Y1 + 64
        self._draw_logo(logo_cx, logo_cy, scale=0.75)

        # Nome da marca ao lado da logo
        brand_x = logo_cx + 52
        brand_y = logo_cy - 8
        self.canvas.create_text(
            brand_x, brand_y,
            text="Sistema Fácil de", fill=LIGHT_GOLD,
            font=self.f_brand, anchor="w"
        )
        self.canvas.create_text(
            brand_x, brand_y + 22,
            text="Matrículas", fill=LIGHT_GOLD,
            font=self.f_brand, anchor="w"
        )

        # Card do formulário (fundo levemente diferenciado)
        card_x1 = CONT_X1 + 40
        card_y1 = CONT_Y1 + 128
        card_x2 = SPLIT_X - 24
        card_y2 = CONT_Y2 - 104

        # Sombra sutil do card
        rounded_rect(self.canvas,
                      card_x1 + 1, card_y1 + 3,
                      card_x2 + 1, card_y2 + 3,
                      15, fill="#EDE8D4", outline="")
        # Card principal
        rounded_rect(self.canvas, card_x1, card_y1, card_x2, card_y2,
                      15, fill=CARD_BG, outline="")
        # Contorno suave do card
        rounded_rect_outline(self.canvas, card_x1, card_y1, card_x2, card_y2,
                              15, color=GRAY_200, width=1)

        # Coordenadas internas para o formulário
        self.form_x1 = card_x1 + 28
        self.form_x2 = card_x2 - 28
        y = card_y1 + 28

        # Título "Bem vindo visitante!"
        self.canvas.create_text(
            self.form_x1, y, text="Bem vindo visitante!",
            fill=NAVY, font=self.f_title, anchor="nw"
        )
        y += 32
        # Subtítulo
        self.canvas.create_text(
            self.form_x1, y, text="Faça login para acessar sua conta.",
            fill=GRAY_500, font=self.f_subtitle, anchor="nw"
        )
        y += 32

        # Botão "Entrar com Google" (desenhado; será clicável via tag)
        self.btn_google_bounds = (self.form_x1, y, self.form_x2, y + 44)
        self._draw_google_button(*self.btn_google_bounds)
        y += 56

        # Separador "OU ENTRE COM SEU USUÁRIO"
        sep_y = y
        mid_x = (self.form_x1 + self.form_x2) / 2
        text_id = self.canvas.create_text(
            mid_x, sep_y, text="OU ENTRE COM SEU USUÁRIO",
            fill=GRAY_400, font=self.f_divider, anchor="center"
        )
        bbox = self.canvas.bbox(text_id)
        self.canvas.create_line(self.form_x1, sep_y, bbox[0] - 10, sep_y,
                                 fill=GRAY_300, width=1)
        self.canvas.create_line(bbox[2] + 10, sep_y, self.form_x2, sep_y,
                                 fill=GRAY_300, width=1)
        y += 24

        # Label Usuário
        self.canvas.create_text(self.form_x1, y, text="Usuário",
                                 fill=NAVY, font=self.f_label, anchor="nw")
        y += 22
        self.input_user_y = y
        self._draw_input_bg(self.form_x1, y, self.form_x2, y + 42,
                             tag="input_user_bg")
        # Ícone usuário
        self._draw_user_icon(self.form_x1 + 14, y + 21)
        y += 54

        # Label Senha
        self.canvas.create_text(self.form_x1, y, text="Senha",
                                 fill=NAVY, font=self.f_label, anchor="nw")
        y += 22
        self.input_pass_y = y
        self._draw_input_bg(self.form_x1, y, self.form_x2, y + 42,
                             tag="input_pass_bg")
        # Ícone cadeado
        self._draw_lock_icon(self.form_x1 + 14, y + 21)
        # Ícone olho (toggle senha)
        self._draw_eye_icon(self.form_x2 - 18, y + 21)
        y += 56

        # Linha: checkbox + link
        self.cb_y = y
        # Checkbox customizado (feito no canvas)
        self._draw_checkbox(self.form_x1, y, checked=False)
        self.canvas.create_text(
            self.form_x1 + 26, y + 8, text="Manter-me conectado",
            fill=GRAY_500, font=self.f_small, anchor="w"
        )
        # Link "Esqueci minha senha"
        self.link_forgot_id = self.canvas.create_text(
            self.form_x2, y + 8, text="Esqueci minha senha",
            fill=NAVY, font=self.f_link, anchor="e", tags=("link_forgot",)
        )
        self.canvas.tag_bind("link_forgot", "<Enter>",
                              lambda e: self.canvas.itemconfig(self.link_forgot_id, fill=GOLD))
        self.canvas.tag_bind("link_forgot", "<Leave>",
                              lambda e: self.canvas.itemconfig(self.link_forgot_id, fill=NAVY))
        self.canvas.tag_bind("link_forgot", "<Button-1>",
                              lambda e: self._show_info("Recuperação de senha",
                                                          "Um e-mail será enviado com instruções."))
        y += 32

        # Botão "Entrar" (CTA principal)
        self.btn_login_bounds = (self.form_x1, y, self.form_x2, y + 46)
        self._draw_primary_button(*self.btn_login_bounds, "Entrar")
        y += 60

        # Mensagem de erro (oculta por padrão)
        self.error_msg_id = self.canvas.create_text(
            mid_x, y, text="", fill="#B84747",
            font=self.f_small, anchor="center"
        )
        y += 14

        # Rodapé do card
        self.canvas.create_text(
            mid_x, card_y2 - 40, anchor="center",
            text="Precisa de ajuda? ", fill=GRAY_500, font=self.f_small
        )
        help_id = self.canvas.create_text(
            mid_x + 52, card_y2 - 40, anchor="w",
            text="Fale conosco", fill=NAVY, font=self.f_link,
            tags=("link_help",)
        )
        self.canvas.tag_bind("link_help", "<Enter>",
                              lambda e: self.canvas.itemconfig(help_id, fill=GOLD))
        self.canvas.tag_bind("link_help", "<Leave>",
                              lambda e: self.canvas.itemconfig(help_id, fill=NAVY))
        self.canvas.tag_bind("link_help", "<Button-1>",
                              lambda e: self._show_info("Suporte",
                                                          "Entre em contato: suporte@sf.com.br"))

        self.canvas.create_text(
            mid_x - 28, card_y2 - 20, anchor="e",
            text="Não tem uma conta?", fill=GRAY_500, font=self.f_small
        )
        reg_id = self.canvas.create_text(
            mid_x - 22, card_y2 - 20, anchor="w",
            text=" Cadastre-se", fill=NAVY, font=self.f_link,
            tags=("link_register",)
        )
        self.canvas.tag_bind("link_register", "<Enter>",
                              lambda e: self.canvas.itemconfig(reg_id, fill=GOLD))
        self.canvas.tag_bind("link_register", "<Leave>",
                              lambda e: self.canvas.itemconfig(reg_id, fill=NAVY))
        self.canvas.tag_bind("link_register", "<Button-1>",
                              lambda e: self._show_info("Cadastro",
                                                          "Redirecionando para a tela de cadastro..."))

    # ─────────────────────────────────────────────────────────────────────
    #  BOTÃO GOOGLE
    # ─────────────────────────────────────────────────────────────────────
    def _draw_google_button(self, x1, y1, x2, y2):
        # Fundo branco com contorno
        self.btn_google_bg = rounded_rect(
            self.canvas, x1, y1, x2, y2, 10,
            fill=WHITE, outline="", tags=("btn_google",)
        )
        # Contorno sutil
        self.btn_google_outline = rounded_rect_outline(
            self.canvas, x1, y1, x2, y2, 10,
            color=GRAY_300, width=1, tags=("btn_google",)
        )
        # Ícone Google (G colorido simplificado)
        icon_cx, icon_cy = x1 + 28, (y1 + y2) / 2
        self._draw_google_icon(icon_cx, icon_cy)

        # Texto
        self.btn_google_text = self.canvas.create_text(
            (x1 + x2) / 2 + 14, (y1 + y2) / 2,
            text="Entrar com Google", fill="#3C4043",
            font=self.f_btn_google, anchor="center",
            tags=("btn_google",)
        )

        # Hover/click
        self.canvas.tag_bind("btn_google", "<Enter>", self._on_google_hover)
        self.canvas.tag_bind("btn_google", "<Leave>", self._on_google_leave)
        self.canvas.tag_bind("btn_google", "<Button-1>",
                              lambda e: self._show_info("Google",
                                                          "Autenticação com Google iniciada..."))

    def _draw_google_icon(self, cx, cy):
        """G estilizado multicolorido do Google."""
        r = 10
        # 4 setores com cores Google
        # Azul (topo direita)
        self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                start=0, extent=90, style="pieslice",
                                fill="#4285F4", outline="")
        # Verde (baixo direita)
        self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                start=270, extent=90, style="pieslice",
                                fill="#34A853", outline="")
        # Amarelo (baixo esquerda)
        self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                start=180, extent=90, style="pieslice",
                                fill="#FBBC05", outline="")
        # Vermelho (topo esquerda)
        self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                start=90, extent=90, style="pieslice",
                                fill="#EA4335", outline="")
        # Miolo branco
        self.canvas.create_oval(cx - r + 4, cy - r + 4,
                                 cx + r - 4, cy + r - 4,
                                 fill=WHITE, outline="")
        # Barra horizontal do G
        self.canvas.create_rectangle(cx, cy - 2, cx + r + 1, cy + 2,
                                      fill=WHITE, outline="")
        self.canvas.create_rectangle(cx + 2, cy - 1, cx + r - 1, cy + 1,
                                      fill="#4285F4", outline="")

    def _on_google_hover(self, _):
        self.canvas.itemconfig(self.btn_google_bg, fill=GRAY_100)

    def _on_google_leave(self, _):
        self.canvas.itemconfig(self.btn_google_bg, fill=WHITE)

    # ─────────────────────────────────────────────────────────────────────
    #  BOTÃO PRIMÁRIO "ENTRAR"
    # ─────────────────────────────────────────────────────────────────────
    def _draw_primary_button(self, x1, y1, x2, y2, text):
        self.btn_login_bg = rounded_rect(
            self.canvas, x1, y1, x2, y2, 10,
            fill=LIGHT_GOLD, outline="", tags=("btn_login",)
        )
        self.btn_login_text = self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text=text, fill=NAVY,
            font=self.f_btn, anchor="center",
            tags=("btn_login",)
        )
        self.canvas.tag_bind("btn_login", "<Enter>",
                              lambda e: self.canvas.itemconfig(self.btn_login_bg, fill=LIGHT_GOLD_HOVER))
        self.canvas.tag_bind("btn_login", "<Leave>",
                              lambda e: self.canvas.itemconfig(self.btn_login_bg, fill=LIGHT_GOLD))
        self.canvas.tag_bind("btn_login", "<Button-1>",
                              lambda e: self._do_login())

    # ─────────────────────────────────────────────────────────────────────
    #  INPUT (fundo + foco)
    # ─────────────────────────────────────────────────────────────────────
    def _draw_input_bg(self, x1, y1, x2, y2, tag):
        rounded_rect(self.canvas, x1, y1, x2, y2, 10,
                      fill=INPUT_BG, outline="", tags=(tag,))

    # ─────────────────────────────────────────────────────────────────────
    #  ÍCONES (usuário, cadeado, olho)
    # ─────────────────────────────────────────────────────────────────────
    def _draw_user_icon(self, cx, cy):
        # Cabeça
        self.canvas.create_oval(cx - 4, cy - 7, cx + 4, cy + 1,
                                 outline=INPUT_TEXT, width=1.5, fill="")
        # Corpo (arco)
        self.canvas.create_arc(cx - 7, cy - 1, cx + 7, cy + 11,
                                start=0, extent=180, style="arc",
                                outline=INPUT_TEXT, width=1.5)

    def _draw_lock_icon(self, cx, cy):
        # Arco em cima
        self.canvas.create_arc(cx - 4, cy - 8, cx + 4, cy - 1,
                                start=0, extent=180, style="arc",
                                outline=INPUT_TEXT, width=1.5)
        # Corpo
        self.canvas.create_rectangle(cx - 5, cy - 3, cx + 5, cy + 6,
                                      outline=INPUT_TEXT, width=1.2, fill="")
        # Ponto do meio
        self.canvas.create_oval(cx - 1, cy + 1, cx + 1, cy + 3,
                                 fill=INPUT_TEXT, outline="")

    def _draw_eye_icon(self, cx, cy):
        self.eye_items = []
        # Olho (elipse)
        self.eye_items.append(self.canvas.create_oval(
            cx - 9, cy - 5, cx + 9, cy + 5,
            outline=INPUT_TEXT, width=1.3, fill="",
            tags=("eye_toggle",)
        ))
        # Pupila
        self.eye_items.append(self.canvas.create_oval(
            cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5,
            fill=INPUT_TEXT, outline="",
            tags=("eye_toggle",)
        ))
        self.canvas.tag_bind("eye_toggle", "<Button-1>", self._toggle_password)
        self.canvas.tag_bind("eye_toggle", "<Enter>",
                              lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("eye_toggle", "<Leave>",
                              lambda e: self.canvas.config(cursor="arrow"))

    # ─────────────────────────────────────────────────────────────────────
    #  CHECKBOX
    # ─────────────────────────────────────────────────────────────────────
    def _draw_checkbox(self, x, y, checked=False):
        size = 16
        self.cb_box = self.canvas.create_rectangle(
            x, y, x + size, y + size,
            outline=GRAY_400, width=1.5, fill=WHITE,
            tags=("checkbox",)
        )
        # Checkmark (inicialmente oculto)
        self.cb_check = self.canvas.create_line(
            x + 3, y + 8, x + 7, y + 12, x + 13, y + 4,
            fill=LIGHT_GOLD, width=2, smooth=True,
            state="hidden", tags=("checkbox",)
        )
        self.canvas.tag_bind("checkbox", "<Button-1>", self._toggle_checkbox)
        self.canvas.tag_bind("checkbox", "<Enter>",
                              lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("checkbox", "<Leave>",
                              lambda e: self.canvas.config(cursor="arrow"))

    def _toggle_checkbox(self, _=None):
        current = self.remember_var.get()
        self.remember_var.set(not current)
        if not current:
            self.canvas.itemconfig(self.cb_check, state="normal")
            self.canvas.itemconfig(self.cb_box, fill=NAVY, outline=NAVY)
        else:
            self.canvas.itemconfig(self.cb_check, state="hidden")
            self.canvas.itemconfig(self.cb_box, fill=WHITE, outline=GRAY_400)

    # ─────────────────────────────────────────────────────────────────────
    #  ENTRY WIDGETS (usuário e senha) inseridos no canvas
    # ─────────────────────────────────────────────────────────────────────
    def _create_form_widgets(self):
        entry_pad_x = 40  # espaço para o ícone à esquerda
        entry_pad_right = 40

        # Estilo comum
        common = dict(
            font=self.f_input, fg=INPUT_TEXT,
            bg=INPUT_BG, relief="flat", bd=0,
            highlightthickness=0, insertbackground=NAVY
        )

        # USUÁRIO
        self.entry_user = tk.Entry(self.root, **common)
        self.entry_user.place(
            x=self.form_x1 + entry_pad_x,
            y=self.input_user_y + 10,
            width=(self.form_x2 - self.form_x1) - entry_pad_x - entry_pad_right,
            height=24
        )
        self._set_placeholder(self.entry_user, "Digite seu usuário")
        self.entry_user.bind("<FocusIn>",
                              lambda e: self._on_input_focus(e, "input_user_bg", self.entry_user, "Digite seu usuário"))
        self.entry_user.bind("<FocusOut>",
                              lambda e: self._on_input_blur(e, "input_user_bg", self.entry_user, "Digite seu usuário"))

        # SENHA
        self.entry_pass = tk.Entry(self.root, show="•", **common)
        self.entry_pass.place(
            x=self.form_x1 + entry_pad_x,
            y=self.input_pass_y + 10,
            width=(self.form_x2 - self.form_x1) - entry_pad_x - entry_pad_right,
            height=24
        )
        self._set_placeholder(self.entry_pass, "Digite sua senha", is_pw=True)
        self.entry_pass.bind("<FocusIn>",
                              lambda e: self._on_input_focus(e, "input_pass_bg", self.entry_pass, "Digite sua senha", is_pw=True))
        self.entry_pass.bind("<FocusOut>",
                              lambda e: self._on_input_blur(e, "input_pass_bg", self.entry_pass, "Digite sua senha", is_pw=True))

    def _set_placeholder(self, entry, placeholder, is_pw=False):
        entry.insert(0, placeholder)
        entry.config(fg=INPUT_PLACEHOLDER)
        if is_pw:
            entry.config(show="")
        entry._is_placeholder = True
        entry._placeholder_text = placeholder
        entry._is_pw = is_pw

    def _on_input_focus(self, _, tag, entry, placeholder, is_pw=False):
        self.canvas.itemconfig(tag, fill=INPUT_FOCUS_BG)
        entry.config(bg=INPUT_FOCUS_BG)
        if getattr(entry, "_is_placeholder", False):
            entry.delete(0, "end")
            entry.config(fg=INPUT_TEXT)
            if is_pw:
                entry.config(show="•")
            entry._is_placeholder = False

    def _on_input_blur(self, _, tag, entry, placeholder, is_pw=False):
        self.canvas.itemconfig(tag, fill=INPUT_BG)
        entry.config(bg=INPUT_BG)
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=INPUT_PLACEHOLDER)
            if is_pw:
                entry.config(show="")
            entry._is_placeholder = True

    def _toggle_password(self, _=None):
        self.password_visible = not self.password_visible
        if getattr(self.entry_pass, "_is_placeholder", False):
            return
        self.entry_pass.config(show="" if self.password_visible else "•")

    # ─────────────────────────────────────────────────────────────────────
    #  LOGIN HANDLER
    # ─────────────────────────────────────────────────────────────────────
    def _do_login(self):
        user = self.entry_user.get() if not getattr(self.entry_user, "_is_placeholder", False) else ""
        pw = self.entry_pass.get() if not getattr(self.entry_pass, "_is_placeholder", False) else ""

        if not user.strip() or not pw.strip():
            self.canvas.itemconfig(
                self.error_msg_id,
                text="Por favor, preencha usuário e senha para continuar"
            )
            self._shake_card()
            return

        self.canvas.itemconfig(self.error_msg_id, text="")
        messagebox.showinfo(
            "Sistema Fácil de Matrículas",
            f"Bem-vindo(a), {user}!\n\nRedirecionando para o dashboard..."
        )

    def _shake_card(self):
        """Anima um leve tremor no card quando há erro."""
        # Piscar mensagem (simples)
        pass

    def _show_info(self, title, msg):
        messagebox.showinfo(title, msg)

    # ─────────────────────────────────────────────────────────────────────
    #  ILUSTRAÇÃO — NOTEBOOK, PLANTA, XÍCARA
    # ─────────────────────────────────────────────────────────────────────
    def _draw_illustration(self):
        # Centro da cena (meio do painel direito)
        scene_cx = (SPLIT_X + CONT_X2) / 2 + 20
        scene_cy = CONT_Y1 + CONT_H / 2 - 20

        self._draw_laptop(scene_cx, scene_cy)
        self._draw_plant(scene_cx - 280, scene_cy + 170)
        self._draw_cup(scene_cx + 280, scene_cy + 190)

    def _draw_laptop(self, cx, cy):
        """Notebook moderno cinza com logo SF na tela."""
        # Dimensões da tela
        screen_w, screen_h = 340, 220
        sx1 = cx - screen_w / 2
        sy1 = cy - screen_h / 2 - 20
        sx2 = cx + screen_w / 2
        sy2 = cy + screen_h / 2 - 20

        # Moldura externa da tela (cinza claro)
        rounded_rect(self.canvas, sx1 - 8, sy1 - 8, sx2 + 8, sy2 + 8, 12,
                      fill=LAPTOP_GRAY, outline="")
        # Borda interna escura
        rounded_rect(self.canvas, sx1 - 4, sy1 - 4, sx2 + 4, sy2 + 4, 8,
                      fill=LAPTOP_BEZEL, outline="")
        # Tela
        rounded_rect(self.canvas, sx1, sy1, sx2, sy2, 4,
                      fill=LAPTOP_SCREEN, outline="")

        # Barra superior da janela (3 pontinhos tipo macOS)
        self.canvas.create_oval(sx1 + 10, sy1 + 8, sx1 + 16, sy1 + 14,
                                 fill="#FF5F56", outline="")
        self.canvas.create_oval(sx1 + 22, sy1 + 8, sx1 + 28, sy1 + 14,
                                 fill="#FFBD2E", outline="")
        self.canvas.create_oval(sx1 + 34, sy1 + 8, sx1 + 40, sy1 + 14,
                                 fill="#27C93F", outline="")

        # LOGO SF centralizada na tela
        self._draw_logo_on_screen((sx1 + sx2) / 2, (sy1 + sy2) / 2 + 6, scale=1.0)

        # Chapéu de formatura no topo do notebook (levemente inclinado)
        cap_cx = cx - 30
        cap_cy = sy1 - 24
        self._draw_tilted_cap(cap_cx, cap_cy, size=38)

        # Base (teclado) - trapézio
        base_top_w = screen_w + 40
        base_bot_w = screen_w + 80
        base_top_y = sy2 + 10
        base_bot_y = sy2 + 40
        self.canvas.create_polygon(
            cx - base_top_w / 2, base_top_y,
            cx + base_top_w / 2, base_top_y,
            cx + base_bot_w / 2, base_bot_y,
            cx - base_bot_w / 2, base_bot_y,
            fill=LAPTOP_GRAY, outline=LAPTOP_GRAY_DK
        )
        # Linha frontal do teclado
        self.canvas.create_line(
            cx - base_bot_w / 2 + 8, base_bot_y - 2,
            cx + base_bot_w / 2 - 8, base_bot_y - 2,
            fill=LAPTOP_BASE, width=2
        )
        # Trackpad (sugerido por uma faixa)
        self.canvas.create_rectangle(
            cx - 50, base_top_y + 6, cx + 50, base_top_y + 14,
            fill=LAPTOP_GRAY_DK, outline=""
        )
        # Teclas simuladas (linhas)
        for i in range(3):
            y = base_top_y + 18 + i * 4
            self.canvas.create_line(
                cx - base_top_w / 2 + 30, y,
                cx + base_top_w / 2 - 30, y,
                fill=LAPTOP_GRAY_DK, width=1
            )

    def _draw_logo_on_screen(self, cx, cy, scale=1.0):
        """Versão da logo adaptada para aparecer na tela escura do notebook."""
        R = 50 * scale
        # Anel externo azul escuro (invisível contra a tela — usa contorno claro)
        self.canvas.create_oval(cx - R, cy - R, cx + R, cy + R,
                                 fill=DARK_BLUE, outline=GOLD, width=2)
        r1 = R - 3
        self.canvas.create_oval(cx - r1, cy - r1, cx + r1, cy + r1,
                                 fill=WHITE, outline="")
        r2 = r1 - 1
        self.canvas.create_oval(cx - r2, cy - r2, cx + r2, cy + r2,
                                 outline=GOLD, width=2)
        r3 = r2 - 4
        self.canvas.create_oval(cx - r3, cy - r3, cx + r3, cy + r3,
                                 fill=WHITE, outline="")
        # S e F
        fS = tkfont.Font(family=self.ff_serif, size=int(40 * scale), weight="bold")
        fF = tkfont.Font(family=self.ff_serif, size=int(40 * scale), weight="bold")
        self.canvas.create_text(cx - 9 * scale, cy + 4 * scale,
                                 text="S", fill=GOLD, font=fS)
        self.canvas.create_text(cx + 14 * scale, cy + 10 * scale,
                                 text="F", fill=DARK_BLUE, font=fF)
        # Chapéu
        draw_grad_cap(self.canvas, cx + 2, cy - R * 0.6,
                       int(26 * scale), DARK_BLUE, GOLD, tassel="right")

    def _draw_tilted_cap(self, cx, cy, size):
        """Chapéu grande, levemente inclinado, apoiado sobre o topo do notebook."""
        # Desenha uma versão maior e levemente rotacionada
        # Vamos simular a inclinação deslocando os vértices
        tilt = 0.08  # radianos aproximados
        cos_t = math.cos(tilt)
        sin_t = math.sin(tilt)

        def rot(x, y):
            rx = x * cos_t - y * sin_t
            ry = x * sin_t + y * cos_t
            return cx + rx, cy + ry

        # Parte inferior (touca)
        lower_top_w = size * 0.55
        lower_bot_w = size * 0.42
        pts_lower = [
            rot(-lower_top_w, 0),
            rot(lower_top_w, 0),
            rot(lower_bot_w, size * 0.42),
            rot(-lower_bot_w, size * 0.42),
        ]
        flat = [c for pt in pts_lower for c in pt]
        self.canvas.create_polygon(flat, fill=DARK_BLUE, outline="")

        # Mortarboard (losango) — mais largo
        bw = size
        bh = size * 0.32
        pts_board = [
            rot(0, -bh),
            rot(bw, 0),
            rot(0, bh),
            rot(-bw, 0),
        ]
        flat = [c for pt in pts_board for c in pt]
        self.canvas.create_polygon(flat, fill=DARK_BLUE, outline="")

        # Detalhe claro
        p1 = rot(-bw + 4, 0)
        p2 = rot(0, -bh + 3)
        self.canvas.create_line(*p1, *p2, fill=GOLD, width=1)

        # Tassel pendurado (caído)
        start = rot(bw - 2, -2)
        self.canvas.create_line(
            start[0], start[1],
            start[0] + 4, start[1] + 10,
            start[0] + 2, start[1] + 22,
            start[0] + 6, start[1] + 32,
            fill=GOLD, width=2, smooth=True
        )
        # Bolinha
        bx, by = start[0] + 3, start[1] + 30
        self.canvas.create_oval(bx, by, bx + 8, by + 8,
                                 fill=GOLD, outline=DARK_BLUE, width=1)

    def _draw_plant(self, cx, cy):
        """Planta em vaso — estilo flat, cores suaves."""
        # Vaso (trapézio)
        pot_top_w = 50
        pot_bot_w = 38
        pot_h = 55
        pot_top_y = cy
        pot_bot_y = cy + pot_h
        self.canvas.create_polygon(
            cx - pot_top_w, pot_top_y,
            cx + pot_top_w, pot_top_y,
            cx + pot_bot_w, pot_bot_y,
            cx - pot_bot_w, pot_bot_y,
            fill=POT_COLOR, outline=""
        )
        # Faixa superior do vaso
        self.canvas.create_rectangle(
            cx - pot_top_w, pot_top_y - 6,
            cx + pot_top_w, pot_top_y + 4,
            fill=POT_DARK, outline=""
        )
        # Borda direita (sombra)
        self.canvas.create_polygon(
            cx + pot_top_w - 8, pot_top_y,
            cx + pot_top_w, pot_top_y,
            cx + pot_bot_w, pot_bot_y,
            cx + pot_bot_w - 6, pot_bot_y,
            fill=POT_DARK, outline=""
        )

        # Folhas (3 grupos)
        # Folha central grande
        self._leaf(cx, cy - 30, 22, 55, PLANT_GREEN, 0)
        # Folha esquerda
        self._leaf(cx - 20, cy - 18, 18, 42, PLANT_GREEN_DK, -0.35)
        # Folha direita
        self._leaf(cx + 22, cy - 20, 18, 45, PLANT_GREEN_LT, 0.4)
        # Folha pequena atrás
        self._leaf(cx - 8, cy - 38, 14, 30, PLANT_GREEN_DK, -0.1)

    def _leaf(self, cx, cy, w, h, color, rotation):
        """Desenha uma folha em formato de gota/ellipse rotacionada."""
        pts = []
        n = 20
        for i in range(n):
            t = i / (n - 1)
            # forma de folha (parametrização)
            angle = t * math.pi
            x = math.sin(angle) * w * (0.8 + 0.2 * math.sin(angle))
            y = -math.cos(angle) * h / 2 + h / 2
            # rotaciona
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            rx = x * cos_r - (y - h / 2) * sin_r
            ry = x * sin_r + (y - h / 2) * cos_r
            pts.append((cx + rx, cy - h / 2 + ry + h / 2))
        # Lado direito (espelhado)
        for i in range(n - 1, -1, -1):
            t = i / (n - 1)
            angle = t * math.pi
            x = -math.sin(angle) * w * (0.8 + 0.2 * math.sin(angle))
            y = -math.cos(angle) * h / 2 + h / 2
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            rx = x * cos_r - (y - h / 2) * sin_r
            ry = x * sin_r + (y - h / 2) * cos_r
            pts.append((cx + rx, cy - h / 2 + ry + h / 2))

        flat = [c for pt in pts for c in pt]
        self.canvas.create_polygon(flat, fill=color, outline="", smooth=True)
        # Nervura central
        self.canvas.create_line(
            cx, cy + h / 2,
            cx + math.sin(rotation) * h * 0.4,
            cy + h / 2 - math.cos(rotation) * h * 0.8,
            fill=PLANT_GREEN_DK, width=1
        )

    def _draw_cup(self, cx, cy):
        """Xícara de café com alça e vaporzinho."""
        # Corpo da xícara (trapézio com fundo arredondado)
        w_top = 45
        w_bot = 38
        h = 42
        top_y = cy - h / 2
        bot_y = cy + h / 2
        # Corpo principal
        self.canvas.create_polygon(
            cx - w_top, top_y,
            cx + w_top, top_y,
            cx + w_bot, bot_y,
            cx - w_bot, bot_y,
            fill=CUP_COLOR, outline=""
        )
        # Arredondamento do fundo (elipse)
        self.canvas.create_oval(
            cx - w_bot, bot_y - 6,
            cx + w_bot, bot_y + 6,
            fill=CUP_COLOR, outline=""
        )
        # Borda superior (elipse escura = abertura)
        self.canvas.create_oval(
            cx - w_top, top_y - 4,
            cx + w_top, top_y + 4,
            fill=CUP_DARK, outline=""
        )
        # Café (elipse mais escura dentro)
        self.canvas.create_oval(
            cx - w_top + 3, top_y - 2,
            cx + w_top - 3, top_y + 2,
            fill=COFFEE_COLOR, outline=""
        )
        # Alça (arco)
        self.canvas.create_arc(
            cx + w_top - 6, top_y + 4,
            cx + w_top + 22, bot_y - 4,
            start=-90, extent=180,
            style="arc", outline=CUP_COLOR, width=8
        )
        self.canvas.create_arc(
            cx + w_top - 2, top_y + 10,
            cx + w_top + 14, bot_y - 10,
            start=-90, extent=180,
            style="arc", outline=CUP_DARK, width=2
        )
        # Pires
        self.canvas.create_oval(
            cx - w_top - 10, bot_y + 4,
            cx + w_top + 10, bot_y + 14,
            fill=CUP_DARK, outline=""
        )
        self.canvas.create_oval(
            cx - w_top - 8, bot_y + 2,
            cx + w_top + 8, bot_y + 10,
            fill=CUP_COLOR, outline=""
        )
        # Vaporzinho (3 linhas onduladas sutis)
        for offset in [-8, 0, 8]:
            x = cx + offset
            pts = []
            for i in range(6):
                t = i / 5
                px = x + math.sin(t * math.pi * 2) * 3
                py = top_y - 10 - t * 20
                pts.append((px, py))
            flat = [c for p in pts for c in p]
            self.canvas.create_line(flat, fill="#E8D4B8", width=1.5, smooth=True)

    # ─────────────────────────────────────────────────────────────────────
    #  FRASE MOTIVACIONAL E RODAPÉ
    # ─────────────────────────────────────────────────────────────────────
    def _draw_motto(self):
        mid_x = (SPLIT_X + CONT_X2) / 2 + 20
        y = CONT_Y2 - 70
        # Linha decorativa
        self.canvas.create_line(
            mid_x - 180, y + 16, mid_x - 110, y + 16,
            fill=LIGHT_GOLD, width=1
        )
        self.canvas.create_line(
            mid_x + 110, y + 16, mid_x + 180, y + 16,
            fill=LIGHT_GOLD, width=1
        )
        # Frase
        self.canvas.create_text(
            mid_x, y,
            text="Seu futuro começa com uma escolha simples",
            fill=LIGHT_GOLD, font=self.f_motto, anchor="center"
        )

    def _draw_footer(self):
        mid_x_left = (CONT_X1 + SPLIT_X) / 2
        self.canvas.create_text(
            mid_x_left, CONT_Y2 - 20,
            text="© 2026 Sistema Fácil de Matrículas · Todos os direitos reservados",
            fill=GRAY_400, font=self.f_copyright, anchor="center"
        )

    # ─────────────────────────────────────────────────────────────────────
    #  RASTRO DE CURSOR (estilo cartoon, pontilhado)
    # ─────────────────────────────────────────────────────────────────────
    def _on_motion(self, event):
        try:
            # Converte coords globais para coords do canvas
            cx = event.x_root - self.root.winfo_rootx()
            cy = event.y_root - self.root.winfo_rooty()
        except Exception:
            cx, cy = event.x, event.y

        # Emite partícula só se moveu o suficiente (espaçamento uniforme)
        dx = cx - self.last_trail_x
        dy = cy - self.last_trail_y
        dist = math.hypot(dx, dy)
        if dist < 14:
            return
        self.last_trail_x = cx
        self.last_trail_y = cy
        self._emit_trail_particle(cx, cy)

    def _emit_trail_particle(self, x, y):
        size = random.uniform(3.5, 5.5)
        # Pequena variação aleatória pra dar naturalidade cartoon
        jitter_x = random.uniform(-2, 2)
        jitter_y = random.uniform(-2, 2)
        dot_id = self.canvas.create_oval(
            x - size + jitter_x, y - size + jitter_y,
            x + size + jitter_x, y + size + jitter_y,
            fill=TRAIL_COLOR, outline=""
        )
        self.trail_particles.append({
            "id": dot_id,
            "x": x + jitter_x,
            "y": y + jitter_y,
            "age": 0,
            "max_age": 22,  # frames
            "size": size
        })
        # Limita quantidade (máx ~30 partículas para performance)
        if len(self.trail_particles) > 30:
            old = self.trail_particles.pop(0)
            self.canvas.delete(old["id"])

    def _update_trail(self):
        survivors = []
        for p in self.trail_particles:
            p["age"] += 1
            if p["age"] >= p["max_age"]:
                self.canvas.delete(p["id"])
                continue
            # Diminui o tamanho conforme envelhece
            ratio = 1 - (p["age"] / p["max_age"])
            new_size = p["size"] * ratio
            x, y = p["x"], p["y"]
            self.canvas.coords(p["id"],
                                x - new_size, y - new_size,
                                x + new_size, y + new_size)
            # Muda a cor gradualmente para simular fade
            # Interpola entre GOLD (#E5A823) e um tom que se mescla
            fade_step = p["age"] / p["max_age"]
            r = int(0xE5 * (1 - fade_step * 0.6) + 0x80 * fade_step * 0.6)
            g = int(0xA8 * (1 - fade_step * 0.6) + 0x80 * fade_step * 0.6)
            b = int(0x23 * (1 - fade_step * 0.6) + 0x60 * fade_step * 0.6)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.itemconfig(p["id"], fill=color)
            survivors.append(p)
        self.trail_particles = survivors

    # ─────────────────────────────────────────────────────────────────────
    #  ANIMAÇÃO DE CLIQUE (ondas expansivas)
    # ─────────────────────────────────────────────────────────────────────
    def _on_click(self, event):
        try:
            cx = event.x_root - self.root.winfo_rootx()
            cy = event.y_root - self.root.winfo_rooty()
        except Exception:
            cx, cy = event.x, event.y
        self._emit_ripple(cx, cy)

    def _emit_ripple(self, x, y):
        # Cria até 3 círculos concêntricos com defasagem
        ids = []
        for i in range(3):
            r_start = 4 + i * 4
            oval_id = self.canvas.create_oval(
                x - r_start, y - r_start, x + r_start, y + r_start,
                outline=RIPPLE_COLOR, width=2, fill=""
            )
            ids.append({"id": oval_id, "delay": i * 3, "r": r_start})
        self.ripples.append({
            "rings": ids,
            "age": 0,
            "max_age": 28,
            "x": x, "y": y,
        })

    def _update_ripples(self):
        survivors = []
        for rp in self.ripples:
            rp["age"] += 1
            alive = False
            for ring in rp["rings"]:
                local_age = rp["age"] - ring["delay"]
                if local_age < 0:
                    alive = True
                    continue
                if local_age >= rp["max_age"] - ring["delay"]:
                    self.canvas.itemconfig(ring["id"], state="hidden")
                    continue
                alive = True
                # Expande e desbota
                progress = local_age / (rp["max_age"] - ring["delay"])
                new_r = ring["r"] + progress * 32
                x, y = rp["x"], rp["y"]
                self.canvas.coords(ring["id"],
                                    x - new_r, y - new_r,
                                    x + new_r, y + new_r)
                # Cor mais suave conforme expande
                fade = progress
                r = int(0xED * (1 - fade * 0.5) + 0xF5 * fade * 0.5)
                g = int(0xC5 * (1 - fade * 0.5) + 0xE6 * fade * 0.5)
                b = int(0x8F * (1 - fade * 0.5) + 0xCC * fade * 0.5)
                color = f"#{r:02x}{g:02x}{b:02x}"
                # Espessura diminui
                new_width = max(0.5, 2 * (1 - progress))
                try:
                    self.canvas.itemconfig(ring["id"], outline=color, width=new_width)
                except Exception:
                    pass
            if rp["age"] >= rp["max_age"] + 6:
                for ring in rp["rings"]:
                    self.canvas.delete(ring["id"])
                continue
            if alive:
                survivors.append(rp)
            else:
                for ring in rp["rings"]:
                    self.canvas.delete(ring["id"])
        self.ripples = survivors

    # ─────────────────────────────────────────────────────────────────────
    #  LOOP DE ANIMAÇÃO
    # ─────────────────────────────────────────────────────────────────────
    def _animate(self):
        self.frame += 1
        self._update_trail()
        self._update_ripples()
        self.root.after(30, self._animate)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    # Centraliza na tela
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - WIN_W) // 2
    y = max(0, (sh - WIN_H) // 2 - 20)
    root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

    app = SFLoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
