"""Painel de Pagamentos - vinculados a vendas."""
import tkinter as tk
from tkinter import ttk, messagebox

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.campo_entrada import CampoArredondado
from componentes.combo_arredondado import ComboArredondado
from componentes.notificacoes import NotificacaoFlutuante
from controladores.controlador_academico import (
    ControladorVenda,
    ControladorPagamento,
)


METODOS = ("PIX", "Cartão", "Boleto", "Dinheiro", "Transferência")


class PainelPagamentos(tk.Frame):

    def __init__(self, mestre, dashboard=None):
        super().__init__(mestre, bg=tema.OFFWHITE)
        self.pack(fill="both", expand=True)
        self.dashboard = dashboard

        topo = tk.Frame(self, bg=tema.OFFWHITE)
        topo.pack(fill="x", padx=20, pady=(20, 10))
        topo.columnconfigure(0, weight=1, minsize=400)
        topo.columnconfigure(1, weight=2, minsize=520)

        form = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._construir_form(form)

        tab = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        tab.grid(row=0, column=1, sticky="nsew")
        self._construir_tabela(tab)

    # =================================================================
    def _construir_form(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Registrar Pagamento", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 12))

        # Carrega lista de vendas
        vendas = ControladorVenda.listar_vendas()
        self._mapa_vendas = {}
        for v in vendas:
            chave = (
                f"#{v['id']} - {v.get('aluno_nome', '—')} "
                f"(R$ {float(v.get('valor', 0)):.2f})"
            )
            self._mapa_vendas[chave] = v["id"]
        opcoes = list(self._mapa_vendas.keys()) or ["(nenhuma venda registrada)"]

        self._lbl(bloco, "Venda *")
        self._combo_venda = ComboArredondado(
            bloco, opcoes=opcoes, valor_inicial=opcoes[0],
            largura=340, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_venda.pack(pady=4)

        self._lbl(bloco, "Valor (R$) *")
        self._campo_valor = CampoArredondado(
            bloco, placeholder="0,00", largura=340,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_valor.pack(pady=4)

        self._lbl(bloco, "Método de pagamento")
        self._combo_metodo = ComboArredondado(
            bloco, opcoes=list(METODOS), valor_inicial=METODOS[0],
            largura=340, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_metodo.pack(pady=4)

        self._lbl(bloco, "Comprovante (referência)")
        self._campo_comp = CampoArredondado(
            bloco, placeholder="Ex: NF-001 / 1ª parcela", largura=340,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_comp.pack(pady=4)

        botoes = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        botoes.pack(fill="x", pady=(14, 0))
        BotaoArredondado(
            botoes, texto="Limpar", comando=self._limpar,
            cor_fundo=tema.CINZA_CLARO, cor_hover=tema.CINZA_BORDA,
            cor_press="#D5D7DF", cor_texto=tema.AZUL_ESCURO,
            largura=100, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left", padx=(0, 8))
        BotaoArredondado(
            botoes, texto="Confirmar Pagamento", comando=self._salvar,
            largura=180, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left")

    def _lbl(self, pai, texto):
        tk.Label(
            pai, text=texto, bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(10),
        ).pack(anchor="w", pady=(8, 0))

    # =================================================================
    def _construir_tabela(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        topo = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        topo.pack(fill="x")
        tk.Label(
            topo, text="Pagamentos Registrados", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(side="left")
        self._lbl_total = tk.Label(
            topo, text="", bg=tema.BRANCO_PURO,
            fg=tema.VERDE_SUCESSO, font=tema.fonte_destaque(11),
        )
        self._lbl_total.pack(side="right")

        cols = ("id", "venda", "aluno", "valor", "metodo", "comp", "data")
        self._tabela = ttk.Treeview(
            bloco, columns=cols, show="headings",
            style="SF.Treeview", height=14,
        )
        for c, t, w, a in (
            ("id", "ID", 50, "center"),
            ("venda", "Venda", 70, "center"),
            ("aluno", "Aluno", 180, "w"),
            ("valor", "Valor", 100, "e"),
            ("metodo", "Método", 100, "w"),
            ("comp", "Comprovante", 130, "w"),
            ("data", "Data", 110, "center"),
        ):
            self._tabela.heading(c, text=t)
            self._tabela.column(c, width=w, anchor=a)
        self._tabela.pack(fill="both", expand=True, pady=(8, 0))

        menu = tk.Menu(self._tabela, tearoff=0)
        menu.add_command(label="\U0001F5D1  Excluir", command=self._excluir)
        self._menu = menu
        self._tabela.bind("<Button-3>", self._menu_ctx)

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
        pgs = ControladorPagamento.listar()
        total = 0.0
        for p in pgs:
            v = float(p.get("valor") or 0)
            total += v
            self._tabela.insert(
                "", "end", iid=str(p["id"]),
                values=(
                    p["id"],
                    p.get("venda_id", "—"),
                    p.get("aluno_nome", "—"),
                    f"R$ {v:,.2f}".replace(",", "v")
                        .replace(".", ",").replace("v", "."),
                    p.get("metodo", ""),
                    p.get("comprovante", ""),
                    str(p.get("data_pagamento", ""))[:10],
                ),
            )
        self._lbl_total.configure(
            text=f"Total: R$ {total:,.2f}".replace(",", "v")
                .replace(".", ",").replace("v", "."),
        )

    # =================================================================
    def _limpar(self):
        for c in (self._campo_valor, self._campo_comp):
            c.definir_valor("")

    def _salvar(self):
        chave = self._combo_venda.obter_valor()
        venda_id = self._mapa_vendas.get(chave)
        if not venda_id:
            NotificacaoFlutuante.exibir(
                self.winfo_toplevel(),
                "Cadastre uma venda antes de registrar pagamentos.",
                tipo="erro",
            )
            return
        dados = {
            "venda_id": venda_id,
            "valor": (self._campo_valor.obter_valor() or "0").replace(",", "."),
            "metodo": self._combo_metodo.obter_valor(),
            "comprovante": self._campo_comp.obter_valor(),
        }
        sucesso, msg, _id = ControladorPagamento.registrar(dados)
        topo = self.winfo_toplevel()
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._limpar()
            self._popular()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")

    def _excluir(self):
        sel = self._tabela.selection()
        if not sel:
            return
        if not messagebox.askyesno(
            "Confirmar", "Excluir o pagamento?", parent=self.winfo_toplevel(),
        ):
            return
        sucesso, msg = ControladorPagamento.excluir(int(sel[0]))
        topo = self.winfo_toplevel()
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._popular()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")
