"""
Pagina Inicial do Sistema Facil - vitrine institucional.

Vista por visitantes antes de logar. Apresenta cursos, beneficios,
informacoes institucionais e botoes para login/cadastro.
"""
import tkinter as tk
import os
from PIL import Image, ImageTk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, AZUL_CLARO,
    BRANCO, BRANCO_GELO, CINZA_FUNDO, CINZA_CLARO, CINZA_MEDIO,
    CINZA_ESCURO, PRETO_TEXTO,
    AMARELO_VIBRANTE, AMARELO_DOURADO,
    VERDE_SUCESSO, ROXO_DESTAQUE, ROSA_DESTAQUE, LARANJA_ALERTA,
    FONTE_TITULO, FONTE_TEXTO, FONTE_BOTAO
)
from componentes.logo_sf import LogoSF, definir_icone_janela
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from componentes.cursor_customizado import aplicar_cursor_global

from app.controlador.listas_constantes import CURSOS


class TelaPaginaInicial(tk.Tk):
    """Janela raiz do sistema - pagina inicial para visitantes."""

    def __init__(self):
        super().__init__()

        self.title("Sistema Facil - Educacao que Transforma")
        self.configure(bg=BRANCO)
        self.minsize(1000, 660)
        definir_icone_janela(self)

        # Maximiza a janela (preenche a tela toda)
        self.state("zoomed")

        # Header fixo
        self._construir_header()

        # Area scrollable do conteudo
        self._construir_conteudo()

        # Cursor global
        self.after(150, lambda: aplicar_cursor_global(self))

        # Efeito fade-in suave
        self.attributes("-alpha", 0.0)
        def _fade():
            try:
                atual = self.attributes("-alpha")
                if atual < 1.0:
                    self.attributes("-alpha", min(1.0, atual + 0.08))
                    self.after(15, _fade)
            except Exception:
                pass
        self.after(10, _fade)

    def _centralizar(self, w, h):
        """Centraliza a janela na tela (mantido para compatibilidade)."""
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _construir_header(self):
        """Header fixo no topo com logo, menu e botoes."""
        header = tk.Frame(self, bg=BRANCO, height=70,
                          highlightbackground=CINZA_CLARO,
                          highlightthickness=1)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Logo + nome
        esquerda = tk.Frame(header, bg=BRANCO)
        esquerda.pack(side="left", padx=24)

        LogoSF(esquerda, tamanho=44, cor_fundo=BRANCO).pack(side="left")

        nome_frame = tk.Frame(esquerda, bg=BRANCO)
        nome_frame.pack(side="left", padx=10)
        tk.Label(nome_frame, text="Sistema Facil",
                 font=(FONTE_TITULO, 14, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Label(nome_frame, text="EDUCACAO QUE TRANSFORMA",
                 font=(FONTE_TEXTO, 7, "bold"),
                 fg=AMARELO_VIBRANTE, bg=BRANCO).pack(anchor="w")

        # Menu central
        menu = tk.Frame(header, bg=BRANCO)
        menu.place(relx=0.5, rely=0.5, anchor="center")

        for item in ["Inicio", "Cursos", "Sobre"]:
            lbl = tk.Label(menu, text=item,
                           font=(FONTE_TEXTO, 10, "bold"),
                           fg=PRETO_TEXTO, bg=BRANCO,
                           cursor="hand2", padx=14, pady=8)
            lbl.pack(side="left")

            def hover_in(e, l=lbl):
                l.configure(fg=AZUL_PRIMARIO)
            def hover_out(e, l=lbl):
                l.configure(fg=PRETO_TEXTO)
            lbl.bind("<Enter>", hover_in)
            lbl.bind("<Leave>", hover_out)
            lbl.bind("<Button-1>",
                     lambda e, i=item: self._navegar_para(i))

        # Botoes login/cadastro
        direita = tk.Frame(header, bg=BRANCO)
        direita.pack(side="right", padx=24)

        BotaoModerno(direita, texto="Entrar",
                     comando=self._abrir_login,
                     largura=110, altura=40,
                     cor_normal=BRANCO, cor_hover=CINZA_FUNDO,
                     cor_texto=AZUL_PRIMARIO,
                     fonte_tamanho=10, cor_fundo=BRANCO).pack(side="left",
                                                              padx=4)

        BotaoModerno(direita, texto="Cadastre-se",
                     comando=self._abrir_registro,
                     largura=130, altura=40,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     fonte_tamanho=10, cor_fundo=BRANCO).pack(side="left",
                                                              padx=4)

    def _construir_conteudo(self):
        """Conteudo scrollavel."""
        self.canvas_principal = tk.Canvas(self, bg=BRANCO,
                                          highlightthickness=0, bd=0)
        self.canvas_principal.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self, orient="vertical",
                                 command=self.canvas_principal.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas_principal.configure(yscrollcommand=scrollbar.set)

        # Frame interno - largura se adapta ao canvas
        self.conteudo = tk.Frame(self.canvas_principal, bg=BRANCO)
        self._win_id = self.canvas_principal.create_window(
            (0, 0), window=self.conteudo, anchor="nw"
        )

        def ao_redimensionar(_=None):
            self.canvas_principal.configure(
                scrollregion=self.canvas_principal.bbox("all")
            )
        self.conteudo.bind("<Configure>", ao_redimensionar)

        # Ajusta largura do frame interno ao tamanho do canvas
        def ao_redimensionar_canvas(evento):
            self.canvas_principal.itemconfig(
                self._win_id, width=evento.width
            )
        self.canvas_principal.bind("<Configure>", ao_redimensionar_canvas)

        # Permite scroll com roda do mouse
        def ao_rolar(evento):
            self.canvas_principal.yview_scroll(
                int(-1 * (evento.delta / 120)), "units"
            )
        self.canvas_principal.bind_all("<MouseWheel>", ao_rolar)

        # Inicializa com a página Início por padrão
        self._carregar_pagina_inicio()

    # ============ SECOES ============
    def _secao_banner(self):
        """Banner principal com imagem estetica e chamada para acao."""
        banner = tk.Canvas(self.conteudo, height=460, bg=AZUL_PRIMARIO,
                           highlightthickness=0, bd=0)
        banner.pack(fill="x")

        # Inicializa o fundo animado
        from componentes.painel_animado import FundoAnimado, criar_retangulo_arredondado
        self.fundo_animado_banner = FundoAnimado(banner, num_particulas=35)

        # Formas decorativas outline apenas (para não cobrir a imagem do banner)
        banner.create_oval(-150, -150, 250, 250,
                           fill="", outline=AZUL_CLARO, width=2)
        banner.create_oval(900, 250, 1300, 600,
                           fill="", outline=AZUL_CLARO, width=2)

        # Linha pontilhada amarela decorativa
        for x in range(0, 1400, 35):
            banner.create_oval(x, 220, x + 5, 225,
                               fill=AMARELO_VIBRANTE, outline="")

        # Texto principal (lado esquerdo)
        banner.create_text(80, 130, anchor="nw",
                           text="Educacao que",
                           fill=BRANCO,
                           font=(FONTE_TITULO, 38, "bold"))
        banner.create_text(80, 180, anchor="nw",
                           text="transforma vidas.",
                           fill=AMARELO_VIBRANTE,
                           font=(FONTE_TITULO, 38, "bold italic"))

        banner.create_text(80, 260, anchor="nw",
                           text="Cursos tecnicos, profissionalizantes\n"
                                "e graduacao com qualidade reconhecida.",
                           fill="#D5DCE8",
                           font=(FONTE_TEXTO, 13))

        # Botoes
        botoes_frame = tk.Frame(banner, bg=AZUL_ESCURO)
        banner.create_window(80, 360, anchor="nw", window=botoes_frame)

        BotaoModerno(botoes_frame, texto="🎓  Inscreva-se",
                     comando=self._abrir_registro,
                     largura=180, altura=48,
                     cor_normal=AMARELO_VIBRANTE, cor_hover="#D4A800",
                     cor_texto=AZUL_ESCURO,
                     fonte_tamanho=11,
                     cor_fundo=AZUL_ESCURO).pack(side="left", padx=4)

        BotaoModerno(botoes_frame, texto="Saiba mais",
                     comando=lambda: Notificacao.info(
                         self, "Conheca nossos cursos nas abas superiores!"),
                     largura=160, altura=48,
                     cor_normal=BRANCO, cor_hover="#E8E8E8",
                     cor_texto=AZUL_ESCURO,
                     fonte_tamanho=11,
                     cor_fundo=AZUL_ESCURO).pack(side="left", padx=4)

        # Card mockup (lado direito) arredondado
        cx, cy = 920, 230
        # Card sombra
        criar_retangulo_arredondado(banner, cx - 145, cy - 115, cx + 155, cy + 145, raio=20,
                                    fill="#0D1A3D", outline="")
        # Card
        criar_retangulo_arredondado(banner, cx - 150, cy - 120, cx + 150, cy + 140, raio=20,
                                    fill=BRANCO, outline="")

        # Avatar
        banner.create_oval(cx - 130, cy - 100, cx - 60, cy - 30,
                           fill=AMARELO_VIBRANTE, outline="")
        banner.create_text(cx - 95, cy - 65, text="👨‍🎓",
                           font=("Segoe UI Emoji", 28))

        # Texto card
        banner.create_text(cx - 50, cy - 90, anchor="nw",
                           text="Pedro Silva",
                           fill=AZUL_ESCURO,
                           font=(FONTE_TEXTO, 11, "bold"))
        banner.create_text(cx - 50, cy - 70, anchor="nw",
                           text="Tec. Enfermagem",
                           fill=CINZA_ESCURO,
                           font=(FONTE_TEXTO, 9))

        # Estrelas
        banner.create_text(cx - 50, cy - 45, anchor="nw",
                           text="⭐⭐⭐⭐⭐",
                           font=("Segoe UI Emoji", 11))

        # Quote
        banner.create_text(cx, cy + 30, anchor="center",
                           text='"O Sistema Facil abriu portas\n'
                                'para minha carreira!"',
                           fill=AZUL_ESCURO,
                           font=(FONTE_TEXTO, 10, "italic"),
                           justify="center", width=270)

        # Decoracao card
        banner.create_rectangle(cx - 120, cy + 95, cx + 120, cy + 100,
                                fill=AMARELO_VIBRANTE, outline="")
        banner.create_text(cx, cy + 115, text="CERTIFICADO RECONHECIDO",
                           fill=AZUL_ESCURO,
                           font=(FONTE_TEXTO, 8, "bold"))

    def _secao_estatisticas(self):
        secao = tk.Frame(self.conteudo, bg=BRANCO_GELO, pady=40)
        secao.pack(fill="x")

        container = tk.Frame(secao, bg=BRANCO_GELO)
        container.pack()

        stats = [
            ("10K+", "Alunos formados", AZUL_PRIMARIO),
            ("50+", "Cursos disponiveis", AMARELO_VIBRANTE),
            ("98%", "Empregabilidade", VERDE_SUCESSO),
            ("15+", "Anos de tradicao", ROXO_DESTAQUE),
        ]

        for valor, descricao, cor in stats:
            box = tk.Frame(container, bg=BRANCO_GELO, padx=30, pady=10)
            box.pack(side="left")
            tk.Label(box, text=valor, font=(FONTE_TITULO, 30, "bold"),
                     fg=cor, bg=BRANCO_GELO).pack()
            tk.Label(box, text=descricao, font=(FONTE_TEXTO, 10),
                     fg=CINZA_ESCURO, bg=BRANCO_GELO).pack()

    def _secao_cursos(self):
        secao = tk.Frame(self.conteudo, bg=BRANCO, pady=50)
        secao.pack(fill="x")

        # Titulo
        tk.Label(secao, text="Nossos Cursos",
                 font=(FONTE_TITULO, 26, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack()
        tk.Label(secao,
                 text="Cursos planejados para o mercado de trabalho atual",
                 font=(FONTE_TEXTO, 11),
                 fg=CINZA_ESCURO, bg=BRANCO).pack(pady=(4, 26))

        # Grid de cursos
        grid = tk.Frame(secao, bg=BRANCO)
        grid.pack()

        icones_cursos = {
            "Tecnico em Enfermagem": ("⚕", VERMELHO := "#EF4444"),
            "Tecnico em Seguranca do Trabalho": ("🦺", LARANJA_ALERTA),
            "Tecnico em Informatica": ("💻", AZUL_PRIMARIO),
            "Tecnico em Administracao": ("📊", VERDE_SUCESSO),
            "Tecnico em Secretaria Escolar": ("📚", ROXO_DESTAQUE),
            "Administracao": ("💼", AMARELO_VIBRANTE),
            "Bombeiro Civil": ("🚒", VERMELHO),
        }

        for indice, curso in enumerate(CURSOS):
            linha = indice // 4
            coluna = indice % 4

            icone, cor = icones_cursos.get(curso, ("🎓", AZUL_PRIMARIO))
            self._criar_card_curso(grid, curso, icone, cor, linha, coluna)

    def _criar_card_curso(self, parent, nome, icone, cor, linha, coluna):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1, width=270, height=180)
        card.grid(row=linha, column=coluna, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)

        # Faixa colorida superior
        faixa = tk.Frame(card, bg=cor, height=8)
        faixa.pack(fill="x")

        # Conteudo
        cont = tk.Frame(card, bg=BRANCO, padx=18, pady=18)
        cont.pack(fill="both", expand=True)

        # Icone
        tk.Label(cont, text=icone, font=("Segoe UI Emoji", 32),
                 bg=BRANCO).pack(anchor="w")

        # Nome
        tk.Label(cont, text=nome, font=(FONTE_TEXTO, 11, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO,
                 wraplength=230, justify="left", anchor="w").pack(
            anchor="w", pady=(8, 4)
        )

        # Duracao
        tk.Label(cont, text="📅 12 meses • Presencial",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO).pack(anchor="w")

        # Hover (muda cor da borda)
        def hover_in(_):
            card.configure(highlightbackground=cor, highlightthickness=2)
        def hover_out(_):
            card.configure(highlightbackground=CINZA_CLARO,
                           highlightthickness=1)
        card.bind("<Enter>", hover_in)
        card.bind("<Leave>", hover_out)
        cont.bind("<Enter>", hover_in)
        cont.bind("<Leave>", hover_out)
        card.configure(cursor="hand2")
        cont.configure(cursor="hand2")

        # Click
        click_handler = lambda e: Notificacao.info(
            self, f"Inscreva-se em {nome}!"
        )
        card.bind("<Button-1>", click_handler)
        cont.bind("<Button-1>", click_handler)

    def _secao_beneficios(self):
        secao = tk.Frame(self.conteudo, bg=AZUL_ESCURO, pady=60)
        secao.pack(fill="x")

        tk.Label(secao, text="Por que escolher o Sistema Facil?",
                 font=(FONTE_TITULO, 24, "bold"),
                 fg=BRANCO, bg=AZUL_ESCURO).pack()
        tk.Label(secao, text="Vantagens que fazem a diferenca",
                 font=(FONTE_TEXTO, 11),
                 fg="#9AA3B5", bg=AZUL_ESCURO).pack(pady=(4, 26))

        grid = tk.Frame(secao, bg=AZUL_ESCURO)
        grid.pack()

        beneficios = [
            ("🎓", "Certificacao\nReconhecida",
             "Diplomas validos em todo o Brasil"),
            ("👨‍🏫", "Professores\nQualificados",
             "Mestres e doutores no corpo docente"),
            ("💼", "Mercado de\nTrabalho",
             "Parcerias com empresas para estagio"),
            ("🏢", "Estrutura\nCompleta",
             "Laboratorios e bibliotecas modernas"),
        ]

        for indice, (emoji, titulo, desc) in enumerate(beneficios):
            box = tk.Frame(grid, bg=AZUL_PRIMARIO,
                           padx=22, pady=24,
                           width=240, height=200)
            box.grid(row=0, column=indice, padx=8)
            box.grid_propagate(False)

            tk.Label(box, text=emoji, font=("Segoe UI Emoji", 36),
                     bg=AZUL_PRIMARIO).pack()
            tk.Label(box, text=titulo, font=(FONTE_TEXTO, 12, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     justify="center").pack(pady=(8, 4))
            tk.Label(box, text=desc, font=(FONTE_TEXTO, 9),
                     fg="#D5DCE8", bg=AZUL_PRIMARIO,
                     wraplength=190, justify="center").pack()

    def _secao_diferenciais(self):
        secao = tk.Frame(self.conteudo, bg=BRANCO, pady=50)
        secao.pack(fill="x")

        container = tk.Frame(secao, bg=BRANCO)
        container.pack()

        # Esquerda - texto
        esq = tk.Frame(container, bg=BRANCO, padx=30)
        esq.grid(row=0, column=0, sticky="n")

        tk.Label(esq, text="📍 Nossa Missao",
                 font=(FONTE_TEXTO, 10, "bold"),
                 fg=AMARELO_VIBRANTE, bg=BRANCO).pack(anchor="w")
        tk.Label(esq, text="Educacao acessivel\ne de qualidade",
                 font=(FONTE_TITULO, 22, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO,
                 justify="left").pack(anchor="w", pady=(6, 10))
        tk.Label(esq,
                 text="O Sistema Facil acredita que toda pessoa merece\n"
                      "acesso a uma educacao transformadora. Por isso,\n"
                      "oferecemos cursos com metodologia inovadora,\n"
                      "preco justo e flexibilidade de horarios.",
                 font=(FONTE_TEXTO, 11),
                 fg=CINZA_ESCURO, bg=BRANCO,
                 justify="left").pack(anchor="w", pady=(0, 14))

        BotaoModerno(esq, texto="Conheca nossa historia",
                     comando=lambda: Notificacao.info(
                         self, "Em breve: pagina sobre nos"),
                     largura=200, altura=42,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     cor_fundo=BRANCO).pack(anchor="w")

        # Direita - card visual
        dir_frame = tk.Frame(container, bg=BRANCO, padx=30)
        dir_frame.grid(row=0, column=1, sticky="n")

        canvas_dir = tk.Canvas(dir_frame, width=420, height=320, bg=BRANCO,
                               highlightthickness=0)
        canvas_dir.pack()

        # Card 1
        canvas_dir.create_rectangle(20, 20, 220, 180,
                                    fill=AMARELO_VIBRANTE, outline="")
        canvas_dir.create_text(120, 80, text="🏆",
                               font=("Segoe UI Emoji", 50))
        canvas_dir.create_text(120, 140, text="Premio Educacao\nde Excelencia",
                               fill=AZUL_ESCURO,
                               font=(FONTE_TEXTO, 10, "bold"),
                               justify="center")

        # Card 2
        canvas_dir.create_rectangle(240, 20, 410, 130,
                                    fill=AZUL_PRIMARIO, outline="")
        canvas_dir.create_text(325, 60, text="📚",
                               font=("Segoe UI Emoji", 36))
        canvas_dir.create_text(325, 105, text="Biblioteca\nDigital",
                               fill=BRANCO,
                               font=(FONTE_TEXTO, 10, "bold"),
                               justify="center")

        # Card 3
        canvas_dir.create_rectangle(240, 150, 410, 300,
                                    fill=VERDE_SUCESSO, outline="")
        canvas_dir.create_text(325, 200, text="🌐",
                               font=("Segoe UI Emoji", 40))
        canvas_dir.create_text(325, 260, text="Plataforma\nOnline",
                               fill=BRANCO,
                               font=(FONTE_TEXTO, 10, "bold"),
                               justify="center")

        # Card 4
        canvas_dir.create_rectangle(20, 200, 220, 300,
                                    fill=ROSA_DESTAQUE, outline="")
        canvas_dir.create_text(120, 235, text="❤️",
                               font=("Segoe UI Emoji", 30))
        canvas_dir.create_text(120, 275, text="Comunidade\nAcolhedora",
                               fill=BRANCO,
                               font=(FONTE_TEXTO, 10, "bold"),
                               justify="center")

    def _secao_cta(self):
        secao = tk.Canvas(self.conteudo, height=240, bg=AMARELO_VIBRANTE,
                          highlightthickness=0)
        secao.pack(fill="x")

        # Gradiente amarelo
        for i in range(240):
            ratio = i / 240
            r = int(245 - ratio * 25)
            g = int(197 - ratio * 30)
            b = int(24 + ratio * 0)
            cor = f"#{r:02x}{g:02x}{b:02x}"
            secao.create_line(0, i, 1200, i, fill=cor)

        secao.create_text(600, 80, text="Pronto para comecar?",
                          font=(FONTE_TITULO, 28, "bold"),
                          fill=AZUL_ESCURO)
        secao.create_text(600, 125,
                          text="Faca seu cadastro agora e ganhe acesso a "
                               "todos os nossos beneficios",
                          font=(FONTE_TEXTO, 12),
                          fill=AZUL_ESCURO)

        # Botao
        btn_frame = tk.Frame(secao, bg=AMARELO_VIBRANTE)
        secao.create_window(600, 180, window=btn_frame)
        BotaoModerno(btn_frame, texto="🚀  Comecar Agora",
                     comando=self._abrir_registro,
                     largura=240, altura=50,
                     cor_normal=AZUL_ESCURO, cor_hover=AZUL_PRIMARIO,
                     fonte_tamanho=12,
                     cor_fundo=AMARELO_VIBRANTE).pack()

    def _secao_rodape(self):
        rodape = tk.Frame(self.conteudo, bg=AZUL_ESCURO, pady=40)
        rodape.pack(fill="x")

        container = tk.Frame(rodape, bg=AZUL_ESCURO)
        container.pack()

        # Coluna 1 - logo + descricao
        col1 = tk.Frame(container, bg=AZUL_ESCURO, padx=30)
        col1.grid(row=0, column=0, sticky="n")
        LogoSF(col1, tamanho=48, cor_fundo=AZUL_ESCURO).pack(anchor="w")
        tk.Label(col1, text="Sistema Facil",
                 font=(FONTE_TITULO, 14, "bold"),
                 fg=BRANCO, bg=AZUL_ESCURO).pack(anchor="w", pady=(8, 0))
        tk.Label(col1,
                 text="Educacao que transforma\nvidas e abre portas.",
                 font=(FONTE_TEXTO, 9),
                 fg="#9AA3B5", bg=AZUL_ESCURO,
                 justify="left").pack(anchor="w", pady=4)

        # Coluna 2 - links
        col2 = tk.Frame(container, bg=AZUL_ESCURO, padx=30)
        col2.grid(row=0, column=1, sticky="n")
        tk.Label(col2, text="LINKS",
                 font=(FONTE_TEXTO, 9, "bold"),
                 fg=AMARELO_VIBRANTE, bg=AZUL_ESCURO).pack(anchor="w",
                                                           pady=(0, 6))
        for link in ["Inicio", "Cursos", "Sobre"]:
            lbl = tk.Label(col2, text=link, font=(FONTE_TEXTO, 9),
                           fg="#D5DCE8", bg=AZUL_ESCURO,
                           cursor="hand2")
            lbl.pack(anchor="w", pady=2)

            def make_hover_rodape(l):
                l.bind("<Enter>", lambda e: l.configure(fg=AMARELO_VIBRANTE))
                l.bind("<Leave>", lambda e: l.configure(fg="#D5DCE8"))
            make_hover_rodape(lbl)
            lbl.bind("<Button-1>", lambda e, l=link: self._navegar_para(l))

        # Coluna 3 - contato
        col3 = tk.Frame(container, bg=AZUL_ESCURO, padx=30)
        col3.grid(row=0, column=2, sticky="n")
        tk.Label(col3, text="CONTATO",
                 font=(FONTE_TEXTO, 9, "bold"),
                 fg=AMARELO_VIBRANTE, bg=AZUL_ESCURO).pack(anchor="w",
                                                           pady=(0, 6))
        for info in [
            "📍 Belem, Para - Brasil",
            "📞 (91) 3000-0000",
            "✉ contato@sistemafacil.pa.br",
            "🕐 Seg a Sex - 8h as 18h"
        ]:
            tk.Label(col3, text=info, font=(FONTE_TEXTO, 9),
                     fg="#D5DCE8", bg=AZUL_ESCURO).pack(anchor="w", pady=2)

        # Coluna 4 - redes
        col4 = tk.Frame(container, bg=AZUL_ESCURO, padx=30)
        col4.grid(row=0, column=3, sticky="n")
        tk.Label(col4, text="SIGA-NOS",
                 font=(FONTE_TEXTO, 9, "bold"),
                 fg=AMARELO_VIBRANTE, bg=AZUL_ESCURO).pack(anchor="w",
                                                           pady=(0, 6))
        redes_frame = tk.Frame(col4, bg=AZUL_ESCURO)
        redes_frame.pack(anchor="w")
        for emoji in ["📘", "📸", "🐦", "💼", "🎵"]:
            tk.Label(redes_frame, text=emoji,
                     font=("Segoe UI Emoji", 16),
                     bg=AZUL_PRIMARIO, fg=BRANCO,
                     width=2, padx=4, pady=4,
                     cursor="hand2").pack(side="left", padx=2)

        # Linha de copyright
        linha = tk.Frame(rodape, bg="#0D1A3D", height=1)
        linha.pack(fill="x", pady=(20, 8))

        tk.Label(rodape,
                 text="© 2025 Sistema Facil • Todos os direitos reservados",
                 font=(FONTE_TEXTO, 8),
                 fg="#9AA3B5", bg=AZUL_ESCURO).pack()

    # ============ ACOES ============
    def _abrir_login(self):
        from app.visao.tela_login import TelaLogin
        TelaLogin(master=self)

    def _abrir_registro(self):
        from app.visao.tela_registro import TelaRegistro
        TelaRegistro(master=self)

    # ============ NAVEGACAO E MULTIPAGINAS ============
    def _navegar_para(self, pagina):
        """Direciona a navegação para a página solicitada com transição de fade."""
        def acao_carregar():
            if pagina == "Inicio":
                self._carregar_pagina_inicio()
            elif pagina == "Cursos":
                self._carregar_pagina_cursos()
            elif pagina == "Sobre":
                self._carregar_pagina_sobre()
            elif pagina == "Beneficios":
                self._carregar_pagina_beneficios()
            elif pagina == "Contato":
                self._carregar_pagina_contato()

        self._transicao_fade(acao_carregar)

    def _transicao_fade(self, acao_reconstrucao):
        """Aplica um efeito de cortina deslizante fluida nas transições de página (sem piscar)."""
        try:
            w_total = self.winfo_width() or 1000
            h_total = self.winfo_height() or 700
            h_curtain = h_total - 70

            cobertura = tk.Frame(self, bg=BRANCO)
            cobertura.place(x=0, y=70, width=w_total, height=h_curtain)
            self.update_idletasks()

            # Executa a limpeza e recriação por baixo
            self._limpar_conteudo()
            acao_reconstrucao()
            self.canvas_principal.yview_moveto(0)

            # Animação de subida da cortina (slide-down wipe)
            y_inicial = 70
            passo = 0
            total_passos = 12

            def deslizar():
                nonlocal passo
                passo += 1
                if passo <= total_passos:
                    ratio = passo / total_passos
                    y_atual = int(y_inicial + ratio * h_curtain)
                    h_atual = int(h_curtain * (1.0 - ratio))
                    cobertura.place_configure(y=y_atual, height=h_atual)
                    self.after(10, deslizar)
                else:
                    cobertura.destroy()

            self.after(10, deslizar)
        except Exception:
            self._limpar_conteudo()
            acao_reconstrucao()

    def _limpar_conteudo(self):
        """Remove todos os componentes atualmente carregados na tela."""
        for widget in self.conteudo.winfo_children():
            widget.destroy()

    def _carregar_pagina_inicio(self):
        """Carrega a exibição padrão da página inicial."""
        self._secao_banner()
        self._secao_estatisticas()
        self._secao_cursos()
        self._secao_diferenciais()
        self._secao_cta()
        self._secao_rodape()

    def _carregar_pagina_cursos(self):
        """Página dedicada de cursos com banner estético e busca dinâmica."""
        banner = tk.Canvas(self.conteudo, height=300, bg=AZUL_PRIMARIO,
                           highlightthickness=0, bd=0)
        banner.pack(fill="x")

        caminho_banner = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "courses_banner.png"
        )
        try:
            self.img_orig_courses = Image.open(caminho_banner)
        except Exception as e:
            print(f"Erro ao carregar courses_banner.png: {e}")
            self.img_orig_courses = None

        def redesenhar_courses_banner(evento=None):
            banner.delete("bg_courses")
            w = banner.winfo_width() or 1200
            h = 300
            if self.img_orig_courses and w > 0:
                img_larg, img_alt = self.img_orig_courses.size
                proporcao_img = img_larg / img_alt
                proporcao_canvas = w / h
                if proporcao_canvas > proporcao_img:
                    nova_larg = w
                    nova_alt = int(w / proporcao_img)
                else:
                    nova_alt = h
                    nova_larg = int(h * proporcao_img)
                img_resized = self.img_orig_courses.resize((nova_larg, nova_alt), Image.Resampling.LANCZOS)
                x_cortar = (nova_larg - w) // 2
                y_cortar = (nova_alt - h) // 2
                img_crop = img_resized.crop((x_cortar, y_cortar, x_cortar + w, y_cortar + h))
                
                overlay_img = img_crop.convert("RGBA")
                overlay_color = Image.new("RGBA", (w, h), (17, 34, 80, 180))
                img_mesclada = Image.alpha_composite(overlay_img, overlay_color).convert("RGB")
                
                self.img_tk_courses = ImageTk.PhotoImage(img_mesclada)
                banner.create_image(0, 0, image=self.img_tk_courses, anchor="nw", tags="bg_courses")
                banner.tag_lower("bg_courses")

        banner.bind("<Configure>", redesenhar_courses_banner)
        self.after(10, redesenhar_courses_banner)

        banner.create_text(80, 100, anchor="nw",
                           text="Nossos Cursos",
                           fill=BRANCO,
                           font=(FONTE_TITULO, 32, "bold"))
        banner.create_text(80, 155, anchor="nw",
                           text="Capacitação profissional de alto nível com certificação reconhecida.",
                           fill="#D5DCE8",
                           font=(FONTE_TEXTO, 12))

        search_frame = tk.Frame(self.conteudo, bg=BRANCO, pady=30)
        search_frame.pack(fill="x", padx=80)

        search_label = tk.Label(search_frame, text="🔍 Buscar curso:",
                                font=(FONTE_TEXTO, 11, "bold"),
                                fg=AZUL_ESCURO, bg=BRANCO)
        search_label.pack(side="left", padx=(0, 10))

        busca_var = tk.StringVar()
        entry_busca = tk.Entry(search_frame, textvariable=busca_var,
                               font=(FONTE_TEXTO, 11),
                               highlightbackground=CINZA_CLARO,
                               highlightthickness=1, bd=0, bg=BRANCO_GELO)
        entry_busca.pack(side="left", fill="x", expand=True, ipady=8, padx=5)

        grid_container = tk.Frame(self.conteudo, bg=BRANCO)
        grid_container.pack(fill="both", expand=True, padx=80, pady=(0, 40))

        icones_cursos = {
            "Tecnico em Enfermagem": ("⚕", "#EF4444"),
            "Tecnico em Seguranca do Trabalho": ("🦺", LARANJA_ALERTA),
            "Tecnico em Informatica": ("💻", AZUL_PRIMARIO),
            "Tecnico em Administracao": ("📊", VERDE_SUCESSO),
            "Tecnico em Secretaria Escolar": ("📚", ROXO_DESTAQUE),
            "Administracao": ("💼", AMARELO_VIBRANTE),
            "Bombeiro Civil": ("🚒", "#EF4444"),
        }

        def atualizar_grid(*args):
            for widget in grid_container.winfo_children():
                widget.destroy()

            query = busca_var.get().lower().strip()
            cursos_filtrados = [c for c in CURSOS if query in c.lower()]

            if not cursos_filtrados:
                lbl_no = tk.Label(grid_container, text="Nenhum curso encontrado para sua busca. 😢",
                                  font=(FONTE_TEXTO, 12, "italic"),
                                  fg=CINZA_ESCURO, bg=BRANCO, pady=40)
                lbl_no.pack()
                return

            for idx, nome in enumerate(cursos_filtrados):
                linha = idx // 3
                coluna = idx % 3
                icone, cor = icones_cursos.get(nome, ("🎓", AZUL_PRIMARIO))
                
                card = tk.Frame(grid_container, bg=BRANCO,
                                highlightbackground=CINZA_CLARO,
                                highlightthickness=1, width=320, height=200)
                card.grid(row=linha, column=coluna, padx=15, pady=15, sticky="nsew")
                card.grid_propagate(False)

                faixa = tk.Frame(card, bg=cor, height=8)
                faixa.pack(fill="x")

                cont = tk.Frame(card, bg=BRANCO, padx=20, pady=20)
                cont.pack(fill="both", expand=True)

                tk.Label(cont, text=icone, font=("Segoe UI Emoji", 32), bg=BRANCO).pack(anchor="w")
                tk.Label(cont, text=nome, font=(FONTE_TEXTO, 12, "bold"),
                         fg=AZUL_ESCURO, bg=BRANCO, wraplength=270, justify="left").pack(anchor="w", pady=(8, 4))
                
                duracao_desc = "📅 12 meses • Presencial & EAD"
                if "Graduacao" in nome or nome == "Administracao":
                    duracao_desc = "📅 4 anos • Bacharelado"
                
                tk.Label(cont, text=duracao_desc, font=(FONTE_TEXTO, 9), fg=CINZA_ESCURO, bg=BRANCO).pack(anchor="w")

                def hover_in(e, cd=card, c=cor):
                    cd.configure(highlightbackground=c, highlightthickness=2)
                def hover_out(e, cd=card):
                    cd.configure(highlightbackground=CINZA_CLARO, highlightthickness=1)
                
                card.bind("<Enter>", hover_in)
                card.bind("<Leave>", hover_out)
                cont.bind("<Enter>", hover_in)
                cont.bind("<Leave>", hover_out)
                
                card.configure(cursor="hand2")
                cont.configure(cursor="hand2")

                click_handler = lambda e, n=nome: Notificacao.info(self, f"Inscricao aberta para {n}!")
                card.bind("<Button-1>", click_handler)
                cont.bind("<Button-1>", click_handler)

        busca_var.trace_add("write", atualizar_grid)
        atualizar_grid()

        self._secao_rodape()

    def _carregar_pagina_sobre(self):
        """Página institucional "Sobre" com história, missão, visão e valores."""
        banner = tk.Canvas(self.conteudo, height=300, bg=AZUL_PRIMARIO,
                           highlightthickness=0, bd=0)
        banner.pack(fill="x")

        caminho_banner = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "about_banner.png"
        )
        try:
            self.img_orig_about = Image.open(caminho_banner)
        except Exception as e:
            print(f"Erro ao carregar about_banner.png: {e}")
            self.img_orig_about = None

        def redesenhar_about_banner(evento=None):
            banner.delete("bg_about")
            w = banner.winfo_width() or 1200
            h = 300
            if self.img_orig_about and w > 0:
                img_larg, img_alt = self.img_orig_about.size
                proporcao_img = img_larg / img_alt
                proporcao_canvas = w / h
                if proporcao_canvas > proporcao_img:
                    nova_larg = w
                    nova_alt = int(w / proporcao_img)
                else:
                    nova_alt = h
                    nova_larg = int(h * proporcao_img)
                img_resized = self.img_orig_about.resize((nova_larg, nova_alt), Image.Resampling.LANCZOS)
                x_cortar = (nova_larg - w) // 2
                y_cortar = (nova_alt - h) // 2
                img_crop = img_resized.crop((x_cortar, y_cortar, x_cortar + w, y_cortar + h))
                
                overlay_img = img_crop.convert("RGBA")
                overlay_color = Image.new("RGBA", (w, h), (17, 34, 80, 180))
                img_mesclada = Image.alpha_composite(overlay_img, overlay_color).convert("RGB")
                
                self.img_tk_about = ImageTk.PhotoImage(img_mesclada)
                banner.create_image(0, 0, image=self.img_tk_about, anchor="nw", tags="bg_about")
                banner.tag_lower("bg_about")

        banner.bind("<Configure>", redesenhar_about_banner)
        self.after(10, redesenhar_about_banner)

        banner.create_text(80, 100, anchor="nw",
                           text="Quem Somos",
                           fill=BRANCO,
                           font=(FONTE_TITULO, 32, "bold"))
        banner.create_text(80, 155, anchor="nw",
                           text="Conheça a história e os valores do Sistema Fácil.",
                           fill="#D5DCE8",
                           font=(FONTE_TEXTO, 12))

        historia_frame = tk.Frame(self.conteudo, bg=BRANCO, pady=50)
        historia_frame.pack(fill="x", padx=80)

        esq = tk.Frame(historia_frame, bg=BRANCO, padx=20)
        esq.pack(side="left", fill="both", expand=True)

        tk.Label(esq, text="Nossa História",
                 font=(FONTE_TITULO, 24, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w", pady=(0, 10))

        historia_txt = (
            "O Sistema Fácil surgiu com o propósito de facilitar a vida das pessoas e simplificar o dia a dia da "
            "área comercial. Entendemos que gerenciar vendas, clientes e turmas pode ser complexo e cansativo. "
            "Por isso, criamos uma solução amigável que unifica todas as etapas importantes do seu trabalho em um "
            "único sistema inteligente.\n\n"
            "Nosso objetivo é tornar a sua rotina mais leve, humana e produtiva, para que você possa focar no que "
            "realmente importa: o crescimento e o sucesso do seu negócio."
        )
        tk.Label(esq, text=historia_txt, font=(FONTE_TEXTO, 11),
                 fg=CINZA_ESCURO, bg=BRANCO, justify="left", wraplength=480).pack(anchor="w")

        dir_frame = tk.Frame(historia_frame, bg=BRANCO, padx=20)
        dir_frame.pack(side="right", fill="both", expand=True)

        pilares = [
            ("🎯 Missao", "Oferecer educacao profissional acessivel e de qualidade, preparando cidadaos conscientes e profissionais altamente capacitados.", AZUL_PRIMARIO),
            ("👁️ Visao", "Ser a instituicao educacional de referencia em empregabilidade e inovacao pedagogica ate 2028.", VERDE_SUCESSO),
            ("💎 Valores", "Compromisso etico, inclusao social, inovacao continua, valorizacao humana e transparencia.", AMARELO_VIBRANTE)
        ]

        for p_titulo, p_desc, cor in pilares:
            p_card = tk.Frame(dir_frame, bg=BRANCO_GELO, highlightbackground=CINZA_CLARO, highlightthickness=1, pady=12, padx=16)
            p_card.pack(fill="x", pady=6)
            
            faixa = tk.Frame(p_card, bg=cor, width=4)
            faixa.pack(side="left", fill="y")
            
            info_frame = tk.Frame(p_card, bg=BRANCO_GELO, padx=10)
            info_frame.pack(side="left", fill="both", expand=True)
            
            tk.Label(info_frame, text=p_titulo, font=(FONTE_TITULO, 12, "bold"), fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
            tk.Label(info_frame, text=p_desc, font=(FONTE_TEXTO, 9), fg=CINZA_ESCURO, bg=BRANCO_GELO, justify="left", wraplength=340).pack(anchor="w")

        test_frame = tk.Frame(self.conteudo, bg=BRANCO_GELO, pady=50)
        test_frame.pack(fill="x")

        tk.Label(test_frame, text="Depoimentos de Sucesso", font=(FONTE_TITULO, 20, "bold"), fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(pady=(0, 25))

        test_container = tk.Frame(test_frame, bg=BRANCO_GELO)
        test_container.pack()

        depoimentos = [
            ("Mariana Souza", "Enfermagem", "A estrutura pratica dos laboratorios simulados me deu toda a confianca que eu precisava para atuar nos estagios e logo conseguir meu primeiro emprego."),
            ("Rodrigo Melo", "Informatica", "Os professores sao incriveis e super conectados com o mercado. A plataforma de estudos online do Sistema Facil facilitou demais minha rotina de trabalho e estudo."),
            ("Beatriz Ramos", "Administracao", "Conclui o curso e ja fui indicada para uma vaga de estagio atraves das parcerias da escola. O Sistema Facil realmente abre portas!")
        ]

        for nome, curso, desc_txt in depoimentos:
            card = tk.Frame(test_container, bg=BRANCO, highlightbackground=CINZA_CLARO, highlightthickness=1, width=280, height=200, padx=16, pady=20)
            card.pack(side="left", padx=15)
            card.pack_propagate(False)

            tk.Label(card, text="“", font=("Georgia", 36, "italic"), fg=AMARELO_VIBRANTE, bg=BRANCO).pack(anchor="w")
            tk.Label(card, text=desc_txt, font=(FONTE_TEXTO, 9, "italic"), fg=CINZA_ESCURO, bg=BRANCO, justify="left", wraplength=240).pack(anchor="w", pady=(0, 8))
            tk.Label(card, text=nome, font=(FONTE_TEXTO, 10, "bold"), fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
            tk.Label(card, text=f"Aluna de {curso}", font=(FONTE_TEXTO, 8), fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")

        self._secao_rodape()

    def _carregar_pagina_beneficios(self):
        """Página de Benefícios detalhada, mostrando todas as vantagens."""
        banner = tk.Canvas(self.conteudo, height=300, bg=AZUL_ESCURO,
                           highlightthickness=0, bd=0)
        banner.pack(fill="x")

        def desenhar_gradiente(evento=None):
            banner.delete("grad")
            w = banner.winfo_width() or 1200
            h = 300
            for i in range(h):
                ratio = i / h
                r = int(17 + ratio * 20)
                g2 = int(34 + ratio * 25)
                b = int(80 + ratio * 30)
                cor = f"#{r:02x}{g2:02x}{b:02x}"
                banner.create_line(0, i, w, i, fill=cor, tags="grad")
            banner.tag_lower("grad")
        banner.bind("<Configure>", desenhar_gradiente)
        self.after(10, desenhar_gradiente)

        banner.create_text(80, 100, anchor="nw",
                           text="Benefícios de Estudar Conosco",
                           fill=BRANCO,
                           font=(FONTE_TITULO, 32, "bold"))
        banner.create_text(80, 155, anchor="nw",
                           text="Vantagens exclusivas que aceleram sua inserção no mercado profissional.",
                           fill="#D5DCE8",
                           font=(FONTE_TEXTO, 12))

        grid_frame = tk.Frame(self.conteudo, bg=BRANCO, pady=60)
        grid_frame.pack(fill="x", padx=80)

        beneficios = [
            ("🎓", "Certificado Valido Nacional", "Seu diploma e reconhecido em todo o territorio nacional, abrindo portas em qualquer estado do Brasil."),
            ("👨‍🏫", "Professores que Atuam no Mercado", "Corpo docente formado por profissionais experientes que trazem casos reais para dentro da sala de aula."),
            ("🏢", "Laboratorios Modernos", "Infraestrutura fisica moderna com laboratorios de informatica, enfermagem e seguranca totalmente equipados."),
            ("🌐", "Plataforma de Estudos EAD", "Acesse materiais de aula, atividades e videoaulas complementares a qualquer hora do dia ou da noite."),
            ("📚", "Biblioteca Digital Completa", "Mais de 5.000 titulos academicos, apostilas e livros tecnicos disponiveis de forma gratuita para os alunos."),
            ("💼", "Parcerias de Estagios", "Convenios com centenas de empresas locais para insercao rapida do aluno no mercado profissional."),
        ]

        for idx, (emoji, titulo, desc) in enumerate(beneficios):
            linha = idx // 2
            coluna = idx % 2

            card = tk.Frame(grid_frame, bg=BRANCO_GELO, highlightbackground=CINZA_CLARO, highlightthickness=1, padx=24, pady=24)
            card.grid(row=linha, column=coluna, padx=15, pady=15, sticky="nsew")
            
            ico_lbl = tk.Label(card, text=emoji, font=("Segoe UI Emoji", 28), bg=BRANCO_GELO)
            ico_lbl.pack(anchor="w")
            
            tit_lbl = tk.Label(card, text=titulo, font=(FONTE_TITULO, 13, "bold"), fg=AZUL_ESCURO, bg=BRANCO_GELO)
            tit_lbl.pack(anchor="w", pady=(8, 4))
            
            desc_lbl = tk.Label(card, text=desc, font=(FONTE_TEXTO, 10), fg=CINZA_ESCURO, bg=BRANCO_GELO, justify="left", wraplength=420)
            desc_lbl.pack(anchor="w")

            def hover_in(e, c=card):
                c.configure(highlightbackground=AZUL_PRIMARIO, highlightthickness=2)
            def hover_out(e, c=card):
                c.configure(highlightbackground=CINZA_CLARO, highlightthickness=1)
            
            card.bind("<Enter>", hover_in)
            card.bind("<Leave>", hover_out)
            ico_lbl.bind("<Enter>", hover_in)
            ico_lbl.bind("<Leave>", hover_out)
            tit_lbl.bind("<Enter>", hover_in)
            tit_lbl.bind("<Leave>", hover_out)
            desc_lbl.bind("<Enter>", hover_in)
            desc_lbl.bind("<Leave>", hover_out)

        cta_frame = tk.Frame(self.conteudo, bg=AMARELO_VIBRANTE, pady=40)
        cta_frame.pack(fill="x")

        tk.Label(cta_frame, text="Aproveite todos esses benefícios e mude de vida!",
                 font=(FONTE_TITULO, 16, "bold"), fg=AZUL_ESCURO, bg=AMARELO_VIBRANTE).pack()
        
        btn_c = tk.Frame(cta_frame, bg=AMARELO_VIBRANTE, pady=12)
        btn_c.pack()
        BotaoModerno(btn_c, texto="Fazer minha Inscrição",
                     comando=self._abrir_registro,
                     largura=220, altura=44,
                     cor_normal=AZUL_ESCURO, cor_hover=AZUL_PRIMARIO,
                     cor_fundo=AMARELO_VIBRANTE).pack()

        self._secao_rodape()

    def _carregar_pagina_contato(self):
        """Página de Contato com formulário de envio funcional e validações."""
        banner = tk.Canvas(self.conteudo, height=240, bg=AZUL_PRIMARIO,
                           highlightthickness=0, bd=0)
        banner.pack(fill="x")

        def desenhar_gradiente(evento=None):
            banner.delete("grad")
            w = banner.winfo_width() or 1200
            h = 240
            for i in range(h):
                ratio = i / h
                r = int(60 + ratio * 20)
                g2 = int(80 + ratio * 25)
                b = int(125 + ratio * 30)
                cor = f"#{r:02x}{g2:02x}{b:02x}"
                banner.create_line(0, i, w, i, fill=cor, tags="grad")
            banner.tag_lower("grad")
        banner.bind("<Configure>", desenhar_gradiente)
        self.after(10, desenhar_gradiente)

        banner.create_text(80, 80, anchor="nw",
                           text="Fale Conosco",
                           fill=BRANCO,
                           font=(FONTE_TITULO, 32, "bold"))
        banner.create_text(80, 135, anchor="nw",
                           text="Dúvidas, sugestões ou suporte? Nossa equipe está pronta para te atender.",
                           fill="#D5DCE8",
                           font=(FONTE_TEXTO, 12))

        contato_frame = tk.Frame(self.conteudo, bg=BRANCO, pady=50)
        contato_frame.pack(fill="x", padx=80)

        esq = tk.Frame(contato_frame, bg=BRANCO_GELO, highlightbackground=CINZA_CLARO, highlightthickness=1, padx=30, pady=30)
        esq.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(esq, text="Envie uma Mensagem", font=(FONTE_TITULO, 16, "bold"), fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w", pady=(0, 15))

        from componentes.campo_entrada import CampoEntrada
        
        self.contato_nome = CampoEntrada(esq, label="NOME COMPLETO", icone="👤", largura=380, cor_fundo_pai=BRANCO_GELO)
        self.contato_nome.pack(pady=6)

        self.contato_email = CampoEntrada(esq, label="E-MAIL", icone="✉", largura=380, cor_fundo_pai=BRANCO_GELO)
        self.contato_email.pack(pady=6)

        self.contato_assunto = CampoEntrada(esq, label="ASSUNTO", icone="📌", largura=380, cor_fundo_pai=BRANCO_GELO)
        self.contato_assunto.pack(pady=6)

        tk.Label(esq, text="MENSAGEM", font=(FONTE_TEXTO, 8, "bold"), fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w", pady=(8, 2))
        
        text_frame = tk.Frame(esq, bg=BRANCO, highlightbackground=CINZA_CLARO, highlightthickness=1)
        text_frame.pack(fill="x", pady=(0, 12))
        
        self.contato_mensagem = tk.Text(text_frame, font=(FONTE_TEXTO, 10), height=5, bd=0, bg=BRANCO, highlightthickness=0)
        self.contato_mensagem.pack(fill="both", expand=True, padx=8, pady=6)

        def enviar_contato():
            nome = self.contato_nome.obter().strip()
            email = self.contato_email.obter().strip()
            assunto = self.contato_assunto.obter().strip()
            mensagem = self.contato_mensagem.get("1.0", "end").strip()

            if not nome or not email or not assunto or not mensagem:
                Notificacao.erro(self, "Todos os campos do formulário são obrigatórios.")
                return
            
            if "@" not in email or "." not in email:
                Notificacao.erro(self, "Por favor, insira um e-mail válido.")
                return
            
            Notificacao.sucesso(self, f"Obrigado, {nome}! Sua mensagem foi enviada com sucesso.")
            self.contato_nome.entry.delete(0, "end")
            self.contato_email.entry.delete(0, "end")
            self.contato_assunto.entry.delete(0, "end")
            self.contato_mensagem.delete("1.0", "end")

        btn_enviar = BotaoModerno(esq, texto="Enviar Mensagem", comando=enviar_contato, largura=380, altura=44, cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER, cor_fundo=BRANCO_GELO)
        btn_enviar.pack(pady=10)

        dire = tk.Frame(contato_frame, bg=BRANCO)
        dire.pack(side="right", fill="both", expand=True, padx=(20, 0))

        tk.Label(dire, text="Canais de Atendimento", font=(FONTE_TITULO, 16, "bold"), fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w", pady=(0, 15))

        canais = [
            ("📍 Endereço Principal", "Av. Nazaré, 1200 - Nazaré\nBelém, PA - CEP 66035-115"),
            ("📞 Telefone Comercial", "(91) 3000-0000\nSegunda a Sexta, 8h às 18h"),
            ("✉ E-mail Institucional", "contato@sistemafacil.pa.br\nRespostas em até 24 horas úteis"),
        ]

        for titulo, desc in canais:
            c_box = tk.Frame(dire, bg=BRANCO_GELO, highlightbackground=CINZA_CLARO, highlightthickness=1, padx=16, pady=12)
            c_box.pack(fill="x", pady=6)
            tk.Label(c_box, text=titulo, font=(FONTE_TITULO, 11, "bold"), fg=AZUL_PRIMARIO, bg=BRANCO_GELO).pack(anchor="w")
            tk.Label(c_box, text=desc, font=(FONTE_TEXTO, 9), fg=CINZA_ESCURO, bg=BRANCO_GELO, justify="left").pack(anchor="w", pady=2)

        map_box = tk.Frame(dire, bg=AZUL_ESCURO, padx=20, pady=20)
        map_box.pack(fill="x", pady=(15, 0))
        
        tk.Label(map_box, text="🗺️ LOCALIZAÇÃO DO CAMPUS", font=(FONTE_TEXTO, 8, "bold"), fg=AMARELO_VIBRANTE, bg=AZUL_ESCURO).pack(anchor="w")
        tk.Label(map_box, text="Veja nosso campus no centro de Belém. Fácil acesso por transporte público e estacionamento privativo para alunos.",
                 font=(FONTE_TEXTO, 9, "italic"), fg=BRANCO, bg=AZUL_ESCURO, wraplength=340, justify="left").pack(anchor="w", pady=4)

        self._secao_rodape()
