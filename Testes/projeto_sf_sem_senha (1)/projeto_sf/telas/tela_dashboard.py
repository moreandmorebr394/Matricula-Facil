"""
Tela do Dashboard (Janela principal do Administrador).

Layout:
    - Sidebar fixa à esquerda (azul escuro) com 11 itens de navegação
    - Header em cima (título, sino de notificações, perfil)
    - Área central que troca de painel conforme o item selecionado
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from componentes import tema
from componentes.logo_sf import LogoSF
from componentes.notificacoes import (
    NotificacaoFlutuante,
    RastroCursor,
    fade_in_janela,
)
from controladores.controlador_aluno import ControladorLead
from controladores.controlador_academico import (
    ControladorVenda,
    ControladorPagamento,
)
from modelos.modelo_academico import ModeloConfiguracoes


# Itens da sidebar: (chave, rótulo, ícone unicode, badge_texto_opcional)
ITENS_SIDEBAR = (
    ("dashboard", "Dashboard", "\u2302", None),
    ("alunos", "Leads / Alunos", "\u2632", None),
    ("vendas", "Vendas", "\u26C2", None),
    ("pagamentos", "Pagamentos", "\u2756", None),
    ("turmas", "Turmas", "\u2630", None),
    ("aulas", "Aulas", "\u2710", None),
    ("frequencia", "Frequência", "\u2713", None),
    ("funil", "Funil de Origem", "\u2207", "novo"),
    ("relatorios", "Relatórios", "\u2261", None),
    ("configuracoes", "Configurações", "\u2699", None),
)


class TelaDashboard:
    """Janela principal do administrador."""

    def __init__(self, sessao=None):
        self.sessao = sessao
        self.administrador = (
            sessao.usuario if sessao and sessao.autenticado else {}
        )

        self.raiz = tk.Tk()
        self.raiz.title("Sistema Fácil - Painel Administrativo")
        self.raiz.configure(bg=tema.OFFWHITE)
        self.raiz.geometry("1366x780")
        self.raiz.minsize(1180, 700)

        self._item_ativo = "alunos"
        self._botoes_sidebar = {}
        self._painel_atual = None
        self._foto_admin_path = ModeloConfiguracoes.obter("foto_admin", "")
        self._foto_admin_imagem = None  # PhotoImage referência

        self._construir()

        # Centraliza
        self.raiz.update_idletasks()
        l = self.raiz.winfo_screenwidth()
        a = self.raiz.winfo_screenheight()
        lar = min(1366, l - 60)
        alt = min(780, a - 80)
        x = (l - lar) // 2
        y = (a - alt) // 2
        self.raiz.geometry(f"{lar}x{alt}+{x}+{y}")

        fade_in_janela(self.raiz, duracao_ms=260)

        # Rastro do cursor
        try:
            self._rastro = RastroCursor(
                self.raiz, cor=tema.AMARELO_DOURADO, quantidade=8,
            )
            self._rastro.iniciar()
        except Exception:
            self._rastro = None

        # Inicia no painel de alunos (lead) - mais relevante
        self._selecionar_item("alunos")

        self.raiz.protocol("WM_DELETE_WINDOW", self._sair)
        self.raiz.mainloop()

    # =================================================================
    def _construir(self):
        # Estrutura: sidebar à esquerda, restante à direita
        self.raiz.columnconfigure(0, weight=0)
        self.raiz.columnconfigure(1, weight=1)
        self.raiz.rowconfigure(0, weight=1)

        self._sidebar = tk.Frame(self.raiz, bg=tema.SIDEBAR_FUNDO, width=240)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        self._area_direita = tk.Frame(self.raiz, bg=tema.OFFWHITE)
        self._area_direita.grid(row=0, column=1, sticky="nsew")
        self._area_direita.rowconfigure(1, weight=1)
        self._area_direita.columnconfigure(0, weight=1)

        self._header = tk.Frame(
            self._area_direita, bg=tema.BRANCO_PURO, height=72,
        )
        self._header.grid(row=0, column=0, sticky="ew")
        self._header.grid_propagate(False)

        self._area_central = tk.Frame(self._area_direita, bg=tema.OFFWHITE)
        self._area_central.grid(row=1, column=0, sticky="nsew")
        self._area_central.rowconfigure(0, weight=1)
        self._area_central.columnconfigure(0, weight=1)

        self._construir_sidebar()
        self._construir_header()

    # =================================================================
    def _construir_sidebar(self):
        # logotipo no topo
        topo = tk.Frame(self._sidebar, bg=tema.SIDEBAR_FUNDO, height=80)
        topo.pack(fill="x", pady=(16, 4))
        topo.pack_propagate(False)

        # mini logo + texto
        logo = LogoSF(topo, tamanho=44, cor_fundo=tema.SIDEBAR_FUNDO)
        logo.pack(side="left", padx=(20, 10))

        bloco_texto = tk.Frame(topo, bg=tema.SIDEBAR_FUNDO)
        bloco_texto.pack(side="left", anchor="w")
        tk.Label(
            bloco_texto,
            text="Sistema Fácil",
            bg=tema.SIDEBAR_FUNDO,
            fg=tema.SIDEBAR_TEXTO,
            font=tema.fonte_destaque(12),
        ).pack(anchor="w")
        tk.Label(
            bloco_texto,
            text="Educação",
            bg=tema.SIDEBAR_FUNDO,
            fg=tema.SIDEBAR_TEXTO_INATIVO,
            font=tema.fonte_corpo(9),
        ).pack(anchor="w")

        # separador
        tk.Frame(self._sidebar, bg=tema.SIDEBAR_FUNDO_HOVER, height=1).pack(
            fill="x", padx=20, pady=(12, 8),
        )

        # itens
        for chave, rotulo, icone, badge in ITENS_SIDEBAR:
            self._criar_item_sidebar(chave, rotulo, icone, badge)

        # Espaçador + botão sair no rodapé
        tk.Frame(self._sidebar, bg=tema.SIDEBAR_FUNDO).pack(
            fill="both", expand=True,
        )

        tk.Frame(self._sidebar, bg=tema.SIDEBAR_FUNDO_HOVER, height=1).pack(
            fill="x", padx=20, pady=(8, 8),
        )

        sair = tk.Frame(self._sidebar, bg=tema.SIDEBAR_FUNDO, height=44)
        sair.pack(fill="x", pady=(0, 16))
        sair.pack_propagate(False)

        lbl_icone = tk.Label(
            sair, text="\u21B6", bg=tema.SIDEBAR_FUNDO,
            fg=tema.VERMELHO_ERRO, font=tema.fonte_destaque(14),
        )
        lbl_icone.pack(side="left", padx=(20, 8))
        lbl_texto = tk.Label(
            sair, text="Sair", bg=tema.SIDEBAR_FUNDO,
            fg=tema.SIDEBAR_TEXTO, font=tema.fonte_corpo(11),
        )
        lbl_texto.pack(side="left")

        for w in (sair, lbl_icone, lbl_texto):
            w.configure(cursor="hand2")
            w.bind("<Button-1>", lambda _e: self._sair())
            w.bind(
                "<Enter>",
                lambda _e, s=sair, i=lbl_icone, t=lbl_texto: (
                    s.configure(bg=tema.SIDEBAR_FUNDO_HOVER),
                    i.configure(bg=tema.SIDEBAR_FUNDO_HOVER),
                    t.configure(bg=tema.SIDEBAR_FUNDO_HOVER),
                ),
            )
            w.bind(
                "<Leave>",
                lambda _e, s=sair, i=lbl_icone, t=lbl_texto: (
                    s.configure(bg=tema.SIDEBAR_FUNDO),
                    i.configure(bg=tema.SIDEBAR_FUNDO),
                    t.configure(bg=tema.SIDEBAR_FUNDO),
                ),
            )

    def _criar_item_sidebar(self, chave, rotulo, icone, badge):
        item = tk.Frame(self._sidebar, bg=tema.SIDEBAR_FUNDO, height=44)
        item.pack(fill="x", padx=10, pady=2)
        item.pack_propagate(False)

        lbl_icone = tk.Label(
            item, text=icone, bg=tema.SIDEBAR_FUNDO,
            fg=tema.SIDEBAR_TEXTO_INATIVO, font=tema.fonte_destaque(13),
            width=2,
        )
        lbl_icone.pack(side="left", padx=(12, 6))

        lbl_rotulo = tk.Label(
            item, text=rotulo, bg=tema.SIDEBAR_FUNDO,
            fg=tema.SIDEBAR_TEXTO_INATIVO, font=tema.fonte_corpo(11),
        )
        lbl_rotulo.pack(side="left")

        if badge:
            lbl_badge = tk.Label(
                item, text=badge.upper(),
                bg=tema.AMARELO_DOURADO, fg=tema.AZUL_ESCURO,
                font=tema.fonte_destaque(8), padx=6, pady=1,
            )
            lbl_badge.pack(side="right", padx=(0, 14))

        widgets = (item, lbl_icone, lbl_rotulo)
        self._botoes_sidebar[chave] = {
            "container": item, "icone": lbl_icone, "rotulo": lbl_rotulo,
        }

        for w in widgets:
            w.configure(cursor="hand2")
            w.bind("<Button-1>", lambda _e, c=chave: self._selecionar_item(c))
            w.bind(
                "<Enter>",
                lambda _e, c=chave: self._hover_sidebar(c, True),
            )
            w.bind(
                "<Leave>",
                lambda _e, c=chave: self._hover_sidebar(c, False),
            )

    def _hover_sidebar(self, chave, entrar):
        if chave == self._item_ativo:
            return
        info = self._botoes_sidebar.get(chave)
        if not info:
            return
        cor = tema.SIDEBAR_FUNDO_HOVER if entrar else tema.SIDEBAR_FUNDO
        for w in (info["container"], info["icone"], info["rotulo"]):
            try:
                w.configure(bg=cor)
            except tk.TclError:
                pass

    def _selecionar_item(self, chave):
        # Atualiza estilo do botão
        for c, info in self._botoes_sidebar.items():
            ativo = c == chave
            cor_fundo = tema.SIDEBAR_ATIVO if ativo else tema.SIDEBAR_FUNDO
            cor_texto = tema.SIDEBAR_TEXTO if ativo else tema.SIDEBAR_TEXTO_INATIVO
            cor_icone = tema.AMARELO_DOURADO if ativo else tema.SIDEBAR_TEXTO_INATIVO
            try:
                info["container"].configure(bg=cor_fundo)
                info["icone"].configure(bg=cor_fundo, fg=cor_icone)
                info["rotulo"].configure(bg=cor_fundo, fg=cor_texto)
            except tk.TclError:
                pass

        self._item_ativo = chave
        self._renderizar_painel(chave)

    # =================================================================
    def _construir_header(self):
        # Título/breadcrumb
        bloco_titulo = tk.Frame(self._header, bg=tema.BRANCO_PURO)
        bloco_titulo.pack(side="left", padx=24, pady=10)

        self._titulo_lbl = tk.Label(
            bloco_titulo,
            text="Cadastro do Aluno (Lead)",
            bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO,
            font=tema.fonte_titulo(18),
        )
        self._titulo_lbl.pack(anchor="w")

        self._breadcrumb_lbl = tk.Label(
            bloco_titulo,
            text="Leads / Novo Cadastro",
            bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(10),
        )
        self._breadcrumb_lbl.pack(anchor="w")

        # Direita: notificações + perfil
        direita = tk.Frame(self._header, bg=tema.BRANCO_PURO)
        direita.pack(side="right", padx=24, pady=10)

        # Sino de notificações
        sino = tk.Label(
            direita, text="\u2407", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(20),
            cursor="hand2",
        )
        sino.pack(side="left", padx=(0, 8))
        sino.bind("<Button-1>", lambda _e: self._abrir_notificacoes())

        # badge vermelho
        tk.Label(
            direita, text="3", bg=tema.VERMELHO_ERRO, fg="#FFFFFF",
            font=tema.fonte_destaque(8), padx=4,
        ).pack(side="left", padx=(0, 16))

        # bloco perfil
        bloco_perfil = tk.Frame(direita, bg=tema.BRANCO_PURO, cursor="hand2")
        bloco_perfil.pack(side="left")

        self._avatar_lbl = tk.Label(
            bloco_perfil, text="\U0001F464", bg=tema.AZUL_PRINCIPAL,
            fg="#FFFFFF", font=tema.fonte_destaque(16), width=2,
        )
        self._avatar_lbl.pack(side="left", padx=(0, 8))
        self._atualizar_avatar()

        bloco_nome = tk.Frame(bloco_perfil, bg=tema.BRANCO_PURO)
        bloco_nome.pack(side="left")
        tk.Label(
            bloco_nome,
            text=self.administrador.get("nome_completo", "Administrador"),
            bg=tema.BRANCO_PURO, fg=tema.AZUL_ESCURO,
            font=tema.fonte_destaque(11),
        ).pack(anchor="w")
        tk.Label(
            bloco_nome,
            text=self.administrador.get("email_pessoal", "admin@sistemafacil.pa.br"),
            bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(9),
        ).pack(anchor="w")

        for w in (bloco_perfil, self._avatar_lbl, bloco_nome):
            w.bind("<Button-1>", lambda _e: self._selecionar_item("configuracoes"))

    def _atualizar_avatar(self):
        """Tenta carregar a foto do administrador como avatar circular."""
        if not self._foto_admin_path or not os.path.exists(self._foto_admin_path):
            return
        try:
            from PIL import Image, ImageDraw, ImageTk
            img = Image.open(self._foto_admin_path).convert("RGBA")
            img = img.resize((48, 48))
            mascara = Image.new("L", (48, 48), 0)
            ImageDraw.Draw(mascara).ellipse((0, 0, 48, 48), fill=255)
            img.putalpha(mascara)
            self._foto_admin_imagem = ImageTk.PhotoImage(img)
            self._avatar_lbl.configure(
                image=self._foto_admin_imagem, text="", width=48, bg=tema.BRANCO_PURO,
            )
        except Exception:
            pass

    # =================================================================
    def _renderizar_painel(self, chave):
        # Limpa área central
        for w in self._area_central.winfo_children():
            w.destroy()
        self._painel_atual = None

        titulos = {
            "dashboard": ("Dashboard Geral", "Visão geral do sistema"),
            "alunos": ("Cadastro do Aluno (Lead)", "Leads / Novo Cadastro"),
            "vendas": ("Vendas", "Gestão de vendas e contratos"),
            "pagamentos": ("Pagamentos", "Controle financeiro"),
            "turmas": ("Turmas", "Formação e gerenciamento de turmas"),
            "aulas": ("Aulas", "Cronograma e conteúdo"),
            "frequencia": ("Frequência", "Controle de presença"),
            "funil": ("Funil de Origem", "Conversão por etapa"),
            "relatorios": ("Relatórios", "Indicadores e métricas"),
            "configuracoes": ("Configurações", "Perfil e preferências"),
        }
        titulo, breadcrumb = titulos.get(chave, ("Sistema Fácil", ""))
        self._titulo_lbl.configure(text=titulo)
        self._breadcrumb_lbl.configure(text=breadcrumb)

        # Importação preguiçosa para evitar circular import
        if chave == "dashboard" or chave == "alunos":
            from telas.paineis_dashboard.painel_alunos import PainelAlunos
            self._painel_atual = PainelAlunos(self._area_central, dashboard=self)
        elif chave == "vendas":
            from telas.paineis_dashboard.painel_vendas import PainelVendas
            self._painel_atual = PainelVendas(self._area_central, dashboard=self)
        elif chave == "pagamentos":
            from telas.paineis_dashboard.painel_pagamentos import PainelPagamentos
            self._painel_atual = PainelPagamentos(self._area_central, dashboard=self)
        elif chave == "turmas":
            from telas.paineis_dashboard.painel_turmas import PainelTurmas
            self._painel_atual = PainelTurmas(self._area_central, dashboard=self)
        elif chave == "aulas":
            from telas.paineis_dashboard.painel_aulas import PainelAulas
            self._painel_atual = PainelAulas(self._area_central, dashboard=self)
        elif chave == "frequencia":
            from telas.paineis_dashboard.painel_frequencia import PainelFrequencia
            self._painel_atual = PainelFrequencia(self._area_central, dashboard=self)
        elif chave == "funil":
            from telas.paineis_dashboard.painel_funil import PainelFunil
            self._painel_atual = PainelFunil(self._area_central, dashboard=self)
        elif chave == "relatorios":
            from telas.paineis_dashboard.painel_relatorios import PainelRelatorios
            self._painel_atual = PainelRelatorios(self._area_central, dashboard=self)
        elif chave == "configuracoes":
            from telas.paineis_dashboard.painel_configuracoes import (
                PainelConfiguracoes,
            )
            self._painel_atual = PainelConfiguracoes(self._area_central, dashboard=self)

    # =================================================================
    def _abrir_notificacoes(self):
        msgs = (
            "\u2022 3 novos leads cadastrados nas últimas 24h\n"
            "\u2022 2 pagamentos pendentes esta semana\n"
            "\u2022 Turma de Enfermagem com 90% de ocupação"
        )
        messagebox.showinfo("Notificações recentes", msgs, parent=self.raiz)

    # =================================================================
    def selecionar_painel(self, chave):
        """Permite que outros painéis solicitem troca."""
        self._selecionar_item(chave)

    def selecionar_foto_admin(self):
        """Abre seletor de imagem para foto do administrador."""
        caminho = filedialog.askopenfilename(
            parent=self.raiz,
            title="Escolher foto do administrador",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if not caminho:
            return None
        ModeloConfiguracoes.salvar("foto_admin", caminho)
        self._foto_admin_path = caminho
        self._atualizar_avatar()
        NotificacaoFlutuante.exibir(
            self.raiz, "Foto do administrador atualizada!", tipo="sucesso",
        )
        return caminho

    # =================================================================
    def _sair(self):
        if not messagebox.askyesno(
            "Encerrar sessão", "Deseja realmente sair do painel?",
            parent=self.raiz,
        ):
            return
        try:
            if self._rastro is not None:
                self._rastro.parar()
        except Exception:
            pass
        if self.sessao:
            self.sessao.encerrar()
        try:
            self.raiz.destroy()
        except Exception:
            pass
        # Reabre tela de login
        from telas.tela_login import TelaLogin
        from utilitarios.sessao import GerenciadorSessao
        TelaLogin(sessao=GerenciadorSessao()).executar()
