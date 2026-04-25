import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
import hashlib


class SistemaEstudante:
    # Paleta de cores (mantida do design original)
    COR_ROYAL_BLUE = "#112250"
    COR_QUICKSAND = "#E0BE7A"
    COR_SHELLSTONE = "#D9CBC2"

    # Tons derivados para a UI moderna
    COR_FUNDO = "#F4EEE4"
    COR_BRANCO = "#FFFFFF"
    COR_TEXTO = "#1A1F36"
    COR_TEXTO_SUAVE = "#5A6478"
    COR_BORDA = "#CDBFB3"
    COR_HOVER_SIDEBAR = "#1B3270"
    COR_ATIVO_SIDEBAR = "#0B1838"
    COR_SUCESSO = "#2E8B57"
    COR_PERIGO = "#C0392B"
    COR_LINHA_ALT = "#F1E8DB"

    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Sistema Fácil — Cadastro de Estudantes")
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

        estilo.configure(
            "Moderno.Vertical.TScrollbar",
            background=self.COR_SHELLSTONE,
            troughcolor=self.COR_FUNDO,
            bordercolor=self.COR_FUNDO,
            arrowcolor=self.COR_ROYAL_BLUE,
        )

    # ----------------------- Layout -----------------------
    def _construir_layout(self):
        principal = tk.Frame(self.raiz, bg=self.COR_FUNDO)
        principal.pack(fill="both", expand=True)

        self._construir_sidebar(principal)

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

        logo_box = tk.Frame(marca_wrap, bg=self.COR_QUICKSAND, width=46, height=46)
        logo_box.pack(side="left")
        logo_box.pack_propagate(False)
        tk.Label(
            logo_box,
            text="SE",
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
            text="Cadastro de Estudantes",
            bg=self.COR_ROYAL_BLUE,
            fg=self.COR_QUICKSAND,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        # Separador
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

        itens = [
            ("\u2630  Listar Todos", self.mostrar_todos),
            ("\u002B  Novo Cadastro", self.funcao_quadro_adicionar),
            ("\U0001F50D  Consultar Aluno", self.funcao_quadro_busca),
            ("\u270E  Editar Registro", self.funcao_quadro_atualizar),
            ("\u2716  Remover Registro", self.funcao_quadro_remover),
            ("\u21BB  Recarregar Dados", self.mostrar_todos),
        ]

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

        # Rodapé sidebar
        rodape = tk.Frame(sidebar, bg=self.COR_ROYAL_BLUE)
        rodape.pack(side="bottom", fill="x", pady=20, padx=24)
        tk.Frame(rodape, bg=self.COR_HOVER_SIDEBAR, height=1).pack(fill="x", pady=(0, 14))
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
            text="Base de Dados de Alunos",
            bg=self.COR_FUNDO,
            fg=self.COR_ROYAL_BLUE,
            font=("Segoe UI Semibold", 22),
        ).pack(anchor="w")
        tk.Label(
            esquerda,
            text="Cadastre, consulte, edite e remova estudantes da instituição",
            bg=self.COR_FUNDO,
            fg=self.COR_TEXTO_SUAVE,
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(2, 0))

        direita = tk.Frame(topbar, bg=self.COR_FUNDO)
        direita.pack(side="right")

        self._criar_botao_pill(
            direita,
            "+  Novo Cadastro",
            self.COR_ROYAL_BLUE,
            "white",
            self.funcao_quadro_adicionar,
        ).pack(side="right", padx=(10, 0))

        self._criar_botao_pill(
            direita,
            "Atualizar Lista",
            self.COR_QUICKSAND,
            self.COR_ROYAL_BLUE,
            self.mostrar_todos,
        ).pack(side="right")

    def _construir_cards_resumo(self, parent):
        wrap = tk.Frame(parent, bg=self.COR_FUNDO)
        wrap.pack(fill="x", padx=32, pady=(8, 16))

        self.card_total = self._criar_card_metric(
            wrap, "Total de Alunos", "—", self.COR_ROYAL_BLUE
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
            text="Registros de Estudantes",
            bg=self.COR_BRANCO,
            fg=self.COR_ROYAL_BLUE,
            font=("Segoe UI Semibold", 14),
        ).pack(side="left")

        # Caixa de busca rápida
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

        # Container da tabela com scrollbar
        tabela_wrap = tk.Frame(painel, bg=self.COR_BRANCO)
        tabela_wrap.pack(fill="both", expand=True, padx=20, pady=(4, 18))

        colunas = ("id", "nome", "email", "endereco", "cpf", "telefone")
        cabecalhos = ["ID", "Nome", "E-mail", "Endereço", "CPF (Hash)", "Telefone"]
        larguras = [60, 200, 230, 230, 180, 140]

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

    def mascarar_cpf(self, cpf):
        return hashlib.sha256(cpf.encode()).hexdigest()

    def _tentar_carregar_inicial(self):
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
        janela = self._criar_modal("Novo Cadastro de Aluno", 520, 600)
        self.janela_form = janela

        self._titulo_modal(
            janela,
            "Novo Cadastro",
            "Preencha os dados abaixo para registrar um novo aluno.",
        )

        form = tk.Frame(janela, bg=self.COR_BRANCO)
        form.pack(fill="both", expand=True, padx=36, pady=(10, 20))

        campos = [
            ("Nome completo", "nome"),
            ("E-mail", "email"),
            ("Endereço", "endereco"),
            ("CPF", "cpf"),
            ("Telefone", "telefone"),
        ]
        self.entradas = {}

        for label, chave in campos:
            self._campo_form(form, label, chave, self.entradas)

        botoes = tk.Frame(janela, bg=self.COR_BRANCO)
        botoes.pack(fill="x", padx=36, pady=(0, 24))

        self._criar_botao_pill(
            botoes, "Cancelar", self.COR_SHELLSTONE, self.COR_ROYAL_BLUE, janela.destroy
        ).pack(side="right", padx=(8, 0))
        self._criar_botao_pill(
            botoes,
            "Salvar Cadastro",
            self.COR_ROYAL_BLUE,
            "white",
            self.salvar_dados,
        ).pack(side="right")

    def _campo_form(self, parent, label, chave, store):
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
            insertbackground=self.COR_ROYAL_BLUE,
        )
        ent.pack(fill="x", padx=12, ipady=8)

        ent.bind(
            "<FocusIn>",
            lambda _e: moldura.configure(highlightbackground=self.COR_QUICKSAND),
        )
        ent.bind(
            "<FocusOut>",
            lambda _e: moldura.configure(highlightbackground=self.COR_BORDA),
        )

        store[chave] = ent

    def salvar_dados(self):
        try:
            self.conectar_db()
            query = "INSERT INTO aluno (nome, email, endereco, CPF, telefone) VALUES (%s, %s, %s, %s, %s)"
            valores = (
                self.entradas["nome"].get(),
                self.entradas["email"].get(),
                self.entradas["endereco"].get(),
                self.mascarar_cpf(self.entradas["cpf"].get()),
                self.entradas["telefone"].get(),
            )
            self.cursor.execute(query, valores)
            self.conexao.commit()
            self.conexao.close()
            messagebox.showinfo("Sucesso", "Estudante cadastrado!")
            self.janela_form.destroy()
            self.mostrar_todos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    # ----------------------- BUSCA -----------------------
    def funcao_quadro_busca(self):
        janela = self._criar_modal("Buscar Aluno", 460, 320)
        self.janela_busca = janela

        self._titulo_modal(
            janela,
            "Consultar Aluno",
            "Digite parte do nome para localizar registros na base.",
        )

        form = tk.Frame(janela, bg=self.COR_BRANCO)
        form.pack(fill="both", expand=True, padx=36, pady=(10, 0))

        store = {}
        self._campo_form(form, "Buscar por nome", "nome", store)
        self.ent_busca_nome = store["nome"]

        botoes = tk.Frame(janela, bg=self.COR_BRANCO)
        botoes.pack(fill="x", padx=36, pady=20)

        self._criar_botao_pill(
            botoes, "Cancelar", self.COR_SHELLSTONE, self.COR_ROYAL_BLUE, janela.destroy
        ).pack(side="right", padx=(8, 0))
        self._criar_botao_pill(
            botoes,
            "Pesquisar",
            self.COR_ROYAL_BLUE,
            "white",
            self.executar_busca,
        ).pack(side="right")

    def executar_busca(self):
        try:
            self.conectar_db()
            query = "SELECT * FROM aluno WHERE nome LIKE %s"
            self.cursor.execute(query, (f"%{self.ent_busca_nome.get()}%",))
            linhas = self.cursor.fetchall()
            self._dados_atuais = list(linhas)
            self._popular_tabela(self._dados_atuais)
            self.conexao.close()
            self._atualizar_cards(self._dados_atuais)
            self.lbl_status.configure(
                text=f"{len(self._dados_atuais)} resultado(s) encontrado(s)."
            )
            self.janela_busca.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Busca falhou: {e}")

    # ----------------------- UPDATE -----------------------
    def funcao_quadro_atualizar(self):
        janela = self._criar_modal("Editar Registro de Aluno", 520, 580)
        self.janela_atua = janela

        self._titulo_modal(
            janela,
            "Editar Registro",
            "Informe o ID do aluno e os novos dados que deseja atualizar.",
        )

        form = tk.Frame(janela, bg=self.COR_BRANCO)
        form.pack(fill="both", expand=True, padx=36, pady=(10, 20))

        store = {}
        self._campo_form(form, "ID do Aluno", "id", store)
        self._campo_form(form, "Novo Nome", "nome", store)
        self._campo_form(form, "Novo E-mail", "email", store)
        self._campo_form(form, "Novo Endereço", "endereco", store)

        self.id_editar = store["id"]
        self.novo_nome = store["nome"]
        self.novo_email = store["email"]
        self.novo_endereco = store["endereco"]

        botoes = tk.Frame(janela, bg=self.COR_BRANCO)
        botoes.pack(fill="x", padx=36, pady=(0, 24))

        self._criar_botao_pill(
            botoes, "Cancelar", self.COR_SHELLSTONE, self.COR_ROYAL_BLUE, janela.destroy
        ).pack(side="right", padx=(8, 0))
        self._criar_botao_pill(
            botoes,
            "Atualizar Dados",
            self.COR_ROYAL_BLUE,
            "white",
            self.executar_atualizacao,
        ).pack(side="right")

    def executar_atualizacao(self):
        try:
            self.conectar_db()
            query = "UPDATE aluno SET nome=%s, email=%s, endereco=%s WHERE id_aluno=%s"
            self.cursor.execute(
                query,
                (
                    self.novo_nome.get(),
                    self.novo_email.get(),
                    self.novo_endereco.get(),
                    self.id_editar.get(),
                ),
            )
            self.conexao.commit()
            self.conexao.close()
            messagebox.showinfo("Sucesso", "Registro atualizado!")
            self.janela_atua.destroy()
            self.mostrar_todos()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar: {e}")

    # ----------------------- DELETE -----------------------
    def funcao_quadro_remover(self):
        janela = self._criar_modal("Remover Aluno", 420, 320)
        self.janela_rem = janela

        self._titulo_modal(
            janela,
            "Remover Registro",
            "Esta ação é permanente. Confirme o ID antes de prosseguir.",
            cor_destaque=self.COR_PERIGO,
        )

        form = tk.Frame(janela, bg=self.COR_BRANCO)
        form.pack(fill="both", expand=True, padx=36, pady=(10, 0))

        store = {}
        self._campo_form(form, "ID para excluir", "id", store)
        self.ent_id_rem = store["id"]

        botoes = tk.Frame(janela, bg=self.COR_BRANCO)
        botoes.pack(fill="x", padx=36, pady=20)

        self._criar_botao_pill(
            botoes, "Cancelar", self.COR_SHELLSTONE, self.COR_ROYAL_BLUE, janela.destroy
        ).pack(side="right", padx=(8, 0))
        self._criar_botao_pill(
            botoes,
            "Confirmar Exclusão",
            self.COR_PERIGO,
            "white",
            self.executar_remocao,
        ).pack(side="right")

    def executar_remocao(self):
        try:
            self.conectar_db()
            query = "DELETE FROM aluno WHERE id_aluno=%s"
            self.cursor.execute(query, (self.ent_id_rem.get(),))
            self.conexao.commit()
            self.conexao.close()
            messagebox.showinfo("Aviso", "Aluno removido com sucesso!")
            self.janela_rem.destroy()
            self.mostrar_todos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    # ----------------------- READ -----------------------
    def mostrar_todos(self):
        try:
            self.conectar_db()
            self.cursor.execute("SELECT * FROM aluno")
            linhas = self.cursor.fetchall()
            self._dados_atuais = list(linhas)
            self._popular_tabela(self._dados_atuais)
            self.conexao.close()
            self._atualizar_cards(self._dados_atuais)
            self.lbl_status.configure(
                text=f"{len(self._dados_atuais)} aluno(s) carregado(s)."
            )
        except Exception as e:
            self.lbl_status.configure(text=f"Erro ao listar: {e}")

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
                text=f"{len(self._dados_atuais)} aluno(s) carregado(s)."
            )
            return
        filtradas = [
            l for l in self._dados_atuais if any(termo in str(c).lower() for c in l)
        ]
        self._popular_tabela(filtradas)
        self.lbl_status.configure(
            text=f"{len(filtradas)} resultado(s) para \"{termo}\"."
        )

    def _atualizar_cards(self, linhas):
        total = len(linhas)
        # Considerando colunas: id, nome, email, endereco, cpf, telefone
        com_email = sum(1 for l in linhas if len(l) > 2 and l[2])
        com_telefone = sum(1 for l in linhas if len(l) > 5 and l[5])
        self.card_total.label_valor.configure(text=str(total))
        self.card_emails.label_valor.configure(text=str(com_email))
        self.card_telefones.label_valor.configure(text=str(com_telefone))

    # ----------------------- Modal helpers -----------------------
    def _criar_modal(self, titulo, largura, altura):
        janela = tk.Toplevel(self.raiz)
        janela.title(titulo)
        janela.configure(bg=self.COR_BRANCO)
        janela.transient(self.raiz)
        janela.grab_set()
        janela.resizable(False, False)

        self.raiz.update_idletasks()
        x = self.raiz.winfo_rootx() + (self.raiz.winfo_width() - largura) // 2
        y = self.raiz.winfo_rooty() + (self.raiz.winfo_height() - altura) // 2
        janela.geometry(f"{largura}x{altura}+{max(x, 0)}+{max(y, 0)}")
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
    janela = tk.Tk()
    app = SistemaEstudante(janela)
    janela.mainloop()
