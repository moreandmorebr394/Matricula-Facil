"""Tela de Leads / Alunos.

Lista todos os leads cadastrados, permite buscar, filtrar por status,
editar, excluir e visualizar detalhes em modal.
"""
import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Callable

from componentes.badge import Badge
from componentes.botao import BotaoPrimario, BotaoSecundario, BotaoPerigo
from componentes.campo_entrada import CampoEntrada, CampoSelecao
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from dados.modelos import Lead


STATUS_OPCOES = ["Todos", "LEAD", "NEGOCIACAO", "PAGO", "NAO_PAGO", "ALUNO_ATIVO"]


class TelaLeads(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self.navegar_para = navegar_para
        self.filtro_status = "Todos"
        self.filtro_busca = ""
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)

        # Filtros
        filtros = Card(wrapper, padding=14)
        filtros.pack(fill="x", pady=(0, 14))
        c = filtros.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)

        c.grid_columnconfigure(0, weight=2)
        c.grid_columnconfigure(1, weight=1)
        c.grid_columnconfigure(2, weight=0)

        self.campo_busca = CampoEntrada(
            c, rotulo="Buscar", placeholder="Nome, e-mail ou telefone...",
        )
        self.campo_busca.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self.campo_filtro = CampoSelecao(
            c, rotulo="Status", opcoes=STATUS_OPCOES, valor_inicial="Todos",
        )
        self.campo_filtro.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        wrap_botao = tk.Frame(c, bg=Cores.CARD_FUNDO)
        wrap_botao.grid(row=0, column=2, sticky="se", pady=(20, 0))
        BotaoPrimario(
            wrap_botao, texto="Aplicar filtros",
            comando=self._aplicar_filtros, largura=140,
        ).pack(side="left")

        BotaoSecundario(
            wrap_botao, texto="Novo Lead",
            comando=lambda: self.navegar_para("dashboard"),
            largura=110,
        ).pack(side="left", padx=(8, 0))

        # Tabela
        tabela_card = CardComCabecalho(
            wrapper, titulo="Lista de Leads",
            acao_texto="Exportar CSV",
            acao_comando=self._exportar_csv,
        )
        tabela_card.pack(fill="both", expand=True)

        self.area_tabela = tabela_card.conteudo()
        self.area_tabela.configure(bg=Cores.CARD_FUNDO)
        self._renderizar_tabela()

    def _aplicar_filtros(self):
        self.filtro_busca = self.campo_busca.obter().lower()
        self.filtro_status = self.campo_filtro.obter() or "Todos"
        self._renderizar_tabela()
        self.mostrar_notificacao("Filtros aplicados.", "INFO")

    def _renderizar_tabela(self):
        for w in self.area_tabela.winfo_children():
            w.destroy()

        # Cabecalho
        cabecalho = tk.Frame(self.area_tabela, bg=Cores.CARD_FUNDO)
        cabecalho.pack(fill="x", pady=(0, 6))
        colunas = ["#", "Nome", "Email", "Telefone", "Curso", "Captador",
                   "Status", "Data", "Acoes"]
        pesos = [1, 3, 3, 2, 2, 2, 2, 2, 2]
        for i, peso in enumerate(pesos):
            cabecalho.grid_columnconfigure(i, weight=peso)
        for i, col in enumerate(colunas):
            tk.Label(
                cabecalho, text=col, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_TERCIARIO, font=Fontes.MICRO_NEGRITO,
                anchor="w",
            ).grid(row=0, column=i, sticky="w", padx=4)

        tk.Frame(self.area_tabela, bg=Cores.CARD_BORDA, height=1).pack(
            fill="x", pady=(0, 4)
        )

        # Lista filtrada
        leads = self._leads_filtrados()
        if not leads:
            tk.Label(
                self.area_tabela, text="Nenhum lead encontrado.",
                bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                font=Fontes.CORPO,
            ).pack(pady=30)
            return

        # Frame com scroll
        canvas = tk.Canvas(
            self.area_tabela, bg=Cores.CARD_FUNDO,
            highlightthickness=0, bd=0, height=420,
        )
        canvas.pack(side="left", fill="both", expand=True)
        scroll = tk.Scrollbar(self.area_tabela, orient="vertical",
                              command=canvas.yview)
        scroll.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scroll.set)

        interno = tk.Frame(canvas, bg=Cores.CARD_FUNDO)
        canvas.create_window((0, 0), window=interno, anchor="nw")
        interno.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        for idx, lead in enumerate(leads):
            cor_fundo = Cores.CARD_FUNDO if idx % 2 == 0 else "#f8fafc"
            linha = tk.Frame(interno, bg=cor_fundo)
            linha.pack(fill="x")
            for i, peso in enumerate(pesos):
                linha.grid_columnconfigure(i, weight=peso)

            self._celula(linha, str(lead.id), 0, cor_fundo, Fontes.PEQUENO_NEGRITO)
            self._celula(linha, lead.nome, 1, cor_fundo, Fontes.PEQUENO_NEGRITO)
            self._celula(linha, lead.email, 2, cor_fundo)
            self._celula(linha, lead.telefone, 3, cor_fundo)
            self._celula(linha, lead.curso_interesse, 4, cor_fundo)
            self._celula(linha, lead.captador, 5, cor_fundo)

            wrap_status = tk.Frame(linha, bg=cor_fundo)
            wrap_status.grid(row=0, column=6, sticky="w", padx=4, pady=8)
            Badge(wrap_status, texto=lead.status.replace("_", " "),
                  status=lead.status, cor_canvas=cor_fundo).pack(anchor="w")

            self._celula(linha, lead.data_cadastro, 7, cor_fundo)

            wrap_acoes = tk.Frame(linha, bg=cor_fundo)
            wrap_acoes.grid(row=0, column=8, sticky="w", padx=4, pady=4)
            self._link(wrap_acoes, "Ver", lambda l=lead: self._ver_detalhes(l))
            self._link(wrap_acoes, "Editar",
                       lambda l=lead: self._editar_status(l))
            self._link(wrap_acoes, "Excluir",
                       lambda l=lead: self._excluir(l), cor=Cores.BOTAO_PERIGO)

    def _celula(self, parent, texto, coluna, cor_fundo, fonte=None):
        tk.Label(
            parent, text=texto, bg=cor_fundo,
            fg=Cores.TEXTO_PRIMARIO if fonte else Cores.TEXTO_SECUNDARIO,
            font=fonte or Fontes.PEQUENO, anchor="w",
        ).grid(row=0, column=coluna, sticky="w", padx=4, pady=8)

    def _link(self, parent, texto, comando, cor=None):
        cor = cor or Cores.BOTAO_PRIMARIO
        l = tk.Label(
            parent, text=texto, bg=parent.cget("bg"),
            fg=cor, font=Fontes.PEQUENO_NEGRITO, cursor="hand2",
        )
        l.pack(side="left", padx=(0, 10))
        l.bind("<Button-1>", lambda _e: comando())
        return l

    def _leads_filtrados(self):
        leads = list(self.banco.leads)
        if self.filtro_status != "Todos":
            leads = [l for l in leads if l.status == self.filtro_status]
        if self.filtro_busca:
            q = self.filtro_busca
            leads = [l for l in leads
                     if q in l.nome.lower()
                     or q in l.email.lower()
                     or q in l.telefone.lower()]
        return leads

    # ------------------------------------------------------------------
    # Modais
    # ------------------------------------------------------------------
    def _ver_detalhes(self, lead: Lead):
        janela = tk.Toplevel(self)
        janela.title(f"Lead - {lead.nome}")
        janela.configure(bg=Cores.CARD_FUNDO)
        janela.geometry("520x540")
        janela.transient(self)
        janela.grab_set()

        cabecalho = tk.Frame(janela, bg=Cores.BOTAO_PRIMARIO, height=80)
        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)
        tk.Label(
            cabecalho, text="Detalhes do Lead",
            bg=Cores.BOTAO_PRIMARIO, fg=Cores.BRANCO,
            font=Fontes.TITULO,
        ).pack(side="left", padx=20, pady=20)

        c = tk.Frame(janela, bg=Cores.CARD_FUNDO)
        c.pack(fill="both", expand=True, padx=24, pady=20)

        campos = [
            ("ID", str(lead.id)),
            ("Nome completo", lead.nome),
            ("E-mail", lead.email),
            ("Telefone", lead.telefone),
            ("CPF", lead.cpf),
            ("Data de nascimento", lead.data_nascimento),
            ("Endereco", f"{lead.endereco}, {lead.cidade} - {lead.estado}"),
            ("Curso de interesse", lead.curso_interesse),
            ("Como conheceu", lead.como_conheceu),
            ("Captador", lead.captador),
            ("Data do cadastro", lead.data_cadastro),
            ("Observacoes", lead.observacoes or "-"),
        ]
        for rotulo, valor in campos:
            linha = tk.Frame(c, bg=Cores.CARD_FUNDO)
            linha.pack(fill="x", pady=3)
            tk.Label(
                linha, text=rotulo, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_TERCIARIO, font=Fontes.MICRO,
                width=20, anchor="w",
            ).pack(side="left")
            tk.Label(
                linha, text=valor, bg=Cores.CARD_FUNDO,
                fg=Cores.TEXTO_PRIMARIO, font=Fontes.PEQUENO_NEGRITO,
                anchor="w", justify="left", wraplength=300,
            ).pack(side="left")

        # Status com badge
        linha_status = tk.Frame(c, bg=Cores.CARD_FUNDO)
        linha_status.pack(fill="x", pady=8)
        tk.Label(
            linha_status, text="Status", bg=Cores.CARD_FUNDO,
            fg=Cores.TEXTO_TERCIARIO, font=Fontes.MICRO,
            width=20, anchor="w",
        ).pack(side="left")
        Badge(linha_status, texto=lead.status.replace("_", " "),
              status=lead.status,
              cor_canvas=Cores.CARD_FUNDO).pack(side="left")

        BotaoSecundario(
            janela, texto="Fechar", comando=janela.destroy, largura=100,
        ).pack(pady=(0, 16))

    def _editar_status(self, lead: Lead):
        janela = tk.Toplevel(self)
        janela.title("Editar Status")
        janela.configure(bg=Cores.CARD_FUNDO)
        janela.geometry("420x260")
        janela.transient(self)
        janela.grab_set()

        tk.Label(
            janela, text=f"Editar status: {lead.nome}",
            bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_PRIMARIO,
            font=Fontes.TITULO_CARD,
        ).pack(pady=(20, 16))

        campo = CampoSelecao(
            janela, rotulo="Novo status",
            opcoes=["LEAD", "NEGOCIACAO", "PAGO", "NAO_PAGO", "ALUNO_ATIVO"],
            valor_inicial=lead.status,
        )
        campo.pack(fill="x", padx=24)

        botoes = tk.Frame(janela, bg=Cores.CARD_FUNDO)
        botoes.pack(pady=24)

        def salvar():
            novo = campo.obter()
            if novo:
                lead.status = novo
                self.banco.atualizar_lead(lead)
                self.mostrar_notificacao(
                    f"Status de {lead.nome} atualizado.", "SUCESSO",
                )
                self._renderizar_tabela()
                janela.destroy()

        BotaoSecundario(botoes, texto="Cancelar",
                        comando=janela.destroy, largura=110).pack(side="left", padx=4)
        BotaoPrimario(botoes, texto="Salvar",
                      comando=salvar, largura=110).pack(side="left", padx=4)

    def _excluir(self, lead: Lead):
        if messagebox.askyesno("Excluir lead",
                                f"Confirmar exclusao de {lead.nome}?"):
            self.banco.remover_lead(lead.id)
            self.mostrar_notificacao(f"Lead {lead.nome} excluido.", "INFO")
            self._renderizar_tabela()

    def _exportar_csv(self):
        import os
        from config.configuracoes import Configuracoes
        os.makedirs(Configuracoes.PASTA_DADOS, exist_ok=True)
        caminho = os.path.join(Configuracoes.PASTA_DADOS, "leads_exportados.csv")
        with open(caminho, "w", encoding="utf-8") as fp:
            fp.write("id;nome;email;telefone;curso;captador;status;data\n")
            for l in self.banco.leads:
                fp.write(f"{l.id};{l.nome};{l.email};{l.telefone};"
                         f"{l.curso_interesse};{l.captador};{l.status};"
                         f"{l.data_cadastro}\n")
        self.mostrar_notificacao(
            f"Exportado em: {caminho}", "SUCESSO", titulo="CSV gerado",
        )
