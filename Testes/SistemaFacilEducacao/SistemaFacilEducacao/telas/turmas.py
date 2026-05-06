"""Tela de Turmas: cards de turmas, criar e gerenciar."""
import tkinter as tk
from typing import Callable

from componentes.botao import BotaoPrimario, BotaoSecundario
from componentes.campo_entrada import CampoEntrada, CampoSelecao
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from dados.modelos import Turma


CURSOS = ["Marketing Digital", "Social Media", "Trafego Pago",
          "Design Grafico", "Programacao Web", "UX/UI Design"]


class TelaTurmas(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)

        # cabecalho
        topo = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        topo.pack(fill="x", pady=(0, 16))
        tk.Label(topo, text="Turmas Ativas", bg=Cores.FUNDO_PRINCIPAL,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO).pack(side="left")
        BotaoPrimario(topo, texto="+  Nova Turma",
                      comando=self._modal_criar_turma,
                      largura=140).pack(side="right")

        # grid de turmas
        grid = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        grid.pack(fill="both", expand=True)
        self.area_grid = grid
        self._renderizar_turmas()

    def _renderizar_turmas(self):
        for w in self.area_grid.winfo_children():
            w.destroy()

        if not self.banco.turmas:
            tk.Label(self.area_grid,
                     text="Nenhuma turma cadastrada.\n"
                          "Clique em 'Nova Turma' para comecar.",
                     bg=Cores.FUNDO_PRINCIPAL, fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.CORPO,
                     justify="center").pack(pady=80)
            return

        colunas = 3
        for i in range(colunas):
            self.area_grid.grid_columnconfigure(i, weight=1, uniform="t")

        for idx, turma in enumerate(self.banco.turmas):
            r, c = divmod(idx, colunas)
            self._card_turma(self.area_grid, turma).grid(
                row=r, column=c, padx=8, pady=8, sticky="nsew")

    def _card_turma(self, parent, turma: Turma):
        card = Card(parent, padding=20)
        c = card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)

        # faixa colorida
        cor_curso = self._cor_curso(turma.curso)
        faixa = tk.Frame(c, bg=cor_curso, height=4)
        faixa.pack(fill="x", pady=(0, 12))

        # status
        topo = tk.Frame(c, bg=Cores.CARD_FUNDO)
        topo.pack(fill="x")
        tk.Label(topo, text=turma.curso, bg=Cores.CARD_FUNDO,
                 fg=cor_curso, font=Fontes.MICRO_NEGRITO).pack(side="left")
        st_fundo = (Cores.STATUS_PAGO_FUNDO if turma.status == "ATIVA"
                    else Cores.STATUS_NAO_PAGO_FUNDO)
        st_txt = (Cores.STATUS_PAGO_TEXTO if turma.status == "ATIVA"
                  else Cores.STATUS_NAO_PAGO_TEXTO)
        tk.Label(topo, text=f"  {turma.status}  ", bg=st_fundo,
                 fg=st_txt, font=Fontes.MICRO_NEGRITO,
                 padx=2).pack(side="right")

        # nome
        tk.Label(c, text=turma.nome, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO_CARD,
                 anchor="w", wraplength=240,
                 justify="left").pack(anchor="w", pady=(8, 12), fill="x")

        # info
        for icone, texto in [
            ("👨‍🏫", turma.professor or "Sem professor"),
            ("🕐", turma.horario or "Horario a definir"),
            ("📅", f"Inicio: {turma.data_inicio or 'a definir'}"),
        ]:
            l = tk.Frame(c, bg=Cores.CARD_FUNDO)
            l.pack(fill="x", pady=2)
            tk.Label(l, text=icone, bg=Cores.CARD_FUNDO,
                     font=(Fontes.FAMILIA, 11)).pack(side="left", padx=(0, 6))
            tk.Label(l, text=texto, bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_SECUNDARIO,
                     font=Fontes.PEQUENO,
                     anchor="w").pack(side="left", fill="x")

        # ocupacao
        ocupados = len(turma.alunos or [])
        capac = max(turma.capacidade, 1)
        pct = ocupados / capac
        sep = tk.Frame(c, bg=Cores.CARD_BORDA, height=1)
        sep.pack(fill="x", pady=(12, 8))

        tk.Label(c, text=f"Alunos: {ocupados} / {capac}",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_SECUNDARIO,
                 font=Fontes.PEQUENO_NEGRITO,
                 anchor="w").pack(anchor="w")

        barra = tk.Canvas(c, height=8, bg=Cores.BOTAO_SECUNDARIO,
                          highlightthickness=0)
        barra.pack(fill="x", pady=(4, 12))
        barra.update_idletasks()
        # animacao da barra
        self._animar_barra(barra, pct, cor_curso)

        # botoes acao
        acoes = tk.Frame(c, bg=Cores.CARD_FUNDO)
        acoes.pack(fill="x")
        BotaoSecundario(acoes, texto="Ver Alunos",
                        comando=lambda t=turma: self._modal_alunos(t),
                        largura=110).pack(side="left", padx=(0, 6))
        BotaoPrimario(acoes, texto="Adicionar",
                      comando=lambda t=turma: self._modal_add_aluno(t),
                      largura=110).pack(side="left")
        return card

    def _animar_barra(self, canvas, pct, cor, passo=0):
        passos = 18
        if passo == 0:
            canvas.delete("preench")
        if passo > passos:
            return
        atual = pct * (passo / passos)
        largura = canvas.winfo_width() or 200
        canvas.delete("preench")
        canvas.create_rectangle(
            0, 0, max(2, int(largura * atual)), 8,
            fill=cor, outline="", tags="preench")
        canvas.after(18, lambda: self._animar_barra(
            canvas, pct, cor, passo + 1))

    def _cor_curso(self, curso):
        m = {
            "Marketing Digital": Cores.FUNIL_VISITANTES,
            "Social Media": Cores.FUNIL_LEADS,
            "Trafego Pago": Cores.FUNIL_NEGOCIACOES,
            "Design Grafico": Cores.FUNIL_VENDAS,
            "Programacao Web": Cores.FUNIL_ALUNOS,
            "UX/UI Design": Cores.PIZZA_OUTROS,
        }
        return m.get(curso, Cores.BOTAO_PRIMARIO)

    # ------------------------------------------------------------------
    def _modal_criar_turma(self):
        win = tk.Toplevel(self)
        win.title("Nova Turma")
        win.configure(bg=Cores.CARD_FUNDO)
        win.geometry("440x540")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="Criar Nova Turma", bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO).pack(pady=(20, 14), padx=24, anchor="w")

        body = tk.Frame(win, bg=Cores.CARD_FUNDO)
        body.pack(fill="both", expand=True, padx=24, pady=4)

        cnome = CampoEntrada(body, rotulo="Nome da turma",
                             obrigatorio=True,
                             placeholder="Ex.: Marketing Digital - Turma C")
        cnome.pack(fill="x", pady=4)
        ccurso = CampoSelecao(body, rotulo="Curso", opcoes=CURSOS,
                              obrigatorio=True)
        ccurso.pack(fill="x", pady=4)
        cprof = CampoEntrada(body, rotulo="Professor responsavel",
                             placeholder="Ex.: Prof. Roberto Almeida")
        cprof.pack(fill="x", pady=4)
        chor = CampoEntrada(body, rotulo="Horario",
                            placeholder="Ex.: Seg/Qua/Sex 19h-21h")
        chor.pack(fill="x", pady=4)
        ccap = CampoEntrada(body, rotulo="Capacidade", placeholder="30")
        ccap.pack(fill="x", pady=4)
        cdata = CampoEntrada(body, rotulo="Data de inicio",
                             placeholder="dd/mm/aaaa")
        cdata.pack(fill="x", pady=4)

        botoes = tk.Frame(win, bg=Cores.CARD_FUNDO)
        botoes.pack(fill="x", padx=24, pady=18)
        BotaoSecundario(botoes, texto="Cancelar",
                        comando=win.destroy,
                        largura=110).pack(side="right", padx=(8, 0))

        def salvar():
            nome = cnome.obter()
            curso = ccurso.obter()
            if not nome or not curso:
                self.mostrar_notificacao(
                    "Preencha nome e curso.", "ERRO")
                return
            try:
                cap = int(ccap.obter() or 30)
            except ValueError:
                cap = 30
            t = Turma(nome=nome, curso=curso,
                      professor=cprof.obter(), horario=chor.obter(),
                      capacidade=cap, data_inicio=cdata.obter(),
                      status="ATIVA")
            self.banco.adicionar_turma(t)
            self.mostrar_notificacao(f"Turma '{nome}' criada!",
                                     "SUCESSO", titulo="Nova turma")
            win.destroy()
            self._renderizar_turmas()

        BotaoPrimario(botoes, texto="Salvar Turma",
                      comando=salvar, largura=140).pack(side="right")

    def _modal_alunos(self, turma: Turma):
        win = tk.Toplevel(self)
        win.title(f"Alunos - {turma.nome}")
        win.configure(bg=Cores.CARD_FUNDO)
        win.geometry("440x420")
        win.transient(self.winfo_toplevel())

        tk.Label(win, text=turma.nome, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO).pack(pady=(18, 6), padx=24, anchor="w")
        tk.Label(win,
                 text=f"{len(turma.alunos)} aluno(s) matriculado(s)",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO).pack(padx=24, anchor="w")

        body = tk.Frame(win, bg=Cores.CARD_FUNDO)
        body.pack(fill="both", expand=True, padx=24, pady=14)

        if not turma.alunos:
            tk.Label(body, text="Nenhum aluno matriculado.",
                     bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.CORPO).pack(pady=40)
        else:
            for nome in turma.alunos:
                linha = tk.Frame(body, bg="#f8fafc")
                linha.pack(fill="x", pady=3)
                tk.Label(linha, text="👤  " + nome,
                         bg="#f8fafc", fg=Cores.TEXTO_PRIMARIO,
                         font=Fontes.PEQUENO_NEGRITO,
                         anchor="w").pack(side="left", padx=10, pady=8)

        BotaoPrimario(win, texto="Fechar",
                      comando=win.destroy,
                      largura=110).pack(pady=14)

    def _modal_add_aluno(self, turma: Turma):
        win = tk.Toplevel(self)
        win.title(f"Adicionar aluno - {turma.nome}")
        win.configure(bg=Cores.CARD_FUNDO)
        win.geometry("420x260")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="Adicionar aluno a turma",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO_CARD).pack(pady=(18, 4),
                                               padx=20, anchor="w")
        tk.Label(win, text=turma.nome, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO).pack(padx=20, anchor="w")

        nomes_leads = [l.nome for l in self.banco.leads]
        body = tk.Frame(win, bg=Cores.CARD_FUNDO)
        body.pack(fill="x", padx=20, pady=14)

        if nomes_leads:
            campo = CampoSelecao(body, rotulo="Selecionar aluno",
                                 opcoes=nomes_leads, obrigatorio=True)
        else:
            campo = CampoEntrada(body, rotulo="Nome do aluno",
                                 obrigatorio=True,
                                 placeholder="Digite o nome")
        campo.pack(fill="x")

        botoes = tk.Frame(win, bg=Cores.CARD_FUNDO)
        botoes.pack(fill="x", padx=20, pady=14)
        BotaoSecundario(botoes, texto="Cancelar",
                        comando=win.destroy,
                        largura=110).pack(side="right", padx=(6, 0))

        def confirmar():
            nome = campo.obter().strip()
            if not nome:
                self.mostrar_notificacao("Selecione um aluno.", "ERRO")
                return
            if len(turma.alunos) >= turma.capacidade:
                self.mostrar_notificacao(
                    "Turma esta na capacidade maxima.", "AVISO")
                return
            if nome in turma.alunos:
                self.mostrar_notificacao(
                    f"{nome} ja esta nesta turma.", "AVISO")
                return
            turma.alunos.append(nome)
            self.banco.salvar()
            self.banco.notificar_observadores()
            self.mostrar_notificacao(
                f"{nome} adicionado(a) a turma.", "SUCESSO")
            win.destroy()
            self._renderizar_turmas()

        BotaoPrimario(botoes, texto="Adicionar",
                      comando=confirmar, largura=120).pack(side="right")
