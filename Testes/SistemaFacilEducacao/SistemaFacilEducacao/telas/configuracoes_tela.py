"""Tela de Configuracoes do sistema."""
import tkinter as tk
from typing import Callable

from componentes.botao import BotaoPrimario, BotaoSecundario, BotaoPerigo
from componentes.campo_entrada import CampoEntrada
from componentes.card import CardComCabecalho
from config.cores import Cores
from config.configuracoes import Configuracoes
from config.fontes import Fontes
from dados.banco_dados import BancoDados


class TelaConfiguracoes(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self.navegar_para = navegar_para
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)
        wrapper.grid_columnconfigure(0, weight=1, uniform="c")
        wrapper.grid_columnconfigure(1, weight=1, uniform="c")

        # ---- Perfil do administrador ----
        perfil = CardComCabecalho(wrapper, titulo="Perfil de Administrador",
                                  icone="👤")
        perfil.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        cp = perfil.conteudo()
        cp.configure(bg=Cores.CARD_FUNDO)

        # avatar
        avatar = tk.Canvas(cp, width=72, height=72, bg=Cores.CARD_FUNDO,
                           highlightthickness=0)
        avatar.pack(pady=(4, 8))
        avatar.create_oval(2, 2, 70, 70, fill=Cores.LOGO_AZUL,
                           outline="")
        avatar.create_text(36, 36, text="A",
                           fill=Cores.LOGO_AMARELO,
                           font=(Fontes.FAMILIA, 28, "bold"))

        self.campo_nome = CampoEntrada(cp, rotulo="Nome de exibicao")
        self.campo_nome.pack(fill="x", pady=4)
        self.campo_nome.definir(Configuracoes.USUARIO_NOME)

        self.campo_email = CampoEntrada(cp, rotulo="E-mail de contato")
        self.campo_email.pack(fill="x", pady=4)
        self.campo_email.definir(Configuracoes.USUARIO_EMAIL)

        self.campo_senha = CampoEntrada(cp, rotulo="Nova senha (opcional)",
                                        placeholder="••••••••")
        self.campo_senha.pack(fill="x", pady=4)

        botoes_perfil = tk.Frame(cp, bg=Cores.CARD_FUNDO)
        botoes_perfil.pack(fill="x", pady=(14, 0))
        BotaoPrimario(botoes_perfil, texto="Salvar Alteracoes",
                      comando=self._salvar_perfil,
                      largura=180).pack(side="right")

        # ---- Sistema ----
        sis = CardComCabecalho(wrapper, titulo="Sistema",
                               icone="⚙")
        sis.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        cs = sis.conteudo()
        cs.configure(bg=Cores.CARD_FUNDO)

        self._linha_info(cs, "Versao", Configuracoes.VERSAO)
        self._linha_info(cs, "Total de leads", str(len(self.banco.leads)))
        self._linha_info(cs, "Total de vendas",
                         str(len(self.banco.vendas)))
        self._linha_info(cs, "Total de turmas",
                         str(len(self.banco.turmas)))
        self._linha_info(cs, "Total de aulas",
                         str(len(self.banco.aulas)))
        self._linha_info(cs, "Pasta de dados",
                         Configuracoes.PASTA_DADOS, pequeno=True)

        BotaoSecundario(cs, texto="Atualizar Dados",
                        comando=self._recarregar,
                        largura=160).pack(pady=(14, 0), anchor="w")

        # ---- Preferencias ----
        pref = CardComCabecalho(wrapper, titulo="Preferencias",
                                icone="🎨")
        pref.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(8, 0))
        cpr = pref.conteudo()
        cpr.configure(bg=Cores.CARD_FUNDO)

        self.var_notif = tk.BooleanVar(value=True)
        self.var_anim = tk.BooleanVar(value=True)
        self.var_auto = tk.BooleanVar(value=True)

        for var, texto, sub in [
            (self.var_notif, "Receber notificacoes em tempo real",
             "Toasts no canto superior direito da tela."),
            (self.var_anim, "Ativar animacoes",
             "Fade-in e transicoes suaves nas telas."),
            (self.var_auto, "Salvamento automatico",
             "Persistir dados em arquivos JSON automaticamente."),
        ]:
            l = tk.Frame(cpr, bg=Cores.CARD_FUNDO)
            l.pack(fill="x", pady=6)
            tk.Checkbutton(l, text=texto, variable=var,
                           bg=Cores.CARD_FUNDO,
                           fg=Cores.TEXTO_PRIMARIO,
                           font=Fontes.PEQUENO_NEGRITO,
                           selectcolor=Cores.CARD_FUNDO,
                           activebackground=Cores.CARD_FUNDO,
                           cursor="hand2").pack(anchor="w")
            tk.Label(l, text=sub, bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.MICRO).pack(anchor="w", padx=20)

        # ---- Zona de risco ----
        risco = CardComCabecalho(wrapper, titulo="Zona de Risco",
                                 icone="⚠")
        risco.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(8, 0))
        cr = risco.conteudo()
        cr.configure(bg=Cores.CARD_FUNDO)

        tk.Label(cr,
                 text="Operacoes irreversiveis. Use com cuidado.",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_SECUNDARIO,
                 font=Fontes.PEQUENO,
                 wraplength=320, justify="left").pack(anchor="w",
                                                      pady=(0, 12))

        BotaoPerigo(cr, texto="Limpar todas as notificacoes",
                    comando=self._limpar_notificacoes,
                    largura=240).pack(anchor="w", pady=4)
        BotaoPerigo(cr, texto="Marcar todos os leads como contatados",
                    comando=self._marcar_contatados,
                    largura=300).pack(anchor="w", pady=4)

        # ---- Sobre ----
        sobre = CardComCabecalho(wrapper, titulo="Sobre",
                                 icone="ℹ")
        sobre.grid(row=2, column=0, columnspan=2, sticky="nsew",
                   pady=(8, 0))
        sb = sobre.conteudo()
        sb.configure(bg=Cores.CARD_FUNDO)
        tk.Label(sb,
                 text=f"{Configuracoes.NOME_SISTEMA}",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO_CARD,
                 anchor="w").pack(anchor="w")
        tk.Label(sb,
                 text=("CRM educacional completo para gestao de leads, "
                       "vendas, turmas e frequencia. Construido com "
                       "Tkinter puro - sem dependencias externas."),
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_SECUNDARIO,
                 font=Fontes.PEQUENO,
                 wraplength=820, justify="left",
                 anchor="w").pack(anchor="w", pady=(4, 4))
        tk.Label(sb, text=f"Versao {Configuracoes.VERSAO}  •  © 2024",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.MICRO,
                 anchor="w").pack(anchor="w")

    def _linha_info(self, parent, rotulo, valor, pequeno=False):
        l = tk.Frame(parent, bg=Cores.CARD_FUNDO)
        l.pack(fill="x", pady=4)
        tk.Label(l, text=rotulo, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO,
                 anchor="w").pack(side="left")
        tk.Label(l, text=valor, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.MICRO if pequeno else Fontes.PEQUENO_NEGRITO,
                 anchor="e",
                 wraplength=260,
                 justify="right").pack(side="right")

    def _salvar_perfil(self):
        nome = self.campo_nome.obter()
        email = self.campo_email.obter()
        if not nome or not email:
            self.mostrar_notificacao(
                "Preencha nome e e-mail.", "ERRO")
            return
        Configuracoes.USUARIO_NOME = nome
        Configuracoes.USUARIO_EMAIL = email
        self.mostrar_notificacao(
            "Perfil atualizado com sucesso.", "SUCESSO",
            titulo="Configuracoes salvas")

    def _recarregar(self):
        self.banco.carregar()
        self.banco.notificar_observadores()
        self.mostrar_notificacao("Dados recarregados.", "INFO")

    def _limpar_notificacoes(self):
        self.banco.notificacoes = []
        self.banco.salvar()
        self.banco.notificar_observadores()
        self.mostrar_notificacao(
            "Notificacoes limpas.", "AVISO")

    def _marcar_contatados(self):
        for l in self.banco.leads:
            if l.status == "LEAD":
                l.status = "NEGOCIACAO"
        self.banco.salvar()
        self.banco.notificar_observadores()
        self.mostrar_notificacao(
            "Leads marcados como em negociacao.", "SUCESSO")
