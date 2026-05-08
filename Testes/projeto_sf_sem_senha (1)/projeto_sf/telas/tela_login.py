"""
Tela de Login (entrada principal do sistema).

Layout: visual à esquerda, formulário à direita.
Usuários comuns (alunos/clientes) entram aqui.
Há um link discreto "Acesso Administrativo" que abre a tela
exclusiva do administrador.
"""
import tkinter as tk
from tkinter import messagebox

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.campo_entrada import CampoArredondado
from componentes.logo_sf import LogoSF
from componentes.notificacoes import (
    NotificacaoFlutuante,
    RastroCursor,
    fade_in_janela,
)
from componentes.painel_visual import PainelVisualLateral
from controladores.controlador_autenticacao import ControladorAutenticacao


class TelaLogin:
    """Tela de login para alunos/clientes."""

    def __init__(self, sessao=None):
        self.sessao = sessao
        self.raiz = tk.Tk()
        self.raiz.title("Sistema Fácil - Login")
        self.raiz.configure(bg=tema.OFFWHITE)
        self.raiz.geometry("1200x720")
        self.raiz.minsize(1000, 640)

        self._rastro = None
        self._construir()

        # Centraliza
        self.raiz.update_idletasks()
        l = self.raiz.winfo_screenwidth()
        a = self.raiz.winfo_screenheight()
        x = (l - 1200) // 2
        y = (a - 720) // 2
        self.raiz.geometry(f"1200x720+{x}+{y}")

        fade_in_janela(self.raiz, duracao_ms=240)

        # Rastro do cursor (animação)
        self._rastro = RastroCursor(self.raiz, cor=tema.AMARELO_DOURADO, quantidade=10)
        try:
            self._rastro.iniciar()
        except Exception:
            pass

    # =================================================================
    def _construir(self):
        container = tk.Frame(self.raiz, bg=tema.OFFWHITE)
        container.pack(fill="both", expand=True)

        # 50/50 grid
        container.columnconfigure(0, weight=1, uniform="x")
        container.columnconfigure(1, weight=1, uniform="x")
        container.rowconfigure(0, weight=1)

        # ------------------- LADO ESQUERDO (visual)
        self._visual = PainelVisualLateral(
            container,
            titulo="Bem-vindo de volta\nao Sistema Fácil",
            subtitulo=(
                "Acesse sua conta e continue sua jornada de aprendizado "
                "com facilidade e segurança."
            ),
            codigo_decorativo="#3C507D",
        )
        self._visual.grid(row=0, column=0, sticky="nsew")

        # ------------------- LADO DIREITO (formulário)
        formulario = tk.Frame(container, bg=tema.OFFWHITE)
        formulario.grid(row=0, column=1, sticky="nsew")
        self._desenhar_formulario(formulario)

    # =================================================================
    def _desenhar_formulario(self, pai: tk.Frame):
        # caixa central
        caixa = tk.Frame(pai, bg=tema.OFFWHITE)
        caixa.place(relx=0.5, rely=0.5, anchor="center", width=420, height=620)

        # Logo
        logo = LogoSF(caixa, tamanho=70, cor_fundo=tema.OFFWHITE)
        logo.pack(pady=(0, 8))

        tk.Label(
            caixa,
            text="Faça login na sua conta",
            bg=tema.OFFWHITE,
            fg=tema.AZUL_ESCURO,
            font=tema.fonte_titulo(22),
        ).pack(pady=(4, 4))

        tk.Label(
            caixa,
            text="Acesse sua conta",
            bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO,
            font=tema.fonte_subtitulo(11),
        ).pack(pady=(0, 18))

        # campos
        self._campo_email = CampoArredondado(
            caixa,
            placeholder="E-mail ou usuário",
            icone="\u2709",
            largura=380,
        )
        self._campo_email.pack(pady=6)

        self._campo_senha = CampoArredondado(
            caixa,
            placeholder="Senha",
            icone="\u26BF",
            senha=True,
            largura=380,
        )
        self._campo_senha.pack(pady=6)

        self._campo_telefone = CampoArredondado(
            caixa,
            placeholder="Número de telefone (opcional)",
            icone="\u260E",
            largura=380,
        )
        self._campo_telefone.pack(pady=6)

        # Linha lembrar-me / esqueci
        linha_extras = tk.Frame(caixa, bg=tema.OFFWHITE)
        linha_extras.pack(fill="x", pady=(6, 8), padx=20)

        self._var_lembrar = tk.IntVar(value=0)
        tk.Checkbutton(
            linha_extras,
            text=" Lembrar de mim",
            variable=self._var_lembrar,
            bg=tema.OFFWHITE,
            fg=tema.AZUL_ESCURO,
            activebackground=tema.OFFWHITE,
            activeforeground=tema.AZUL_PRINCIPAL,
            selectcolor=tema.OFFWHITE,
            bd=0,
            highlightthickness=0,
            font=tema.fonte_corpo(10),
        ).pack(side="left")

        link_esqueci = tk.Label(
            linha_extras,
            text="Esqueci minha senha",
            bg=tema.OFFWHITE,
            fg=tema.AZUL_PRINCIPAL,
            cursor="hand2",
            font=tema.fonte_corpo(10),
        )
        link_esqueci.pack(side="right")
        link_esqueci.bind("<Button-1>", lambda _e: self._abrir_recuperacao())

        # Botão Entrar
        BotaoArredondado(
            caixa,
            texto="Entrar",
            comando=self._tentar_login,
            largura=380,
            altura=46,
            fonte=tema.fonte_destaque(13),
        ).pack(pady=(8, 6))

        # Botão Google (mock)
        BotaoArredondado(
            caixa,
            texto="Continuar com Google",
            comando=self._login_google,
            cor_fundo="#FFFFFF",
            cor_hover=tema.CINZA_CLARO,
            cor_press="#E2E4EC",
            cor_texto=tema.AZUL_ESCURO,
            largura=380,
            altura=44,
            fonte=tema.fonte_destaque(11),
        ).pack(pady=(0, 8))

        # Links
        link_cadastro = tk.Label(
            caixa,
            text="Não tem uma conta? Cadastre-se",
            bg=tema.OFFWHITE,
            fg=tema.AZUL_ESCURO,
            cursor="hand2",
            font=tema.fonte_corpo(11),
        )
        link_cadastro.pack(pady=(6, 4))
        link_cadastro.bind("<Button-1>", lambda _e: self._abrir_registro())

        # Acesso administrativo (discreto)
        link_admin = tk.Label(
            caixa,
            text="Acesso administrativo \u2192",
            bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO,
            cursor="hand2",
            font=tema.fonte_corpo(10),
        )
        link_admin.pack(pady=(14, 0))
        link_admin.bind("<Button-1>", lambda _e: self._abrir_login_admin())

    # =================================================================
    def _tentar_login(self):
        email = self._campo_email.obter_valor().strip()
        senha = self._campo_senha.obter_valor().strip()

        sucesso, msg, usuario = ControladorAutenticacao.autenticar_usuario(
            email, senha,
        )
        if not sucesso:
            self._campo_email.marcar_erro()
            self._campo_senha.marcar_erro()
            NotificacaoFlutuante.exibir(self.raiz, msg, tipo="erro")
            return

        # Limpa marcações de erro
        self._campo_email.limpar_erro()
        self._campo_senha.limpar_erro()

        if self.sessao:
            self.sessao.iniciar(usuario, tipo=usuario.get("tipo_conta", "aluno"))

        NotificacaoFlutuante.exibir(
            self.raiz,
            f"Bem-vindo(a), {usuario['nome_completo'].split()[0]}!",
            tipo="sucesso",
        )

        # Aluno/cliente ainda não tem painel próprio: somente mensagem
        self.raiz.after(900, lambda: self._exibir_aviso_pos_login(usuario))

    def _exibir_aviso_pos_login(self, usuario: dict):
        msg = (
            "Login realizado com sucesso!\n\n"
            f"Olá {usuario['nome_completo']}, sua sessão foi iniciada.\n\n"
            f"Email institucional gerado:\n{usuario['email_institucional']}\n\n"
            "O painel exclusivo de aluno/cliente está em desenvolvimento. "
            "Apenas o administrador acessa o dashboard de gestão."
        )
        messagebox.showinfo("Sessão iniciada", msg, parent=self.raiz)

    # =================================================================
    def _login_google(self):
        NotificacaoFlutuante.exibir(
            self.raiz,
            "Login com Google: integração OAuth disponível em produção.",
            tipo="info",
            duracao_ms=2400,
        )

    def _abrir_recuperacao(self):
        from telas.tela_recuperacao_senha import TelaRecuperacaoSenha
        TelaRecuperacaoSenha(self.raiz)

    def _abrir_registro(self):
        from telas.tela_registro import TelaRegistro
        # transição: oculta a janela atual, mostra a de registro
        self._fechar_rastro()
        self.raiz.withdraw()
        TelaRegistro(self.sessao, ao_voltar=self._restaurar_e_iniciar_rastro)

    def _abrir_login_admin(self):
        from telas.tela_login_admin import TelaLoginAdministrador
        self._fechar_rastro()
        self.raiz.withdraw()
        TelaLoginAdministrador(
            sessao=self.sessao,
            ao_voltar=self._restaurar_e_iniciar_rastro,
            raiz_principal=self.raiz,
        )

    def _restaurar_e_iniciar_rastro(self):
        """Callback chamado quando outra tela fecha e voltamos para login."""
        try:
            self.raiz.deiconify()
        except tk.TclError:
            return
        if self._rastro is None:
            self._rastro = RastroCursor(
                self.raiz, cor=tema.AMARELO_DOURADO, quantidade=10,
            )
        try:
            self._rastro.iniciar()
        except Exception:
            pass

    def _fechar_rastro(self):
        if self._rastro is not None:
            try:
                self._rastro.parar()
            except Exception:
                pass
            self._rastro = None

    # =================================================================
    def executar(self):
        self.raiz.mainloop()
