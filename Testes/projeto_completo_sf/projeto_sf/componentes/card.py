"""
Card moderno com sombra suave e bordas arredondadas.
Usado nos dashboards e telas internas.
"""
import tkinter as tk
from componentes.cores import BRANCO, CINZA_CLARO, PRETO_TEXTO, FONTE_TITULO


class Card(tk.Frame):
    """
    Card com bordas arredondadas (simuladas via borda fina) e padding interno.

    Args:
        master: widget pai
        titulo: titulo opcional do card
        cor_fundo: cor de fundo do card
        padding: padding interno
    """

    def __init__(self, master, titulo=None, cor_fundo=BRANCO,
                 padding=18, **kwargs):
        super().__init__(
            master,
            bg=cor_fundo,
            highlightbackground=CINZA_CLARO,
            highlightthickness=1,
            bd=0,
            **kwargs
        )

        self.cor_fundo = cor_fundo

        # Container interno (com padding)
        self.interno = tk.Frame(self, bg=cor_fundo)
        self.interno.pack(fill="both", expand=True, padx=padding, pady=padding)

        if titulo:
            self.lbl_titulo = tk.Label(
                self.interno,
                text=titulo,
                font=(FONTE_TITULO, 13, "bold"),
                fg=PRETO_TEXTO,
                bg=cor_fundo,
                anchor="w"
            )
            self.lbl_titulo.pack(fill="x", pady=(0, 12))

    def adicionar(self, widget):
        """Adiciona um widget ao container interno do card."""
        widget.pack(in_=self.interno, fill="x", pady=4)
