"""
Pagina Relatorios - tabelas e graficos resumo com filtros por periodo.
"""
import tkinter as tk
from tkinter import ttk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    AMARELO_VIBRANTE, VERDE_SUCESSO, VERMELHO_ERRO,
    ROXO_DESTAQUE, LARANJA_ALERTA,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from app.controlador import controlador_dashboard
from app.controlador.listas_constantes import PERIODOS


class PaginaRelatorios(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self._construir()

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Relatorios",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo,
                 text="Visualize e exporte relatorios de desempenho",
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

        # Filtros
        self._construir_filtros(cont)

        # Cards resumo
        self._construir_resumo(cont)

        # Grafico evolutivo
        self._construir_grafico_evolutivo(cont)

        # Tabela ranking cursos
        self._construir_ranking_cursos(cont)

    def _construir_filtros(self, parent):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        h.pack(fill="x")

        tk.Label(h, text="🔍  Filtros",
                 font=(FONTE_TEXTO, 11, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(side="left")

        # Periodo
        tk.Label(h, text="Periodo:",
                 font=(FONTE_TEXTO, 9, "bold"),
                 fg=CINZA_ESCURO, bg=BRANCO).pack(side="left", padx=(20, 6))

        self.combo_periodo = ttk.Combobox(h, values=PERIODOS,
                                          state="readonly",
                                          font=(FONTE_TEXTO, 10), width=12)
        self.combo_periodo.set("Mensal")
        self.combo_periodo.pack(side="left", padx=4)

        # Categoria
        tk.Label(h, text="Categoria:",
                 font=(FONTE_TEXTO, 9, "bold"),
                 fg=CINZA_ESCURO, bg=BRANCO).pack(side="left", padx=(16, 6))

        self.combo_categoria = ttk.Combobox(
            h, values=["Vendas", "Pagamentos", "Leads", "Geral"],
            state="readonly",
            font=(FONTE_TEXTO, 10), width=14)
        self.combo_categoria.set("Geral")
        self.combo_categoria.pack(side="left", padx=4)

        BotaoModerno(h, texto="Aplicar Filtro",
                     comando=self._aplicar_filtro,
                     largura=140, altura=32,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     fonte_tamanho=10,
                     cor_fundo=BRANCO).pack(side="left", padx=10)

        BotaoModerno(h, texto="📥  Exportar PDF",
                     comando=lambda: Notificacao.info(
                         self,
                         "Exportacao em desenvolvimento"),
                     largura=140, altura=32,
                     cor_normal=AMARELO_VIBRANTE, cor_hover="#D4A800",
                     cor_texto=AZUL_ESCURO,
                     fonte_tamanho=10,
                     cor_fundo=BRANCO).pack(side="right", padx=4)

    def _construir_resumo(self, parent):
        try:
            stats = controlador_dashboard.estatisticas_gerais()
        except Exception:
            stats = {"total_leads": 0, "total_vendas": 0,
                     "total_turmas": 0, "total_aulas": 0,
                     "faturamento": 0.0, "recebido": 0.0}

        cards = [
            ("👥 Total de Leads", str(stats["total_leads"]),
             "+12% vs anterior", AZUL_PRIMARIO),
            ("💰 Vendas", str(stats["total_vendas"]),
             "+8% vs anterior", VERDE_SUCESSO),
            ("📚 Turmas Ativas", str(stats["total_turmas"]),
             "Cadastradas", ROXO_DESTAQUE),
            ("💵 Faturamento",
             f"R$ {stats['faturamento']:,.2f}".replace(",", "."),
             "Total acumulado", AMARELO_VIBRANTE),
            ("✓ Recebido",
             f"R$ {stats['recebido']:,.2f}".replace(",", "."),
             "Pagamentos confirmados", VERDE_SUCESSO),
        ]

        wrap = tk.Frame(parent, bg=BRANCO_GELO, padx=24, pady=10)
        wrap.pack(fill="x")

        for i, (titulo, valor, descricao, cor) in enumerate(cards):
            card = tk.Frame(wrap, bg=BRANCO,
                            highlightbackground=CINZA_CLARO,
                            highlightthickness=1)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            wrap.columnconfigure(i, weight=1)

            tk.Frame(card, bg=cor, height=4).pack(fill="x")
            c = tk.Frame(card, bg=BRANCO, padx=14, pady=12)
            c.pack(fill="both", expand=True)

            tk.Label(c, text=titulo,
                     font=(FONTE_TEXTO, 8, "bold"),
                     fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
            tk.Label(c, text=valor,
                     font=(FONTE_TITULO, 18, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w", pady=(4, 4))
            tk.Label(c, text=descricao,
                     font=(FONTE_TEXTO, 8),
                     fg=cor, bg=BRANCO).pack(anchor="w")

    def _construir_grafico_evolutivo(self, parent):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="📈  Evolucao Mensal",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        canvas = tk.Canvas(card, bg=BRANCO, height=300,
                           highlightthickness=0)
        canvas.pack(fill="x", padx=18, pady=14)

        # Dados de exemplo (em producao viriam do banco)
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                 "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        valores = [12, 18, 22, 28, 32, 38, 42, 38, 45, 52, 48, 55]
        max_val = max(valores)

        # Eixos
        x_inicio = 60
        x_fim = 1060
        y_topo = 30
        y_base = 240

        # Linha base
        canvas.create_line(x_inicio, y_base, x_fim, y_base,
                           fill=CINZA_CLARO, width=2)

        # Linhas horizontais de grade
        for i in range(5):
            y = y_topo + i * ((y_base - y_topo) / 4)
            canvas.create_line(x_inicio, y, x_fim, y,
                               fill=CINZA_CLARO, dash=(2, 4))
            valor_eixo = max_val * (1 - i / 4)
            canvas.create_text(x_inicio - 10, y, anchor="e",
                               text=f"{valor_eixo:.0f}",
                               fill=CINZA_MEDIO,
                               font=(FONTE_TEXTO, 8))

        # Calcula posicoes
        pontos = []
        for i, (mes, valor) in enumerate(zip(meses, valores)):
            x = x_inicio + (i * (x_fim - x_inicio) / (len(meses) - 1))
            y = y_base - ((valor / max_val) * (y_base - y_topo))
            pontos.append((x, y, mes, valor))

        # Linha conectando
        coords = []
        for x, y, _, _ in pontos:
            coords.extend([x, y])
        canvas.create_line(coords, fill=AZUL_PRIMARIO, width=3,
                           smooth=True)

        # Pontos
        for x, y, mes, valor in pontos:
            canvas.create_oval(x - 5, y - 5, x + 5, y + 5,
                               fill=AZUL_PRIMARIO, outline=BRANCO, width=2)
            # Valor acima
            canvas.create_text(x, y - 14, text=str(valor),
                               fill=AZUL_ESCURO,
                               font=(FONTE_TEXTO, 8, "bold"))
            # Mes embaixo
            canvas.create_text(x, y_base + 18, text=mes,
                               fill=CINZA_ESCURO,
                               font=(FONTE_TEXTO, 9))

    def _construir_ranking_cursos(self, parent):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="🏆  Ranking de Cursos Mais Procurados",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        head = tk.Frame(card, bg=AZUL_PRIMARIO)
        head.pack(fill="x", padx=18, pady=(8, 0))
        for col in ["Posicao", "Curso", "Leads", "Vendas",
                    "Conversao", "Faturamento"]:
            tk.Label(head, text=col,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        # Dados exemplo
        ranking = [
            ("Tecnico em Informatica", 45, 18, "40%", "R$ 21.600"),
            ("Tecnico em Enfermagem", 38, 15, "39%", "R$ 22.500"),
            ("Tecnico em Administracao", 32, 12, "37%", "R$ 14.400"),
            ("Bombeiro Civil", 28, 10, "36%", "R$ 12.000"),
            ("Tecnico em Seguranca do Trabalho", 22, 8, "36%", "R$ 9.600"),
            ("Administracao", 18, 6, "33%", "R$ 7.200"),
            ("Tecnico em Secretaria Escolar", 12, 4, "33%", "R$ 4.800"),
        ]

        wrap_linhas = tk.Frame(card, bg=BRANCO)
        wrap_linhas.pack(fill="x", padx=18, pady=(0, 14))

        for i, (curso, leads, vendas, conv, fat) in enumerate(ranking):
            linha = tk.Frame(wrap_linhas, bg=BRANCO,
                             highlightbackground=CINZA_CLARO,
                             highlightthickness=1)
            linha.pack(fill="x")

            # Medal
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"

            for j, valor in enumerate([medal, curso, str(leads),
                                       str(vendas), conv, fat]):
                fonte_estilo = "bold" if j in (0, 5) else "normal"
                cor = AZUL_ESCURO if j == 0 else (
                    VERDE_SUCESSO if j == 5 else PRETO_TEXTO)
                tk.Label(linha, text=str(valor),
                         font=(FONTE_TEXTO, 9, fonte_estilo),
                         fg=cor, bg=BRANCO,
                         padx=8, pady=8).pack(side="left", expand=True,
                                              fill="x")

    def _aplicar_filtro(self):
        periodo = self.combo_periodo.get()
        categoria = self.combo_categoria.get()
        Notificacao.sucesso(
            self, f"Filtro aplicado: {categoria} ({periodo})"
        )
