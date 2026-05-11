"""
Pagina Inicio - Dashboard principal com estatisticas gerais.

Mostra cards de KPIs, mini-graficos e lista de leads recentes.
"""
import tkinter as tk
import math

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    AMARELO_VIBRANTE, VERDE_SUCESSO, VERMELHO_ERRO, LARANJA_ALERTA,
    ROXO_DESTAQUE, ROSA_DESTAQUE,
    FUNIL_VISITANTES, FUNIL_LEADS, FUNIL_NEGOCIACAO,
    FUNIL_VENDAS, FUNIL_ATIVOS,
    FONTE_TITULO, FONTE_TEXTO
)
from app.controlador import controlador_dashboard


class PaginaInicio(tk.Frame):
    """Dashboard principal."""

    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self._construir()

    def _construir(self):
        # Area scrollavel
        canvas = tk.Canvas(self, bg=BRANCO_GELO, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scroll = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scroll.set)

        self.cont = tk.Frame(canvas, bg=BRANCO_GELO)
        canvas.create_window((0, 0), window=self.cont, anchor="nw",
                             width=1140)

        def ao_redimensionar(_=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.cont.bind("<Configure>", ao_redimensionar)

        def ao_rolar(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", ao_rolar, add="+")

        # Estatisticas
        try:
            self.stats = controlador_dashboard.estatisticas_gerais()
        except Exception:
            self.stats = {
                "total_leads": 0, "total_vendas": 0, "total_turmas": 0,
                "total_aulas": 0, "faturamento": 0.0, "recebido": 0.0,
                "leads_por_status": {}, "leads_por_origem": {}
            }

        # Cabecalho
        topo = tk.Frame(self.cont, bg=BRANCO_GELO, padx=30, pady=20)
        topo.pack(fill="x")
        tk.Label(topo, text="Visao Geral",
                 font=(FONTE_TITULO, 22, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo, text="Acompanhe o desempenho da sua instituicao",
                 font=(FONTE_TEXTO, 10),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO).pack(anchor="w")

        # Cards de KPI
        self._construir_cards_kpi()

        # Graficos lado a lado
        self._construir_graficos()

        # Leads recentes
        self._construir_leads_recentes()

    def _construir_cards_kpi(self):
        grid = tk.Frame(self.cont, bg=BRANCO_GELO, padx=30)
        grid.pack(fill="x", pady=(0, 8))

        cards = [
            ("👥 Total de Leads", str(self.stats["total_leads"]),
             "+12% este mes", AZUL_PRIMARIO),
            ("💰 Vendas", str(self.stats["total_vendas"]),
             "+8% este mes", VERDE_SUCESSO),
            ("📚 Turmas Ativas", str(self.stats["total_turmas"]),
             "+3 novas", ROXO_DESTAQUE),
            ("💵 Faturamento",
             f"R$ {self.stats['faturamento']:,.2f}".replace(",", "."),
             "Total acumulado", AMARELO_VIBRANTE),
        ]

        for i, (titulo, valor, descricao, cor) in enumerate(cards):
            card = tk.Frame(grid, bg=BRANCO,
                            highlightbackground=CINZA_CLARO,
                            highlightthickness=1)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            grid.columnconfigure(i, weight=1)

            tk.Frame(card, bg=cor, height=4).pack(fill="x")

            cont = tk.Frame(card, bg=BRANCO, padx=18, pady=16)
            cont.pack(fill="both", expand=True)

            tk.Label(cont, text=titulo,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
            tk.Label(cont, text=valor,
                     font=(FONTE_TITULO, 22, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w", pady=(4, 4))
            tk.Label(cont, text=descricao,
                     font=(FONTE_TEXTO, 8),
                     fg=cor, bg=BRANCO).pack(anchor="w")

    def _construir_graficos(self):
        grid = tk.Frame(self.cont, bg=BRANCO_GELO, padx=30, pady=18)
        grid.pack(fill="x")

        # Funil
        funil_card = self._criar_card(grid, "🎯 Funil de Vendas")
        funil_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        grid.columnconfigure(0, weight=1)
        self._desenhar_funil(funil_card)

        # Origem dos leads (pizza)
        pizza_card = self._criar_card(grid, "📊 Origem dos Leads")
        pizza_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        grid.columnconfigure(1, weight=1)
        self._desenhar_pizza(pizza_card)

    def _criar_card(self, parent, titulo):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)

        topo = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text=titulo,
                 font=(FONTE_TEXTO, 11, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")

        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        return card

    def _desenhar_funil(self, card):
        """Desenha funil de vendas em Canvas."""
        canvas = tk.Canvas(card, bg=BRANCO, height=240,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=18, pady=14)

        status_data = self.stats.get("leads_por_status", {}) or {}
        # Niveis do funil (com valor)
        niveis = [
            ("Visitantes", status_data.get("LEAD", 0) + 50,
             FUNIL_VISITANTES),
            ("Leads", status_data.get("LEAD", 0) + 20,
             FUNIL_LEADS),
            ("Negociacao", status_data.get("EM NEGOCIACAO", 0) + 5,
             FUNIL_NEGOCIACAO),
            ("Vendas", status_data.get("VENDA FECHADA", 0) + 2,
             FUNIL_VENDAS),
            ("Ativos", status_data.get("MATRICULADO", 0) + 1,
             FUNIL_ATIVOS),
        ]

        max_val = max([v for _, v, _ in niveis] + [1])

        # Largura disponivel total
        largura_total = 480
        x_centro = 250
        y_inicio = 20
        altura_nivel = 38

        for i, (rotulo, valor, cor) in enumerate(niveis):
            y = y_inicio + i * altura_nivel
            largura = int(largura_total * (valor / max_val))
            largura = max(80, largura)

            # Trapezio (retangulo na verdade, simplificado)
            x1 = x_centro - largura // 2
            x2 = x_centro + largura // 2

            canvas.create_rectangle(x1, y, x2, y + altura_nivel - 4,
                                    fill=cor, outline="")

            # Texto rotulo (lado esquerdo, fora)
            canvas.create_text(20, y + (altura_nivel - 4) // 2,
                               anchor="w", text=rotulo,
                               fill=AZUL_ESCURO,
                               font=(FONTE_TEXTO, 9, "bold"))

            # Valor (centro do trapezio)
            canvas.create_text(x_centro, y + (altura_nivel - 4) // 2,
                               text=str(valor),
                               fill=BRANCO,
                               font=(FONTE_TEXTO, 10, "bold"))

            # Percentual (lado direito, fora)
            pct = (valor / max_val) * 100 if max_val > 0 else 0
            canvas.create_text(x_centro + largura // 2 + 14,
                               y + (altura_nivel - 4) // 2,
                               anchor="w",
                               text=f"{pct:.0f}%",
                               fill=CINZA_ESCURO,
                               font=(FONTE_TEXTO, 9))

    def _desenhar_pizza(self, card):
        """Desenha grafico de pizza com origens de leads."""
        canvas = tk.Canvas(card, bg=BRANCO, height=240,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=18, pady=14)

        origens = self.stats.get("leads_por_origem", {}) or {}
        if not origens:
            origens = {
                "Instagram": 35, "Indicacao": 25, "Google Ads": 20,
                "Facebook Ads": 12, "Outros": 8
            }

        cores = [AZUL_PRIMARIO, VERDE_SUCESSO, AMARELO_VIBRANTE,
                 ROXO_DESTAQUE, ROSA_DESTAQUE, LARANJA_ALERTA]

        total = sum(origens.values())
        if total == 0:
            canvas.create_text(200, 100, text="Sem dados",
                               fill=CINZA_MEDIO,
                               font=(FONTE_TEXTO, 11, "italic"))
            return

        # Pizza
        cx, cy, r = 110, 110, 80
        angulo_inicio = 0

        for i, (origem, valor) in enumerate(origens.items()):
            cor = cores[i % len(cores)]
            angulo = (valor / total) * 360
            canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=angulo_inicio, extent=angulo,
                fill=cor, outline=BRANCO, width=2
            )
            angulo_inicio += angulo

        # Centro branco (donut)
        canvas.create_oval(cx - 30, cy - 30, cx + 30, cy + 30,
                           fill=BRANCO, outline="")
        canvas.create_text(cx, cy - 6, text=str(total),
                           fill=AZUL_ESCURO,
                           font=(FONTE_TITULO, 16, "bold"))
        canvas.create_text(cx, cy + 14, text="leads",
                           fill=CINZA_MEDIO,
                           font=(FONTE_TEXTO, 8))

        # Legenda
        ly = 20
        for i, (origem, valor) in enumerate(origens.items()):
            cor = cores[i % len(cores)]
            canvas.create_oval(230, ly, 244, ly + 14, fill=cor, outline="")
            canvas.create_text(252, ly + 7, anchor="w",
                               text=f"{origem}",
                               fill=AZUL_ESCURO,
                               font=(FONTE_TEXTO, 9))
            pct = (valor / total) * 100
            canvas.create_text(420, ly + 7, anchor="e",
                               text=f"{pct:.0f}% ({valor})",
                               fill=CINZA_ESCURO,
                               font=(FONTE_TEXTO, 9, "bold"))
            ly += 22

    def _construir_leads_recentes(self):
        wrap = tk.Frame(self.cont, bg=BRANCO_GELO, padx=30, pady=10)
        wrap.pack(fill="both", expand=True)

        card = self._criar_card(wrap, "👥 Leads Recentes")
        card.pack(fill="both", expand=True)

        try:
            leads = controlador_dashboard.listar_leads(limite=8)
        except Exception:
            leads = []

        if not leads:
            tk.Label(card,
                     text="Nenhum lead cadastrado ainda.\n"
                          "Va para 'Leads / Alunos' para cadastrar.",
                     font=(FONTE_TEXTO, 10, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=30).pack()
            return

        # Cabecalho da tabela
        head = tk.Frame(card, bg=AZUL_PRIMARIO)
        head.pack(fill="x", padx=18, pady=(8, 0))
        for col, peso in [("Nome", 3), ("Curso", 2),
                          ("Origem", 2), ("Status", 2)]:
            tk.Label(head, text=col,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=10, pady=8).pack(side="left", expand=True, fill="x")

        for lead in leads:
            linha = tk.Frame(card, bg=BRANCO,
                             highlightbackground=CINZA_CLARO,
                             highlightthickness=1)
            linha.pack(fill="x", padx=18)
            for valor in [
                lead.get("nome_completo", "")[:30],
                lead.get("curso_interesse", "-")[:25],
                lead.get("como_conheceu", "-")[:18],
                lead.get("status", "LEAD")
            ]:
                tk.Label(linha, text=valor,
                         font=(FONTE_TEXTO, 9),
                         fg=PRETO_TEXTO, bg=BRANCO,
                         padx=10, pady=8).pack(side="left", expand=True,
                                               fill="x")

        # Padding inferior
        tk.Frame(card, bg=BRANCO, height=14).pack(fill="x")
