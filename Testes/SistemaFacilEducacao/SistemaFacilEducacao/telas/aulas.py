"""Tela de Aulas: agenda e gerenciamento de aulas."""
import tkinter as tk
from typing import Callable

from componentes.botao import BotaoPrimario, BotaoSecundario, BotaoSucesso
from componentes.campo_entrada import CampoEntrada, CampoSelecao
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from dados.modelos import Aula


class TelaAulas(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)

        topo = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        topo.pack(fill="x", pady=(0, 16))
        tk.Label(topo, text="Agenda de Aulas", bg=Cores.FUNDO_PRINCIPAL,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO).pack(side="left")
        BotaoPrimario(topo, texto="+  Nova Aula",
                      comando=self._modal_criar,
                      largura=130).pack(side="right")

        # 2 colunas: realizadas / agendadas (em outro frame com grid)
        grid = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=1, uniform="a")
        grid.grid_columnconfigure(1, weight=1, uniform="a")
        grid.grid_rowconfigure(0, weight=1)

        agendadas = CardComCabecalho(grid, titulo="Aulas Agendadas",
                                     icone="📅")
        agendadas.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.area_agend = agendadas.conteudo()
        self.area_agend.configure(bg=Cores.CARD_FUNDO)

        realizadas = CardComCabecalho(grid, titulo="Aulas Realizadas",
                                      icone="✓")
        realizadas.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.area_real = realizadas.conteudo()
        self.area_real.configure(bg=Cores.CARD_FUNDO)

        self._renderizar()

    def _renderizar(self):
        for w in self.area_agend.winfo_children():
            w.destroy()
        for w in self.area_real.winfo_children():
            w.destroy()

        agendadas = [a for a in self.banco.aulas if not a.realizada]
        realizadas = [a for a in self.banco.aulas if a.realizada]

        self._render_lista(self.area_agend, agendadas, False)
        self._render_lista(self.area_real, realizadas, True)

    def _render_lista(self, parent, aulas, ja_realizada):
        if not aulas:
            msg = ("Nenhuma aula realizada ainda." if ja_realizada
                   else "Sem aulas agendadas.\nClique em 'Nova Aula'.")
            tk.Label(parent, text=msg, bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.CORPO,
                     justify="center").pack(pady=50)
            return

        for a in aulas:
            self._item_aula(parent, a, ja_realizada).pack(fill="x", pady=4)

    def _item_aula(self, parent, aula: Aula, ja_realizada: bool):
        cor_fundo = "#f8fafc"
        item = tk.Frame(parent, bg=cor_fundo)

        # barra lateral colorida
        cor_barra = (Cores.BOTAO_SUCESSO if ja_realizada
                     else Cores.BOTAO_PRIMARIO)
        tk.Frame(item, bg=cor_barra, width=4).pack(side="left", fill="y")

        info = tk.Frame(item, bg=cor_fundo)
        info.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        # turma
        turma = next((t for t in self.banco.turmas
                      if t.id == aula.turma_id), None)
        nome_turma = turma.nome if turma else "Turma desconhecida"

        tk.Label(info, text=aula.titulo, bg=cor_fundo,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.PEQUENO_NEGRITO,
                 anchor="w").pack(anchor="w")
        tk.Label(info, text=f"📚  {nome_turma}",
                 bg=cor_fundo, fg=Cores.TEXTO_SECUNDARIO,
                 font=Fontes.MICRO,
                 anchor="w").pack(anchor="w", pady=(2, 0))

        sub = tk.Frame(info, bg=cor_fundo)
        sub.pack(anchor="w", pady=(4, 0))
        tk.Label(sub, text=f"📅  {aula.data}  ", bg=cor_fundo,
                 fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.MICRO).pack(side="left")
        tk.Label(sub, text=f"🕐  {aula.horario}", bg=cor_fundo,
                 fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.MICRO).pack(side="left")

        if aula.descricao:
            tk.Label(info, text=aula.descricao, bg=cor_fundo,
                     fg=Cores.TEXTO_SECUNDARIO,
                     font=Fontes.MICRO,
                     wraplength=320, justify="left",
                     anchor="w").pack(anchor="w", pady=(4, 0))

        # acoes
        if not ja_realizada:
            BotaoSucesso(item, texto="Marcar realizada",
                         comando=lambda a=aula: self._marcar_realizada(a),
                         largura=140).pack(side="right", padx=10)
        else:
            tk.Label(item, text="✓ Concluida",
                     bg=cor_fundo, fg=Cores.STATUS_PAGO_TEXTO,
                     font=Fontes.PEQUENO_NEGRITO).pack(side="right", padx=14)
        return item

    def _marcar_realizada(self, aula: Aula):
        aula.realizada = True
        self.banco.salvar()
        self.banco.notificar_observadores()
        self.mostrar_notificacao(
            f"Aula '{aula.titulo}' marcada como realizada.",
            "SUCESSO", titulo="Aula concluida")
        self._renderizar()

    def _modal_criar(self):
        if not self.banco.turmas:
            self.mostrar_notificacao(
                "Cadastre uma turma antes de criar aulas.", "AVISO")
            return

        win = tk.Toplevel(self)
        win.title("Nova Aula")
        win.configure(bg=Cores.CARD_FUNDO)
        win.geometry("440x500")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="Agendar Nova Aula", bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO).pack(pady=(20, 14), padx=24, anchor="w")

        body = tk.Frame(win, bg=Cores.CARD_FUNDO)
        body.pack(fill="both", expand=True, padx=24)

        ctit = CampoEntrada(body, rotulo="Titulo da aula",
                            obrigatorio=True,
                            placeholder="Ex.: Introducao ao SEO")
        ctit.pack(fill="x", pady=4)
        cturma = CampoSelecao(body, rotulo="Turma",
                              opcoes=[t.nome for t in self.banco.turmas],
                              obrigatorio=True)
        cturma.pack(fill="x", pady=4)
        cprof = CampoEntrada(body, rotulo="Professor",
                             placeholder="Nome do professor")
        cprof.pack(fill="x", pady=4)
        cdata = CampoEntrada(body, rotulo="Data", placeholder="dd/mm/aaaa",
                             obrigatorio=True)
        cdata.pack(fill="x", pady=4)
        chor = CampoEntrada(body, rotulo="Horario", placeholder="Ex.: 19h")
        chor.pack(fill="x", pady=4)
        cdesc = CampoEntrada(body, rotulo="Descricao",
                             placeholder="Conteudo da aula")
        cdesc.pack(fill="x", pady=4)

        botoes = tk.Frame(win, bg=Cores.CARD_FUNDO)
        botoes.pack(fill="x", padx=24, pady=18)
        BotaoSecundario(botoes, texto="Cancelar",
                        comando=win.destroy,
                        largura=110).pack(side="right", padx=(6, 0))

        def salvar():
            tit = ctit.obter()
            tnome = cturma.obter()
            data = cdata.obter()
            if not tit or not tnome or not data:
                self.mostrar_notificacao(
                    "Preencha titulo, turma e data.", "ERRO")
                return
            turma = next((t for t in self.banco.turmas
                          if t.nome == tnome), None)
            a = Aula(turma_id=turma.id if turma else 0,
                     titulo=tit, descricao=cdesc.obter(),
                     data=data, horario=chor.obter() or "19h",
                     professor=cprof.obter() or (turma.professor if turma
                                                 else ""),
                     realizada=False)
            self.banco.adicionar_aula(a)
            self.mostrar_notificacao(
                f"Aula '{tit}' agendada.", "SUCESSO",
                titulo="Aula criada")
            win.destroy()
            self._renderizar()

        BotaoPrimario(botoes, texto="Agendar Aula",
                      comando=salvar, largura=140).pack(side="right")
