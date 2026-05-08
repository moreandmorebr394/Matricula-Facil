"""Painel de Aulas - cronograma."""
import tkinter as tk
from tkinter import ttk, messagebox

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.campo_entrada import CampoArredondado
from componentes.combo_arredondado import ComboArredondado
from componentes.notificacoes import NotificacaoFlutuante
from controladores.controlador_academico import ControladorTurma, ControladorAula
from utilitarios.validadores import formatar_data_progressivo


class PainelAulas(tk.Frame):

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
            bloco, text="Cadastrar Aula", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 12))

        turmas = ControladorTurma.listar()
        self._mapa_turmas = {
            f"{t['codigo']} - {t.get('curso', '')[:30]}": t["id"]
            for t in turmas
        }
        opcoes = list(self._mapa_turmas.keys()) or ["(sem turmas)"]

        self._lbl(bloco, "Turma *")
        self._combo_turma = ComboArredondado(
            bloco, opcoes=opcoes, valor_inicial=opcoes[0],
            largura=340, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_turma.pack(pady=4)

        self._lbl(bloco, "Título da aula *")
        self._campo_titulo = CampoArredondado(
            bloco, placeholder="Ex: Introdução à Anatomia",
            largura=340, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_titulo.pack(pady=4)

        self._lbl(bloco, "Descrição")
        bg_desc = tk.Frame(bloco, bg=tema.AMARELO_INPUT)
        bg_desc.pack(fill="x", pady=4)
        self._campo_desc = tk.Text(
            bg_desc, height=3, bg=tema.AMARELO_INPUT,
            fg=tema.AZUL_ESCURO, font=tema.fonte_corpo(10),
            relief="flat", bd=0, wrap="word", padx=10, pady=8,
        )
        self._campo_desc.pack(fill="both", expand=True, padx=2, pady=2)

        linha = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        linha.pack(fill="x", pady=4)

        col_d = tk.Frame(linha, bg=tema.BRANCO_PURO)
        col_d.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Label(col_d, text="Data", bg=tema.BRANCO_PURO,
                 fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10)).pack(anchor="w")
        self._campo_data = CampoArredondado(
            col_d, placeholder="15/03/2026", largura=160,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_data.pack()
        self._campo_data.widget_entry().bind(
            "<KeyRelease>", lambda _e: self._fmt_data(),
        )

        col_h = tk.Frame(linha, bg=tema.BRANCO_PURO)
        col_h.pack(side="left", fill="x", expand=True, padx=(4, 0))
        tk.Label(col_h, text="Horário", bg=tema.BRANCO_PURO,
                 fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10)).pack(anchor="w")
        self._campo_hora = CampoArredondado(
            col_h, placeholder="19:00 - 22:00", largura=160,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_hora.pack()

        self._lbl(bloco, "Professor")
        self._campo_prof = CampoArredondado(
            bloco, placeholder="Nome do professor",
            largura=340, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_prof.pack(pady=4)

        self._var_realizada = tk.IntVar(value=0)
        tk.Checkbutton(
            bloco, text=" Aula realizada", variable=self._var_realizada,
            bg=tema.BRANCO_PURO, fg=tema.AZUL_ESCURO,
            activebackground=tema.BRANCO_PURO, selectcolor=tema.BRANCO_PURO,
            font=tema.fonte_corpo(10), bd=0, highlightthickness=0,
        ).pack(anchor="w", pady=8)

        botoes = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        botoes.pack(fill="x", pady=(8, 0))
        BotaoArredondado(
            botoes, texto="Cancelar", comando=self._cancelar,
            cor_fundo=tema.CINZA_CLARO, cor_hover=tema.CINZA_BORDA,
            cor_press="#D5D7DF", cor_texto=tema.AZUL_ESCURO,
            largura=110, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left", padx=(0, 8))
        self._botao_salvar = BotaoArredondado(
            botoes, texto="Salvar Aula", comando=self._salvar,
            largura=140, altura=40, fonte=tema.fonte_destaque(11),
        )
        self._botao_salvar.pack(side="left")

    def _fmt_data(self):
        v = self._campo_data.obter_valor()
        nv = formatar_data_progressivo(v)
        if nv != v:
            self._campo_data.definir_valor(nv)
            self._campo_data.widget_entry().icursor("end")

    # =================================================================
    def _construir_tabela(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Aulas Cadastradas", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w")

        cols = ("id", "turma", "titulo", "data", "hora", "prof", "real")
        self._tabela = ttk.Treeview(
            bloco, columns=cols, show="headings",
            style="SF.Treeview", height=14,
        )
        for c, t, w, a in (
            ("id", "ID", 50, "center"),
            ("turma", "Turma", 120, "w"),
            ("titulo", "Título", 200, "w"),
            ("data", "Data", 100, "center"),
            ("hora", "Horário", 110, "center"),
            ("prof", "Professor", 140, "w"),
            ("real", "Realizada", 80, "center"),
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
        for a in ControladorAula.listar():
            self._tabela.insert(
                "", "end", iid=str(a["id"]),
                values=(
                    a["id"],
                    a.get("turma_codigo", "—"),
                    a.get("titulo", ""),
                    a.get("data", ""),
                    a.get("horario", ""),
                    a.get("professor", ""),
                    "\u2714" if a.get("realizada") else "—",
                ),
            )

    # =================================================================
    def _coletar(self) -> dict:
        chave = self._combo_turma.obter_valor()
        return {
            "turma_id": self._mapa_turmas.get(chave) or 0,
            "titulo": self._campo_titulo.obter_valor().strip(),
            "descricao": self._campo_desc.get("1.0", "end").strip(),
            "data": self._campo_data.obter_valor().strip(),
            "horario": self._campo_hora.obter_valor().strip(),
            "professor": self._campo_prof.obter_valor().strip(),
            "realizada": bool(self._var_realizada.get()),
        }

    def _salvar(self):
        dados = self._coletar()
        topo = self.winfo_toplevel()
        if self._em_edicao:
            sucesso, msg = ControladorAula.atualizar(self._em_edicao, dados)
        else:
            sucesso, msg, _id = ControladorAula.cadastrar(dados)
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._cancelar()
            self._popular()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")

    def _cancelar(self):
        for c in (self._campo_titulo, self._campo_data, self._campo_hora,
                  self._campo_prof):
            c.definir_valor("")
        self._campo_desc.delete("1.0", "end")
        self._var_realizada.set(0)
        self._em_edicao = None
        try:
            self._botao_salvar._texto = "Salvar Aula"
            self._botao_salvar._desenhar()
        except Exception:
            pass

    def _editar(self):
        sel = self._tabela.selection()
        if not sel:
            return
        id_a = int(sel[0])
        aula = next((x for x in ControladorAula.listar() if x["id"] == id_a), None)
        if not aula:
            return
        # tenta achar a chave do combo correspondente
        for chave, idt in self._mapa_turmas.items():
            if idt == aula.get("turma_id"):
                self._combo_turma.definir_valor(chave)
                break
        self._campo_titulo.definir_valor(aula.get("titulo") or "")
        self._campo_desc.delete("1.0", "end")
        self._campo_desc.insert("1.0", aula.get("descricao") or "")
        self._campo_data.definir_valor(aula.get("data") or "")
        self._campo_hora.definir_valor(aula.get("horario") or "")
        self._campo_prof.definir_valor(aula.get("professor") or "")
        self._var_realizada.set(1 if aula.get("realizada") else 0)
        self._em_edicao = id_a
        try:
            self._botao_salvar._texto = "Atualizar Aula"
            self._botao_salvar._desenhar()
        except Exception:
            pass

    def _excluir(self):
        sel = self._tabela.selection()
        if not sel:
            return
        if not messagebox.askyesno(
            "Confirmar", "Excluir a aula selecionada?",
            parent=self.winfo_toplevel(),
        ):
            return
        sucesso, msg = ControladorAula.excluir(int(sel[0]))
        topo = self.winfo_toplevel()
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._popular()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")
