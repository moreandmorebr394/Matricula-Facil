"""Painel de Relatórios - filtros por ano/trimestre/mês/semana."""
import tkinter as tk
from datetime import datetime, timedelta

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.combo_arredondado import ComboArredondado
from componentes.notificacoes import NotificacaoFlutuante
from controladores.controlador_aluno import ControladorLead
from controladores.controlador_academico import (
    ControladorVenda,
    ControladorTurma,
    ControladorAula,
    ControladorFrequencia,
    ControladorPagamento,
    ControladorFunil,
)


PERIODOS = ("Ano atual", "Trimestre atual", "Mês atual", "Semana atual")
ANOS = tuple(str(a) for a in range(2024, datetime.now().year + 2))


class PainelRelatorios(tk.Frame):

    def __init__(self, mestre, dashboard=None):
        super().__init__(mestre, bg=tema.OFFWHITE)
        self.pack(fill="both", expand=True)
        self.dashboard = dashboard

        # Filtros no topo
        filtros = tk.Frame(self, bg=tema.BRANCO_PURO,
                            highlightthickness=1,
                            highlightbackground=tema.CINZA_BORDA)
        filtros.pack(fill="x", padx=20, pady=(20, 10))

        bloco_f = tk.Frame(filtros, bg=tema.BRANCO_PURO)
        bloco_f.pack(fill="x", padx=20, pady=14)

        tk.Label(
            bloco_f, text="Filtros do Relatório", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 8))

        linha = tk.Frame(bloco_f, bg=tema.BRANCO_PURO)
        linha.pack(fill="x")

        tk.Label(
            linha, text="Período:", bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
        ).pack(side="left")
        self._combo_periodo = ComboArredondado(
            linha, opcoes=list(PERIODOS), valor_inicial=PERIODOS[2],
            largura=180, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_periodo.pack(side="left", padx=8)

        tk.Label(
            linha, text="Ano:", bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
        ).pack(side="left")
        self._combo_ano = ComboArredondado(
            linha, opcoes=list(ANOS), valor_inicial=str(datetime.now().year),
            largura=110, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_ano.pack(side="left", padx=8)

        BotaoArredondado(
            linha, texto="Atualizar Relatório", comando=self._atualizar,
            largura=180, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left", padx=8)

        BotaoArredondado(
            linha, texto="Exportar (.csv)", comando=self._exportar,
            cor_fundo=tema.AMARELO_DOURADO, cor_hover="#F5D45C",
            cor_press="#D6AA1F", cor_texto=tema.AZUL_ESCURO,
            largura=140, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="right")

        # Área de indicadores em grid
        self._area = tk.Frame(self, bg=tema.OFFWHITE)
        self._area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._construir_indicadores()

    # =================================================================
    def _construir_indicadores(self):
        for w in self._area.winfo_children():
            w.destroy()

        # 4 colunas no topo, 2 colunas embaixo
        topo = tk.Frame(self._area, bg=tema.OFFWHITE)
        topo.pack(fill="x", pady=(8, 12))
        for c in range(4):
            topo.columnconfigure(c, weight=1, uniform="x")

        # KPIs principais
        total_leads = ControladorLead.total_leads()
        total_vendas = ControladorVenda.total()
        faturamento = ControladorVenda.faturamento()
        media_freq = ControladorFrequencia.media_geral()

        self._kpi(topo, 0, "\u2632", "Leads", str(total_leads),
                  tema.AZUL_PRINCIPAL)
        self._kpi(topo, 1, "\u26C2", "Vendas", str(total_vendas),
                  tema.VERDE_SUCESSO)
        self._kpi(topo, 2, "$", "Faturamento",
                  f"R$ {faturamento:,.2f}".replace(",", "v")
                      .replace(".", ",").replace("v", "."),
                  tema.AMARELO_DOURADO)
        self._kpi(topo, 3, "%", "Frequência média",
                  f"{media_freq:.1f}%", tema.FUNIL_VENDAS)

        # 2 cards grandes embaixo
        meio = tk.Frame(self._area, bg=tema.OFFWHITE)
        meio.pack(fill="both", expand=True)
        meio.columnconfigure(0, weight=1, uniform="x")
        meio.columnconfigure(1, weight=1, uniform="x")
        meio.rowconfigure(0, weight=1)

        # Card de status dos leads
        card_st = tk.Frame(
            meio, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card_st.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._construir_status_leads(card_st)

        # Card consolidado
        card_co = tk.Frame(
            meio, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card_co.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self._construir_consolidado(card_co)

    def _kpi(self, pai, col, icone, rotulo, valor, cor):
        card = tk.Frame(
            pai, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card.grid(row=0, column=col, padx=4, sticky="nsew")
        bloco = tk.Frame(card, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(
            bloco, text=icone, bg=tema.BRANCO_PURO, fg=cor,
            font=tema.fonte_destaque(20),
        ).pack(anchor="w")
        tk.Label(
            bloco, text=rotulo, bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
        ).pack(anchor="w", pady=(2, 2))
        tk.Label(
            bloco, text=valor, bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(18),
        ).pack(anchor="w")

    def _construir_status_leads(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            bloco, text="Distribuição por Status", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 8))

        contagem = ControladorLead.contagem_status()
        total = sum(contagem.values()) or 1
        rotulos = {
            "LEAD": "Leads",
            "NEGOCIACAO": "Em Negociação",
            "PAGO": "Pagos",
            "NAO_PAGO": "Não Pagos",
            "ATIVO": "Ativos",
            "CANCELADO": "Cancelados",
        }
        for chave, rotulo in rotulos.items():
            qtd = contagem.get(chave, 0)
            pct = (qtd / total) * 100
            cor = tema.COR_STATUS.get(chave, tema.AZUL_PRINCIPAL)
            self._barra(bloco, rotulo, qtd, pct, cor)

    def _barra(self, pai, rotulo, qtd, pct, cor):
        linha = tk.Frame(pai, bg=tema.BRANCO_PURO)
        linha.pack(fill="x", pady=4)

        cabec = tk.Frame(linha, bg=tema.BRANCO_PURO)
        cabec.pack(fill="x")
        tk.Label(
            cabec, text=rotulo, bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_corpo(10),
        ).pack(side="left")
        tk.Label(
            cabec, text=f"{qtd}  ({pct:.1f}%)", bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(9),
        ).pack(side="right")

        # Barra de progresso (canvas)
        canvas = tk.Canvas(
            linha, width=300, height=10, bg=tema.CINZA_CLARO,
            highlightthickness=0, bd=0,
        )
        canvas.pack(fill="x", pady=(2, 0))
        canvas.update_idletasks()
        l = max(canvas.winfo_width(), 300)
        canvas.create_rectangle(
            0, 0, max(8, int(l * pct / 100)), 10, fill=cor, outline="",
        )

    def _construir_consolidado(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            bloco, text="Consolidado do Período", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 8))

        periodo = self._combo_periodo.obter_valor() if hasattr(self, "_combo_periodo") else "Mês atual"
        ano = self._combo_ano.obter_valor() if hasattr(self, "_combo_ano") else str(datetime.now().year)

        info = (
            ("Período selecionado:", periodo),
            ("Ano de referência:", ano),
            ("Total de turmas ativas:", str(len(ControladorTurma.listar()))),
            ("Total de aulas registradas:", str(len(ControladorAula.listar()))),
            ("Pagamentos confirmados:", str(len(ControladorPagamento.listar()))),
        )

        for rotulo, valor in info:
            linha = tk.Frame(bloco, bg=tema.BRANCO_PURO)
            linha.pack(fill="x", pady=6)
            tk.Label(
                linha, text=rotulo, bg=tema.BRANCO_PURO,
                fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
            ).pack(side="left")
            tk.Label(
                linha, text=valor, bg=tema.BRANCO_PURO,
                fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(11),
            ).pack(side="right")

        tk.Frame(bloco, bg=tema.CINZA_BORDA, height=1).pack(
            fill="x", pady=(14, 8),
        )

        tk.Label(
            bloco,
            text=(
                "Os indicadores acima refletem dados em tempo real.\n"
                "Para análises mais detalhadas, exporte o relatório em CSV."
            ),
            bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(9), justify="left",
        ).pack(anchor="w")

    # =================================================================
    def _atualizar(self):
        NotificacaoFlutuante.exibir(
            self.winfo_toplevel(), "Relatório atualizado.", tipo="sucesso",
            duracao_ms=1400,
        )
        self._construir_indicadores()

    def _exportar(self):
        # Mock: gerar CSV simples em memória e mostrar caminho
        import os
        from tkinter import filedialog
        caminho = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="relatorio_sistema_facil.csv",
        )
        if not caminho:
            return
        try:
            leads = ControladorLead.listar_leads()
            with open(caminho, "w", encoding="utf-8") as f:
                f.write("ID,Nome,Email,Curso,Captador,Status,Data\n")
                for l in leads:
                    f.write(
                        f"{l['id']},"
                        f"{(l.get('nome_completo') or '').replace(',', ';')},"
                        f"{l.get('email', '')},"
                        f"{(l.get('curso_interesse') or '').replace(',', ';')},"
                        f"{(l.get('captador') or '').replace(',', ';')},"
                        f"{l.get('status', '')},"
                        f"{l.get('criado_em', '')}\n"
                    )
            NotificacaoFlutuante.exibir(
                self.winfo_toplevel(),
                f"Relatório exportado: {os.path.basename(caminho)}",
                tipo="sucesso",
            )
        except Exception as exc:
            NotificacaoFlutuante.exibir(
                self.winfo_toplevel(),
                f"Erro ao exportar: {exc}", tipo="erro",
            )
