"""
Painel de Cadastro do Aluno (Lead).

Reproduz o layout da imagem de referência:
    - Coluna 1 (esquerda): formulário de cadastro
    - Coluna 2 (centro): resumo do lead + jornada do aluno
    - Coluna 3 (direita): funil de origem + gráfico de origem
    - Rodapé: tabela leads recentes + resumo geral
"""
import math
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.campo_entrada import CampoArredondado
from componentes.combo_arredondado import ComboArredondado
from componentes.notificacoes import NotificacaoFlutuante
from controladores.controlador_aluno import (
    ControladorLead,
    CURSOS_DISPONIVEIS,
    ORIGENS_DISPONIVEIS,
    ESTADOS_BRASIL,
    CAPTADORES_PADRAO,
)
from controladores.controlador_academico import ControladorVenda, ControladorPagamento
from modelos.modelo_academico import ModeloOrigemLeads
from utilitarios.validadores import (
    formatar_cpf_progressivo,
    formatar_data_progressivo,
    formatar_telefone_progressivo,
)


JORNADA_ETAPAS = (
    ("Cadastro do aluno (lead)", "Lead cadastrado no sistema."),
    ("Registro da venda (captador)", "Registrar negociação e definir condição."),
    ("Definição do status (Pago / Não pago)", "Definir se o aluno já está pago."),
    ("Registro do pagamento", "Registrar pagamento e emitir comprovante."),
    ("Liberação para turma (pós-venda)", "Liberar aluno para a turma."),
    ("Formação de turma", "Adicionar aluno à turma."),
    ("Início das aulas", "Aulas liberadas conforme calendário."),
    ("Controle de frequência", "Acompanhar presença nas aulas."),
)


class PainelAlunos(tk.Frame):

    def __init__(self, mestre, dashboard=None):
        super().__init__(mestre, bg=tema.OFFWHITE)
        self.pack(fill="both", expand=True)
        self.dashboard = dashboard

        self._lead_em_edicao = None  # id do lead sendo editado (None = novo)

        # Scroll geral (a área é grande)
        self._canvas_scroll = tk.Canvas(
            self, bg=tema.OFFWHITE, highlightthickness=0, bd=0,
        )
        self._canvas_scroll.pack(side="left", fill="both", expand=True)

        scroll_v = ttk.Scrollbar(
            self, orient="vertical", command=self._canvas_scroll.yview,
        )
        scroll_v.pack(side="right", fill="y")
        self._canvas_scroll.configure(yscrollcommand=scroll_v.set)

        self._conteudo = tk.Frame(self._canvas_scroll, bg=tema.OFFWHITE)
        self._win_id = self._canvas_scroll.create_window(
            (0, 0), window=self._conteudo, anchor="nw",
        )
        self._conteudo.bind(
            "<Configure>",
            lambda _e: self._canvas_scroll.configure(
                scrollregion=self._canvas_scroll.bbox("all"),
            ),
        )
        self._canvas_scroll.bind(
            "<Configure>",
            lambda e: self._canvas_scroll.itemconfigure(
                self._win_id, width=e.width,
            ),
        )
        # Scroll com a roda do mouse
        self._canvas_scroll.bind_all(
            "<MouseWheel>", self._scroll_mouse, add="+",
        )

        self._construir()

    def _scroll_mouse(self, evento):
        try:
            self._canvas_scroll.yview_scroll(
                int(-1 * (evento.delta / 120)), "units",
            )
        except Exception:
            pass

    def destroy(self):
        try:
            self._canvas_scroll.unbind_all("<MouseWheel>")
        except Exception:
            pass
        super().destroy()

    # =================================================================
    def _construir(self):
        # 3 colunas em cima
        topo = tk.Frame(self._conteudo, bg=tema.OFFWHITE)
        topo.pack(fill="x", padx=20, pady=(20, 10))
        topo.columnconfigure(0, weight=2, minsize=420)
        topo.columnconfigure(1, weight=1, minsize=300)
        topo.columnconfigure(2, weight=1, minsize=300)

        # Coluna 1: formulário
        form_card = self._card(topo)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._construir_formulario(form_card)

        # Coluna 2: Resumo + jornada
        coluna_central = tk.Frame(topo, bg=tema.OFFWHITE)
        coluna_central.grid(row=0, column=1, sticky="nsew", padx=6)

        resumo_card = self._card(coluna_central)
        resumo_card.pack(fill="x", pady=(0, 10))
        self._construir_resumo(resumo_card)

        jornada_card = self._card(coluna_central)
        jornada_card.pack(fill="both", expand=True)
        self._construir_jornada(jornada_card)

        # Coluna 3: Funil + Origem
        coluna_direita = tk.Frame(topo, bg=tema.OFFWHITE)
        coluna_direita.grid(row=0, column=2, sticky="nsew", padx=(12, 0))

        funil_card = self._card(coluna_direita)
        funil_card.pack(fill="x", pady=(0, 10))
        self._construir_funil(funil_card)

        origem_card = self._card(coluna_direita)
        origem_card.pack(fill="both", expand=True)
        self._construir_origem(origem_card)

        # Rodapé: leads recentes + resumo geral
        rodape = tk.Frame(self._conteudo, bg=tema.OFFWHITE)
        rodape.pack(fill="x", padx=20, pady=(10, 24))
        rodape.columnconfigure(0, weight=2, minsize=520)
        rodape.columnconfigure(1, weight=1, minsize=300)

        tabela_card = self._card(rodape)
        tabela_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._construir_tabela_leads(tabela_card)

        resumo_geral_card = self._card(rodape)
        resumo_geral_card.grid(row=0, column=1, sticky="nsew")
        self._construir_resumo_geral(resumo_geral_card)

    # =================================================================
    def _card(self, mestre, **kwargs) -> tk.Frame:
        f = tk.Frame(
            mestre, bg=tema.BRANCO_PURO,
            highlightbackground=tema.CINZA_BORDA, highlightthickness=1,
        )
        return f

    # =================================================================
    def _construir_formulario(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Dados do Aluno (Lead)",
            bg=tema.BRANCO_PURO, fg=tema.AZUL_ESCURO,
            font=tema.fonte_destaque(13),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))

        # Linha 1: Nome / Data Nascimento / CPF
        self._lbl(bloco, "Nome completo *", 1, 0)
        self._lbl(bloco, "Data de nascimento", 1, 1)
        self._lbl(bloco, "CPF", 1, 2)

        self._campo_nome = CampoArredondado(
            bloco, placeholder="João da Silva", largura=240, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_nome.grid(row=2, column=0, padx=(0, 8), pady=4, sticky="w")

        self._campo_data = CampoArredondado(
            bloco, placeholder="15/04/2002", largura=160, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_data.grid(row=2, column=1, padx=8, pady=4, sticky="w")

        self._campo_cpf = CampoArredondado(
            bloco, placeholder="123.456.789-01", largura=160,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_cpf.grid(row=2, column=2, padx=(8, 0), pady=4, sticky="w")

        # Auto-formatadores
        self._campo_data.widget_entry().bind(
            "<KeyRelease>", self._formatar_data,
        )
        self._campo_cpf.widget_entry().bind(
            "<KeyRelease>", self._formatar_cpf,
        )

        # Linha 2: Email / Telefone
        self._lbl(bloco, "E-mail *", 3, 0)
        self._lbl(bloco, "Telefone / WhatsApp", 3, 1, colspan=2)

        self._campo_email = CampoArredondado(
            bloco, placeholder="joao.silva@email.com", largura=240,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_email.grid(row=4, column=0, padx=(0, 8), pady=4, sticky="w")

        self._campo_telefone = CampoArredondado(
            bloco, placeholder="(11) 98765-4321", largura=336,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_telefone.grid(row=4, column=1, columnspan=2, padx=(8, 0), pady=4, sticky="w")

        self._campo_telefone.widget_entry().bind(
            "<KeyRelease>", self._formatar_telefone,
        )

        # Linha 3: Endereço / Cidade / Estado
        self._lbl(bloco, "Endereço", 5, 0)
        self._lbl(bloco, "Cidade", 5, 1)
        self._lbl(bloco, "Estado", 5, 2)

        self._campo_endereco = CampoArredondado(
            bloco, placeholder="Rua das Flores, 123", largura=240,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_endereco.grid(row=6, column=0, padx=(0, 8), pady=4, sticky="w")

        self._campo_cidade = CampoArredondado(
            bloco, placeholder="São Paulo", largura=160,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._campo_cidade.grid(row=6, column=1, padx=8, pady=4, sticky="w")

        self._combo_estado = ComboArredondado(
            bloco, opcoes=list(ESTADOS_BRASIL), valor_inicial="SP",
            largura=160, cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_estado.grid(row=6, column=2, padx=(8, 0), pady=4, sticky="w")

        # Linha 4: Curso / Como conheceu / Captador
        self._lbl(bloco, "Curso de interesse *", 7, 0)
        self._lbl(bloco, "Como conheceu?", 7, 1)
        self._lbl(bloco, "Captador (vendedor) *", 7, 2)

        self._combo_curso = ComboArredondado(
            bloco, opcoes=list(CURSOS_DISPONIVEIS),
            valor_inicial=CURSOS_DISPONIVEIS[0], largura=240,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_curso.grid(row=8, column=0, padx=(0, 8), pady=4, sticky="w")

        self._combo_origem = ComboArredondado(
            bloco, opcoes=list(ORIGENS_DISPONIVEIS),
            valor_inicial=ORIGENS_DISPONIVEIS[0], largura=160,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_origem.grid(row=8, column=1, padx=8, pady=4, sticky="w")

        self._combo_captador = ComboArredondado(
            bloco, opcoes=list(CAPTADORES_PADRAO),
            valor_inicial=CAPTADORES_PADRAO[0], largura=160,
            cor_fundo_pai=tema.BRANCO_PURO,
        )
        self._combo_captador.grid(row=8, column=2, padx=(8, 0), pady=4, sticky="w")

        # Linha 5: Observações
        self._lbl(bloco, "Observações", 9, 0, colspan=3)

        bg_text = tk.Frame(
            bloco, bg=tema.AMARELO_INPUT,
            highlightbackground=tema.AMARELO_INPUT, highlightthickness=0,
        )
        bg_text.grid(row=10, column=0, columnspan=3, sticky="we", pady=4)
        self._campo_obs = tk.Text(
            bg_text, height=3, bg=tema.AMARELO_INPUT,
            fg=tema.AZUL_ESCURO, font=tema.fonte_corpo(10),
            relief="flat", bd=0, wrap="word", padx=10, pady=8,
        )
        self._campo_obs.pack(fill="both", expand=True, padx=2, pady=2)
        self._campo_obs.insert("1.0", "Interessado no curso noturno.")

        # Linha 6: Botões
        botoes = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        botoes.grid(row=11, column=0, columnspan=3, sticky="e", pady=(16, 0))

        BotaoArredondado(
            botoes, texto="Cancelar", comando=self._cancelar,
            cor_fundo=tema.CINZA_CLARO, cor_hover=tema.CINZA_BORDA,
            cor_press="#D5D7DF", cor_texto=tema.AZUL_ESCURO,
            largura=120, altura=40, fonte=tema.fonte_destaque(11),
        ).pack(side="left", padx=(0, 10))

        self._botao_salvar = BotaoArredondado(
            botoes, texto="Salvar Lead", comando=self._salvar,
            largura=140, altura=40, fonte=tema.fonte_destaque(11),
        )
        self._botao_salvar.pack(side="left")

    def _lbl(self, pai, texto, linha, coluna, colspan=1):
        tk.Label(
            pai, text=texto, bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(10),
        ).grid(row=linha, column=coluna, columnspan=colspan,
               sticky="w", pady=(8, 2))

    # =================================================================
    def _formatar_cpf(self, _e):
        v = self._campo_cpf.obter_valor()
        nv = formatar_cpf_progressivo(v)
        if nv != v:
            self._campo_cpf.definir_valor(nv)
            self._campo_cpf.widget_entry().icursor("end")

    def _formatar_data(self, _e):
        v = self._campo_data.obter_valor()
        nv = formatar_data_progressivo(v)
        if nv != v:
            self._campo_data.definir_valor(nv)
            self._campo_data.widget_entry().icursor("end")

    def _formatar_telefone(self, _e):
        v = self._campo_telefone.obter_valor()
        nv = formatar_telefone_progressivo(v)
        if nv != v:
            self._campo_telefone.definir_valor(nv)
            self._campo_telefone.widget_entry().icursor("end")

    # =================================================================
    def _coletar_dados(self) -> dict:
        return {
            "nome_completo": self._campo_nome.obter_valor().strip(),
            "data_nascimento": self._campo_data.obter_valor().strip(),
            "cpf": self._campo_cpf.obter_valor().strip(),
            "email": self._campo_email.obter_valor().strip().lower(),
            "telefone": self._campo_telefone.obter_valor().strip(),
            "endereco": self._campo_endereco.obter_valor().strip(),
            "cidade": self._campo_cidade.obter_valor().strip(),
            "estado": self._combo_estado.obter_valor().strip().upper(),
            "curso_interesse": self._combo_curso.obter_valor(),
            "como_conheceu": self._combo_origem.obter_valor(),
            "captador": self._combo_captador.obter_valor(),
            "observacoes": self._campo_obs.get("1.0", "end").strip(),
            "status": "LEAD",
        }

    def _limpar_formulario(self):
        for c in (
            self._campo_nome, self._campo_data, self._campo_cpf,
            self._campo_email, self._campo_telefone,
            self._campo_endereco, self._campo_cidade,
        ):
            try:
                c.definir_valor("")
                c.limpar_erro()
            except Exception:
                pass
        self._combo_estado.definir_valor("SP")
        self._combo_curso.definir_valor(CURSOS_DISPONIVEIS[0])
        self._combo_origem.definir_valor(ORIGENS_DISPONIVEIS[0])
        self._combo_captador.definir_valor(CAPTADORES_PADRAO[0])
        self._campo_obs.delete("1.0", "end")

    def _cancelar(self):
        self._limpar_formulario()
        self._lead_em_edicao = None
        try:
            self._botao_salvar._texto = "Salvar Lead"
            self._botao_salvar._desenhar()
        except Exception:
            pass
        NotificacaoFlutuante.exibir(
            self.winfo_toplevel(), "Formulário limpo.", tipo="info",
            duracao_ms=1600,
        )

    def _salvar(self):
        dados = self._coletar_dados()
        if self._lead_em_edicao:
            sucesso, msg = ControladorLead.atualizar_lead(
                self._lead_em_edicao, dados,
            )
        else:
            sucesso, msg, _id = ControladorLead.cadastrar_lead(dados)

        topo = self.winfo_toplevel()
        if not sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")
            return
        NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
        self._limpar_formulario()
        self._lead_em_edicao = None
        try:
            self._botao_salvar._texto = "Salvar Lead"
            self._botao_salvar._desenhar()
        except Exception:
            pass
        self._recarregar_dinamicos()

    # =================================================================
    def _construir_resumo(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            bloco, text="Resumo do Lead",
            bg=tema.BRANCO_PURO, fg=tema.AZUL_ESCURO,
            font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 12))

        # Status atual com badge
        linha_status = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        linha_status.pack(fill="x", pady=4)
        tk.Label(
            linha_status, text="\u2756 Status atual:",
            bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(10),
        ).pack(side="left")
        self._badge_status = tk.Label(
            linha_status, text="LEAD",
            bg=tema.COR_STATUS["LEAD"], fg="#FFFFFF",
            font=tema.fonte_destaque(9), padx=10, pady=2,
        )
        self._badge_status.pack(side="left", padx=8)

        self._lbl_data_cad = self._linha_resumo(
            bloco, "\U0001F4C5 Data do cadastro:", "—",
        )
        self._lbl_captador = self._linha_resumo(
            bloco, "\u270D Captador:", "—",
        )
        self._lbl_curso = self._linha_resumo(
            bloco, "\U0001F4D6 Curso de interesse:", "—",
        )

        self._atualizar_resumo()

    def _linha_resumo(self, pai, rotulo, valor) -> tk.Label:
        linha = tk.Frame(pai, bg=tema.BRANCO_PURO)
        linha.pack(fill="x", pady=4)
        tk.Label(
            linha, text=rotulo, bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
        ).pack(side="left")
        v = tk.Label(
            linha, text=valor, bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(10),
        )
        v.pack(side="right")
        return v

    def _atualizar_resumo(self):
        leads = ControladorLead.listar_leads()
        if leads:
            ultimo = leads[0]
            self._lbl_data_cad.configure(text=str(ultimo.get("criado_em", "—"))[:16])
            self._lbl_captador.configure(text=ultimo.get("captador") or "—")
            self._lbl_curso.configure(text=ultimo.get("curso_interesse") or "—")
            status = (ultimo.get("status") or "LEAD").upper()
            cor_b = tema.COR_STATUS.get(status, tema.AZUL_PRINCIPAL)
            self._badge_status.configure(text=status, bg=cor_b)

    # =================================================================
    def _construir_jornada(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            bloco, text="Jornada do Aluno",
            bg=tema.BRANCO_PURO, fg=tema.AZUL_ESCURO,
            font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 8))

        for indice, (titulo, descricao) in enumerate(JORNADA_ETAPAS, start=1):
            ativo = indice <= 3
            self._etapa_jornada(bloco, indice, titulo, descricao, ativo)

    def _etapa_jornada(self, pai, numero, titulo, descricao, ativo):
        linha = tk.Frame(pai, bg=tema.BRANCO_PURO)
        linha.pack(fill="x", pady=4, anchor="w")

        cor_circulo = tema.AZUL_PRINCIPAL if ativo else tema.CINZA_BORDA
        cor_num = "#FFFFFF" if ativo else tema.CINZA_TEXTO

        circulo = tk.Canvas(
            linha, width=26, height=26, bg=tema.BRANCO_PURO,
            highlightthickness=0, bd=0,
        )
        circulo.pack(side="left", padx=(0, 10))
        circulo.create_oval(2, 2, 24, 24, fill=cor_circulo, outline="")
        circulo.create_text(
            13, 13, text=str(numero), fill=cor_num,
            font=tema.fonte_destaque(10),
        )

        bloco_texto = tk.Frame(linha, bg=tema.BRANCO_PURO)
        bloco_texto.pack(side="left", anchor="w", fill="x", expand=True)
        tk.Label(
            bloco_texto, text=titulo, bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO if ativo else tema.CINZA_TITULO,
            font=tema.fonte_destaque(10), anchor="w", justify="left",
        ).pack(anchor="w")
        tk.Label(
            bloco_texto, text=descricao, bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(9),
            anchor="w", justify="left",
        ).pack(anchor="w")

    # =================================================================
    def _construir_funil(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=18, pady=14)

        topo = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        topo.pack(fill="x")
        tk.Label(
            topo, text="\u2207 Funil de Origem",
            bg=tema.BRANCO_PURO, fg=tema.AZUL_ESCURO,
            font=tema.fonte_destaque(13),
        ).pack(side="left")
        tk.Label(
            topo, text="Período: Este mês",
            bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(9),
        ).pack(side="right")

        from controladores.controlador_academico import ControladorFunil
        dados = ControladorFunil.obter_periodo("ATUAL")
        # mapeia chaves -> rótulos / cores
        etapas = (
            ("visitantes", "Visitantes", tema.FUNIL_VISITANTES),
            ("leads", "Leads", tema.FUNIL_LEADS),
            ("negociacoes", "Negociações", tema.FUNIL_NEGOCIACOES),
            ("vendas", "Vendas", tema.FUNIL_VENDAS),
            ("alunos_ativos", "Alunos Ativos", tema.FUNIL_ATIVOS),
        )

        canvas = tk.Canvas(
            bloco, width=280, height=260, bg=tema.BRANCO_PURO,
            highlightthickness=0, bd=0,
        )
        canvas.pack(pady=(8, 0))

        # desenha trapézios empilhados
        valores = [int(dados.get(k, 0) or 0) for k, _, _ in etapas]
        max_val = max(valores) if valores and max(valores) > 0 else 1
        altura_etapa = 44
        topo_y = 6
        for i, ((_chave, rotulo, cor), valor) in enumerate(zip(etapas, valores)):
            rel = max(valor / max_val, 0.18)
            largura_topo = int(220 * rel)
            largura_base = int(220 * (1 - i * 0.05) * (rel - 0.04))
            largura_base = max(largura_base, 60)
            x_centro = 140
            y_t = topo_y + i * altura_etapa
            y_b = y_t + altura_etapa - 4
            pontos = [
                x_centro - largura_topo // 2, y_t,
                x_centro + largura_topo // 2, y_t,
                x_centro + largura_base // 2, y_b,
                x_centro - largura_base // 2, y_b,
            ]
            canvas.create_polygon(pontos, fill=cor, outline="")
            canvas.create_text(
                x_centro, y_t + 6, text=rotulo, fill="#FFFFFF",
                font=tema.fonte_corpo(9), anchor="n",
            )
            canvas.create_text(
                x_centro, y_t + 22, text=f"{valor:,}".replace(",", "."),
                fill="#FFFFFF", font=tema.fonte_destaque(13), anchor="n",
            )

        # legenda à direita: percentuais de conversão
        legenda = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        legenda.pack(fill="x", pady=(8, 0))
        for i in range(len(etapas) - 1):
            origem, _, _ = etapas[i]
            destino, dest_rotulo, _ = etapas[i + 1]
            v_origem = max(valores[i], 1)
            v_destino = valores[i + 1]
            pct = (v_destino / v_origem) * 100
            tk.Label(
                legenda,
                text=f"{pct:.1f}%   conversão {etapas[i][1]} \u2192 {dest_rotulo}",
                bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
                font=tema.fonte_corpo(9), anchor="w",
            ).pack(anchor="w", pady=1)

    # =================================================================
    def _construir_origem(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            bloco, text="Origem dos Leads",
            bg=tema.BRANCO_PURO, fg=tema.AZUL_ESCURO,
            font=tema.fonte_destaque(13),
        ).pack(anchor="w")

        # Busca no banco
        origens = ModeloOrigemLeads.listar()  # lista de dict {origem, quantidade}
        total = sum(o.get("quantidade", 0) for o in origens) or 1

        canvas = tk.Canvas(
            bloco, width=180, height=180, bg=tema.BRANCO_PURO,
            highlightthickness=0, bd=0,
        )
        canvas.pack(side="left", padx=(0, 14), pady=8)

        # gráfico pizza tipo donut
        x0, y0, x1, y1 = 10, 10, 170, 170
        inicio = 0
        for i, o in enumerate(origens):
            qtd = o.get("quantidade", 0)
            extensao = (qtd / total) * 360
            if extensao <= 0:
                continue
            cor = tema.ORIGEM_CORES[i % len(tema.ORIGEM_CORES)]
            canvas.create_arc(
                x0, y0, x1, y1, start=inicio, extent=extensao,
                fill=cor, outline=tema.BRANCO_PURO, width=2,
            )
            inicio += extensao

        # Furo central (donut)
        canvas.create_oval(48, 48, 132, 132, fill=tema.BRANCO_PURO, outline="")
        canvas.create_text(
            90, 84, text=f"{total}", fill=tema.AZUL_ESCURO,
            font=tema.fonte_destaque(18),
        )
        canvas.create_text(
            90, 104, text="leads", fill=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(9),
        )

        # Legenda
        legenda = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        legenda.pack(side="left", fill="both", expand=True)
        for i, o in enumerate(origens):
            cor = tema.ORIGEM_CORES[i % len(tema.ORIGEM_CORES)]
            qtd = o.get("quantidade", 0)
            pct = (qtd / total) * 100 if total else 0
            linha = tk.Frame(legenda, bg=tema.BRANCO_PURO)
            linha.pack(fill="x", pady=2)
            ponto = tk.Canvas(
                linha, width=12, height=12, bg=tema.BRANCO_PURO,
                highlightthickness=0, bd=0,
            )
            ponto.pack(side="left", padx=(0, 8))
            ponto.create_oval(2, 2, 11, 11, fill=cor, outline="")
            tk.Label(
                linha, text=o.get("origem", ""), bg=tema.BRANCO_PURO,
                fg=tema.AZUL_ESCURO, font=tema.fonte_corpo(10),
            ).pack(side="left")
            tk.Label(
                linha, text=f"{qtd} ({pct:.1f}%)",
                bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
                font=tema.fonte_corpo(9),
            ).pack(side="right")

    # =================================================================
    def _construir_tabela_leads(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=18, pady=14)

        topo = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        topo.pack(fill="x", pady=(0, 8))
        tk.Label(
            topo, text="Leads Recentes", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(side="left")

        link_ver = tk.Label(
            topo, text="Ver todos os leads \u2192", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_PRINCIPAL, cursor="hand2",
            font=tema.fonte_corpo(10),
        )
        link_ver.pack(side="right")
        link_ver.bind("<Button-1>", lambda _e: self._abrir_lista_completa())

        # tabela
        colunas = ("nome", "curso", "captador", "status", "data")
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except Exception:
            pass
        estilo.configure(
            "SF.Treeview", background=tema.BRANCO_PURO, foreground=tema.AZUL_ESCURO,
            fieldbackground=tema.BRANCO_PURO, rowheight=28,
            font=tema.fonte_corpo(10), borderwidth=0,
        )
        estilo.configure(
            "SF.Treeview.Heading", background=tema.OFFWHITE,
            foreground=tema.CINZA_TEXTO, font=tema.fonte_destaque(10),
            relief="flat",
        )
        estilo.map("SF.Treeview", background=[("selected", tema.AZUL_HOVER)])

        self._tabela = ttk.Treeview(
            bloco, columns=colunas, show="headings",
            style="SF.Treeview", height=6,
        )
        self._tabela.heading("nome", text="Nome")
        self._tabela.heading("curso", text="Curso")
        self._tabela.heading("captador", text="Captador")
        self._tabela.heading("status", text="Status")
        self._tabela.heading("data", text="Data")
        self._tabela.column("nome", width=180, anchor="w")
        self._tabela.column("curso", width=180, anchor="w")
        self._tabela.column("captador", width=130, anchor="w")
        self._tabela.column("status", width=90, anchor="center")
        self._tabela.column("data", width=110, anchor="center")
        self._tabela.pack(fill="both", expand=True)

        # menu de contexto
        self._menu_tabela = tk.Menu(self._tabela, tearoff=0)
        self._menu_tabela.add_command(
            label="\u270E Editar lead", command=self._editar_selecionado,
        )
        self._menu_tabela.add_command(
            label="\U0001F5D1  Excluir lead", command=self._excluir_selecionado,
        )
        self._menu_tabela.add_separator()
        self._menu_tabela.add_command(
            label="Marcar como NEGOCIAÇÃO",
            command=lambda: self._mudar_status("NEGOCIACAO"),
        )
        self._menu_tabela.add_command(
            label="Marcar como PAGO",
            command=lambda: self._mudar_status("PAGO"),
        )
        self._menu_tabela.add_command(
            label="Marcar como NÃO PAGO",
            command=lambda: self._mudar_status("NAO_PAGO"),
        )

        self._tabela.bind("<Button-3>", self._abrir_menu_tabela)
        self._tabela.bind("<Double-1>", lambda _e: self._editar_selecionado())

        self._popular_tabela()

    def _popular_tabela(self):
        for i in self._tabela.get_children():
            self._tabela.delete(i)
        leads = ControladorLead.listar_leads()
        for l in leads[:50]:
            data_str = str(l.get("criado_em", ""))[:10]
            try:
                d = datetime.strptime(data_str, "%Y-%m-%d")
                data_str = d.strftime("%d/%m/%Y")
            except Exception:
                pass
            self._tabela.insert(
                "", "end", iid=str(l["id"]),
                values=(
                    l.get("nome_completo", ""),
                    l.get("curso_interesse", ""),
                    l.get("captador", ""),
                    l.get("status", "LEAD"),
                    data_str,
                ),
            )

    def _abrir_menu_tabela(self, evento):
        item = self._tabela.identify_row(evento.y)
        if item:
            self._tabela.selection_set(item)
            try:
                self._menu_tabela.tk_popup(evento.x_root, evento.y_root)
            finally:
                self._menu_tabela.grab_release()

    def _editar_selecionado(self):
        sel = self._tabela.selection()
        if not sel:
            return
        id_lead = int(sel[0])
        lead = ControladorLead.buscar_lead(id_lead)
        if not lead:
            return
        # Carrega no formulário
        self._campo_nome.definir_valor(lead.get("nome_completo", ""))
        self._campo_data.definir_valor(lead.get("data_nascimento", "") or "")
        self._campo_cpf.definir_valor(lead.get("cpf", "") or "")
        self._campo_email.definir_valor(lead.get("email", ""))
        self._campo_telefone.definir_valor(lead.get("telefone", "") or "")
        self._campo_endereco.definir_valor(lead.get("endereco", "") or "")
        self._campo_cidade.definir_valor(lead.get("cidade", "") or "")
        self._combo_estado.definir_valor(lead.get("estado") or "SP")
        self._combo_curso.definir_valor(
            lead.get("curso_interesse") or CURSOS_DISPONIVEIS[0]
        )
        self._combo_origem.definir_valor(
            lead.get("como_conheceu") or ORIGENS_DISPONIVEIS[0]
        )
        self._combo_captador.definir_valor(
            lead.get("captador") or CAPTADORES_PADRAO[0]
        )
        self._campo_obs.delete("1.0", "end")
        self._campo_obs.insert("1.0", lead.get("observacoes") or "")
        self._lead_em_edicao = id_lead
        try:
            self._botao_salvar._texto = "Atualizar Lead"
            self._botao_salvar._desenhar()
        except Exception:
            pass
        NotificacaoFlutuante.exibir(
            self.winfo_toplevel(),
            f"Editando lead #{id_lead}", tipo="info", duracao_ms=1500,
        )
        # Rola para o topo
        self._canvas_scroll.yview_moveto(0)

    def _excluir_selecionado(self):
        sel = self._tabela.selection()
        if not sel:
            return
        id_lead = int(sel[0])
        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir este lead?",
            parent=self.winfo_toplevel(),
        ):
            return
        sucesso, msg = ControladorLead.excluir_lead(id_lead)
        topo = self.winfo_toplevel()
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._recarregar_dinamicos()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")

    def _mudar_status(self, novo):
        sel = self._tabela.selection()
        if not sel:
            return
        id_lead = int(sel[0])
        sucesso, msg = ControladorLead.alterar_status(id_lead, novo)
        topo = self.winfo_toplevel()
        if sucesso:
            NotificacaoFlutuante.exibir(topo, msg, tipo="sucesso")
            self._popular_tabela()
            self._atualizar_resumo()
        else:
            NotificacaoFlutuante.exibir(topo, msg, tipo="erro")

    def _abrir_lista_completa(self):
        if self.dashboard:
            self.dashboard.selecionar_painel("alunos")
        NotificacaoFlutuante.exibir(
            self.winfo_toplevel(),
            f"Total de leads: {ControladorLead.total_leads()}",
            tipo="info", duracao_ms=2200,
        )

    # =================================================================
    def _construir_resumo_geral(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            bloco, text="Resumo Geral", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(0, 8))

        # Valores
        total_leads = ControladorLead.total_leads()
        total_vendas = ControladorVenda.total()
        faturamento = ControladorVenda.faturamento()
        contagem = ControladorLead.contagem_status()
        ativos = contagem.get("ATIVO", 0) + contagem.get("PAGO", 0)
        conv = (total_vendas / total_leads * 100) if total_leads else 0

        grid = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self._mini_card(grid, 0, 0, "\u2632", "Leads (este mês)",
                        str(total_leads), tema.AZUL_PRINCIPAL)
        self._mini_card(grid, 0, 1, "\u26C2", "Vendas (este mês)",
                        str(total_vendas), tema.VERDE_SUCESSO)
        self._mini_card(grid, 1, 0, "$", "Faturamento (este mês)",
                        f"R$ {faturamento:,.2f}".replace(",", "v")
                            .replace(".", ",").replace("v", "."),
                        tema.AMARELO_DOURADO)
        self._mini_card(grid, 1, 1, "%", "Conversão (este mês)",
                        f"{conv:.1f}%", tema.FUNIL_VENDAS)

    def _mini_card(self, pai, r, c, icone, rotulo, valor, cor):
        card = tk.Frame(
            pai, bg=tema.OFFWHITE, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
        interno = tk.Frame(card, bg=tema.OFFWHITE)
        interno.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            interno, text=icone, bg=tema.OFFWHITE, fg=cor,
            font=tema.fonte_destaque(16),
        ).pack(anchor="w")
        tk.Label(
            interno, text=rotulo, bg=tema.OFFWHITE,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(9),
        ).pack(anchor="w")
        tk.Label(
            interno, text=valor, bg=tema.OFFWHITE,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(15),
        ).pack(anchor="w", pady=(4, 0))

    # =================================================================
    def _recarregar_dinamicos(self):
        try:
            self._popular_tabela()
            self._atualizar_resumo()
        except Exception:
            pass
