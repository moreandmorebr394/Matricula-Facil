"""
Tela de Recuperação de Senha.

Tela simples (mock) que solicita o e-mail e exibe um toast confirmando
o envio das instruções.
"""
import tkinter as tk

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.campo_entrada import CampoArredondado
from componentes.logo_sf import LogoSF
from componentes.notificacoes import NotificacaoFlutuante, fade_in_janela
from utilitarios.validadores import validar_email


class TelaRecuperacaoSenha:

    def __init__(self, pai=None):
        self.janela = tk.Toplevel(pai)
        self.janela.title("Sistema Fácil - Recuperar senha")
        self.janela.configure(bg=tema.OFFWHITE)
        self.janela.geometry("520x440")
        self.janela.resizable(False, False)
        self.janela.transient(pai)
        self.janela.grab_set()

        self._construir()

        self.janela.update_idletasks()
        l = self.janela.winfo_screenwidth()
        a = self.janela.winfo_screenheight()
        x = (l - 520) // 2
        y = (a - 440) // 2
        self.janela.geometry(f"520x440+{x}+{y}")
        fade_in_janela(self.janela, duracao_ms=200)

    def _construir(self):
        caixa = tk.Frame(self.janela, bg=tema.OFFWHITE)
        caixa.pack(fill="both", expand=True, padx=24, pady=24)

        LogoSF(caixa, tamanho=56, cor_fundo=tema.OFFWHITE).pack(pady=(0, 8))

        tk.Label(
            caixa,
            text="Recuperar senha",
            bg=tema.OFFWHITE,
            fg=tema.AZUL_ESCURO,
            font=tema.fonte_titulo(20),
        ).pack(pady=(0, 6))

        tk.Label(
            caixa,
            text=(
                "Informe o e-mail cadastrado e enviaremos as instruções\n"
                "para criar uma nova senha de acesso."
            ),
            bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO,
            font=tema.fonte_subtitulo(11),
            justify="center",
        ).pack(pady=(0, 20))

        self._campo_email = CampoArredondado(
            caixa,
            placeholder="E-mail cadastrado",
            icone="\u2709",
            largura=440,
        )
        self._campo_email.pack(pady=10)

        BotaoArredondado(
            caixa,
            texto="Enviar instruções",
            comando=self._enviar,
            largura=440,
            altura=46,
            fonte=tema.fonte_destaque(13),
        ).pack(pady=(16, 8))

        link_fechar = tk.Label(
            caixa,
            text="Voltar ao login",
            bg=tema.OFFWHITE,
            fg=tema.AZUL_PRINCIPAL,
            cursor="hand2",
            font=tema.fonte_corpo(11),
        )
        link_fechar.pack(pady=(6, 0))
        link_fechar.bind("<Button-1>", lambda _e: self.janela.destroy())

    def _enviar(self):
        email = self._campo_email.obter_valor().strip()
        if not validar_email(email):
            self._campo_email.marcar_erro()
            NotificacaoFlutuante.exibir(
                self.janela, "Informe um e-mail válido.", tipo="erro",
            )
            return
        self._campo_email.limpar_erro()
        NotificacaoFlutuante.exibir(
            self.janela,
            f"Instruções enviadas para {email}",
            tipo="sucesso",
            duracao_ms=2200,
        )
        self.janela.after(1600, self.janela.destroy)
