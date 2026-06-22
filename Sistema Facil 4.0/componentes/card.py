"""
Card moderno com bordas arredondadas usando Canvas.
Usado nos dashboards e telas internas para organizar informacoes.
"""
import tkinter as tk
from componentes.cores import BRANCO, BRANCO_GELO, CINZA_CLARO, PRETO_TEXTO, FONTE_TITULO, FONTE_TEXTO


class Card(tk.Canvas):
    """
    Card com bordas arredondadas desenhado em Canvas com container interno.

    Args:
        master: widget pai
        titulo: titulo opcional do card
        cor_fundo: cor de fundo do card
        padding: padding interno do conteudo
        raio: raio de arredondamento das bordas
    """

    def __init__(self, master, titulo=None, cor_fundo=BRANCO,
                 padding=18, raio=12, **kwargs):
        
        try:
            parent_bg = master.cget("bg")
        except Exception:
            parent_bg = BRANCO_GELO
            
        super().__init__(
            master,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        
        self.cor_fundo = cor_fundo
        self.raio = raio
        
        # Frame container que fica por cima do Canvas
        self.frame_container = tk.Frame(self, bg=cor_fundo)
        self.window_id = self.create_window((0, 0), window=self.frame_container, anchor="nw")
        
        # Ajusta dinamicamente a altura do Canvas conforme os filhos do frame_container mudam
        self.frame_container.bind("<Configure>", self._atualizar_altura_canvas)
        
        # Frame interno com padding para os filhos (antigo self.interno)
        self.interno = tk.Frame(self.frame_container, bg=cor_fundo)
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
            
        self.bind("<Configure>", self._redimensionar)

    def _atualizar_altura_canvas(self, event):
        req_h = self.frame_container.winfo_reqheight()
        if self.cget("height") != str(req_h):
            self.configure(height=req_h)

    def _redimensionar(self, event):
        self.delete("fundo")
        w, h = event.width, event.height
        r = self.raio
        
        # Desenha poligono do card com cantos arredondados
        pontos = [
            r, 0,
            w - r, 0,
            w, 0,
            w, r,
            w, h - r,
            w, h,
            w - r, h,
            r, h,
            0, h,
            0, h - r,
            0, r,
            0, 0
        ]
        self.create_polygon(pontos, fill=self.cor_fundo, outline=CINZA_CLARO, smooth=True, width=1, tags="fundo")
        self.tag_lower("fundo")
        
        # Reposiciona o container interno com uma pequena folga para a borda
        pad = 1
        self.coords(self.window_id, pad, pad)
        self.itemconfig(self.window_id, width=w - 2 * pad, height=h - 2 * pad)

    def adicionar(self, widget):
        """Adiciona um widget ao container interno do card (mantem compatibilidade)."""
        widget.pack(in_=self.interno, fill="x", pady=4)
