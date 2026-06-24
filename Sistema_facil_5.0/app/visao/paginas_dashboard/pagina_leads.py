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
from componentes.card import Card
from componentes.mascaras import (
    aplicar_mascara_cpf, aplicar_mascara_data, aplicar_mascara_telefone,
    aplicar_mascara_cep
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
        window_id = canvas.create_window((0, 0), window=cont, anchor="n", width=1140)

        def ar(_=None):
            canvas.update_idletasks()
            h_req = cont.winfo_reqheight()
            canvas.configure(scrollregion=(0, 0, 0, h_req))
        cont.bind("<Configure>", ar)

        def ao_redimensionar_canvas(e):
            nova_largura = min(1140, e.width - 40)
            if nova_largura < 300:
                nova_largura = 300
            canvas.itemconfig(window_id, width=nova_largura)
            canvas.coords(window_id, e.width // 2, 0)
        canvas.bind("<Configure>", ao_redimensionar_canvas, add="+")

        # Rolar com mouse wheel apenas quando focado/ativo
        def _ao_rolar(e):
            try:
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            except Exception:
                pass
        
        def _bind_mousewheel(e):
            canvas.bind_all("<MouseWheel>", _ao_rolar)
        def _unbind_mousewheel(e):
            canvas.unbind_all("<MouseWheel>")
            
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        canvas.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Grid de 2 colunas principais (Formulário na esquerda, Jornada + Stats na direita)
        grid = tk.Frame(cont, bg=BRANCO_GELO, padx=24, pady=10)
        grid.pack(fill="both", expand=True)
        grid.rowconfigure(0, weight=1)
        grid.rowconfigure(1, weight=1)

        # Coluna 1 (formulario) - ocupa a coluna da esquerda (rowspan 2 para alinhar com os outros dois cards)
        self._construir_formulario(grid)

        # Coluna 2 (jornada) - no topo direito
        self._construir_jornada(grid)

        # Coluna 3 (stats origem) - abaixo da jornada na direita
        self._construir_stats_origem(grid)

        # Tabela leads
        self._construir_tabela(cont)

    # ============ COLUNA 1: FORMULARIO ============
    def _construir_formulario(self, parent):
        card = Card(parent, titulo="📝  Cadastro de Lead", padding=14, raio=12)
        card.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=4, pady=4)
        parent.columnconfigure(0, weight=3)

        # Form
        form = tk.Frame(card.interno, bg=BRANCO)
        form.pack(fill="both", expand=True)

        # Linha 1: nome, data nascimento
        linha1 = tk.Frame(form, bg=BRANCO)
        linha1.pack(fill="x", pady=4)
        self._criar_campo(linha1, "nome_completo", "Nome Completo *", col=0, weight=3)
        self._criar_campo(linha1, "data_nascimento", "Data de Nasc. (DD/MM/AAAA)", col=1, mascara="data", weight=1)

        # Linha 2: cpf, telefone, email
        linha2 = tk.Frame(form, bg=BRANCO)
        linha2.pack(fill="x", pady=4)
        self._criar_campo(linha2, "cpf", "CPF (000.000.000-00)", col=0, mascara="cpf", weight=1)
        self._criar_campo(linha2, "telefone", "Telefone", col=1, mascara="telefone", weight=1)
        self._criar_campo(linha2, "email", "Email", col=2, weight=2)

        # Linha 3: endereco, numero, complemento
        linha3 = tk.Frame(form, bg=BRANCO)
        linha3.pack(fill="x", pady=4)
        self._criar_campo(linha3, "endereco", "Endereco", col=0, weight=3)
        self._criar_campo(linha3, "numero", "Numero", col=1, weight=1)
        self._criar_campo(linha3, "complemento", "Complemento", col=2, weight=1)

        # Linha 4: cep, bairro, cidade, estado
        linha4 = tk.Frame(form, bg=BRANCO)
        linha4.pack(fill="x", pady=4)
        self._criar_campo(linha4, "cep", "CEP", col=0, mascara="cep", weight=1)
        self._criar_campo(linha4, "bairro", "Bairro", col=1, weight=2)
        self._criar_campo(linha4, "cidade", "Cidade", col=2, weight=2)
        self._criar_combo(linha4, "estado", "Estado", ESTADOS_BR, col=3, weight=1)

        # Linha 5: curso, origem, status
        linha5 = tk.Frame(form, bg=BRANCO)
        linha5.pack(fill="x", pady=4)
        self._criar_combo(linha5, "curso_interesse", "Curso de Interesse", CURSOS, col=0, weight=2)
        self._criar_combo(linha5, "como_conheceu", "Como Conheceu", ORIGEM_LEADS, col=1, weight=1)
        self._criar_combo(linha5, "status", "Status", STATUS_LEAD, col=2, weight=1)

        # Linha 6: captador
        linha6 = tk.Frame(form, bg=BRANCO)
        linha6.pack(fill="x", pady=4)
        self._criar_combo(linha6, "captador", "Captador / Vendedor", CAPTADORES, col=0, weight=2)

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

    def _criar_campo(self, parent, chave, label, col, mascara=None, weight=1):
        wrap = tk.Frame(parent, bg=BRANCO)
        wrap.grid(row=0, column=col, sticky="ew", padx=4)
        parent.columnconfigure(col, weight=weight)

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
        elif mascara == "cep":
            aplicar_mascara_cep(entry)

        self.entries[chave] = entry

    def _criar_combo(self, parent, chave, label, valores, col, weight=1):
        wrap = tk.Frame(parent, bg=BRANCO)
        wrap.grid(row=0, column=col, sticky="ew", padx=4)
        parent.columnconfigure(col, weight=weight)

        tk.Label(wrap, text=label,
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")

        combo = ttk.Combobox(wrap, values=valores, state="readonly",
                             font=(FONTE_TEXTO, 10))
        combo.pack(fill="x", ipady=4)
        self.entries[chave] = combo

    # ============ COLUNA 2: JORNADA ============
    def _construir_jornada(self, parent):
        card = Card(parent, titulo="🚀  Jornada do Aluno", padding=14, raio=12)
        card.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        parent.columnconfigure(1, weight=2)

        cont = tk.Frame(card.interno, bg=BRANCO)
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
        card = Card(parent, titulo="📊  Origem dos Leads", padding=14, raio=12)
        card.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)

        cont = tk.Frame(card.interno, bg=BRANCO)
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

        card = Card(wrap, titulo="👥  Leads Cadastrados", padding=14, raio=12)
        card.pack(fill="both", expand=True)

        # Cabecalho tabela
        head = tk.Frame(card.interno, bg=AZUL_PRIMARIO)
        head.pack(fill="x", pady=(8, 0))
        
        colunas = [
            ("ID", 1),
            ("Nome", 4),
            ("Telefone", 2),
            ("Curso", 3),
            ("Origem", 2),
            ("Status", 2),
            ("Acoes", 2)
        ]
        for col_idx, (col_name, weight) in enumerate(colunas):
            lbl = tk.Label(head, text=col_name,
                           font=(FONTE_TEXTO, 9, "bold"),
                           fg=BRANCO, bg=AZUL_PRIMARIO,
                           padx=8, pady=8)
            lbl.grid(row=0, column=col_idx, sticky="ew")
            head.columnconfigure(col_idx, weight=weight)

        # Container linhas
        self.frame_linhas = tk.Frame(card.interno, bg=BRANCO)
        self.frame_linhas.pack(fill="both", expand=True, pady=(10, 0))

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

        valores = [
            (f"#{lead.get('id', '')}", 1),
            ((lead.get("nome_completo") or ""), 4),
            ((lead.get("telefone") or "-"), 2),
            ((lead.get("curso_interesse") or "-"), 3),
            ((lead.get("como_conheceu") or "-"), 2),
            ((lead.get("status") or "LEAD"), 2),
        ]

        for col_idx, (valor, weight) in enumerate(valores):
            lbl = tk.Label(linha, text=str(valor),
                           font=(FONTE_TEXTO, 9),
                           fg=PRETO_TEXTO, bg=BRANCO,
                           padx=8, pady=8, anchor="w" if col_idx == 1 else "center")
            lbl.grid(row=0, column=col_idx, sticky="ew")
            linha.columnconfigure(col_idx, weight=weight)

        # Acoes
        acoes = tk.Frame(linha, bg=BRANCO)
        acoes.grid(row=0, column=6, sticky="ew")
        linha.columnconfigure(6, weight=2)
        
        # Centralizar botoes de acao
        acoes.columnconfigure(0, weight=1)
        acoes.columnconfigure(3, weight=1)
        
        btn_edit = tk.Label(acoes, text="✏",
                 font=("Segoe UI Emoji", 12),
                 bg=BRANCO, fg=AZUL_PRIMARIO,
                 cursor="hand2")
        btn_edit.grid(row=0, column=1, padx=4, pady=8)
        
        btn_del = tk.Label(acoes, text="🗑",
                 font=("Segoe UI Emoji", 12),
                 bg=BRANCO, fg=VERMELHO_ERRO,
                 cursor="hand2")
        btn_del.grid(row=0, column=2, padx=4, pady=8)

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
            def desfazer():
                res, m = controlador_dashboard.restaurar_registro("leads", lead)
                if res:
                    Notificacao.sucesso(self, "Exclusão desfeita!")
                    self._carregar_lista()
                else:
                    Notificacao.erro(self, f"Erro ao desfazer: {m}")

            Notificacao.sucesso(self, msg, comando_desfazer=desfazer)
            self._carregar_lista()
        else:
            Notificacao.erro(self, msg)
