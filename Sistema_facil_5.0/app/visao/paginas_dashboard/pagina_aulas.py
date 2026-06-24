"""
Pagina Aulas - cadastro e listagem de aulas vinculadas a turmas.
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
from componentes.card import Card
from componentes.mascaras import aplicar_mascara_data
from app.controlador import controlador_dashboard
from app.controlador.listas_constantes import STATUS_AULA
from app.modelo import modelo_turma


class PaginaAulas(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self.aula_em_edicao = None
        self.entries = {}
        self.turmas_dict = {}
        self._construir()
        self._carregar_lista()

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Gestao de Aulas",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo, text="Agende aulas vinculadas as turmas",
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

        # Carrega turmas para o dropdown
        try:
            turmas = modelo_turma.listar_turmas()
            self.turmas_dict = {
                f"#{t['id']} - {t['nome_turma']}": t["id"] for t in turmas
            }
        except Exception:
            self.turmas_dict = {}

        # Form
        card = Card(cont, titulo="🎓  Nova Aula", padding=14, raio=12)
        card.pack(fill="x", padx=24, pady=10)

        form = tk.Frame(card.interno, bg=BRANCO)
        form.pack(fill="x")

        l1 = tk.Frame(form, bg=BRANCO); l1.pack(fill="x", pady=4)
        self._campo(l1, "titulo", "Titulo da Aula *")
        self._combo(l1, "turma_label", "Turma",
                    list(self.turmas_dict.keys()))

        tk.Label(form, text="Descricao",
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w", pady=(8, 2))
        self.txt_desc = tk.Text(form, height=2, font=(FONTE_TEXTO, 10),
                                bg=BRANCO_GELO, fg=PRETO_TEXTO,
                                relief="flat",
                                highlightbackground=CINZA_CLARO,
                                highlightthickness=1, padx=8, pady=6)
        self.txt_desc.pack(fill="x", pady=(0, 8))

        l2 = tk.Frame(form, bg=BRANCO); l2.pack(fill="x", pady=4)
        self._campo(l2, "data_aula", "Data (DD/MM/AAAA)", mascara="data")
        self._campo(l2, "horario_inicio", "Hora Inicio (HH:MM)")
        self._campo(l2, "horario_fim", "Hora Fim (HH:MM)")

        l3 = tk.Frame(form, bg=BRANCO); l3.pack(fill="x", pady=4)
        self._campo(l3, "professor", "Professor")
        self._campo(l3, "sala", "Sala")
        self._combo(l3, "status", "Status", STATUS_AULA)

        btns = tk.Frame(form, bg=BRANCO)
        btns.pack(fill="x", pady=(8, 0))
        BotaoModerno(btns, texto="Cancelar", comando=self._limpar,
                     largura=120, altura=36,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     cor_fundo=BRANCO).pack(side="left", padx=4)
        BotaoModerno(btns, texto="💾  Salvar Aula", comando=self._salvar,
                     largura=170, altura=36,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     cor_fundo=BRANCO).pack(side="right", padx=4)

        # Tabela
        tcard = Card(cont, titulo="📋  Aulas Agendadas", padding=14, raio=12)
        tcard.pack(fill="both", expand=True, padx=24, pady=10)

        head = tk.Frame(tcard.interno, bg=AZUL_PRIMARIO)
        head.pack(fill="x", pady=(8, 0))
        for col in ["ID", "Titulo", "Data", "Horario", "Professor",
                    "Status", "Acoes"]:
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
        d = {}
        for k, w in self.entries.items():
            if k == "turma_label":
                continue
            d[k] = w.get()
        # Mapeia turma_label -> turma_id
        rotulo = self.entries["turma_label"].get()
        d["turma_id"] = self.turmas_dict.get(rotulo)
        d["descricao"] = self.txt_desc.get("1.0", "end").strip()
        return d

    def _salvar(self):
        dados = self._coletar()
        if self.aula_em_edicao:
            sucesso, msg = controlador_dashboard.atualizar_aula(
                self.aula_em_edicao, dados)
        else:
            sucesso, msg, _ = controlador_dashboard.salvar_aula(dados)
        if sucesso:
            Notificacao.sucesso(self, msg)
            self._limpar()
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)

    def _limpar(self):
        self.aula_em_edicao = None
        for w in self.entries.values():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0, "end")
        self.txt_desc.delete("1.0", "end")

    def _carregar_lista(self):
        for w in self.frame_linhas.winfo_children():
            w.destroy()
        try:
            aulas = controlador_dashboard.listar_aulas()
        except Exception as e:
            Notificacao.erro(self, f"Erro: {e}")
            return

        if not aulas:
            tk.Label(self.frame_linhas, text="Nenhuma aula agendada",
                     font=(FONTE_TEXTO, 10, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=20).pack()
            return

        for a in aulas:
            self._linha(a)

    def _linha(self, a):
        linha = tk.Frame(self.frame_linhas, bg=BRANCO,
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1)
        linha.pack(fill="x")
        horario = (
            f"{a.get('horario_inicio') or ''} - {a.get('horario_fim') or ''}"
        ).strip(" -")
        for valor in [
            f"#{a.get('id')}",
            (a.get("titulo") or "")[:25],
            a.get("data_aula") or "-",
            horario or "-",
            (a.get("professor") or "-")[:18],
            a.get("status") or "-",
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
        ic_e.bind("<Button-1>", lambda e: self._editar(a))
        ic_d.bind("<Button-1>", lambda e: self._excluir(a))

    def _editar(self, a):
        self._limpar()
        self.aula_em_edicao = a.get("id")
        for k, w in self.entries.items():
            if k == "turma_label":
                # Encontra label pela turma_id
                tid = a.get("turma_id")
                rotulo = next(
                    (r for r, i in self.turmas_dict.items() if i == tid),
                    "")
                w.set(rotulo)
            else:
                valor = a.get(k, "")
                if isinstance(w, ttk.Combobox):
                    w.set(valor or "")
                else:
                    w.insert(0, str(valor or ""))
        self.txt_desc.insert("1.0", a.get("descricao") or "")
        Notificacao.info(self, f"Editando aula #{a.get('id')}")

    def _excluir(self, a):
        sucesso, msg = controlador_dashboard.excluir_aula(a.get("id"))
        if sucesso:
            def desfazer():
                res, m = controlador_dashboard.restaurar_registro("aulas", a)
                if res:
                    Notificacao.sucesso(self, "Aula restaurada!")
                    self._carregar_lista()
                else:
                    Notificacao.erro(self, f"Erro ao desfazer: {m}")
            Notificacao.sucesso(self, msg, comando_desfazer=desfazer)
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)
