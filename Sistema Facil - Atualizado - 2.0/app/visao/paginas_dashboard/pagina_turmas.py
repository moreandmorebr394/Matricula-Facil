"""
Pagina Turmas - cadastro e listagem de turmas.
"""
import tkinter as tk
from tkinter import ttk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    VERDE_SUCESSO, VERMELHO_ERRO, AMARELO_VIBRANTE,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from componentes.mascaras import aplicar_mascara_data
from app.controlador import controlador_dashboard
from app.controlador.listas_constantes import CURSOS, STATUS_TURMA


class PaginaTurmas(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self.turma_em_edicao = None
        self.entries = {}
        self._construir()
        self._carregar_lista()

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Gestao de Turmas",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo, text="Cadastre e gerencie suas turmas",
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

        # Form
        card = tk.Frame(cont, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=10)

        h = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="📚  Nova Turma",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        form = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        form.pack(fill="x")

        l1 = tk.Frame(form, bg=BRANCO); l1.pack(fill="x", pady=4)
        self._campo(l1, "nome_turma", "Nome da Turma *")
        self._combo(l1, "curso", "Curso *", CURSOS)

        l2 = tk.Frame(form, bg=BRANCO); l2.pack(fill="x", pady=4)
        self._campo(l2, "professor", "Professor")
        self._campo(l2, "horario", "Horario (Ex: 19h-22h)")
        self._campo(l2, "sala", "Sala")

        l3 = tk.Frame(form, bg=BRANCO); l3.pack(fill="x", pady=4)
        self._campo(l3, "data_inicio", "Inicio (DD/MM/AAAA)",
                    mascara="data")
        self._campo(l3, "data_fim", "Fim (DD/MM/AAAA)", mascara="data")
        self._campo(l3, "capacidade_maxima", "Capacidade Max.")

        l4 = tk.Frame(form, bg=BRANCO); l4.pack(fill="x", pady=4)
        self._campo(l4, "alunos_matriculados", "Alunos Matriculados")
        self._combo(l4, "status", "Status", STATUS_TURMA)

        btns = tk.Frame(form, bg=BRANCO)
        btns.pack(fill="x", pady=(8, 0))
        BotaoModerno(btns, texto="Cancelar", comando=self._limpar,
                     largura=120, altura=36,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     cor_fundo=BRANCO).pack(side="left", padx=4)
        BotaoModerno(btns, texto="💾  Salvar Turma", comando=self._salvar,
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
        tk.Label(th, text="📋  Turmas Cadastradas",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(side="left")
        tk.Frame(tcard, bg=CINZA_CLARO, height=1).pack(fill="x")

        head = tk.Frame(tcard, bg=AZUL_PRIMARIO)
        head.pack(fill="x", padx=18, pady=(8, 0))
        for col in ["ID", "Nome", "Curso", "Professor", "Horario",
                    "Status", "Acoes"]:
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
        if mascara == "data":
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
        return {k: w.get() for k, w in self.entries.items()}

    def _salvar(self):
        dados = self._coletar()
        if self.turma_em_edicao:
            sucesso, msg = controlador_dashboard.atualizar_turma(
                self.turma_em_edicao, dados)
        else:
            sucesso, msg, _ = controlador_dashboard.salvar_turma(dados)
        if sucesso:
            Notificacao.sucesso(self, msg)
            self._limpar()
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)

    def _limpar(self):
        self.turma_em_edicao = None
        for w in self.entries.values():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0, "end")

    def _carregar_lista(self):
        for w in self.frame_linhas.winfo_children():
            w.destroy()
        try:
            turmas = controlador_dashboard.listar_turmas()
        except Exception as e:
            Notificacao.erro(self, f"Erro: {e}")
            return

        if not turmas:
            tk.Label(self.frame_linhas, text="Nenhuma turma cadastrada",
                     font=(FONTE_TEXTO, 10, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=20).pack()
            return

        for t in turmas:
            self._linha(t)

    def _linha(self, t):
        linha = tk.Frame(self.frame_linhas, bg=BRANCO,
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1)
        linha.pack(fill="x")
        for valor in [
            f"#{t.get('id')}",
            (t.get("nome_turma") or "")[:25],
            (t.get("curso") or "-")[:20],
            (t.get("professor") or "-")[:18],
            t.get("horario") or "-",
            t.get("status") or "-",
        ]:
            tk.Label(linha, text=str(valor),
                     font=(FONTE_TEXTO, 9),
                     fg=PRETO_TEXTO, bg=BRANCO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        acoes = tk.Frame(linha, bg=BRANCO)
        acoes.pack(side="left", expand=True, fill="x")
        ic_e = tk.Label(acoes, text="✏",
                        font=("Segoe UI Emoji", 12),
                        bg=BRANCO, fg=AZUL_PRIMARIO, cursor="hand2")
        ic_e.pack(side="left", padx=4)
        ic_d = tk.Label(acoes, text="🗑",
                        font=("Segoe UI Emoji", 12),
                        bg=BRANCO, fg=VERMELHO_ERRO, cursor="hand2")
        ic_d.pack(side="left", padx=4)
        ic_e.bind("<Button-1>", lambda e: self._editar(t))
        ic_d.bind("<Button-1>", lambda e: self._excluir(t))

    def _editar(self, t):
        self._limpar()
        self.turma_em_edicao = t.get("id")
        for k, w in self.entries.items():
            valor = t.get(k, "")
            if isinstance(w, ttk.Combobox):
                w.set(valor or "")
            else:
                w.insert(0, str(valor or ""))
        Notificacao.info(self, f"Editando turma #{t.get('id')}")

    def _excluir(self, t):
        sucesso, msg = controlador_dashboard.excluir_turma(t.get("id"))
        if sucesso:
            Notificacao.sucesso(self, msg)
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)
