"""
Tela de Registro (Cadastro de Aluno/Cliente).

Layout: formulário à esquerda, painel visual à direita.
Após cadastro bem-sucedido, exibe o e-mail institucional gerado.
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
from utilitarios.validadores import formatar_telefone_progressivo


class TelaRegistro:
    """Tela de cadastro para alunos/clientes."""

    def __init__(self, sessao=None, ao_voltar=None):
        self.sessao = sessao
        self._ao_voltar = ao_voltar
        self.janela = tk.Toplevel()
        self.janela.title("Sistema Fácil - Criar conta")
        self.janela.configure(bg=tema.OFFWHITE)
        self.janela.geometry("1200x720")
        self.janela.minsize(1000, 640)
        self.janela.protocol("WM_DELETE_WINDOW", self._fechar)

        self._tipo_conta = tk.StringVar(value="aluno")
        self._rastro = None

        self._construir()

        self.janela.update_idletasks()
        l = self.janela.winfo_screenwidth()
        a = self.janela.winfo_screenheight()
        x = (l - 1200) // 2
        y = (a - 720) // 2
        self.janela.geometry(f"1200x720+{x}+{y}")

        fade_in_janela(self.janela, duracao_ms=240)

        try:
            self._rastro = RastroCursor(
                self.janela, cor=tema.AMARELO_DOURADO, quantidade=10,
            )
            self._rastro.iniciar()
        except Exception:
            pass

    # =================================================================
    def _construir(self):
        container = tk.Frame(self.janela, bg=tema.OFFWHITE)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=1, uniform="x")
        container.columnconfigure(1, weight=1, uniform="x")
        container.rowconfigure(0, weight=1)

        # ------------------- LADO ESQUERDO (formulário)
        formulario = tk.Frame(container, bg=tema.OFFWHITE)
        formulario.grid(row=0, column=0, sticky="nsew")
        self._desenhar_formulario(formulario)

        # ------------------- LADO DIREITO (visual)
        self._visual = PainelVisualLateral(
            container,
            titulo="Seu futuro começa\ncom uma escolha\nsimples",
            subtitulo=(
                "Descubra novas oportunidades, desenvolva habilidades e "
                "faça parte de uma comunidade de aprendizado moderna."
            ),
            codigo_decorativo="#3C507D",
        )
        self._visual.grid(row=0, column=1, sticky="nsew")

    # =================================================================
    def _desenhar_formulario(self, pai: tk.Frame):
        caixa = tk.Frame(pai, bg=tema.OFFWHITE)
        caixa.place(relx=0.5, rely=0.5, anchor="center", width=440, height=660)

        logo = LogoSF(caixa, tamanho=64, cor_fundo=tema.OFFWHITE)
        logo.pack(pady=(0, 4))

        tk.Label(
            caixa,
            text="Crie sua conta",
            bg=tema.OFFWHITE,
            fg=tema.AZUL_ESCURO,
            font=tema.fonte_titulo(24),
        ).pack(pady=(2, 2))

        tk.Label(
            caixa,
            text="Comece sua jornada no Sistema Fácil",
            bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO,
            font=tema.fonte_subtitulo(11),
        ).pack(pady=(0, 14))

        # Seletor de tipo de conta (aluno / cliente)
        seletor = tk.Frame(caixa, bg=tema.OFFWHITE)
        seletor.pack(pady=(0, 8))

        for valor, rotulo in (("aluno", "Aluno"), ("cliente", "Cliente / Visitante")):
            rb = tk.Radiobutton(
                seletor,
                text=rotulo,
                variable=self._tipo_conta,
                value=valor,
                bg=tema.OFFWHITE,
                fg=tema.AZUL_ESCURO,
                activebackground=tema.OFFWHITE,
                activeforeground=tema.AZUL_PRINCIPAL,
                selectcolor=tema.OFFWHITE,
                bd=0,
                highlightthickness=0,
                font=tema.fonte_corpo(10),
                cursor="hand2",
            )
            rb.pack(side="left", padx=8)

        # campos
        self._campo_nome = CampoArredondado(
            caixa, placeholder="Nome completo", icone="\u2302", largura=400,
        )
        self._campo_nome.pack(pady=4)

        self._campo_email = CampoArredondado(
            caixa, placeholder="E-mail", icone="\u2709", largura=400,
        )
        self._campo_email.pack(pady=4)

        self._campo_email_rep = CampoArredondado(
            caixa, placeholder="Repetir e-mail", icone="\u2709", largura=400,
        )
        self._campo_email_rep.pack(pady=4)

        self._campo_senha = CampoArredondado(
            caixa, placeholder="Senha (mínimo 8 caracteres)",
            icone="\u26BF", senha=True, largura=400,
        )
        self._campo_senha.pack(pady=4)

        self._campo_senha_rep = CampoArredondado(
            caixa, placeholder="Repetir senha",
            icone="\u26BF", senha=True, largura=400,
        )
        self._campo_senha_rep.pack(pady=4)

        self._campo_telefone = CampoArredondado(
            caixa, placeholder="Número de telefone",
            icone="\u260E", largura=400,
        )
        self._campo_telefone.pack(pady=4)

        # formatação automática de telefone
        try:
            self._campo_telefone.widget_entry().bind(
                "<KeyRelease>", self._auto_formatar_telefone,
            )
        except Exception:
            pass

        # Botão Cadastrar
        BotaoArredondado(
            caixa,
            texto="Cadastrar",
            comando=self._tentar_cadastrar,
            largura=400,
            altura=46,
            fonte=tema.fonte_destaque(13),
        ).pack(pady=(10, 6))

        # Botão Google (mock)
        BotaoArredondado(
            caixa,
            texto="Cadastrar com Google",
            comando=self._cadastro_google,
            cor_fundo="#FFFFFF",
            cor_hover=tema.CINZA_CLARO,
            cor_press="#E2E4EC",
            cor_texto=tema.AZUL_ESCURO,
            largura=400,
            altura=42,
            fonte=tema.fonte_destaque(11),
        ).pack(pady=(0, 8))

        link_voltar = tk.Label(
            caixa,
            text="Já tem uma conta? Entrar",
            bg=tema.OFFWHITE,
            fg=tema.AZUL_PRINCIPAL,
            cursor="hand2",
            font=tema.fonte_corpo(11),
        )
        link_voltar.pack(pady=(4, 2))
        link_voltar.bind("<Button-1>", lambda _e: self._fechar())

        tk.Label(
            caixa,
            text="Todos os campos são obrigatórios",
            bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(9),
        ).pack(pady=(2, 0))

    # =================================================================
    def _auto_formatar_telefone(self, _evento):
        try:
            valor_atual = self._campo_telefone.obter_valor()
            formatado = formatar_telefone_progressivo(valor_atual)
            if formatado != valor_atual:
                self._campo_telefone.definir_valor(formatado)
                # mantém o cursor no fim
                self._campo_telefone.widget_entry().icursor("end")
        except Exception:
            pass

    # =================================================================
    def _limpar_erros(self):
        for c in (
            self._campo_nome, self._campo_email, self._campo_email_rep,
            self._campo_senha, self._campo_senha_rep, self._campo_telefone,
        ):
            try:
                c.limpar_erro()
            except Exception:
                pass

    def _tentar_cadastrar(self):
        self._limpar_erros()
        dados = {
            "nome_completo": self._campo_nome.obter_valor(),
            "email_pessoal": self._campo_email.obter_valor(),
            "email_repetir": self._campo_email_rep.obter_valor(),
            "senha": self._campo_senha.obter_valor(),
            "senha_repetir": self._campo_senha_rep.obter_valor(),
            "telefone": self._campo_telefone.obter_valor(),
            "tipo_conta": self._tipo_conta.get(),
        }
        sucesso, msg, usuario = ControladorAutenticacao.registrar_usuario(dados)
        if not sucesso:
            NotificacaoFlutuante.exibir(self.janela, msg, tipo="erro")
            self._marcar_campos_com_erro(msg)
            return

        NotificacaoFlutuante.exibir(
            self.janela,
            "Conta criada com sucesso!",
            tipo="sucesso",
        )
        self.janela.after(900, lambda: self._exibir_resumo_pos_cadastro(usuario))

    def _marcar_campos_com_erro(self, mensagem: str):
        msg = mensagem.lower()
        if "nome" in msg:
            self._campo_nome.marcar_erro()
        if "e-mail" in msg or "email" in msg:
            if "conferem" in msg or "repetir" in msg:
                self._campo_email_rep.marcar_erro()
            self._campo_email.marcar_erro()
        if "senha" in msg:
            self._campo_senha.marcar_erro()
            if "conferem" in msg or "repetir" in msg:
                self._campo_senha_rep.marcar_erro()

    def _exibir_resumo_pos_cadastro(self, usuario: dict):
        msg = (
            "Cadastro concluído!\n\n"
            f"Bem-vindo(a), {usuario['nome_completo']}!\n\n"
            "E-mail institucional gerado automaticamente:\n"
            f"   {usuario['email_institucional']}\n\n"
            "Use esse e-mail (ou seu e-mail pessoal) para entrar.\n\n"
            "Anote o e-mail institucional em local seguro."
        )
        messagebox.showinfo("Conta criada", msg, parent=self.janela)
        self._fechar()

    def _cadastro_google(self):
        NotificacaoFlutuante.exibir(
            self.janela,
            "Cadastro com Google: integração OAuth disponível em produção.",
            tipo="info",
            duracao_ms=2400,
        )

    # =================================================================
    def _fechar(self):
        try:
            if self._rastro is not None:
                self._rastro.parar()
        except Exception:
            pass
        try:
            self.janela.destroy()
        except Exception:
            pass
        if self._ao_voltar:
            try:
                self._ao_voltar()
            except Exception:
                pass
