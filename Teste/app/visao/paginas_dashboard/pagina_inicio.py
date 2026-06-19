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
    FONTE_TITULO, FONTE_TEXTO,
    CORES_GRAFICOS as cores
)
from app.controlador import controlador_dashboard
from componentes.card import Card


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
        window_id = canvas.create_window((0, 0), window=self.cont, anchor="n",
                             width=1140)

        def ao_redimensionar(_=None):
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=(0, 0, 0, bbox[3]))
        self.cont.bind("<Configure>", ao_redimensionar)

        def ao_redimensionar_canvas(e):
            nova_largura = min(1140, e.width - 40)
            if nova_largura < 300:
                nova_largura = 300
            canvas.itemconfig(window_id, width=nova_largura)
            canvas.coords(window_id, e.width // 2, 0)
        canvas.bind("<Configure>", ao_redimensionar_canvas, add="+")

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
            ("\U0001f465 Total de Leads", str(self.stats["total_leads"]),
             "Leads cadastrados", AZUL_PRIMARIO),
            ("\U0001f4b0 Vendas", str(self.stats["total_vendas"]),
             "Vendas realizadas", VERDE_SUCESSO),
            ("\U0001f4da Turmas Ativas", str(self.stats["total_turmas"]),
             "Turmas abertas", ROXO_DESTAQUE),
            ("\U0001f4b5 Faturamento",
             f"R$ {self.stats['faturamento']:,.2f}".replace(",", "."),
             "Total acumulado", AMARELO_VIBRANTE),
        ]

        for i, (titulo, valor, descricao, cor) in enumerate(cards):
            card = Card(grid, padding=0, raio=12)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            grid.columnconfigure(i, weight=1)

            tk.Frame(card.interno, bg=cor, height=4).pack(fill="x")

            cont = tk.Frame(card.interno, bg=BRANCO, padx=18, pady=16)
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
        self._desenhar_funil(funil_card.interno)

        # Origem dos leads (pizza)
        pizza_card = self._criar_card(grid, "📊 Origem dos Leads")
        pizza_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        grid.columnconfigure(1, weight=1)
        self._desenhar_pizza(pizza_card.interno)

    def _criar_card(self, parent, titulo):
        card = Card(parent, titulo=titulo, padding=14, raio=12)
        return card

    def _desenhar_funil(self, card):
        """Desenha funil de vendas em Canvas com animacao de entrada."""
        canvas = tk.Canvas(card, bg=BRANCO, height=240,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=18, pady=14)

        status_data = self.stats.get("leads_por_status", {}) or {}

        niveis = [
            ("Visitantes", status_data.get("LEAD", 0), FUNIL_VISITANTES),
            ("Leads", status_data.get("LEAD", 0), FUNIL_LEADS),
            ("Negociacao", status_data.get("EM NEGOCIACAO", 0), FUNIL_NEGOCIACAO),
            ("Vendas", status_data.get("VENDA FECHADA", 0), FUNIL_VENDAS),
            ("Ativos", status_data.get("MATRICULADO", 0), FUNIL_ATIVOS),
        ]

        total_geral = sum(v for _, v, _ in niveis)

        if total_geral == 0:
            canvas.create_text(
                240, 120,
                text="Sem dados no funil ainda.\n"
                     "Adicione leads para visualizar.",
                fill=CINZA_MEDIO,
                font=(FONTE_TEXTO, 11, "italic"),
                justify="center"
            )
            return

        max_val = max([v for _, v, _ in niveis] + [1])

        largura_total = 480
        x_centro = 250
        y_inicio = 20
        altura_nivel = 38

        bars = []
        for i, (rotulo, valor, cor) in enumerate(niveis):
            y = y_inicio + i * altura_nivel
            largura_alvo = int(largura_total * (valor / max_val)) if max_val > 0 else 80
            largura_alvo = max(80, largura_alvo)

            rect_id = canvas.create_rectangle(x_centro - 5, y, x_centro + 5, y + altura_nivel - 4,
                                              fill=cor, outline="")

            canvas.create_text(20, y + (altura_nivel - 4) // 2,
                               anchor="w", text=rotulo,
                               fill=AZUL_ESCURO,
                               font=(FONTE_TEXTO, 9, "bold"))

            val_id = canvas.create_text(x_centro, y + (altura_nivel - 4) // 2,
                                        text="", fill=BRANCO,
                                        font=(FONTE_TEXTO, 10, "bold"))

            pct = (valor / max_val) * 100 if max_val > 0 else 0
            pct_id = canvas.create_text(x_centro + largura_alvo // 2 + 14,
                                        y + (altura_nivel - 4) // 2,
                                        anchor="w", text="",
                                        fill=CINZA_ESCURO, font=(FONTE_TEXTO, 9))

            bars.append((rect_id, largura_alvo, val_id, str(valor), pct_id, f"{pct:.0f}%", y, cor))

        def _configurar_hover_funil():
            def ao_mover(event):
                item = canvas.find_withtag("current")
                if item and item[0] in [b[0] for b in bars]:
                    idx = [b[0] for b in bars].index(item[0])
                    rect_id, max_w, val_id, val_str, pct_id, pct_str, y, cor = bars[idx]
                    for b in bars:
                        canvas.itemconfigure(b[0], width=0, outline="")
                    canvas.itemconfigure(rect_id, width=1.5, outline=AZUL_ESCURO)
                else:
                    for b in bars:
                        canvas.itemconfigure(b[0], width=0, outline="")
            canvas.bind("<Motion>", ao_mover)

        def animar_funil(passo=1):
            if passo > 20:
                _configurar_hover_funil()
                return
            prog = passo / 20.0
            for rect_id, max_w, val_id, val_str, pct_id, pct_str, y, cor in bars:
                w_atual = int(max_w * prog)
                w_atual = max(10, w_atual)
                x1 = x_centro - w_atual // 2
                x2 = x_centro + w_atual // 2
                canvas.coords(rect_id, x1, y, x2, y + altura_nivel - 4)
                if passo == 20:
                    canvas.itemconfigure(val_id, text=val_str)
                    canvas.itemconfigure(pct_id, text=pct_str, x=x_centro + max_w // 2 + 14)
            card.after(15, lambda: animar_funil(passo + 1))

        animar_funil()

    def _desenhar_pizza(self, card):
        """Desenha grafico de pizza/donut interativo e animado."""
        canvas = tk.Canvas(card, bg=BRANCO, height=240,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=18, pady=14)

        origens = self.stats.get("leads_por_origem", {}) or {}

        total = sum(origens.values()) if origens else 0
        if total == 0:
            canvas.create_text(200, 100,
                               text="Sem dados de origem ainda.\n"
                                    "Adicione leads com origem definida.",
                               fill=CINZA_MEDIO,
                               font=(FONTE_TEXTO, 10, "italic"),
                               justify="center")
            return

        cx, cy, r = 110, 110, 80
        angulo_inicio = 0

        arcos_info = []
        for i, (origem, valor) in enumerate(origens.items()):
            cor = cores[i % len(cores)]
            ext = (valor / total) * 360
            arcos_info.append({
                "start": angulo_inicio,
                "target_extent": ext,
                "color": cor,
                "origem": origem,
                "valor": valor
            })
            angulo_inicio += ext

        arcos_widgets = []
        for info in arcos_info:
            arc_id = canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=info["start"], extent=0,
                fill=info["color"], outline=BRANCO, width=2
            )
            arcos_widgets.append((arc_id, info))

        # Centro do Donut
        canvas.create_oval(cx - 40, cy - 40, cx + 40, cy + 40, fill=BRANCO, outline="")
        total_text_id = canvas.create_text(cx, cy - 6, text=str(total),
                                           fill=AZUL_ESCURO, font=(FONTE_TITULO, 16, "bold"))
        label_text_id = canvas.create_text(cx, cy + 14, text="leads",
                                           fill=CINZA_MEDIO, font=(FONTE_TEXTO, 8))

        def _configurar_hover():
            def ao_mover(event):
                item = canvas.find_withtag("current")
                if item and item[0] in [aw[0] for aw in arcos_widgets]:
                    idx = [aw[0] for aw in arcos_widgets].index(item[0])
                    info = arcos_widgets[idx][1]
                    for aw in arcos_widgets:
                        canvas.itemconfigure(aw[0], width=2, outline=BRANCO)
                    canvas.itemconfigure(item[0], width=3, outline=AZUL_ESCURO)
                    pct = (info["valor"] / total) * 100
                    canvas.itemconfigure(total_text_id, text=f"{pct:.0f}%", font=(FONTE_TITULO, 14, "bold"))
                    canvas.itemconfigure(label_text_id, text=f"{info['origem']}\n({info['valor']})", font=(FONTE_TEXTO, 7, "bold"))
                else:
                    for aw in arcos_widgets:
                        canvas.itemconfigure(aw[0], width=2, outline=BRANCO)
                    canvas.itemconfigure(total_text_id, text=str(total), font=(FONTE_TITULO, 16, "bold"))
                    canvas.itemconfigure(label_text_id, text="leads", font=(FONTE_TEXTO, 8))
            canvas.bind("<Motion>", ao_mover)

        def animar_pizza(passo=1):
            if passo > 20:
                _configurar_hover()
                return
            prog = passo / 20.0
            for arc_id, info in arcos_widgets:
                canvas.itemconfigure(arc_id, extent=info["target_extent"] * prog)
            card.after(15, lambda: animar_pizza(passo + 1))

        animar_pizza()

        # Legenda detalhada
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
            tk.Label(card.interno,
                     text="Nenhum lead cadastrado ainda.\n"
                          "Va para 'Leads / Alunos' para cadastrar.",
                     font=(FONTE_TEXTO, 10, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=30).pack()
            return

        # Cabecalho da tabela
        head = tk.Frame(card.interno, bg=AZUL_PRIMARIO)
        head.pack(fill="x", padx=18, pady=(8, 0))
        for col, peso in [("Nome", 3), ("Curso", 2),
                          ("Origem", 2), ("Status", 2)]:
            tk.Label(head, text=col,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=10, pady=8).pack(side="left", expand=True, fill="x")

        for lead in leads:
            linha = tk.Frame(card.interno, bg=BRANCO)
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
        tk.Frame(card.interno, bg=BRANCO, height=14).pack(fill="x")
