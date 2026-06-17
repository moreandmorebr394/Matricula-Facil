"""
Tela de Login - Acesso para alunos e visitantes.
Layout dividido em duas colunas (visual a esquerda, formulario a direita).

Tambem possui link discreto "Acesso Administrativo" que abre a tela de
login fixo do administrador.
"""
import tkinter as tk
from tkinter import messagebox

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    AMARELO_DOURADO, AMARELO_VIBRANTE, CINZA_MEDIO, CINZA_ESCURO,
    PRETO_TEXTO, FONTE_TITULO, FONTE_TEXTO, FONTE_BOTAO,
    TAM_TITULO_GRANDE, TAM_SUBTITULO
)
from componentes.logo_sf import LogoSF
from componentes.botao_moderno import BotaoModerno
from componentes.campo_entrada import CampoEntrada
from componentes.notificacao import Notificacao
from componentes.cursor_customizado import aplicar_cursor_global

from app.controlador import controlador_autenticacao


class TelaLogin(tk.Toplevel):
    """Janela de Login (visitantes e alunos)."""

    def __init__(self, master=None, ao_voltar=None):
        super().__init__(master)
        self.master_ref = master
        self.ao_voltar = ao_voltar

        self.title("Sistema Facil - Entrar")
        self.geometry("1100x680")
        self.configure(bg=BRANCO)
        self.resizable(False, False)

        # Centraliza
        self._centralizar(1100, 680)

        # Layout 50/50
        self._construir_lado_visual()
        self._construir_lado_formulario()

        # Cursor
        self.after(100, lambda: aplicar_cursor_global(self))

        # Animacao fade-in da janela
        try:
            self.attributes("-alpha", 0.0)
            self._fade_in(0.0)
        except tk.TclError:
            pass

    def _centralizar(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _fade_in(self, alfa):
        try:
            self.attributes("-alpha", alfa)
            if alfa < 1.0:
                self.after(15, lambda: self._fade_in(min(1.0, alfa + 0.08)))
        except tk.TclError:
            pass

    # ============ LADO ESQUERDO (VISUAL) ============
    def _construir_lado_visual(self):
        canvas = tk.Canvas(
            self, width=550, height=680,
            bg=AZUL_PRIMARIO, highlightthickness=0, bd=0
        )
        canvas.place(x=0, y=0, width=550, height=680)

        # Gradiente sutil (linhas progressivas)
        for i in range(680):
            ratio = i / 680
            r = int(60 + ratio * 20)
            g = int(80 + ratio * 25)
            b = int(125 + ratio * 30)
            cor = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, 550, i, fill=cor)

        # Formas geometricas decorativas
        canvas.create_oval(
            -100, -100, 200, 200,
            fill=AZUL_HOVER, outline=""
        )
        canvas.create_oval(
            400, 500, 700, 800,
            fill=AZUL_HOVER, outline=""
        )
        canvas.create_oval(
            420, -50, 620, 150,
            outline=AMARELO_VIBRANTE, width=3, fill=""
        )

        # Linhas pontilhadas decorativas
        for i in range(0, 550, 30):
            canvas.create_oval(i, 350, i + 4, 354, fill=AMARELO_VIBRANTE,
                               outline="")

        # Logo grande centralizado
        logo_frame = tk.Frame(canvas, bg=AZUL_PRIMARIO)
        logo_frame.place(relx=0.5, y=130, anchor="center")
        LogoSF(logo_frame, tamanho=110, cor_fundo=AZUL_PRIMARIO).pack()

        # Texto principal
        canvas.create_text(
            275, 290,
            text="Bem-vindo de volta\nao seu futuro",
            fill=BRANCO,
            font=(FONTE_TITULO, 26, "bold"),
            justify="center"
        )

        canvas.create_text(
            275, 380,
            text="Continue sua jornada de aprendizado\ncom facilidade e seguranca.",
            fill="#D5DCE8",
            font=(FONTE_TEXTO, 12),
            justify="center"
        )

        # Card decorativo (mockup de aluno estudando)
        card_x, card_y = 275, 510
        canvas.create_rectangle(
            card_x - 130, card_y - 60, card_x + 130, card_y + 60,
            fill=BRANCO, outline=""
        )
        # "Foto" estilizada
        canvas.create_oval(
            card_x - 110, card_y - 40, card_x - 50, card_y + 20,
            fill=AMARELO_VIBRANTE, outline=""
        )
        canvas.create_text(
            card_x - 80, card_y - 10,
            text="🎓", fill=AZUL_ESCURO, font=("Segoe UI Emoji", 26)
        )
        # Linhas representando texto
        canvas.create_rectangle(card_x - 30, card_y - 30,
                                card_x + 110, card_y - 22,
                                fill=AZUL_PRIMARIO, outline="")
        canvas.create_rectangle(card_x - 30, card_y - 12,
                                card_x + 90, card_y - 5,
                                fill="#C5CDD9", outline="")
        canvas.create_rectangle(card_x - 30, card_y + 5,
                                card_x + 100, card_y + 12,
                                fill="#C5CDD9", outline="")
        canvas.create_rectangle(card_x - 30, card_y + 22,
                                card_x + 70, card_y + 29,
                                fill=AMARELO_VIBRANTE, outline="")

        # Particulas decorativas
        for px, py in [(80, 600), (480, 90), (50, 80), (490, 600), (140, 460)]:
            canvas.create_oval(
                px, py, px + 8, py + 8,
                fill=AMARELO_VIBRANTE, outline=""
            )

        # Texto rodape
        canvas.create_text(
            275, 640,
            text="© 2025 Sistema Facil • Plataforma Educacional",
            fill="#9AA3B5", font=(FONTE_TEXTO, 9)
        )

    # ============ LADO DIREITO (FORMULARIO) ============
    def _construir_lado_formulario(self):
        frame_form = tk.Frame(self, bg=BRANCO_GELO)
        frame_form.place(x=550, y=0, width=550, height=680)

        # Container central
        container = tk.Frame(frame_form, bg=BRANCO_GELO)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo pequeno
        topo = tk.Frame(container, bg=BRANCO_GELO)
        topo.pack(pady=(0, 12))
        LogoSF(topo, tamanho=56, cor_fundo=BRANCO_GELO).pack()

        # Titulo
        tk.Label(
            container, text="Entrar",
            font=(FONTE_TITULO, 26, "bold"),
            fg=AZUL_ESCURO, bg=BRANCO_GELO
        ).pack(pady=(2, 4))

        tk.Label(
            container, text="Acesse sua conta no Sistema Facil",
            font=(FONTE_TEXTO, 11),
            fg=CINZA_ESCURO, bg=BRANCO_GELO
        ).pack(pady=(0, 22))

        # Campos
        self.campo_email = CampoEntrada(
            container, label="EMAIL",
            icone="✉",
            largura=380,
            cor_fundo_pai=BRANCO_GELO
        )
        self.campo_email.pack(pady=8)

        self.campo_senha = CampoEntrada(
            container, label="SENHA",
            icone="🔒",
            senha=True,
            largura=380,
            cor_fundo_pai=BRANCO_GELO
        )
        self.campo_senha.pack(pady=8)

        # Linha de checkbox + esqueceu senha
        linha_opcoes = tk.Frame(container, bg=BRANCO_GELO)
        linha_opcoes.pack(fill="x", pady=(8, 4))

        self.lembrar_var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(
            linha_opcoes, text="Lembrar de mim",
            variable=self.lembrar_var,
            font=(FONTE_TEXTO, 9), fg=CINZA_ESCURO, bg=BRANCO_GELO,
            activebackground=BRANCO_GELO, selectcolor=BRANCO,
            cursor="hand2", bd=0, highlightthickness=0
        )
        chk.pack(side="left")

        link_esqueceu = tk.Label(
            linha_opcoes, text="Esqueceu a senha?",
            font=(FONTE_TEXTO, 9, "underline"),
            fg=AZUL_PRIMARIO, bg=BRANCO_GELO, cursor="hand2"
        )
        link_esqueceu.pack(side="right")
        link_esqueceu.bind("<Button-1>", self._abrir_recuperacao)

        # Botao Entrar
        btn_entrar = BotaoModerno(
            container, texto="Entrar", comando=self._fazer_login,
            largura=380, altura=46,
            cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
            fonte_tamanho=12,
            cor_fundo=BRANCO_GELO
        )
        btn_entrar.pack(pady=(18, 8))

        # Bind Enter no campo de senha
        self.campo_senha.entry.bind(
            "<Return>", lambda e: self._fazer_login()
        )

        # Separador OU
        linha_sep = tk.Frame(container, bg=BRANCO_GELO)
        linha_sep.pack(fill="x", pady=8)
        tk.Frame(linha_sep, bg="#D5DCE8", height=1).pack(
            side="left", fill="x", expand=True, padx=10, pady=(8, 0)
        )
        tk.Label(linha_sep, text="OU", font=(FONTE_TEXTO, 9, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO_GELO).pack(side="left")
        tk.Frame(linha_sep, bg="#D5DCE8", height=1).pack(
            side="left", fill="x", expand=True, padx=10, pady=(8, 0)
        )

        # Botao Google
        btn_google = BotaoModerno(
            container, texto="🔍   Entrar com Google",
            comando=self._login_google,
            largura=380, altura=44,
            cor_normal=BRANCO, cor_hover="#F0F0F0",
            cor_texto=PRETO_TEXTO,
            fonte_tamanho=11,
            cor_fundo=BRANCO_GELO
        )
        btn_google.pack(pady=4)

        # Link de cadastro
        linha_cadastro = tk.Frame(container, bg=BRANCO_GELO)
        linha_cadastro.pack(pady=(18, 6))
        tk.Label(linha_cadastro, text="Nao tem uma conta?",
                 font=(FONTE_TEXTO, 10), fg=CINZA_ESCURO,
                 bg=BRANCO_GELO).pack(side="left")
        link_cad = tk.Label(linha_cadastro, text="  Cadastre-se",
                            font=(FONTE_TEXTO, 10, "bold underline"),
                            fg=AZUL_PRIMARIO, bg=BRANCO_GELO, cursor="hand2")
        link_cad.pack(side="left")
        link_cad.bind("<Button-1>", self._abrir_registro)

        # Acesso administrativo (discreto)
        link_admin = tk.Label(
            container, text="🔐 Acesso Administrativo",
            font=(FONTE_TEXTO, 9, "italic"),
            fg=CINZA_MEDIO, bg=BRANCO_GELO, cursor="hand2"
        )
        link_admin.pack(pady=(20, 0))
        link_admin.bind("<Button-1>", self._abrir_login_admin)

        # Hover no link admin
        def hover_admin_in(_):
            link_admin.configure(fg=AZUL_PRIMARIO,
                                 font=(FONTE_TEXTO, 9, "italic underline"))
        def hover_admin_out(_):
            link_admin.configure(fg=CINZA_MEDIO,
                                 font=(FONTE_TEXTO, 9, "italic"))
        link_admin.bind("<Enter>", hover_admin_in)
        link_admin.bind("<Leave>", hover_admin_out)

    # ============ ACOES ============
    def _fazer_login(self):
        email = self.campo_email.obter()
        senha = self.campo_senha.obter()

        sucesso, msg, dados = controlador_autenticacao.autenticar_usuario(
            email, senha
        )

        if not sucesso:
            Notificacao.erro(self, msg)
            return

        Notificacao.sucesso(self, msg)
        # Apos login, abre area do aluno/visitante
        self.after(800, lambda: self._abrir_area_aluno(dados))

    def _abrir_area_aluno(self, dados):
        from app.visao.tela_area_aluno import TelaAreaAluno

        # Fecha esta janela
        self.destroy()
        # Tambem fecha a tela inicial
        if self.master_ref:
            try:
                self.master_ref.withdraw()
            except tk.TclError:
                pass

        TelaAreaAluno(usuario=dados, master=self.master_ref)

    def _abrir_registro(self, _=None):
        from app.visao.tela_registro import TelaRegistro
        self.destroy()
        TelaRegistro(master=self.master_ref, ao_voltar=self.ao_voltar)

    def _abrir_login_admin(self, _=None):
        from app.visao.tela_login_admin import TelaLoginAdmin
        TelaLoginAdmin(master=self)

    def _abrir_recuperacao(self, _=None):
        Notificacao.info(
            self,
            "Funcionalidade em breve. Contate o administrador para resetar."
        )

    def _login_google(self):
        Notificacao.info(
            self,
            "Login com Google sera ativado quando o OAuth for configurado."
        )
