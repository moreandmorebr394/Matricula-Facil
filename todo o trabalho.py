"""
Políglota — Sistema de Gestão Acadêmica
=======================================

Aplicação desktop em Tkinter (apenas biblioteca padrão do Python).
Conversão fiel do mockup HTML/CSS para uma interface nativa,
preservando a paleta "Caderno Editorial", a navegação lateral
e as nove visões: Dashboard, Funil de Vendas, Alunos, Matrículas,
Pagamentos, Cursos, Turmas, Frequência e Vendedores.

Como executar (no VSCode ou terminal):
    python poliglota_app.py

Requisitos: Python 3.9+ (Tkinter já vem incluso).
"""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk, font as tkfont
from dataclasses import dataclass


# =====================================================================
# DESIGN TOKENS — paleta "Caderno Editorial"
# =====================================================================
class Theme:
    INK       = "#1a1715"
    INK_2     = "#2a2520"
    INK_3     = "#3d362f"
    PAPER     = "#f7f2e8"
    PAPER_2   = "#efe8d9"
    PAPER_3   = "#e5dcc8"
    LINE      = "#d4c9b0"
    LINE_2    = "#c2b594"
    MUTED     = "#8a8275"
    MUTED_2   = "#6b6458"
    ACCENT    = "#c24d28"
    ACCENT_2  = "#8a3516"
    FOREST    = "#2d4a35"
    OCHRE     = "#c98a1a"
    PLUM      = "#6b3a4e"
    SKY       = "#3a5a78"
    SUCCESS   = "#2d6a4f"
    WARNING   = "#b88612"
    DANGER    = "#a63a1e"

    AVATAR_PALETTE = [
        "#c24d28", "#2d4a35", "#3a5a78", "#6b3a4e",
        "#c98a1a", "#4a5c3d", "#8a3516", "#3d362f",
    ]


# =====================================================================
# TIPOGRAFIA
# =====================================================================
class Fonts:
    """Fontes registradas após a criação da raiz Tk."""

    serif: tkfont.Font
    serif_lg: tkfont.Font
    serif_xl: tkfont.Font
    sans: tkfont.Font
    sans_md: tkfont.Font
    sans_bold: tkfont.Font
    sans_sm: tkfont.Font
    sans_xs: tkfont.Font
    mono: tkfont.Font
    mono_bold: tkfont.Font
    label: tkfont.Font

    @classmethod
    def init(cls) -> None:
        # Famílias com fallback multiplataforma.
        serif_family = cls._pick(["Georgia", "Cambria", "Times New Roman", "serif"])
        sans_family  = cls._pick(["Segoe UI", "Helvetica Neue", "Arial", "sans-serif"])
        mono_family  = cls._pick(["Consolas", "Menlo", "DejaVu Sans Mono", "Courier New"])

        cls.serif      = tkfont.Font(family=serif_family, size=16, weight="normal")
        cls.serif_lg   = tkfont.Font(family=serif_family, size=22, weight="normal")
        cls.serif_xl   = tkfont.Font(family=serif_family, size=30, weight="normal")
        cls.sans       = tkfont.Font(family=sans_family, size=10)
        cls.sans_md    = tkfont.Font(family=sans_family, size=11)
        cls.sans_bold  = tkfont.Font(family=sans_family, size=11, weight="bold")
        cls.sans_sm    = tkfont.Font(family=sans_family, size=9)
        cls.sans_xs    = tkfont.Font(family=sans_family, size=8)
        cls.mono       = tkfont.Font(family=mono_family, size=10)
        cls.mono_bold  = tkfont.Font(family=mono_family, size=10, weight="bold")
        cls.label      = tkfont.Font(family=sans_family, size=8, weight="bold")

    @staticmethod
    def _pick(candidates: list[str]) -> str:
        available = set(tkfont.families())
        for name in candidates:
            if name in available:
                return name
        return candidates[-1]


# =====================================================================
# WIDGETS UTILITÁRIOS
# =====================================================================
def hcard(parent: tk.Misc, **kw) -> tk.Frame:
    """Frame padrão estilo 'card' (papel com borda)."""
    frame = tk.Frame(
        parent,
        bg=Theme.PAPER,
        highlightthickness=1,
        highlightbackground=Theme.LINE,
        bd=0,
        **kw,
    )
    return frame


def hsep(parent: tk.Misc, color: str = Theme.LINE) -> tk.Frame:
    return tk.Frame(parent, height=1, bg=color)


class Badge(tk.Label):
    STYLES = {
        "success": (Theme.SUCCESS, "#e7f1ec"),
        "warning": (Theme.WARNING, "#f6ecd2"),
        "danger":  (Theme.DANGER,  "#f3dcd5"),
        "info":    (Theme.SKY,     "#dbe5ee"),
        "neutral": (Theme.MUTED_2, Theme.PAPER_2),
        "accent":  (Theme.ACCENT,  "#f1d9cf"),
        "plum":    (Theme.PLUM,    "#ead7df"),
    }

    def __init__(self, parent, text: str, kind: str = "neutral"):
        fg, bg = self.STYLES.get(kind, self.STYLES["neutral"])
        super().__init__(
            parent,
            text=f" • {text} ",
            font=Fonts.sans_xs,
            fg=fg,
            bg=bg,
            padx=6,
            pady=1,
        )


class FlatButton(tk.Label):
    """Botão estilizado tipo 'flat' com hover."""

    def __init__(self, parent, text: str, kind: str = "secondary", command=None):
        self.command = command
        self.kind = kind
        bg, fg, hover = self._palette(kind)
        self._bg, self._fg, self._hover = bg, fg, hover
        super().__init__(
            parent,
            text=text,
            font=Fonts.sans_bold,
            bg=bg,
            fg=fg,
            padx=14,
            pady=7,
            cursor="hand2",
            bd=0,
        )
        self.bind("<Enter>", lambda _e: self.configure(bg=hover))
        self.bind("<Leave>", lambda _e: self.configure(bg=bg))
        if command:
            self.bind("<Button-1>", lambda _e: command())

    @staticmethod
    def _palette(kind: str) -> tuple[str, str, str]:
        if kind == "primary":
            return Theme.INK, Theme.PAPER, Theme.INK_2
        if kind == "accent":
            return Theme.ACCENT, Theme.PAPER, Theme.ACCENT_2
        if kind == "ghost":
            return Theme.PAPER, Theme.INK_2, Theme.PAPER_2
        # secondary
        return Theme.PAPER, Theme.INK, Theme.PAPER_2


class Avatar(tk.Canvas):
    """Avatar circular com iniciais."""

    def __init__(self, parent, initials: str, size: int = 32, color_index: int = 0,
                 bg: str = Theme.PAPER):
        super().__init__(parent, width=size, height=size, bg=bg,
                         highlightthickness=0, bd=0)
        color = Theme.AVATAR_PALETTE[color_index % len(Theme.AVATAR_PALETTE)]
        self.create_oval(1, 1, size - 1, size - 1, fill=color, outline="")
        font_size = max(8, int(size * 0.38))
        self.create_text(
            size / 2, size / 2,
            text=initials.upper()[:2],
            fill=Theme.PAPER,
            font=(Fonts.sans_bold.actual("family"), font_size, "bold"),
        )


class VScroll(tk.Frame):
    """Frame com scroll vertical, conteúdo em self.body."""

    def __init__(self, parent, bg: str = Theme.PAPER):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.body = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        self.body.bind("<Configure>", self._on_body_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel(self.canvas)

    def _on_body_configure(self, _e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas.itemconfigure(self._win, width=e.width)

    def _bind_mousewheel(self, widget: tk.Widget):
        def _wheel(e):
            delta = -1 if (getattr(e, "delta", 0) > 0 or e.num == 4) else 1
            self.canvas.yview_scroll(delta, "units")
        widget.bind_all("<MouseWheel>", _wheel)
        widget.bind_all("<Button-4>", _wheel)
        widget.bind_all("<Button-5>", _wheel)


# =====================================================================
# DADOS MOCK
# =====================================================================
@dataclass
class Lead:
    name: str
    course: str
    origin: str
    value: str = ""
    badge: tuple[str, str] | None = None  # (texto, kind)
    color_index: int = 0


FUNIL = {
    "Novo lead": [
        Lead("Luiza Pimentel", "Inglês · Avançado", "Instagram", "R$ 850", ("Quente", "info"), 0),
        Lead("Vinícius Kawasaki", "Japonês · Iniciante", "Indicação", "R$ 680", None, 5),
        Lead("Ana Flor Siqueira", "Espanhol · A1", "Instagram", "R$ 420", ("Nova", "accent"), 3),
    ],
    "Em contato": [
        Lead("Henrique Salgado", "Francês · A2", "Presencial", "", None, 0),
        Lead("Clarice Nogueira", "Italiano · B1", "Instagram", "", ("5 dias", "warning"), 2),
        Lead("Marcos Bittencourt", "Inglês · B2", "Indicação", "", None, 1),
    ],
    "Interessado": [
        Lead("Teresa Holanda", "Alemão · A1", "Instagram", "", ("Aula teste", "success"), 3),
        Lead("Pedro Amaral", "Inglês · B1", "Indicação", "", None, 0),
        Lead("Sofia Rebouças", "Espanhol · B1", "Presencial", "", None, 4),
    ],
    "Negociando": [
        Lead("Gabriel Fontes", "Inglês · C1 Intensivo", "Indicação", "R$ 1.280", ("Proposta", "accent"), 5),
        Lead("Laura Menezes", "Francês · B2", "Instagram", "R$ 920", None, 6),
        Lead("Diego Salles", "Japonês · A2", "Instagram", "R$ 740", ("3 dias", "warning"), 1),
    ],
    "Matriculado": [
        Lead("Beatriz Coutinho", "Italiano · A2", "Indicação", "R$ 520", ("OK", "success"), 4),
        Lead("Rafael Monteiro", "Inglês · C1", "Instagram", "R$ 850", None, 1),
        Lead("Helena Brandão", "Inglês · B2", "Presencial", "R$ 420", None, 0),
    ],
    "Perdido": [
        Lead("Otávio Pires", "Inglês · B1", "Preço", "há 12 dias", None, 7),
        Lead("Camila Rocha", "Alemão · A1", "Sem retorno", "há 18 dias", None, 7),
    ],
}

ALUNOS = [
    ("HB", "Helena Brandão", "28 anos · São Paulo/SP", "helena.brandao@gmail.com",
     "(11) 98432-1209", "ING-B2-MA", "12/02/2026", "94%", "good", "Em dia", "success", 0),
    ("RM", "Rafael Monteiro", "34 anos · Santos/SP", "rafael.monteiro@outlook.com",
     "(13) 99211-7788", "ING-C1-NO", "03/04/2026", "100%", "good", "Em dia", "success", 1),
    ("TA", "Tomás Albuquerque", "19 anos · Guarulhos/SP", "tomas.alb@hotmail.com",
     "(11) 94301-5567", "ESP-B1-MA", "18/01/2026", "78%", "mid", "Pendente", "warning", 2),
    ("CI", "Clara Ishikawa", "26 anos · São Paulo/SP", "clara.ishikawa@gmail.com",
     "(11) 98112-3344", "JAP-A2-NO", "22/11/2025", "62%", "bad", "Atrasado", "danger", 3),
    ("BC", "Beatriz Coutinho", "31 anos · Campinas/SP", "bia.coutinho@gmail.com",
     "(19) 99772-1100", "ITA-A2-TA", "09/04/2026", "88%", "good", "Em dia", "success", 4),
    ("LM", "Laura Menezes", "23 anos · São Paulo/SP", "laura.m@gmail.com",
     "(11) 99001-4567", "FRA-B2-NO", "15/03/2026", "91%", "good", "Em dia", "success", 6),
    ("GF", "Gabriel Fontes", "29 anos · São Paulo/SP", "gabriel.fontes@gmail.com",
     "(11) 98765-4321", "ING-C1-NO", "14/04/2026", "97%", "good", "Em dia", "success", 5),
    ("TH", "Teresa Holanda", "37 anos · Osasco/SP", "teresa.h@gmail.com",
     "(11) 94110-2030", "ALE-A1-TA", "15/04/2026", "—", "good", "Novo", "info", 7),
]

PAGAMENTOS = [
    ("PAG-4821", "HB", "Helena Brandão", 0, "Mensalidade · Abril/26", "PIX",
     "10/04/2026", "10/04/2026", "R$ 420,00", "Pago", "success"),
    ("PAG-4820", "RM", "Rafael Monteiro", 1, "Matrícula · Inglês C1", "Cartão 10×",
     "03/04/2026", "03/04/2026", "R$ 850,00", "Pago", "success"),
    ("PAG-4819", "BC", "Beatriz Coutinho", 4, "Mensalidade · Abril/26", "PIX",
     "09/04/2026", "08/04/2026", "R$ 520,00", "Pago", "success"),
    ("PAG-4818", "TA", "Tomás Albuquerque", 2, "Mensalidade · Abril/26", "Boleto",
     "20/04/2026", "—", "R$ 420,00", "Pendente", "warning"),
    ("PAG-4817", "CI", "Clara Ishikawa", 3, "Mensalidade · Abril/26", "Boleto",
     "10/04/2026", "—", "R$ 480,00", "Atrasado · 7d", "danger"),
    ("PAG-4816", "LM", "Laura Menezes", 6, "Mensalidade · Abril/26", "PIX",
     "07/04/2026", "07/04/2026", "R$ 767,00", "Pago", "success"),
    ("PAG-4815", "GF", "Gabriel Fontes", 5, "Matrícula · Inglês C1 Intensivo", "PIX à vista",
     "14/04/2026", "14/04/2026", "R$ 12.800,00", "Pago", "success"),
    ("PAG-4814", "TH", "Teresa Holanda", 7, "Matrícula · Alemão A1", "Cartão 10×",
     "15/04/2026", "15/04/2026", "R$ 420,00", "Pago", "success"),
]

CURSOS = [
    ("En", "Inglês",   "ING · CEFR A1–C2",  Theme.FOREST, "Do iniciante ao avançado. Metodologia comunicativa, preparação TOEFL/IELTS.", "12", "128", "R$ 420"),
    ("Es", "Espanhol", "ESP · CEFR A1–C1",  Theme.ACCENT, "Variações latino-americanas e peninsulares. Foco em conversação.",          "6",  "54",  "R$ 380"),
    ("Fr", "Francês",  "FRA · CEFR A1–B2",  Theme.SKY,    "Preparação para DELF/DALF. Imersão cultural com cinema e literatura.",      "4",  "31",  "R$ 460"),
    ("De", "Alemão",   "ALE · CEFR A1–B1",  Theme.PLUM,   "Parceria Goethe-Institut. Aulas para certificação oficial.",                "3",  "22",  "R$ 480"),
    ("It", "Italiano", "ITA · CEFR A1–B2",  Theme.OCHRE,  "Gramática, cinema italiano e culinária regional integrados.",               "3",  "26",  "R$ 433"),
    ("Ja", "Japonês",  "JAP · JLPT N5–N3",  "#4a5c3d",    "Hiragana, katakana e kanji progressivos. Preparação JLPT.",                 "2",  "16",  "R$ 520"),
]

TURMAS = [
    ("ING-A2-MA", "Inglês · Módulo 3",       "Manhã", "07:30–09:00", "Seg · Qua · Sex", "04", "Prof. Anna Keating",   "12 / 14", "05/02/26", "Ativa",     "success"),
    ("ING-B2-MA", "Inglês · Módulo 5",       "Manhã", "09:15–10:45", "Ter · Qui",       "04", "Prof. Anna Keating",   "14 / 14", "03/02/26", "Ativa",     "success"),
    ("ING-C1-NO", "Inglês · Avançado C1",    "Noite", "19:00–20:30", "Seg · Qua",       "01", "Prof. Nathan O'Brien", "11 / 12", "01/03/26", "Ativa",     "success"),
    ("ESP-B1-MA", "Espanhol · Intermediário","Manhã", "09:15–10:45", "Seg · Qua · Sex", "02", "Prof. Isabela Ortiz",  "9 / 12",  "18/01/26", "Ativa",     "success"),
    ("FRA-A1-TA", "Francês · Iniciante",     "Tarde", "14:00–15:30", "Ter · Qui",       "06", "Prof. Claire Dubois",  "8 / 10",  "05/04/26", "Ativa",     "success"),
    ("FRA-B2-NO", "Francês · B2",            "Noite", "20:30–22:00", "Seg · Qua",       "05", "Prof. Claire Dubois",  "7 / 10",  "15/03/26", "Ativa",     "success"),
    ("ITA-A2-TA", "Italiano · A2",           "Tarde", "16:00–17:30", "Ter · Qui",       "03", "Prof. Marco Ferri",    "10 / 12", "09/04/26", "Ativa",     "success"),
    ("JAP-A1-NO", "Japonês · Iniciante",     "Noite", "20:30–22:00", "Ter · Qui",       "03", "Prof. Yuki Tanaka",    "7 / 8",   "10/02/26", "Atenção",   "warning"),
    ("JAP-A2-NO", "Japonês · A2",            "Noite", "19:00–20:30", "Ter · Qui",       "03", "Prof. Yuki Tanaka",    "9 / 10",  "22/11/25", "Ativa",     "success"),
    ("ALE-A1-TA", "Alemão · Iniciante",      "Tarde", "17:30–19:00", "Seg · Qua · Sex", "07", "Prof. Klaus Hermann",  "6 / 10",  "16/04/26", "Formando",  "info"),
]

VENDEDORES = [
    ("HC", "Henrique Carvalho", "Coordenador comercial", 0, 18, 12, 67, "R$ 14.820"),
    ("PA", "Paula Almeida",     "Vendedora sênior",      3, 22, 14, 64, "R$ 16.940"),
    ("LM", "Lucas Marques",     "Vendedor pleno",        2, 14,  8, 57, "R$  9.380"),
    ("MV", "Marina Vasconcelos","Coordenadora",          4, 11,  7, 64, "R$  8.120"),
]

FREQ_DAYS = ["01", "03", "06", "08", "10", "13", "15", "17", "20", "22", "24", "27", "29"]
FREQUENCIA = [
    ("HB", "Helena Brandão",      0, ["P","P","P","J","P","P","P","P","·","·","·","·","·"], "94%", "good"),
    ("GF", "Gabriel Fontes",      5, ["P","P","P","P","P","P","P","P","·","·","·","·","·"], "100%","good"),
    ("RM", "Rafael Monteiro",     1, ["P","P","P","P","P","P","F","P","·","·","·","·","·"], "88%", "good"),
    ("TA", "Tomás Albuquerque",   2, ["P","F","P","F","P","J","P","F","·","·","·","·","·"], "62%", "bad"),
    ("CI", "Clara Ishikawa",      3, ["F","P","F","P","F","P","F","P","·","·","·","·","·"], "50%", "bad"),
    ("BC", "Beatriz Coutinho",    4, ["P","P","P","P","J","P","P","P","·","·","·","·","·"], "94%", "good"),
    ("LM", "Laura Menezes",       6, ["P","P","P","P","P","P","P","J","·","·","·","·","·"], "94%", "good"),
    ("TH", "Teresa Holanda",      7, ["·","·","·","·","P","P","P","P","·","·","·","·","·"], "100%","good"),
]


# =====================================================================
# COMPONENTES DE LAYOUT
# =====================================================================
class Sidebar(tk.Frame):
    SECTIONS = [
        ("Principal", [
            ("dashboard",   "Dashboard",       None),
            ("funil",       "Funil de Vendas", "47"),
            ("alunos",      "Alunos",          "284"),
            ("matriculas",  "Matrículas",      None),
            ("pagamentos",  "Pagamentos",      None),
        ]),
        ("Acadêmico", [
            ("cursos",      "Cursos",          None),
            ("turmas",      "Turmas",          None),
            ("frequencia",  "Frequência",      None),
        ]),
        ("Equipe", [
            ("vendedores",  "Vendedores",      None),
        ]),
    ]

    def __init__(self, parent, on_navigate):
        super().__init__(parent, bg=Theme.INK, width=248)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.buttons: dict[str, tk.Frame] = {}
        self._build()

    def _build(self):
        # Brand
        brand = tk.Frame(self, bg=Theme.INK)
        brand.pack(fill="x", padx=18, pady=(20, 16))

        mark = tk.Label(
            brand, text="P", bg=Theme.ACCENT, fg=Theme.PAPER,
            font=(Fonts.serif.actual("family"), 16, "bold italic"),
            width=2, height=1,
        )
        mark.pack(side="left", padx=(0, 10))

        text_box = tk.Frame(brand, bg=Theme.INK)
        text_box.pack(side="left", fill="x", expand=True)
        tk.Label(text_box, text="Políglota", bg=Theme.INK, fg=Theme.PAPER,
                 font=Fonts.serif, anchor="w").pack(anchor="w")
        tk.Label(text_box, text="GESTÃO ACADÊMICA", bg=Theme.INK, fg=Theme.MUTED,
                 font=Fonts.label, anchor="w").pack(anchor="w")

        hsep(self, color=Theme.INK_2).pack(fill="x")

        # Navegação
        for section_title, items in self.SECTIONS:
            tk.Label(
                self, text=section_title.upper(),
                bg=Theme.INK, fg="#6b6358",
                font=Fonts.label, anchor="w",
            ).pack(fill="x", padx=18, pady=(16, 6))

            for view_id, label, count in items:
                self._make_nav_btn(view_id, label, count)

        # Rodapé do usuário
        foot = tk.Frame(self, bg=Theme.INK)
        foot.pack(side="bottom", fill="x", padx=12, pady=12)
        hsep(foot, color=Theme.INK_2).pack(fill="x", pady=(0, 10))

        card = tk.Frame(foot, bg="#221d18")
        card.pack(fill="x")
        Avatar(card, "MV", size=32, color_index=4, bg="#221d18").pack(side="left", padx=8, pady=8)
        info = tk.Frame(card, bg="#221d18")
        info.pack(side="left", fill="x", expand=True, pady=8)
        tk.Label(info, text="Marina Vasconcelos", bg="#221d18", fg=Theme.PAPER,
                 font=Fonts.sans_bold, anchor="w").pack(anchor="w")
        tk.Label(info, text="Coordenadora", bg="#221d18", fg=Theme.MUTED,
                 font=Fonts.sans_xs, anchor="w").pack(anchor="w")

    def _make_nav_btn(self, view_id: str, label: str, count: str | None):
        wrap = tk.Frame(self, bg=Theme.INK, cursor="hand2")
        wrap.pack(fill="x", padx=10, pady=1)

        inner = tk.Frame(wrap, bg=Theme.INK)
        inner.pack(fill="x")

        bullet = tk.Frame(inner, width=3, bg=Theme.INK)
        bullet.pack(side="left", fill="y")

        body = tk.Frame(inner, bg=Theme.INK)
        body.pack(side="left", fill="x", expand=True)

        lbl = tk.Label(body, text=label, bg=Theme.INK, fg="#c8bfae",
                       font=Fonts.sans_md, anchor="w", padx=12, pady=8)
        lbl.pack(side="left", fill="x", expand=True)

        cnt = None
        if count:
            cnt = tk.Label(body, text=count, bg="#2c2622", fg="#a59d8c",
                           font=Fonts.mono, padx=6)
            cnt.pack(side="right", padx=(0, 10))

        widgets = [wrap, inner, body, lbl] + ([cnt] if cnt else [])

        def on_enter(_e=None):
            if self.buttons.get("_active") is wrap:
                return
            for w in (wrap, inner, body, lbl):
                w.configure(bg="#231e1a")
            if cnt:
                cnt.configure(bg="#231e1a")

        def on_leave(_e=None):
            if self.buttons.get("_active") is wrap:
                return
            for w in (wrap, inner, body, lbl):
                w.configure(bg=Theme.INK)
            if cnt:
                cnt.configure(bg="#2c2622")

        def on_click(_e=None):
            self.set_active(view_id)
            self.on_navigate(view_id)

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        wrap._refs = (inner, body, lbl, bullet, cnt)  # type: ignore[attr-defined]
        self.buttons[view_id] = wrap

    def set_active(self, view_id: str):
        for vid, wrap in self.buttons.items():
            if vid.startswith("_"):
                continue
            inner, body, lbl, bullet, cnt = wrap._refs  # type: ignore[attr-defined]
            if vid == view_id:
                for w in (wrap, inner, body, lbl):
                    w.configure(bg=Theme.PAPER)
                lbl.configure(fg=Theme.INK, font=Fonts.sans_bold)
                bullet.configure(bg=Theme.ACCENT)
                if cnt:
                    cnt.configure(bg=Theme.PAPER_3, fg=Theme.INK_3)
            else:
                for w in (wrap, inner, body, lbl):
                    w.configure(bg=Theme.INK)
                lbl.configure(fg="#c8bfae", font=Fonts.sans_md)
                bullet.configure(bg=Theme.INK)
                if cnt:
                    cnt.configure(bg="#2c2622", fg="#a59d8c")
        self.buttons["_active"] = self.buttons[view_id]


class Topbar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=Theme.PAPER, height=64)
        self.pack_propagate(False)

        self.title_box = tk.Frame(self, bg=Theme.PAPER)
        self.title_box.pack(side="left", padx=24, pady=10)

        self.crumb_var = tk.StringVar(value="VISÃO GERAL")
        self.title_var = tk.StringVar(value="Bom dia, Marina")

        tk.Label(self.title_box, textvariable=self.crumb_var,
                 bg=Theme.PAPER, fg=Theme.MUTED, font=Fonts.label, anchor="w"
                 ).pack(anchor="w")
        tk.Label(self.title_box, textvariable=self.title_var,
                 bg=Theme.PAPER, fg=Theme.INK, font=Fonts.serif_lg, anchor="w"
                 ).pack(anchor="w")

        # Ações à direita
        actions = tk.Frame(self, bg=Theme.PAPER)
        actions.pack(side="right", padx=24)

        FlatButton(actions, "+ Novo lead", kind="accent").pack(side="right", padx=(8, 0))
        FlatButton(actions, "Notificações", kind="secondary").pack(side="right", padx=4)

        search = tk.Frame(actions, bg=Theme.PAPER_2,
                          highlightthickness=1, highlightbackground=Theme.LINE)
        search.pack(side="right", padx=8)
        tk.Label(search, text="🔎", bg=Theme.PAPER_2, fg=Theme.MUTED,
                 font=Fonts.sans_md).pack(side="left", padx=(8, 4))
        entry = tk.Entry(search, bd=0, bg=Theme.PAPER_2, fg=Theme.INK,
                         font=Fonts.sans_md, width=28,
                         insertbackground=Theme.INK)
        entry.insert(0, "Buscar alunos, cursos, leads…")
        entry.bind("<FocusIn>", lambda _e: entry.delete(0, "end")
                   if entry.get().startswith("Buscar") else None)
        entry.pack(side="left", padx=(0, 8), pady=6)

        hsep(self, color=Theme.LINE).pack(side="bottom", fill="x")

    def set_page(self, crumb: str, title: str, accent_word: str | None = None):
        self.crumb_var.set(crumb.upper())
        if accent_word:
            self.title_var.set(f"{title}")
        else:
            self.title_var.set(title)


# =====================================================================
# VIEWS
# =====================================================================
class ViewBase(tk.Frame):
    """Cada view é um Frame em VScroll.body."""

    def __init__(self, parent):
        super().__init__(parent, bg=Theme.PAPER)

    def head(self, title: str, em: str, subtitle: str, actions: list[tuple[str, str]] | None = None):
        head = tk.Frame(self, bg=Theme.PAPER)
        head.pack(fill="x", padx=28, pady=(28, 18))

        left = tk.Frame(head, bg=Theme.PAPER)
        left.pack(side="left", fill="x", expand=True)

        title_frame = tk.Frame(left, bg=Theme.PAPER)
        title_frame.pack(anchor="w")
        tk.Label(title_frame, text=title + " ", bg=Theme.PAPER, fg=Theme.INK,
                 font=Fonts.serif_xl).pack(side="left")
        tk.Label(title_frame, text=em, bg=Theme.PAPER, fg=Theme.ACCENT,
                 font=(Fonts.serif_xl.actual("family"), 28, "italic")).pack(side="left")

        tk.Label(left, text=subtitle, bg=Theme.PAPER, fg=Theme.MUTED_2,
                 font=Fonts.sans_md, wraplength=620, justify="left", anchor="w"
                 ).pack(anchor="w", pady=(6, 0))

        if actions:
            btns = tk.Frame(head, bg=Theme.PAPER)
            btns.pack(side="right")
            for label, kind in actions:
                FlatButton(btns, label, kind=kind).pack(side="left", padx=4)


class DashboardView(ViewBase):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        # Saudação compacta + KPIs
        wrap = tk.Frame(self, bg=Theme.PAPER)
        wrap.pack(fill="both", expand=True, padx=28, pady=20)

        self._kpi_grid(wrap)
        self._dash_grid(wrap)

    def _kpi_grid(self, parent):
        row = tk.Frame(parent, bg=Theme.PAPER)
        row.pack(fill="x", pady=(0, 18))

        kpis = [
            ("LEADS ATIVOS",        "47",       "",   "+12,5%", "up"),
            ("MATRÍCULAS · MÊS",    "23",       "",   "+8,2%",  "up"),
            ("RECEITA · ABRIL",     "84.320",   "R$", "+16,2%", "up"),
            ("INADIMPLÊNCIA",       "4,7",      "%",  "−1,3 pp","down"),
        ]
        for i, (label, value, unit, delta, dir_) in enumerate(kpis):
            card = hcard(row)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            row.grid_columnconfigure(i, weight=1, uniform="kpi")

            inner = tk.Frame(card, bg=Theme.PAPER)
            inner.pack(fill="both", expand=True, padx=18, pady=16)

            tk.Label(inner, text=label, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.label, anchor="w").pack(anchor="w")

            value_row = tk.Frame(inner, bg=Theme.PAPER)
            value_row.pack(anchor="w", pady=(6, 8))
            if unit and not unit.endswith("%"):
                tk.Label(value_row, text=unit + " ", bg=Theme.PAPER,
                         fg=Theme.MUTED, font=Fonts.sans_md).pack(side="left")
            tk.Label(value_row, text=value, bg=Theme.PAPER, fg=Theme.INK,
                     font=(Fonts.serif_xl.actual("family"), 26)).pack(side="left")
            if unit and unit.endswith("%"):
                tk.Label(value_row, text=unit, bg=Theme.PAPER,
                         fg=Theme.MUTED, font=Fonts.sans_md).pack(side="left")

            color = Theme.SUCCESS if dir_ == "up" else Theme.DANGER
            tk.Label(inner, text=("▲ " if dir_ == "up" else "▼ ") + delta,
                     bg=Theme.PAPER, fg=color, font=Fonts.sans_xs, anchor="w"
                     ).pack(anchor="w")

    def _dash_grid(self, parent):
        grid = tk.Frame(parent, bg=Theme.PAPER)
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=2)
        grid.grid_columnconfigure(1, weight=1)

        # Coluna esquerda — gráfico de barras
        chart_card = hcard(grid)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 16))
        self._chart_head(chart_card, "Conversão de leads", "Últimos 6 meses")
        self._bar_chart(chart_card)

        # Coluna direita — origem dos leads
        origem_card = hcard(grid)
        origem_card.grid(row=0, column=1, sticky="nsew", pady=(0, 16))
        self._chart_head(origem_card, "Origem dos leads", "Distribuição mensal")
        self._origem_list(origem_card)

        # Linha de baixo
        agenda_card = hcard(grid)
        agenda_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self._chart_head(agenda_card, "Aulas de hoje", "5 turmas em atividade")
        self._aulas_table(agenda_card)

        pay_card = hcard(grid)
        pay_card.grid(row=1, column=1, sticky="nsew")
        self._chart_head(pay_card, "Pagamentos recentes", "Últimos registros")
        self._pay_list(pay_card)

    def _chart_head(self, card, title, subtitle):
        head = tk.Frame(card, bg=Theme.PAPER)
        head.pack(fill="x", padx=20, pady=(14, 8))
        tk.Label(head, text=title, bg=Theme.PAPER, fg=Theme.INK,
                 font=Fonts.serif).pack(anchor="w")
        tk.Label(head, text=subtitle, bg=Theme.PAPER, fg=Theme.MUTED,
                 font=Fonts.sans_xs).pack(anchor="w")
        hsep(card).pack(fill="x")

    def _bar_chart(self, card):
        wrap = tk.Frame(card, bg=Theme.PAPER, height=240)
        wrap.pack(fill="x", padx=18, pady=12)

        canvas = tk.Canvas(wrap, height=200, bg=Theme.PAPER, highlightthickness=0)
        canvas.pack(fill="x", expand=True)

        meses = [
            ("Nov", 14, 8,  6),
            ("Dez", 18, 11, 7),
            ("Jan", 24, 14, 9),
            ("Fev", 30, 18, 11),
            ("Mar", 36, 22, 14),
            ("Abr", 47, 28, 19),
        ]
        max_val = max(sum(m[1:]) for m in meses)
        canvas.update_idletasks()

        def redraw(_e=None):
            canvas.delete("all")
            w = canvas.winfo_width()
            h = 200
            n = len(meses)
            pad_left, pad_right = 30, 30
            avail = w - pad_left - pad_right
            col_w = avail / n
            bar_w = col_w * 0.45

            # linhas guia
            for frac in (0.33, 0.66, 1.0):
                y = h - 30 - (h - 50) * frac + (h - 50)
                y2 = h - 30 - (h - 50) * frac
                canvas.create_line(pad_left, y2, w - pad_right, y2,
                                   fill=Theme.PAPER_3, dash=(2, 4))

            for i, (m, lead, contato, mat) in enumerate(meses):
                cx = pad_left + col_w * i + col_w / 2
                base = h - 30
                total = lead + contato + mat
                scale = (h - 60) / max_val

                # empilhado: lead (papel), contato (accent), matriculados (forest)
                y = base
                lead_h = lead * scale
                contato_h = contato * scale
                mat_h = mat * scale

                canvas.create_rectangle(cx - bar_w / 2, y - mat_h, cx + bar_w / 2, y,
                                        fill=Theme.FOREST, outline="")
                y -= mat_h + 1
                canvas.create_rectangle(cx - bar_w / 2, y - contato_h, cx + bar_w / 2, y,
                                        fill=Theme.ACCENT, outline="")
                y -= contato_h + 1
                canvas.create_rectangle(cx - bar_w / 2, y - lead_h, cx + bar_w / 2, y,
                                        fill=Theme.PAPER_3, outline=Theme.LINE_2)

                canvas.create_text(cx, base + 14, text=m, fill=Theme.MUTED,
                                   font=Fonts.sans_xs)

        canvas.bind("<Configure>", redraw)
        # legenda
        legend = tk.Frame(card, bg=Theme.PAPER)
        legend.pack(fill="x", padx=20, pady=(0, 16))
        for color, text in [
            (Theme.FOREST,  "Matriculados"),
            (Theme.ACCENT,  "Em contato"),
            (Theme.PAPER_3, "Leads novos"),
        ]:
            item = tk.Frame(legend, bg=Theme.PAPER)
            item.pack(side="left", padx=(0, 18))
            tk.Frame(item, width=10, height=10, bg=color,
                     highlightthickness=1, highlightbackground=Theme.LINE_2
                     ).pack(side="left", padx=(0, 6))
            tk.Label(item, text=text, bg=Theme.PAPER, fg=Theme.MUTED_2,
                     font=Fonts.sans_xs).pack(side="left")

    def _origem_list(self, card):
        items = [
            ("Instagram",  "Tráfego orgânico",   "18", 0.85),
            ("Indicação",  "Cliente atual",      "14", 0.66),
            ("Presencial", "Walk-in / panfleto", "9",  0.42),
            ("Site",       "Formulário",         "6",  0.28),
        ]
        for i, (name, sub, value, frac) in enumerate(items):
            row = tk.Frame(card, bg=Theme.PAPER)
            row.pack(fill="x", padx=20, pady=8)
            box = tk.Label(row, text=name[0], bg=Theme.PAPER_2, fg=Theme.INK_3,
                           font=Fonts.sans_bold, width=2, height=1, padx=8, pady=4)
            box.pack(side="left", padx=(0, 12))

            mid = tk.Frame(row, bg=Theme.PAPER)
            mid.pack(side="left", fill="x", expand=True)
            tk.Label(mid, text=name, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.sans_bold, anchor="w").pack(anchor="w")
            tk.Label(mid, text=sub, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.sans_xs, anchor="w").pack(anchor="w")
            bar = tk.Frame(mid, height=4, bg=Theme.PAPER_2)
            bar.pack(fill="x", pady=(4, 0))
            fill = tk.Frame(bar, height=4, bg=Theme.ACCENT)
            fill.place(relwidth=frac, relheight=1)

            tk.Label(row, text=value, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.mono_bold).pack(side="right")

            if i < len(items) - 1:
                hsep(card, color=Theme.PAPER_2).pack(fill="x", padx=20)

    def _aulas_table(self, card):
        rows = [
            ("07:30 – 09:00", "ING-A2-MA", "Inglês · Módulo 3",       "Sala 04", "12 / 14", ("Em andamento",      "success")),
            ("09:15 – 10:45", "ESP-B1-MA", "Espanhol · Intermediário","Sala 02", "9 / 12",  ("Iniciará em breve", "info")),
            ("14:00 – 15:30", "FRA-A1-TA", "Francês · Iniciante",     "Sala 06", "8 / 10",  ("Agendada",          "neutral")),
            ("19:00 – 20:30", "ING-C1-NO", "Inglês · Avançado",       "Sala 01", "11 / 12", ("Agendada",          "neutral")),
            ("20:30 – 22:00", "JAP-A1-NO", "Japonês · Iniciante",     "Sala 03", "7 / 8",   ("Professor ausente", "warning")),
        ]
        header = ["Horário", "Código", "Curso", "Sala", "Vagas", "Status"]
        TableBuilder(card, header, rows, weights=[1, 1, 2, 1, 1, 1.5],
                     status_columns={5}).pack(fill="both", padx=8, pady=8)

    def _pay_list(self, card):
        rows = [
            ("✓",  "Helena Brandão",     "Mensalidade · Abril",   "R$ 420", Theme.SUCCESS),
            ("✓",  "Rafael Monteiro",    "Matrícula · Inglês C1", "R$ 850", Theme.SUCCESS),
            ("⏱",  "Tomás Albuquerque",  "Pendente · Vence 20/04","R$ 420", Theme.WARNING),
            ("!",  "Clara Ishikawa",     "Atrasado · 7 dias",     "R$ 480", Theme.DANGER),
            ("✓",  "Beatriz Coutinho",   "Mensalidade · Abril",   "R$ 520", Theme.SUCCESS),
        ]
        for icon, name, desc, amount, color in rows:
            row = tk.Frame(card, bg=Theme.PAPER)
            row.pack(fill="x", padx=20, pady=8)
            tk.Label(row, text=icon, bg=Theme.PAPER_2, fg=color,
                     font=Fonts.sans_bold, width=3, height=1, padx=4, pady=4
                     ).pack(side="left", padx=(0, 12))
            mid = tk.Frame(row, bg=Theme.PAPER)
            mid.pack(side="left", fill="x", expand=True)
            tk.Label(mid, text=name, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.sans_bold, anchor="w").pack(anchor="w")
            tk.Label(mid, text=desc, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.sans_xs, anchor="w").pack(anchor="w")
            tk.Label(row, text=amount, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.mono_bold).pack(side="right")


class TableBuilder(tk.Frame):
    """Tabela leve usando Frames + Labels (controle total de cores)."""

    def __init__(self, parent, headers: list[str], rows: list[tuple],
                 weights: list[float] | None = None,
                 status_columns: set[int] | None = None):
        super().__init__(parent, bg=Theme.PAPER)
        self.headers = headers
        self.rows = rows
        self.weights = weights or [1] * len(headers)
        self.status_columns = status_columns or set()

        head = tk.Frame(self, bg=Theme.PAPER_2)
        head.pack(fill="x")
        for i, h in enumerate(headers):
            tk.Label(head, text=h.upper(), bg=Theme.PAPER_2, fg=Theme.MUTED,
                     font=Fonts.label, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=i, sticky="ew")
            head.grid_columnconfigure(i, weight=int(self.weights[i] * 10))
        hsep(self).pack(fill="x")

        for r_idx, row in enumerate(rows):
            line = tk.Frame(self, bg=Theme.PAPER)
            line.pack(fill="x")
            for c_idx, cell in enumerate(row):
                line.grid_columnconfigure(c_idx, weight=int(self.weights[c_idx] * 10))
                if c_idx in self.status_columns and isinstance(cell, tuple):
                    container = tk.Frame(line, bg=Theme.PAPER, padx=10, pady=8)
                    container.grid(row=0, column=c_idx, sticky="w")
                    Badge(container, cell[0], cell[1]).pack(anchor="w")
                else:
                    text = str(cell)
                    is_mono = c_idx == 4 and "/" in text
                    tk.Label(line, text=text, bg=Theme.PAPER, fg=Theme.INK,
                             font=Fonts.mono if is_mono else Fonts.sans_md,
                             anchor="w", padx=12, pady=10
                             ).grid(row=0, column=c_idx, sticky="ew")
            hsep(self, color=Theme.PAPER_2).pack(fill="x")


class FunilView(ViewBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.head(
            "Funil de", "Vendas",
            "Acompanhe cada lead desde o primeiro contato até a matrícula. "
            "Cada coluna representa um estágio do processo comercial.",
            actions=[("Filtros", "secondary"), ("+ Novo lead", "primary")],
        )
        self._summary()
        self._kanban()

    def _summary(self):
        bar = hcard(self)
        bar.pack(fill="x", padx=28, pady=(0, 16))
        inner = tk.Frame(bar, bg=Theme.PAPER)
        inner.pack(fill="x", padx=16, pady=12)

        for label, options in [
            ("Origem:", ["Todas", "Instagram", "Indicação", "Presencial"]),
            ("Vendedor:", ["Todos", "Henrique", "Paula"]),
            ("Curso:", ["Todos", "Inglês", "Espanhol"]),
            ("Período:", ["Últimos 30 dias"]),
        ]:
            box = tk.Frame(inner, bg=Theme.PAPER_2,
                           highlightthickness=1, highlightbackground=Theme.LINE)
            box.pack(side="left", padx=(0, 8))
            tk.Label(box, text=label, bg=Theme.PAPER_2, fg=Theme.MUTED,
                     font=Fonts.sans_xs, padx=8, pady=4).pack(side="left")
            cb = ttk.Combobox(box, values=options, width=14, state="readonly")
            cb.set(options[0])
            cb.pack(side="left", padx=(0, 6), pady=2)

        Badge(inner, "47 leads · R$ 38.290 em potencial", "accent").pack(side="right")

    def _kanban(self):
        wrap = tk.Frame(self, bg=Theme.PAPER)
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 28))

        # canvas horizontal scroll para caber todas as colunas
        h_canvas = tk.Canvas(wrap, bg=Theme.PAPER, highlightthickness=0, height=580)
        h_scroll = ttk.Scrollbar(wrap, orient="horizontal", command=h_canvas.xview)
        h_canvas.configure(xscrollcommand=h_scroll.set)
        h_canvas.pack(side="top", fill="both", expand=True)
        h_scroll.pack(side="bottom", fill="x")

        inner = tk.Frame(h_canvas, bg=Theme.PAPER)
        h_canvas.create_window((0, 0), window=inner, anchor="nw")

        column_color = {
            "Novo lead":   Theme.SKY,
            "Em contato":  Theme.OCHRE,
            "Interessado": Theme.ACCENT,
            "Negociando":  Theme.PLUM,
            "Matriculado": Theme.FOREST,
            "Perdido":     Theme.MUTED,
        }

        for col_name, leads in FUNIL.items():
            col = tk.Frame(inner, bg=Theme.PAPER_2,
                           highlightthickness=1, highlightbackground=Theme.LINE,
                           width=240)
            col.pack(side="left", fill="y", padx=6, pady=8, ipady=8)
            col.pack_propagate(False)

            head = tk.Frame(col, bg=Theme.PAPER_2)
            head.pack(fill="x", padx=10, pady=(8, 6))
            tk.Frame(head, width=8, height=8, bg=column_color[col_name]
                     ).pack(side="left", padx=(0, 6))
            tk.Label(head, text=col_name.upper(), bg=Theme.PAPER_2, fg=Theme.INK,
                     font=Fonts.label).pack(side="left")
            tk.Label(head, text=str(len(leads)), bg=Theme.PAPER, fg=Theme.MUTED_2,
                     font=Fonts.mono, padx=6).pack(side="right")

            hsep(col, color=Theme.LINE_2).pack(fill="x", padx=10, pady=(0, 6))

            for lead in leads:
                self._kanban_card(col, lead, column_color[col_name])

            add = tk.Label(col, text="+ Adicionar lead", bg=Theme.PAPER_2,
                           fg=Theme.MUTED, font=Fonts.sans_md, pady=8,
                           cursor="hand2",
                           highlightthickness=1, highlightbackground=Theme.LINE_2)
            add.pack(fill="x", padx=10, pady=(8, 0))

        inner.update_idletasks()
        h_canvas.configure(scrollregion=h_canvas.bbox("all"), height=560)

    def _kanban_card(self, parent, lead: Lead, accent_color: str):
        card = tk.Frame(parent, bg=Theme.PAPER,
                        highlightthickness=1, highlightbackground=Theme.LINE)
        card.pack(fill="x", padx=10, pady=4)

        top = tk.Frame(card, bg=Theme.PAPER)
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(top, text=lead.name, bg=Theme.PAPER, fg=Theme.INK,
                 font=Fonts.sans_bold, anchor="w").pack(side="left")
        if lead.badge:
            Badge(top, lead.badge[0], lead.badge[1]).pack(side="right")

        tk.Label(card, text=lead.course, bg=Theme.PAPER, fg=Theme.ACCENT,
                 font=Fonts.sans_bold, anchor="w"
                 ).pack(fill="x", padx=10, pady=(0, 8))

        meta = tk.Frame(card, bg=Theme.PAPER)
        meta.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(meta, text=lead.origin, bg=Theme.PAPER, fg=Theme.MUTED_2,
                 font=Fonts.sans_xs, anchor="w").pack(side="left")
        if lead.value:
            tk.Label(meta, text=lead.value, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.mono_bold).pack(side="right")


class AlunosView(ViewBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.head(
            "Alunos", "matriculados",
            "Base total de 284 alunos ativos. Consulte dados de cadastro, "
            "turma atual, frequência e situação financeira.",
            actions=[("Exportar", "secondary"), ("+ Novo aluno", "primary")],
        )
        self._table()

    def _table(self):
        card = hcard(self)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        self._toolbar(card)

        # Cabeçalho
        cols = ("aluno", "contato", "turma", "matricula", "freq", "situacao")
        headers = ("Aluno", "Contato", "Turma atual", "Matrícula",
                   "Frequência", "Situação")

        tbl = tk.Frame(card, bg=Theme.PAPER)
        tbl.pack(fill="both", expand=True)

        head = tk.Frame(tbl, bg=Theme.PAPER_2)
        head.pack(fill="x")
        weights = [3, 3, 2, 2, 1, 2]
        for i, h in enumerate(headers):
            tk.Label(head, text=h.upper(), bg=Theme.PAPER_2, fg=Theme.MUTED,
                     font=Fonts.label, anchor="w", padx=14, pady=10
                     ).grid(row=0, column=i, sticky="ew")
            head.grid_columnconfigure(i, weight=weights[i])
        hsep(tbl).pack(fill="x")

        for (init, name, sub, mail, phone, turma, mat, freq, freq_kind,
             sit, sit_kind, color_idx) in ALUNOS:
            row = tk.Frame(tbl, bg=Theme.PAPER)
            row.pack(fill="x")
            for i in range(6):
                row.grid_columnconfigure(i, weight=weights[i])

            # Aluno
            cell0 = tk.Frame(row, bg=Theme.PAPER, padx=14, pady=10)
            cell0.grid(row=0, column=0, sticky="ew")
            Avatar(cell0, init, size=30, color_index=color_idx).pack(side="left")
            box = tk.Frame(cell0, bg=Theme.PAPER)
            box.pack(side="left", padx=(10, 0))
            tk.Label(box, text=name, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.sans_bold, anchor="w").pack(anchor="w")
            tk.Label(box, text=sub, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.sans_xs, anchor="w").pack(anchor="w")

            # Contato
            cell1 = tk.Frame(row, bg=Theme.PAPER, padx=14, pady=10)
            cell1.grid(row=0, column=1, sticky="ew")
            tk.Label(cell1, text=mail, bg=Theme.PAPER, fg=Theme.MUTED_2,
                     font=Fonts.sans_md, anchor="w").pack(anchor="w")
            tk.Label(cell1, text=phone, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.mono, anchor="w").pack(anchor="w")

            # Turma
            cell2 = tk.Frame(row, bg=Theme.PAPER, padx=14, pady=10)
            cell2.grid(row=0, column=2, sticky="w")
            tag = tk.Label(cell2, text=" • " + turma + " ", bg=Theme.PAPER_2,
                           fg=Theme.INK_3, font=Fonts.mono_bold,
                           padx=4, pady=2)
            tag.pack(anchor="w")

            # Matrícula
            tk.Label(row, text=mat, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.mono, anchor="w", padx=14, pady=10
                     ).grid(row=0, column=3, sticky="ew")

            # Frequência
            cell4 = tk.Frame(row, bg=Theme.PAPER, padx=14, pady=10)
            cell4.grid(row=0, column=4, sticky="w")
            kind_color = {"good": Theme.SUCCESS,
                          "mid":  Theme.WARNING,
                          "bad":  Theme.DANGER}[freq_kind]
            tk.Label(cell4, text=freq, bg=Theme.PAPER, fg=kind_color,
                     font=Fonts.mono_bold, padx=6, pady=2).pack(anchor="w")

            # Situação
            cell5 = tk.Frame(row, bg=Theme.PAPER, padx=14, pady=10)
            cell5.grid(row=0, column=5, sticky="w")
            Badge(cell5, sit, sit_kind).pack(anchor="w")

            hsep(tbl, color=Theme.PAPER_2).pack(fill="x")

    def _toolbar(self, parent):
        bar = tk.Frame(parent, bg=Theme.PAPER)
        bar.pack(fill="x", padx=14, pady=12)
        for label, options in [
            ("Curso:",    ["Todos", "Inglês", "Espanhol"]),
            ("Turno:",    ["Todos", "Manhã", "Tarde", "Noite"]),
            ("Situação:", ["Ativos", "Inadimplentes", "Cancelados"]),
        ]:
            box = tk.Frame(bar, bg=Theme.PAPER_2,
                           highlightthickness=1, highlightbackground=Theme.LINE)
            box.pack(side="left", padx=(0, 8))
            tk.Label(box, text=label, bg=Theme.PAPER_2, fg=Theme.MUTED,
                     font=Fonts.sans_xs, padx=8, pady=4).pack(side="left")
            cb = ttk.Combobox(box, values=options, width=14, state="readonly")
            cb.set(options[0])
            cb.pack(side="left", padx=(0, 6), pady=2)
        hsep(parent).pack(fill="x")


class MatriculasView(ViewBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.head(
            "Matrículas", "ativas",
            "Cada matrícula vincula um aluno a uma turma específica, "
            "incluindo plano de pagamento e data de início.",
            actions=[("Exportar", "secondary"), ("+ Nova matrícula", "primary")],
        )

        card = hcard(self)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 28))

        headers = ["Ref.", "Aluno", "Curso · Turma", "Início", "Plano", "Mensalidade", "Status"]
        weights = [1, 2.5, 2.5, 1.2, 1.4, 1.2, 1.2]
        rows = [
            ("MAT-2026-0148", "Helena Brandão",    "Inglês · ING-B2-MA",   "12/02/2026", "10× cartão", "R$ 420,00", ("Ativa", "success")),
            ("MAT-2026-0162", "Rafael Monteiro",   "Inglês · ING-C1-NO",   "03/04/2026", "PIX à vista","R$ 850,00", ("Ativa", "success")),
            ("MAT-2026-0119", "Tomás Albuquerque", "Espanhol · ESP-B1-MA", "18/01/2026", "Boleto 12×", "R$ 380,00", ("Pendente", "warning")),
            ("MAT-2026-0085", "Clara Ishikawa",    "Japonês · JAP-A2-NO",  "22/11/2025", "Boleto 12×", "R$ 480,00", ("Inadimplente", "danger")),
            ("MAT-2026-0173", "Beatriz Coutinho",  "Italiano · ITA-A2-TA", "09/04/2026", "Cartão 6×",  "R$ 520,00", ("Ativa", "success")),
            ("MAT-2026-0181", "Gabriel Fontes",    "Inglês · ING-C1-NO",   "14/04/2026", "PIX à vista","R$ 1.280,00",("Ativa", "success")),
            ("MAT-2026-0189", "Teresa Holanda",    "Alemão · ALE-A1-TA",   "15/04/2026", "Cartão 10×", "R$ 420,00", ("Ativa", "success")),
        ]
        TableBuilder(card, headers, rows, weights=weights,
                     status_columns={6}).pack(fill="both", expand=True)


class PagamentosView(ViewBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.head(
            "Movimento", "financeiro",
            "Recebimentos do mês, pagamentos pendentes e inadimplência. "
            "Acompanhe boletos, PIX e cartões em um só lugar.",
            actions=[("Gerar boletos", "secondary"), ("+ Lançar pagamento", "primary")],
        )

        # KPIs
        kpi_row = tk.Frame(self, bg=Theme.PAPER)
        kpi_row.pack(fill="x", padx=28, pady=(0, 16))

        kpis = [
            ("RECEBIDO NO MÊS",        "R$",  "84.320", "+16,2%", "up", Theme.INK),
            ("A RECEBER",              "R$",  "27.480", None,     None, Theme.INK),
            ("EM ATRASO",              "R$",  "5.240",  None,     None, Theme.DANGER),
            ("TAXA DE INADIMPLÊNCIA",  "",    "4,7%",   "−1,3 pp","down", Theme.INK),
        ]
        for i, (label, unit, value, delta, dir_, color) in enumerate(kpis):
            card = hcard(kpi_row)
            card.grid(row=0, column=i, sticky="nsew",
                      padx=(0 if i == 0 else 8, 0))
            kpi_row.grid_columnconfigure(i, weight=1, uniform="kp")

            inner = tk.Frame(card, bg=Theme.PAPER, padx=18, pady=14)
            inner.pack(fill="both", expand=True)
            tk.Label(inner, text=label, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.label, anchor="w").pack(anchor="w")

            value_row = tk.Frame(inner, bg=Theme.PAPER)
            value_row.pack(anchor="w", pady=(6, 6))
            if unit:
                tk.Label(value_row, text=unit + " ", bg=Theme.PAPER,
                         fg=Theme.MUTED, font=Fonts.sans_md).pack(side="left")
            tk.Label(value_row, text=value, bg=Theme.PAPER, fg=color,
                     font=(Fonts.serif_xl.actual("family"), 24)).pack(side="left")

            if delta:
                col = Theme.SUCCESS if dir_ == "up" else Theme.DANGER
                tk.Label(inner, text=("▲ " if dir_ == "up" else "▼ ") + delta,
                         bg=Theme.PAPER, fg=col, font=Fonts.sans_xs
                         ).pack(anchor="w")

        card = hcard(self)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 28))

        # Tabs
        tabs = tk.Frame(card, bg=Theme.PAPER, padx=14, pady=12)
        tabs.pack(fill="x")
        tab_box = tk.Frame(tabs, bg=Theme.PAPER_2)
        tab_box.pack(side="left")
        for i, name in enumerate(["Todos", "Pagos", "Pendentes", "Atrasados"]):
            bg = Theme.PAPER if i == 0 else Theme.PAPER_2
            fg = Theme.INK if i == 0 else Theme.MUTED_2
            tk.Label(tab_box, text=name, bg=bg, fg=fg,
                     font=Fonts.sans_bold, padx=14, pady=6
                     ).pack(side="left", padx=2, pady=2)
        hsep(card).pack(fill="x")

        # Tabela de pagamentos
        headers = ["Ref.", "Aluno", "Descrição", "Método", "Vencimento",
                   "Pago em", "Valor", "Status"]
        weights = [1.1, 2.2, 2.4, 1.3, 1.3, 1.3, 1.5, 1.5]

        tbl = tk.Frame(card, bg=Theme.PAPER)
        tbl.pack(fill="both", expand=True)

        head = tk.Frame(tbl, bg=Theme.PAPER_2)
        head.pack(fill="x")
        for i, h in enumerate(headers):
            tk.Label(head, text=h.upper(), bg=Theme.PAPER_2, fg=Theme.MUTED,
                     font=Fonts.label, anchor="w" if i != 6 else "e",
                     padx=12, pady=10
                     ).grid(row=0, column=i, sticky="ew")
            head.grid_columnconfigure(i, weight=int(weights[i] * 10))
        hsep(tbl).pack(fill="x")

        for ref, init, name, color_idx, desc, method, due, paid, value, status, kind in PAGAMENTOS:
            row = tk.Frame(tbl, bg=Theme.PAPER)
            row.pack(fill="x")
            for i in range(8):
                row.grid_columnconfigure(i, weight=int(weights[i] * 10))

            tk.Label(row, text=ref, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.mono, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=0, sticky="ew")

            cell1 = tk.Frame(row, bg=Theme.PAPER, padx=12, pady=8)
            cell1.grid(row=0, column=1, sticky="ew")
            Avatar(cell1, init, size=28, color_index=color_idx).pack(side="left")
            tk.Label(cell1, text=" " + name, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.sans_bold).pack(side="left", padx=(8, 0))

            tk.Label(row, text=desc, bg=Theme.PAPER, fg=Theme.INK_3,
                     font=Fonts.sans_md, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=2, sticky="ew")

            cell3 = tk.Frame(row, bg=Theme.PAPER, padx=12, pady=8)
            cell3.grid(row=0, column=3, sticky="w")
            Badge(cell3, method, "neutral").pack(anchor="w")

            due_color = Theme.DANGER if kind == "danger" else Theme.MUTED
            tk.Label(row, text=due, bg=Theme.PAPER, fg=due_color,
                     font=Fonts.mono, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=4, sticky="ew")
            tk.Label(row, text=paid, bg=Theme.PAPER,
                     fg=Theme.MUTED if paid == "—" else Theme.INK,
                     font=Fonts.mono, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=5, sticky="ew")

            value_color = Theme.DANGER if kind == "danger" else Theme.INK
            tk.Label(row, text=value, bg=Theme.PAPER, fg=value_color,
                     font=Fonts.mono_bold, anchor="e", padx=12, pady=10
                     ).grid(row=0, column=6, sticky="ew")

            cell7 = tk.Frame(row, bg=Theme.PAPER, padx=12, pady=8)
            cell7.grid(row=0, column=7, sticky="w")
            Badge(cell7, status, kind).pack(anchor="w")

            hsep(tbl, color=Theme.PAPER_2).pack(fill="x")


class CursosView(ViewBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.head(
            "Catálogo de", "cursos",
            "Seis cursos ativos, organizados por idioma e nível CEFR. "
            "Cada curso possui turmas associadas em diferentes turnos.",
            actions=[("+ Novo curso", "primary")],
        )

        grid = tk.Frame(self, bg=Theme.PAPER)
        grid.pack(fill="both", expand=True, padx=28, pady=(0, 28))

        cols = 3
        for i in range(cols):
            grid.grid_columnconfigure(i, weight=1, uniform="course")

        for i, (flag, name, code, color, desc, t, a, p) in enumerate(CURSOS):
            r, c = divmod(i, cols)
            card = hcard(grid)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            banner = tk.Frame(card, bg=color, height=86)
            banner.pack(fill="x")
            banner.pack_propagate(False)
            tk.Label(banner, text=flag, bg=color, fg=Theme.PAPER,
                     font=(Fonts.serif_lg.actual("family"), 28, "italic")
                     ).pack(side="left", anchor="sw", padx=14, pady=8)

            body = tk.Frame(card, bg=Theme.PAPER)
            body.pack(fill="both", expand=True, padx=18, pady=14)
            tk.Label(body, text=code, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.mono, anchor="w").pack(anchor="w")
            tk.Label(body, text=name, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.serif, anchor="w").pack(anchor="w", pady=(2, 8))
            tk.Label(body, text=desc, bg=Theme.PAPER, fg=Theme.MUTED_2,
                     font=Fonts.sans_md, wraplength=240, justify="left",
                     anchor="w").pack(anchor="w")

            hsep(body, color=Theme.PAPER_3).pack(fill="x", pady=(12, 8))
            row = tk.Frame(body, bg=Theme.PAPER)
            row.pack(fill="x")
            for j, (lbl, val) in enumerate([("Turmas", t), ("Alunos", a), ("Desde", p)]):
                box = tk.Frame(row, bg=Theme.PAPER)
                box.pack(side="left", expand=True, fill="x")
                tk.Label(box, text=lbl.upper(), bg=Theme.PAPER, fg=Theme.MUTED,
                         font=Fonts.label).pack()
                tk.Label(box, text=val, bg=Theme.PAPER, fg=Theme.INK,
                         font=Fonts.mono_bold).pack()


class TurmasView(ViewBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.head(
            "Turmas", "em atividade",
            "Organização por curso, turno e sala. Acompanhe vagas disponíveis, "
            "professor responsável e status operacional.",
            actions=[("+ Nova turma", "primary")],
        )

        card = hcard(self)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 28))

        headers = ["Código", "Curso", "Turno", "Horário", "Dias", "Sala",
                   "Professor", "Vagas", "Início", "Status"]
        weights = [1.2, 2.2, 1, 1.4, 1.5, 0.6, 1.8, 1, 1, 1.3]

        tbl = tk.Frame(card, bg=Theme.PAPER)
        tbl.pack(fill="both", expand=True)

        head = tk.Frame(tbl, bg=Theme.PAPER_2)
        head.pack(fill="x")
        for i, h in enumerate(headers):
            tk.Label(head, text=h.upper(), bg=Theme.PAPER_2, fg=Theme.MUTED,
                     font=Fonts.label, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=i, sticky="ew")
            head.grid_columnconfigure(i, weight=int(weights[i] * 10))
        hsep(tbl).pack(fill="x")

        turn_kind = {"Manhã": "warning", "Tarde": "accent", "Noite": "plum"}

        for cod, curso, turno, hora, dias, sala, prof, vagas, ini, status, kind in TURMAS:
            row = tk.Frame(tbl, bg=Theme.PAPER)
            row.pack(fill="x")
            for i in range(10):
                row.grid_columnconfigure(i, weight=int(weights[i] * 10))

            tk.Label(row, text=cod, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.mono_bold, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=0, sticky="ew")
            tk.Label(row, text=curso, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.sans_md, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=1, sticky="ew")
            cell2 = tk.Frame(row, bg=Theme.PAPER, padx=12, pady=8)
            cell2.grid(row=0, column=2, sticky="w")
            Badge(cell2, turno, turn_kind.get(turno, "neutral")).pack(anchor="w")

            tk.Label(row, text=hora, bg=Theme.PAPER, fg=Theme.MUTED_2,
                     font=Fonts.mono, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=3, sticky="ew")
            tk.Label(row, text=dias, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.sans_sm, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=4, sticky="ew")
            tk.Label(row, text=sala, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.sans_md, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=5, sticky="ew")
            tk.Label(row, text=prof, bg=Theme.PAPER, fg=Theme.INK_3,
                     font=Fonts.sans_md, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=6, sticky="ew")
            tk.Label(row, text=vagas, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.mono_bold, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=7, sticky="ew")
            tk.Label(row, text=ini, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.mono, anchor="w", padx=12, pady=10
                     ).grid(row=0, column=8, sticky="ew")
            cell9 = tk.Frame(row, bg=Theme.PAPER, padx=12, pady=8)
            cell9.grid(row=0, column=9, sticky="w")
            Badge(cell9, status, kind).pack(anchor="w")

            hsep(tbl, color=Theme.PAPER_2).pack(fill="x")


class FrequenciaView(ViewBase):
    LEGEND = [
        ("P", "Presente",    Theme.SUCCESS, "#e7f1ec"),
        ("F", "Falta",       Theme.DANGER,  "#f3dcd5"),
        ("J", "Justificada", Theme.WARNING, "#f6ecd2"),
        ("·", "Sem aula",    Theme.MUTED,   Theme.PAPER_2),
    ]
    KIND_MAP = {
        "P": (Theme.SUCCESS, "#e7f1ec"),
        "F": (Theme.DANGER,  "#f3dcd5"),
        "J": (Theme.WARNING, "#f6ecd2"),
        "·": (Theme.MUTED,   Theme.PAPER_2),
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.head(
            "Controle de", "Frequência",
            "Registro diário de presença por turma. Alertas automáticos para "
            "alunos com frequência abaixo de 75%.",
            actions=[("Exportar relatório", "secondary"),
                     ("+ Lançar chamada", "primary")],
        )

        card = hcard(self)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 28))

        # Toolbar
        bar = tk.Frame(card, bg=Theme.PAPER, padx=14, pady=12)
        bar.pack(fill="x")
        for label, options in [
            ("Turma:", ["ING-B2-MA · Inglês B2 Manhã", "ESP-B1-MA"]),
            ("Período:", ["Abril/2026"]),
        ]:
            box = tk.Frame(bar, bg=Theme.PAPER_2,
                           highlightthickness=1, highlightbackground=Theme.LINE)
            box.pack(side="left", padx=(0, 8))
            tk.Label(box, text=label, bg=Theme.PAPER_2, fg=Theme.MUTED,
                     font=Fonts.sans_xs, padx=8, pady=4).pack(side="left")
            cb = ttk.Combobox(box, values=options, width=24, state="readonly")
            cb.set(options[0])
            cb.pack(side="left", padx=(0, 6), pady=2)

        legend = tk.Frame(bar, bg=Theme.PAPER)
        legend.pack(side="right")
        for letter, label, fg, bg in self.LEGEND:
            item = tk.Frame(legend, bg=Theme.PAPER)
            item.pack(side="left", padx=6)
            tk.Label(item, text=letter, bg=bg, fg=fg, font=Fonts.mono_bold,
                     width=2, padx=2, pady=1).pack(side="left", padx=(0, 4))
            tk.Label(item, text=label, bg=Theme.PAPER, fg=Theme.MUTED_2,
                     font=Fonts.sans_xs).pack(side="left")

        hsep(card).pack(fill="x")

        # Grade
        grid = tk.Frame(card, bg=Theme.PAPER, padx=18, pady=14)
        grid.pack(fill="both", expand=True)

        # cabeçalho de dias
        head = tk.Frame(grid, bg=Theme.PAPER)
        head.pack(fill="x")
        tk.Label(head, text="ALUNO", bg=Theme.PAPER, fg=Theme.MUTED,
                 font=Fonts.label, width=24, anchor="w").pack(side="left")
        for d in FREQ_DAYS:
            tk.Label(head, text=d, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.mono, width=4).pack(side="left")
        tk.Label(head, text="%", bg=Theme.PAPER, fg=Theme.MUTED,
                 font=Fonts.label, padx=10).pack(side="left")

        hsep(grid, color=Theme.PAPER_2).pack(fill="x", pady=4)

        for init, name, color_idx, marks, pct, kind in FREQUENCIA:
            row = tk.Frame(grid, bg=Theme.PAPER)
            row.pack(fill="x", pady=2)

            name_box = tk.Frame(row, bg=Theme.PAPER, width=200)
            name_box.pack(side="left")
            name_box.pack_propagate(False)
            Avatar(name_box, init, size=26, color_index=color_idx).pack(side="left", padx=(0, 8))
            tk.Label(name_box, text=name, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.sans_bold, anchor="w").pack(side="left")

            for m in marks:
                fg, bg = self.KIND_MAP[m]
                tk.Label(row, text=m, bg=bg, fg=fg, font=Fonts.mono_bold,
                         width=2, padx=4, pady=2,
                         highlightthickness=1, highlightbackground=Theme.LINE
                         ).pack(side="left", padx=2)

            pct_color = {"good": Theme.SUCCESS,
                         "mid":  Theme.WARNING,
                         "bad":  Theme.DANGER}[kind]
            tk.Label(row, text=pct, bg=Theme.PAPER, fg=pct_color,
                     font=Fonts.mono_bold, padx=10).pack(side="left")


class VendedoresView(ViewBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.head(
            "Equipe", "comercial",
            "Performance da equipe de vendas no período. Leads atendidos, "
            "matrículas fechadas e receita gerada por vendedor.",
            actions=[("+ Novo vendedor", "primary")],
        )

        grid = tk.Frame(self, bg=Theme.PAPER)
        grid.pack(fill="both", expand=True, padx=28, pady=(0, 28))

        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="team")

        for i, (init, name, role, color_idx, leads, fechadas, taxa, receita) in enumerate(VENDEDORES):
            r, c = divmod(i, 2)
            card = hcard(grid)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            head = tk.Frame(card, bg=Theme.PAPER, padx=18, pady=18)
            head.pack(fill="x")
            Avatar(head, init, size=44, color_index=color_idx).pack(side="left", padx=(0, 12))
            box = tk.Frame(head, bg=Theme.PAPER)
            box.pack(side="left")
            tk.Label(box, text=name, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.serif).pack(anchor="w")
            tk.Label(box, text=role, bg=Theme.PAPER, fg=Theme.MUTED,
                     font=Fonts.sans_xs).pack(anchor="w")

            hsep(card, color=Theme.PAPER_3).pack(fill="x", padx=18)

            metrics = tk.Frame(card, bg=Theme.PAPER, padx=18, pady=14)
            metrics.pack(fill="x")
            for label, value in [("LEADS", str(leads)),
                                 ("MATRÍCULAS", str(fechadas)),
                                 ("CONVERSÃO", f"{taxa}%")]:
                col = tk.Frame(metrics, bg=Theme.PAPER)
                col.pack(side="left", expand=True, fill="x")
                tk.Label(col, text=value, bg=Theme.PAPER, fg=Theme.INK,
                         font=Fonts.serif).pack()
                tk.Label(col, text=label, bg=Theme.PAPER, fg=Theme.MUTED,
                         font=Fonts.label).pack()

            hsep(card, color=Theme.PAPER_3).pack(fill="x", padx=18)

            prog = tk.Frame(card, bg=Theme.PAPER, padx=18, pady=14)
            prog.pack(fill="x")
            top = tk.Frame(prog, bg=Theme.PAPER)
            top.pack(fill="x")
            tk.Label(top, text="Receita gerada · abril", bg=Theme.PAPER,
                     fg=Theme.MUTED_2, font=Fonts.sans_md).pack(side="left")
            tk.Label(top, text=receita, bg=Theme.PAPER, fg=Theme.INK,
                     font=Fonts.mono_bold).pack(side="right")
            bar_bg = tk.Frame(prog, height=6, bg=Theme.PAPER_2)
            bar_bg.pack(fill="x", pady=(8, 0))
            fill = tk.Frame(bar_bg, height=6, bg=Theme.ACCENT)
            fill.place(relwidth=min(1.0, taxa / 70), relheight=1)


# =====================================================================
# APP PRINCIPAL
# =====================================================================
class App(tk.Tk):
    PAGE_INFO = {
        "dashboard":  ("Visão geral",       "Bom dia, Marina"),
        "funil":      ("CRM Comercial",     "Funil de vendas"),
        "alunos":     ("Cadastro",          "Alunos matriculados"),
        "matriculas": ("Acadêmico",         "Matrículas ativas"),
        "pagamentos": ("Financeiro",        "Movimento financeiro"),
        "cursos":     ("Acadêmico",         "Catálogo de cursos"),
        "turmas":     ("Acadêmico",         "Turmas em atividade"),
        "frequencia": ("Acadêmico",         "Controle de frequência"),
        "vendedores": ("Equipe",            "Equipe comercial"),
    }

    def __init__(self):
        super().__init__()
        self.title("Políglota — Sistema de Gestão Acadêmica")
        self.geometry("1320x800")
        self.minsize(1100, 680)
        self.configure(bg=Theme.PAPER)

        Fonts.init()
        self._init_ttk_styles()

        # Layout principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_navigate=self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.right = tk.Frame(self, bg=Theme.PAPER)
        self.right.grid(row=0, column=1, sticky="nsew")
        self.right.grid_rowconfigure(1, weight=1)
        self.right.grid_columnconfigure(0, weight=1)

        self.topbar = Topbar(self.right)
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.scroll = VScroll(self.right, bg=Theme.PAPER)
        self.scroll.grid(row=1, column=0, sticky="nsew")

        self.views: dict[str, tk.Frame] = {}
        self._build_views()

        self.sidebar.set_active("dashboard")
        self.show_view("dashboard")

    def _init_ttk_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "TCombobox",
            fieldbackground=Theme.PAPER_2,
            background=Theme.PAPER_2,
            foreground=Theme.INK,
            arrowcolor=Theme.MUTED,
            bordercolor=Theme.LINE,
            lightcolor=Theme.LINE,
            darkcolor=Theme.LINE,
        )
        style.map("TCombobox",
                  fieldbackground=[("readonly", Theme.PAPER_2)],
                  foreground=[("readonly", Theme.INK)])
        style.configure("Vertical.TScrollbar",
                        background=Theme.PAPER_3,
                        troughcolor=Theme.PAPER,
                        bordercolor=Theme.PAPER,
                        arrowcolor=Theme.MUTED)
        style.configure("Horizontal.TScrollbar",
                        background=Theme.PAPER_3,
                        troughcolor=Theme.PAPER,
                        bordercolor=Theme.PAPER,
                        arrowcolor=Theme.MUTED)

    def _build_views(self):
        builders = {
            "dashboard":  DashboardView,
            "funil":      FunilView,
            "alunos":     AlunosView,
            "matriculas": MatriculasView,
            "pagamentos": PagamentosView,
            "cursos":     CursosView,
            "turmas":     TurmasView,
            "frequencia": FrequenciaView,
            "vendedores": VendedoresView,
        }
        for vid, cls in builders.items():
            view = cls(self.scroll.body)
            self.views[vid] = view

    def show_view(self, view_id: str):
        for v in self.views.values():
            v.pack_forget()
        view = self.views[view_id]
        view.pack(fill="both", expand=True)
        crumb, title = self.PAGE_INFO[view_id]
        self.topbar.set_page(crumb, title)
        # rolar para o topo
        self.scroll.canvas.yview_moveto(0.0)


# =====================================================================
# ENTRYPOINT
# =====================================================================
def main() -> int:
    try:
        app = App()
    except tk.TclError as exc:
        print(f"Erro ao iniciar a interface gráfica: {exc}", file=sys.stderr)
        return 1
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
