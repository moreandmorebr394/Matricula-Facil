"""
Tela de Login do Administrador.

Tela exclusiva e privada. Apenas o e-mail institucional e necessario
para entrar (sem senha). Em caso de e-mail valido, fecha esta janela
e abre o Dashboard.
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
from configuracoes_admin import credenciais_admin
from controladores.controlador_autenticacao import ControladorAutenticacao


class TelaLoginAdministrador:
    """Tela de autenticacao exclusiva do administrador (somente e-mail)."""

    def __init__(self, sessao=None, ao_voltar=None, raiz_principal=None):
        self.sessao = sessao
        self._ao_voltar = ao_voltar
        self._raiz_principal = raiz_principal

        self.janela = tk.Toplevel()
        self.janela.title("Sistema Facil - Acesso Administrativo")
        self.janela.configure(bg=tema.OFFWHITE)
        self.janela.geometry("1100x680")
        self.janela.minsize(960, 600)
        self.janela.protocol("WM_DELETE_WINDOW", self._fechar)

        self._tentativas = 0
        self._rastro = None
        self._abrindo_dashboard = False

        self._construir()

        # Centraliza
        self.janela.update_idletasks()
        l = self.janela.winfo_screenwidth()
        a = self.janela.winfo_screenheight()
        x = (l - 1100) // 2
        y = (a - 680) // 2
        self.janela.geometry(f"1100x680+{x}+{y}")

        fade_in_janela(self.janela, duracao_ms=240)

        # Rastro do cursor (animacao)
        try:
            self._rastro = RastroCursor(
                self.janela, cor=tema.AMARELO_DOURADO, quantidade=10,
            )
            self._rastro.iniciar()
        except Exception:
            self._rastro = None

        # Foco no campo de email para o usuario digitar imediatamente
        try:
            self._campo_email.widget_entry().focus_set()
        except Exception:
            pass

    # =================================================================
    def _construir(self):
        container = tk.Frame(self.janela, bg=tema.OFFWHITE)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=1, uniform="x")
        container.columnconfigure(1, weight=1, uniform="x")
        container.rowconfigure(0, weight=1)

        # Visual a esquerda (identidade premium para area admin)
        self._visual = PainelVisualLateral(
            container,
            titulo="Acesso\nAdministrativo",
            subtitulo=(
                "Area restrita ao gestor do sistema. "
                "Informe o e-mail institucional cadastrado para "
                "acessar o painel de gestao educacional."
            ),
            codigo_decorativo="#112250",
        )
        self._visual.grid(row=0, column=0, sticky="nsew")

        # Formulario a direita
        formulario = tk.Frame(container, bg=tema.OFFWHITE)
        formulario.grid(row=0, column=1, sticky="nsew")
        self._desenhar_formulario(formulario)

    def _desenhar_formulario(self, pai: tk.Frame):
        caixa = tk.Frame(pai, bg=tema.OFFWHITE)
        caixa.place(relx=0.5, rely=0.5, anchor="center", width=440, height=520)

        # Logo
        LogoSF(caixa, tamanho=72, cor_fundo=tema.OFFWHITE).pack(pady=(0, 8))

        tk.Label(
            caixa,
            text="Painel do Administrador",
            bg=tema.OFFWHITE,
            fg=tema.AZUL_ESCURO,
            font=tema.fonte_titulo(22),
        ).pack(pady=(2, 4))

        tk.Label(
            caixa,
            text="Informe seu e-mail institucional",
            bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO,
            font=tema.fonte_subtitulo(11),
        ).pack(pady=(0, 22))

        # Campo de e-mail (unico campo da tela)
        self._campo_email = CampoArredondado(
            caixa,
            placeholder="E-mail institucional do administrador",
            icone="\u2709",
            largura=400,
            altura=48,
        )
        self._campo_email.pack(pady=10)

        # Tecla Enter envia
        try:
            self._campo_email.widget_entry().bind(
                "<Return>", lambda _e: self._tentar_login(),
            )
        except Exception:
            pass

        # Botao principal
        BotaoArredondado(
            caixa,
            texto="Entrar no Painel",
            comando=self._tentar_login,
            largura=400,
            altura=48,
            fonte=tema.fonte_destaque(13),
        ).pack(pady=(16, 8))

        # Aviso/dica em destaque com o e-mail padrao para facilitar
        dica = tk.Frame(caixa, bg=tema.AMARELO_INPUT_FOCO)
        dica.pack(fill="x", pady=(14, 0))
        tk.Label(
            dica,
            text=(
                "Dica: o e-mail do administrador principal e\n"
                f"{credenciais_admin.EMAIL_ADMIN}"
            ),
            bg=tema.AMARELO_INPUT_FOCO,
            fg=tema.AZUL_ESCURO,
            font=tema.fonte_corpo(10),
            justify="center",
            padx=10,
            pady=8,
        ).pack(fill="x")

        # Link voltar
        link_voltar = tk.Label(
            caixa,
            text="\u2190 Voltar para o login de aluno",
            bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO,
            cursor="hand2",
            font=tema.fonte_corpo(10),
        )
        link_voltar.pack(pady=(18, 0))
        link_voltar.bind("<Button-1>", lambda _e: self._fechar())

        # Aviso discreto
        tk.Label(
            caixa,
            text=(
                "Area protegida. Apenas e-mails cadastrados em\n"
                "configuracoes_admin/credenciais_admin.py podem entrar."
            ),
            bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(9),
            justify="center",
        ).pack(pady=(14, 0))

    # =================================================================
    def _tentar_login(self):
        # Evita disparos duplos durante a transicao para o dashboard
        if self._abrindo_dashboard:
            return

        email = self._campo_email.obter_valor().strip()

        sucesso, msg, dados = (
            ControladorAutenticacao.autenticar_administrador_por_email(email)
        )

        if not sucesso:
            self._tentativas += 1
            try:
                self._campo_email.marcar_erro()
            except Exception:
                pass
            NotificacaoFlutuante.exibir(self.janela, msg, tipo="erro")
            if self._tentativas >= 5:
                messagebox.showerror(
                    "Acesso bloqueado",
                    "Muitas tentativas invalidas. Reinicie o sistema.",
                    parent=self.janela,
                )
                self._fechar()
            return

        # Sucesso
        try:
            self._campo_email.limpar_erro()
        except Exception:
            pass

        if self.sessao:
            try:
                self.sessao.iniciar(dados, tipo="administrador")
            except Exception:
                pass

        NotificacaoFlutuante.exibir(
            self.janela,
            f"Bem-vindo, {dados.get('nome_completo', 'administrador')}!",
            tipo="sucesso",
            duracao_ms=1400,
        )

        self._abrindo_dashboard = True
        self.janela.after(900, self._abrir_dashboard)

    def _abrir_dashboard(self):
        # Para o rastro do cursor
        try:
            if self._rastro is not None:
                self._rastro.parar()
                self._rastro = None
        except Exception:
            pass

        # Importa aqui para evitar imports circulares
        try:
            from telas.tela_dashboard import TelaDashboard
        except Exception as exc:
            messagebox.showerror(
                "Erro ao abrir dashboard",
                f"Nao foi possivel carregar o painel: {exc}",
                parent=self.janela,
            )
            self._abrindo_dashboard = False
            return

        # Fecha a janela de login admin
        try:
            self.janela.destroy()
        except Exception:
            pass

        # Fecha a janela principal (login de aluno) se foi passada
        try:
            if self._raiz_principal is not None:
                self._raiz_principal.destroy()
        except Exception:
            pass

        # Abre o dashboard (vira a janela principal do app)
        try:
            TelaDashboard(sessao=self.sessao)
        except Exception as exc:
            # Se algo der errado ao iniciar o dashboard, mostra mensagem
            try:
                erro_root = tk.Tk()
                erro_root.withdraw()
                messagebox.showerror(
                    "Erro ao abrir dashboard",
                    f"Falha ao iniciar o painel administrativo:\n{exc}",
                )
                erro_root.destroy()
            except Exception:
                pass

    # =================================================================
    def _fechar(self):
        try:
            if self._rastro is not None:
                self._rastro.parar()
                self._rastro = None
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
