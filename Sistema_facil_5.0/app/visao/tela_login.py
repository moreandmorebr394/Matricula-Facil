"""
Tela de Login - Acesso para alunos e visitantes.
Layout dividido em duas colunas (visual a esquerda, formulario a direita).

Tambem possui link discreto "Acesso Administrativo" que abre a tela de
login fixo do administrador.
"""
import tkinter as tk
from tkinter import messagebox

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, AZUL_CLARO, BRANCO, BRANCO_GELO,
    AMARELO_DOURADO, AMARELO_VIBRANTE, CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO,
    PRETO_TEXTO, FONTE_TITULO, FONTE_TEXTO, FONTE_BOTAO,
    TAM_TITULO_GRANDE, TAM_SUBTITULO
)
from componentes.logo_sf import LogoSF, definir_icone_janela
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
        self.configure(bg=BRANCO)
        definir_icone_janela(self)

        # Maximiza a janela
        self.state("zoomed")
        self.update_idletasks()

        # Layout 50/50 responsivo
        self._construir_lado_visual()
        self._construir_lado_formulario()

        # Cursor
        self.after(100, lambda: aplicar_cursor_global(self))

    def _centralizar(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ============ LADO ESQUERDO (VISUAL) ============
    def _construir_lado_visual(self):
        from componentes.painel_animado import FundoAnimado, criar_retangulo_arredondado

        canvas = tk.Canvas(
            self, bg=AZUL_PRIMARIO, highlightthickness=0, bd=0
        )
        # Ocupa 50% da largura and 100% da altura via place relativo
        canvas.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)

        # Inicializa o fundo animado
        self.fundo_animado = FundoAnimado(canvas, num_particulas=22)
        self.logo_frame_visual = None

        def redesenhar(evento=None):
            # Limpa apenas elementos estáticos
            canvas.delete("estatico")
            w = canvas.winfo_width() or 600
            h = canvas.winfo_height() or 700

            # Card centralizado com estilo glassmorphism sólido/branco
            cx, cy = w // 2, h // 2
            card_w = 420
            card_h = 470
            
            # Card principal arredondado
            criar_retangulo_arredondado(canvas, cx - card_w//2, cy - card_h//2, cx + card_w//2, cy + card_h//2,
                                        raio=24, fill=BRANCO, outline=CINZA_CLARO, width=1, tags="estatico")
            
            # Evita vazamento de memória destruindo o frame antigo do logo
            if self.logo_frame_visual:
                try:
                    self.logo_frame_visual.destroy()
                except Exception:
                    pass
            
            # Logo grande centralizado dentro do card
            self.logo_frame_visual = tk.Frame(canvas, bg=BRANCO)
            canvas.create_window(cx, cy - card_h//2 + 80, window=self.logo_frame_visual,
                                 anchor="center", tags="estatico")
            LogoSF(self.logo_frame_visual, tamanho=90, cor_fundo=BRANCO).pack()

            # Texto principal dentro do card
            canvas.create_text(
                cx, cy - card_h//2 + 180,
                text="Bem-vindo de volta\nao seu futuro",
                fill=AZUL_ESCURO,
                font=(FONTE_TITULO, 20, "bold"),
                justify="center",
                width=380,
                tags="estatico"
            )
            canvas.create_text(
                cx, cy - card_h//2 + 250,
                text="Continue sua jornada de aprendizado\ncom facilidade e seguranca.",
                fill=CINZA_ESCURO,
                font=(FONTE_TEXTO, 11),
                justify="center",
                width=380,
                tags="estatico"
            )

            # Badge decorativo interno arredondado
            mcx = cx
            mcy = cy + 110
            criar_retangulo_arredondado(canvas, mcx-140, mcy-40, mcx+140, mcy+40, raio=12, fill=BRANCO_GELO, outline=CINZA_CLARO, width=1, tags="estatico")
            canvas.create_oval(mcx-120, mcy-25, mcx-80, mcy+15, fill=AMARELO_VIBRANTE, outline="", tags="estatico")
            canvas.create_text(mcx-100, mcy-5, text="🎓", font=("Segoe UI Emoji", 20), tags="estatico")
            canvas.create_rectangle(mcx-65, mcy-18, mcx+120, mcy-12, fill=AZUL_PRIMARIO, outline="", tags="estatico")
            canvas.create_rectangle(mcx-65, mcy-3, mcx+90, mcy+3, fill="#C5CDD9", outline="", tags="estatico")
            canvas.create_rectangle(mcx-65, mcy+12, mcx+70, mcy+18, fill=AMARELO_VIBRANTE, outline="", tags="estatico")

            # Texto rodape externo
            canvas.create_text(
                w//2, h-20,
                text="© 2025 Sistema Facil • Plataforma Educacional",
                fill=AZUL_ESCURO, font=(FONTE_TEXTO, 9, "bold"), tags="estatico"
            )

        canvas.bind("<Configure>", redesenhar, add="+")
        self.after(20, redesenhar)

    # ============ LADO DIREITO (FORMULARIO) ============
    def _construir_lado_formulario(self):
        frame_form = tk.Frame(self, bg=BRANCO_GELO)
        frame_form.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=1.0)

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
