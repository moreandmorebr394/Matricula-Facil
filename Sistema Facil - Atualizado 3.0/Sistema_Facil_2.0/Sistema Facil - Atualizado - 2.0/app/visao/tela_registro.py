"""
Tela de Registro - Cadastro de novos alunos ou visitantes.
Layout: visual a direita, formulario a esquerda.
"""
import tkinter as tk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    AMARELO_DOURADO, AMARELO_VIBRANTE, CINZA_MEDIO, CINZA_ESCURO,
    PRETO_TEXTO, FONTE_TITULO, FONTE_TEXTO, VERDE_SUCESSO
)
from componentes.logo_sf import LogoSF
from componentes.botao_moderno import BotaoModerno
from componentes.campo_entrada import CampoEntrada
from componentes.notificacao import Notificacao
from componentes.cursor_customizado import aplicar_cursor_global
from componentes.mascaras import aplicar_mascara_telefone

from app.controlador import controlador_autenticacao


class TelaRegistro(tk.Toplevel):
    """Janela de Registro/Cadastro."""

    def __init__(self, master=None, ao_voltar=None):
        super().__init__(master)
        self.master_ref = master
        self.ao_voltar = ao_voltar

        self.title("Sistema Facil - Cadastrar")
        self.configure(bg=BRANCO)

        # Maximiza a janela
        self.state("zoomed")
        self.update_idletasks()

        # Layout 50/50 (FORMULARIO ESQUERDA, VISUAL DIREITA)
        self._construir_lado_formulario()
        self._construir_lado_visual()

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
                self.after(15, lambda: self._fade_in(min(1.0, alfa + 0.08)))
        except tk.TclError:
            pass

    # ============ LADO ESQUERDO (FORMULARIO) ============
    def _construir_lado_formulario(self):
        frame = tk.Frame(self, bg=BRANCO_GELO)
        frame.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)

        container = tk.Frame(frame, bg=BRANCO_GELO)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo + titulo
        topo = tk.Frame(container, bg=BRANCO_GELO)
        topo.pack(pady=(0, 8))
        LogoSF(topo, tamanho=52, cor_fundo=BRANCO_GELO).pack()

        tk.Label(
            container, text="Crie sua conta",
            font=(FONTE_TITULO, 24, "bold"),
            fg=AZUL_ESCURO, bg=BRANCO_GELO
        ).pack(pady=(2, 2))

        tk.Label(
            container, text="Comece sua jornada no Sistema Facil",
            font=(FONTE_TEXTO, 10),
            fg=CINZA_ESCURO, bg=BRANCO_GELO
        ).pack(pady=(0, 14))

        # Tipo de conta
        tipo_frame = tk.Frame(container, bg=BRANCO_GELO)
        tipo_frame.pack(pady=(0, 10))

        tk.Label(tipo_frame, text="Tipo de conta:",
                 font=(FONTE_TEXTO, 9, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(side="left", padx=(0, 8))

        self.tipo_var = tk.StringVar(value="aluno")
        for valor, texto in [("aluno", "🎓 Aluno"), ("visitante", "👤 Visitante")]:
            rb = tk.Radiobutton(
                tipo_frame, text=texto, variable=self.tipo_var, value=valor,
                font=(FONTE_TEXTO, 10), fg=PRETO_TEXTO, bg=BRANCO_GELO,
                activebackground=BRANCO_GELO, selectcolor=BRANCO,
                cursor="hand2", bd=0, highlightthickness=0
            )
            rb.pack(side="left", padx=4)

        # Campos
        self.campo_nome = CampoEntrada(
            container, label="NOME COMPLETO", icone="👤",
            largura=380, cor_fundo_pai=BRANCO_GELO
        )
        self.campo_nome.pack(pady=4)

        self.campo_email = CampoEntrada(
            container, label="EMAIL", icone="✉",
            largura=380, cor_fundo_pai=BRANCO_GELO
        )
        self.campo_email.pack(pady=4)

        self.campo_repetir_email = CampoEntrada(
            container, label="REPETIR EMAIL", icone="✉",
            largura=380, cor_fundo_pai=BRANCO_GELO
        )
        self.campo_repetir_email.pack(pady=4)

        self.campo_senha = CampoEntrada(
            container, label="SENHA", icone="🔒", senha=True,
            largura=380, cor_fundo_pai=BRANCO_GELO
        )
        self.campo_senha.pack(pady=4)

        self.campo_repetir_senha = CampoEntrada(
            container, label="REPETIR SENHA", icone="🔒", senha=True,
            largura=380, cor_fundo_pai=BRANCO_GELO
        )
        self.campo_repetir_senha.pack(pady=4)

        self.campo_telefone = CampoEntrada(
            container, label="TELEFONE", icone="📞",
            largura=380, cor_fundo_pai=BRANCO_GELO
        )
        self.campo_telefone.pack(pady=4)
        aplicar_mascara_telefone(self.campo_telefone.entry)

        # Termos
        self.aceito_termos = tk.BooleanVar(value=False)
        chk_termos = tk.Checkbutton(
            container,
            text="Li e aceito os Termos de Uso e Politica de Privacidade",
            variable=self.aceito_termos,
            font=(FONTE_TEXTO, 9), fg=CINZA_ESCURO, bg=BRANCO_GELO,
            activebackground=BRANCO_GELO, selectcolor=BRANCO,
            cursor="hand2", bd=0, highlightthickness=0
        )
        chk_termos.pack(pady=(8, 4))

        # Botao Cadastrar
        btn_cad = BotaoModerno(
            container, texto="Cadastrar", comando=self._cadastrar,
            largura=380, altura=46,
            cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
            fonte_tamanho=12, cor_fundo=BRANCO_GELO
        )
        btn_cad.pack(pady=(8, 4))

        # Linha link login
        linha_login = tk.Frame(container, bg=BRANCO_GELO)
        linha_login.pack(pady=(8, 0))
        tk.Label(linha_login, text="Ja tem uma conta?",
                 font=(FONTE_TEXTO, 9), fg=CINZA_ESCURO,
                 bg=BRANCO_GELO).pack(side="left")
        link_login = tk.Label(
            linha_login, text="  Entrar",
            font=(FONTE_TEXTO, 9, "bold underline"),
            fg=AZUL_PRIMARIO, bg=BRANCO_GELO, cursor="hand2"
        )
        link_login.pack(side="left")
        link_login.bind("<Button-1>", self._abrir_login)

    # ============ LADO DIREITO (VISUAL) ============
    def _construir_lado_visual(self):
        canvas = tk.Canvas(
            self, bg=AZUL_PRIMARIO, highlightthickness=0, bd=0
        )
        canvas.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=1.0)

        def redesenhar(evento=None):
            canvas.delete("all")
            w = canvas.winfo_width() or 600
            h = canvas.winfo_height() or 720

            # Gradiente
            for i in range(h):
                ratio = i / h
                r = int(60 + ratio * 25)
                g2 = int(80 + ratio * 30)
                b = int(125 + ratio * 35)
                cor = f"#{r:02x}{g2:02x}{b:02x}"
                canvas.create_line(0, i, w, i, fill=cor)

            # Formas decorativas
            canvas.create_oval(-150, h-220, 200, h+130,
                               fill=AZUL_HOVER, outline="")
            canvas.create_oval(w-170, -100, w+130, 220,
                               fill=AZUL_HOVER, outline="")
            canvas.create_polygon(
                w-130, h-170, w-10, h-120, w-30, h, w-170, h-20,
                fill=AMARELO_VIBRANTE, outline="",
                stipple="gray25"
            )

            # Linha pontilhada
            for i in range(0, w, 25):
                canvas.create_oval(i, h*0.39, i+4, h*0.39+4,
                                   fill=AMARELO_VIBRANTE, outline="")

            # Logo grande
            logo_frame = tk.Frame(canvas, bg=AZUL_PRIMARIO)
            canvas.create_window(w//2, int(h*0.15), window=logo_frame,
                                 anchor="center")
            LogoSF(logo_frame, tamanho=100, cor_fundo=AZUL_PRIMARIO).pack()

            # Texto principal
            canvas.create_text(
                w//2, int(h*0.32),
                text="Seu futuro comeca\ncom uma escolha simples",
                fill=BRANCO,
                font=(FONTE_TITULO, 22, "bold"),
                justify="center"
            )
            canvas.create_text(
                w//2, int(h*0.45),
                text="Descubra novas oportunidades, desenvolva\n"
                     "habilidades e faca parte de uma comunidade\n"
                     "de aprendizado moderna.",
                fill="#D5DCE8",
                font=(FONTE_TEXTO, 11),
                justify="center"
            )

            # Cards decorativos (3 mockups de cursos)
            beneficios = [
                ("\U0001f4da", "Cursos\nTecnicos", int(w*0.23), int(h*0.64)),
                ("\U0001f393", "Certificacao\nReconhecida", int(w*0.5), int(h*0.64)),
                ("\U0001f4bc", "Mercado\nde Trabalho", int(w*0.77), int(h*0.64)),
            ]
            for emoji, texto, x, y in beneficios:
                canvas.create_rectangle(
                    x-55, y-50, x+55, y+50,
                    fill=BRANCO, outline=""
                )
                canvas.create_text(x, y-18, text=emoji,
                                   font=("Segoe UI Emoji", 26))
                canvas.create_text(x, y+22, text=texto,
                                   fill=AZUL_ESCURO,
                                   font=(FONTE_TEXTO, 9, "bold"),
                                   justify="center")

            # Particulas
            for px, py in [(60, int(h*0.8)), (w-60, int(h*0.83)),
                           (90, int(h*0.93)), (w-80, int(h*0.53))]:
                canvas.create_oval(px, py, px+6, py+6,
                                   fill=AMARELO_VIBRANTE, outline="")

            # Texto rodape
            canvas.create_text(
                w//2, h-20,
                text="\u2728 Mais de 10.000 alunos ja transformaram seu futuro",
                fill="#D5DCE8", font=(FONTE_TEXTO, 9, "italic")
            )

        canvas.bind("<Configure>", redesenhar)
        self.after(20, redesenhar)


    # ============ ACOES ============
    def _cadastrar(self):
        if not self.aceito_termos.get():
            Notificacao.aviso(self, "Voce precisa aceitar os termos de uso")
            return

        nome = self.campo_nome.obter()
        email = self.campo_email.obter()
        rep_email = self.campo_repetir_email.obter()
        senha = self.campo_senha.obter()
        rep_senha = self.campo_repetir_senha.obter()
        telefone = self.campo_telefone.obter()
        tipo = self.tipo_var.get()

        sucesso, msg, dados = controlador_autenticacao.registrar_aluno(
            nome, email, rep_email, senha, rep_senha, telefone, tipo
        )

        if not sucesso:
            Notificacao.erro(self, msg)
            return

        Notificacao.sucesso(self, msg)

        # Se for aluno, mostra o email institucional gerado
        if tipo == "aluno" and dados and dados.get("email_institucional"):
            self._mostrar_dialog_sucesso(dados)
        else:
            self.after(1200, self._abrir_login)

    def _mostrar_dialog_sucesso(self, dados):
        """Dialog modal mostrando email institucional gerado."""
        dlg = tk.Toplevel(self)
        dlg.title("Cadastro Concluido")
        dlg.geometry("480x340")
        dlg.configure(bg=BRANCO)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)

        # Centraliza
        dlg.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 480) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 340) // 2
        dlg.geometry(f"480x340+{x}+{y}")

        # Header verde
        header = tk.Frame(dlg, bg=VERDE_SUCESSO, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="✓", font=("Segoe UI", 32, "bold"),
                 fg=BRANCO, bg=VERDE_SUCESSO).pack(pady=12)

        # Corpo
        corpo = tk.Frame(dlg, bg=BRANCO)
        corpo.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(corpo, text="Cadastro realizado com sucesso!",
                 font=(FONTE_TITULO, 14, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(pady=(0, 8))

        tk.Label(corpo,
                 text="Sua matricula institucional foi gerada:",
                 font=(FONTE_TEXTO, 10),
                 fg=CINZA_ESCURO, bg=BRANCO).pack(pady=(0, 6))

        # Email institucional destacado
        email_frame = tk.Frame(corpo, bg=BRANCO_GELO,
                               highlightbackground=AZUL_PRIMARIO,
                               highlightthickness=2)
        email_frame.pack(fill="x", pady=4)

        tk.Label(email_frame, text="📧 EMAIL INSTITUCIONAL",
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=AZUL_PRIMARIO, bg=BRANCO_GELO).pack(pady=(8, 2))
        tk.Label(email_frame, text=dados["email_institucional"],
                 font=(FONTE_TEXTO, 11, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(pady=(0, 4))
        tk.Label(email_frame, text=f"Matricula: {dados['matricula']}",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO).pack(pady=(0, 8))

        tk.Label(corpo,
                 text="Use a senha que voce cadastrou para acessar.",
                 font=(FONTE_TEXTO, 9, "italic"),
                 fg=CINZA_ESCURO, bg=BRANCO).pack(pady=(8, 4))

        BotaoModerno(corpo, texto="Ir para o Login",
                     comando=lambda: (dlg.destroy(), self._abrir_login()),
                     largura=200, altura=38,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     cor_fundo=BRANCO).pack(pady=(8, 0))

    def _abrir_login(self, _=None):
        from app.visao.tela_login import TelaLogin
        self.destroy()
        TelaLogin(master=self.master_ref, ao_voltar=self.ao_voltar)
