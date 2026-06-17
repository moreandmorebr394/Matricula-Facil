"""
Pagina Pagamentos - registro e listagem de pagamentos.
"""
import tkinter as tk
from tkinter import ttk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    VERDE_SUCESSO, VERMELHO_ERRO, LARANJA_ALERTA, AMARELO_VIBRANTE,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from componentes.mascaras import aplicar_mascara_dinheiro, aplicar_mascara_data
from app.controlador import controlador_dashboard
from app.controlador.listas_constantes import (
    FORMAS_PAGAMENTO, STATUS_PAGAMENTO
)
from app.modelo import modelo_pagamento


class PaginaPagamentos(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self.entries = {}
        self._construir()
        self._carregar_lista()

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Gestao de Pagamentos",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo, text="Registre pagamentos recebidos",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO).pack(anchor="w")

        canvas = tk.Canvas(self, bg=BRANCO_GELO, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)

        cont = tk.Frame(canvas, bg=BRANCO_GELO)
        canvas.create_window((0, 0), window=cont, anchor="nw", width=1140)
        cont.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * (e.delta / 120)), "units"), add="+")

        # Cards de resumo
        try:
            total = modelo_pagamento.total_recebido()
        except Exception:
            total = 0.0

        resumo = tk.Frame(cont, bg=BRANCO_GELO, padx=24, pady=10)
        resumo.pack(fill="x")
        for titulo, valor, cor in [
            ("Total Recebido",
             f"R$ {total:,.2f}".replace(",", "."),
             VERDE_SUCESSO),
            ("Pendentes", "R$ 0,00", LARANJA_ALERTA),
            ("Atrasados", "R$ 0,00", VERMELHO_ERRO),
        ]:
            box = tk.Frame(resumo, bg=BRANCO, padx=18, pady=14,
                           highlightbackground=CINZA_CLARO,
                           highlightthickness=1)
            box.pack(side="left", padx=4, fill="x", expand=True)
            tk.Label(box, text=titulo,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
            tk.Label(box, text=valor,
                     font=(FONTE_TITULO, 16, "bold"),
                     fg=cor, bg=BRANCO).pack(anchor="w")

        # Form
        card = tk.Frame(cont, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="💳  Registrar Pagamento",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        form = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        form.pack(fill="x")

        l1 = tk.Frame(form, bg=BRANCO); l1.pack(fill="x", pady=4)
        self._campo(l1, "nome_aluno", "Nome do Aluno *")
        self._campo(l1, "valor", "Valor (R$) *", mascara="dinheiro")

        l2 = tk.Frame(form, bg=BRANCO); l2.pack(fill="x", pady=4)
        self._campo(l2, "data_pagamento", "Data (DD/MM/AAAA)",
                    mascara="data")
        self._combo(l2, "forma_pagamento", "Forma", FORMAS_PAGAMENTO)
        self._campo(l2, "parcela_numero", "Numero Parcela")

        l3 = tk.Frame(form, bg=BRANCO); l3.pack(fill="x", pady=4)
        self._combo(l3, "status", "Status", STATUS_PAGAMENTO)

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
        BotaoModerno(btns, texto="Cancelar", comando=self._limpar,
                     largura=120, altura=36,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     cor_fundo=BRANCO).pack(side="left", padx=4)
        BotaoModerno(btns, texto="💾  Registrar", comando=self._salvar,
                     largura=170, altura=36,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     cor_fundo=BRANCO).pack(side="right", padx=4)

        # Tabela
        tcard = tk.Frame(cont, bg=BRANCO,
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1)
        tcard.pack(fill="both", expand=True, padx=24, pady=10)

        th = tk.Frame(tcard, bg=BRANCO, padx=18, pady=14)
        th.pack(fill="x")
        tk.Label(th, text="📋  Pagamentos",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(side="left")
        tk.Frame(tcard, bg=CINZA_CLARO, height=1).pack(fill="x")

        head = tk.Frame(tcard, bg=AZUL_PRIMARIO)
        head.pack(fill="x", padx=18, pady=(8, 0))
        for col in ["ID", "Aluno", "Valor", "Data", "Forma", "Status",
                    "Acoes"]:
            tk.Label(head, text=col,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        self.frame_linhas = tk.Frame(tcard, bg=BRANCO)
        self.frame_linhas.pack(fill="both", expand=True, padx=18, pady=(0, 14))

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
        elif mascara == "data":
            aplicar_mascara_data(entry)
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
        d = {k: w.get() for k, w in self.entries.items()}
        d["observacoes"] = self.txt_obs.get("1.0", "end").strip()
        return d

    def _salvar(self):
        sucesso, msg, _ = controlador_dashboard.salvar_pagamento(
            self._coletar())
        if sucesso:
            Notificacao.sucesso(self, msg)
            self._limpar()
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)

    def _limpar(self):
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
            pgs = controlador_dashboard.listar_pagamentos()
        except Exception as e:
            Notificacao.erro(self, f"Erro: {e}")
            return

        if not pgs:
            tk.Label(self.frame_linhas, text="Nenhum pagamento registrado",
                     font=(FONTE_TEXTO, 10, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=20).pack()
            return

        for p in pgs:
            self._linha(p)

    def _linha(self, p):
        linha = tk.Frame(self.frame_linhas, bg=BRANCO,
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1)
        linha.pack(fill="x")
        valor_str = f"R$ {float(p.get('valor') or 0):.2f}".replace(".", ",")
        for valor in [
            f"#{p.get('id')}",
            (p.get("nome_aluno") or "")[:25],
            valor_str,
            p.get("data_pagamento") or "-",
            p.get("forma_pagamento") or "-",
            p.get("status") or "-",
        ]:
            tk.Label(linha, text=str(valor),
                     font=(FONTE_TEXTO, 9),
                     fg=PRETO_TEXTO, bg=BRANCO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        acoes = tk.Frame(linha, bg=BRANCO)
        acoes.pack(side="left", expand=True, fill="x")
        ic_d = tk.Label(acoes, text="🗑",
                        font=("Segoe UI Emoji", 12),
                        bg=BRANCO, fg=VERMELHO_ERRO,
                        cursor="hand2")
        ic_d.pack(side="left", padx=4)
        ic_d.bind("<Button-1>", lambda e: self._excluir(p))

    def _excluir(self, p):
        sucesso, msg = controlador_dashboard.excluir_pagamento(p.get("id"))
        if sucesso:
            Notificacao.sucesso(self, msg)
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)
