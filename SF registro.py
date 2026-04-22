"""
═══════════════════════════════════════════════════════════════════════
  SISTEMA FÁCIL  ·  Cadastro de Alunos  ·  versão Tkinter
═══════════════════════════════════════════════════════════════════════
 
Versão fiel em Tkinter do design HTML original. Preserva:
  ‣ Layout dividido 50/50 (formulário à esquerda, branding à direita)
  ‣ Paleta completa (#112250, #3C507D, #E0C58F, #FBF8F1 …)
  ‣ Tipografia serif italic + sans moderna
  ‣ Campos dourados arredondados com ícones + foco + hover
  ‣ Toggle mostrar/ocultar senha  ‣ Validação de e-mail / senha
  ‣ Fundo com "gradient mesh"   ‣ Formas decorativas flutuantes
  ‣ Colagem de 3 fotos inclinadas   ‣ Badges  ‣ Estatísticas
  ‣ Animações (flutuar, rotacionar, revelar em cascata)
 
REQUISITOS
    pip install pillow
 
EXECUTAR NO VSCODE
    Tenha o arquivo `sf-logo.png` na mesma pasta que este .py
    (se faltar, um logo de reserva é gerado automaticamente)
    > Run Python File  |  ou no terminal:  python sistema_facil.py
═══════════════════════════════════════════════════════════════════════
"""
 
import os
import math
import random
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
 
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageTk, ImageFont
except ImportError:
    import sys
    print("\n[!] Pillow não encontrado. Instale com:  pip install pillow\n")
    sys.exit(1)
 
try:
    import urllib.request, io
    _HAS_NET = True
except ImportError:
    _HAS_NET = False
 
 
# ═══════════════════════════════════════════════════════════════════
#                       1 · CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════════
APP_TITLE   = "Sistema Fácil — Crie sua conta"
WIN_W       = 1360
WIN_H       = 860
PANEL_W     = WIN_W // 2
 
# ─── Paleta (idêntica ao CSS) ────────────────────────────────────
NAVY_DEEP   = "#112250"
NAVY_MID    = "#3C507D"
NAVY_DARK   = "#2A3960"
NAVY_SOFT   = "#34466F"
GOLD        = "#E0C58F"
GOLD_DEEP   = "#C9A96A"
GOLD_LIGHT  = "#F0DFB8"
CREAM       = "#FBF8F1"
WHITE       = "#FFFFFF"
MUTED       = "#6B7393"
MUTED_SOFT  = "#8C8FA7"
GREEN_OK    = "#1F7A4D"
DOT_GREEN   = "#8FE3B3"
GRAY_BORDER = "#D8DBE8"
 
# ─── Fontes (escolhidas após Tk iniciar) ─────────────────────────
FONT_SERIF  = "Georgia"
FONT_SANS   = "Segoe UI"
 
# ─── Caminhos ────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
CACHE_DIR = os.path.join(HERE, ".sf_cache")
try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except Exception:
    pass
 
# ─── URLs das fotos (baixadas em background; tem fallback local) ─
PHOTO_URLS = [
    "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=500&q=80",
]
 
 
# ═══════════════════════════════════════════════════════════════════
#                       2 · HELPERS GENÉRICOS
# ═══════════════════════════════════════════════════════════════════
def hex_rgb(h):
    """'#112250' → (17, 34, 80)"""
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
 
 
def rounded_rect_points(x1, y1, x2, y2, r):
    """Polígono com pontos duplicados — o truque clássico para
    aproveitar smooth=True e fazer cantos arredondados no Canvas."""
    return [
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1,
        x2,     y1, x2,     y1 + r, x2, y1 + r, x2, y2 - r,
        x2,     y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
        x1 + r, y2, x1 + r, y2, x1,     y2, x1,     y2 - r,
        x1,     y2 - r, x1, y1 + r, x1, y1 + r, x1, y1,
    ]
 
 
def draw_rounded(canvas, x1, y1, x2, y2, r=12, **kw):
    return canvas.create_polygon(
        rounded_rect_points(x1, y1, x2, y2, r),
        smooth=True, **kw
    )
 
 
def round_corners(img, radius):
    """Aplica cantos arredondados a uma PIL Image."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, img.size[0], img.size[1]), radius, fill=255
    )
    img.putalpha(mask)
    return img
 
 
def pick_font(candidates, fallback="TkDefaultFont"):
    """Pega a primeira fonte disponível no sistema."""
    try:
        available = set(tkfont.families())
    except tk.TclError:
        return fallback
    for c in candidates:
        if c in available:
            return c
    return fallback
 
 
# ═══════════════════════════════════════════════════════════════════
#             3 · GERAÇÃO DE IMAGENS COM PIL
# ═══════════════════════════════════════════════════════════════════
def make_right_bg(w, h):
    """Gradient mesh do painel direito (análogo às radial-gradients CSS)."""
    # Base: gradient vertical NAVY_MID → NAVY_SOFT → NAVY_DARK
    seed = Image.new("RGB", (1, 200))
    c1, c2, c3 = hex_rgb(NAVY_MID), hex_rgb(NAVY_SOFT), hex_rgb(NAVY_DARK)
    for y in range(200):
        t = y / 200
        if t < 0.6:
            u = t / 0.6
            col = tuple(int(c1[i] * (1 - u) + c2[i] * u) for i in range(3))
        else:
            u = (t - 0.6) / 0.4
            col = tuple(int(c2[i] * (1 - u) + c3[i] * u) for i in range(3))
        seed.putpixel((0, y), col)
    base = seed.resize((w, h), Image.BICUBIC).convert("RGBA")
 
    # Gold blob top-right
    blob = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(blob)
    cx, cy = int(w * 0.85), int(h * 0.15)
    for i in range(24, 0, -1):
        s = i * 22
        a = int(22 * (i / 24))
        d.ellipse(
            (cx - s, cy - int(s * 0.7), cx + s, cy + int(s * 0.7)),
            fill=hex_rgb(GOLD) + (a,),
        )
    blob = blob.filter(ImageFilter.GaussianBlur(55))
    base = Image.alpha_composite(base, blob)
 
    # Dark blob bottom-left
    blob2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(blob2)
    cx, cy = int(w * 0.1), int(h * 0.9)
    for i in range(24, 0, -1):
        s = i * 24
        a = int(28 * (i / 24))
        d.ellipse(
            (cx - s, cy - int(s * 0.7), cx + s, cy + int(s * 0.7)),
            fill=hex_rgb(NAVY_DEEP) + (a,),
        )
    blob2 = blob2.filter(ImageFilter.GaussianBlur(65))
    base = Image.alpha_composite(base, blob2)
 
    # Ruído sutil (grão de filme) — equivalente ao SVG noise do CSS
    try:
        noise = Image.effect_noise((w, h), 128).convert("RGBA")
        # máscara com baixa opacidade
        mask = Image.new("L", (w, h), 10)  # ~4% alpha
        noise.putalpha(mask)
        base = Image.alpha_composite(base, noise)
    except Exception:
        pass
 
    return base.convert("RGB")
 
 
def make_left_bg(w, h):
    """Fundo creme com textura sutil e círculo decorativo no canto."""
    base = Image.new("RGBA", (w, h), hex_rgb(CREAM) + (255,))
 
    # Círculo decorativo grande no canto superior direito
    deco = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(deco)
    rr = 280
    d.ellipse(
        (w - 130, -100, w - 130 + rr, -100 + rr),
        outline=hex_rgb(GOLD) + (90,), width=1,
    )
    # Segundo anel
    d.ellipse(
        (w - 90, -70, w - 90 + 200, -70 + 200),
        outline=hex_rgb(GOLD_DEEP) + (60,), width=1,
    )
    base = Image.alpha_composite(base, deco)
 
    # Pequeno brilho no canto inferior esquerdo
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(18, 0, -1):
        s = i * 18
        a = int(8 * (i / 18))
        gd.ellipse((-100 - s, h - 100 - s, -100 + s, h - 100 + s),
                   fill=hex_rgb(GOLD) + (a,))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    base = Image.alpha_composite(base, glow)
 
    return base.convert("RGB")
 
 
def make_photo_placeholder(w, h, seed=0):
    """Placeholder artístico para fotos (usado se a internet falhar)."""
    rnd = random.Random(seed * 17 + 3)
    palettes = [
        ((85, 115, 175), (230, 195, 150), (50, 70, 120)),
        ((215, 180, 145), (85, 110, 155), (240, 220, 195)),
        ((70, 100, 150), (220, 185, 145), (35, 55, 100)),
    ]
    p = palettes[seed % len(palettes)]
 
    line = Image.new("RGB", (1, 140))
    for y in range(140):
        t = y / 140
        col = tuple(int(p[0][i] * (1 - t) + p[2][i] * t) for i in range(3))
        line.putpixel((0, y), col)
    img = line.resize((w, h), Image.BICUBIC).convert("RGBA")
 
    # Blob quente
    blob = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(blob)
    bx = rnd.randint(w // 4, 3 * w // 4)
    by = rnd.randint(h // 4, 3 * h // 4)
    for i in range(18, 0, -1):
        s = i * 14
        a = int(22 * (i / 18))
        d.ellipse((bx - s, by - s, bx + s, by + s), fill=p[1] + (a,))
    blob = blob.filter(ImageFilter.GaussianBlur(26))
    img = Image.alpha_composite(img, blob)
 
    # Vinheta sutil
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(vignette).rectangle(
        (0, 0, w, h), outline=(0, 0, 0, 70),
        width=int(min(w, h) * 0.18)
    )
    vignette = vignette.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, vignette)
 
    return img.convert("RGB")
 
 
def make_icon(name, size=18, color=NAVY_DEEP, stroke=2):
    """Desenha ícones line-art simples com supersampling."""
    S = size * 3
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = hex_rgb(color) + (200,)
    sw = stroke * 3
 
    if name == "user":
        d.ellipse([S * 0.32, S * 0.15, S * 0.68, S * 0.5], outline=c, width=sw)
        d.arc([S * 0.18, S * 0.45, S * 0.82, S * 1.05], 180, 360, fill=c, width=sw)
    elif name == "mail":
        d.rounded_rectangle([S * 0.15, S * 0.3, S * 0.85, S * 0.75],
                            radius=int(S * 0.04), outline=c, width=sw)
        d.line([(S * 0.15, S * 0.32), (S * 0.5, S * 0.58), (S * 0.85, S * 0.32)],
               fill=c, width=sw)
    elif name == "check":
        d.ellipse([S * 0.15, S * 0.15, S * 0.85, S * 0.85], outline=c, width=sw)
        d.line([(S * 0.3, S * 0.5), (S * 0.45, S * 0.65), (S * 0.7, S * 0.38)],
               fill=c, width=sw)
    elif name == "lock":
        d.rounded_rectangle([S * 0.22, S * 0.45, S * 0.78, S * 0.85],
                            radius=int(S * 0.05), outline=c, width=sw)
        d.arc([S * 0.3, S * 0.2, S * 0.7, S * 0.6], 180, 360, fill=c, width=sw)
    elif name == "phone":
        d.rounded_rectangle([S * 0.32, S * 0.12, S * 0.68, S * 0.88],
                            radius=int(S * 0.07), outline=c, width=sw)
        d.line([(S * 0.44, S * 0.78), (S * 0.56, S * 0.78)], fill=c, width=sw)
    elif name == "eye":
        d.ellipse([S * 0.1, S * 0.3, S * 0.9, S * 0.7], outline=c, width=sw)
        d.ellipse([S * 0.37, S * 0.37, S * 0.63, S * 0.63], fill=c)
    elif name == "eye-off":
        # Olho com corte diagonal (fechado/ocultar)
        d.ellipse([S * 0.1, S * 0.3, S * 0.9, S * 0.7], outline=c, width=sw)
        d.ellipse([S * 0.37, S * 0.37, S * 0.63, S * 0.63], fill=c)
        # Traço diagonal "cortando" o olho
        d.line([(S * 0.18, S * 0.22), (S * 0.82, S * 0.78)],
               fill=c, width=int(sw * 1.3))
    elif name == "arrow":
        d.line([(S * 0.25, S * 0.5), (S * 0.75, S * 0.5)],
               fill=c, width=int(sw * 1.2))
        d.polygon(
            [(S * 0.58, S * 0.32), (S * 0.82, S * 0.5), (S * 0.58, S * 0.68)],
            fill=c,
        )
 
    return img.resize((size, size), Image.LANCZOS)
 
 
def make_star(size=22, color=GOLD):
    S = size * 3
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = S / 2, S / 2, S * 0.46
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=hex_rgb(color) + (210,))
    return img.resize((size, size), Image.LANCZOS)
 
 
def make_plus(size=26, color=GOLD):
    S = size * 3
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = int(S * 0.13)
    c = hex_rgb(color) + (210,)
    d.line([(S / 2, S * 0.15), (S / 2, S * 0.85)], fill=c, width=w)
    d.line([(S * 0.15, S / 2), (S * 0.85, S / 2)], fill=c, width=w)
    return img.resize((size, size), Image.LANCZOS)
 
 
def make_dot_grid(w, h, color=GOLD, spacing=14, dot=2):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = hex_rgb(color) + (140,)
    for y in range(spacing // 2, h, spacing):
        for x in range(spacing // 2, w, spacing):
            d.ellipse([x - dot, y - dot, x + dot, y + dot], fill=c)
    return img
 
 
def make_gold_square(size, angle, fill=GOLD):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle(
        (0, 0, size, size), radius=10, fill=hex_rgb(fill)
    )
    # Leve sombra dourada
    sh = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((20, 26, size + 20, size + 26), radius=10,
                         fill=hex_rgb(fill) + (80,))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    sh.alpha_composite(img, (20, 20))
    return sh.rotate(angle, resample=Image.BICUBIC, expand=True)
 
 
def make_outline_square(size, angle, color=GOLD, stroke=2):
    S = size + 8
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle(
        (4, 4, size + 4, size + 4), radius=8,
        outline=hex_rgb(color) + (210,), width=stroke,
    )
    return img.rotate(angle, resample=Image.BICUBIC, expand=True)
 
 
def generate_sf_logo_fallback(size=56):
    """Gera um logo de reserva se sf-logo.png estiver ausente."""
    S = size * 3
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, S - 1, S - 1), outline=hex_rgb(NAVY_DEEP), width=int(S * 0.04))
    d.ellipse((int(S * 0.06), int(S * 0.06), int(S * 0.94), int(S * 0.94)),
              outline=hex_rgb(GOLD_DEEP), width=int(S * 0.02))
    font = None
    for candidate in ["georgia.ttf", "Georgia.ttf", "times.ttf",
                      "Times.ttf", "DejaVuSerif.ttf"]:
        try:
            font = ImageFont.truetype(candidate, int(S * 0.55))
            break
        except Exception:
            pass
    if font is None:
        font = ImageFont.load_default()
    d.text((S * 0.22, S * 0.22), "S", fill=hex_rgb(GOLD_DEEP), font=font)
    d.text((S * 0.52, S * 0.22), "F", fill=hex_rgb(NAVY_DEEP), font=font)
    return img.resize((size, size), Image.LANCZOS)
 
 
# ═══════════════════════════════════════════════════════════════════
#                       4 · APLICATIVO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
class SistemaFacilApp:
 
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry(f"{WIN_W}x{WIN_H}")
        root.configure(bg=CREAM)
        root.resizable(False, False)
 
        # Centralizar na tela
        root.update_idletasks()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        x, y = (sw - WIN_W) // 2, max(10, (sh - WIN_H) // 2 - 20)
        root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")
 
        # Fontes
        global FONT_SERIF, FONT_SANS
        FONT_SERIF = pick_font(
            ["Georgia", "Cambria", "Times New Roman", "DejaVu Serif"], "TkDefaultFont"
        )
        FONT_SANS = pick_font(
            ["Segoe UI", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
            "TkDefaultFont",
        )
 
        # Referências fortes para PhotoImage (anti-GC)
        self._imgs = []
        self.entries = {}
 
        # Canvases
        container = tk.Frame(root, bg=CREAM)
        container.pack(fill="both", expand=True)
 
        self.left = tk.Canvas(container, width=PANEL_W, height=WIN_H,
                              bg=CREAM, highlightthickness=0, bd=0)
        self.left.pack(side="left", fill="both", expand=False)
 
        self.right = tk.Canvas(container, width=PANEL_W, height=WIN_H,
                               bg=NAVY_MID, highlightthickness=0, bd=0)
        self.right.pack(side="left", fill="both", expand=False)
 
        # Cache de ícones
        self.icons = {}
        for n in ("user", "mail", "check", "lock", "phone",
                  "eye", "eye-off", "arrow"):
            pil = make_icon(n, size=18, color=NAVY_DEEP, stroke=2)
            tkimg = ImageTk.PhotoImage(pil)
            self.icons[n] = tkimg
            self._imgs.append(tkimg)
        # Ícone branco (arrow do botão)
        pil = make_icon("arrow", size=18, color=WHITE, stroke=2)
        self.icons["arrow_w"] = ImageTk.PhotoImage(pil)
        self._imgs.append(self.icons["arrow_w"])
 
        # Construir painéis
        self._build_left()
        self._build_right()
 
        # Animações
        self._tick = 0
        self._setup_anim_state()
        self.root.after(60, self._animate)
 
        # Revelar em cascata
        self._reveal()
 
        # Download das fotos (background)
        threading.Thread(target=self._download_photos, daemon=True).start()
 
    # ══════════════════════════════════════════════════════════════
    #                    4A · PAINEL ESQUERDO
    # ══════════════════════════════════════════════════════════════
    def _build_left(self):
        c = self.left
 
        # Fundo decorativo
        left_bg = make_left_bg(PANEL_W, WIN_H)
        self.left_bg_tk = ImageTk.PhotoImage(left_bg)
        self._imgs.append(self.left_bg_tk)
        c.create_image(0, 0, image=self.left_bg_tk, anchor="nw")
 
        # ── Brand (logo + textos) ──────────────────────────────
        logo_path = os.path.join(HERE, "sf-logo.png")
        logo_pil = None
        if os.path.exists(logo_path):
            try:
                logo_pil = Image.open(logo_path).convert("RGBA").resize(
                    (56, 56), Image.LANCZOS
                )
            except Exception:
                logo_pil = None
        if logo_pil is None:
            logo_pil = generate_sf_logo_fallback(56)
        self.logo_tk = ImageTk.PhotoImage(logo_pil)
        self._imgs.append(self.logo_tk)
        self._brand_logo = c.create_image(66, 62, image=self.logo_tk, anchor="center")
        self._brand_t1 = c.create_text(
            106, 54, text="Sistema Fácil",
            font=(FONT_SERIF, 16, "bold"), fill=NAVY_DEEP, anchor="w",
        )
        self._brand_t2 = c.create_text(
            106, 76, text="M A T R Í C U L A S",
            font=(FONT_SANS, 8, "bold"), fill=GOLD_DEEP, anchor="w",
        )
 
        # Coordenadas base do conteúdo
        CX = 88   # margem esquerda
        FIELD_W = 440
 
        # ── Eyebrow ("NOVO CADASTRO") ─────────────────────────
        y = 148
        self._eyeb_line = c.create_line(CX, y, CX + 28, y,
                                        fill=GOLD_DEEP, width=1)
        self._eyeb_text = c.create_text(
            CX + 38, y, text="NOVO CADASTRO",
            font=(FONT_SANS, 9, "bold"), fill=GOLD_DEEP, anchor="w",
        )
 
        # ── Título (com "conta" em itálico dourado) ───────────
        y = 170
        title_reg = tkfont.Font(family=FONT_SERIF, size=34)
        t1a = c.create_text(CX, y, text="Crie sua ",
                            font=(FONT_SERIF, 34), fill=NAVY_DEEP, anchor="nw")
        w1 = title_reg.measure("Crie sua ")
        t1b = c.create_text(CX + w1, y, text="conta",
                            font=(FONT_SERIF, 34, "italic"), fill=GOLD_DEEP,
                            anchor="nw")
        t2 = c.create_text(CX, y + 46, text="e comece a estudar",
                           font=(FONT_SERIF, 34), fill=NAVY_DEEP, anchor="nw")
        self._title_ids = (t1a, t1b, t2)
 
        # ── Subtítulo ──────────────────────────────────────────
        self._sub_id = c.create_text(
            CX, 270,
            text=("Junte-se a uma comunidade de aprendizado moderna.\n"
                  "Descubra oportunidades e conquiste seu futuro."),
            font=(FONT_SANS, 10), fill=MUTED, anchor="nw", justify="left",
        )
 
        # ── Campos ────────────────────────────────────────────
        FH = 46                # altura do campo
        LABEL_OFFSET = 18      # do label ao campo
        GAP = 12               # entre um campo e o próximo
 
        y = 340
        y = self._make_field(CX, y, FIELD_W, FH, "NOME COMPLETO",
                             "Seu nome completo", "user", "fullname")
        y += GAP
        y = self._make_field(CX, y, FIELD_W, FH, "E-MAIL",
                             "voce@exemplo.com", "mail", "email")
        y += GAP
        y = self._make_field(CX, y, FIELD_W, FH, "CONFIRME SEU E-MAIL",
                             "Repita o e-mail", "check", "email2")
        y += GAP
 
        # Senhas lado a lado
        half_w = (FIELD_W - 12) // 2
        y_start = y
        self._make_field(CX, y_start, half_w, FH, "SENHA",
                         "Mín. 8 caracteres", "lock", "pass",
                         show="•", eye_toggle=True)
        self._make_field(CX + half_w + 12, y_start, half_w, FH, "CONFIRMAR",
                         "Repita a senha", "lock", "pass2",
                         show="•", eye_toggle=True)
        y = y_start + LABEL_OFFSET + FH + GAP
 
        y = self._make_field(CX, y, FIELD_W, FH, "NÚMERO DE TELEFONE",
                             "(91) 9 9999-9999", "phone", "phone")
        y += 6
 
        # ── Checkbox de termos ────────────────────────────────
        box_x, box_y = CX, y + 6
        self._terms_checked = False
        self._terms_box = draw_rounded(
            c, box_x, box_y, box_x + 18, box_y + 18, 5,
            fill=CREAM, outline=NAVY_DEEP, width=2,
        )
        self._terms_tick = c.create_text(
            box_x + 9, box_y + 8, text="", font=(FONT_SANS, 12, "bold"),
            fill=WHITE,
        )
 
        def toggle_terms(_e=None):
            self._terms_checked = not self._terms_checked
            if self._terms_checked:
                c.itemconfig(self._terms_box, fill=NAVY_DEEP)
                c.itemconfig(self._terms_tick, text="✓")
            else:
                c.itemconfig(self._terms_box, fill=CREAM)
                c.itemconfig(self._terms_tick, text="")
 
        for item in (self._terms_box, self._terms_tick):
            c.tag_bind(item, "<Button-1>", toggle_terms)
 
        self._terms_txt = c.create_text(
            box_x + 28, box_y - 1,
            text=("Ao criar uma conta, concordo com os Termos de\n"
                  "Uso e a Política de Privacidade do Sistema Fácil."),
            font=(FONT_SANS, 9), fill=MUTED, anchor="nw", justify="left",
        )
 
        # ── Botão "Cadastrar" ────────────────────────────────
        btn_y = y + 56
        btn_h = 50
        self._btn_bg = draw_rounded(
            c, CX, btn_y, CX + FIELD_W, btn_y + btn_h, 12,
            fill=NAVY_DEEP, outline=NAVY_DEEP,
        )
        self._btn_shadow = draw_rounded(
            c, CX, btn_y + 4, CX + FIELD_W, btn_y + btn_h + 4, 12,
            fill="", outline=""
        )
        c.tag_lower(self._btn_shadow, self._btn_bg)
        self._btn_text = c.create_text(
            CX + FIELD_W // 2 - 10, btn_y + btn_h // 2, text="Cadastrar",
            font=(FONT_SANS, 13, "bold"), fill=WHITE,
        )
        self._btn_arrow = c.create_image(
            CX + FIELD_W // 2 + 60, btn_y + btn_h // 2,
            image=self.icons["arrow_w"], anchor="center",
        )
 
        def btn_hover(_e=None):
            c.itemconfig(self._btn_bg, fill="#0B1738")
            # leve deslocamento da seta
            c.coords(self._btn_arrow,
                     CX + FIELD_W // 2 + 64, btn_y + btn_h // 2)
 
        def btn_leave(_e=None):
            c.itemconfig(self._btn_bg, fill=NAVY_DEEP)
            c.coords(self._btn_arrow,
                     CX + FIELD_W // 2 + 60, btn_y + btn_h // 2)
 
        for item in (self._btn_bg, self._btn_text, self._btn_arrow):
            c.tag_bind(item, "<Enter>", btn_hover)
            c.tag_bind(item, "<Leave>", btn_leave)
            c.tag_bind(item, "<Button-1>", lambda _e: self._on_submit())
 
        # ── Foot (links) ──────────────────────────────────────
        foot_y = btn_y + btn_h + 28
        self._foot_t1 = c.create_text(
            CX, foot_y, text="Já tem uma conta? ",
            font=(FONT_SANS, 10), fill=MUTED, anchor="w",
        )
        t1w = tkfont.Font(family=FONT_SANS, size=10).measure("Já tem uma conta? ")
        self._foot_link1 = c.create_text(
            CX + t1w, foot_y, text="Entrar",
            font=(FONT_SANS, 10, "bold"), fill=NAVY_DEEP, anchor="w",
        )
        # Sublinhar "Entrar"
        link1_w = tkfont.Font(family=FONT_SANS, size=10, weight="bold").measure("Entrar")
        self._foot_link1_u = c.create_line(
            CX + t1w, foot_y + 10, CX + t1w + link1_w, foot_y + 10,
            fill=GOLD, width=1,
        )
 
        self._foot_link2 = c.create_text(
            CX + FIELD_W, foot_y, text="Precisa de ajuda?",
            font=(FONT_SANS, 10, "bold"), fill=NAVY_DEEP, anchor="e",
        )
        link2_w = tkfont.Font(family=FONT_SANS, size=10, weight="bold").measure("Precisa de ajuda?")
        self._foot_link2_u = c.create_line(
            CX + FIELD_W - link2_w, foot_y + 10, CX + FIELD_W, foot_y + 10,
            fill=GOLD, width=1,
        )
 
        # Hover dos links
        def hover_link(item, normal):
            def enter(_e=None): c.itemconfig(item, fill=GOLD_DEEP)
            def leave(_e=None): c.itemconfig(item, fill=normal)
            return enter, leave
 
        e1, l1 = hover_link(self._foot_link1, NAVY_DEEP)
        c.tag_bind(self._foot_link1, "<Enter>", e1)
        c.tag_bind(self._foot_link1, "<Leave>", l1)
        c.tag_bind(self._foot_link1, "<Button-1>",
                   lambda _e: messagebox.showinfo("Entrar", "Função de login ainda não implementada."))
 
        e2, l2 = hover_link(self._foot_link2, NAVY_DEEP)
        c.tag_bind(self._foot_link2, "<Enter>", e2)
        c.tag_bind(self._foot_link2, "<Leave>", l2)
        c.tag_bind(self._foot_link2, "<Button-1>",
                   lambda _e: messagebox.showinfo("Ajuda", "Entre em contato: ajuda@sistemafacil.com.br"))
 
        # ── Copyright ─────────────────────────────────────────
        self._copyr = c.create_text(
            CX, WIN_H - 28,
            text="© 2026 Sistema Fácil de Matrículas · Todos os direitos reservados",
            font=(FONT_SANS, 8), fill=MUTED, anchor="w",
        )
 
    # ─────────────── helper: criar um campo completo ───────────
    def _make_field(self, x, y, w, h, label, placeholder, icon_name, key,
                    show=None, eye_toggle=False):
        c = self.left
 
        # Label
        c.create_text(x, y, text=label, font=(FONT_SANS, 9, "bold"),
                      fill=NAVY_DEEP, anchor="nw")
 
        yf = y + 18
        bg = draw_rounded(c, x, yf, x + w, yf + h, 11,
                          fill=GOLD, outline=GOLD)
 
        # Ícone
        icon_img = self.icons[icon_name]
        c.create_image(x + 18, yf + h // 2, image=icon_img, anchor="center")
 
        # Entry widget real
        eye_width = 30 if eye_toggle else 0
        entry = tk.Entry(
            c, bd=0, bg=GOLD, fg=NAVY_DEEP,
            font=(FONT_SANS, 12),
            insertbackground=NAVY_DEEP, highlightthickness=0,
            show="" if not show else show,
        )
        c.create_window(
            x + 38, yf + h // 2, window=entry,
            width=w - 52 - eye_width, height=h - 16, anchor="w",
        )
 
        # Placeholder simulado
        ph_color = MUTED_SOFT
 
        def set_placeholder():
            entry.delete(0, "end")
            entry.configure(fg=ph_color, show="")
            entry.insert(0, placeholder)
            entry._placeholder_on = True  # marker
 
        def clear_placeholder():
            if getattr(entry, "_placeholder_on", False):
                entry.delete(0, "end")
                entry.configure(fg=NAVY_DEEP)
                if show and not getattr(entry, "_eye_visible", False):
                    entry.configure(show=show)
                entry._placeholder_on = False
 
        def on_focus_in(_e=None):
            clear_placeholder()
            c.itemconfig(bg, fill="#FFFBF1", outline=NAVY_DEEP)
            entry.configure(bg="#FFFBF1")
 
        def on_focus_out(_e=None):
            if entry.get() == "":
                set_placeholder()
            c.itemconfig(bg, fill=GOLD, outline=GOLD)
            entry.configure(bg=GOLD)
 
        def on_hover(_e=None):
            if c.focus_get() is not entry:
                c.itemconfig(bg, fill=GOLD_LIGHT)
                entry.configure(bg=GOLD_LIGHT)
 
        def on_leave(_e=None):
            if c.focus_get() is not entry:
                c.itemconfig(bg, fill=GOLD, outline=GOLD)
                entry.configure(bg=GOLD)
 
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Enter>", on_hover)
        entry.bind("<Leave>", on_leave)
        c.tag_bind(bg, "<Enter>", on_hover)
        c.tag_bind(bg, "<Leave>", on_leave)
        c.tag_bind(bg, "<Button-1>", lambda _e: entry.focus_set())
 
        set_placeholder()
 
        # Toggle olho
        if eye_toggle:
            entry._eye_visible = False
            eye_lbl = tk.Label(c, image=self.icons["eye"], bg=GOLD,
                               cursor="hand2", bd=0)
            c.create_window(x + w - 18, yf + h // 2,
                            window=eye_lbl, anchor="center")
 
            def toggle_eye(_e=None):
                entry._eye_visible = not entry._eye_visible
                if entry._eye_visible:
                    if not getattr(entry, "_placeholder_on", False):
                        entry.configure(show="")
                    eye_lbl.configure(image=self.icons["eye-off"])
                else:
                    if not getattr(entry, "_placeholder_on", False):
                        entry.configure(show=show)
                    eye_lbl.configure(image=self.icons["eye"])
 
            eye_lbl.bind("<Button-1>", toggle_eye)
 
            # Sobrescrever handlers para manter cor do label do olho sincronizada
            def _sync(color):
                eye_lbl.configure(bg=color)
 
            def on_focus_in_eye(_e=None):
                on_focus_in(_e)
                _sync("#FFFBF1")
 
            def on_focus_out_eye(_e=None):
                on_focus_out(_e)
                _sync(GOLD)
 
            def on_hover_eye(_e=None):
                on_hover(_e)
                if c.focus_get() is not entry:
                    _sync(GOLD_LIGHT)
 
            def on_leave_eye(_e=None):
                on_leave(_e)
                if c.focus_get() is not entry:
                    _sync(GOLD)
 
            entry.bind("<FocusIn>", on_focus_in_eye)
            entry.bind("<FocusOut>", on_focus_out_eye)
            entry.bind("<Enter>", on_hover_eye)
            entry.bind("<Leave>", on_leave_eye)
            eye_lbl.bind("<Enter>", on_hover_eye)
            eye_lbl.bind("<Leave>", on_leave_eye)
 
        self.entries[key] = entry
        return yf + h
 
    # ══════════════════════════════════════════════════════════════
    #                    4B · PAINEL DIREITO
    # ══════════════════════════════════════════════════════════════
    def _build_right(self):
        c = self.right
        W, H = PANEL_W, WIN_H
 
        # ── Fundo gradient mesh ───────────────────────────────
        bg_pil = make_right_bg(W, H)
        self.right_bg_tk = ImageTk.PhotoImage(bg_pil)
        self._imgs.append(self.right_bg_tk)
        c.create_image(0, 0, image=self.right_bg_tk, anchor="nw")
 
        # ── Formas decorativas ────────────────────────────────
        # Anel superior esquerdo
        self._ring_id = c.create_oval(
            40, 50, 200, 210, outline=GOLD, width=2, dash=()
        )
 
        # Dot grid inferior esquerdo
        dot_pil = make_dot_grid(110, 110, GOLD, 14, 2)
        self.dot_tk = ImageTk.PhotoImage(dot_pil)
        self._imgs.append(self.dot_tk)
        self._dot_orig = (50, H - 200)
        self._dot_id = c.create_image(*self._dot_orig, image=self.dot_tk,
                                      anchor="nw")
 
        # Quadrado dourado (rotacionado)
        sq_pil = make_gold_square(64, 18)
        self.sq_tk = ImageTk.PhotoImage(sq_pil)
        self._imgs.append(self.sq_tk)
        self._sq_orig = (W - 100, 150)
        self._sq_id = c.create_image(*self._sq_orig, image=self.sq_tk,
                                     anchor="center")
 
        # Quadrado só contorno (rotacionado)
        osq_pil = make_outline_square(46, -14, GOLD, 2)
        self.osq_tk = ImageTk.PhotoImage(osq_pil)
        self._imgs.append(self.osq_tk)
        self._osq_orig = (W - 130, H - 230)
        self._osq_id = c.create_image(*self._osq_orig, image=self.osq_tk,
                                      anchor="center")
 
        # Estrela (rotação contínua) — frames pré-renderizados
        self._star_frames = []
        star_base = make_star(22, GOLD)
        for a in range(0, 360, 10):
            r = star_base.rotate(a, resample=Image.BICUBIC, expand=True)
            # pad to keep size consistent
            tk_f = ImageTk.PhotoImage(r)
            self._star_frames.append(tk_f)
            self._imgs.append(tk_f)
        self._star_orig = (35, H // 2 - 20)
        self._star_id = c.create_image(*self._star_orig,
                                       image=self._star_frames[0], anchor="center")
 
        # Plus (rotação contra)
        self._plus_frames = []
        plus_base = make_plus(26, GOLD)
        for a in range(0, 360, 10):
            r = plus_base.rotate(-a, resample=Image.BICUBIC, expand=True)
            tk_f = ImageTk.PhotoImage(r)
            self._plus_frames.append(tk_f)
            self._imgs.append(tk_f)
        self._plus_orig = (W - 50, H - 70)
        self._plus_id = c.create_image(*self._plus_orig,
                                       image=self._plus_frames[0], anchor="center")
 
        # ── Pill "Plataforma online" ──────────────────────────
        px1, py1 = W - 210, 44
        px2, py2 = W - 36, 76
        draw_rounded(c, px1, py1, px2, py2, 16,
                     fill=NAVY_SOFT, outline="#FFFFFF30", width=1)
        # Halo verde (pulsação)
        self._pulse_halo = c.create_oval(px1 + 11, py1 + 9, px1 + 25, py1 + 23,
                                         outline=DOT_GREEN, width=1)
        # Dot verde central
        self._pulse_dot = c.create_oval(px1 + 14, py1 + 12, px1 + 22, py1 + 20,
                                        fill=DOT_GREEN, outline="")
        self._pulse_center = (px1 + 18, py1 + 16)  # centro
        c.create_text(px1 + 34, (py1 + py2) // 2,
                      text="PLATAFORMA ONLINE",
                      font=(FONT_SANS, 8, "bold"), fill=WHITE, anchor="w")
 
        # ── Colagem de fotos (placeholders iniciais) ──────────
        # Specs: (cx, cy, w, h, angle)
        self._photo_specs = [
            (230, 280, 200, 250, -4),     # foto 1 — alto à esquerda
            (470, 320, 200, 260, 3),      # foto 2 — à direita, mais alta
            (220, 460, 210, 165, 2),      # foto 3 — embaixo à esquerda
        ]
        self._photo_tks = [None, None, None]
        self._photo_items = [None, None, None]
 
        for i, (cx, cy, w, h, angle) in enumerate(self._photo_specs):
            pl = make_photo_placeholder(w, h, seed=i)
            pl = round_corners(pl, 18)
            # sombra projetada
            shadow = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
            ImageDraw.Draw(shadow).rounded_rectangle(
                (30, 40, w + 30, h + 40), 18, fill=(0, 0, 0, 100)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(20))
            shadow.alpha_composite(pl, (30, 30))
            rotated = shadow.rotate(angle, resample=Image.BICUBIC, expand=True)
            tkimg = ImageTk.PhotoImage(rotated)
            self._photo_tks[i] = tkimg
            self._imgs.append(tkimg)
            self._photo_items[i] = c.create_image(cx, cy, image=tkimg,
                                                  anchor="center")
 
        # ── Badge "+120 cursos ativos" ────────────────────────
        b1x1, b1y1 = 330, 215
        b1x2, b1y2 = 468, 272
        # sombra
        sh_img = Image.new("RGBA", (b1x2 - b1x1 + 40, b1y2 - b1y1 + 40), (0, 0, 0, 0))
        ImageDraw.Draw(sh_img).rounded_rectangle(
            (20, 28, b1x2 - b1x1 + 20, b1y2 - b1y1 + 28),
            14, fill=(0, 0, 0, 110),
        )
        sh_img = sh_img.filter(ImageFilter.GaussianBlur(16))
        self._badge1_sh_tk = ImageTk.PhotoImage(sh_img)
        self._imgs.append(self._badge1_sh_tk)
        c.create_image(b1x1 - 20, b1y1 - 20, image=self._badge1_sh_tk, anchor="nw")
 
        self._badge1_bg = draw_rounded(c, b1x1, b1y1, b1x2, b1y2, 14,
                                       fill=GOLD, outline=GOLD)
        # ícone check
        mini_check = make_icon("check", size=20, color=NAVY_DEEP, stroke=2)
        self.badge1_icon_tk = ImageTk.PhotoImage(mini_check)
        self._imgs.append(self.badge1_icon_tk)
        c.create_image(b1x1 + 18, (b1y1 + b1y2) // 2,
                       image=self.badge1_icon_tk, anchor="center")
        c.create_text(b1x1 + 40, (b1y1 + b1y2) // 2 - 6,
                      text="+120", font=(FONT_SERIF, 20, "bold"),
                      fill=NAVY_DEEP, anchor="w")
        c.create_text(b1x1 + 40, (b1y1 + b1y2) // 2 + 14,
                      text="CURSOS ATIVOS", font=(FONT_SANS, 7, "bold"),
                      fill=NAVY_DEEP, anchor="w")
 
        # ── Badge "★ 4.9 / 5.0" (canto inferior direito) ─────
        b2x1, b2y1 = W - 180, 470
        b2x2, b2y2 = W - 40, 524
        sh_img2 = Image.new("RGBA",
                            (b2x2 - b2x1 + 40, b2y2 - b2y1 + 40),
                            (0, 0, 0, 0))
        ImageDraw.Draw(sh_img2).rounded_rectangle(
            (20, 28, b2x2 - b2x1 + 20, b2y2 - b2y1 + 28),
            12, fill=(0, 0, 0, 110),
        )
        sh_img2 = sh_img2.filter(ImageFilter.GaussianBlur(14))
        self._badge2_sh_tk = ImageTk.PhotoImage(sh_img2)
        self._imgs.append(self._badge2_sh_tk)
        c.create_image(b2x1 - 20, b2y1 - 20, image=self._badge2_sh_tk, anchor="nw")
 
        draw_rounded(c, b2x1, b2y1, b2x2, b2y2, 12, fill=WHITE, outline=WHITE)
        c.create_text(b2x1 + 14, b2y1 + 10, text="AVALIAÇÃO",
                      font=(FONT_SANS, 7, "bold"), fill=GOLD_DEEP, anchor="nw")
        c.create_text(b2x1 + 14, b2y1 + 24, text="★ 4.9 / 5.0",
                      font=(FONT_SERIF, 14, "bold"), fill=NAVY_DEEP, anchor="nw")
 
        # ── Tagline ────────────────────────────────────────────
        TX = 64
        TY = 578
        # Linha divisora ao lado do texto
        c.create_line(TX, TY + 14, TX + 36, TY + 14, fill=GOLD, width=1)
        ital = tkfont.Font(family=FONT_SERIF, size=26, slant="italic")
        c.create_text(TX + 48, TY, text="Seu futuro começa",
                      font=(FONT_SERIF, 26, "italic"), fill=WHITE, anchor="nw")
        c.create_text(TX, TY + 34, text="com uma ",
                      font=(FONT_SERIF, 26, "italic"), fill=WHITE, anchor="nw")
        w_com = ital.measure("com uma ")
        c.create_text(TX + w_com, TY + 34, text="escolha simples.",
                      font=(FONT_SERIF, 26, "italic"), fill=GOLD, anchor="nw")
 
        # Subtítulo
        c.create_text(
            TX, TY + 86,
            text=("Descubra novas oportunidades, desenvolva habilidades\n"
                  "e faça parte de uma comunidade de aprendizado moderna."),
            font=(FONT_SANS, 10), fill="#D8DBE8", anchor="nw", justify="left",
        )
 
        # ── Stats ─────────────────────────────────────────────
        SY = TY + 150
        # Divisor
        c.create_line(TX, SY - 16, TX + 310, SY - 16,
                      fill="#FFFFFF26", width=1)
 
        stats = [
            ("10k", "+", "ALUNOS ATIVOS"),
            ("95",  "%", "APROVAÇÃO"),
            ("24/7", "", "SUPORTE"),
        ]
        num_font = tkfont.Font(family=FONT_SERIF, size=22, weight="bold")
        sx = TX
        for num, suf, label in stats:
            c.create_text(sx, SY, text=num,
                          font=(FONT_SERIF, 22, "bold"), fill=WHITE, anchor="nw")
            w_num = num_font.measure(num)
            if suf:
                c.create_text(sx + w_num, SY, text=suf,
                              font=(FONT_SERIF, 22, "bold"), fill=GOLD, anchor="nw")
            c.create_text(sx, SY + 34, text=label,
                          font=(FONT_SANS, 8, "bold"), fill="#A0A6C0", anchor="nw")
            sx += 120
 
    # ══════════════════════════════════════════════════════════════
    #                    4C · ANIMAÇÕES
    # ══════════════════════════════════════════════════════════════
    def _setup_anim_state(self):
        self._star_idx = 0
        self._plus_idx = 0
        # Estado do parallax (deslocamento suave do mouse)
        self._parallax_x = 0.0
        self._parallax_y = 0.0
        self._parallax_target_x = 0.0
        self._parallax_target_y = 0.0
        # Bind do mouse no painel direito para parallax
        self.right.bind("<Motion>", self._on_mouse_parallax)
 
    def _on_mouse_parallax(self, event):
        # Normalizar posição do mouse em [-1, +1]
        self._parallax_target_x = (event.x / PANEL_W - 0.5) * 2
        self._parallax_target_y = (event.y / WIN_H - 0.5) * 2
 
    def _animate(self):
        self._tick += 1
        t = self._tick
 
        # Interpolação suave do parallax (lerp)
        self._parallax_x += (self._parallax_target_x - self._parallax_x) * 0.08
        self._parallax_y += (self._parallax_target_y - self._parallax_y) * 0.08
        px = self._parallax_x
        py = self._parallax_y
 
        # Flutuar — quadrado dourado (+ parallax)
        ox, oy = self._sq_orig
        dy = math.sin(t * 0.05) * 6
        self.right.coords(self._sq_id,
                          ox + px * 8, oy + dy + py * 6)
 
        # Flutuar — dot grid
        ox, oy = self._dot_orig
        dy = math.sin(t * 0.04 + 1.2) * 5
        self.right.coords(self._dot_id,
                          ox - px * 6, oy + dy - py * 4)
 
        # Flutuar — quadrado outline
        ox, oy = self._osq_orig
        dy = math.sin(t * 0.045 + 2) * 5
        self.right.coords(self._osq_id,
                          ox + px * 10, oy + dy + py * 8)
 
        # Estrela girando (+ parallax leve)
        if t % 2 == 0:
            self._star_idx = (self._star_idx + 1) % len(self._star_frames)
            self.right.itemconfig(self._star_id,
                                  image=self._star_frames[self._star_idx])
            ox, oy = self._star_orig
            self.right.coords(self._star_id,
                              ox + px * 4,
                              oy + math.sin(t * 0.03) * 3 + py * 3)
 
        # Plus girando (contra)
        if t % 3 == 0:
            self._plus_idx = (self._plus_idx + 1) % len(self._plus_frames)
            self.right.itemconfig(self._plus_id,
                                  image=self._plus_frames[self._plus_idx])
            ox, oy = self._plus_orig
            self.right.coords(self._plus_id,
                              ox - px * 5, oy - py * 4)
 
        # Dot verde pulsante (halo expande/contrai)
        pulse = 1 + 0.4 * math.sin(t * 0.1)
        cx, cy = self._pulse_center
        rr = 7 * pulse
        self.right.coords(self._pulse_halo,
                          cx - rr, cy - rr, cx + rr, cy + rr)
 
        self.root.after(50, self._animate)
 
    # ══════════════════════════════════════════════════════════════
    #                    4D · REVEAL EM CASCATA
    # ══════════════════════════════════════════════════════════════
    def _reveal(self):
        """Efeito sutil: esconder alguns itens e revelar com delay."""
        # Neste ponto tudo já está visível. Para manter simples e evitar
        # bugs de z-order, apenas piscamos a borda do painel como "entrada".
        # Mantemos vazio para garantir estabilidade.
        pass
 
    # ══════════════════════════════════════════════════════════════
    #                 4E · DOWNLOAD DAS FOTOS (thread)
    # ══════════════════════════════════════════════════════════════
    def _download_photos(self):
        if not _HAS_NET:
            return
        for i, url in enumerate(PHOTO_URLS):
            cache = os.path.join(CACHE_DIR, f"photo_{i}.jpg")
            img = None
            if os.path.exists(cache):
                try:
                    img = Image.open(cache).convert("RGB")
                except Exception:
                    img = None
            if img is None:
                try:
                    req = urllib.request.Request(
                        url, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = resp.read()
                    img = Image.open(io.BytesIO(data)).convert("RGB")
                    try:
                        img.save(cache, "JPEG", quality=85)
                    except Exception:
                        pass
                except Exception:
                    img = None
            if img is not None:
                # Atualizar UI na main thread
                self.root.after(0, lambda i=i, img=img: self._replace_photo(i, img))
 
    def _replace_photo(self, i, pil_img):
        try:
            cx, cy, w, h, angle = self._photo_specs[i]
            # crop centrado para manter proporção
            src = pil_img
            sr = src.size[0] / src.size[1]
            tr = w / h
            if sr > tr:
                new_w = int(src.size[1] * tr)
                off = (src.size[0] - new_w) // 2
                src = src.crop((off, 0, off + new_w, src.size[1]))
            else:
                new_h = int(src.size[0] / tr)
                off = (src.size[1] - new_h) // 2
                src = src.crop((0, off, src.size[0], off + new_h))
            src = src.resize((w, h), Image.LANCZOS)
            src = round_corners(src, 18)
            # sombra
            shadow = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
            ImageDraw.Draw(shadow).rounded_rectangle(
                (30, 40, w + 30, h + 40), 18, fill=(0, 0, 0, 110)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(22))
            shadow.alpha_composite(src, (30, 30))
            rotated = shadow.rotate(angle, resample=Image.BICUBIC, expand=True)
            tkimg = ImageTk.PhotoImage(rotated)
            self._photo_tks[i] = tkimg
            self._imgs.append(tkimg)
            self.right.itemconfig(self._photo_items[i], image=tkimg)
        except Exception:
            pass
 
    # ══════════════════════════════════════════════════════════════
    #                    4F · SUBMIT / VALIDAÇÃO
    # ══════════════════════════════════════════════════════════════
    def _val(self, key):
        e = self.entries[key]
        if getattr(e, "_placeholder_on", False):
            return ""
        return e.get().strip()
 
    def _on_submit(self):
        nome = self._val("fullname")
        email = self._val("email")
        email2 = self._val("email2")
        senha = self._val("pass")
        senha2 = self._val("pass2")
        tel = self._val("phone")
 
        if not nome:
            messagebox.showwarning("Campo obrigatório", "Informe seu nome completo.")
            return
        if not email or "@" not in email or "." not in email:
            messagebox.showwarning("E-mail inválido", "Informe um e-mail válido.")
            return
        if email != email2:
            messagebox.showwarning("E-mails diferentes",
                                   "Os e-mails informados não coincidem.")
            return
        if len(senha) < 8:
            messagebox.showwarning("Senha curta",
                                   "A senha deve ter no mínimo 8 caracteres.")
            return
        if senha != senha2:
            messagebox.showwarning("Senhas diferentes",
                                   "As senhas informadas não coincidem.")
            return
        if not tel:
            messagebox.showwarning("Telefone",
                                   "Informe um número de telefone.")
            return
        if not self._terms_checked:
            messagebox.showwarning("Termos",
                                   "Você precisa aceitar os Termos de Uso.")
            return
 
        # Feedback visual no botão
        c = self.left
        c.itemconfig(self._btn_text, text="Cadastrando…")
        c.itemconfig(self._btn_arrow, state="hidden")
        c.itemconfig(self._btn_bg, fill="#1B2B5B")
 
        def success():
            c.itemconfig(self._btn_bg, fill=GREEN_OK)
            c.itemconfig(self._btn_text, text="✓ Cadastro realizado!")
            self.root.after(1800, reset)
 
        def reset():
            c.itemconfig(self._btn_bg, fill=NAVY_DEEP)
            c.itemconfig(self._btn_text, text="Cadastrar")
            c.itemconfig(self._btn_arrow, state="normal")
 
        self.root.after(900, success)
 
 
# ═══════════════════════════════════════════════════════════════════
#                       5 · BOOTSTRAP
# ═══════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    # Ícone da janela (usa o logo se disponível)
    try:
        logo_path = os.path.join(HERE, "sf-logo.png")
        if os.path.exists(logo_path):
            icon_img = Image.open(logo_path).convert("RGBA").resize(
                (32, 32), Image.LANCZOS
            )
            icon_tk = ImageTk.PhotoImage(icon_img)
            root.iconphoto(True, icon_tk)
            root._icon_ref = icon_tk  # anti-GC
    except Exception:
        pass
 
    SistemaFacilApp(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()
