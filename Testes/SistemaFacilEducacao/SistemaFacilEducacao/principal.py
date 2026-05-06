"""Sistema Facil Educacao - CRM Educacional.

Ponto de entrada da aplicacao. Execute com:

    python3 principal.py

Construido com tkinter puro (sem dependencias externas).
"""
import os
import sys
import tkinter as tk

# Garante que o diretorio do script esteja no path
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
if DIR_BASE not in sys.path:
    sys.path.insert(0, DIR_BASE)

from componentes.barra_lateral import BarraLateral
from componentes.botao import BotaoPrimario, BotaoSecundario
from componentes.cabecalho import Cabecalho
from componentes.campo_entrada import CampoEntrada
from config.configuracoes import Configuracoes
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from utilitarios.animacoes import animar_aparecer
from utilitarios.notificacoes import GerenciadorNotificacoes

from telas import (
    TelaDashboard, TelaLeads, TelaVendas, TelaPagamentos,
    TelaTurmas, TelaAulas, TelaFrequencia, TelaFunilOrigem,
    TelaRelatorios, TelaConfiguracoes,
)


# Mapeamento de telas: chave da sidebar -> classe + (titulo, breadcrumb)
TELAS = {
    "dashboard":     (TelaDashboard,     "Cadastro do Aluno (Lead)",
                      "Leads › Novo Cadastro"),
    "leads":         (TelaLeads,         "Leads / Alunos",
                      "Gestao › Leads"),
    "vendas":        (TelaVendas,        "Vendas",
                      "Gestao › Vendas"),
    "pagamentos":    (TelaPagamentos,    "Pagamentos",
                      "Financeiro › Pagamentos"),
    "turmas":        (TelaTurmas,        "Turmas",
                      "Educacional › Turmas"),
    "aulas":         (TelaAulas,         "Aulas",
                      "Educacional › Aulas"),
    "frequencia":    (TelaFrequencia,    "Controle de Frequencia",
                      "Educacional › Frequencia"),
    "funil":         (TelaFunilOrigem,   "Funil de Origem",
                      "Analises › Funil"),
    "relatorios":    (TelaRelatorios,    "Relatorios",
                      "Analises › Relatorios"),
    "configuracoes": (TelaConfiguracoes, "Configuracoes",
                      "Sistema › Configuracoes"),
}


class Aplicacao:
    """Orquestrador principal da aplicacao."""

    def __init__(self):
        self.raiz = tk.Tk()
        self.raiz.title(Configuracoes.TITULO_JANELA)
        self.raiz.configure(bg=Cores.FUNDO_PRINCIPAL)
        self.raiz.geometry(
            f"{Configuracoes.LARGURA_INICIAL}x{Configuracoes.ALTURA_INICIAL}"
        )
        self.raiz.minsize(Configuracoes.LARGURA_MINIMA,
                          Configuracoes.ALTURA_MINIMA)

        # Aplica fontes
        Fontes.aplicar()

        # Banco
        self.banco = BancoDados()
        self.banco.adicionar_observador(self._sincronizar_header)

        # Notificacoes
        self.gerenciador_notif = GerenciadorNotificacoes(self.raiz)

        # Logo (carregada uma vez)
        self.logo_imagem = self._carregar_logo()

        # Layout: sidebar | (header + conteudo)
        self.sidebar = BarraLateral(
            self.raiz,
            ao_navegar=self.navegar_para,
            ao_sair=self._confirmar_sair,
            logo_imagem=self.logo_imagem,
        )
        self.sidebar.pack(side="left", fill="y")

        direita = tk.Frame(self.raiz, bg=Cores.FUNDO_PRINCIPAL)
        direita.pack(side="left", fill="both", expand=True)

        self.cabecalho = Cabecalho(
            direita,
            ao_clicar_notificacoes=self._abrir_notificacoes,
            ao_clicar_perfil=self._abrir_perfil,
        )
        self.cabecalho.pack(fill="x")

        self.conteudo = tk.Frame(direita, bg=Cores.FUNDO_PRINCIPAL)
        self.conteudo.pack(fill="both", expand=True)

        self._tela_atual = None
        self._sincronizar_header()
        self.navegar_para("dashboard")

    # ------------------------------------------------------------------
    # Logo
    # ------------------------------------------------------------------
    def _carregar_logo(self):
        try:
            if os.path.exists(Configuracoes.LOGO_PEQUENO):
                return tk.PhotoImage(file=Configuracoes.LOGO_PEQUENO)
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Navegacao
    # ------------------------------------------------------------------
    def navegar_para(self, chave: str):
        if chave not in TELAS:
            self._mostrar_notificacao(
                f"Tela '{chave}' nao implementada.", "AVISO")
            return

        # destroi tela anterior
        if self._tela_atual is not None:
            self._tela_atual.destroy()

        classe, titulo, breadcrumb = TELAS[chave]
        nova = classe(self.conteudo, banco=self.banco,
                      mostrar_notificacao=self._mostrar_notificacao,
                      navegar_para=self.navegar_para)
        nova.pack(fill="both", expand=True)
        self._tela_atual = nova

        # animacao fade-in
        try:
            animar_aparecer(nova)
        except Exception:
            pass

        self.cabecalho.atualizar_titulo(titulo, breadcrumb)
        self.sidebar.definir_ativo(chave)

    # ------------------------------------------------------------------
    # Sincroniza sino/quantidade
    # ------------------------------------------------------------------
    def _sincronizar_header(self):
        try:
            self.cabecalho.atualizar_quantidade_notificacoes(
                self.banco.notificacoes_nao_lidas())
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Notificacoes (toast + modal)
    # ------------------------------------------------------------------
    def _mostrar_notificacao(self, mensagem: str, tipo: str = "INFO",
                             titulo: str = ""):
        self.gerenciador_notif.mostrar(mensagem, tipo, titulo)

    def _abrir_notificacoes(self):
        win = tk.Toplevel(self.raiz)
        win.title("Notificacoes")
        win.configure(bg=Cores.CARD_FUNDO)
        win.geometry("440x520")
        win.transient(self.raiz)

        topo = tk.Frame(win, bg=Cores.CARD_FUNDO)
        topo.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(topo, text="🔔  Notificacoes",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO).pack(side="left")
        nlidas = self.banco.notificacoes_nao_lidas()
        tk.Label(topo, text=f"{nlidas} nao lidas",
                 bg=Cores.CARD_FUNDO, fg=Cores.BOTAO_PRIMARIO,
                 font=Fontes.PEQUENO_NEGRITO).pack(side="right")

        # lista
        lista = tk.Frame(win, bg=Cores.CARD_FUNDO)
        lista.pack(fill="both", expand=True, padx=20)

        if not self.banco.notificacoes:
            tk.Label(lista,
                     text="Nenhuma notificacao no momento.",
                     bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.CORPO).pack(pady=40)
        else:
            cores_tipo = {
                "SUCESSO": Cores.BOTAO_SUCESSO,
                "ERRO": Cores.BOTAO_PERIGO,
                "INFO": Cores.BOTAO_PRIMARIO,
                "AVISO": Cores.NOTIF_AVISO_FUNDO,
            }
            for n in self.banco.notificacoes[:15]:
                cor_lat = cores_tipo.get(n.tipo, Cores.BOTAO_PRIMARIO)
                cor_fundo = "#f8fafc" if n.lida else "#eef4ff"
                item = tk.Frame(lista, bg=cor_fundo)
                item.pack(fill="x", pady=3)

                tk.Frame(item, bg=cor_lat, width=4).pack(side="left",
                                                         fill="y")
                inner = tk.Frame(item, bg=cor_fundo)
                inner.pack(side="left", fill="both", expand=True,
                           padx=10, pady=8)
                tk.Label(inner, text=n.titulo, bg=cor_fundo,
                         fg=Cores.TEXTO_PRIMARIO,
                         font=Fontes.PEQUENO_NEGRITO,
                         anchor="w").pack(anchor="w")
                tk.Label(inner, text=n.mensagem, bg=cor_fundo,
                         fg=Cores.TEXTO_SECUNDARIO,
                         font=Fontes.MICRO,
                         anchor="w", wraplength=360,
                         justify="left").pack(anchor="w")
                tk.Label(inner, text=n.data, bg=cor_fundo,
                         fg=Cores.TEXTO_TERCIARIO,
                         font=Fontes.MICRO,
                         anchor="w").pack(anchor="w", pady=(2, 0))

        # botoes
        botoes = tk.Frame(win, bg=Cores.CARD_FUNDO)
        botoes.pack(fill="x", padx=20, pady=14)
        BotaoSecundario(botoes, texto="Fechar",
                        comando=win.destroy,
                        largura=100).pack(side="right", padx=(6, 0))

        def marcar():
            self.banco.marcar_todas_notificacoes_lidas()
            self._mostrar_notificacao(
                "Notificacoes marcadas como lidas.", "SUCESSO")
            win.destroy()

        BotaoPrimario(botoes, texto="Marcar todas como lidas",
                      comando=marcar, largura=200).pack(side="right")

    # ------------------------------------------------------------------
    # Perfil (modal)
    # ------------------------------------------------------------------
    def _abrir_perfil(self):
        win = tk.Toplevel(self.raiz)
        win.title("Perfil do Administrador")
        win.configure(bg=Cores.CARD_FUNDO)
        win.geometry("420x460")
        win.transient(self.raiz)

        # avatar
        cnv = tk.Canvas(win, width=88, height=88, bg=Cores.CARD_FUNDO,
                        highlightthickness=0)
        cnv.pack(pady=(24, 8))
        cnv.create_oval(2, 2, 86, 86, fill=Cores.LOGO_AZUL, outline="")
        cnv.create_text(44, 44, text="A",
                        fill=Cores.LOGO_AMARELO,
                        font=(Fontes.FAMILIA, 36, "bold"))

        tk.Label(win, text=Configuracoes.USUARIO_NOME,
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO).pack()
        tk.Label(win, text=Configuracoes.USUARIO_EMAIL,
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO).pack(pady=(0, 16))

        # opcoes
        body = tk.Frame(win, bg=Cores.CARD_FUNDO)
        body.pack(fill="x", padx=24, pady=10)

        for icone, texto, acao in [
            ("⚙", "Editar perfil",
             lambda: (win.destroy(),
                      self.navegar_para("configuracoes"))),
            ("📊", "Ver relatorios",
             lambda: (win.destroy(),
                      self.navegar_para("relatorios"))),
            ("🔔", "Notificacoes",
             lambda: (win.destroy(),
                      self._abrir_notificacoes())),
            ("ℹ", "Sobre o sistema",
             lambda: self._mostrar_notificacao(
                 f"{Configuracoes.NOME_SISTEMA} v{Configuracoes.VERSAO}",
                 "INFO", titulo="Sobre")),
        ]:
            l = tk.Frame(body, bg="#f8fafc", cursor="hand2")
            l.pack(fill="x", pady=3)
            tk.Label(l, text=icone, bg="#f8fafc",
                     fg=Cores.BOTAO_PRIMARIO,
                     font=(Fontes.FAMILIA, 14)).pack(
                side="left", padx=12, pady=10)
            tk.Label(l, text=texto, bg="#f8fafc",
                     fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO_NEGRITO).pack(
                side="left", padx=4)
            tk.Label(l, text="›", bg="#f8fafc",
                     fg=Cores.TEXTO_TERCIARIO,
                     font=(Fontes.FAMILIA, 14)).pack(
                side="right", padx=12)
            for w in (l, *l.winfo_children()):
                w.bind("<Button-1>", lambda e, a=acao: a())

        # sair
        tk.Frame(win, bg=Cores.CARD_BORDA, height=1).pack(
            fill="x", padx=24, pady=12)

        def sair():
            win.destroy()
            self._confirmar_sair()

        BotaoSecundario(win, texto="Sair do sistema",
                        comando=sair, largura=200).pack(pady=10)

    # ------------------------------------------------------------------
    # Sair (confirmacao)
    # ------------------------------------------------------------------
    def _confirmar_sair(self):
        win = tk.Toplevel(self.raiz)
        win.title("Confirmar saida")
        win.configure(bg=Cores.CARD_FUNDO)
        win.geometry("380x200")
        win.transient(self.raiz)
        win.grab_set()

        tk.Label(win, text="⚠", bg=Cores.CARD_FUNDO,
                 fg=Cores.NOTIF_AVISO_FUNDO,
                 font=(Fontes.FAMILIA, 30, "bold")).pack(pady=(20, 6))
        tk.Label(win, text="Deseja realmente sair?",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO_CARD).pack()
        tk.Label(win,
                 text="Os dados ja foram salvos automaticamente.",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO).pack(pady=(2, 14))

        botoes = tk.Frame(win, bg=Cores.CARD_FUNDO)
        botoes.pack()
        BotaoSecundario(botoes, texto="Cancelar",
                        comando=win.destroy,
                        largura=110).pack(side="left", padx=6)
        BotaoPrimario(botoes, texto="Sair",
                      comando=lambda: (self.banco.salvar(),
                                       self.raiz.destroy()),
                      largura=110).pack(side="left", padx=6)

    # ------------------------------------------------------------------
    def executar(self):
        self.raiz.mainloop()


def principal():
    app = Aplicacao()
    app.executar()


if __name__ == "__main__":
    principal()
