"""
Pagina Frequencia - registro de presencas e faltas dos alunos por aula.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    VERDE_SUCESSO, VERMELHO_ERRO, AMARELO_VIBRANTE,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from componentes.card import Card
from app.controlador import controlador_dashboard
from app.modelo import modelo_aula


class PaginaFrequencia(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self.entries = {}
        self.aulas_dict = {}
        self._construir()
        self._carregar_lista()

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Frequencia de Alunos",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo, text="Registre presencas e faltas por aula",
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

        # Carrega aulas para dropdown
        try:
            aulas = modelo_aula.listar_aulas()
            self.aulas_dict = {
                f"#{a['id']} - {a['titulo']}": a["id"] for a in aulas
            }
        except Exception:
            self.aulas_dict = {}

        # Form
        card = Card(cont, titulo="✓  Registrar Presenca", padding=14, raio=12)
        card.pack(fill="x", padx=24, pady=10)

        form = tk.Frame(card.interno, bg=BRANCO)
        form.pack(fill="x")

        l1 = tk.Frame(form, bg=BRANCO); l1.pack(fill="x", pady=4)
        # Aula
        wa = tk.Frame(l1, bg=BRANCO)
        wa.pack(side="left", fill="x", expand=True, padx=4)
        tk.Label(wa, text="Aula",
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
        self.entries["aula_label"] = ttk.Combobox(
            wa, values=list(self.aulas_dict.keys()),
            state="readonly", font=(FONTE_TEXTO, 10))
        self.entries["aula_label"].pack(fill="x", ipady=4)

        # Aluno
        self._campo(l1, "aluno_nome", "Nome do Aluno *")

        # Presente?
        l2 = tk.Frame(form, bg=BRANCO); l2.pack(fill="x", pady=4)
        wp = tk.Frame(l2, bg=BRANCO)
        wp.pack(side="left", fill="x", expand=True, padx=4)
        tk.Label(wp, text="Status",
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
        self.var_presente = tk.StringVar(value="presente")
        radios = tk.Frame(wp, bg=BRANCO)
        radios.pack(fill="x", pady=6)
        tk.Radiobutton(radios, text="✓ Presente",
                       variable=self.var_presente, value="presente",
                       font=(FONTE_TEXTO, 10), fg=VERDE_SUCESSO, bg=BRANCO,
                       selectcolor=BRANCO_GELO,
                       cursor="hand2").pack(side="left", padx=8)
        tk.Radiobutton(radios, text="✗ Falta",
                       variable=self.var_presente, value="falta",
                       font=(FONTE_TEXTO, 10), fg=VERMELHO_ERRO, bg=BRANCO,
                       selectcolor=BRANCO_GELO,
                       cursor="hand2").pack(side="left", padx=8)

        self._campo(l2, "justificativa", "Justificativa (se falta)")

        btns = tk.Frame(form, bg=BRANCO)
        btns.pack(fill="x", pady=(8, 0))
        BotaoModerno(btns, texto="Cancelar", comando=self._limpar,
                     largura=120, altura=36,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     cor_fundo=BRANCO).pack(side="left", padx=4)
        BotaoModerno(btns, texto="✓  Registrar", comando=self._salvar,
                     largura=170, altura=36,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     cor_fundo=BRANCO).pack(side="right", padx=4)

        # Tabela
        tcard = Card(cont, titulo="📋  Frequencias Registradas", padding=14, raio=12)
        tcard.pack(fill="both", expand=True, padx=24, pady=10)

        head = tk.Frame(tcard.interno, bg=AZUL_PRIMARIO)
        head.pack(fill="x", pady=(8, 0))
        for col in ["ID", "Aluno", "Aula ID", "Status",
                    "Justificativa", "Data"]:
            tk.Label(head, text=col,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        self.frame_linhas = tk.Frame(tcard.interno, bg=BRANCO)
        self.frame_linhas.pack(fill="both", expand=True, pady=(10, 0))

    def _campo(self, parent, chave, label):
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
        self.entries[chave] = entry

    def _coletar(self):
        rotulo_aula = self.entries["aula_label"].get()
        return {
            "aula_id": self.aulas_dict.get(rotulo_aula),
            "aluno_nome": self.entries["aluno_nome"].get(),
            "presente": 1 if self.var_presente.get() == "presente" else 0,
            "justificativa": self.entries["justificativa"].get(),
            "data_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _salvar(self):
        dados = self._coletar()
        if not dados.get("aluno_nome"):
            Notificacao.erro(self, "Informe o nome do aluno")
            return
        sucesso, msg, _ = controlador_dashboard.salvar_frequencia(dados)
        if sucesso:
            Notificacao.sucesso(self, msg)
            self._limpar()
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)

    def _limpar(self):
        for k, w in self.entries.items():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0, "end")
        self.var_presente.set("presente")

    def _carregar_lista(self):
        for w in self.frame_linhas.winfo_children():
            w.destroy()
        try:
            freqs = controlador_dashboard.listar_frequencia()
        except Exception as e:
            Notificacao.erro(self, f"Erro: {e}")
            return

        if not freqs:
            tk.Label(self.frame_linhas, text="Nenhuma frequencia registrada",
                     font=(FONTE_TEXTO, 10, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=20).pack()
            return

        for f in freqs:
            self._linha(f)

    def _linha(self, f):
        linha = tk.Frame(self.frame_linhas, bg=BRANCO,
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1)
        linha.pack(fill="x")
        status = "✓ Presente" if f.get("presente") else "✗ Falta"
        cor_status = VERDE_SUCESSO if f.get("presente") else VERMELHO_ERRO

        for i, valor in enumerate([
            f"#{f.get('id')}",
            (f.get("aluno_nome") or "")[:25],
            f"#{f.get('aula_id', '-')}",
            status,
            (f.get("justificativa") or "-")[:25],
            str(f.get("data_registro") or "")[:16],
        ]):
            cor = cor_status if i == 3 else PRETO_TEXTO
            peso = "bold" if i == 3 else "normal"
            tk.Label(linha, text=str(valor),
                     font=(FONTE_TEXTO, 9, peso),
                     fg=cor, bg=BRANCO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")
