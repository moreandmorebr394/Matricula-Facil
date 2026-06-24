"""
Cursor personalizado do Sistema Facil.

IMPORTANTE: O cursor nao usa overlay/Toplevel sobre o conteudo, pois
isso bloqueia cliques. Em vez disso, apenas troca o cursor padrao do
sistema para um estilo coerente com o tema (hand2 em botoes, arrow
em outros lugares) e usa cursor "@" customizado quando possivel.

Para nao bloquear cliques, NAO criamos uma janela seguidora.
Apenas configuramos cursores nativos por widget.
"""
import tkinter as tk


# Mapeamento de cursores por tipo de widget
CURSORES = {
    "padrao": "arrow",
    "botao": "hand2",
    "texto": "xterm",
    "link": "hand2",
    "espera": "watch",
    "movimentacao": "fleur",
}


def aplicar_cursor_global(widget, recursivo=True):
    """
    Aplica cursor padrao em todos os widgets recursivamente.
    Nao usa overlay para nao bloquear cliques.
    """
    try:
        classe = widget.winfo_class()

        # Cursores adequados por classe
        if classe in ("Button", "Canvas"):
            # Verifica se tem comando ou bind de clique
            try:
                if widget.cget("cursor") in ("", "arrow"):
                    widget.configure(cursor="hand2")
            except tk.TclError:
                pass
        elif classe in ("Entry", "Text"):
            try:
                widget.configure(cursor="xterm")
            except tk.TclError:
                pass
        elif classe == "Label":
            try:
                widget.configure(cursor="arrow")
            except tk.TclError:
                pass

        if recursivo:
            for filho in widget.winfo_children():
                aplicar_cursor_global(filho, recursivo=True)
    except Exception:
        pass


class RastroCursor:
    """
    Efeito sutil de "particula" que segue o cursor SOMENTE quando
    o usuario clica - nao fica permanente para nao atrapalhar.

    Cria pequenos circulos coloridos no Canvas que somem em ~400ms.
    """

    def __init__(self, canvas, cor="#3C507D", raio=8):
        self.canvas = canvas
        self.cor = cor
        self.raio = raio
        self.particulas_ativas = []

        # Bind apenas no clique para nao gerar overhead
        canvas.bind("<Button-1>", self._criar_particula, add="+")

    def _criar_particula(self, evento):
        """Cria uma particula expansiva no ponto do clique."""
        x, y = evento.x, evento.y
        try:
            id_circulo = self.canvas.create_oval(
                x - self.raio, y - self.raio,
                x + self.raio, y + self.raio,
                fill="", outline=self.cor, width=2
            )
            self.particulas_ativas.append(id_circulo)
            self._animar(id_circulo, x, y, 0)
        except tk.TclError:
            pass

    def _animar(self, id_circulo, x, y, passo):
        """Expande e some o circulo."""
        if passo > 8:
            try:
                self.canvas.delete(id_circulo)
                if id_circulo in self.particulas_ativas:
                    self.particulas_ativas.remove(id_circulo)
            except tk.TclError:
                pass
            return

        try:
            r = self.raio + passo * 3
            self.canvas.coords(id_circulo, x - r, y - r, x + r, y + r)
            self.canvas.after(30, lambda: self._animar(id_circulo, x, y, passo + 1))
        except tk.TclError:
            pass
