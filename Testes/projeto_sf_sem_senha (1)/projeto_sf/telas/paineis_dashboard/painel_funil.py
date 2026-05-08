"""Painel do Funil de Origem - editar números do funil e origens."""
import tkinter as tk
from tkinter import ttk

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.campo_entrada import CampoArredondado
from componentes.notificacoes import NotificacaoFlutuante
from controladores.controlador_academico import ControladorFunil


REFERENCIA_PADRAO = "ATUAL"

ETAPAS_FUNIL = (
    ("visitantes", "Visitantes", tema.FUNIL_VISITANTES),
    ("leads", "Leads", tema.FUNIL_LEADS),
    ("negociacoes", "Negociações", tema.FUNIL_NEGOCIACOES),
    ("vendas", "Vendas", tema.FUNIL_VENDAS),
    ("alunos_ativos", "Alunos Ativos", tema.FUNIL_ATIVOS),
)


class PainelFunil(tk.Frame):

    def __init__(self, mestre, dashboard=None):
        super().__init__(mestre, bg=tema.OFFWHITE)
        self.pack(fill="both", expand=True)
        self.dashboard = dashboard

        topo = tk.Frame(self, bg=tema.OFFWHITE)
        topo.pack(fill="x", padx=20, pady=(20, 10))
        topo.columnconfigure(0, weight=1, minsize=420)
        topo.columnconfigure(1, weight=1, minsize=420)

        # Coluna 1: Editar números do funil
        card_funil = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card_funil.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._construir_funil(card_funil)

        # Coluna 2: Editar origens
        card_origens = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card_origens.grid(row=0, column=1, sticky="nsew")
        self._construir_origens(card_origens)

    # =================================================================
    def _construir_funil(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Funil de Conversão", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(15),
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            bloco, text="Edite os totais de cada etapa do funil:",
            bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(10),
        ).pack(anchor="w", pady=(0, 14))

        dados = ControladorFunil.obter_periodo(REFERENCIA_PADRAO)

        # Para evitar sobreposição: rótulo em cima, número abaixo, cada
        # bloco com largura fixa
        self._campos_funil = {}
        for chave, rotulo, cor in ETAPAS_FUNIL:
            linha = tk.Frame(bloco, bg=tema.BRANCO_PURO)
            linha.pack(fill="x", pady=8)

            # Indicador colorido (círculo)
            ind = tk.Canvas(
                linha, width=14, height=14, bg=tema.BRANCO_PURO,
                highlightthickness=0, bd=0,
            )
            ind.pack(side="left", padx=(0, 10))
            ind.create_oval(2, 2, 13, 13, fill=cor, outline="")

            tk.Label(
                linha, text=rotulo, bg=tema.BRANCO_PURO,
                fg=tema.AZUL_ESCURO, font=tema.fonte_corpo(11),
                width=14, anchor="w",
            ).pack(side="left")

            campo = CampoArredondado(
                linha, placeholder="0", largura=160, altura=38,
                cor_fundo_pai=tema.BRANCO_PURO,
            )
            campo.pack(side="left", padx=(8, 0))
            campo.definir_valor(str(dados.get(chave, 0) or 0))

            self._campos_funil[chave] = campo

        BotaoArredondado(
            bloco, texto="Salvar Funil", comando=self._salvar_funil,
            largura=400, altura=44, fonte=tema.fonte_destaque(12),
        ).pack(pady=(20, 0))

        # Visualização do funil
        tk.Label(
            bloco, text="Visualização", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(11),
        ).pack(anchor="w", pady=(20, 4))

        self._canvas_funil = tk.Canvas(
            bloco, width=400, height=220, bg=tema.BRANCO_PURO,
            highlightthickness=0, bd=0,
        )
        self._canvas_funil.pack()
        self._desenhar_funil(dados)

    def _desenhar_funil(self, dados):
        c = self._canvas_funil
        c.delete("all")
        valores = [int(dados.get(k, 0) or 0) for k, _, _ in ETAPAS_FUNIL]
        max_val = max(valores) if valores and max(valores) > 0 else 1

        altura = 38
        topo_y = 6
        for i, ((_chave, rotulo, cor), valor) in enumerate(zip(ETAPAS_FUNIL, valores)):
            rel = max(valor / max_val, 0.18)
            largura_topo = int(340 * rel)
            largura_base = max(60, int(largura_topo * 0.85))
            x_centro = 200
            y_t = topo_y + i * altura
            y_b = y_t + altura - 4
            pontos = [
                x_centro - largura_topo // 2, y_t,
                x_centro + largura_topo // 2, y_t,
                x_centro + largura_base // 2, y_b,
                x_centro - largura_base // 2, y_b,
            ]
            c.create_polygon(pontos, fill=cor, outline="")
            c.create_text(
                x_centro, y_t + 8, text=rotulo, fill="#FFFFFF",
                font=tema.fonte_corpo(9), anchor="n",
            )
            c.create_text(
                x_centro, y_t + 22, text=f"{valor:,}".replace(",", "."),
                fill="#FFFFFF", font=tema.fonte_destaque(11), anchor="n",
            )

    def _salvar_funil(self):
        dados = {}
        for chave, campo in self._campos_funil.items():
            try:
                dados[chave] = int(campo.obter_valor() or 0)
            except (TypeError, ValueError):
                dados[chave] = 0
        sucesso, msg = ControladorFunil.atualizar_periodo(
            REFERENCIA_PADRAO, dados,
        )
        topo = self.winfo_toplevel()
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._desenhar_funil(dados)
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")

    # =================================================================
    def _construir_origens(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Origem dos Leads", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(15),
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            bloco, text="Edite os totais de cada origem:",
            bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(10),
        ).pack(anchor="w", pady=(0, 14))

        # Lista de origens com campo numérico
        origens = ControladorFunil.origens()
        self._campos_origem = {}
        for i, o in enumerate(origens):
            cor = tema.ORIGEM_CORES[i % len(tema.ORIGEM_CORES)]
            linha = tk.Frame(bloco, bg=tema.BRANCO_PURO)
            linha.pack(fill="x", pady=6)

            ind = tk.Canvas(
                linha, width=14, height=14, bg=tema.BRANCO_PURO,
                highlightthickness=0, bd=0,
            )
            ind.pack(side="left", padx=(0, 10))
            ind.create_oval(2, 2, 13, 13, fill=cor, outline="")

            tk.Label(
                linha, text=o.get("origem", ""), bg=tema.BRANCO_PURO,
                fg=tema.AZUL_ESCURO, font=tema.fonte_corpo(11),
                width=18, anchor="w",
            ).pack(side="left")

            campo = CampoArredondado(
                linha, placeholder="0", largura=120, altura=38,
                cor_fundo_pai=tema.BRANCO_PURO,
            )
            campo.pack(side="left", padx=(8, 0))
            campo.definir_valor(str(o.get("quantidade", 0)))
            self._campos_origem[o.get("origem")] = campo

        BotaoArredondado(
            bloco, texto="Salvar Origens", comando=self._salvar_origens,
            largura=400, altura=44, fonte=tema.fonte_destaque(12),
        ).pack(pady=(20, 0))

    def _salvar_origens(self):
        ok = True
        for origem, campo in self._campos_origem.items():
            try:
                qtd = int(campo.obter_valor() or 0)
            except (TypeError, ValueError):
                qtd = 0
            sucesso, _ = ControladorFunil.definir_origem(origem, qtd)
            ok = ok and sucesso
        topo = self.winfo_toplevel()
        if ok:
            NotificacaoFlutuante.exibir(topo, "Origens atualizadas.", tipo="sucesso")
        else:
            NotificacaoFlutuante.exibir(topo, "Falha ao salvar algumas origens.",
                                        tipo="erro")
