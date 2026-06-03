"""
Pagina Leads - CRUD de leads/alunos com formulario completo,
jornada do aluno e graficos de origem.
"""
import tkinter as tk
from tkinter import ttk

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    AMARELO_VIBRANTE, VERDE_SUCESSO, VERMELHO_ERRO, LARANJA_ALERTA,
    ROXO_DESTAQUE, ROSA_DESTAQUE, FONTE_TITULO, FONTE_TEXTO,
    FUNIL_VISITANTES, FUNIL_LEADS, FUNIL_NEGOCIACAO,
    FUNIL_VENDAS, FUNIL_ATIVOS
)
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from componentes.mascaras import (
    aplicar_mascara_cpf, aplicar_mascara_data, aplicar_mascara_telefone
)
from app.controlador import controlador_dashboard
from app.controlador.listas_constantes import (
    CURSOS, ESTADOS_BR, ORIGEM_LEADS, CAPTADORES, STATUS_LEAD
)


class PaginaLeads(tk.Frame):
    """Pagina de gerenciamento de leads."""

    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self.lead_em_edicao = None  # id se estiver editando
        self.entries = {}
        self._construir()
        self._carregar_lista()

    def _construir(self):
        # Topo com titulo
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Cadastro de Leads",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo,
                 text="Cadastre, edite e acompanhe seus leads pela jornada",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO).pack(anchor="w")

        # Area scrollavel
        canvas = tk.Canvas(self, bg=BRANCO_GELO, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)

        cont = tk.Frame(canvas, bg=BRANCO_GELO)
        canvas.create_window((0, 0), window=cont, anchor="nw", width=1140)

        def ar(_=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        cont.bind("<Configure>", ar)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * (e.delta / 120)), "units"), add="+")

        # Grid de 3 colunas
        grid = tk.Frame(cont, bg=BRANCO_GELO, padx=24, pady=10)
        grid.pack(fill="both", expand=True)

        # Coluna 1 (formulario) - mais larga
        self._construir_formulario(grid)

        # Coluna 2 (jornada)
        self._construir_jornada(grid)

        # Coluna 3 (stats origem)
        self._construir_stats_origem(grid)

        # Tabela leads
        self._construir_tabela(cont)

    # ============ COLUNA 1: FORMULARIO ============
    def _construir_formulario(self, parent):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        parent.columnconfigure(0, weight=3)

        # Header
        header = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="📝  Cadastro de Lead",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        # Form
        form = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        form.pack(fill="both", expand=True)

        # Linha 1: nome, data nascimento
        linha1 = tk.Frame(form, bg=BRANCO)
        linha1.pack(fill="x", pady=4)
        self._criar_campo(linha1, "nome_completo", "Nome Completo *",
                          largura_pct=2)
        self._criar_campo(linha1, "data_nascimento", "Data de Nasc. (DD/MM/AAAA)",
                          mascara="data")

        # Linha 2: cpf, email
        linha2 = tk.Frame(form, bg=BRANCO)
        linha2.pack(fill="x", pady=4)
        self._criar_campo(linha2, "cpf", "CPF (000.000.000-00)",
                          mascara="cpf")
        self._criar_campo(linha2, "email", "Email", largura_pct=2)

        # Linha 3: telefone, endereco
        linha3 = tk.Frame(form, bg=BRANCO)
        linha3.pack(fill="x", pady=4)
        self._criar_campo(linha3, "telefone", "Telefone",
                          mascara="telefone")
        self._criar_campo(linha3, "endereco", "Endereco", largura_pct=2)

        # Linha 4: cidade, estado, status
        linha4 = tk.Frame(form, bg=BRANCO)
        linha4.pack(fill="x", pady=4)
        self._criar_campo(linha4, "cidade", "Cidade")
        self._criar_combo(linha4, "estado", "Estado", ESTADOS_BR)
        self._criar_combo(linha4, "status", "Status", STATUS_LEAD)

        # Linha 5: curso, origem
        linha5 = tk.Frame(form, bg=BRANCO)
        linha5.pack(fill="x", pady=4)
        self._criar_combo(linha5, "curso_interesse", "Curso de Interesse",
                          CURSOS, largura_pct=2)
        self._criar_combo(linha5, "como_conheceu", "Como Conheceu",
                          ORIGEM_LEADS)

        # Linha 6: captador
        linha6 = tk.Frame(form, bg=BRANCO)
        linha6.pack(fill="x", pady=4)
        self._criar_combo(linha6, "captador", "Captador / Vendedor",
                          CAPTADORES, largura_pct=2)

        # Observacoes
        tk.Label(form, text="Observacoes",
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w", pady=(8, 2))
        self.txt_obs = tk.Text(form, height=3, font=(FONTE_TEXTO, 10),
                               bg=BRANCO_GELO, fg=PRETO_TEXTO,
                               relief="flat",
                               highlightbackground=CINZA_CLARO,
                               highlightthickness=1, padx=8, pady=6)
        self.txt_obs.pack(fill="x", pady=(0, 8))

        # Botoes
        botoes = tk.Frame(form, bg=BRANCO)
        botoes.pack(fill="x", pady=(8, 0))

        BotaoModerno(botoes, texto="Cancelar",
                     comando=self._limpar_formulario,
                     largura=130, altura=38,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     fonte_tamanho=10,
                     cor_fundo=BRANCO).pack(side="left", padx=4)

        BotaoModerno(botoes, texto="💾  Salvar Lead",
                     comando=self._salvar_lead,
                     largura=170, altura=38,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     fonte_tamanho=10,
                     cor_fundo=BRANCO).pack(side="right", padx=4)

    def _criar_campo(self, parent, chave, label, mascara=None, largura_pct=1):
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

        if mascara == "cpf":
            aplicar_mascara_cpf(entry)
        elif mascara == "data":
            aplicar_mascara_data(entry)
        elif mascara == "telefone":
            aplicar_mascara_telefone(entry)

        self.entries[chave] = entry

    def _criar_combo(self, parent, chave, label, valores, largura_pct=1):
        wrap = tk.Frame(parent, bg=BRANCO)
        wrap.pack(side="left", fill="x", expand=True, padx=4)

        tk.Label(wrap, text=label,
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")

        combo = ttk.Combobox(wrap, values=valores, state="readonly",
                             font=(FONTE_TEXTO, 10))
        combo.pack(fill="x", ipady=4)
        self.entries[chave] = combo

    # ============ COLUNA 2: JORNADA ============
    def _construir_jornada(self, parent):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        parent.columnconfigure(1, weight=2)

        header = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="🚀  Jornada do Aluno",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        cont = tk.Frame(card, bg=BRANCO, padx=24, pady=18)
        cont.pack(fill="both", expand=True)

        etapas = [
            ("📝", "Cadastro", "Lead inserido", VERDE_SUCESSO),
            ("💰", "Venda", "Aguardando", AMARELO_VIBRANTE),
            ("✅", "Pagamento", "Pendente", CINZA_MEDIO),
            ("🔓", "Liberacao", "Pendente", CINZA_MEDIO),
            ("📚", "Turma", "Pendente", CINZA_MEDIO),
            ("🎓", "Aulas", "Pendente", CINZA_MEDIO),
            ("✓", "Frequencia", "Pendente", CINZA_MEDIO),
        ]

        for i, (icone, titulo, status, cor) in enumerate(etapas):
            linha = tk.Frame(cont, bg=BRANCO)
            linha.pack(fill="x", pady=2)

            # Bolinha
            bolinha = tk.Frame(linha, bg=cor, width=32, height=32)
            bolinha.pack(side="left")
            bolinha.pack_propagate(False)
            tk.Label(bolinha, text=icone, font=("Segoe UI Emoji", 12),
                     bg=cor, fg=BRANCO).pack(expand=True)

            # Texto
            txt = tk.Frame(linha, bg=BRANCO)
            txt.pack(side="left", fill="x", expand=True, padx=10)
            tk.Label(txt, text=titulo,
                     font=(FONTE_TEXTO, 10, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
            tk.Label(txt, text=status,
                     font=(FONTE_TEXTO, 8),
                     fg=cor, bg=BRANCO).pack(anchor="w")

            # Linha conectora (exceto ultimo)
            if i < len(etapas) - 1:
                tk.Frame(cont, bg=CINZA_CLARO,
                         width=2, height=12).pack(anchor="w", padx=15)

    # ============ COLUNA 3: STATS ORIGEM ============
    def _construir_stats_origem(self, parent):
        card = tk.Frame(parent, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
        parent.columnconfigure(2, weight=2)

        header = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="📊  Origem dos Leads",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        cont = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        cont.pack(fill="both", expand=True)

        try:
            stats = controlador_dashboard.estatisticas_leads()
            origens = stats.get("por_origem", {}) or {}
        except Exception:
            origens = {}

        if not origens:
            origens = {"Instagram": 0, "Indicacao": 0, "Google Ads": 0,
                       "Facebook Ads": 0, "Outros": 0}

        cores = [AZUL_PRIMARIO, VERDE_SUCESSO, AMARELO_VIBRANTE,
                 ROXO_DESTAQUE, ROSA_DESTAQUE, LARANJA_ALERTA]

        total = sum(origens.values()) or 1

        for i, (origem, valor) in enumerate(origens.items()):
            cor = cores[i % len(cores)]
            pct = (valor / total) * 100

            linha = tk.Frame(cont, bg=BRANCO)
            linha.pack(fill="x", pady=4)

            topo = tk.Frame(linha, bg=BRANCO)
            topo.pack(fill="x")
            tk.Label(topo, text=origem,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(side="left")
            tk.Label(topo, text=f"{valor} ({pct:.0f}%)",
                     font=(FONTE_TEXTO, 9),
                     fg=cor, bg=BRANCO).pack(side="right")

            # Barra
            barra_bg = tk.Frame(linha, bg=CINZA_CLARO, height=6)
            barra_bg.pack(fill="x", pady=(4, 0))
            preenchido = max(2, int(pct * 2.5))
            tk.Frame(barra_bg, bg=cor, height=6,
                     width=preenchido).pack(side="left", fill="y")

    # ============ TABELA ============
    def _construir_tabela(self, parent):
        wrap = tk.Frame(parent, bg=BRANCO_GELO, padx=24, pady=10)
        wrap.pack(fill="both", expand=True)

        card = tk.Frame(wrap, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="both", expand=True)

        header = tk.Frame(card, bg=BRANCO, padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="👥  Leads Cadastrados",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(side="left")
        tk.Frame(card, bg=CINZA_CLARO, height=1).pack(fill="x")

        # Cabecalho tabela
        head = tk.Frame(card, bg=AZUL_PRIMARIO)
        head.pack(fill="x", padx=18, pady=(8, 0))
        for col in ["ID", "Nome", "Telefone", "Curso", "Origem",
                    "Status", "Acoes"]:
            tk.Label(head, text=col,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        # Container linhas
        self.frame_linhas = tk.Frame(card, bg=BRANCO)
        self.frame_linhas.pack(fill="both", expand=True, padx=18, pady=(0, 14))

    def _carregar_lista(self):
        for w in self.frame_linhas.winfo_children():
            w.destroy()

        try:
            leads = controlador_dashboard.listar_leads()
        except Exception as e:
            Notificacao.erro(self, f"Erro ao carregar: {e}")
            return

        if not leads:
            tk.Label(self.frame_linhas,
                     text="Nenhum lead cadastrado ainda",
                     font=(FONTE_TEXTO, 10, "italic"),
                     fg=CINZA_MEDIO, bg=BRANCO,
                     pady=20).pack()
            return

        for lead in leads:
            self._criar_linha_tabela(lead)

    def _criar_linha_tabela(self, lead):
        linha = tk.Frame(self.frame_linhas, bg=BRANCO,
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1)
        linha.pack(fill="x")

        for valor in [
            f"#{lead.get('id', '')}",
            (lead.get("nome_completo") or "")[:25],
            lead.get("telefone") or "-",
            (lead.get("curso_interesse") or "-")[:20],
            (lead.get("como_conheceu") or "-")[:15],
            lead.get("status") or "LEAD",
        ]:
            tk.Label(linha, text=str(valor),
                     font=(FONTE_TEXTO, 9),
                     fg=PRETO_TEXTO, bg=BRANCO,
                     padx=8, pady=8).pack(side="left", expand=True, fill="x")

        # Acoes
        acoes = tk.Frame(linha, bg=BRANCO)
        acoes.pack(side="left", expand=True, fill="x")
        tk.Label(acoes, text="✏",
                 font=("Segoe UI Emoji", 12),
                 bg=BRANCO, fg=AZUL_PRIMARIO,
                 cursor="hand2").pack(side="left", padx=4)
        tk.Label(acoes, text="🗑",
                 font=("Segoe UI Emoji", 12),
                 bg=BRANCO, fg=VERMELHO_ERRO,
                 cursor="hand2").pack(side="left", padx=4)

        # Bind acoes
        for child in acoes.winfo_children():
            txt = child.cget("text")
            if txt == "✏":
                child.bind("<Button-1>",
                           lambda e, l=lead: self._editar_lead(l))
            elif txt == "🗑":
                child.bind("<Button-1>",
                           lambda e, l=lead: self._confirmar_excluir(l))

    # ============ ACOES ============
    def _coletar_dados(self):
        dados = {}
        for chave, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                dados[chave] = widget.get()
            else:
                dados[chave] = widget.get()
        dados["observacoes"] = self.txt_obs.get("1.0", "end").strip()
        return dados

    def _salvar_lead(self):
        dados = self._coletar_dados()

        if self.lead_em_edicao:
            sucesso, msg = controlador_dashboard.atualizar_lead(
                self.lead_em_edicao, dados)
        else:
            sucesso, msg, _ = controlador_dashboard.salvar_lead(dados)

        if sucesso:
            Notificacao.sucesso(self, msg)
            self._limpar_formulario()
            self._carregar_lista()
            if self.dashboard:
                try:
                    self.dashboard.atualizar_contador_notificacoes()
                except Exception:
                    pass
        else:
            Notificacao.erro(self, msg)

    def _limpar_formulario(self):
        self.lead_em_edicao = None
        for widget in self.entries.values():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, "end")
        self.txt_obs.delete("1.0", "end")

    def _editar_lead(self, lead):
        self.lead_em_edicao = lead.get("id")
        self._limpar_formulario()
        self.lead_em_edicao = lead.get("id")  # Re-set apos limpar

        for chave, widget in self.entries.items():
            valor = lead.get(chave, "")
            if isinstance(widget, ttk.Combobox):
                widget.set(valor or "")
            else:
                widget.insert(0, valor or "")
        self.txt_obs.insert("1.0", lead.get("observacoes") or "")
        Notificacao.info(self, f"Editando lead #{lead.get('id')}")

    def _confirmar_excluir(self, lead):
        dlg = tk.Toplevel(self)
        dlg.title("Confirmar exclusao")
        dlg.geometry("420x200")
        dlg.configure(bg=BRANCO)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)

        # Centraliza
        dlg.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 420) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 200) // 2
        dlg.geometry(f"420x200+{x}+{y}")

        h = tk.Frame(dlg, bg=VERMELHO_ERRO, height=60)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Label(h, text="⚠  Confirmar exclusao",
                 font=(FONTE_TEXTO, 12, "bold"),
                 fg=BRANCO, bg=VERMELHO_ERRO).pack(pady=18)

        corpo = tk.Frame(dlg, bg=BRANCO)
        corpo.pack(fill="both", expand=True, padx=20, pady=14)

        tk.Label(corpo,
                 text=f"Excluir lead '{lead.get('nome_completo')}'?\n"
                      "Esta acao nao pode ser desfeita.",
                 font=(FONTE_TEXTO, 10),
                 fg=PRETO_TEXTO, bg=BRANCO,
                 justify="center").pack(pady=8)

        btns = tk.Frame(corpo, bg=BRANCO)
        btns.pack(pady=8)

        BotaoModerno(btns, texto="Cancelar",
                     comando=dlg.destroy,
                     largura=120, altura=34,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     cor_fundo=BRANCO).pack(side="left", padx=4)

        BotaoModerno(btns, texto="Excluir",
                     comando=lambda: self._excluir_confirmado(
                         lead, dlg),
                     largura=120, altura=34,
                     cor_normal=VERMELHO_ERRO, cor_hover="#DC2626",
                     cor_fundo=BRANCO).pack(side="left", padx=4)

    def _excluir_confirmado(self, lead, dlg):
        sucesso, msg = controlador_dashboard.excluir_lead(lead.get("id"))
        dlg.destroy()
        if sucesso:
            Notificacao.sucesso(self, msg)
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)
