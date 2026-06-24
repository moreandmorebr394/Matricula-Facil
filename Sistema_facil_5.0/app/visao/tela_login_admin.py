"""
Tela de Login Administrativo.
Acesso fixo - apenas o administrador configurado em
configuracoes_admin/credenciais_admin.py pode entrar.

Sem opcao de cadastro, recuperacao automatica nem primeiro acesso.
Apos login valido, fecha tudo e abre o dashboard.
"""
import tkinter as tk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    AMARELO_VIBRANTE, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.logo_sf import LogoSF, definir_icone_janela
from componentes.botao_moderno import BotaoModerno
from componentes.campo_entrada import CampoEntrada
from componentes.notificacao import Notificacao
from componentes.cursor_customizado import aplicar_cursor_global

from app.controlador import controlador_autenticacao


class TelaLoginAdmin(tk.Toplevel):
    """Janela exclusiva de login do administrador."""

    def __init__(self, master=None):
        super().__init__(master)
        self.master_ref = master

        self.title("Sistema Facil - Acesso Administrativo")
        self.geometry("520x620")
        self.configure(bg=BRANCO)
        self.resizable(False, False)
        self._centralizar(520, 620)
        definir_icone_janela(self)

        # Garante que fica sobre o login normal
        try:
            self.transient(master)
            self.grab_set()
        except tk.TclError:
            pass

        self._construir()

        self.after(100, lambda: aplicar_cursor_global(self))

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
                self.after(15, lambda: self._fade_in(min(1.0, alfa + 0.1)))
        except tk.TclError:
            pass

    def _construir(self):
        # Header escuro
        header = tk.Canvas(self, bg=AZUL_ESCURO,
                           highlightthickness=0, bd=0)
        header.pack(fill="x")
        header.configure(height=180)

        # Inicializa o fundo animado
        from componentes.painel_animado import FundoAnimado
        self.fundo_animado = FundoAnimado(header, num_particulas=15)
        self.logo_frame_visual = None

        # Gradiente
        def desenhar_grad(evento=None):
            header.delete("estatico")
            w = header.winfo_width() or 520

            # Decoracoes
            header.create_oval(-50, -50, 100, 100,
                               fill="#2D3F66", outline="", tags="estatico")
            header.create_oval(w-100, 100, w+80, 280,
                               fill="#2D3F66", outline="", tags="estatico")

            # Linhas decorativas
            for x in range(0, w, 22):
                header.create_oval(x, 160, x+3, 163,
                                   fill=AMARELO_VIBRANTE, outline="", tags="estatico")

            # Evita vazamento de memória
            if self.logo_frame_visual:
                try:
                    self.logo_frame_visual.destroy()
                except Exception:
                    pass

            # Logo
            self.logo_frame_visual = tk.Frame(header, bg=AZUL_ESCURO)
            header.create_window(w//2, 60, window=self.logo_frame_visual, tags="estatico")
            LogoSF(self.logo_frame_visual, tamanho=70, cor_fundo=AZUL_ESCURO).pack()

            # Cadeado e titulo
            header.create_text(w//2, 120, text="\U0001f510",
                               font=("Segoe UI Emoji", 22), tags="estatico")
            header.create_text(w//2, 150, text="Acesso Administrativo",
                               fill=BRANCO, font=(FONTE_TITULO, 16, "bold"), tags="estatico")

        header.bind("<Configure>", desenhar_grad, add="+")
        self.after(20, desenhar_grad)

        # Corpo
        corpo = tk.Frame(self, bg=BRANCO_GELO)
        corpo.pack(fill="both", expand=True)

        container = tk.Frame(corpo, bg=BRANCO_GELO)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container,
                 text="Area Restrita",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(pady=(0, 4))

        tk.Label(container,
                 text="Apenas o administrador autorizado pode acessar.\n"
                      "Insira suas credenciais institucionais.",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO,
                 justify="center").pack(pady=(0, 18))

        # Email
        self.campo_email = CampoEntrada(
            container, label="EMAIL INSTITUCIONAL",
            icone="✉",
            largura=380, cor_fundo_pai=BRANCO_GELO
        )
        self.campo_email.pack(pady=6)

        # Senha
        self.campo_senha = CampoEntrada(
            container, label="SENHA",
            icone="🔒", senha=True,
            largura=380, cor_fundo_pai=BRANCO_GELO
        )
        self.campo_senha.pack(pady=6)

        # Botao
        BotaoModerno(
            container, texto="🔓  Entrar como Administrador",
            comando=self._fazer_login,
            largura=380, altura=46,
            cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
            fonte_tamanho=11, cor_fundo=BRANCO_GELO
        ).pack(pady=(18, 8))

        # Aviso seguranca
        aviso = tk.Frame(container, bg="#FFF7E6",
                         highlightbackground=AMARELO_VIBRANTE,
                         highlightthickness=1)
        aviso.pack(fill="x", pady=(8, 4))
        tk.Label(
            aviso,
            text="⚠ Tentativas invalidas sao registradas no sistema.",
            font=(FONTE_TEXTO, 8, "italic"),
            fg="#7A5C00", bg="#FFF7E6", padx=10, pady=8
        ).pack()

        # Voltar
        link_voltar = tk.Label(
            container, text="← Voltar ao login normal",
            font=(FONTE_TEXTO, 9, "underline"),
            fg=CINZA_MEDIO, bg=BRANCO_GELO, cursor="hand2"
        )
        link_voltar.pack(pady=(14, 0))
        link_voltar.bind("<Button-1>", lambda e: self.destroy())

        # Enter no campo de senha submete
        self.campo_senha.entry.bind(
            "<Return>", lambda e: self._fazer_login()
        )

    def _fazer_login(self):
        email = self.campo_email.obter()
        senha = self.campo_senha.obter()

        sucesso, msg = controlador_autenticacao.autenticar_admin(
            email, senha
        )

        if not sucesso:
            Notificacao.erro(self, msg)
            return

        Notificacao.sucesso(self, msg)
        self.after(800, self._abrir_dashboard)

    def _abrir_dashboard(self):
        from app.visao.tela_dashboard import TelaDashboard

        # Fecha esta janela e o login normal
        try:
            if self.master_ref:
                self.master_ref.destroy()
        except tk.TclError:
            pass

        try:
            self.destroy()
        except tk.TclError:
            pass

        # Procura e fecha qualquer outra janela aberta exceto dashboard
        raiz_atual = None
        try:
            raiz_atual = tk._default_root
            if raiz_atual:
                raiz_atual.withdraw()
        except Exception:
            pass

        TelaDashboard(master=raiz_atual)
