"""
Dashboard Administrativo - Shell principal.

Contem sidebar com navegacao, header com perfil/notificacoes
e area central que troca de conteudo conforme a secao selecionada.

Cada pagina interna esta em um arquivo separado dentro de
paginas_dashboard/ para manter o codigo organizado.
"""
import tkinter as tk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_SIDEBAR, AZUL_HOVER,
    BRANCO, BRANCO_GELO, CINZA_FUNDO, CINZA_CLARO, CINZA_MEDIO,
    CINZA_ESCURO, PRETO_TEXTO, AMARELO_VIBRANTE, VERMELHO_ERRO,
    VERDE_SUCESSO, FONTE_TITULO, FONTE_TEXTO,
    LARGURA_SIDEBAR, ALTURA_HEADER
)
from componentes.logo_sf import LogoSF
from componentes.notificacao import Notificacao
from componentes.cursor_customizado import aplicar_cursor_global

from app.controlador import controlador_autenticacao
from app.modelo import modelo_geral

from app.visao.paginas_dashboard.pagina_inicio import PaginaInicio
from app.visao.paginas_dashboard.pagina_leads import PaginaLeads
from app.visao.paginas_dashboard.pagina_vendas import PaginaVendas
from app.visao.paginas_dashboard.pagina_pagamentos import PaginaPagamentos
from app.visao.paginas_dashboard.pagina_turmas import PaginaTurmas
from app.visao.paginas_dashboard.pagina_aulas import PaginaAulas
from app.visao.paginas_dashboard.pagina_frequencia import PaginaFrequencia
from app.visao.paginas_dashboard.pagina_funil import PaginaFunil
from app.visao.paginas_dashboard.pagina_relatorios import PaginaRelatorios
from app.visao.paginas_dashboard.pagina_configuracoes import PaginaConfiguracoes


class TelaDashboard(tk.Tk):
    """Dashboard administrativo."""

    def __init__(self):
        super().__init__()

        self.title("Sistema Facil Educacao - Dashboard Administrativo")
        self.configure(bg=BRANCO_GELO)
        self.minsize(1200, 700)

        # Maximiza o dashboard
        self.state("zoomed")
        self.update_idletasks()

        # Pega sessao
        sessao = controlador_autenticacao.obter_sessao()
        self.nome_admin = sessao.get("nome", "Administrador")
        self.email_admin = sessao.get("email", "")

        # Carrega configuracoes (foto, etc)
        self.foto_admin_b64 = modelo_geral.obter_configuracao("foto_admin", "")

        self.secao_atual = "inicio"

        self._construir_sidebar()
        self._construir_header()
        self._construir_area_central()

        # Cursor global
        self.after(150, lambda: aplicar_cursor_global(self))

        # Mostra inicio
        self._navegar("inicio")

        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _centralizar(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ============ SIDEBAR ============
    def _construir_sidebar(self):
        self.sidebar = tk.Frame(self, bg=AZUL_SIDEBAR, width=LARGURA_SIDEBAR)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        topo = tk.Frame(self.sidebar, bg=AZUL_SIDEBAR, pady=20)
        topo.pack(fill="x")

        logo_frame = tk.Frame(topo, bg=AZUL_SIDEBAR)
        logo_frame.pack()
        LogoSF(logo_frame, tamanho=44, cor_fundo=AZUL_SIDEBAR).pack(side="left",
                                                                    padx=4)

        nome_frame = tk.Frame(logo_frame, bg=AZUL_SIDEBAR)
        nome_frame.pack(side="left", padx=4)
        tk.Label(nome_frame, text="Sistema Facil",
                 font=(FONTE_TITULO, 11, "bold"),
                 fg=BRANCO, bg=AZUL_SIDEBAR).pack(anchor="w")
        tk.Label(nome_frame, text="EDUCACAO",
                 font=(FONTE_TEXTO, 7, "bold"),
                 fg=AMARELO_VIBRANTE, bg=AZUL_SIDEBAR).pack(anchor="w")

        # Linha
        tk.Frame(self.sidebar, bg="#0D1A3D", height=1).pack(fill="x", padx=14,
                                                            pady=(0, 6))

        # Itens
        self.itens_menu = [
            ("inicio", "📊", "Dashboard", None),
            ("leads", "👥", "Leads / Alunos", None),
            ("vendas", "💰", "Vendas", None),
            ("pagamentos", "💳", "Pagamentos", None),
            ("turmas", "📚", "Turmas", None),
            ("aulas", "🎓", "Aulas", None),
            ("frequencia", "✓", "Frequencia", None),
            ("funil", "🎯", "Funil de Origem", "novo"),
            ("relatorios", "📈", "Relatorios", None),
            ("configuracoes", "⚙", "Configuracoes", None),
        ]

        self.botoes_menu = {}
        for chave, icone, texto, badge in self.itens_menu:
            self._criar_item_menu(chave, icone, texto, badge)

        # Espacador
        tk.Frame(self.sidebar, bg=AZUL_SIDEBAR).pack(expand=True, fill="y")

        tk.Frame(self.sidebar, bg="#0D1A3D", height=1).pack(fill="x", padx=14)
        self._criar_item_menu("sair", "🚪", "Sair", None,
                              cor_acento=VERMELHO_ERRO)

    def _criar_item_menu(self, chave, icone, texto, badge=None,
                         cor_acento=None):
        item = tk.Frame(self.sidebar, bg=AZUL_SIDEBAR, cursor="hand2")
        item.pack(fill="x", padx=10, pady=2)

        cor_fg = cor_acento or "#D5DCE8"

        lbl_icone = tk.Label(item, text=icone,
                             font=("Segoe UI Emoji", 13),
                             bg=AZUL_SIDEBAR, fg=cor_fg, cursor="hand2")
        lbl_icone.pack(side="left", padx=(12, 8), pady=10)

        lbl_texto = tk.Label(item, text=texto,
                             font=(FONTE_TEXTO, 10),
                             bg=AZUL_SIDEBAR, fg=cor_fg,
                             cursor="hand2", anchor="w")
        lbl_texto.pack(side="left", fill="x", expand=True)

        if badge:
            badge_frame = tk.Frame(item, bg=AMARELO_VIBRANTE)
            badge_frame.pack(side="right", padx=10)
            tk.Label(badge_frame, text=f" {badge.upper()} ",
                     font=(FONTE_TEXTO, 7, "bold"),
                     fg=AZUL_ESCURO, bg=AMARELO_VIBRANTE).pack(padx=2, pady=1)

        def hover_in(_):
            if self.secao_atual != chave:
                item.configure(bg="#2D3F66")
                lbl_icone.configure(bg="#2D3F66")
                lbl_texto.configure(bg="#2D3F66")

        def hover_out(_):
            if self.secao_atual != chave:
                item.configure(bg=AZUL_SIDEBAR)
                lbl_icone.configure(bg=AZUL_SIDEBAR)
                lbl_texto.configure(bg=AZUL_SIDEBAR)

        for w in (item, lbl_icone, lbl_texto):
            w.bind("<Enter>", hover_in)
            w.bind("<Leave>", hover_out)
            w.bind("<Button-1>", lambda e, c=chave: self._navegar(c))

        self.botoes_menu[chave] = (item, lbl_icone, lbl_texto)

    def _navegar(self, secao):
        if secao == "sair":
            self._sair()
            return

        # Atualiza visual
        for chave, (item, ic, tx) in self.botoes_menu.items():
            if chave == secao:
                item.configure(bg=AZUL_PRIMARIO)
                ic.configure(bg=AZUL_PRIMARIO, fg=AMARELO_VIBRANTE)
                tx.configure(bg=AZUL_PRIMARIO, fg=BRANCO)
            else:
                cor_def = (VERMELHO_ERRO if chave == "sair" else "#D5DCE8")
                item.configure(bg=AZUL_SIDEBAR)
                ic.configure(bg=AZUL_SIDEBAR, fg=cor_def)
                tx.configure(bg=AZUL_SIDEBAR, fg=cor_def)

        self.secao_atual = secao

        # Limpa area
        for widget in self.area_central.winfo_children():
            widget.destroy()

        # Mapa de paginas
        paginas = {
            "inicio": PaginaInicio,
            "leads": PaginaLeads,
            "vendas": PaginaVendas,
            "pagamentos": PaginaPagamentos,
            "turmas": PaginaTurmas,
            "aulas": PaginaAulas,
            "frequencia": PaginaFrequencia,
            "funil": PaginaFunil,
            "relatorios": PaginaRelatorios,
            "configuracoes": PaginaConfiguracoes,
        }

        ClassePagina = paginas.get(secao)
        if ClassePagina:
            try:
                pagina = ClassePagina(self.area_central, dashboard=self)
                pagina.pack(fill="both", expand=True)
            except Exception as e:
                Notificacao.erro(self, f"Erro ao abrir secao: {e}")
                # Mostra mensagem de erro como fallback
                tk.Label(self.area_central,
                         text=f"Erro ao carregar pagina:\n{e}",
                         font=(FONTE_TEXTO, 11),
                         fg=VERMELHO_ERRO, bg=BRANCO_GELO).pack(pady=40)

        # Atualiza topo
        self._atualizar_titulo_header(secao)

    # ============ HEADER ============
    def _construir_header(self):
        self.header = tk.Frame(self, bg=BRANCO, height=ALTURA_HEADER,
                               highlightbackground=CINZA_CLARO,
                               highlightthickness=1)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)

        # Titulo
        self.lbl_titulo_secao = tk.Label(
            self.header, text="Dashboard",
            font=(FONTE_TITULO, 16, "bold"),
            fg=AZUL_ESCURO, bg=BRANCO
        )
        self.lbl_titulo_secao.pack(side="left", padx=24)

        # Direita - notificacoes + perfil
        direita = tk.Frame(self.header, bg=BRANCO)
        direita.pack(side="right", padx=20)

        # Notificacoes
        self.btn_notif = tk.Frame(direita, bg=BRANCO, cursor="hand2")
        self.btn_notif.pack(side="left", padx=10)

        self.lbl_notif = tk.Label(self.btn_notif, text="🔔",
                                  font=("Segoe UI Emoji", 16),
                                  bg=BRANCO, cursor="hand2")
        self.lbl_notif.pack(side="left")

        # Badge contador
        self.contador_notif = modelo_geral.contar_notificacoes_nao_lidas()
        self.badge_notif = tk.Label(
            self.btn_notif, text=str(self.contador_notif),
            font=(FONTE_TEXTO, 8, "bold"),
            fg=BRANCO, bg=VERMELHO_ERRO,
            padx=4, pady=0
        )
        if self.contador_notif > 0:
            self.badge_notif.pack(side="left", padx=(2, 0))

        for w in (self.btn_notif, self.lbl_notif):
            w.bind("<Button-1>", lambda e: self._abrir_notificacoes())

        # Separador
        tk.Frame(direita, bg=CINZA_CLARO, width=1, height=30).pack(
            side="left", padx=14, pady=10)

        # Perfil
        perfil = tk.Frame(direita, bg=BRANCO, cursor="hand2")
        perfil.pack(side="left")

        # Avatar
        avatar = tk.Frame(perfil, bg=AMARELO_VIBRANTE, width=40, height=40)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        tk.Label(avatar, text="👨‍💼", font=("Segoe UI Emoji", 18),
                 bg=AMARELO_VIBRANTE, cursor="hand2").pack(expand=True)

        # Info
        info = tk.Frame(perfil, bg=BRANCO)
        info.pack(side="left", padx=10)
        nome_admin_atual = modelo_geral.obter_configuracao(
            "nome_admin", self.nome_admin)
        tk.Label(info, text=nome_admin_atual,
                 font=(FONTE_TEXTO, 10, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Label(info, text=self.email_admin,
                 font=(FONTE_TEXTO, 8),
                 fg=CINZA_ESCURO, bg=BRANCO).pack(anchor="w")

        for w in (perfil, avatar, info):
            try:
                w.bind("<Button-1>",
                       lambda e: self._navegar("configuracoes"))
            except tk.TclError:
                pass

    def _atualizar_titulo_header(self, secao):
        nomes = {
            "inicio": "Dashboard",
            "leads": "Leads / Alunos",
            "vendas": "Vendas",
            "pagamentos": "Pagamentos",
            "turmas": "Turmas",
            "aulas": "Aulas",
            "frequencia": "Frequencia",
            "funil": "Funil de Origem",
            "relatorios": "Relatorios",
            "configuracoes": "Configuracoes",
        }
        if hasattr(self, "lbl_titulo_secao"):
            self.lbl_titulo_secao.configure(text=nomes.get(secao, "Dashboard"))

    def atualizar_contador_notificacoes(self):
        """Chamado pelas paginas quando criam notificacoes."""
        self.contador_notif = modelo_geral.contar_notificacoes_nao_lidas()
        self.badge_notif.configure(text=str(self.contador_notif))
        if self.contador_notif > 0:
            try:
                self.badge_notif.pack(side="left", padx=(2, 0))
            except tk.TclError:
                pass
        else:
            self.badge_notif.pack_forget()

    def _abrir_notificacoes(self):
        # Abre janela popover com notificacoes recentes
        popover = tk.Toplevel(self)
        popover.title("Notificacoes")
        popover.geometry("420x500")
        popover.configure(bg=BRANCO)
        popover.transient(self)

        # Posiciona perto do botao
        x = self.winfo_rootx() + self.winfo_width() - 440
        y = self.winfo_rooty() + 60
        popover.geometry(f"420x500+{x}+{y}")

        # Header
        h = tk.Frame(popover, bg=AZUL_PRIMARIO, pady=14, padx=18)
        h.pack(fill="x")
        tk.Label(h, text="🔔  Notificacoes",
                 font=(FONTE_TITULO, 13, "bold"),
                 fg=BRANCO, bg=AZUL_PRIMARIO).pack(side="left")

        tk.Label(h, text="✕", font=(FONTE_TEXTO, 12, "bold"),
                 fg=BRANCO, bg=AZUL_PRIMARIO,
                 cursor="hand2").pack(side="right")

        # Lista
        lista_frame = tk.Frame(popover, bg=BRANCO_GELO)
        lista_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(lista_frame, bg=BRANCO_GELO,
                           highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(lista_frame, orient="vertical",
                          command=canvas.yview)
        sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)

        inner = tk.Frame(canvas, bg=BRANCO_GELO)
        canvas.create_window((0, 0), window=inner, anchor="nw", width=420)

        notificacoes = modelo_geral.listar_notificacoes(limite=30)
        if not notificacoes:
            tk.Label(inner, text="Sem notificacoes",
                     font=(FONTE_TEXTO, 11, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO_GELO,
                     pady=40).pack()
        else:
            for n in notificacoes:
                self._criar_card_notif(inner, n, popover)

        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _criar_card_notif(self, parent, n, popover):
        cor_tipo = {
            "sucesso": VERDE_SUCESSO,
            "erro": VERMELHO_ERRO,
            "aviso": "#F59E0B",
            "info": AZUL_PRIMARIO,
        }.get(n.get("tipo", "info"), AZUL_PRIMARIO)

        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1, padx=14, pady=12)
        card.pack(fill="x", padx=8, pady=4)

        if not n.get("lida"):
            tk.Frame(card, bg=cor_tipo, width=4).pack(side="left", fill="y",
                                                      padx=(0, 10))

        cont = tk.Frame(card, bg=BRANCO)
        cont.pack(side="left", fill="x", expand=True)

        tk.Label(cont, text=n.get("titulo", ""),
                 font=(FONTE_TEXTO, 10, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO,
                 wraplength=340, justify="left").pack(anchor="w")
        tk.Label(cont, text=n.get("mensagem", ""),
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO,
                 wraplength=340, justify="left").pack(anchor="w")

        data_str = str(n.get("data_criacao", ""))[:16]
        tk.Label(cont, text=data_str,
                 font=(FONTE_TEXTO, 8),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w", pady=(4, 0))

        def marcar(_=None):
            modelo_geral.marcar_notificacao_lida(n["id"])
            self.atualizar_contador_notificacoes()
            try:
                popover.destroy()
            except tk.TclError:
                pass
            self._abrir_notificacoes()

        for w in (card, cont):
            w.bind("<Button-1>", marcar)
            w.configure(cursor="hand2")

    # ============ AREA CENTRAL ============
    def _construir_area_central(self):
        self.area_central = tk.Frame(self, bg=BRANCO_GELO)
        self.area_central.pack(fill="both", expand=True)

    # ============ SAIR ============
    def _sair(self):
        controlador_autenticacao.encerrar_sessao()
        Notificacao.info(self, "Sessao encerrada")
        self.after(800, self._fechar_e_reabrir)

    def _fechar_e_reabrir(self):
        self.destroy()
        from app.visao.tela_pagina_inicial import TelaPaginaInicial
        TelaPaginaInicial().mainloop()

    def _ao_fechar(self):
        self._sair()
