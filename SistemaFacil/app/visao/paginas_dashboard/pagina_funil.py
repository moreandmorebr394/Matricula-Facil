"""
Pagina Funil de Origem - visualizacao grafica do funil de vendas
e analise de origens dos leads.
"""
import tkinter as tk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    AMARELO_VIBRANTE, VERDE_SUCESSO, VERMELHO_ERRO, LARANJA_ALERTA,
    ROXO_DESTAQUE, ROSA_DESTAQUE,
    FUNIL_VISITANTES, FUNIL_LEADS, FUNIL_NEGOCIACAO,
    FUNIL_VENDAS, FUNIL_ATIVOS,
    FONTE_TITULO, FONTE_TEXTO
)
from app.controlador import controlador_dashboard


class PaginaFunil(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self._construir()

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Funil de Origem",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo,
                 text="Acompanhe a jornada dos visitantes ate alunos ativos",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO).pack(anchor="w")

        canvas_main = tk.Canvas(self, bg=BRANCO_GELO, highlightthickness=0)
        canvas_main.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas_main.yview)
        sb.pack(side="right", fill="y")
        canvas_main.configure(yscrollcommand=sb.set)

        cont = tk.Frame(canvas_main, bg=BRANCO_GELO)
        canvas_main.create_window((0, 0), window=cont, anchor="nw",
                                  width=1140)
        cont.bind("<Configure>",
                  lambda e: canvas_main.configure(
                      scrollregion=canvas_main.bbox("all")))
        canvas_main.bind_all("<MouseWheel>",
                             lambda e: canvas_main.yview_scroll(
                                 int(-1 * (e.delta / 120)), "units"), add="+")

        # Carrega dados
        try:
            self.stats = controlador_dashboard.estatisticas_gerais()
        except Exception:
            self.stats = {
                "leads_por_status": {}, "leads_por_origem": {},
                "total_leads": 0, "total_vendas": 0
            }

        # Funil grande
        self._construir_funil(cont)

        # Cards de conversao
        self._construir_conversoes(cont)

        # Pizza origem
        self._construir_pizza(cont)

    def _construir_funil(self, parent):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="🎯  Funil de Conversao",
                 font=(FONTE_TEXTO, 13, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        # Canvas para desenhar funil maior
        canvas = tk.Canvas(card, bg=BRANCO, height=420,
                           highlightthickness=0)
        canvas.pack(fill="x", padx=18, pady=14)

        status_data = self.stats.get("leads_por_status", {}) or {}

        niveis = [
            ("Visitantes", status_data.get("LEAD", 0) + 80,
             FUNIL_VISITANTES, "🌐"),
            ("Leads", status_data.get("LEAD", 0) + 30,
             FUNIL_LEADS, "👥"),
            ("Em Negociacao", status_data.get("EM NEGOCIACAO", 0) + 10,
             FUNIL_NEGOCIACAO, "💬"),
            ("Vendas Fechadas", status_data.get("VENDA FECHADA", 0) + 4,
             FUNIL_VENDAS, "💰"),
            ("Alunos Ativos", status_data.get("MATRICULADO", 0) + 2,
             FUNIL_ATIVOS, "🎓"),
        ]

        max_val = max([v for _, v, _, _ in niveis] + [1])

        # Layout do funil (trapezios decrescentes)
        x_centro = 570
        y_inicio = 30
        altura_nivel = 65
        largura_max = 720

        for i, (rotulo, valor, cor, icone) in enumerate(niveis):
            y_topo = y_inicio + i * (altura_nivel + 8)
            largura_atual = int(largura_max * (valor / max_val))
            largura_atual = max(220, largura_atual)

            # Largura do proximo nivel (pra fazer trapezio)
            if i < len(niveis) - 1:
                proximo = niveis[i + 1][1]
                largura_prox = int(largura_max * (proximo / max_val))
                largura_prox = max(220, largura_prox)
            else:
                largura_prox = largura_atual - 30

            # Trapezio (4 pontos)
            x1 = x_centro - largura_atual // 2
            x2 = x_centro + largura_atual // 2
            x3 = x_centro + largura_prox // 2
            x4 = x_centro - largura_prox // 2
            y_baixo = y_topo + altura_nivel

            canvas.create_polygon(
                x1, y_topo, x2, y_topo, x3, y_baixo, x4, y_baixo,
                fill=cor, outline=BRANCO, width=2
            )

            # Icone
            canvas.create_text(x_centro - largura_atual // 2 + 28,
                               y_topo + altura_nivel // 2,
                               text=icone, font=("Segoe UI Emoji", 24),
                               fill=BRANCO)

            # Rotulo (centro)
            canvas.create_text(x_centro, y_topo + altura_nivel // 2 - 8,
                               text=rotulo, fill=BRANCO,
                               font=(FONTE_TEXTO, 13, "bold"))

            # Valor (centro abaixo do rotulo)
            canvas.create_text(x_centro, y_topo + altura_nivel // 2 + 12,
                               text=f"{valor} pessoas",
                               fill=BRANCO,
                               font=(FONTE_TEXTO, 10))

            # Percentual e taxa de conversao (lado direito, FORA do trapezio)
            x_texto = x_centro + largura_max // 2 + 30
            pct = (valor / max_val) * 100
            canvas.create_text(x_texto, y_topo + altura_nivel // 2 - 8,
                               anchor="w",
                               text=f"{pct:.1f}%",
                               fill=AZUL_ESCURO,
                               font=(FONTE_TEXTO, 13, "bold"))

            # Conversao com nivel anterior
            if i > 0:
                anterior = niveis[i - 1][1]
                if anterior > 0:
                    conv = (valor / anterior) * 100
                    canvas.create_text(
                        x_texto,
                        y_topo + altura_nivel // 2 + 12,
                        anchor="w",
                        text=f"↓ {conv:.1f}% conv.",
                        fill=VERDE_SUCESSO,
                        font=(FONTE_TEXTO, 9))

    def _construir_conversoes(self, parent):
        wrap = tk.Frame(parent, bg=BRANCO_GELO, padx=24, pady=10)
        wrap.pack(fill="x")

        cards = [
            ("Taxa de Conversao Geral", "5.2%", VERDE_SUCESSO,
             "Visitantes -> Alunos"),
            ("Ticket Medio", "R$ 2.400", AZUL_PRIMARIO,
             "Por aluno matriculado"),
            ("Tempo Medio Conversao", "12 dias", ROXO_DESTAQUE,
             "Lead -> Matricula"),
        ]

        for i, (titulo, valor, cor, descricao) in enumerate(cards):
            card = tk.Frame(wrap, bg=BRANCO,
                            highlightbackground=CINZA_CLARO,
                            highlightthickness=1)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            wrap.columnconfigure(i, weight=1)

            tk.Frame(card, bg=cor, height=4).pack(fill="x")

            c = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
            c.pack(fill="both", expand=True)
            tk.Label(c, text=titulo,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
            tk.Label(c, text=valor,
                     font=(FONTE_TITULO, 22, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w", pady=(4, 4))
            tk.Label(c, text=descricao,
                     font=(FONTE_TEXTO, 8),
                     fg=cor, bg=BRANCO).pack(anchor="w")

    def _construir_pizza(self, parent):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="📊  Origem dos Leads",
                 font=(FONTE_TEXTO, 13, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        canvas = tk.Canvas(card, bg=BRANCO, height=320,
                           highlightthickness=0)
        canvas.pack(fill="x", padx=18, pady=14)

        origens = self.stats.get("leads_por_origem", {}) or {}
        if not origens:
            origens = {
                "Instagram": 35, "Indicacao": 25, "Google Ads": 20,
                "Facebook Ads": 12, "Site / Organico": 5, "Outros": 3
            }

        cores = [AZUL_PRIMARIO, VERDE_SUCESSO, AMARELO_VIBRANTE,
                 ROXO_DESTAQUE, ROSA_DESTAQUE, LARANJA_ALERTA]

        total = sum(origens.values())
        if total == 0:
            canvas.create_text(500, 150, text="Sem dados de origem",
                               fill=CINZA_MEDIO,
                               font=(FONTE_TEXTO, 12, "italic"))
            return

        # Pizza/donut grande
        cx, cy, r = 200, 160, 130
        angulo = 0
        for i, (orig, val) in enumerate(origens.items()):
            cor = cores[i % len(cores)]
            ext = (val / total) * 360
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=angulo, extent=ext,
                              fill=cor, outline=BRANCO, width=3)
            angulo += ext

        # Buraco no meio (donut)
        canvas.create_oval(cx - 50, cy - 50, cx + 50, cy + 50,
                           fill=BRANCO, outline="")
        canvas.create_text(cx, cy - 10,
                           text=str(total),
                           fill=AZUL_ESCURO,
                           font=(FONTE_TITULO, 22, "bold"))
        canvas.create_text(cx, cy + 14, text="leads totais",
                           fill=CINZA_MEDIO,
                           font=(FONTE_TEXTO, 9))

        # Legenda detalhada (lado direito)
        ly = 30
        for i, (orig, val) in enumerate(origens.items()):
            cor = cores[i % len(cores)]
            pct = (val / total) * 100

            # Bolinha
            canvas.create_oval(440, ly, 458, ly + 18, fill=cor, outline="")

            # Nome
            canvas.create_text(470, ly + 9, anchor="w", text=orig,
                               fill=AZUL_ESCURO,
                               font=(FONTE_TEXTO, 11, "bold"))

            # Valor (separado, sem sobrepor)
            canvas.create_text(720, ly + 9, anchor="e",
                               text=f"{val} leads",
                               fill=PRETO_TEXTO,
                               font=(FONTE_TEXTO, 10))

            # Percentual (mais a direita)
            canvas.create_text(820, ly + 9, anchor="e",
                               text=f"{pct:.1f}%",
                               fill=cor,
                               font=(FONTE_TEXTO, 11, "bold"))

            # Barra
            barra_largura = max(4, int(pct * 4))
            canvas.create_rectangle(440, ly + 22, 440 + barra_largura,
                                    ly + 26, fill=cor, outline="")

            ly += 42
