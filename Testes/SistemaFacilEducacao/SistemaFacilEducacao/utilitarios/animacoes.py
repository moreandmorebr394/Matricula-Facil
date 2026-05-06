"""Pequenas funcoes utilitarias de animacao."""
import tkinter as tk


def animar_aparecer(widget: tk.Widget, duracao_ms: int = 220):
    """Animacao de fade-in deslocando o widget verticalmente.

    Como tkinter nao suporta opacidade real, usamos place() para
    deslocar o widget e dar a sensacao de "subir e aparecer".
    """
    if not widget.winfo_exists():
        return
    info = widget.place_info()
    if not info or "y" not in info:
        return
    try:
        y_alvo = int(info.get("y", 0))
    except ValueError:
        return
    deslocamento = 18
    passos = 12
    intervalo = max(1, duracao_ms // passos)

    def passo(atual):
        if atual >= passos or not widget.winfo_exists():
            widget.place_configure(y=y_alvo)
            return
        progresso = atual / passos
        # Easing-out cubico
        e = 1 - (1 - progresso) ** 3
        y = int(y_alvo + deslocamento * (1 - e))
        widget.place_configure(y=y)
        widget.after(intervalo, lambda: passo(atual + 1))

    passo(0)


def animar_valor(widget: tk.Label, valor_inicial: float, valor_final: float,
                 duracao_ms: int = 600, prefixo: str = "", sufixo: str = "",
                 casas_decimais: int = 0):
    """Anima a exibicao de um numero contando de inicial a final."""
    passos = 30
    intervalo = max(1, duracao_ms // passos)
    delta = (valor_final - valor_inicial) / passos

    def passo(atual):
        if not widget.winfo_exists():
            return
        if atual >= passos:
            valor = valor_final
            if casas_decimais == 0:
                texto = f"{prefixo}{int(valor):,}".replace(",", ".") + sufixo
            else:
                texto = f"{prefixo}{valor:.{casas_decimais}f}".replace(".", ",") + sufixo
            widget.configure(text=texto)
            return
        valor = valor_inicial + delta * atual
        if casas_decimais == 0:
            texto = f"{prefixo}{int(valor):,}".replace(",", ".") + sufixo
        else:
            texto = f"{prefixo}{valor:.{casas_decimais}f}".replace(".", ",") + sufixo
        widget.configure(text=texto)
        widget.after(intervalo, lambda: passo(atual + 1))

    passo(0)
