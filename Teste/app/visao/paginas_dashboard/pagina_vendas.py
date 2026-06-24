"""
Pagina Vendas - cadastro e listagem de vendas.
"""
import tkinter as tk
from tkinter import ttk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    VERDE_SUCESSO, VERMELHO_ERRO, LARANJA_ALERTA,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from componentes.card import Card
from componentes.mascaras import aplicar_mascara_dinheiro
from app.controlador import controlador_dashboard
from app.controlador.listas_constantes import (
    CURSOS, FORMAS_PAGAMENTO, STATUS_PAGAMENTO, CAPTADORES
)


class PaginaVendas(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self.venda_em_edicao = None
        self.entries = {}
        self._construir()
        self._carregar_lista()

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Gestao de Vendas",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo, text="Registre vendas e acompanhe o financeiro",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO).pack(anchor="w")

        canvas = tk.Canvas(self, bg=BRANCO_GELO, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)

        cont = tk.Frame(canvas, bg=BRANCO_GELO)
        window_id = canvas.create_window((0, 0), window=cont, anchor="n", width=1140)

        def ar(_=None):
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=(0, 0, 0, bbox[3]))
        cont.bind("<Configure>", ar)

        def ao_redimensionar_canvas(e):
            nova_largura = min(1140, e.width - 40)
            if nova_largura < 300:
                nova_largura = 300
            canvas.itemconfig(window_id, width=nova_largura)
            canvas.coords(window_id, e.width // 2, 0)
        canvas.bind("<Configure>", ao_redimensionar_canvas, add="+")
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * (e.delta / 120)), "units"), add="+")

        # Card do form
        card = Card(cont, titulo="💰  Nova Venda", padding=14, raio=12)
        card.pack(fill="x", padx=24, pady=10)

        form = tk.Frame(card.interno, bg=BRANCO)
        form.pack(fill="x")

        l1 = tk.Frame(form, bg=BRANCO); l1.pack(fill="x", pady=4)
        self._campo(l1, "nome_aluno", "Nome do Aluno *")
        self._combo(l1, "curso", "Curso *", CURSOS)

        l2 = tk.Frame(form, bg=BRANCO); l2.pack(fill="x", pady=4)
        self._campo(l2, "valor_total", "Valor Total *", mascara="dinheiro")
        self._combo(l2, "forma_pagamento", "Forma de Pagamento",
                    FORMAS_PAGAMENTO)
        self._campo(l2, "parcelas", "Parcelas")

        l3 = tk.Frame(form, bg=BRANCO); l3.pack(fill="x", pady=4)
        self._combo(l3, "status_pagamento", "Status",
                    STATUS_PAGAMENTO)
        self._combo(l3, "vendedor", "Vendedor", CAPTADORES)

        tk.Label(form, text="Observacoes",
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w", pady=(8, 2))
        self.txt_obs = tk.Text(form, height=2, font=(FONTE_TEXTO, 10),
                               bg=BRANCO_GELO, fg=PRETO_TEXTO,
                               relief="flat",
                               highlightbackground=CINZA_CLARO,
                               highlightthickness=1, padx=8, pady=6)
        self.txt_obs.pack(fill="x", pady=(0, 8))

        btns = tk.Frame(form, bg=BRANCO)
        btns.pack(fill="x", pady=(8, 0))
        BotaoModerno(btns, texto="Cancelar",
                     comando=self._limpar,
                     largura=120, altura=36,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     cor_fundo=BRANCO).pack(side="left", padx=4)
        BotaoModerno(btns, texto="💾  Salvar Venda",
                     comando=self._salvar,
                     largura=170, altura=36,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     cor_fundo=BRANCO).pack(side="right", padx=4)

        # Tabela
        tcard = Card(cont, titulo="📋  Vendas Registradas", padding=14, raio=12)
        tcard.pack(fill="both", expand=True, padx=24, pady=10)

        head = tk.Frame(tcard.interno, bg=AZUL_PRIMARIO)
        head.pack(fill="x", pady=(8, 0))
        for col in ["ID", "Aluno", "Curso", "Valor",
                    "Forma", "Status", "Acoes"]:
            tk.Label(head, text=col,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        self.frame_linhas = tk.Frame(tcard.interno, bg=BRANCO)
        self.frame_linhas.pack(fill="both", expand=True, pady=(10, 0))

    def _campo(self, parent, chave, label, mascara=None):
        wrap = tk.Frame(parent, bg=BRANCO)
        wrap.pack(side="left", fill="x", expand=True, padx=4)
        tk.Label(wrap, text=label,
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
        entry = tk.Entry(wrap, font=(FONTE_TEXTO, 10),
                         bg=BRANCO_GELO, fg=PRETO_TEXTO,
                         relief="flat",
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1)
        entry.pack(fill="x", ipady=6)
        if mascara == "dinheiro":
            aplicar_mascara_dinheiro(entry)
        self.entries[chave] = entry

    def _combo(self, parent, chave, label, valores):
        wrap = tk.Frame(parent, bg=BRANCO)
        wrap.pack(side="left", fill="x", expand=True, padx=4)
        tk.Label(wrap, text=label,
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
        combo = ttk.Combobox(wrap, values=valores, state="readonly",
                             font=(FONTE_TEXTO, 10))
        combo.pack(fill="x", ipady=4)
        self.entries[chave] = combo

    def _coletar(self):
        d = {}
        for k, w in self.entries.items():
            d[k] = w.get()
        d["observacoes"] = self.txt_obs.get("1.0", "end").strip()
        return d

    def _salvar(self):
        dados = self._coletar()
        if self.venda_em_edicao:
            sucesso, msg = controlador_dashboard.atualizar_venda(
                self.venda_em_edicao, dados)
        else:
            sucesso, msg, _ = controlador_dashboard.salvar_venda(dados)
        if sucesso:
            Notificacao.sucesso(self, msg)
            self._limpar()
            self._carregar_lista()
            if self.dashboard:
                try:
                    self.dashboard.atualizar_contador_notificacoes()
                except Exception:
                    pass
        else:
            Notificacao.erro(self, msg)

    def _limpar(self):
        self.venda_em_edicao = None
        for w in self.entries.values():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0, "end")
        self.txt_obs.delete("1.0", "end")

    def _carregar_lista(self):
        for w in self.frame_linhas.winfo_children():
            w.destroy()

        try:
            vendas = controlador_dashboard.listar_vendas()
        except Exception as e:
            Notificacao.erro(self, f"Erro: {e}")
            return

        if not vendas:
            tk.Label(self.frame_linhas, text="Nenhuma venda registrada",
                     font=(FONTE_TEXTO, 10, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=20).pack()
            return

        for v in vendas:
            self._linha(v)

    def _linha(self, v):
        linha = tk.Frame(self.frame_linhas, bg=BRANCO,
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1)
        linha.pack(fill="x")

        valor_str = f"R$ {float(v.get('valor_total') or 0):.2f}".replace(
            ".", ",")

        for valor in [
            f"#{v.get('id')}",
            (v.get("nome_aluno") or "")[:25],
            (v.get("curso") or "-")[:20],
            valor_str,
            v.get("forma_pagamento") or "-",
            v.get("status_pagamento") or "-",
        ]:
            tk.Label(linha, text=str(valor),
                     font=(FONTE_TEXTO, 9),
                     fg=PRETO_TEXTO, bg=BRANCO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        acoes = tk.Frame(linha, bg=BRANCO)
        acoes.pack(side="left", expand=True, fill="x")
        ic_e = tk.Label(acoes, text="✏",
                        font=("Segoe UI Emoji", 12),
                        bg=BRANCO, fg=AZUL_PRIMARIO,
                        cursor="hand2")
        ic_e.pack(side="left", padx=4)
        ic_d = tk.Label(acoes, text="🗑",
                        font=("Segoe UI Emoji", 12),
                        bg=BRANCO, fg=VERMELHO_ERRO,
                        cursor="hand2")
        ic_d.pack(side="left", padx=4)
        ic_e.bind("<Button-1>", lambda e: self._editar(v))
        ic_d.bind("<Button-1>", lambda e: self._confirmar_excluir(v))

    def _editar(self, v):
        self._limpar()
        self.venda_em_edicao = v.get("id")
        for k, w in self.entries.items():
            valor = v.get(k, "")
            if isinstance(w, ttk.Combobox):
                w.set(valor or "")
            else:
                if k == "valor_total" and valor:
                    valor = f"R$ {float(valor):.2f}".replace(".", ",")
                w.insert(0, str(valor or ""))
        self.txt_obs.insert("1.0", v.get("observacoes") or "")
        Notificacao.info(self, f"Editando venda #{v.get('id')}")

    def _confirmar_excluir(self, v):
        dlg = tk.Toplevel(self)
        dlg.title("Excluir venda")
        dlg.geometry("400x180")
        dlg.configure(bg=BRANCO)
        dlg.transient(self); dlg.grab_set(); dlg.resizable(False, False)

        h = tk.Frame(dlg, bg=VERMELHO_ERRO, height=50)
        h.pack(fill="x"); h.pack_propagate(False)
        tk.Label(h, text="⚠  Confirmar exclusao",
                 font=(FONTE_TEXTO, 11, "bold"),
                 fg=BRANCO, bg=VERMELHO_ERRO).pack(pady=14)

        c = tk.Frame(dlg, bg=BRANCO); c.pack(fill="both", expand=True,
                                              padx=20, pady=14)
        tk.Label(c, text=f"Excluir venda #{v.get('id')}?",
                 font=(FONTE_TEXTO, 10),
                 fg=PRETO_TEXTO, bg=BRANCO).pack(pady=8)

        b = tk.Frame(c, bg=BRANCO); b.pack(pady=8)
        BotaoModerno(b, texto="Cancelar", comando=dlg.destroy,
                     largura=110, altura=32,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     cor_fundo=BRANCO).pack(side="left", padx=4)
        def confirmar():
            sucesso, msg = controlador_dashboard.excluir_venda(v.get("id"))
            dlg.destroy()
            if sucesso:
                def desfazer():
                    res, m = controlador_dashboard.restaurar_registro("vendas", v)
                    if res:
                        Notificacao.sucesso(self, "Venda restaurada!")
                        self._carregar_lista()
                    else:
                        Notificacao.erro(self, f"Erro ao desfazer: {m}")
                Notificacao.sucesso(self, msg, comando_desfazer=desfazer)
                self._carregar_lista()
            else:
                Notificacao.erro(self, msg)
        BotaoModerno(b, texto="Excluir", comando=confirmar,
                     largura=110, altura=32,
                     cor_normal=VERMELHO_ERRO, cor_hover="#DC2626",
                     cor_fundo=BRANCO).pack(side="left", padx=4)
