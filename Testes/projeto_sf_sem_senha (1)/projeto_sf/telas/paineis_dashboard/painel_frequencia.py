"""Painel de Frequência - controle de presença por aula."""
import tkinter as tk
from tkinter import ttk

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.combo_arredondado import ComboArredondado
from componentes.notificacoes import NotificacaoFlutuante
from controladores.controlador_aluno import ControladorLead
from controladores.controlador_academico import (
    ControladorAula,
    ControladorFrequencia,
)


class PainelFrequencia(tk.Frame):

    def __init__(self, mestre, dashboard=None):
        super().__init__(mestre, bg=tema.OFFWHITE)
        self.pack(fill="both", expand=True)
        self.dashboard = dashboard

        # cabeçalho com seletor de aula
        topo = tk.Frame(self, bg=tema.BRANCO_PURO)
        topo.pack(fill="x", padx=20, pady=(20, 0))

        cabec = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        cabec.pack(fill="x")
        bloco = tk.Frame(cabec, bg=tema.BRANCO_PURO)
        bloco.pack(fill="x", padx=20, pady=14)

        tk.Label(
            bloco, text="Controle de Frequência", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(15),
        ).pack(anchor="w", pady=(0, 8))

        linha = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        linha.pack(fill="x", pady=(4, 0))

        tk.Label(
            linha, text="Aula:", bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
        ).pack(side="left", padx=(0, 8))

        aulas = ControladorAula.listar()
        self._mapa_aulas = {
            f"#{a['id']} - {a.get('titulo', '')[:40]} ({a.get('data', '')})": a["id"]
            for a in aulas
        }
        opcoes = list(self._mapa_aulas.keys()) or ["(nenhuma aula)"]

        self._combo_aula = ComboArredondado(
            linha, opcoes=opcoes, valor_inicial=opcoes[0],
            largura=420, cor_fundo_pai=tema.BRANCO_PURO,
            ao_alterar=lambda _v: self._popular_chamada(),
        )
        self._combo_aula.pack(side="left", padx=(0, 8))

        self._lbl_media = tk.Label(
            linha, text="", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_PRINCIPAL, font=tema.fonte_destaque(11),
        )
        self._lbl_media.pack(side="right")

        # Tabela de chamada
        card_tabela = tk.Frame(
            self, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card_tabela.pack(fill="both", expand=True, padx=20, pady=10)

        bloco_tab = tk.Frame(card_tabela, bg=tema.BRANCO_PURO)
        bloco_tab.pack(fill="both", expand=True, padx=20, pady=14)

        tk.Label(
            bloco_tab, text="Lista de Chamada", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 8))

        cols = ("id", "nome", "presente", "obs")
        self._tabela = ttk.Treeview(
            bloco_tab, columns=cols, show="headings",
            style="SF.Treeview", height=15,
        )
        for c, t, w, a in (
            ("id", "ID", 50, "center"),
            ("nome", "Aluno", 320, "w"),
            ("presente", "Presença", 120, "center"),
            ("obs", "Observação", 200, "w"),
        ):
            self._tabela.heading(c, text=t)
            self._tabela.column(c, width=w, anchor=a)
        self._tabela.pack(fill="both", expand=True, pady=(0, 8))

        # toggle por click duplo
        self._tabela.bind("<Double-1>", lambda _e: self._toggle())

        # Botões de ação em massa
        botoes = tk.Frame(bloco_tab, bg=tema.BRANCO_PURO)
        botoes.pack(fill="x", pady=(8, 0))

        BotaoArredondado(
            botoes, texto="Marcar todos PRESENTES",
            comando=lambda: self._marcar_todos(True),
            cor_fundo=tema.VERDE_SUCESSO, cor_hover="#3FCB85",
            cor_press="#229E62",
            largura=200, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left", padx=(0, 8))

        BotaoArredondado(
            botoes, texto="Marcar todos AUSENTES",
            comando=lambda: self._marcar_todos(False),
            cor_fundo=tema.VERMELHO_ERRO, cor_hover="#EE6655",
            cor_press="#C0392B",
            largura=200, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left", padx=(0, 8))

        BotaoArredondado(
            botoes, texto="Inverter seleção",
            comando=self._toggle,
            cor_fundo=tema.AZUL_PRINCIPAL,
            largura=160, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left")

        tk.Label(
            botoes, text="Duplo clique no aluno para alternar presença",
            bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(9),
        ).pack(side="right")

        self._popular_chamada()

    # =================================================================
    def _aula_id_atual(self) -> int | None:
        return self._mapa_aulas.get(self._combo_aula.obter_valor())

    def _popular_chamada(self):
        for i in self._tabela.get_children():
            self._tabela.delete(i)
        aula_id = self._aula_id_atual()
        if not aula_id:
            self._atualizar_media()
            return
        # busca lista de leads e cruza com presenças
        leads = ControladorLead.listar_leads()
        presencas = {
            f["lead_id"]: f for f in ControladorFrequencia.por_aula(aula_id)
        }
        for l in leads:
            f = presencas.get(l["id"])
            presente = bool(f and f.get("presente"))
            obs = (f or {}).get("observacao", "") or ""
            self._tabela.insert(
                "", "end", iid=str(l["id"]),
                values=(
                    l["id"], l.get("nome_completo", ""),
                    "\u2714 Presente" if presente else "\u2716 Ausente",
                    obs,
                ),
            )
        self._atualizar_media()

    def _atualizar_media(self):
        try:
            m = ControladorFrequencia.media_geral()
            self._lbl_media.configure(
                text=f"Média geral de presença: {m:.1f}%",
            )
        except Exception:
            self._lbl_media.configure(text="")

    # =================================================================
    def _toggle(self):
        sel = self._tabela.selection()
        if not sel:
            return
        aula_id = self._aula_id_atual()
        if not aula_id:
            return
        for iid in sel:
            valores = self._tabela.item(iid, "values")
            estava_presente = "Presente" in (valores[2] if len(valores) > 2 else "")
            novo = not estava_presente
            ControladorFrequencia.registrar(
                aula_id, int(iid), novo, valores[3] if len(valores) > 3 else "",
            )
        NotificacaoFlutuante.exibir(
            self.winfo_toplevel(), "Presença atualizada.",
            tipo="sucesso", duracao_ms=1400,
        )
        self._popular_chamada()

    def _marcar_todos(self, presente: bool):
        aula_id = self._aula_id_atual()
        if not aula_id:
            return
        for iid in self._tabela.get_children():
            ControladorFrequencia.registrar(aula_id, int(iid), presente, "")
        NotificacaoFlutuante.exibir(
            self.winfo_toplevel(),
            "Todos marcados como presentes." if presente
            else "Todos marcados como ausentes.",
            tipo="sucesso",
        )
        self._popular_chamada()
