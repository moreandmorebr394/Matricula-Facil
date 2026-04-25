# ============================================================
# telas/login.py — Tela de Login
# ============================================================
import tkinter as tk
from configuracoes import *
from componentes.widgets import CampoInput, BotaoPrincipal, LinkClicavel, AvisoLabel
from componentes.animacoes import FormasGeometricas, LinhasPontilhadas


class TelaLogin(tk.Frame):
    """Tela de login com visual à esquerda e formulário à direita (invertido)."""

    def __init__(self, master, app, logo_img):
        super().__init__(master, bg=AZUL_ESCURO)
        self.app = app
        self.logo_img = logo_img
        self.campos = {}
        self._construir()

    def _construir(self):
        # ── Container principal ──
        container = tk.Frame(self, bg=AZUL_ESCURO, padx=8, pady=8)
        container.pack(fill="both", expand=True)

        # ── Lado Esquerdo — Visual (invertido) ──
        self.lado_esq = tk.Frame(container, bg=AZUL_MEDIO, width=LARGURA_JANELA // 2)
        self.lado_esq.pack(side="left", fill="both", expand=True)
        self.lado_esq.pack_propagate(False)

        self.canvas_visual = tk.Canvas(
            self.lado_esq, bg=AZUL_MEDIO, highlightthickness=0
        )
        self.canvas_visual.pack(fill="both", expand=True)

        self.lado_esq.after(100, self._iniciar_visual)

        # ── Lado Direito — Formulário ──
        self.lado_dir = tk.Frame(container, bg=OFF_WHITE, width=LARGURA_JANELA // 2)
        self.lado_dir.pack(side="right", fill="both", expand=True)
        self.lado_dir.pack_propagate(False)

        frame_form = tk.Frame(self.lado_dir, bg=OFF_WHITE, padx=40, pady=40)
        frame_form.pack(fill="both", expand=True)

        # Logo
        if self.logo_img:
            lbl_logo = tk.Label(frame_form, image=self.logo_img, bg=OFF_WHITE)
            lbl_logo.pack(anchor="center", pady=(10, 15))

        # Título
        tk.Label(
            frame_form, text=TEXTOS["login"]["titulo"],
            font=(FONTE_FAMILIA, FONTE_TITULO, "bold"),
            fg=AZUL_ESCURO, bg=OFF_WHITE, justify="center"
        ).pack(anchor="center")

        # Subtítulo
        tk.Label(
            frame_form, text=TEXTOS["login"]["subtitulo"],
            font=(FONTE_FAMILIA, FONTE_SUBTITULO),
            fg=CINZA_TEXTO, bg=OFF_WHITE
        ).pack(anchor="center", pady=(0, 20))

        # ── Campos ──
        campos_config = [
            ("email", "Email ou Usuário", "✉", ""),
            ("senha", "Senha", "🔒", "●"),
            ("telefone", "Número de telefone (opcional)", "📱", ""),
        ]

        for nome, placeholder, icone, show in campos_config:
            campo = CampoInput(
                frame_form, placeholder=placeholder,
                icone=icone, mostrar=show
            )
            campo.pack(fill="x")
            self.campos[nome] = campo

        # ── Botão Entrar ──
        BotaoPrincipal(
            frame_form, texto=TEXTOS["login"]["botao"],
            comando=self._entrar, largura=380, altura=44
        ).pack(pady=(20, 10))

        # ── Link Esqueceu Senha ──
        LinkClicavel(
            frame_form, texto=TEXTOS["login"]["link_esqueceu"],
            comando=self._esqueceu_senha
        ).pack(pady=(5, 3))

        # ── Link Cadastre-se ──
        frame_cadastro = tk.Frame(frame_form, bg=OFF_WHITE)
        frame_cadastro.pack(pady=(3, 3))

        tk.Label(
            frame_cadastro, text=TEXTOS["login"]["link_principal"],
            font=(FONTE_FAMILIA, FONTE_LINK), fg=CINZA_TEXTO, bg=OFF_WHITE
        ).pack(side="left")

        LinkClicavel(
            frame_cadastro, texto=" " + TEXTOS["login"]["link_acao"],
            comando=lambda: self.app.mostrar_tela("registro"),
            negrito=True
        ).pack(side="left")

        # ── Link Google ──
        self._criar_botao_google(frame_form)

    def _criar_botao_google(self, parent):
        """Cria um botão estilizado 'Entrar com Google'."""
        frame_google = tk.Frame(parent, bg=OFF_WHITE)
        frame_google.pack(pady=(10, 0))

        # Separador
        sep_frame = tk.Frame(frame_google, bg=OFF_WHITE)
        sep_frame.pack(fill="x", pady=(0, 10))
        tk.Frame(sep_frame, bg=CINZA_CLARO, height=1).pack(side="left", fill="x", expand=True)
        tk.Label(
            sep_frame, text="  ou  ", font=(FONTE_FAMILIA, 10),
            fg=CINZA_TEXTO, bg=OFF_WHITE
        ).pack(side="left")
        tk.Frame(sep_frame, bg=CINZA_CLARO, height=1).pack(side="left", fill="x", expand=True)

        # Botão Google
        btn_google = tk.Canvas(
            frame_google, width=380, height=40,
            bg=OFF_WHITE, highlightthickness=0
        )
        btn_google.pack()

        # Desenhar botão com borda
        r = 10
        w, h = 380, 40
        # Borda
        btn_google.create_rectangle(1, 1, w - 1, h - 1, outline=CINZA_CLARO, width=2)
        # Texto
        btn_google.create_text(
            w // 2, h // 2, text="🌐  Entrar com Google",
            font=(FONTE_FAMILIA, 12), fill=AZUL_ESCURO
        )

        btn_google.bind("<Enter>", lambda e: btn_google.config(cursor="hand2"))
        btn_google.bind("<Button-1>", lambda e: self._login_google())

    def _iniciar_visual(self):
        self.lado_esq.update_idletasks()
        w = self.lado_esq.winfo_width()
        h = self.lado_esq.winfo_height()

        if w < 10:
            w = LARGURA_JANELA // 2
        if h < 10:
            h = ALTURA_JANELA

        # Formas flutuantes
        self.formas = FormasGeometricas(self.canvas_visual, w, h)

        # Linhas pontilhadas
        self.linhas = LinhasPontilhadas(self.canvas_visual, w, h)

        # Texto principal
        self.canvas_visual.create_text(
            w // 2, h * 0.35,
            text=TEXTOS["login"]["frase_visual"],
            font=(FONTE_FAMILIA, FONTE_FRASE_GRANDE, "bold"),
            fill=BRANCO, justify="center", width=w - 60
        )

        # Subtexto
        self.canvas_visual.create_text(
            w // 2, h * 0.60,
            text=TEXTOS["login"]["subtexto_visual"],
            font=(FONTE_FAMILIA, FONTE_SUBTEXTO),
            fill=DOURADO_CLARO, justify="center", width=w - 60
        )

        # Elementos decorativos extras (mais premium)
        self._adicionar_decoracoes(w, h)

    def _adicionar_decoracoes(self, w, h):
        """Adiciona elementos decorativos extras no visual do login."""
        # Retângulos dourados decorativos
        for pos in [(w * 0.1, h * 0.15, 18), (w * 0.85, h * 0.8, 22), (w * 0.15, h * 0.85, 14)]:
            x, y, tam = pos
            self.canvas_visual.create_rectangle(
                x, y, x + tam, y + tam,
                fill=DOURADO, outline=""
            )

    def _entrar(self):
        """Validação básica dos campos de login."""
        email = self.campos["email"].obter_valor()
        senha = self.campos["senha"].obter_valor()

        erros = []
        if not email:
            erros.append("Email ou usuário é obrigatório")
        if not senha:
            erros.append("Senha é obrigatória")

        if erros:
            from tkinter import messagebox
            messagebox.showwarning("Atenção", "\n".join(erros))
        else:
            from tkinter import messagebox
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")

    def _esqueceu_senha(self):
        from tkinter import messagebox
        messagebox.showinfo(
            "Recuperar Senha",
            "Um email de recuperação será enviado para o endereço cadastrado."
        )

    def _login_google(self):
        from tkinter import messagebox
        messagebox.showinfo(
            "Google Login",
            "Redirecionando para autenticação Google..."
        )

    def destruir_animacoes(self):
        if hasattr(self, "formas"):
            self.formas.parar()
        if hasattr(self, "linhas"):
            self.linhas.parar()
