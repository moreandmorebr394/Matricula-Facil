"""Tela principal: Dashboard / Cadastro do Aluno (Lead).

Reproduz fielmente o layout do mockup:
- Coluna 1: formulario de cadastro
- Coluna 2: resumo + jornada do aluno
- Coluna 3: funil de origem + origem dos leads
- Rodape: leads recentes + resumo geral
"""
import tkinter as tk
from tkinter import messagebox
from typing import Callable

from componentes.badge import Badge
from componentes.botao import BotaoPrimario, BotaoSecundario
from componentes.campo_entrada import (CampoEntrada, CampoSelecao,
                                        CampoTextoLongo)
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from dados.modelos import Lead
from utilitarios.animacoes import animar_valor
from utilitarios.graficos import GraficoFunil, GraficoPizza


# Listas usadas nos selects
ESTADOS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
           "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
           "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
CURSOS = ["Marketing Digital", "Social Media", "Trafego Pago",
          "Design Grafico", "Programacao Web", "UX/UI Design", "Copywriting"]
ORIGENS = ["Instagram", "Indicacao", "Google Ads", "Facebook Ads",
           "Site / Organico", "Outros"]
CAPTADORES = ["Maria Santos", "Carlos Lima", "Joao Pereira", "Ana Costa"]


class TelaDashboard(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self.navegar_para = navegar_para

        self._construir()

    # ------------------------------------------------------------------
    def _construir(self):
        # Container com scroll vertical (caso a tela seja menor)
        self.canvas_scroll = tk.Canvas(
            self, bg=Cores.FUNDO_PRINCIPAL, highlightthickness=0, bd=0,
        )
        self.canvas_scroll.pack(side="left", fill="both", expand=True)

        scroll_v = tk.Scrollbar(
            self, orient="vertical", command=self.canvas_scroll.yview,
        )
        scroll_v.pack(side="right", fill="y")
        self.canvas_scroll.configure(yscrollcommand=scroll_v.set)

        self.conteudo = tk.Frame(self.canvas_scroll, bg=Cores.FUNDO_PRINCIPAL)
        self.canvas_scroll.create_window((0, 0), window=self.conteudo, anchor="nw")

        self.conteudo.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.configure(
                scrollregion=self.canvas_scroll.bbox("all")
            ),
        )
        self.canvas_scroll.bind_all("<MouseWheel>", self._scroll_mouse)

        # Grid 3 colunas
        topo = tk.Frame(self.conteudo, bg=Cores.FUNDO_PRINCIPAL)
        topo.pack(fill="x", padx=24, pady=(20, 0))

        topo.grid_columnconfigure(0, weight=3, uniform="cols")
        topo.grid_columnconfigure(1, weight=2, uniform="cols")
        topo.grid_columnconfigure(2, weight=2, uniform="cols")

        self._coluna_formulario(topo).grid(
            row=0, column=0, sticky="nsew", padx=(0, 12),
        )
        self._coluna_resumo(topo).grid(
            row=0, column=1, sticky="nsew", padx=6,
        )
        self._coluna_analytics(topo).grid(
            row=0, column=2, sticky="nsew", padx=(12, 0),
        )

        # Rodape: Leads recentes + resumo geral
        rodape = tk.Frame(self.conteudo, bg=Cores.FUNDO_PRINCIPAL)
        rodape.pack(fill="x", padx=24, pady=20)
        rodape.grid_columnconfigure(0, weight=3, uniform="r")
        rodape.grid_columnconfigure(1, weight=2, uniform="r")

        self._card_leads_recentes(rodape).grid(
            row=0, column=0, sticky="nsew", padx=(0, 12),
        )
        self._card_resumo_geral(rodape).grid(
            row=0, column=1, sticky="nsew", padx=(12, 0),
        )

    def _scroll_mouse(self, evento):
        try:
            self.canvas_scroll.yview_scroll(int(-1 * (evento.delta / 120)), "units")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # COLUNA 1: FORMULARIO
    # ------------------------------------------------------------------
    def _coluna_formulario(self, parent) -> tk.Frame:
        card = CardComCabecalho(parent, titulo="Dados do Aluno (Lead)", icone="👤")
        c = card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)

        # Linha 1: Nome, Data nascimento, CPF
        linha1 = tk.Frame(c, bg=Cores.CARD_FUNDO)
        linha1.pack(fill="x", pady=(0, 12))
        linha1.grid_columnconfigure(0, weight=2, uniform="l1")
        linha1.grid_columnconfigure(1, weight=1, uniform="l1")
        linha1.grid_columnconfigure(2, weight=1, uniform="l1")

        self.campo_nome = CampoEntrada(
            linha1, rotulo="Nome completo", placeholder="Joao da Silva",
            obrigatorio=True,
        )
        self.campo_nome.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.campo_nascimento = CampoEntrada(
            linha1, rotulo="Data de nascimento", placeholder="dd/mm/aaaa",
        )
        self.campo_nascimento.grid(row=0, column=1, sticky="ew", padx=4)

        self.campo_cpf = CampoEntrada(
            linha1, rotulo="CPF", placeholder="000.000.000-00",
        )
        self.campo_cpf.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        # Linha 2: Email + Telefone
        linha2 = tk.Frame(c, bg=Cores.CARD_FUNDO)
        linha2.pack(fill="x", pady=12)
        linha2.grid_columnconfigure(0, weight=1, uniform="l2")
        linha2.grid_columnconfigure(1, weight=1, uniform="l2")

        self.campo_email = CampoEntrada(
            linha2, rotulo="E-mail", placeholder="exemplo@email.com",
            obrigatorio=True,
        )
        self.campo_email.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.campo_telefone = CampoEntrada(
            linha2, rotulo="Telefone / WhatsApp",
            placeholder="(11) 98765-4321",
        )
        self.campo_telefone.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        # Linha 3: Endereco + Cidade + Estado
        linha3 = tk.Frame(c, bg=Cores.CARD_FUNDO)
        linha3.pack(fill="x", pady=12)
        linha3.grid_columnconfigure(0, weight=2, uniform="l3")
        linha3.grid_columnconfigure(1, weight=1, uniform="l3")
        linha3.grid_columnconfigure(2, weight=1, uniform="l3")

        self.campo_endereco = CampoEntrada(
            linha3, rotulo="Endereco", placeholder="Rua, numero",
        )
        self.campo_endereco.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.campo_cidade = CampoEntrada(linha3, rotulo="Cidade")
        self.campo_cidade.grid(row=0, column=1, sticky="ew", padx=4)

        self.campo_estado = CampoSelecao(
            linha3, rotulo="Estado", opcoes=ESTADOS,
        )
        self.campo_estado.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        # Linha 4: Curso + Como conheceu + Captador
        linha4 = tk.Frame(c, bg=Cores.CARD_FUNDO)
        linha4.pack(fill="x", pady=12)
        linha4.grid_columnconfigure(0, weight=1, uniform="l4")
        linha4.grid_columnconfigure(1, weight=1, uniform="l4")
        linha4.grid_columnconfigure(2, weight=1, uniform="l4")

        self.campo_curso = CampoSelecao(
            linha4, rotulo="Curso de interesse", opcoes=CURSOS,
            obrigatorio=True,
        )
        self.campo_curso.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.campo_origem = CampoSelecao(
            linha4, rotulo="Como conheceu?", opcoes=ORIGENS,
        )
        self.campo_origem.grid(row=0, column=1, sticky="ew", padx=4)

        self.campo_captador = CampoSelecao(
            linha4, rotulo="Captador (vendedor)", opcoes=CAPTADORES,
            obrigatorio=True,
        )
        self.campo_captador.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        # Linha 5: Observacoes
        self.campo_observacoes = CampoTextoLongo(
            c, rotulo="Observacoes",
            placeholder="Anote informacoes relevantes sobre o lead...",
            altura=3,
        )
        self.campo_observacoes.pack(fill="x", pady=(12, 16))

        # Botoes
        botoes = tk.Frame(c, bg=Cores.CARD_FUNDO)
        botoes.pack(fill="x", anchor="e")

        BotaoSecundario(
            botoes, texto="Cancelar", comando=self._limpar_formulario,
            largura=120,
        ).pack(side="right", padx=(8, 0))

        BotaoPrimario(
            botoes, texto="Salvar Lead", comando=self._salvar_lead,
            largura=140,
        ).pack(side="right")

        return card

    def _limpar_formulario(self):
        for campo in (
            self.campo_nome, self.campo_nascimento, self.campo_cpf,
            self.campo_email, self.campo_telefone, self.campo_endereco,
            self.campo_cidade,
        ):
            campo.limpar()
        self.campo_estado.definir("")
        self.campo_curso.definir("")
        self.campo_origem.definir("")
        self.campo_captador.definir("")
        self.campo_observacoes.definir("")
        self.mostrar_notificacao("Formulario limpo.", "INFO")

    def _salvar_lead(self):
        nome = self.campo_nome.obter()
        email = self.campo_email.obter()
        curso = self.campo_curso.obter()
        captador = self.campo_captador.obter()

        # Validacao basica
        if not nome:
            self.mostrar_notificacao("Informe o nome completo.", "ERRO")
            return
        if not email or "@" not in email:
            self.mostrar_notificacao("E-mail invalido.", "ERRO")
            return
        if not curso:
            self.mostrar_notificacao("Selecione o curso de interesse.", "ERRO")
            return
        if not captador:
            self.mostrar_notificacao("Selecione um captador.", "ERRO")
            return

        lead = Lead(
            nome=nome,
            data_nascimento=self.campo_nascimento.obter(),
            cpf=self.campo_cpf.obter(),
            email=email,
            telefone=self.campo_telefone.obter(),
            endereco=self.campo_endereco.obter(),
            cidade=self.campo_cidade.obter(),
            estado=self.campo_estado.obter(),
            curso_interesse=curso,
            como_conheceu=self.campo_origem.obter(),
            captador=captador,
            observacoes=self.campo_observacoes.obter(),
        )
        self.banco.adicionar_lead(lead)
        self._limpar_formulario()
        self.mostrar_notificacao(
            f"Lead {lead.nome} salvo com sucesso!", "SUCESSO",
            titulo="Lead cadastrado",
        )
        self._atualizar_resumos_dinamicos()

    # ------------------------------------------------------------------
    # COLUNA 2: RESUMO + JORNADA
    # ------------------------------------------------------------------
    def _coluna_resumo(self, parent) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=Cores.FUNDO_PRINCIPAL)

        # Card Resumo do Lead
        card_resumo = CardComCabecalho(wrapper, titulo="Resumo do Lead", icone="📋")
        card_resumo.pack(fill="x")
        c = card_resumo.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)

        self._linha_info_resumo(c, "Status atual:", None, status="LEAD")
        self._linha_info_resumo(c, "Data do cadastro:", "24/05/2024 14:30")
        self._linha_info_resumo(c, "Captador:", "Maria Santos")
        self._linha_info_resumo(c, "Curso de interesse:", "Marketing Digital")

        # Card Jornada
        card_jornada = CardComCabecalho(
            wrapper, titulo="Jornada do Aluno", icone="🛤",
        )
        card_jornada.pack(fill="x", pady=(16, 0))
        cj = card_jornada.conteudo()
        cj.configure(bg=Cores.CARD_FUNDO)

        etapas = [
            ("Cadastro do aluno (lead)", "Lead cadastrado no sistema.", True),
            ("Registro da venda (captador)",
             "Registrar negociacao e definir condicao.", True),
            ("Definicao do status (Pago / Nao pago)",
             "Definir se o aluno ja esta pago.", True),
            ("Registro do pagamento",
             "Registrar pagamento e emitir comprovante.", False),
            ("Liberacao para turma (pos-venda)",
             "Liberar aluno apos pagamento.", False),
            ("Formacao de turma",
             "Adicionar aluno a turma.", False),
            ("Inicio das aulas",
             "Aulas liberadas conforme calendario.", False),
            ("Controle de frequencia",
             "Acompanhar presenca nas aulas.", False),
        ]
        for i, (titulo, descricao, ativo) in enumerate(etapas, start=1):
            self._etapa_jornada(cj, i, titulo, descricao, ativo)

        return wrapper

    def _linha_info_resumo(self, parent, rotulo, valor, status=None):
        linha = tk.Frame(parent, bg=Cores.CARD_FUNDO)
        linha.pack(fill="x", pady=4)

        tk.Label(
            linha, text=rotulo, bg=Cores.CARD_FUNDO,
            fg=Cores.TEXTO_SECUNDARIO, font=Fontes.PEQUENO,
        ).pack(side="left")

        if status:
            Badge(linha, texto=status, status=status,
                  cor_canvas=Cores.CARD_FUNDO).pack(side="left", padx=(8, 0))
        else:
            tk.Label(
                linha, text=valor, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_PRIMARIO, font=Fontes.PEQUENO_NEGRITO,
            ).pack(side="right")

    def _etapa_jornada(self, parent, numero, titulo, descricao, ativo):
        cor_bola = Cores.BOTAO_PRIMARIO if ativo else "#cbd5e1"
        cor_texto_titulo = Cores.BOTAO_PRIMARIO if ativo else Cores.TEXTO_TERCIARIO

        linha = tk.Frame(parent, bg=Cores.CARD_FUNDO)
        linha.pack(fill="x", pady=5)

        # Bolinha numerada
        cnv = tk.Canvas(
            linha, width=28, height=28,
            highlightthickness=0, bd=0, bg=Cores.CARD_FUNDO,
        )
        cnv.pack(side="left", padx=(0, 12), anchor="n")
        cnv.create_oval(2, 2, 26, 26, fill=cor_bola, outline="")
        cnv.create_text(14, 14, text=str(numero), fill=Cores.BRANCO,
                        font=Fontes.PEQUENO_NEGRITO)

        # Texto
        textos = tk.Frame(linha, bg=Cores.CARD_FUNDO)
        textos.pack(side="left", fill="x", expand=True)
        tk.Label(
            textos, text=titulo, bg=Cores.CARD_FUNDO,
            fg=cor_texto_titulo,
            font=Fontes.PEQUENO_NEGRITO, anchor="w", justify="left",
        ).pack(anchor="w")
        tk.Label(
            textos, text=descricao, bg=Cores.CARD_FUNDO,
            fg=Cores.TEXTO_TERCIARIO, font=Fontes.MICRO, anchor="w",
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # COLUNA 3: ANALYTICS
    # ------------------------------------------------------------------
    def _coluna_analytics(self, parent) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=Cores.FUNDO_PRINCIPAL)

        card_funil = CardComCabecalho(
            wrapper, titulo="Funil de Origem", icone="▼",
            acao_texto="Este mes  ▾",
        )
        card_funil.pack(fill="x")

        dados_funil = list(self.banco.funil_origem().items())
        self.grafico_funil = GraficoFunil(
            card_funil.conteudo(), dados=dados_funil,
            largura=380, altura=340,
        )
        self.grafico_funil.pack()

        card_origem = CardComCabecalho(
            wrapper, titulo="Origem dos Leads", icone="🎯",
            acao_texto="Ver relatorio →",
            acao_comando=lambda: self.navegar_para("relatorios"),
        )
        card_origem.pack(fill="x", pady=(16, 0))

        self.grafico_pizza = GraficoPizza(
            card_origem.conteudo(),
            dados=self.banco.origem_dos_leads(),
            largura=380, altura=240,
        )
        self.grafico_pizza.pack()

        return wrapper

    # ------------------------------------------------------------------
    # RODAPE: Leads recentes + Resumo geral
    # ------------------------------------------------------------------
    def _card_leads_recentes(self, parent):
        card = CardComCabecalho(
            parent, titulo="Leads Recentes", icone="🆕",
            acao_texto="Ver todos os leads →",
            acao_comando=lambda: self.navegar_para("leads"),
        )
        c = card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)

        cabecalho = tk.Frame(c, bg=Cores.CARD_FUNDO)
        cabecalho.pack(fill="x", pady=(0, 6))
        for col, peso in (
            ("Nome", 3), ("Curso", 3), ("Captador", 2),
            ("Status", 2), ("Data", 2),
        ):
            cabecalho.grid_columnconfigure(("Nome Curso Captador Status Data".split()
                                            ).index(col), weight=peso)
        for i, col in enumerate("Nome Curso Captador Status Data".split()):
            tk.Label(
                cabecalho, text=col, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_TERCIARIO, font=Fontes.MICRO_NEGRITO,
                anchor="w",
            ).grid(row=0, column=i, sticky="w", padx=4)

        tk.Frame(c, bg=Cores.CARD_BORDA, height=1).pack(fill="x", pady=(0, 4))

        self.frame_leads = tk.Frame(c, bg=Cores.CARD_FUNDO)
        self.frame_leads.pack(fill="x")
        self._popular_leads_recentes()

        return card

    def _popular_leads_recentes(self):
        for w in self.frame_leads.winfo_children():
            w.destroy()
        leads = self.banco.leads[:4]
        for i, lead in enumerate(leads):
            linha = tk.Frame(self.frame_leads, bg=Cores.CARD_FUNDO)
            linha.pack(fill="x", pady=6)
            for j, peso in enumerate((3, 3, 2, 2, 2)):
                linha.grid_columnconfigure(j, weight=peso)

            tk.Label(
                linha, text=lead.nome, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_PRIMARIO, font=Fontes.PEQUENO_NEGRITO,
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=4)
            tk.Label(
                linha, text=lead.curso_interesse, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_SECUNDARIO, font=Fontes.PEQUENO, anchor="w",
            ).grid(row=0, column=1, sticky="w", padx=4)
            tk.Label(
                linha, text=lead.captador, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_SECUNDARIO, font=Fontes.PEQUENO, anchor="w",
            ).grid(row=0, column=2, sticky="w", padx=4)

            wrap_status = tk.Frame(linha, bg=Cores.CARD_FUNDO)
            wrap_status.grid(row=0, column=3, sticky="w", padx=4)
            Badge(wrap_status, texto=lead.status.replace("_", " "),
                  status=lead.status,
                  cor_canvas=Cores.CARD_FUNDO).pack(anchor="w")

            tk.Label(
                linha, text=lead.data_cadastro, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_SECUNDARIO, font=Fontes.PEQUENO, anchor="w",
            ).grid(row=0, column=4, sticky="w", padx=4)

    def _card_resumo_geral(self, parent):
        card = CardComCabecalho(parent, titulo="Resumo Geral", icone="📈")
        c = card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)

        c.grid_columnconfigure(0, weight=1, uniform="rg")
        c.grid_columnconfigure(1, weight=1, uniform="rg")

        stats = self.banco.estatisticas_dashboard()

        self.lbl_leads = self._mini_card_estatistica(
            c, "👥", "Leads (este mes)", str(stats["leads"]),
        )
        self.lbl_leads_widget = self.lbl_leads
        self.lbl_leads.master.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.lbl_vendas = self._mini_card_estatistica(
            c, "🛒", "Vendas (este mes)", str(stats["vendas"]),
        )
        self.lbl_vendas.master.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        valor = f"R$ {stats['faturamento']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.lbl_faturamento = self._mini_card_estatistica(
            c, "💰", "Faturamento (este mes)", valor,
        )
        self.lbl_faturamento.master.grid(
            row=1, column=0, sticky="nsew", padx=4, pady=4,
        )

        self.lbl_conversao = self._mini_card_estatistica(
            c, "📊", "Conversao (este mes)", f"{stats['conversao']}%",
        )
        self.lbl_conversao.master.grid(
            row=1, column=1, sticky="nsew", padx=4, pady=4,
        )

        return card

    def _mini_card_estatistica(self, parent, icone, rotulo, valor):
        wrapper = tk.Frame(
            parent, bg=Cores.FUNDO_PRINCIPAL,
            highlightthickness=1, highlightbackground=Cores.CARD_BORDA,
        )

        moldura = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        moldura.pack(fill="both", expand=True, padx=14, pady=14)

        topo = tk.Frame(moldura, bg=Cores.FUNDO_PRINCIPAL)
        topo.pack(fill="x")
        tk.Label(
            topo, text=icone, bg=Cores.FUNDO_PRINCIPAL,
            fg=Cores.BOTAO_PRIMARIO, font=(Fontes.FAMILIA, 14),
        ).pack(side="left")
        tk.Label(
            topo, text=rotulo, bg=Cores.FUNDO_PRINCIPAL,
            fg=Cores.TEXTO_TERCIARIO, font=Fontes.MICRO,
        ).pack(side="left", padx=(6, 0))

        valor_label = tk.Label(
            moldura, text=valor, bg=Cores.FUNDO_PRINCIPAL,
            fg=Cores.TEXTO_PRIMARIO, font=Fontes.NUMERO_MEDIO,
        )
        valor_label.pack(anchor="w", pady=(8, 0))
        return valor_label

    # ------------------------------------------------------------------
    def _atualizar_resumos_dinamicos(self):
        stats = self.banco.estatisticas_dashboard()
        self.lbl_leads.configure(text=str(stats["leads"]))
        self.lbl_vendas.configure(text=str(stats["vendas"]))
        valor = (f"R$ {stats['faturamento']:,.2f}"
                 .replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_faturamento.configure(text=valor)
        self.lbl_conversao.configure(text=f"{stats['conversao']}%")
        # Atualiza graficos
        self.grafico_funil.atualizar(list(self.banco.funil_origem().items()))
        self.grafico_pizza.atualizar(self.banco.origem_dos_leads())
        # Atualiza tabela
        self._popular_leads_recentes()
