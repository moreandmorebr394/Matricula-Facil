"""
componentes/sidebar.py — Sidebar fixa com navegação e logo SF
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
from utils.tema import *
from utils.helpers import badge


ITENS_MENU = [
    ("⊞",  "Dashboard",        True),
    ("👥", "Leads / Alunos",   False),
    ("🛒", "Vendas",           False),
    ("💳", "Pagamentos",       False),
    ("📚", "Turmas",           False),
    ("📖", "Aulas",            False),
    ("📋", "Frequência",       False),
    ("📊", "Funil de Origem",  False, True),   # True = badge "novo"
    ("📈", "Relatórios",       False),
    ("⚙",  "Configurações",    False),
]


class Sidebar(tk.Frame):
    def __init__(self, pai, ao_navegar=None, **kwargs):
        super().__init__(pai, bg=AZUL_ESCURO,
                         width=LARGURA_SIDEBAR, **kwargs)
        self.pack_propagate(False)
        self.ao_navegar = ao_navegar
        self._botoes = []
        self._ativo = 0
        self._construir()

    # ── Logo ──────────────────────────────────────────────────────────────
    def _construir(self):
        # ─ Logo / header ─
        topo = tk.Frame(self, bg=AZUL_ESCURO, pady=0)
        topo.pack(fill="x")

        # Linha dourada decorativa no topo
        tk.Frame(topo, bg=DOURADO, height=3).pack(fill="x")

        logo_area = tk.Frame(topo, bg=AZUL_ESCURO, pady=14, padx=12)
        logo_area.pack(fill="x")

        # Tentar carregar logo SF
        logo_carregada = False
        caminho_logo = os.path.join(os.path.dirname(__file__),
                                    "..", "assets", "logo_sf.png")
        try:
            img = Image.open(os.path.abspath(caminho_logo))
            img = img.resize((42, 42), Image.LANCZOS)
            self._foto_logo = ImageTk.PhotoImage(img)
            tk.Label(logo_area, image=self._foto_logo,
                     bg=AZUL_ESCURO).pack(side="left", padx=(0, 8))
            logo_carregada = True
        except Exception:
            # Fallback: círculo SF desenhado em Canvas
            c = tk.Canvas(logo_area, width=42, height=42,
                          bg=AZUL_ESCURO, highlightthickness=0)
            c.pack(side="left", padx=(0, 8))
            c.create_oval(2, 2, 40, 40, fill=DOURADO, outline=BRANCO, width=2)
            c.create_text(21, 21, text="SF", font=("Segoe UI", 13, "bold"),
                          fill=AZUL_ESCURO)

        # Nome do sistema
        nomes = tk.Frame(logo_area, bg=AZUL_ESCURO)
        nomes.pack(side="left", fill="y")
        tk.Label(nomes, text="Sistema Fácil",
                 font=("Segoe UI", 11, "bold"),
                 fg=BRANCO, bg=AZUL_ESCURO).pack(anchor="w")
        tk.Label(nomes, text="Educação",
                 font=("Segoe UI", 9),
                 fg="#8AAFD4", bg=AZUL_ESCURO).pack(anchor="w")

        # ─ Separador ─
        tk.Frame(self, bg="#2A3F63", height=1).pack(fill="x", padx=12)
        tk.Frame(self, bg=AZUL_ESCURO, height=8).pack(fill="x")

        # ─ Itens de menu ─
        self._frame_menu = tk.Frame(self, bg=AZUL_ESCURO)
        self._frame_menu.pack(fill="both", expand=True)

        for i, item in enumerate(ITENS_MENU):
            icone, nome = item[0], item[1]
            ativo = item[2] if len(item) > 2 else False
            tem_badge = item[3] if len(item) > 3 else False
            self._criar_item(i, icone, nome, ativo, tem_badge)

        # ─ Rodapé: Sair ─
        tk.Frame(self, bg="#2A3F63", height=1).pack(fill="x", padx=12)
        self._criar_sair()

    def _criar_item(self, idx, icone, nome, ativo=False, tem_badge=False):
        cor_bg = AZUL_MEDIO if ativo else AZUL_ESCURO
        cor_texto = BRANCO if ativo else "#8AAFD4"

        f = tk.Frame(self._frame_menu, bg=cor_bg,
                     cursor="hand2", pady=0)
        f.pack(fill="x")

        # Indicador lateral esquerdo
        indicador = tk.Frame(f, bg=DOURADO if ativo else AZUL_ESCURO,
                             width=4)
        indicador.pack(side="left", fill="y")

        conteudo = tk.Frame(f, bg=cor_bg, padx=8, pady=9)
        conteudo.pack(side="left", fill="both", expand=True)

        tk.Label(conteudo, text=icone, font=("Segoe UI", 12),
                 fg=cor_texto, bg=cor_bg, width=2).pack(side="left")

        tk.Label(conteudo, text=nome, font=FONTE_MENU,
                 fg=cor_texto, bg=cor_bg, anchor="w").pack(side="left",
                                                            padx=(4, 0),
                                                            fill="x",
                                                            expand=True)

        if tem_badge:
            b = tk.Label(conteudo, text="NOVO",
                         font=("Segoe UI", 7, "bold"),
                         bg=DOURADO, fg=AZUL_ESCURO,
                         padx=4, pady=1)
            b.pack(side="right", padx=4)

        # Hover
        widgets = [f, conteudo] + list(conteudo.winfo_children())

        def _hover_on(e, bg_alvo=AZUL_MEDIO, fg_alvo=BRANCO,
                      frame=f, cont=conteudo, ind=indicador):
            frame.config(bg=bg_alvo)
            cont.config(bg=bg_alvo)
            for w in cont.winfo_children():
                try:
                    w.config(bg=bg_alvo, fg=fg_alvo)
                except Exception:
                    pass

        def _hover_off(e, ativo_=ativo, frame=f, cont=conteudo, ind=indicador,
                       bg_orig=cor_bg, fg_orig=cor_texto):
            frame.config(bg=bg_orig)
            cont.config(bg=bg_orig)
            for w in cont.winfo_children():
                try:
                    w.config(bg=bg_orig, fg=fg_orig)
                except Exception:
                    pass

        def _clique(e, i=idx):
            self._selecionar(i)
            if self.ao_navegar:
                self.ao_navegar(nome)

        for w in [f, conteudo] + list(conteudo.winfo_children()):
            w.bind("<Enter>", _hover_on)
            w.bind("<Leave>", _hover_off)
            w.bind("<Button-1>", _clique)

        self._botoes.append((f, conteudo, indicador, cor_bg, cor_texto))

    def _criar_sair(self):
        f = tk.Frame(self, bg=AZUL_ESCURO, cursor="hand2", pady=0)
        f.pack(fill="x", pady=(4, 0))
        tk.Frame(f, bg=AZUL_ESCURO, width=4).pack(side="left", fill="y")
        cont = tk.Frame(f, bg=AZUL_ESCURO, padx=8, pady=10)
        cont.pack(side="left", fill="both", expand=True)
        tk.Label(cont, text="🚪", font=("Segoe UI", 12),
                 fg="#E57373", bg=AZUL_ESCURO, width=2).pack(side="left")
        tk.Label(cont, text="Sair", font=FONTE_MENU,
                 fg="#E57373", bg=AZUL_ESCURO).pack(side="left", padx=(4,0))

        for w in [f, cont] + list(cont.winfo_children()):
            w.bind("<Enter>", lambda e: None)
            w.bind("<Button-1>", lambda e: None)

    def _selecionar(self, idx):
        # Reset todos
        for i, (f, cont, ind, bg_orig, fg_orig) in enumerate(self._botoes):
            f.config(bg=AZUL_ESCURO)
            cont.config(bg=AZUL_ESCURO)
            ind.config(bg=AZUL_ESCURO)
            for w in cont.winfo_children():
                try:
                    w.config(bg=AZUL_ESCURO, fg="#8AAFD4")
                except Exception:
                    pass

        # Ativar selecionado
        if idx < len(self._botoes):
            f, cont, ind, _, _ = self._botoes[idx]
            f.config(bg=AZUL_MEDIO)
            cont.config(bg=AZUL_MEDIO)
            ind.config(bg=DOURADO)
            for w in cont.winfo_children():
                try:
                    w.config(bg=AZUL_MEDIO, fg=BRANCO)
                except Exception:
                    pass
        self._ativo = idx
