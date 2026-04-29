import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
import hashlib


class SistemaFuncionario:
    # Paleta de cores (mantida do design original)
    COR_ROYAL_BLUE = "#112250"
    COR_QUICKSAND = "#E0BE7A"
    COR_SHELLSTONE = "#E5DED1"

    # Tons derivados para uma UI mais moderna
    COR_FUNDO = "#F5F1E8"
    COR_BRANCO = "#FFFFFF"
    COR_TEXTO = "#1A1F36"
    COR_TEXTO_SUAVE = "#5A6478"
    COR_BORDA = "#D9D2C2"
    COR_HOVER_SIDEBAR = "#1B3270"
    COR_ATIVO_SIDEBAR = "#0B1838"
    COR_SUCESSO = "#2E8B57"
    COR_PERIGO = "#C0392B"
    COR_LINHA_ALT = "#F2EADB"

    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Sistema Fácil — Gestão de Funcionários")
        self.raiz.configure(bg=self.COR_FUNDO)

        # Dimensões
        self.largura = self.raiz.winfo_screenwidth()
        self.altura = self.raiz.winfo_screenheight()
        self.raiz.geometry(f"{self.largura}x{self.altura}+0+0")
        self.raiz.minsize(1100, 650)

        self._configurar_estilos()
        self._construir_layout()
        self._tentar_carregar_inicial()

    # ----------------------- Estilos -----------------------
    def _configurar_estilos(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except Exception:
            pass

        # Treeview moderno
        estilo.configure(
            "Moderno.Treeview",
            background=self.COR_BRANCO,
            fieldbackground=self.COR_BRANCO,
            foreground=self.COR_TEXTO,
            rowheight=38,
            font=("Segoe UI", 11),
            borderwidth=0,
            relief="flat",
        )
        estilo.configure(
            "Moderno.Treeview.Heading",
            background=self.COR_ROYAL_BLUE,
            foreground="white",
            font=("Segoe UI Semibold", 11),
            padding=(10, 12),
            borderwidth=0,
            relief="flat",
        )
        estilo.map(
            "Moderno.Treeview.Heading",
            background=[("active", self.COR_HOVER_SIDEBAR)],
        )
        estilo.map(
            "Moderno.Treeview",
            background=[("selected", self.COR_QUICKSAND)],
            foreground=[("selected", self.COR_ROYAL_BLUE)],
        )

        # Scrollbar
        estilo.configure(
            "Moderno.Vertical.TScrollbar",
            background=self.COR_SHELLSTONE,
            troughcolor=self.COR_FUNDO,
            bordercolor=self.COR_FUNDO,
            arrowcolor=self.COR_ROYAL_BLUE,
        )

        # Entradas modernas
        estilo.configure(
            "Moderno.TEntry",
            fieldbackground=self.COR_BRANCO,
            foreground=self.COR_TEXTO,
            bordercolor=self.COR_BORDA,
            lightcolor=self.COR_BORDA,
            darkcolor=self.COR_BORDA,
            padding=10,
        )
        estilo.map(
            "Moderno.TEntry",
            bordercolor=[("focus", self.COR_QUICKSAND)],
            lightcolor=[("focus", self.COR_QUICKSAND)],
            darkcolor=[("focus", self.COR_QUICKSAND)],
        )

    # ----------------------- Layout -----------------------
    def _construir_layout(self):
        # Container principal
        principal = tk.Frame(self.raiz, bg=self.COR_FUNDO)
        principal.pack(fill="both", expand=True)

        # Sidebar à esquerda
        self._construir_sidebar(principal)

        # Área de conteúdo à direita
        conteudo = tk.Frame(principal, bg=self.COR_FUNDO)
        conteudo.pack(side="left", fill="both", expand=True)

        self._construir_topbar(conteudo)
        self._construir_cards_resumo(conteudo)
        self._construir_painel_tabela(conteudo)

    def _construir_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.COR_ROYAL_BLUE, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Marca
        marca_wrap = tk.Frame(sidebar, bg=self.COR_ROYAL_BLUE)
        marca_wrap.pack(fill="x", pady=(28, 30), padx=24)

        logo_box = tk.Frame(
            marca_wrap, bg=self.COR_QUICKSAND, width=46, height=46
        )
        logo_box.pack(side="left")
        logo_box.pack_propagate(False)
        tk.Label(
            logo_box,
            text="SF",
            bg=self.COR_QUICKSAND,
            fg=self.COR_ROYAL_BLUE,
            font=("Segoe UI Black", 14),
        ).pack(expand=True)

        marca_texto = tk.Frame(marca_wrap, bg=self.COR_ROYAL_BLUE)
        marca_texto.pack(side="left", padx=12)
        tk.Label(
            marca_texto,
            text="Sistema Fácil",
            bg=self.COR_ROYAL_BLUE,
            fg="white",
            font=("Segoe UI Semibold", 14),
        ).pack(anchor="w")
        tk.Label(
            marca_texto,
            text="Gestão de Funcionários",
            bg=self.COR_ROYAL_BLUE,
            fg=self.COR_QUICKSAND,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        # Separador sutil
        tk.Frame(sidebar, bg=self.COR_HOVER_SIDEBAR, height=1).pack(
            fill="x", padx=20, pady=(0, 18)
        )

        tk.Label(
            sidebar,
            text="MENU",
            bg=self.COR_ROYAL_BLUE,
            fg=self.COR_QUICKSAND,
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w", padx=28, pady=(0, 10))

        # Itens do menu
        itens = [
            ("\u2630  Painel", self.mostrar_todos),
            ("\u002B  Novo Funcionário", self.funcao_quadro_adicionar),
            ("\U0001F50E  Buscar Funcionário", self.funcao_quadro_buscar),
            ("\u270E  Atualizar Cadastro", self.funcao_quadro_atualizar),
            ("\u2716  Remover Acesso", self.funcao_quadro_remover),
            ("\u21BB  Recarregar Dados", self.mostrar_todos),
        ]

        self._botoes_menu = []
        for texto, comando in itens:
            btn = tk.Label(
                sidebar,
                text=texto,
                bg=self.COR_ROYAL_BLUE,
                fg="white",
                font=("Segoe UI", 11),
                anchor="w",
                padx=28,
                pady=12,
                cursor="hand2",
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._aplicar_hover_sidebar(btn, comando)
            self._botoes_menu.append(btn)

        # Rodapé da sidebar
        rodape = tk.Frame(sidebar, bg=self.COR_ROYAL_BLUE)
        rodape.pack(side="bottom", fill="x", pady=20, padx=24)
        tk.Frame(rodape, bg=self.COR_HOVER_SIDEBAR, height=1).pack(
            fill="x", pady=(0, 14)
        )
        tk.Label(
            rodape,
            text="\u25CF  Conectado a sistema_facil",
            bg=self.COR_ROYAL_BLUE,
            fg=self.COR_QUICKSAND,
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Label(
            rodape,
            text="v2.0  •  MySQL",
            bg=self.COR_ROYAL_BLUE,
            fg="#8FA0C8",
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(4, 0))

    def _aplicar_hover_sidebar(self, widget, comando):
        cor_normal = self.COR_ROYAL_BLUE
        cor_hover = self.COR_HOVER_SIDEBAR

        def on_enter(_):
            widget.configure(bg=cor_hover)

        def on_leave(_):
            widget.configure(bg=cor_normal)

        def on_click(_):
            widget.configure(bg=self.COR_ATIVO_SIDEBAR)
            self.raiz.after(120, lambda: widget.configure(bg=cor_hover))
            comando()

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", on_click)

    def _construir_topbar(self, parent):
        topbar = tk.Frame(parent, bg=self.COR_FUNDO)
        topbar.pack(fill="x", padx=32, pady=(28, 10))

        esquerda = tk.Frame(topbar, bg=self.COR_FUNDO)
        esquerda.pack(side="left")
        tk.Label(
            esquerda,
            text="Painel de Funcionários",
            bg=self.COR_FUNDO,
            fg=self.COR_ROYAL_BLUE,
            font=("Segoe UI Semibold", 22),
        ).pack(anchor="w")
        tk.Label(
            esquerda,
            text="Gerencie cadastros, acessos e informações da equipe",
            bg=self.COR_FUNDO,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(2, 0))

        direita = tk.Frame(topbar, bg=self.COR_FUNDO)
        direita.pack(side="right")

        # Botão de ação principal
        self._criar_botao_pill(
            direita,
            "+  Novo Funcionário",
            self.COR_ROYAL_BLUE,
            "white",
            self.funcao_quadro_adicionar,
        ).pack(side="right", padx=(10, 0))

        self._criar_botao_pill(
            direita,
            "\U0001F50E  Buscar",
            self.COR_QUICKSAND,
            self.COR_ROYAL_BLUE,
            self.funcao_quadro_buscar,
        ).pack(side="right", padx=(10, 0))

        self._criar_botao_pill(
            direita,
            "Atualizar Lista",
            self.COR_SHELLSTONE,
            self.COR_ROYAL_BLUE,
            self.mostrar_todos,
        ).pack(side="right")

    def _construir_cards_resumo(self, parent):
        wrap = tk.Frame(parent, bg=self.COR_FUNDO)
        wrap.pack(fill="x", padx=32, pady=(8, 16))

        self.card_total = self._criar_card_metric(
            wrap, "Total de Funcionários", "—", self.COR_ROYAL_BLUE
        )
        self.card_total.pack(side="left", expand=True, fill="x", padx=(0, 12))

        self.card_emails = self._criar_card_metric(
            wrap, "Com E-mail Cadastrado", "—", self.COR_QUICKSAND
        )
        self.card_emails.pack(side="left", expand=True, fill="x", padx=6)

        self.card_telefones = self._criar_card_metric(
            wrap, "Com Telefone Cadastrado", "—", self.COR_SUCESSO
        )
        self.card_telefones.pack(side="left", expand=True, fill="x", padx=(12, 0))

    def _criar_card_metric(self, parent, titulo, valor, cor_destaque):
        card = tk.Frame(
            parent,
            bg=self.COR_BRANCO,
            highlightthickness=1,
            highlightbackground=self.COR_BORDA,
        )
        # Barra colorida no topo
        tk.Frame(card, bg=cor_destaque, height=3).pack(fill="x")

        interior = tk.Frame(card, bg=self.COR_BRANCO)
        interior.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            interior,
            text=titulo.upper(),
            bg=self.COR_BRANCO,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w")

        lbl_valor = tk.Label(
            interior,
            text=valor,
            bg=self.COR_BRANCO,
            fg=self.COR_ROYAL_BLUE,
            font=("Segoe UI", 26, "bold"),
        )
        lbl_valor.pack(anchor="w", pady=(6, 0))

        # Guarda a referência para atualizar depois
        card.label_valor = lbl_valor
        return card

    def _construir_painel_tabela(self, parent):
        painel = tk.Frame(
            parent,
            bg=self.COR_BRANCO,
            highlightthickness=1,
            highlightbackground=self.COR_BORDA,
        )
        painel.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        # Cabeçalho do painel
        cab = tk.Frame(painel, bg=self.COR_BRANCO)
        cab.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(
            cab,
            text="Quadro de Funcionários Ativos",
            bg=self.COR_BRANCO,
            fg=self.COR_ROYAL_BLUE,
            font=("Segoe UI Semibold", 14),
        ).pack(side="left")

        # Caixa de busca
        busca_wrap = tk.Frame(
            cab,
            bg=self.COR_SHELLSTONE,
            highlightthickness=1,
            highlightbackground=self.COR_BORDA,
        )
        busca_wrap.pack(side="right")

        tk.Label(
            busca_wrap,
            text="\U0001F50D",
            bg=self.COR_SHELLSTONE,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI", 11),
        ).pack(side="left", padx=(10, 4), pady=6)

        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *a: self._filtrar_tabela())
        entrada_busca = tk.Entry(
            busca_wrap,
            textvariable=self.var_busca,
            bd=0,
            bg=self.COR_SHELLSTONE,
            fg=self.COR_TEXTO,
            font=("Segoe UI", 10),
            width=28,
            relief="flat",
        )
        entrada_busca.pack(side="left", padx=(0, 10), pady=8, ipady=2)
        entrada_busca.insert(0, "")

        # Container da tabela com scrollbar
        tabela_wrap = tk.Frame(painel, bg=self.COR_BRANCO)
        tabela_wrap.pack(fill="both", expand=True, padx=20, pady=(4, 18))

        colunas = ("id", "nome", "email", "endereco", "cpf", "telefone")
        cabecalhos = ["ID", "Nome", "E-mail", "Endereço", "CPF (Hash)", "Telefone"]
        larguras = [60, 200, 230, 230, 200, 140]

        scroll_y = ttk.Scrollbar(
            tabela_wrap, orient="vertical", style="Moderno.Vertical.TScrollbar"
        )
        scroll_y.pack(side="right", fill="y")

        self.tabela = ttk.Treeview(
            tabela_wrap,
            columns=colunas,
            show="headings",
            style="Moderno.Treeview",
            yscrollcommand=scroll_y.set,
        )
        for col, cab_txt, larg in zip(colunas, cabecalhos, larguras):
            self.tabela.heading(col, text=cab_txt)
            self.tabela.column(col, width=larg, anchor="w", stretch=True)

        # Linhas zebradas
        self.tabela.tag_configure("par", background=self.COR_BRANCO)
        self.tabela.tag_configure("impar", background=self.COR_LINHA_ALT)

        self.tabela.pack(fill="both", expand=True)
        scroll_y.config(command=self.tabela.yview)

        # Rodapé do painel
        rodape = tk.Frame(painel, bg=self.COR_BRANCO)
        rodape.pack(fill="x", padx=20, pady=(0, 14))

        self.lbl_status = tk.Label(
            rodape,
            text="Aguardando dados...",
            bg=self.COR_BRANCO,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI", 10),
        )
        self.lbl_status.pack(side="left")

    # ----------------------- Botões pill -----------------------
    def _criar_botao_pill(self, parent, texto, cor_bg, cor_fg, comando):
        btn = tk.Label(
            parent,
            text=f"  {texto}  ",
            bg=cor_bg,
            fg=cor_fg,
            font=("Segoe UI Semibold", 11),
            padx=18,
            pady=10,
            cursor="hand2",
        )

        def escurecer(cor_hex, fator=0.88):
            cor_hex = cor_hex.lstrip("#")
            r, g, b = int(cor_hex[0:2], 16), int(cor_hex[2:4], 16), int(cor_hex[4:6], 16)
            r, g, b = int(r * fator), int(g * fator), int(b * fator)
            return f"#{r:02x}{g:02x}{b:02x}"

        cor_hover = escurecer(cor_bg)

        btn.bind("<Enter>", lambda _: btn.configure(bg=cor_hover))
        btn.bind("<Leave>", lambda _: btn.configure(bg=cor_bg))
        btn.bind("<Button-1>", lambda _: comando())
        return btn

    # ----------------------- Banco -----------------------
    def conectar_db(self):
        self.conexao = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_facil",
        )
        self.cursor = self.conexao.cursor()

    def mascarar_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def mascarar_cpf(self, cpf):
        return hashlib.sha256(cpf.encode()).hexdigest()

    def _tentar_carregar_inicial(self):
        # Carrega na inicialização sem travar a UI caso o banco esteja indisponível
        self.raiz.after(200, self._carregar_silencioso)

    def _carregar_silencioso(self):
        try:
            self.mostrar_todos()
        except Exception:
            self.lbl_status.configure(
                text="Não foi possível carregar dados. Verifique a conexão com o banco."
            )

    # ----------------------- CREATE -----------------------
    def funcao_quadro_adicionar(self):
        janela = self._criar_modal("Cadastrar Novo Funcionário", 540, 760)
        self.janela_form = janela

        self._titulo_modal(
            janela,
            "Novo Funcionário",
            "Preencha os dados abaixo. CPF e senha serão protegidos com hash SHA-256 antes de serem salvos.",
        )

        form = tk.Frame(janela, bg=self.COR_BRANCO)
        form.pack(fill="both", expand=True, padx=36, pady=(10, 20))

        campos = [
            ("Nome completo", "nome", False),
            ("E-mail", "email", False),
            ("Endereço", "endereco", False),
            ("CPF (apenas números)", "cpf", False),
            ("Telefone", "telefone", False),
            ("Senha de acesso", "senha", True),
            ("Confirmar senha", "senha_confirma", True),
        ]
        self.entradas = {}

        for label, chave, oculto in campos:
            self._campo_form(form, label, chave, oculto, self.entradas)

        # Mensagem de validação (aparece quando senhas não conferem)
        self.lbl_alerta_senha = tk.Label(
            form,
            text="",
            bg=self.COR_BRANCO,
            fg=self.COR_PERIGO,
            font=("Segoe UI", 9, "italic"),
        )
        self.lbl_alerta_senha.pack(anchor="w", pady=(0, 4))

        # Validação em tempo real conforme o usuário digita
        def _validar_match(*_):
            s1 = self.entradas["senha"].get()
            s2 = self.entradas["senha_confirma"].get()
            if s2 and s1 != s2:
                self.lbl_alerta_senha.configure(text="As senhas não conferem.")
            elif s1 and s2 and s1 == s2:
                self.lbl_alerta_senha.configure(
                    text="\u2713  Senhas conferem.", fg=self.COR_SUCESSO
                )
            else:
                self.lbl_alerta_senha.configure(text="", fg=self.COR_PERIGO)

        self.entradas["senha"].bind("<KeyRelease>", _validar_match)
        self.entradas["senha_confirma"].bind("<KeyRelease>", _validar_match)

        botoes = tk.Frame(janela, bg=self.COR_BRANCO)
        botoes.pack(fill="x", padx=36, pady=(0, 24))

        self._criar_botao_pill(
            botoes, "Cancelar", self.COR_SHELLSTONE, self.COR_ROYAL_BLUE, janela.destroy
        ).pack(side="right", padx=(8, 0))
        self._criar_botao_pill(
            botoes,
            "Confirmar Registro",
            self.COR_ROYAL_BLUE,
            "white",
            self.salvar_funcionario,
        ).pack(side="right")

    def _campo_form(self, parent, label, chave, oculto, store):
        wrap = tk.Frame(parent, bg=self.COR_BRANCO)
        wrap.pack(fill="x", pady=(6, 10))

        tk.Label(
            wrap,
            text=label.upper(),
            bg=self.COR_BRANCO,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w", pady=(0, 4))

        moldura = tk.Frame(
            wrap,
            bg=self.COR_FUNDO,
            highlightthickness=1,
            highlightbackground=self.COR_BORDA,
        )
        moldura.pack(fill="x")

        ent = tk.Entry(
            moldura,
            font=("Segoe UI", 11),
            bd=0,
            bg=self.COR_FUNDO,
            fg=self.COR_TEXTO,
            relief="flat",
            show="*" if oculto else "",
            insertbackground=self.COR_ROYAL_BLUE,
        )
        ent.pack(fill="x", padx=12, ipady=8)

        # Foco => destaca a borda
        ent.bind(
            "<FocusIn>",
            lambda _e: moldura.configure(highlightbackground=self.COR_QUICKSAND),
        )
        ent.bind(
            "<FocusOut>",
            lambda _e: moldura.configure(highlightbackground=self.COR_BORDA),
        )

        store[chave] = ent

    def salvar_funcionario(self):
        # Coleta dos campos
        nome = self.entradas["nome"].get().strip()
        email = self.entradas["email"].get().strip()
        endereco = self.entradas["endereco"].get().strip()
        cpf = self.entradas["cpf"].get().strip()
        telefone = self.entradas["telefone"].get().strip()
        senha = self.entradas["senha"].get()
        senha_confirma = self.entradas["senha_confirma"].get()

        # Validações antes de tocar no banco
        if not all([nome, endereco, cpf, telefone, senha, senha_confirma]):
            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha todos os campos antes de confirmar o registro.",
            )
            return

        if senha != senha_confirma:
            messagebox.showerror(
                "Senhas diferentes",
                "A senha e a confirmação não conferem. Verifique e tente novamente.",
            )
            return

        if len(senha) < 4:
            messagebox.showwarning(
                "Senha muito curta",
                "A senha precisa ter pelo menos 4 caracteres.",
            )
            return

        try:
            self.conectar_db()
            query = (
                "INSERT INTO funcionario (nome, email, endereco, CPF, telefone, senha) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cpf_hash = self.mascarar_cpf(cpf)
            senha_hash = self.mascarar_senha(senha)
            valores = (
                nome,
                email or None,
                endereco,
                cpf_hash,
                telefone,
                senha_hash,
            )
            self.cursor.execute(query, valores)
            self.conexao.commit()
            self.conexao.close()
            messagebox.showinfo("Sucesso", "Funcionário cadastrado com sucesso!")
            self.janela_form.destroy()
            self.mostrar_todos()
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao salvar funcionário: {e}")

    # ----------------------- READ -----------------------
    def mostrar_todos(self):
        try:
            self.conectar_db()
            self.cursor.execute(
                "SELECT id_funcionario, nome, email, endereco, CPF, telefone FROM funcionario"
            )
            linhas = self.cursor.fetchall()
            self._dados_atuais = list(linhas)
            self._popular_tabela(self._dados_atuais)
            self.conexao.close()
            self._atualizar_cards(self._dados_atuais)
            self.lbl_status.configure(
                text=f"{len(self._dados_atuais)} funcionário(s) carregado(s)."
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados: {e}")

    def _popular_tabela(self, linhas):
        self.tabela.delete(*self.tabela.get_children())
        for i, linha in enumerate(linhas):
            tag = "par" if i % 2 == 0 else "impar"
            self.tabela.insert("", tk.END, values=linha, tags=(tag,))

    def _filtrar_tabela(self):
        termo = self.var_busca.get().strip().lower()
        if not hasattr(self, "_dados_atuais"):
            return
        if not termo:
            self._popular_tabela(self._dados_atuais)
            self.lbl_status.configure(
                text=f"{len(self._dados_atuais)} funcionário(s) carregado(s)."
            )
            return
        filtradas = [
            l
            for l in self._dados_atuais
            if any(termo in str(c).lower() for c in l)
        ]
        self._popular_tabela(filtradas)
        self.lbl_status.configure(
            text=f"{len(filtradas)} resultado(s) para \"{termo}\"."
        )

    def _atualizar_cards(self, linhas):
        total = len(linhas)
        # Colunas: id_funcionario, nome, email, endereco, CPF, telefone
        com_email = sum(1 for l in linhas if len(l) > 2 and l[2])
        com_telefone = sum(1 for l in linhas if len(l) > 5 and l[5])
        self.card_total.label_valor.configure(text=str(total))
        self.card_emails.label_valor.configure(text=str(com_email))
        self.card_telefones.label_valor.configure(text=str(com_telefone))

    # ----------------------- UPDATE -----------------------
    def funcao_quadro_atualizar(self):
        janela = self._criar_modal("Atualizar Funcionário", 500, 720)
        self.janela_atua = janela

        self._titulo_modal(
            janela,
            "Atualizar Cadastro",
            "Informe o ID e os novos dados. A senha é opcional — preencha apenas se quiser alterá-la.",
        )

        form = tk.Frame(janela, bg=self.COR_BRANCO)
        form.pack(fill="both", expand=True, padx=36, pady=(10, 20))

        store = {}
        self._campo_form(form, "ID do Funcionário", "id", False, store)
        self._campo_form(form, "Novo E-mail", "email", False, store)
        self._campo_form(form, "Novo Telefone", "telefone", False, store)
        self._campo_form(form, "Nova senha (opcional)", "senha", True, store)
        self._campo_form(form, "Confirmar nova senha", "senha_confirma", True, store)

        # Mensagem de validação para as senhas
        self.lbl_alerta_senha_upd = tk.Label(
            form,
            text="",
            bg=self.COR_BRANCO,
            fg=self.COR_PERIGO,
            font=("Segoe UI", 9, "italic"),
        )
        self.lbl_alerta_senha_upd.pack(anchor="w", pady=(0, 4))

        def _validar_match_upd(*_):
            s1 = store["senha"].get()
            s2 = store["senha_confirma"].get()
            if s2 and s1 != s2:
                self.lbl_alerta_senha_upd.configure(
                    text="As senhas não conferem.", fg=self.COR_PERIGO
                )
            elif s1 and s2 and s1 == s2:
                self.lbl_alerta_senha_upd.configure(
                    text="\u2713  Senhas conferem.", fg=self.COR_SUCESSO
                )
            else:
                self.lbl_alerta_senha_upd.configure(text="")

        store["senha"].bind("<KeyRelease>", _validar_match_upd)
        store["senha_confirma"].bind("<KeyRelease>", _validar_match_upd)

        self.id_atua = store["id"]
        self.novo_email = store["email"]
        self.novo_tel = store["telefone"]
        self.nova_senha = store["senha"]
        self.nova_senha_conf = store["senha_confirma"]

        botoes = tk.Frame(janela, bg=self.COR_BRANCO)
        botoes.pack(fill="x", padx=36, pady=(0, 24))

        self._criar_botao_pill(
            botoes, "Cancelar", self.COR_SHELLSTONE, self.COR_ROYAL_BLUE, janela.destroy
        ).pack(side="right", padx=(8, 0))
        self._criar_botao_pill(
            botoes,
            "Confirmar Mudanças",
            self.COR_ROYAL_BLUE,
            "white",
            self.executar_update,
        ).pack(side="right")

    def executar_update(self):
        id_func = self.id_atua.get().strip()
        email = self.novo_email.get().strip()
        tel = self.novo_tel.get().strip()
        senha = self.nova_senha.get()
        senha_conf = self.nova_senha_conf.get()

        if not id_func:
            messagebox.showwarning(
                "Campo obrigatório",
                "Informe o ID do funcionário a ser atualizado.",
            )
            return

        # Se o usuário começou a digitar uma nova senha, validar
        atualiza_senha = bool(senha or senha_conf)
        if atualiza_senha:
            if senha != senha_conf:
                messagebox.showerror(
                    "Senhas diferentes",
                    "A nova senha e a confirmação não conferem.",
                )
                return
            if len(senha) < 4:
                messagebox.showwarning(
                    "Senha muito curta",
                    "A nova senha precisa ter pelo menos 4 caracteres.",
                )
                return

        try:
            self.conectar_db()
            if atualiza_senha:
                senha_hash = self.mascarar_senha(senha)
                query = (
                    "UPDATE funcionario "
                    "SET email = %s, telefone = %s, senha = %s "
                    "WHERE id_funcionario = %s"
                )
                self.cursor.execute(
                    query, (email or None, tel, senha_hash, id_func)
                )
            else:
                query = (
                    "UPDATE funcionario "
                    "SET email = %s, telefone = %s "
                    "WHERE id_funcionario = %s"
                )
                self.cursor.execute(query, (email or None, tel, id_func))

            if self.cursor.rowcount == 0:
                self.conexao.close()
                messagebox.showwarning(
                    "Não encontrado",
                    f"Nenhum funcionário com ID {id_func} foi encontrado.",
                )
                return

            self.conexao.commit()
            self.conexao.close()
            msg = "Dados do funcionário atualizados!"
            if atualiza_senha:
                msg += "\nSenha alterada com sucesso."
            messagebox.showinfo("Sucesso", msg)
            self.janela_atua.destroy()
            self.mostrar_todos()
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro na atualização: {e}")

    # ----------------------- BUSCAR -----------------------
    def funcao_quadro_buscar(self):
        janela = self._criar_modal("Buscar Funcionário", 480, 420)
        self.janela_busca = janela

        self._titulo_modal(
            janela,
            "Buscar Funcionário",
            "Pesquise por ID, nome ou e-mail. O resultado aparecerá no painel principal.",
        )

        form = tk.Frame(janela, bg=self.COR_BRANCO)
        form.pack(fill="both", expand=True, padx=36, pady=(10, 20))

        # Tipo de busca
        tk.Label(
            form,
            text="BUSCAR POR",
            bg=self.COR_BRANCO,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w", pady=(0, 4))

        self.var_tipo_busca = tk.StringVar(value="Nome")
        moldura_combo = tk.Frame(
            form,
            bg=self.COR_FUNDO,
            highlightthickness=1,
            highlightbackground=self.COR_BORDA,
        )
        moldura_combo.pack(fill="x", pady=(0, 12))

        combo = ttk.Combobox(
            moldura_combo,
            textvariable=self.var_tipo_busca,
            values=["ID", "Nome", "E-mail"],
            state="readonly",
            font=("Segoe UI", 11),
        )
        combo.pack(fill="x", padx=12, ipady=6, pady=4)

        # Campo termo
        store = {}
        self._campo_form(form, "Termo de busca", "termo", False, store)
        self.entrada_busca_termo = store["termo"]
        self.entrada_busca_termo.bind(
            "<Return>", lambda _e: self.executar_busca()
        )

        # Dica
        tk.Label(
            form,
            text="Dica: para Nome e E-mail é feita busca parcial (LIKE).",
            bg=self.COR_BRANCO,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI", 9, "italic"),
        ).pack(anchor="w", pady=(2, 0))

        botoes = tk.Frame(janela, bg=self.COR_BRANCO)
        botoes.pack(fill="x", padx=36, pady=(0, 24))

        self._criar_botao_pill(
            botoes, "Cancelar", self.COR_SHELLSTONE, self.COR_ROYAL_BLUE, janela.destroy
        ).pack(side="right", padx=(8, 0))
        self._criar_botao_pill(
            botoes,
            "Buscar",
            self.COR_ROYAL_BLUE,
            "white",
            self.executar_busca,
        ).pack(side="right")

    def executar_busca(self):
        tipo = self.var_tipo_busca.get()
        termo = self.entrada_busca_termo.get().strip()

        if not termo:
            messagebox.showwarning(
                "Atenção", "Digite um termo para realizar a busca."
            )
            return

        try:
            self.conectar_db()
            base = (
                "SELECT id_funcionario, nome, email, endereco, CPF, telefone "
                "FROM funcionario "
            )
            if tipo == "ID":
                if not termo.isdigit():
                    messagebox.showwarning(
                        "ID inválido", "Para buscar por ID, digite apenas números."
                    )
                    self.conexao.close()
                    return
                self.cursor.execute(
                    base + "WHERE id_funcionario = %s", (int(termo),)
                )
            elif tipo == "E-mail":
                self.cursor.execute(
                    base + "WHERE email LIKE %s ORDER BY nome",
                    (f"%{termo}%",),
                )
            else:  # Nome
                self.cursor.execute(
                    base + "WHERE nome LIKE %s ORDER BY nome",
                    (f"%{termo}%",),
                )

            linhas = list(self.cursor.fetchall())
            self.conexao.close()

            if not linhas:
                messagebox.showinfo(
                    "Sem resultados",
                    f"Nenhum funcionário encontrado para \"{termo}\" em {tipo}.",
                )
                return

            # Exibe os resultados no painel principal
            self._dados_atuais = linhas
            self._popular_tabela(linhas)
            self._atualizar_cards(linhas)
            self.lbl_status.configure(
                text=f"{len(linhas)} resultado(s) para \"{termo}\" em {tipo}. "
                "Clique em \"Recarregar Dados\" para ver todos novamente."
            )
            self.janela_busca.destroy()
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro na busca: {e}")

    # ----------------------- DELETE -----------------------
    def funcao_quadro_remover(self):
        janela = self._criar_modal("Excluir Cadastro", 420, 320)
        self.janela_del = janela

        self._titulo_modal(
            janela,
            "Remover Acesso",
            "Esta ação é permanente. Confirme o ID antes de prosseguir.",
            cor_destaque=self.COR_PERIGO,
        )

        form = tk.Frame(janela, bg=self.COR_BRANCO)
        form.pack(fill="both", expand=True, padx=36, pady=(10, 0))

        store = {}
        self._campo_form(form, "ID para deletar", "id", False, store)
        self.id_del = store["id"]

        botoes = tk.Frame(janela, bg=self.COR_BRANCO)
        botoes.pack(fill="x", padx=36, pady=20)

        self._criar_botao_pill(
            botoes, "Cancelar", self.COR_SHELLSTONE, self.COR_ROYAL_BLUE, janela.destroy
        ).pack(side="right", padx=(8, 0))
        self._criar_botao_pill(
            botoes,
            "Remover Acesso",
            self.COR_PERIGO,
            "white",
            self.executar_delete,
        ).pack(side="right")

    def executar_delete(self):
        try:
            self.conectar_db()
            self.cursor.execute(
                "DELETE FROM funcionario WHERE id_funcionario = %s",
                (self.id_del.get(),),
            )
            self.conexao.commit()
            self.conexao.close()
            messagebox.showinfo("Aviso", "Acesso do funcionário removido com sucesso.")
            self.janela_del.destroy()
            self.mostrar_todos()
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao excluir: {e}")

    # ----------------------- Modal helpers -----------------------
    def _criar_modal(self, titulo, largura, altura):
        janela = tk.Toplevel(self.raiz)
        janela.title(titulo)
        janela.configure(bg=self.COR_BRANCO)
        janela.transient(self.raiz)
        janela.grab_set()
        janela.resizable(False, False)

        # Centraliza na tela
        self.raiz.update_idletasks()
        x = self.raiz.winfo_rootx() + (self.raiz.winfo_width() - largura) // 2
        y = self.raiz.winfo_rooty() + (self.raiz.winfo_height() - altura) // 2
        janela.geometry(f"{largura}x{altura}+{max(x,0)}+{max(y,0)}")
        return janela

    def _titulo_modal(self, parent, titulo, subtitulo, cor_destaque=None):
        cor_destaque = cor_destaque or self.COR_ROYAL_BLUE
        cabecalho = tk.Frame(parent, bg=self.COR_BRANCO)
        cabecalho.pack(fill="x", padx=36, pady=(28, 0))

        tk.Frame(cabecalho, bg=cor_destaque, width=4, height=34).pack(
            side="left", padx=(0, 12)
        )

        textos = tk.Frame(cabecalho, bg=self.COR_BRANCO)
        textos.pack(side="left", fill="x", expand=True)
        tk.Label(
            textos,
            text=titulo,
            bg=self.COR_BRANCO,
            fg=cor_destaque,
            font=("Segoe UI Semibold", 16),
        ).pack(anchor="w")
        tk.Label(
            textos,
            text=subtitulo,
            bg=self.COR_BRANCO,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI", 10),
            wraplength=400,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))


if __name__ == "__main__":
    raiz = tk.Tk()
    app = SistemaFuncionario(raiz)
    raiz.mainloop()
