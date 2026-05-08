"""Painel de Turmas - cadastro e gestão."""
import tkinter as tk
from tkinter import ttk, messagebox

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.campo_entrada import CampoArredondado
from componentes.combo_arredondado import ComboArredondado
from componentes.notificacoes import NotificacaoFlutuante
from controladores.controlador_aluno import CURSOS_DISPONIVEIS
from controladores.controlador_academico import ControladorTurma
from utilitarios.validadores import formatar_data_progressivo


TURNOS = ("MANHA", "TARDE", "NOITE", "INTEGRAL")


class PainelTurmas(tk.Frame):

    def __init__(self, mestre, dashboard=None):
        super().__init__(mestre, bg=tema.OFFWHITE)
        self.pack(fill="both", expand=True)
        self.dashboard = dashboard
        self._em_edicao = None

        topo = tk.Frame(self, bg=tema.OFFWHITE)
        topo.pack(fill="x", padx=20, pady=(20, 10))
        topo.columnconfigure(0, weight=1, minsize=400)
        topo.columnconfigure(1, weight=2, minsize=520)

        f = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        f.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._construir_form(f)

        t = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        t.grid(row=0, column=1, sticky="nsew")
        self._construir_tabela(t)

    def _lbl(self, pai, texto):
        tk.Label(
            pai, text=texto, bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(10),
        ).pack(anchor="w", pady=(8, 0))

    def _construir_form(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Cadastrar Turma", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 12))

        self._lbl(bloco, "Curso *")
        self._combo_curso = ComboArredondado(
            bloco, opcoes=list(CURSOS_DISPONIVEIS),
            valor_inicial=CURSOS_DISPONIVEIS[0],
            largura=340, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_curso.pack(pady=4)

        self._lbl(bloco, "Turno")
        self._combo_turno = ComboArredondado(
            bloco, opcoes=list(TURNOS), valor_inicial="NOITE",
            largura=340, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_turno.pack(pady=4)

        linha_datas = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        linha_datas.pack(fill="x", pady=4)

        col_e = tk.Frame(linha_datas, bg=tema.BRANCO_PURO)
        col_e.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Label(
            col_e, text="Início", bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
        ).pack(anchor="w")
        self._campo_inicio = CampoArredondado(
            col_e, placeholder="01/03/2026", largura=160,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_inicio.pack()
        self._campo_inicio.widget_entry().bind(
            "<KeyRelease>", lambda _e: self._fmt(self._campo_inicio),
        )

        col_d = tk.Frame(linha_datas, bg=tema.BRANCO_PURO)
        col_d.pack(side="left", fill="x", expand=True, padx=(4, 0))
        tk.Label(
            col_d, text="Término", bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
        ).pack(anchor="w")
        self._campo_fim = CampoArredondado(
            col_d, placeholder="01/12/2026", largura=160,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_fim.pack()
        self._campo_fim.widget_entry().bind(
            "<KeyRelease>", lambda _e: self._fmt(self._campo_fim),
        )

        self._lbl(bloco, "Capacidade")
        self._campo_cap = CampoArredondado(
            bloco, placeholder="30", largura=340,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_cap.pack(pady=4)

        self._lbl(bloco, "Professor")
        self._campo_prof = CampoArredondado(
            bloco, placeholder="Nome do professor", largura=340,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_prof.pack(pady=4)

        self._lbl(bloco, "Sala")
        self._campo_sala = CampoArredondado(
            bloco, placeholder="Sala 12", largura=340,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_sala.pack(pady=4)

        botoes = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        botoes.pack(fill="x", pady=(14, 0))
        BotaoArredondado(
            botoes, texto="Cancelar", comando=self._cancelar,
            cor_fundo=tema.CINZA_CLARO, cor_hover=tema.CINZA_BORDA,
            cor_press="#D5D7DF", cor_texto=tema.AZUL_ESCURO,
            largura=110, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left", padx=(0, 8))
        self._botao_salvar = BotaoArredondado(
            botoes, texto="Criar Turma", comando=self._salvar,
            largura=140, altura=40, fonte=tema.fonte_destaque(11),
        )
        self._botao_salvar.pack(side="left")

    def _fmt(self, campo):
        v = campo.obter_valor()
        nv = formatar_data_progressivo(v)
        if nv != v:
            campo.definir_valor(nv)
            campo.widget_entry().icursor("end")

    # =================================================================
    def _construir_tabela(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Turmas Cadastradas", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w")

        cols = ("id", "codigo", "curso", "turno", "inicio", "fim", "cap", "prof")
        self._tabela = ttk.Treeview(
            bloco, columns=cols, show="headings",
            style="SF.Treeview", height=14,
        )
        for c, t, w, a in (
            ("id", "ID", 50, "center"),
            ("codigo", "Código", 100, "w"),
            ("curso", "Curso", 180, "w"),
            ("turno", "Turno", 80, "center"),
            ("inicio", "Início", 90, "center"),
            ("fim", "Fim", 90, "center"),
            ("cap", "Capacidade", 90, "center"),
            ("prof", "Professor", 140, "w"),
        ):
            self._tabela.heading(c, text=t)
            self._tabela.column(c, width=w, anchor=a)
        self._tabela.pack(fill="both", expand=True, pady=(8, 0))

        menu = tk.Menu(self._tabela, tearoff=0)
        menu.add_command(label="\u270E Editar", command=self._editar)
        menu.add_command(label="\U0001F5D1  Excluir", command=self._excluir)
        self._menu = menu
        self._tabela.bind("<Button-3>", self._menu_ctx)
        self._tabela.bind("<Double-1>", lambda _e: self._editar())

        self._popular()

    def _menu_ctx(self, evento):
        item = self._tabela.identify_row(evento.y)
        if item:
            self._tabela.selection_set(item)
            try:
                self._menu.tk_popup(evento.x_root, evento.y_root)
            finally:
                self._menu.grab_release()

    def _popular(self):
        for i in self._tabela.get_children():
            self._tabela.delete(i)
        for t in ControladorTurma.listar():
            self._tabela.insert(
                "", "end", iid=str(t["id"]),
                values=(
                    t["id"], t.get("codigo", ""), t.get("curso", ""),
                    t.get("turno", ""), t.get("data_inicio", ""),
                    t.get("data_fim", ""), t.get("capacidade", 0),
                    t.get("professor", ""),
                ),
            )

    # =================================================================
    def _coletar(self) -> dict:
        return {
            "curso": self._combo_curso.obter_valor(),
            "turno": self._combo_turno.obter_valor(),
            "data_inicio": self._campo_inicio.obter_valor().strip(),
            "data_fim": self._campo_fim.obter_valor().strip(),
            "capacidade": self._campo_cap.obter_valor() or "30",
            "professor": self._campo_prof.obter_valor().strip(),
            "sala": self._campo_sala.obter_valor().strip(),
        }

    def _salvar(self):
        dados = self._coletar()
        topo = self.winfo_toplevel()
        if self._em_edicao:
            sucesso, msg = ControladorTurma.atualizar(self._em_edicao, dados)
        else:
            sucesso, msg, _id = ControladorTurma.cadastrar(dados)
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._cancelar()
            self._popular()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")

    def _cancelar(self):
        for c in (self._campo_inicio, self._campo_fim, self._campo_cap,
                  self._campo_prof, self._campo_sala):
            c.definir_valor("")
        self._em_edicao = None
        try:
            self._botao_salvar._texto = "Criar Turma"
            self._botao_salvar._desenhar()
        except Exception:
            pass

    def _editar(self):
        sel = self._tabela.selection()
        if not sel:
            return
        id_t = int(sel[0])
        turma = next(
            (x for x in ControladorTurma.listar() if x["id"] == id_t), None,
        )
        if not turma:
            return
        self._combo_curso.definir_valor(turma.get("curso") or CURSOS_DISPONIVEIS[0])
        self._combo_turno.definir_valor(turma.get("turno") or "MANHA")
        self._campo_inicio.definir_valor(turma.get("data_inicio") or "")
        self._campo_fim.definir_valor(turma.get("data_fim") or "")
        self._campo_cap.definir_valor(str(turma.get("capacidade") or 30))
        self._campo_prof.definir_valor(turma.get("professor") or "")
        self._campo_sala.definir_valor(turma.get("sala") or "")
        self._em_edicao = id_t
        try:
            self._botao_salvar._texto = "Atualizar Turma"
            self._botao_salvar._desenhar()
        except Exception:
            pass

    def _excluir(self):
        sel = self._tabela.selection()
        if not sel:
            return
        if not messagebox.askyesno(
            "Confirmar", "Excluir a turma selecionada?",
            parent=self.winfo_toplevel(),
        ):
            return
        sucesso, msg = ControladorTurma.excluir(int(sel[0]))
        topo = self.winfo_toplevel()
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._popular()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")
