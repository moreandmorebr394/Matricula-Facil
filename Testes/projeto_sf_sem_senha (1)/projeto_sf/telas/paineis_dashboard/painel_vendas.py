"""Painel de Vendas - Registro e gestão."""
import tkinter as tk
from tkinter import ttk, messagebox

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.campo_entrada import CampoArredondado
from componentes.combo_arredondado import ComboArredondado
from componentes.notificacoes import NotificacaoFlutuante
from controladores.controlador_aluno import ControladorLead, CAPTADORES_PADRAO
from controladores.controlador_academico import ControladorVenda


FORMAS_PAGAMENTO = ("PIX", "Cartão de Crédito", "Cartão de Débito", "Boleto", "Dinheiro")
STATUS_PAGAMENTO = ("PAGO", "NAO_PAGO", "PARCIAL")


class PainelVendas(tk.Frame):

    def __init__(self, mestre, dashboard=None):
        super().__init__(mestre, bg=tema.OFFWHITE)
        self.pack(fill="both", expand=True)
        self.dashboard = dashboard
        self._venda_em_edicao = None

        topo = tk.Frame(self, bg=tema.OFFWHITE)
        topo.pack(fill="x", padx=20, pady=(20, 10))

        # form à esquerda, tabela à direita
        topo.columnconfigure(0, weight=1, minsize=420)
        topo.columnconfigure(1, weight=2, minsize=520)

        form_card = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._construir_form(form_card)

        tabela_card = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        tabela_card.grid(row=0, column=1, sticky="nsew")
        self._construir_tabela(tabela_card)

    # =================================================================
    def _construir_form(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Registrar Venda", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 12))

        leads = ControladorLead.listar_leads()
        self._mapa_leads = {
            f"#{l['id']} - {l['nome_completo']}": l["id"] for l in leads
        }
        opcoes = list(self._mapa_leads.keys()) or ["(nenhum lead cadastrado)"]

        self._lbl(bloco, "Aluno (Lead) *")
        self._combo_lead = ComboArredondado(
            bloco, opcoes=opcoes, valor_inicial=opcoes[0],
            largura=360, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_lead.pack(pady=4)

        self._lbl(bloco, "Curso vendido")
        self._campo_curso = CampoArredondado(
            bloco, placeholder="Ex: Técnico em Enfermagem",
            largura=360, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_curso.pack(pady=4)

        self._lbl(bloco, "Valor (R$)")
        self._campo_valor = CampoArredondado(
            bloco, placeholder="0,00", largura=360,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_valor.pack(pady=4)

        self._lbl(bloco, "Forma de pagamento")
        self._combo_forma = ComboArredondado(
            bloco, opcoes=list(FORMAS_PAGAMENTO),
            valor_inicial=FORMAS_PAGAMENTO[0], largura=360,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_forma.pack(pady=4)

        self._lbl(bloco, "Status do pagamento")
        self._combo_status = ComboArredondado(
            bloco, opcoes=list(STATUS_PAGAMENTO),
            valor_inicial="NAO_PAGO", largura=360,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_status.pack(pady=4)

        self._lbl(bloco, "Captador")
        self._combo_captador = ComboArredondado(
            bloco, opcoes=list(CAPTADORES_PADRAO),
            valor_inicial=CAPTADORES_PADRAO[0], largura=360,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_captador.pack(pady=4)

        botoes = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        botoes.pack(fill="x", pady=(14, 0))
        BotaoArredondado(
            botoes, texto="Cancelar", comando=self._cancelar,
            cor_fundo=tema.CINZA_CLARO, cor_hover=tema.CINZA_BORDA,
            cor_press="#D5D7DF", cor_texto=tema.AZUL_ESCURO,
            largura=100, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left", padx=(0, 8))
        self._botao_salvar = BotaoArredondado(
            botoes, texto="Registrar Venda", comando=self._salvar,
            largura=160, altura=40, fonte=tema.fonte_destaque(11),
        )
        self._botao_salvar.pack(side="left")

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
            topo, text="Vendas Registradas", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(side="left")

        self._lbl_total = tk.Label(
            topo, text="", bg=tema.BRANCO_PURO,
            fg=tema.VERDE_SUCESSO, font=tema.fonte_destaque(11),
        )
        self._lbl_total.pack(side="right")

        colunas = ("id", "lead", "curso", "valor", "forma", "status", "data")
        self._tabela = ttk.Treeview(
            bloco, columns=colunas, show="headings",
            style="SF.Treeview", height=14,
        )
        for c, txt, w, anchor in (
            ("id", "ID", 50, "center"),
            ("lead", "Aluno", 180, "w"),
            ("curso", "Curso", 160, "w"),
            ("valor", "Valor", 100, "e"),
            ("forma", "Forma", 110, "w"),
            ("status", "Status", 80, "center"),
            ("data", "Data", 110, "center"),
        ):
            self._tabela.heading(c, text=txt)
            self._tabela.column(c, width=w, anchor=anchor)

        self._tabela.pack(fill="both", expand=True, pady=(8, 0))

        menu = tk.Menu(self._tabela, tearoff=0)
        menu.add_command(label="\u270E Editar", command=self._editar)
        menu.add_command(label="\U0001F5D1  Excluir", command=self._excluir)
        self._menu = menu
        self._tabela.bind("<Button-3>", self._menu_contexto)
        self._tabela.bind("<Double-1>", lambda _e: self._editar())

        self._popular()

    def _menu_contexto(self, evento):
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
        vendas = ControladorVenda.listar_vendas()
        total = 0.0
        for v in vendas:
            valor = float(v.get("valor") or 0)
            total += valor
            self._tabela.insert(
                "", "end", iid=str(v["id"]),
                values=(
                    v["id"],
                    v.get("aluno_nome", "—"),
                    v.get("curso_vendido", "") or v.get("observacoes", ""),
                    f"R$ {valor:,.2f}".replace(",", "v")
                        .replace(".", ",").replace("v", "."),
                    v.get("forma_pagamento", ""),
                    v.get("status_pagamento", ""),
                    str(v.get("criado_em", ""))[:10],
                ),
            )
        self._lbl_total.configure(
            text=f"Total: R$ {total:,.2f}".replace(",", "v")
                .replace(".", ",").replace("v", "."),
        )

    # =================================================================
    def _coletar(self) -> dict:
        chave = self._combo_lead.obter_valor()
        lead_id = self._mapa_leads.get(chave)
        return {
            "lead_id": lead_id,
            "observacoes": "Curso: " + self._campo_curso.obter_valor().strip(),
            "valor": (self._campo_valor.obter_valor() or "0").replace(",", "."),
            "forma_pagamento": self._combo_forma.obter_valor(),
            "status_pagamento": self._combo_status.obter_valor(),
            "captador": self._combo_captador.obter_valor(),
            "parcelas": 1,
        }

    def _salvar(self):
        dados = self._coletar()
        topo = self.winfo_toplevel()
        if self._venda_em_edicao:
            sucesso, msg = ControladorVenda.atualizar_venda(
                self._venda_em_edicao, dados,
            )
        else:
            sucesso, msg, _id = ControladorVenda.registrar_venda(dados)
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._cancelar()
            self._popular()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")

    def _cancelar(self):
        for c in (self._campo_curso, self._campo_valor):
            c.definir_valor("")
        self._venda_em_edicao = None
        try:
            self._botao_salvar._texto = "Registrar Venda"
            self._botao_salvar._desenhar()
        except Exception:
            pass

    def _editar(self):
        sel = self._tabela.selection()
        if not sel:
            return
        id_v = int(sel[0])
        vendas = ControladorVenda.listar_vendas()
        venda = next((v for v in vendas if v["id"] == id_v), None)
        if not venda:
            return
        # Extrai curso do campo observações (formato: "Curso: ...")
        obs = venda.get("observacoes") or ""
        curso = obs.replace("Curso: ", "") if obs.startswith("Curso: ") else ""
        self._campo_curso.definir_valor(curso)
        self._campo_valor.definir_valor(str(venda.get("valor", "")))
        self._combo_forma.definir_valor(venda.get("forma_pagamento", FORMAS_PAGAMENTO[0]))
        self._combo_status.definir_valor(venda.get("status_pagamento", "NAO_PAGO"))
        self._combo_captador.definir_valor(venda.get("captador") or CAPTADORES_PADRAO[0])
        self._venda_em_edicao = id_v
        try:
            self._botao_salvar._texto = "Atualizar Venda"
            self._botao_salvar._desenhar()
        except Exception:
            pass

    def _excluir(self):
        sel = self._tabela.selection()
        if not sel:
            return
        id_v = int(sel[0])
        if not messagebox.askyesno(
            "Confirmar", "Excluir a venda selecionada?",
            parent=self.winfo_toplevel(),
        ):
            return
        sucesso, msg = ControladorVenda.excluir_venda(id_v)
        topo = self.winfo_toplevel()
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._popular()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")
