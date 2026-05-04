"""
telas/dashboard.py — Tela principal do CRM Sistema Fácil Educação
"""

import tkinter as tk
from tkinter import ttk

from utils.tema import *
from utils.helpers import (card, label_titulo, label_secao, label_normal,
                            label_pequena, entrada, botao_primario,
                            botao_secundario, combo, separador)
from componentes.sidebar import Sidebar
from componentes.header import Header
from componentes.grafico_funil import GraficoFunil, GraficoPizza


# ─── Dados mock ────────────────────────────────────────────────────────────
LEADS_RECENTES = [
    ("Ana Beatriz Lima",  "Social Media",    "Carlos Lima",   "LEAD",     "24/05/2024"),
    ("Pedro Henrique",    "Tráfego Pago",    "Maria Santos",  "NEGOC.",   "23/05/2024"),
    ("Lucas Oliveira",    "Design Gráfico",  "João Pereira",  "PAGO",     "22/05/2024"),
    ("Julia Costa",       "Marketing Digital","Maria Santos", "NÃO PAGO", "21/05/2024"),
]

JORNADA = [
    (1, "Cadastro do aluno (lead)",       "Lead cadastrado no sistema.",          True),
    (2, "Registro da venda (captador)",   "Registrar negociação e definir cond.", True),
    (3, "Definição do status (Pago/Não)", "Definir se o aluno já está pago.",     False),
    (4, "Registro do pagamento",          "Registrar pagamento e emitir comprov..",False),
    (5, "Liberação para turma",           "Liberar aluno para a turma.",          False),
    (6, "Formação de turma",              "Adicionar aluno à turma.",             False),
    (7, "Início das aulas",               "Aulas liberadas conforme calendário.", False),
    (8, "Controle de frequência",         "Acompanhar presença nas aulas.",       False),
]

COR_STATUS = {
    "LEAD":     (AZUL_PRIMARIO, BRANCO),
    "NEGOC.":   (LARANJA,      BRANCO),
    "PAGO":     (VERDE,        BRANCO),
    "NÃO PAGO": (VERMELHO,     BRANCO),
}


class TelaDashboard(tk.Frame):
    def __init__(self, pai, **kwargs):
        super().__init__(pai, bg=CINZA_FUNDO, **kwargs)
        self._construir()
        self.after(300, self._animar_entrada)

    # ── Layout raiz ────────────────────────────────────────────────────────
    def _construir(self):
        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.pack(side="left", fill="y")

        # Conteúdo principal
        self._area_principal = tk.Frame(self, bg=CINZA_FUNDO)
        self._area_principal.pack(side="left", fill="both", expand=True)

        # Header
        self.header = Header(self._area_principal,
                             titulo_pagina="Cadastro do Aluno (Lead)",
                             subtitulo="Leads / Novo Cadastro")
        self.header.pack(fill="x")

        # Scroll container
        self._canvas_scroll = tk.Canvas(self._area_principal,
                                        bg=CINZA_FUNDO,
                                        highlightthickness=0)
        self._scroll_y = ttk.Scrollbar(self._area_principal,
                                       orient="vertical",
                                       command=self._canvas_scroll.yview)
        self._canvas_scroll.configure(yscrollcommand=self._scroll_y.set)
        self._scroll_y.pack(side="right", fill="y")
        self._canvas_scroll.pack(side="left", fill="both", expand=True)

        self._frame_conteudo = tk.Frame(self._canvas_scroll, bg=CINZA_FUNDO)
        self._janela_scroll = self._canvas_scroll.create_window(
            (0, 0), window=self._frame_conteudo, anchor="nw")

        self._frame_conteudo.bind("<Configure>", self._on_configure)
        self._canvas_scroll.bind("<Configure>", self._on_canvas_resize)
        self._canvas_scroll.bind_all("<MouseWheel>", self._on_scroll)

        self._montar_conteudo()

    def _on_configure(self, e):
        self._canvas_scroll.configure(
            scrollregion=self._canvas_scroll.bbox("all"))

    def _on_canvas_resize(self, e):
        self._canvas_scroll.itemconfig(
            self._janela_scroll, width=e.width)

    def _on_scroll(self, e):
        self._canvas_scroll.yview_scroll(int(-1*(e.delta/120)), "units")

    # ── Conteúdo: 3 colunas ────────────────────────────────────────────────
    def _montar_conteudo(self):
        pad = 14
        frame = self._frame_conteudo

        # Wrapper das 3 colunas
        self._cols = tk.Frame(frame, bg=CINZA_FUNDO)
        self._cols.pack(fill="both", expand=True, padx=pad, pady=pad)
        self._cols.columnconfigure(0, weight=5, minsize=380)
        self._cols.columnconfigure(1, weight=3, minsize=260)
        self._cols.columnconfigure(2, weight=3, minsize=260)

        # Col 1 — Formulário
        col1 = tk.Frame(self._cols, bg=CINZA_FUNDO)
        col1.grid(row=0, column=0, sticky="nsew", padx=(0, pad))
        self._montar_formulario(col1)

        # Col 2 — Resumo + Jornada
        col2 = tk.Frame(self._cols, bg=CINZA_FUNDO)
        col2.grid(row=0, column=1, sticky="nsew", padx=(0, pad))
        self._montar_resumo(col2)
        self._montar_jornada(col2)

        # Col 3 — Analytics
        col3 = tk.Frame(self._cols, bg=CINZA_FUNDO)
        col3.grid(row=0, column=2, sticky="nsew")
        self._montar_funil(col3)
        self._montar_pizza(col3)

        # Rodapé
        rodape = tk.Frame(frame, bg=CINZA_FUNDO)
        rodape.pack(fill="x", padx=pad, pady=(0, pad))
        rodape.columnconfigure(0, weight=3)
        rodape.columnconfigure(1, weight=2)
        self._montar_leads_recentes(rodape)
        self._montar_resumo_geral(rodape)

    # ── Col 1: Formulário ──────────────────────────────────────────────────
    def _montar_formulario(self, pai):
        c = card(pai)
        c.pack(fill="both", expand=True)

        # Título do card
        topo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=12)
        topo.pack(fill="x")
        label_titulo(topo, "Cadastro do Aluno (Lead)", bg=BRANCO).pack(side="left")
        separador(c, cor=CINZA_BORDA).pack(fill="x")

        corpo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        corpo.pack(fill="both", expand=True)

        def linha(texto, col_span=1):
            tk.Label(corpo, text=texto, font=FONTE_PEQUENA_B,
                     fg=TEXTO_LABEL, bg=BRANCO).pack(anchor="w", pady=(8,2))

        def campo_row(*labels_and_widgets):
            """Agrupa campos em grid horizontal."""
            r = tk.Frame(corpo, bg=BRANCO)
            r.pack(fill="x", pady=2)
            for i, (lbl, wid) in enumerate(labels_and_widgets):
                sub = tk.Frame(r, bg=BRANCO)
                sub.pack(side="left", fill="x", expand=True,
                         padx=(0, 8) if i < len(labels_and_widgets)-1 else 0)
                tk.Label(sub, text=lbl, font=FONTE_PEQUENA_B,
                         fg=TEXTO_LABEL, bg=BRANCO).pack(anchor="w", pady=(0,2))
                wid(sub).pack(fill="x", ipady=4)

        # ─ Nome completo ─
        campo_row(
            ("Nome completo *",
             lambda p: self._campo(p, "João da Silva")),
        )
        # ─ Nasc / CPF ─
        campo_row(
            ("Data de nascimento",
             lambda p: self._campo(p, "15/04/2002")),
            ("CPF",
             lambda p: self._campo(p, "123.456.789-01")),
        )
        # ─ Email / Tel ─
        campo_row(
            ("E-mail *",
             lambda p: self._campo(p, "joao.silva@email.com")),
            ("Telefone / WhatsApp",
             lambda p: self._campo(p, "(11) 98765-4321")),
        )
        # ─ Endereço ─
        campo_row(
            ("Endereço",
             lambda p: self._campo(p, "Rua das Flores, 123")),
        )
        # ─ Cidade / Estado ─
        campo_row(
            ("Cidade",
             lambda p: self._campo(p, "São Paulo")),
            ("Estado",
             lambda p: self._combo_estado(p)),
        )
        # ─ Curso / Como Conheceu / Captador ─
        campo_row(
            ("Curso de interesse *",
             lambda p: self._combo_gen(p, ["Marketing Digital",
                                           "Design Gráfico",
                                           "Tráfego Pago",
                                           "Social Media"])),
        )
        campo_row(
            ("Como conheceu?",
             lambda p: self._combo_gen(p, ["Instagram", "Indicação",
                                           "Google Ads", "Facebook Ads",
                                           "Site / Orgânico"])),
            ("Captador (vendedor) *",
             lambda p: self._combo_gen(p, ["Maria Santos", "Carlos Lima",
                                           "João Pereira"])),
        )
        # ─ Observações ─
        tk.Label(corpo, text="Observações", font=FONTE_PEQUENA_B,
                 fg=TEXTO_LABEL, bg=BRANCO).pack(anchor="w", pady=(8,2))
        obs = tk.Text(corpo, height=3, font=FONTE_NORMAL,
                      bg=BRANCO, fg=CINZA_ESCURO,
                      relief="flat",
                      highlightbackground=CINZA_BORDA,
                      highlightthickness=1,
                      insertbackground=AZUL_PRIMARIO,
                      wrap="word")
        obs.insert("1.0", "Interessado no curso noturno.")
        obs.config(fg="#AABBD4")
        obs.pack(fill="x", pady=(0, 4))

        # ─ Botões ─
        separador(c).pack(fill="x", pady=(8,0))
        f_btn = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        f_btn.pack(fill="x")
        botao_secundario(f_btn, "Cancelar").pack(side="left", padx=(0,8))
        botao_primario(f_btn, "💾  Salvar Lead",
                       width=16).pack(side="left")

    def _campo(self, pai, placeholder):
        e = tk.Entry(pai, font=FONTE_NORMAL,
                     bg=BRANCO, fg=CINZA_ESCURO,
                     relief="flat",
                     highlightbackground=CINZA_BORDA,
                     highlightcolor=AZUL_PRIMARIO,
                     highlightthickness=1,
                     insertbackground=AZUL_PRIMARIO)
        e.insert(0, placeholder)
        e.config(fg=CINZA_ESCURO)
        return e

    def _combo_gen(self, pai, opcoes):
        style = ttk.Style()
        style.configure("C.TCombobox",
                        fieldbackground=BRANCO,
                        background=BRANCO,
                        foreground=CINZA_ESCURO)
        cb = ttk.Combobox(pai, values=opcoes, font=FONTE_NORMAL,
                          state="readonly", style="C.TCombobox")
        cb.current(0)
        return cb

    def _combo_estado(self, pai):
        estados = ["SP","RJ","MG","BA","PR","RS","SC","GO","PE",
                   "CE","PA","AM","MA","ES","RN","PB","MT","MS",
                   "AL","SE","RO","TO","AC","AP","RR","DF","PI"]
        return self._combo_gen(pai, estados)

    # ── Col 2: Resumo Lead ─────────────────────────────────────────────────
    def _montar_resumo(self, pai):
        c = card(pai)
        c.pack(fill="x", pady=(0, 10))

        topo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        topo.pack(fill="x")
        label_secao(topo, "Resumo do Lead", bg=BRANCO).pack(side="left")
        separador(c).pack(fill="x")

        corpo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        corpo.pack(fill="x")

        def linha_info(icone, chave, valor, cor_valor=CINZA_ESCURO):
            r = tk.Frame(corpo, bg=BRANCO)
            r.pack(fill="x", pady=4)
            tk.Label(r, text=icone, font=("Segoe UI", 10),
                     bg=BRANCO, fg=CINZA_TEXTO, width=2).pack(side="left")
            tk.Label(r, text=chave, font=FONTE_PEQUENA,
                     bg=BRANCO, fg=CINZA_TEXTO, width=14,
                     anchor="w").pack(side="left")
            if chave == "Status atual:":
                b = tk.Label(r, text=valor,
                             font=("Segoe UI", 8, "bold"),
                             bg=AZUL_PRIMARIO, fg=BRANCO,
                             padx=8, pady=2)
                b.pack(side="left")
            else:
                tk.Label(r, text=valor, font=FONTE_PEQUENA_B,
                         bg=BRANCO, fg=cor_valor).pack(side="left")

        linha_info("📌", "Status atual:",     "LEAD")
        linha_info("📅", "Data do cadastro:", "24/05/2024 14:30")
        linha_info("👤", "Captador:",         "Maria Santos")
        linha_info("📚", "Curso de interesse:", "Marketing Digital")

    # ── Col 2: Jornada ─────────────────────────────────────────────────────
    def _montar_jornada(self, pai):
        c = card(pai)
        c.pack(fill="both", expand=True)

        topo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        topo.pack(fill="x")
        label_secao(topo, "Jornada do Aluno", bg=BRANCO).pack(side="left")
        separador(c).pack(fill="x")

        corpo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=8)
        corpo.pack(fill="both", expand=True)

        for num, titulo, desc, feito in JORNADA:
            f = tk.Frame(corpo, bg=BRANCO)
            f.pack(fill="x", pady=3)

            # Coluna esquerda: número + linha
            col_num = tk.Frame(f, bg=BRANCO, width=32)
            col_num.pack(side="left", fill="y")
            col_num.pack_propagate(False)

            cor_circulo = AZUL_PRIMARIO if feito else "#CBD5E0"
            cor_txt_num = BRANCO if feito else CINZA_TEXTO

            cv = tk.Canvas(col_num, width=26, height=26,
                           bg=BRANCO, highlightthickness=0)
            cv.pack(pady=(2,0))
            cv.create_oval(2, 2, 24, 24,
                           fill=cor_circulo, outline="")
            cv.create_text(13, 13, text=str(num),
                           font=("Segoe UI", 8, "bold"),
                           fill=cor_txt_num)

            # Linha conectora (exceto último)
            if num < len(JORNADA):
                tk.Frame(col_num, bg="#CBD5E0", width=2,
                         height=20).pack()

            # Coluna direita: texto
            col_txt = tk.Frame(f, bg=BRANCO, padx=6)
            col_txt.pack(side="left", fill="x", expand=True)

            cor_titulo = TEXTO_HEADER if feito else CINZA_TEXTO
            tk.Label(col_txt, text=titulo,
                     font=FONTE_PEQUENA_B,
                     fg=cor_titulo, bg=BRANCO,
                     anchor="w").pack(fill="x")
            tk.Label(col_txt, text=desc,
                     font=("Segoe UI", 8),
                     fg=CINZA_TEXTO, bg=BRANCO,
                     anchor="w").pack(fill="x")

    # ── Col 3: Funil ───────────────────────────────────────────────────────
    def _montar_funil(self, pai):
        c = card(pai)
        c.pack(fill="x", pady=(0, 10))

        topo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        topo.pack(fill="x")
        label_secao(topo, "Funil de Origem", bg=BRANCO).pack(side="left")
        tk.Label(topo, text="Período: Este mês ▾",
                 font=FONTE_PEQUENA, fg=CINZA_TEXTO,
                 bg=BRANCO).pack(side="right")
        separador(c).pack(fill="x")

        corpo = tk.Frame(c, bg=BRANCO, padx=8, pady=8)
        corpo.pack(fill="x")
        funil = GraficoFunil(corpo, largura=270, altura=230)
        funil.pack(pady=4)

    # ── Col 3: Pizza ───────────────────────────────────────────────────────
    def _montar_pizza(self, pai):
        c = card(pai)
        c.pack(fill="x")

        topo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        topo.pack(fill="x")
        label_secao(topo, "Origem dos Leads", bg=BRANCO).pack(side="left")
        separador(c).pack(fill="x")

        corpo = tk.Frame(c, bg=BRANCO, padx=8, pady=8)
        corpo.pack(fill="x")
        pizza = GraficoPizza(corpo, tam=100)
        pizza.pack(pady=4)

        link = tk.Label(c, text="Ver relatório completo →",
                        font=FONTE_PEQUENA_B,
                        fg=AZUL_PRIMARIO, bg=BRANCO,
                        cursor="hand2")
        link.pack(anchor="e", padx=PAD_CARD, pady=(0, 10))

    # ── Rodapé: Leads recentes ─────────────────────────────────────────────
    def _montar_leads_recentes(self, pai):
        c = card(pai)
        c.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        topo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        topo.pack(fill="x")
        label_secao(topo, "Leads Recentes", bg=BRANCO).pack(side="left")
        tk.Label(topo, text="Ver todos os leads →",
                 font=FONTE_PEQUENA_B, fg=AZUL_PRIMARIO,
                 bg=BRANCO, cursor="hand2").pack(side="right")
        separador(c).pack(fill="x")

        # Cabeçalho da tabela
        cols = ["Nome", "Curso", "Captador", "Status", "Data"]
        cabecalho = tk.Frame(c, bg="#F7F9FC", padx=PAD_CARD, pady=6)
        cabecalho.pack(fill="x")
        larguras = [18, 16, 14, 10, 11]
        for lbl, w in zip(cols, larguras):
            tk.Label(cabecalho, text=lbl,
                     font=FONTE_PEQUENA_B,
                     fg=CINZA_TEXTO, bg="#F7F9FC",
                     width=w, anchor="w").pack(side="left")

        separador(c).pack(fill="x")

        # Linhas
        for i, (nome, curso, capt, status, data) in enumerate(LEADS_RECENTES):
            cor_linha = BRANCO if i % 2 == 0 else "#FAFBFD"
            linha = tk.Frame(c, bg=cor_linha, padx=PAD_CARD, pady=8)
            linha.pack(fill="x")

            def _hover_on(e, f=linha, cor=cor_linha):
                f.config(bg="#EBF0FB")
                for w in f.winfo_children():
                    try: w.config(bg="#EBF0FB")
                    except: pass

            def _hover_off(e, f=linha, cor=cor_linha):
                f.config(bg=cor)
                for w in f.winfo_children():
                    try: w.config(bg=cor)
                    except: pass

            linha.bind("<Enter>", _hover_on)
            linha.bind("<Leave>", _hover_off)

            dados = [(nome, larguras[0]), (curso, larguras[1]),
                     (capt, larguras[2])]
            for txt, w in dados:
                tk.Label(linha, text=txt, font=FONTE_PEQUENA,
                         fg=CINZA_ESCURO, bg=cor_linha,
                         width=w, anchor="w").pack(side="left")

            # Badge status
            bg_s, fg_s = COR_STATUS.get(status, (CINZA_TEXTO, BRANCO))
            badge_f = tk.Frame(linha, bg=cor_linha, width=larguras[3]*7)
            badge_f.pack(side="left")
            badge_f.pack_propagate(False)
            tk.Label(badge_f, text=status,
                     font=("Segoe UI", 7, "bold"),
                     bg=bg_s, fg=fg_s,
                     padx=5, pady=2).pack(anchor="w")

            tk.Label(linha, text=data, font=FONTE_PEQUENA,
                     fg=CINZA_TEXTO, bg=cor_linha,
                     width=larguras[4], anchor="w").pack(side="left")

    # ── Rodapé: Resumo geral ───────────────────────────────────────────────
    def _montar_resumo_geral(self, pai):
        c = card(pai)
        c.grid(row=0, column=1, sticky="nsew")

        topo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=10)
        topo.pack(fill="x")
        label_secao(topo, "Resumo Geral", bg=BRANCO).pack(side="left")
        separador(c).pack(fill="x")

        corpo = tk.Frame(c, bg=BRANCO, padx=PAD_CARD, pady=12)
        corpo.pack(fill="both", expand=True)

        metricas = [
            ("👥", "Leads\n(este mês)",       "132",       AZUL_PRIMARIO),
            ("🛒", "Vendas\n(este mês)",       "38",        VERDE),
            ("💰", "Faturamento\n(este mês)",  "R$ 18.750", LARANJA),
            ("📈", "Taxa de\nConversão",        "28,8%",     ROXO),
        ]

        # Grid 2x2
        for i, (icone, rotulo, valor, cor) in enumerate(metricas):
            linha_ = i // 2
            col_  = i % 2
            f = tk.Frame(corpo, bg=AZUL_CLARO, padx=12, pady=10)
            f.grid(row=linha_, column=col_,
                   padx=4, pady=4, sticky="nsew")
            corpo.columnconfigure(col_, weight=1)
            corpo.rowconfigure(linha_, weight=1)

            topo_m = tk.Frame(f, bg=AZUL_CLARO)
            topo_m.pack(fill="x")
            tk.Label(topo_m, text=icone, font=("Segoe UI", 16),
                     bg=AZUL_CLARO).pack(side="left")

            tk.Label(f, text=valor,
                     font=("Segoe UI", 18, "bold"),
                     fg=cor, bg=AZUL_CLARO).pack(anchor="w")
            tk.Label(f, text=rotulo,
                     font=("Segoe UI", 8),
                     fg=CINZA_TEXTO, bg=AZUL_CLARO,
                     justify="left").pack(anchor="w")

    # ── Animação de entrada ────────────────────────────────────────────────
    def _animar_entrada(self):
        """Fade-in suave do conteúdo ao carregar."""
        self._alpha = 0.0
        self._fade_step()

    def _fade_step(self):
        if self._alpha < 1.0:
            self._alpha = min(1.0, self._alpha + 0.08)
            try:
                self.winfo_toplevel().attributes("-alpha", self._alpha)
            except Exception:
                pass
            self.after(20, self._fade_step)
