"""Tela do Funil de Origem - analise detalhada."""
import tkinter as tk
from typing import Callable

from componentes.botao import BotaoSecundario
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from utilitarios.graficos import GraficoFunil, GraficoPizza


class TelaFunilOrigem(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)

        # cabecalho com filtros
        topo = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        topo.pack(fill="x", pady=(0, 16))
        bloco_titulo = tk.Frame(topo, bg=Cores.FUNDO_PRINCIPAL)
        bloco_titulo.pack(side="left")
        tk.Label(bloco_titulo, text="Analise de Funil",
                 bg=Cores.FUNDO_PRINCIPAL, fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO,
                 anchor="w").pack(anchor="w")
        tk.Label(bloco_titulo,
                 text="Acompanhe a conversao em cada etapa do processo.",
                 bg=Cores.FUNDO_PRINCIPAL, fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO,
                 anchor="w").pack(anchor="w")

        for periodo in ["Semana", "Mes", "Trimestre", "Ano"]:
            BotaoSecundario(topo, texto=periodo,
                            comando=lambda p=periodo:
                            self.mostrar_notificacao(
                                f"Periodo '{p}' aplicado.", "INFO"),
                            largura=88).pack(side="right", padx=4)

        # 2 colunas (em frame separado para nao misturar pack+grid)
        grid = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=2, uniform="fu")
        grid.grid_columnconfigure(1, weight=1, uniform="fu")
        grid.grid_rowconfigure(0, weight=1)

        # ---- Funil grande ----
        funil_card = CardComCabecalho(grid,
                                      titulo="Funil Geral de Vendas",
                                      icone="🔻")
        funil_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        cf = funil_card.conteudo()
        cf.configure(bg=Cores.CARD_FUNDO)
        dados_funil = list(self.banco.funil_origem().items())
        graf = GraficoFunil(cf, dados_funil, largura=560, altura=420)
        graf.pack(pady=10)

        # ---- Pizza + tabela origens ----
        direita = tk.Frame(grid, bg=Cores.FUNDO_PRINCIPAL)
        direita.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        direita.grid_columnconfigure(0, weight=1)

        pizza_card = CardComCabecalho(direita,
                                      titulo="Origem dos Leads",
                                      icone="🍩")
        pizza_card.pack(fill="x", pady=(0, 8))
        cp = pizza_card.conteudo()
        cp.configure(bg=Cores.CARD_FUNDO)
        dados_origem = self.banco.origem_dos_leads()
        pizza = GraficoPizza(cp, dados_origem, largura=320, altura=240)
        pizza.pack(pady=8)

        # ---- Tabela detalhada ----
        tab_card = CardComCabecalho(direita,
                                    titulo="Detalhamento por Etapa",
                                    icone="📊")
        tab_card.pack(fill="both", expand=True, pady=(8, 0))
        ct = tab_card.conteudo()
        ct.configure(bg=Cores.CARD_FUNDO)

        etapas = list(self.banco.funil_origem().items())
        for i, (nome, qtd) in enumerate(etapas):
            cor = self._cor_etapa(i)
            linha = tk.Frame(ct, bg=Cores.CARD_FUNDO)
            linha.pack(fill="x", pady=4)

            ponto = tk.Canvas(linha, width=12, height=12,
                              bg=Cores.CARD_FUNDO,
                              highlightthickness=0)
            ponto.create_oval(2, 2, 12, 12, fill=cor, outline="")
            ponto.pack(side="left", padx=(0, 8))
            tk.Label(linha, text=nome, bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO,
                     anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(linha, text=f"{qtd:,}".replace(",", "."),
                     bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO_NEGRITO,
                     anchor="e").pack(side="right")

            if i < len(etapas) - 1:
                proximo = etapas[i + 1][1]
                if qtd > 0:
                    pct = proximo / qtd * 100
                    cap = tk.Frame(ct, bg=Cores.CARD_FUNDO)
                    cap.pack(fill="x", padx=20)
                    tk.Label(cap,
                             text=f"↓ Conversao: {pct:.1f}%",
                             bg=Cores.CARD_FUNDO,
                             fg=Cores.TEXTO_TERCIARIO,
                             font=Fontes.MICRO).pack(anchor="w")

    def _cor_etapa(self, idx):
        cores = [
            Cores.FUNIL_VISITANTES, Cores.FUNIL_LEADS,
            Cores.FUNIL_NEGOCIACOES, Cores.FUNIL_VENDAS,
            Cores.FUNIL_ALUNOS,
        ]
        return cores[idx % len(cores)]
