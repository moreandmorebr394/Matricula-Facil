# ============================================================
# telas/registro.py — Tela de Registro / Cadastro
# ============================================================
import tkinter as tk
from configuracoes import *
from componentes.widgets import CampoInput, BotaoPrincipal, LinkClicavel, AvisoLabel
from componentes.animacoes import FormasGeometricas, LinhasPontilhadas


class TelaRegistro(tk.Frame):
    """Tela de registro com formulário à esquerda e visual à direita."""

    def __init__(self, master, app, logo_img):
        super().__init__(master, bg=AZUL_ESCURO)
        self.app = app
        self.logo_img = logo_img
        self.campos = {}
        self._construir()

    def _construir(self):
        # ── Container principal com "borda" arredondada ──
        container = tk.Frame(self, bg=AZUL_ESCURO, padx=8, pady=8)
        container.pack(fill="both", expand=True)

        # ── Lado Esquerdo — Formulário ──
        self.lado_esq = tk.Frame(container, bg=OFF_WHITE, width=LARGURA_JANELA // 2)
        self.lado_esq.pack(side="left", fill="both", expand=True)
        self.lado_esq.pack_propagate(False)

        frame_form = tk.Frame(self.lado_esq, bg=OFF_WHITE, padx=40, pady=25)
        frame_form.pack(fill="both", expand=True)

        # Logo
        if self.logo_img:
            lbl_logo = tk.Label(frame_form, image=self.logo_img, bg=OFF_WHITE)
            lbl_logo.pack(anchor="w", pady=(5, 10))

        # Título
        tk.Label(
            frame_form, text=TEXTOS["registro"]["titulo"],
            font=(FONTE_FAMILIA, FONTE_TITULO, "bold"),
            fg=AZUL_ESCURO, bg=OFF_WHITE, anchor="w"
        ).pack(anchor="w")

        # Subtítulo
        tk.Label(
            frame_form, text=TEXTOS["registro"]["subtitulo"],
            font=(FONTE_FAMILIA, FONTE_SUBTITULO),
            fg=CINZA_TEXTO, bg=OFF_WHITE, anchor="w"
        ).pack(anchor="w", pady=(0, 15))

        # ── Campos ──
        campos_config = [
            ("nome", "Nome completo", "👤", ""),
            ("email", "Email", "✉", ""),
            ("email2", "Repetir email", "✉", ""),
            ("senha", "Senha", "🔒", "●"),
            ("senha2", "Repetir senha", "🔒", "●"),
            ("telefone", "Número de telefone", "📱", ""),
        ]

        # Frame para dois campos lado a lado (email/repetir email)
        for nome, placeholder, icone, show in campos_config:
            campo = CampoInput(
                frame_form, placeholder=placeholder,
                icone=icone, mostrar=show
            )
            campo.pack(fill="x")
            self.campos[nome] = campo

        # ── Botão Cadastrar ──
        BotaoPrincipal(
            frame_form, texto=TEXTOS["registro"]["botao"],
            comando=self._cadastrar, largura=380, altura=44
        ).pack(pady=(15, 10))

        # ── Links ──
        frame_links = tk.Frame(frame_form, bg=OFF_WHITE)
        frame_links.pack(pady=(5, 0))

        tk.Label(
            frame_links, text=TEXTOS["registro"]["link_principal"],
            font=(FONTE_FAMILIA, FONTE_LINK), fg=CINZA_TEXTO, bg=OFF_WHITE
        ).pack(side="left")

        LinkClicavel(
            frame_links, texto=" " + TEXTOS["registro"]["link_acao"],
            comando=lambda: self.app.mostrar_tela("login"),
            negrito=True
        ).pack(side="left")

        # Aviso
        AvisoLabel(
            frame_form, texto=TEXTOS["registro"]["aviso"], tipo="info"
        ).pack(pady=(8, 0))

        # ── Lado Direito — Visual ──
        self.lado_dir = tk.Frame(container, bg=AZUL_MEDIO, width=LARGURA_JANELA // 2)
        self.lado_dir.pack(side="right", fill="both", expand=True)
        self.lado_dir.pack_propagate(False)

        # Canvas para animações
        self.canvas_visual = tk.Canvas(
            self.lado_dir, bg=AZUL_MEDIO,
            highlightthickness=0
        )
        self.canvas_visual.pack(fill="both", expand=True)

        # Formas geométricas animadas
        self.lado_dir.after(100, self._iniciar_visual)

    def _iniciar_visual(self):
        self.lado_dir.update_idletasks()
        w = self.lado_dir.winfo_width()
        h = self.lado_dir.winfo_height()

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
            text=TEXTOS["registro"]["frase_visual"],
            font=(FONTE_FAMILIA, FONTE_FRASE_GRANDE, "bold"),
            fill=BRANCO, justify="center", width=w - 60
        )

        # Subtexto
        self.canvas_visual.create_text(
            w // 2, h * 0.65,
            text=TEXTOS["registro"]["subtexto_visual"],
            font=(FONTE_FAMILIA, FONTE_SUBTEXTO),
            fill=DOURADO_CLARO, justify="center", width=w - 60
        )

    def _cadastrar(self):
        """Validação básica dos campos de registro."""
        erros = []
        nome = self.campos["nome"].obter_valor()
        email = self.campos["email"].obter_valor()
        email2 = self.campos["email2"].obter_valor()
        senha = self.campos["senha"].obter_valor()
        senha2 = self.campos["senha2"].obter_valor()
        telefone = self.campos["telefone"].obter_valor()

        if not nome:
            erros.append("Nome é obrigatório")
        if not email or "@" not in email:
            erros.append("Email inválido")
        if email != email2:
            erros.append("Os emails não coincidem")
        if not senha or len(senha) < 6:
            erros.append("Senha deve ter no mínimo 6 caracteres")
        if senha != senha2:
            erros.append("As senhas não coincidem")
        if not telefone:
            erros.append("Telefone é obrigatório")

        if erros:
            from tkinter import messagebox
            messagebox.showwarning("Atenção", "\n".join(erros))
        else:
            from tkinter import messagebox
            messagebox.showinfo(
                "Sucesso",
                f"Conta criada com sucesso!\nBem-vindo(a), {nome}!"
            )

    def destruir_animacoes(self):
        if hasattr(self, "formas"):
            self.formas.parar()
        if hasattr(self, "linhas"):
            self.linhas.parar()
