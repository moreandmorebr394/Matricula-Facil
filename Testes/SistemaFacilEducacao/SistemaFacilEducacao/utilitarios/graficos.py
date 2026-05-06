"""Graficos personalizados desenhados em tk.Canvas.

GraficoFunil: trapezios coloridos empilhados verticalmente, com setas
laterais mostrando os percentuais de conversao entre etapas.

GraficoPizza: gosto-de-rosquinha (donut) com legenda lateral.
"""
import math
import tkinter as tk
from typing import List, Tuple

from config.cores import Cores
from config.fontes import Fontes


class GraficoFunil(tk.Canvas):
    """Funil em forma de trapezios sobrepostos - estilo do mockup."""

    PALETA_PADRAO = [
        Cores.FUNIL_VISITANTES,
        Cores.FUNIL_LEADS,
        Cores.FUNIL_NEGOCIACOES,
        Cores.FUNIL_VENDAS,
        Cores.FUNIL_ALUNOS,
    ]

    def __init__(self, master, dados: List[Tuple[str, int]],
                 largura: int = 360, altura: int = 360, **kwargs):
        cor_fundo = Cores.CARD_FUNDO
        super().__init__(
            master, width=largura, height=altura,
            highlightthickness=0, bd=0, bg=cor_fundo, **kwargs,
        )
        self.dados = dados
        self.largura = largura
        self.altura = altura
        self._desenhar()

    def atualizar(self, dados: List[Tuple[str, int]]):
        self.dados = dados
        self._desenhar()

    def _desenhar(self):
        self.delete("all")
        if not self.dados:
            return

        valores = [v for _, v in self.dados]
        valor_max = max(valores)

        n = len(self.dados)
        margem_topo = 16
        margem_inferior = 16
        margem_lateral = 80  # espaco para as setas/conversao
        altura_disponivel = self.altura - margem_topo - margem_inferior
        altura_secao = altura_disponivel / n

        # Largura de cada secao (trapezio): vai diminuindo
        largura_max = self.largura - 2 * margem_lateral
        largura_min = largura_max * 0.30

        for i, (rotulo, valor) in enumerate(self.dados):
            # Largura proporcional ao valor (comparado ao maior)
            proporcao_topo = valores[i] / valor_max if i == 0 else valores[i - 1] / valor_max
            proporcao_base = valores[i] / valor_max
            proporcao_topo = max(proporcao_topo, 0.30)
            proporcao_base = max(proporcao_base, 0.30)

            largura_topo = largura_max * proporcao_topo
            largura_base = largura_max * proporcao_base
            if i == n - 1:
                largura_base = max(largura_base, largura_min * 0.9)

            cx = self.largura / 2
            y_topo = margem_topo + i * altura_secao
            y_base = y_topo + altura_secao - 2  # gap minusculo

            x1_t = cx - largura_topo / 2
            x2_t = cx + largura_topo / 2
            x1_b = cx - largura_base / 2
            x2_b = cx + largura_base / 2

            cor = self.PALETA_PADRAO[i % len(self.PALETA_PADRAO)]

            # Trapezio (poligono)
            self.create_polygon(
                x1_t, y_topo, x2_t, y_topo, x2_b, y_base, x1_b, y_base,
                fill=cor, outline="",
            )

            # Texto: rotulo + valor centralizado
            y_centro = (y_topo + y_base) / 2
            self.create_text(
                cx, y_centro - 8, text=rotulo,
                fill=Cores.BRANCO, font=Fontes.PEQUENO_NEGRITO,
            )
            self.create_text(
                cx, y_centro + 8, text=f"{valor:,}".replace(",", "."),
                fill=Cores.BRANCO, font=Fontes.SUBTITULO,
            )

            # Setas com taxa de conversao para a proxima etapa
            if i < n - 1:
                proximo = valores[i + 1]
                if valor > 0:
                    pct = proximo / valor * 100
                else:
                    pct = 0
                self._desenhar_seta_conversao(
                    self.largura - margem_lateral + 10,
                    y_base + altura_secao / 2 - 1,
                    pct, rotulo, self.dados[i + 1][0],
                )

    def _desenhar_seta_conversao(self, x, y, pct, de_, para):
        # Texto da conversao
        self.create_text(
            x, y - 8, text=f"{pct:.1f}%", anchor="w",
            fill=Cores.TEXTO_PRIMARIO, font=Fontes.PERCENTUAL,
        )
        self.create_text(
            x, y + 6, text=f"Conversao\n{de_} → {para}", anchor="w",
            fill=Cores.TEXTO_TERCIARIO, font=(Fontes.FAMILIA, 8),
        )


class GraficoPizza(tk.Canvas):
    """Donut chart com legenda lateral."""

    PALETA = [
        Cores.PIZZA_INSTAGRAM,
        Cores.PIZZA_INDICACAO,
        Cores.PIZZA_GOOGLE,
        Cores.PIZZA_FACEBOOK,
        Cores.PIZZA_SITE,
        Cores.PIZZA_OUTROS,
    ]

    def __init__(self, master, dados: List[Tuple[str, int]],
                 largura: int = 360, altura: int = 220, **kwargs):
        cor_fundo = Cores.CARD_FUNDO
        super().__init__(
            master, width=largura, height=altura,
            highlightthickness=0, bd=0, bg=cor_fundo, **kwargs,
        )
        self.dados = dados
        self.largura = largura
        self.altura = altura
        self._desenhar()

    def atualizar(self, dados: List[Tuple[str, int]]):
        self.dados = dados
        self._desenhar()

    def _desenhar(self):
        self.delete("all")
        if not self.dados:
            return

        total = sum(v for _, v in self.dados) or 1

        # Donut a esquerda
        tamanho = min(self.altura - 20, 180)
        x0, y0 = 10, (self.altura - tamanho) / 2
        x1, y1 = x0 + tamanho, y0 + tamanho

        angulo_inicial = 90  # comeca no topo
        for i, (_, valor) in enumerate(self.dados):
            extensao = -(valor / total) * 360  # negativo = sentido horario
            cor = self.PALETA[i % len(self.PALETA)]
            self.create_arc(
                x0, y0, x1, y1,
                start=angulo_inicial, extent=extensao,
                fill=cor, outline=Cores.CARD_FUNDO, width=3,
                style="pieslice",
            )
            angulo_inicial += extensao

        # Buraco central (donut)
        margem_furo = tamanho * 0.30
        self.create_oval(
            x0 + margem_furo, y0 + margem_furo,
            x1 - margem_furo, y1 - margem_furo,
            fill=Cores.CARD_FUNDO, outline="",
        )
        # Texto central com total
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.create_text(
            cx, cy - 8, text=f"{total}",
            fill=Cores.TEXTO_PRIMARIO, font=Fontes.NUMERO_MEDIO,
        )
        self.create_text(
            cx, cy + 14, text="Total",
            fill=Cores.TEXTO_TERCIARIO, font=Fontes.MICRO,
        )

        # Legenda a direita
        x_legenda = x1 + 24
        y_legenda = y0 + 8
        for i, (rotulo, valor) in enumerate(self.dados):
            cor = self.PALETA[i % len(self.PALETA)]
            # Bolinha colorida
            self.create_oval(
                x_legenda, y_legenda + 5, x_legenda + 9, y_legenda + 14,
                fill=cor, outline="",
            )
            pct = valor / total * 100
            self.create_text(
                x_legenda + 16, y_legenda + 9, anchor="w",
                text=rotulo, fill=Cores.TEXTO_SECUNDARIO,
                font=Fontes.PEQUENO,
            )
            self.create_text(
                self.largura - 8, y_legenda + 9, anchor="e",
                text=f"{valor} ({pct:.1f}%)",
                fill=Cores.TEXTO_PRIMARIO, font=Fontes.PEQUENO_NEGRITO,
            )
            y_legenda += 24
