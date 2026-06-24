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
    FONTE_TITULO, FONTE_TEXTO,
    CORES_GRAFICOS as cores
)
from app.controlador import controlador_dashboard
from componentes.card import Card


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
        window_id = canvas_main.create_window((0, 0), window=cont, anchor="n",
                                  width=1140)

        def ar(_=None):
            bbox = canvas_main.bbox("all")
            if bbox:
                canvas_main.configure(scrollregion=(0, 0, 0, bbox[3]))
        cont.bind("<Configure>", ar)

        def ao_redimensionar_canvas(e):
            nova_largura = min(1140, e.width - 40)
            if nova_largura < 300:
                nova_largura = 300
            canvas_main.itemconfig(window_id, width=nova_largura)
            canvas_main.coords(window_id, e.width // 2, 0)
        canvas_main.bind("<Configure>", ao_redimensionar_canvas, add="+")
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
        card = Card(parent, titulo="🎯  Funil de Conversao", padding=14, raio=12)
        card.pack(fill="x", padx=24, pady=10)

        # Canvas para desenhar funil maior
        canvas = tk.Canvas(card.interno, bg=BRANCO, height=420,
                           highlightthickness=0)
        canvas.pack(fill="x", padx=18, pady=14)

        status_data = self.stats.get("leads_por_status", {}) or {}

        niveis = [
            ("Visitantes", status_data.get("LEAD", 0), FUNIL_VISITANTES, "\U0001f310"),
            ("Leads", status_data.get("LEAD", 0), FUNIL_LEADS, "\U0001f465"),
            ("Em Negociacao", status_data.get("EM NEGOCIACAO", 0), FUNIL_NEGOCIACAO, "\U0001f4ac"),
            ("Vendas Fechadas", status_data.get("VENDA FECHADA", 0), FUNIL_VENDAS, "\U0001f4b0"),
            ("Alunos Ativos", status_data.get("MATRICULADO", 0), FUNIL_ATIVOS, "\U0001f393"),
        ]

        max_val = max([v for _, v, _, _ in niveis] + [1])

        total_geral = sum(v for _, v, _, _ in niveis)
        if total_geral == 0:
            canvas.create_text(
                570, 210,
                text="Sem dados no funil ainda.\n"
                     "Adicione leads para visualizar o funil.",
                fill=CINZA_MEDIO,
                font=(FONTE_TEXTO, 14, "italic"),
                justify="center"
            )
            return

        x_centro = 570
        y_inicio = 30
        altura_nivel = 65
        largura_max = 720

        polygons = []
        for i, (rotulo, valor, cor, icone) in enumerate(niveis):
            y_topo = y_inicio + i * (altura_nivel + 8)
            largura_atual = int(largura_max * (valor / max_val))
            largura_atual = max(220, largura_atual)

            if i < len(niveis) - 1:
                proximo = niveis[i + 1][1]
                largura_prox = int(largura_max * (proximo / max_val))
                largura_prox = max(220, largura_prox)
            else:
                largura_prox = largura_atual - 30

            y_baixo = y_topo + altura_nivel

            # Cria poligono com largura inicial 0
            poly_id = canvas.create_polygon(
                x_centro, y_topo, x_centro, y_topo, x_centro, y_baixo, x_centro, y_baixo,
                fill=cor, outline=BRANCO, width=2
            )

            ico_id = canvas.create_text(x_centro, y_topo + altura_nivel // 2,
                                        text=icone, font=("Segoe UI Emoji", 24), fill=BRANCO)

            lbl_id = canvas.create_text(x_centro, y_topo + altura_nivel // 2 - 8,
                                        text="", fill=BRANCO, font=(FONTE_TEXTO, 13, "bold"))

            val_id = canvas.create_text(x_centro, y_topo + altura_nivel // 2 + 12,
                                        text="", fill=BRANCO, font=(FONTE_TEXTO, 10))

            x_texto = x_centro + largura_max // 2 + 30
            pct = (valor / max_val) * 100
            pct_id = canvas.create_text(x_texto, y_topo + altura_nivel // 2 - 8,
                                        anchor="w", text="", fill=AZUL_ESCURO, font=(FONTE_TEXTO, 13, "bold"))

            txt_conv_id = None
            if i > 0:
                anterior = niveis[i - 1][1]
                if anterior > 0:
                    txt_conv_id = canvas.create_text(
                        x_texto, y_topo + altura_nivel // 2 + 12,
                        anchor="w", text="", fill=VERDE_SUCESSO, font=(FONTE_TEXTO, 9))

            polygons.append({
                "id": poly_id, "ico_id": ico_id, "lbl_id": lbl_id, "val_id": val_id,
                "pct_id": pct_id, "conv_id": txt_conv_id, "w_atual": largura_atual, "w_prox": largura_prox,
                "y_topo": y_topo, "y_baixo": y_baixo, "cor": cor, "rotulo": rotulo,
                "valor_str": f"{valor} pessoas", "pct_str": f"{pct:.1f}%",
                "conv_str": f"↓ {((valor/niveis[i-1][1]*100) if niveis[i-1][1] > 0 else 0):.1f}% conv." if i > 0 else ""
            })

        def _configurar_hover_funil():
            def ao_mover(event):
                item = canvas.find_withtag("current")
                if item and item[0] in [p["id"] for p in polygons]:
                    idx = [p["id"] for p in polygons].index(item[0])
                    poly = polygons[idx]
                    for p in polygons:
                        canvas.itemconfigure(p["id"], width=2, outline=BRANCO)
                    canvas.itemconfigure(poly["id"], width=3.5, outline=AZUL_ESCURO)
                else:
                    for p in polygons:
                        canvas.itemconfigure(p["id"], width=2, outline=BRANCO)
            canvas.bind("<Motion>", ao_mover)

        def animar_niveis(passo=1):
            if passo > 20:
                _configurar_hover_funil()
                return
            prog = passo / 20.0
            for p in polygons:
                w_c = int(p["w_atual"] * prog)
                w_p = int(p["w_prox"] * prog)
                x1 = x_centro - w_c // 2
                x2 = x_centro + w_c // 2
                x3 = x_centro + w_p // 2
                x4 = x_centro - w_p // 2

                canvas.coords(p["id"], x1, p["y_topo"], x2, p["y_topo"], x3, p["y_baixo"], x4, p["y_baixo"])
                canvas.coords(p["ico_id"], x_centro - w_c // 2 + 28, p["y_topo"] + altura_nivel // 2)

                if passo == 20:
                    canvas.itemconfigure(p["lbl_id"], text=p["rotulo"])
                    canvas.itemconfigure(p["val_id"], text=p["valor_str"])
                    canvas.itemconfigure(p["pct_id"], text=p["pct_str"])
                    if p["conv_id"] and p["conv_str"]:
                        canvas.itemconfigure(p["conv_id"], text=p["conv_str"])
            card.after(15, lambda: animar_niveis(passo + 1))

        animar_niveis()

    def _construir_conversoes(self, parent):
        wrap = tk.Frame(parent, bg=BRANCO_GELO, padx=24, pady=10)
        wrap.pack(fill="x")

        # Calcula dados reais
        status_data = self.stats.get("leads_por_status", {}) or {}
        total_leads = self.stats.get("total_leads", 0)
        total_vendas = self.stats.get("total_vendas", 0)
        faturamento = self.stats.get("faturamento", 0.0)

        # Taxa de conversao real
        if total_leads > 0:
            taxa = (total_vendas / total_leads) * 100
            taxa_str = f"{taxa:.1f}%"
        else:
            taxa_str = "0%"

        # Ticket medio real
        if total_vendas > 0:
            ticket = faturamento / total_vendas
            ticket_str = f"R$ {ticket:,.2f}".replace(",", ".")
        else:
            ticket_str = "R$ 0,00"

        cards = [
            ("Taxa de Conversao Geral", taxa_str, VERDE_SUCESSO,
             "Leads -> Vendas"),
            ("Ticket Medio", ticket_str, AZUL_PRIMARIO,
             "Por venda realizada"),
            ("Total de Leads", str(total_leads), ROXO_DESTAQUE,
             "Cadastrados no sistema"),
        ]

        for i, (titulo, valor, cor, descricao) in enumerate(cards):
            card = Card(wrap, padding=0, raio=12)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            wrap.columnconfigure(i, weight=1)

            tk.Frame(card.interno, bg=cor, height=4).pack(fill="x")

            c = tk.Frame(card.interno, bg=BRANCO, padx=18, pady=14)
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
        card = Card(parent, titulo="📊  Origem dos Leads", padding=14, raio=12)
        card.pack(fill="x", padx=24, pady=10)

        canvas = tk.Canvas(card.interno, bg=BRANCO, height=320,
                           highlightthickness=0)
        canvas.pack(fill="x", padx=18, pady=14)

        origens = self.stats.get("leads_por_origem", {}) or {}

        # Sem fallback - exibe mensagem se nao ha dados reais
        total = sum(origens.values()) if origens else 0
        if total == 0:
            canvas.create_text(500, 150,
                               text="Sem dados de origem ainda.\n"
                                    "Adicione leads com origem para ver o grafico.",
                               fill=CINZA_MEDIO,
                               font=(FONTE_TEXTO, 12, "italic"),
                               justify="center")
            return

        # Pizza/donut grande
        cx, cy, r = 200, 160, 130
        angulo_inicio = 0
        arcos_info = []
        for i, (orig, val) in enumerate(origens.items()):
            cor = cores[i % len(cores)]
            ext = (val / total) * 360
            arcos_info.append({
                "start": angulo_inicio,
                "target_extent": ext,
                "color": cor,
                "origem": orig,
                "valor": val
            })
            angulo_inicio += ext

        arcos_widgets = []
        for info in arcos_info:
            arc_id = canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=info["start"], extent=0,
                fill=info["color"], outline=BRANCO, width=3
            )
            arcos_widgets.append((arc_id, info))

        # Buraco no meio (donut)
        canvas.create_oval(cx - 65, cy - 65, cx + 65, cy + 65,
                           fill=BRANCO, outline="")
        total_text_id = canvas.create_text(cx, cy - 10,
                                           text=str(total),
                                           fill=AZUL_ESCURO,
                                           font=(FONTE_TITULO, 22, "bold"))
        label_text_id = canvas.create_text(cx, cy + 16, text="leads totais",
                                           fill=CINZA_MEDIO,
                                           font=(FONTE_TEXTO, 9))

        # Legenda detalhada (lado direito)
        ly = 30
        legenda_widgets = []
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
            barra_id = canvas.create_rectangle(440, ly + 22, 440,
                                               ly + 26, fill=cor, outline="")
            barra_largura_alvo = max(4, int(pct * 4))
            legenda_widgets.append((barra_id, barra_largura_alvo, ly + 22))

            ly += 42

        def _configurar_hover():
            def ao_mover(event):
                item = canvas.find_withtag("current")
                if item and item[0] in [aw[0] for aw in arcos_widgets]:
                    idx = [aw[0] for aw in arcos_widgets].index(item[0])
                    info = arcos_widgets[idx][1]
                    for aw in arcos_widgets:
                        canvas.itemconfigure(aw[0], width=3, outline=BRANCO)
                    canvas.itemconfigure(item[0], width=4.5, outline=AZUL_ESCURO)
                    pct = (info["valor"] / total) * 100
                    canvas.itemconfigure(total_text_id, text=f"{pct:.1f}%", font=(FONTE_TITULO, 18, "bold"))
                    canvas.itemconfigure(label_text_id, text=f"{info['origem']}\n({info['valor']} leads)", font=(FONTE_TEXTO, 8, "bold"))
                else:
                    for aw in arcos_widgets:
                        canvas.itemconfigure(aw[0], width=3, outline=BRANCO)
                    canvas.itemconfigure(total_text_id, text=str(total), font=(FONTE_TITULO, 22, "bold"))
                    canvas.itemconfigure(label_text_id, text="leads totais", font=(FONTE_TEXTO, 9))
            canvas.bind("<Motion>", ao_mover)

        def animar_pizza(passo=1):
            if passo > 20:
                _configurar_hover()
                return
            prog = passo / 20.0
            for arc_id, info in arcos_widgets:
                canvas.itemconfigure(arc_id, extent=info["target_extent"] * prog)
            for barra_id, w_alvo, y_pos in legenda_widgets:
                w_atual = int(w_alvo * prog)
                canvas.coords(barra_id, 440, y_pos, 440 + w_atual, y_pos + 4)
            card.after(15, lambda: animar_pizza(passo + 1))

        animar_pizza()

