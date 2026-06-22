"""
Pagina Relatorios - tabelas e graficos resumo com filtros por periodo e categoria.
Exportacao real em PDF via reportlab.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    AMARELO_VIBRANTE, VERDE_SUCESSO, VERMELHO_ERRO,
    ROXO_DESTAQUE, LARANJA_ALERTA,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from componentes.card import Card
from app.controlador import controlador_dashboard
from app.controlador.listas_constantes import PERIODOS


def _intervalo_periodo(periodo):
    """
    Retorna (data_inicio, data_fim) como strings 'YYYY-MM-DD'
    para o periodo selecionado.
    """
    hoje = datetime.today()
    if periodo == "Diario":
        inicio = hoje
    elif periodo == "Semanal":
        inicio = hoje - timedelta(days=7)
    elif periodo == "Mensal":
        inicio = hoje - timedelta(days=30)
    elif periodo == "Trimestral":
        inicio = hoje - timedelta(days=90)
    else:  # Anual ou qualquer outro
        inicio = hoje - timedelta(days=365)
    return inicio.strftime("%Y-%m-%d"), hoje.strftime("%Y-%m-%d")


def _data_no_periodo(data_str, inicio_str, fim_str):
    """Verifica se uma string de data esta dentro do intervalo."""
    if not data_str:
        return True  # sem data = inclui sempre
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(str(data_str)[:len(fmt.replace("%Y", "0000").replace("%m", "00").replace("%d", "00").replace("%H", "00").replace("%M", "00").replace("%S", "00"))], fmt)
            break
        except ValueError:
            continue
    else:
        return True  # nao conseguiu parsear, inclui
    ini = datetime.strptime(inicio_str, "%Y-%m-%d")
    fim = datetime.strptime(fim_str, "%Y-%m-%d") + timedelta(days=1)
    return ini <= dt < fim


def _filtrar_por_periodo(registros, campo_data, periodo):
    """Filtra lista de dicts por periodo."""
    if periodo == "Anual":
        return registros
    inicio, fim = _intervalo_periodo(periodo)
    return [r for r in registros if _data_no_periodo(r.get(campo_data, ""), inicio, fim)]


class PaginaRelatorios(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        # Estado atual dos filtros
        self._periodo_atual = "Mensal"
        self._categoria_atual = "Geral"
        # Dados filtrados para uso no PDF
        self._dados_filtrados = {}
        self._construir()

    # ---------------------------------------------------------------
    # CONSTRUCAO DA TELA
    # ---------------------------------------------------------------

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Relatórios",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo,
                 text="Visualize e exporte relatórios de desempenho",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO).pack(anchor="w")

        self._canvas_main = tk.Canvas(self, bg=BRANCO_GELO, highlightthickness=0)
        self._canvas_main.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(self, orient="vertical", command=self._canvas_main.yview)
        sb.pack(side="right", fill="y")
        self._canvas_main.configure(yscrollcommand=sb.set)

        self._cont = tk.Frame(self._canvas_main, bg=BRANCO_GELO)
        window_id = self._canvas_main.create_window((0, 0), window=self._cont, anchor="n",
                                        width=1140)

        def ar(_=None):
            bbox = self._canvas_main.bbox("all")
            if bbox:
                self._canvas_main.configure(scrollregion=(0, 0, 0, bbox[3]))
        self._cont.bind("<Configure>", ar)

        def ao_redimensionar_canvas(e):
            nova_largura = min(1140, e.width - 40)
            if nova_largura < 300:
                nova_largura = 300
            self._canvas_main.itemconfig(window_id, width=nova_largura)
            self._canvas_main.coords(window_id, e.width // 2, 0)
        self._canvas_main.bind("<Configure>", ao_redimensionar_canvas, add="+")
        self._canvas_main.bind_all("<MouseWheel>",
                                   lambda e: self._canvas_main.yview_scroll(
                                       int(-1 * (e.delta / 120)), "units"), add="+")

        self._construir_filtros(self._cont)
        self._area_conteudo = tk.Frame(self._cont, bg=BRANCO_GELO)
        self._area_conteudo.pack(fill="both", expand=True)
        self._renderizar_conteudo()

    def _construir_filtros(self, parent):
        card = Card(parent, titulo="🔍  Filtros", padding=14, raio=12)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card.interno, bg=BRANCO)
        h.pack(fill="x")

        # Periodo
        tk.Label(h, text="Período:",
                 font=(FONTE_TEXTO, 9, "bold"),
                 fg=CINZA_ESCURO, bg=BRANCO).pack(side="left", padx=(0, 6))

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
                     comando=self._exportar_pdf,
                     largura=150, altura=32,
                     cor_normal=AMARELO_VIBRANTE, cor_hover="#D4A800",
                     cor_texto=AZUL_ESCURO,
                     fonte_tamanho=10,
                     cor_fundo=BRANCO).pack(side="right", padx=4)

        # Label indicador do filtro ativo
        self._label_filtro_ativo = tk.Label(
            card.interno,
            text=f"  🟢  Exibindo: Geral · Mensal  (últimos 30 dias)",
            font=(FONTE_TEXTO, 8),
            fg=VERDE_SUCESSO, bg=BRANCO,
            anchor="w", pady=6
        )
        self._label_filtro_ativo.pack(fill="x")

    # ---------------------------------------------------------------
    # LOGICA DE FILTRO
    # ---------------------------------------------------------------

    def _aplicar_filtro(self):
        self._periodo_atual = self.combo_periodo.get()
        self._categoria_atual = self.combo_categoria.get()
        self._atualizar_label_filtro()
        self._renderizar_conteudo()

    def _atualizar_label_filtro(self):
        inicio, fim = _intervalo_periodo(self._periodo_atual)
        # formata para exibicao
        d_ini = datetime.strptime(inicio, "%Y-%m-%d").strftime("%d/%m/%Y")
        d_fim = datetime.strptime(fim, "%Y-%m-%d").strftime("%d/%m/%Y")
        texto = f"  🟢  Exibindo: {self._categoria_atual} · {self._periodo_atual}  ({d_ini} → {d_fim})"
        self._label_filtro_ativo.config(text=texto)

    def _renderizar_conteudo(self):
        # Limpa area de conteudo
        for w in self._area_conteudo.winfo_children():
            w.destroy()

        periodo = self._periodo_atual
        categoria = self._categoria_atual

        # Carrega dados brutos
        try:
            todos_leads = controlador_dashboard.listar_leads()
        except Exception:
            todos_leads = []
        try:
            todas_vendas = controlador_dashboard.listar_vendas()
        except Exception:
            todas_vendas = []
        try:
            todos_pagamentos = controlador_dashboard.listar_pagamentos()
        except Exception:
            todos_pagamentos = []
        try:
            todos_alunos = self._listar_alunos()
        except Exception:
            todos_alunos = []

        # Aplica filtro de periodo
        leads = _filtrar_por_periodo(todos_leads, "data_cadastro", periodo)
        vendas = _filtrar_por_periodo(todas_vendas, "data_venda", periodo)
        pagamentos = _filtrar_por_periodo(todos_pagamentos, "data_registro", periodo)

        # Guarda para PDF
        self._dados_filtrados = {
            "leads": leads,
            "vendas": vendas,
            "pagamentos": pagamentos,
            "alunos": todos_alunos,
            "periodo": periodo,
            "categoria": categoria,
        }

        # Renderiza secoes conforme categoria
        if categoria in ("Geral", "Leads"):
            self._construir_resumo_cards(self._area_conteudo, leads, vendas, pagamentos)

        if categoria in ("Geral", "Vendas"):
            self._construir_tabela_vendas(self._area_conteudo, vendas)

        if categoria in ("Geral", "Pagamentos"):
            self._construir_tabela_pagamentos(self._area_conteudo, pagamentos)

        if categoria in ("Geral", "Leads"):
            self._construir_tabela_leads(self._area_conteudo, leads)

        # Cadastro de alunos sempre exibido
        self._construir_tabela_alunos(self._area_conteudo, todos_alunos)

    # ---------------------------------------------------------------
    # CARDS DE RESUMO
    # ---------------------------------------------------------------

    def _construir_resumo_cards(self, parent, leads, vendas, pagamentos):
        fat = sum(float(v.get("valor_total", 0) or 0) for v in vendas)
        rec = sum(float(p.get("valor", 0) or 0)
                  for p in pagamentos if str(p.get("status", "")).lower() == "pago")

        cards = [
            ("👥 Total de Leads", str(len(leads)), "no período", AZUL_PRIMARIO),
            ("💰 Vendas", str(len(vendas)), "no período", VERDE_SUCESSO),
            ("💵 Faturamento",
             f"R$ {fat:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
             "total das vendas", AMARELO_VIBRANTE),
            ("✓ Recebido",
             f"R$ {rec:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
             "pagamentos confirmados", VERDE_SUCESSO),
            ("📋 Pagamentos", str(len(pagamentos)), "no período", ROXO_DESTAQUE),
        ]

        wrap = tk.Frame(parent, bg=BRANCO_GELO, padx=24, pady=10)
        wrap.pack(fill="x")

        for i, (titulo, valor, descricao, cor) in enumerate(cards):
            card = Card(wrap, padding=0, raio=12)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            wrap.columnconfigure(i, weight=1)

            tk.Frame(card.interno, bg=cor, height=4).pack(fill="x")
            c = tk.Frame(card.interno, bg=BRANCO, padx=14, pady=12)
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

    # ---------------------------------------------------------------
    # TABELAS
    # ---------------------------------------------------------------

    def _tabela_generica(self, parent, titulo, colunas, linhas, cor_titulo=AZUL_PRIMARIO):
        card = Card(parent, padding=14, raio=12)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card.interno, bg=BRANCO)
        h.pack(fill="x", pady=(0, 8))
        tk.Label(h, text=titulo,
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(side="left")
        tk.Label(h, text=f"{len(linhas)} registro(s)",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(side="right")

        # Cabecalho
        head = tk.Frame(card.interno, bg=cor_titulo)
        head.pack(fill="x", pady=(8, 0))
        for col in colunas:
            tk.Label(head, text=col,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=BRANCO, bg=cor_titulo,
                     padx=8, pady=7).pack(side="left", expand=True, fill="x")

        # Linhas
        wrap_linhas = tk.Frame(card.interno, bg=BRANCO)
        wrap_linhas.pack(fill="x", pady=(10, 0))

        if not linhas:
            tk.Label(wrap_linhas,
                     text="Nenhum registro encontrado no período selecionado.",
                     font=(FONTE_TEXTO, 9),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=16).pack()
            return

        for i, row in enumerate(linhas):
            bg_row = BRANCO if i % 2 == 0 else "#F7F9FC"
            linha = tk.Frame(wrap_linhas, bg=bg_row,
                             highlightbackground=CINZA_CLARO,
                             highlightthickness=1)
            linha.pack(fill="x")
            for j, valor in enumerate(row):
                tk.Label(linha, text=str(valor),
                         font=(FONTE_TEXTO, 9),
                         fg=PRETO_TEXTO, bg=bg_row,
                         padx=8, pady=7).pack(side="left", expand=True, fill="x")

    def _construir_tabela_vendas(self, parent, vendas):
        colunas = ["#", "Aluno", "Curso", "Valor Total", "Pagamento", "Status", "Data"]
        linhas = []
        for i, v in enumerate(vendas[:50], 1):
            data_raw = v.get("data_venda", "")
            data_fmt = str(data_raw)[:10] if data_raw else "-"
            valor = float(v.get("valor_total", 0) or 0)
            linhas.append([
                i,
                v.get("nome_aluno", "-"),
                v.get("curso", "-"),
                f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                v.get("forma_pagamento", "-"),
                v.get("status_pagamento", "-"),
                data_fmt,
            ])
        self._tabela_generica(parent, "💰  Vendas no Período", colunas, linhas, VERDE_SUCESSO)

    def _construir_tabela_pagamentos(self, parent, pagamentos):
        colunas = ["#", "Aluno", "Valor", "Forma Pgto", "Parcela", "Status", "Data"]
        linhas = []
        for i, p in enumerate(pagamentos[:50], 1):
            data_raw = p.get("data_registro", "")
            data_fmt = str(data_raw)[:10] if data_raw else "-"
            valor = float(p.get("valor", 0) or 0)
            linhas.append([
                i,
                p.get("nome_aluno", "-"),
                f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                p.get("forma_pagamento", "-"),
                p.get("parcela_numero", "1"),
                p.get("status", "-"),
                data_fmt,
            ])
        self._tabela_generica(parent, "📋  Pagamentos no Período", colunas, linhas, ROXO_DESTAQUE)

    def _construir_tabela_leads(self, parent, leads):
        colunas = ["#", "Nome", "Curso Interesse", "Status", "Captador", "Data Cadastro"]
        linhas = []
        for i, l in enumerate(leads[:50], 1):
            data_raw = l.get("data_cadastro", "")
            data_fmt = str(data_raw)[:10] if data_raw else "-"
            linhas.append([
                i,
                l.get("nome_completo", "-"),
                l.get("curso_interesse", "-"),
                l.get("status", "-"),
                l.get("captador", "-"),
                data_fmt,
            ])
        self._tabela_generica(parent, "👥  Leads no Período", colunas, linhas, AZUL_PRIMARIO)

    def _listar_alunos(self):
        """Busca usuarios do tipo aluno."""
        from app.modelo import modelo_usuario
        try:
            return modelo_usuario.listar_usuarios(tipo="aluno")
        except Exception:
            return []

    def _construir_tabela_alunos(self, parent, alunos):
        colunas = ["#", "Nome Completo", "Email Cadastro", "Email Institucional", "Matrícula", "Data Cadastro"]
        linhas = []
        for i, a in enumerate(alunos, 1):
            data_raw = a.get("data_cadastro", "")
            data_fmt = str(data_raw)[:10] if data_raw else "-"
            linhas.append([
                i,
                a.get("nome_completo", "-"),
                a.get("email_cadastro", "-"),
                a.get("email_institucional", "-"),
                a.get("matricula", "-"),
                data_fmt,
            ])
        self._tabela_generica(parent, "🎓  Cadastro de Alunos", colunas, linhas, AZUL_ESCURO)

    # ---------------------------------------------------------------
    # EXPORTACAO PDF
    # ---------------------------------------------------------------

    def _exportar_pdf(self):
        """Exporta o relatorio atual para PDF usando reportlab."""
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                             Paragraph, Spacer, HRFlowable)
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            messagebox.showerror(
                "Dependência ausente",
                "A biblioteca 'reportlab' não está instalada.\n\n"
                "Execute: pip install reportlab",
                parent=self
            )
            return

        # Escolhe caminho
        caminho = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"relatorio_{self._categoria_atual.lower()}_{self._periodo_atual.lower()}.pdf",
            title="Salvar Relatório PDF"
        )
        if not caminho:
            return

        d = self._dados_filtrados
        periodo = d.get("periodo", self._periodo_atual)
        categoria = d.get("categoria", self._categoria_atual)
        leads = d.get("leads", [])
        vendas = d.get("vendas", [])
        pagamentos = d.get("pagamentos", [])
        alunos = d.get("alunos", [])

        inicio, fim = _intervalo_periodo(periodo)
        d_ini = datetime.strptime(inicio, "%Y-%m-%d").strftime("%d/%m/%Y")
        d_fim = datetime.strptime(fim, "%Y-%m-%d").strftime("%d/%m/%Y")

        # Cores reportlab
        COR_AZUL = colors.HexColor("#112250")
        COR_AZUL_MED = colors.HexColor("#3C507D")
        COR_VERDE = colors.HexColor("#10B981")
        COR_ROXO = colors.HexColor("#8B5CF6")
        COR_AMARELO = colors.HexColor("#F5C518")
        COR_CINZA = colors.HexColor("#E5E9F0")
        COR_CINZA_TEXTO = colors.HexColor("#4B5563")
        BRANCO_RL = colors.white

        doc = SimpleDocTemplate(
            caminho,
            pagesize=landscape(A4),
            leftMargin=15*mm, rightMargin=15*mm,
            topMargin=15*mm, bottomMargin=15*mm
        )

        styles = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle(
            "Titulo",
            parent=styles["Title"],
            fontSize=20,
            textColor=COR_AZUL,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        )
        estilo_subtitulo = ParagraphStyle(
            "SubTitulo",
            parent=styles["Normal"],
            fontSize=10,
            textColor=COR_CINZA_TEXTO,
            spaceAfter=2,
        )
        estilo_secao = ParagraphStyle(
            "Secao",
            parent=styles["Normal"],
            fontSize=12,
            textColor=COR_AZUL,
            fontName="Helvetica-Bold",
            spaceBefore=10,
            spaceAfter=4,
        )
        estilo_rodape = ParagraphStyle(
            "Rodape",
            parent=styles["Normal"],
            fontSize=8,
            textColor=COR_CINZA_TEXTO,
        )

        largura_pagina = landscape(A4)[0] - 30*mm

        story = []

        # Cabecalho
        story.append(Paragraph("📊 Sistema Fácil — Relatório de Desempenho", estilo_titulo))
        story.append(Paragraph(
            f"Categoria: <b>{categoria}</b>  |  Período: <b>{periodo}</b>  |  "
            f"Intervalo: <b>{d_ini} → {d_fim}</b>  |  "
            f"Gerado em: <b>{datetime.now().strftime('%d/%m/%Y às %H:%M')}</b>",
            estilo_subtitulo
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=COR_AZUL_MED, spaceAfter=8))

        # --- RESUMO GERAL ---
        if categoria in ("Geral", "Leads", "Vendas", "Pagamentos"):
            fat = sum(float(v.get("valor_total", 0) or 0) for v in vendas)
            rec = sum(float(p.get("valor", 0) or 0)
                      for p in pagamentos if str(p.get("status", "")).lower() == "pago")
            fat_fmt = f"R$ {fat:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            rec_fmt = f"R$ {rec:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            story.append(Paragraph("Resumo do Período", estilo_secao))
            resumo_data = [
                ["Total de Leads", "Total de Vendas", "Faturamento", "Total Recebido", "Total Pagamentos"],
                [str(len(leads)), str(len(vendas)), fat_fmt, rec_fmt, str(len(pagamentos))]
            ]
            t_resumo = Table(resumo_data, colWidths=[largura_pagina/5]*5)
            t_resumo.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COR_AZUL_MED),
                ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO_RL),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F0F4FF")]),
                ("GRID", (0, 0), (-1, -1), 0.5, COR_CINZA),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(t_resumo)
            story.append(Spacer(1, 8))

        # --- CADASTRO DE ALUNOS (sempre exportado) ---
        story.append(Paragraph(f"🎓 Cadastro de Alunos ({len(alunos)} registros)", estilo_secao))
        if alunos:
            cab_alunos = ["#", "Nome Completo", "Email Cadastro", "Email Institucional", "Matrícula", "Cadastro"]
            col_w_alunos = [10*mm, 60*mm, 60*mm, 60*mm, 30*mm, 27*mm]
            dados_alunos = [cab_alunos]
            for i, a in enumerate(alunos, 1):
                data_raw = a.get("data_cadastro", "")
                data_fmt = str(data_raw)[:10] if data_raw else "-"
                dados_alunos.append([
                    str(i),
                    str(a.get("nome_completo", "-"))[:35],
                    str(a.get("email_cadastro", "-"))[:30],
                    str(a.get("email_institucional", "-"))[:30],
                    str(a.get("matricula", "-")),
                    data_fmt,
                ])
            t_alunos = Table(dados_alunos, colWidths=col_w_alunos, repeatRows=1)
            t_alunos.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COR_AZUL),
                ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO_RL),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO_RL, colors.HexColor("#F7F9FC")]),
                ("GRID", (0, 0), (-1, -1), 0.4, COR_CINZA),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t_alunos)
        else:
            story.append(Paragraph("Nenhum aluno cadastrado.", estilo_subtitulo))
        story.append(Spacer(1, 8))

        # --- VENDAS ---
        if categoria in ("Geral", "Vendas") and vendas:
            story.append(Paragraph(f"💰 Vendas no Período ({len(vendas)} registros)", estilo_secao))
            cab_v = ["#", "Aluno", "Curso", "Valor Total", "Pagamento", "Status", "Data"]
            col_w_v = [10*mm, 50*mm, 55*mm, 30*mm, 30*mm, 27*mm, 25*mm]
            dados_v = [cab_v]
            for i, v in enumerate(vendas[:100], 1):
                data_raw = v.get("data_venda", "")
                data_fmt = str(data_raw)[:10] if data_raw else "-"
                valor = float(v.get("valor_total", 0) or 0)
                val_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                dados_v.append([
                    str(i),
                    str(v.get("nome_aluno", "-"))[:28],
                    str(v.get("curso", "-"))[:32],
                    val_fmt,
                    str(v.get("forma_pagamento", "-")),
                    str(v.get("status_pagamento", "-")),
                    data_fmt,
                ])
            t_v = Table(dados_v, colWidths=col_w_v, repeatRows=1)
            t_v.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COR_VERDE),
                ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO_RL),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO_RL, colors.HexColor("#F0FFF8")]),
                ("GRID", (0, 0), (-1, -1), 0.4, COR_CINZA),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t_v)
            story.append(Spacer(1, 8))

        # --- PAGAMENTOS ---
        if categoria in ("Geral", "Pagamentos") and pagamentos:
            story.append(Paragraph(f"📋 Pagamentos no Período ({len(pagamentos)} registros)", estilo_secao))
            cab_p = ["#", "Aluno", "Valor", "Forma Pgto", "Parcela", "Status", "Data"]
            col_w_p = [10*mm, 55*mm, 30*mm, 35*mm, 22*mm, 27*mm, 25*mm]
            dados_p = [cab_p]
            for i, pg in enumerate(pagamentos[:100], 1):
                data_raw = pg.get("data_registro", "")
                data_fmt = str(data_raw)[:10] if data_raw else "-"
                valor = float(pg.get("valor", 0) or 0)
                val_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                dados_p.append([
                    str(i),
                    str(pg.get("nome_aluno", "-"))[:30],
                    val_fmt,
                    str(pg.get("forma_pagamento", "-")),
                    str(pg.get("parcela_numero", "1")),
                    str(pg.get("status", "-")),
                    data_fmt,
                ])
            t_p = Table(dados_p, colWidths=col_w_p, repeatRows=1)
            t_p.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COR_ROXO),
                ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO_RL),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO_RL, colors.HexColor("#F5F0FF")]),
                ("GRID", (0, 0), (-1, -1), 0.4, COR_CINZA),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t_p)
            story.append(Spacer(1, 8))

        # --- LEADS ---
        if categoria in ("Geral", "Leads") and leads:
            story.append(Paragraph(f"👥 Leads no Período ({len(leads)} registros)", estilo_secao))
            cab_l = ["#", "Nome", "Curso Interesse", "Status", "Captador", "Data Cadastro"]
            col_w_l = [10*mm, 60*mm, 60*mm, 35*mm, 40*mm, 27*mm]
            dados_l = [cab_l]
            for i, lead in enumerate(leads[:100], 1):
                data_raw = lead.get("data_cadastro", "")
                data_fmt = str(data_raw)[:10] if data_raw else "-"
                dados_l.append([
                    str(i),
                    str(lead.get("nome_completo", "-"))[:35],
                    str(lead.get("curso_interesse", "-"))[:35],
                    str(lead.get("status", "-")),
                    str(lead.get("captador", "-")),
                    data_fmt,
                ])
            t_l = Table(dados_l, colWidths=col_w_l, repeatRows=1)
            t_l.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COR_AZUL_MED),
                ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO_RL),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO_RL, colors.HexColor("#F0F4FF")]),
                ("GRID", (0, 0), (-1, -1), 0.4, COR_CINZA),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t_l)
            story.append(Spacer(1, 8))

        # Rodape
        story.append(HRFlowable(width="100%", thickness=1, color=COR_CINZA, spaceBefore=6))
        story.append(Paragraph(
            f"Relatório gerado automaticamente pelo Sistema Fácil  |  "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
            estilo_rodape
        ))

        try:
            doc.build(story)
            Notificacao.sucesso(self, f"PDF exportado com sucesso!")
            # Tenta abrir o arquivo
            import subprocess, sys
            if sys.platform == "win32":
                import os
                os.startfile(caminho)
            elif sys.platform == "darwin":
                subprocess.call(["open", caminho])
            else:
                subprocess.call(["xdg-open", caminho])
        except Exception as e:
            messagebox.showerror("Erro ao gerar PDF", str(e), parent=self)