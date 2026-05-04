"""
componentes/grafico_funil.py — Funil de origem desenhado com Canvas
"""

import tkinter as tk
from utils.tema import *


ESTAGIOS_FUNIL = [
    ("Visitantes",   1248, "#1B4FD8", "10.6%"),
    ("Leads",         132, "#27AE60", "47.0%"),
    ("Negociações",    62, "#F39C12", "61.3%"),
    ("Vendas",         38, "#8E44AD", "92.1%"),
    ("Alunos Ativos",  35, "#E91E8C", ""),
]


class GraficoFunil(tk.Canvas):
    def __init__(self, pai, **kwargs):
        largura = kwargs.pop("largura", 260)
        altura  = kwargs.pop("altura",  240)
        super().__init__(pai, width=largura, height=altura,
                         bg=BRANCO, highlightthickness=0, **kwargs)
        self._largura = largura
        self._altura  = altura
        self._desenhar()

    def _desenhar(self):
        self.delete("all")
        w, h = self._largura, self._altura
        n = len(ESTAGIOS_FUNIL)
        altura_seg = (h - 20) / n
        max_larg = w * 0.78
        min_larg = w * 0.22
        cx = w / 2

        for i, (nome, valor, cor, conv) in enumerate(ESTAGIOS_FUNIL):
            # Trapézio
            larg_topo = max_larg - (max_larg - min_larg) * (i / n)
            larg_base = max_larg - (max_larg - min_larg) * ((i+1) / n)
            y_topo = 10 + i * altura_seg
            y_base = y_topo + altura_seg - 3

            x1t = cx - larg_topo/2
            x2t = cx + larg_topo/2
            x1b = cx - larg_base/2
            x2b = cx + larg_base/2

            pontos = [x1t, y_topo, x2t, y_topo, x2b, y_base, x1b, y_base]
            self.create_polygon(pontos, fill=cor, outline=BRANCO, width=2)

            # Texto dentro
            cy_seg = (y_topo + y_base) / 2
            self.create_text(cx, cy_seg - 5, text=nome,
                             font=("Segoe UI", 8, "bold"),
                             fill=BRANCO, anchor="center")
            self.create_text(cx, cy_seg + 8, text=str(valor),
                             font=("Segoe UI", 9, "bold"),
                             fill=BRANCO, anchor="center")

            # Percentual de conversão (entre estágios)
            if conv:
                self.create_text(w - 8, y_base - 2, text=conv,
                                 font=("Segoe UI", 7, "bold"),
                                 fill=CINZA_TEXTO, anchor="e")


class GraficoPizza(tk.Canvas):
    """Gráfico de pizza para origem dos leads."""

    DADOS = [
        ("Instagram",    42, "#1B4FD8"),
        ("Indicação",    31, "#27AE60"),
        ("Google Ads",   24, "#F39C12"),
        ("Facebook Ads", 18, "#8E44AD"),
        ("Site/Orgânico",10, "#E91E8C"),
        ("Outros",        7, "#78909C"),
    ]

    def __init__(self, pai, **kwargs):
        tam = kwargs.pop("tam", 130)
        super().__init__(pai, width=tam * 2 + 10, height=tam + 20,
                         bg=BRANCO, highlightthickness=0, **kwargs)
        self._tam = tam
        self.after(100, self._desenhar)

    def _desenhar(self):
        import math
        self.delete("all")
        tam = self._tam
        cx, cy = tam // 2 + 5, tam // 2 + 10
        r = tam // 2 - 4
        r_int = r * 0.52   # Donut

        total = sum(d[1] for d in self.DADOS)
        angulo = -90.0

        for nome, val, cor in self.DADOS:
            graus = (val / total) * 360
            self.create_arc(cx - r, cy - r, cx + r, cy + r,
                            start=angulo, extent=graus,
                            fill=cor, outline=BRANCO, width=2)
            angulo += graus

        # Buraco central (donut)
        self.create_oval(cx - r_int, cy - r_int,
                         cx + r_int, cy + r_int,
                         fill=BRANCO, outline=BRANCO)
        self.create_text(cx, cy - 6, text=str(total),
                         font=("Segoe UI", 11, "bold"), fill=TEXTO_HEADER)
        self.create_text(cx, cy + 8, text="leads",
                         font=("Segoe UI", 8), fill=CINZA_TEXTO)

        # Legenda
        lx = tam + 16
        ly_start = 12
        for i, (nome, val, cor) in enumerate(self.DADOS):
            ly = ly_start + i * 19
            pct = round(val / total * 100, 1)
            self.create_oval(lx, ly, lx+9, ly+9, fill=cor, outline="")
            self.create_text(lx + 13, ly + 4,
                             text=f"{nome}  {pct}%",
                             font=("Segoe UI", 8),
                             fill=CINZA_ESCURO, anchor="w")
