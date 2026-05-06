"""Cards (containers retangulares com sombra e cantos arredondados).

Implementa duas variacoes:
- Card: container basico
- CardComCabecalho: card com titulo e area de conteudo separadas
"""
import tkinter as tk

from config.cores import Cores
from config.fontes import Fontes


class Card(tk.Frame):
    """Frame branco com borda fina, simulando um card de SaaS moderno."""

    def __init__(self, master, padding=18, **kwargs):
        super().__init__(
            master,
            bg=Cores.CARD_FUNDO,
            highlightthickness=1,
            highlightbackground=Cores.CARD_BORDA,
            bd=0,
            **kwargs,
        )
        self.padding = padding
        # Frame interno que respeita o padding
        self.area = tk.Frame(self, bg=Cores.CARD_FUNDO)
        self.area.pack(fill="both", expand=True, padx=padding, pady=padding)

    def conteudo(self) -> tk.Frame:
        return self.area


class CardComCabecalho(tk.Frame):
    """Card com titulo no topo e area de conteudo abaixo."""

    def __init__(self, master, titulo: str = "", icone: str = "",
                 acao_texto: str = "", acao_comando=None, padding=18, **kwargs):
        super().__init__(
            master,
            bg=Cores.CARD_FUNDO,
            highlightthickness=1,
            highlightbackground=Cores.CARD_BORDA,
            bd=0,
            **kwargs,
        )
        self.titulo = titulo
        self.icone = icone

        # Cabecalho
        cabecalho = tk.Frame(self, bg=Cores.CARD_FUNDO)
        cabecalho.pack(fill="x", padx=padding, pady=(padding, 8))

        if icone:
            tk.Label(
                cabecalho, text=icone, bg=Cores.CARD_FUNDO,
                fg=Cores.BOTAO_PRIMARIO, font=(Fontes.FAMILIA, 16),
            ).pack(side="left", padx=(0, 8))

        tk.Label(
            cabecalho, text=titulo, bg=Cores.CARD_FUNDO,
            fg=Cores.TEXTO_PRIMARIO, font=Fontes.TITULO_CARD,
        ).pack(side="left")

        if acao_texto:
            link = tk.Label(
                cabecalho, text=acao_texto, bg=Cores.CARD_FUNDO,
                fg=Cores.BOTAO_PRIMARIO, font=Fontes.PEQUENO_NEGRITO,
                cursor="hand2",
            )
            link.pack(side="right")
            if acao_comando:
                link.bind("<Button-1>", lambda _e: acao_comando())

        # Linha divisoria sutil
        tk.Frame(self, bg=Cores.CARD_BORDA, height=1).pack(
            fill="x", padx=padding,
        )

        # Area de conteudo
        self.area = tk.Frame(self, bg=Cores.CARD_FUNDO)
        self.area.pack(fill="both", expand=True, padx=padding, pady=(12, padding))

    def conteudo(self) -> tk.Frame:
        return self.area
