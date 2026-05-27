"""
Logo SF desenhado em Canvas Tkinter - sem fundo recortado.

O logo e desenhado vetorialmente para nao ter o problema de fundo
branco/preto recortado de imagens. Usa as cores oficiais da marca.
"""
import tkinter as tk
from componentes.cores import AZUL_PRIMARIO, AMARELO_VIBRANTE, AZUL_ESCURO


class LogoSF(tk.Canvas):
    """
    Logo SF (Sistema Facil) - circulo com letras S amarela e F azul,
    com chapeu de formatura no topo.

    Args:
        master: widget pai
        tamanho: diametro do logo em pixels (default 80)
        cor_fundo: cor de fundo do canvas (deve combinar com o pai)
    """

    def __init__(self, master, tamanho=80, cor_fundo="#FFFFFF", **kwargs):
        super().__init__(
            master,
            width=tamanho,
            height=tamanho,
            bg=cor_fundo,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.tamanho = tamanho
        self.cor_fundo = cor_fundo
        self._desenhar()

    def _desenhar(self):
        """Desenha o logo SF no canvas."""
        t = self.tamanho
        margem = 2

        # Anel externo azul
        self.create_oval(
            margem, margem, t - margem, t - margem,
            outline=AZUL_PRIMARIO, width=max(2, t // 30),
            fill=self.cor_fundo
        )

        # Anel amarelo interno
        margem_amarelo = t * 0.08
        self.create_oval(
            margem_amarelo, margem_amarelo,
            t - margem_amarelo, t - margem_amarelo,
            outline=AMARELO_VIBRANTE, width=max(2, t // 35),
            fill=self.cor_fundo
        )

        # Letra "S" amarela (lado esquerdo)
        fonte_s = ("Georgia", int(t * 0.55), "bold")
        self.create_text(
            t * 0.40, t * 0.55,
            text="S",
            fill=AMARELO_VIBRANTE,
            font=fonte_s
        )

        # Letra "F" azul (lado direito)
        fonte_f = ("Georgia", int(t * 0.55), "bold")
        self.create_text(
            t * 0.62, t * 0.58,
            text="F",
            fill=AZUL_ESCURO,
            font=fonte_f
        )

        # Chapeu de formatura (poligono azul no topo do S)
        meio_x = t * 0.50
        topo_y = t * 0.22
        largura_chapeu = t * 0.32
        altura_chapeu = t * 0.06

        # Base do chapeu (poligono losango)
        self.create_polygon(
            meio_x - largura_chapeu / 2, topo_y,
            meio_x, topo_y - altura_chapeu,
            meio_x + largura_chapeu / 2, topo_y,
            meio_x, topo_y + altura_chapeu,
            fill=AZUL_ESCURO, outline=AZUL_ESCURO
        )

        # Borla (linha + bolinha)
        borla_x = meio_x + largura_chapeu * 0.45
        self.create_line(
            borla_x, topo_y,
            borla_x + t * 0.04, topo_y + t * 0.10,
            fill=AZUL_ESCURO, width=max(1, t // 50)
        )
        self.create_oval(
            borla_x + t * 0.025, topo_y + t * 0.09,
            borla_x + t * 0.06, topo_y + t * 0.13,
            fill=AZUL_ESCURO, outline=AZUL_ESCURO
        )
