"""
Pagina Inicial do Sistema Facil - vitrine institucional.

Vista por visitantes antes de logar. Apresenta cursos, beneficios,
informacoes institucionais e botoes para login/cadastro.
"""
import tkinter as tk

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
        menu.pack(side="left", expand=True)

        for item in ["Inicio", "Cursos", "Sobre", "Beneficios", "Contato"]:
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
                     lambda e, i=item: Notificacao.info(self, f"Secao: {i}"))

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

        # Construindo cada secao
        self._secao_banner()
        self._secao_estatisticas()
        self._secao_cursos()
        self._secao_beneficios()
        self._secao_diferenciais()
        self._secao_cta()
        self._secao_rodape()

    # ============ SECOES ============
    def _secao_banner(self):
        """Banner principal com chamada para acao."""
        banner = tk.Canvas(self.conteudo, height=460, bg=AZUL_PRIMARIO,
                           highlightthickness=0, bd=0)
        banner.pack(fill="x")

        # Gradiente adaptativo
        def desenhar_gradiente(evento=None):
            banner.delete("gradiente")
            larg = banner.winfo_width() or 1400
            for i in range(460):
                ratio = i / 460
                r = int(60 + ratio * 25)
                g2 = int(80 + ratio * 30)
                b = int(125 + ratio * 35)
                cor = f"#{r:02x}{g2:02x}{b:02x}"
                banner.create_line(0, i, larg, i, fill=cor, tags="gradiente")

        banner.bind("<Configure>", desenhar_gradiente)
        self.after(10, desenhar_gradiente)

        # Formas decorativas
        banner.create_oval(-150, -150, 250, 250,
                           fill=AZUL_HOVER, outline="")
        banner.create_oval(900, 250, 1300, 600,
                           fill=AZUL_HOVER, outline="")

        # Linha pontilhada amarela
        for x in range(0, 1200, 30):
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
        botoes_frame = tk.Frame(banner, bg=AZUL_PRIMARIO)
        banner.create_window(80, 360, anchor="nw", window=botoes_frame)

        BotaoModerno(botoes_frame, texto="🎓  Inscreva-se",
                     comando=self._abrir_registro,
                     largura=180, altura=48,
                     cor_normal=AMARELO_VIBRANTE, cor_hover="#D4A800",
                     cor_texto=AZUL_ESCURO,
                     fonte_tamanho=11,
                     cor_fundo=AZUL_PRIMARIO).pack(side="left", padx=4)

        BotaoModerno(botoes_frame, texto="Saiba mais",
                     comando=lambda: Notificacao.info(
                         self, "Role a pagina para conhecer nossos cursos"),
                     largura=160, altura=48,
                     cor_normal=BRANCO, cor_hover="#E8E8E8",
                     cor_texto=AZUL_ESCURO,
                     fonte_tamanho=11,
                     cor_fundo=AZUL_PRIMARIO).pack(side="left", padx=4)

        # Card mockup (lado direito)
        cx, cy = 920, 230
        # Card sombra
        banner.create_rectangle(cx - 145, cy - 115, cx + 155, cy + 145,
                                fill="#2D3F66", outline="")
        # Card
        banner.create_rectangle(cx - 150, cy - 120, cx + 150, cy + 140,
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
        for link in ["Inicio", "Cursos", "Sobre nos", "Contato", "FAQ"]:
            tk.Label(col2, text=link, font=(FONTE_TEXTO, 9),
                     fg="#D5DCE8", bg=AZUL_ESCURO,
                     cursor="hand2").pack(anchor="w", pady=2)

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
