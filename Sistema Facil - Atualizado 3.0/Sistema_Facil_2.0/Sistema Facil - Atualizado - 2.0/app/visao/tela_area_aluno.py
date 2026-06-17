"""
Area do Aluno - Painel privado do aluno apos o login.

Mostra perfil, cursos, calendario, materiais, notas, frequencia,
mensagens, certificados e financeiro.
"""
import tkinter as tk
from datetime import datetime

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, AZUL_SIDEBAR,
    BRANCO, BRANCO_GELO, CINZA_FUNDO, CINZA_CLARO, CINZA_MEDIO,
    CINZA_ESCURO, PRETO_TEXTO, AMARELO_VIBRANTE, AMARELO_DOURADO,
    VERDE_SUCESSO, VERDE_CLARO, VERMELHO_ERRO, LARANJA_ALERTA,
    LARANJA_CLARO, ROXO_DESTAQUE, ROSA_DESTAQUE,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.logo_sf import LogoSF
from componentes.botao_moderno import BotaoModerno
from componentes.notificacao import Notificacao
from componentes.cursor_customizado import aplicar_cursor_global
from app.controlador import controlador_autenticacao


class TelaAreaAluno(tk.Tk):
    """Area do aluno apos login."""

    def __init__(self, usuario, master=None):
        super().__init__()
        self.usuario = usuario or {}
        self.master_ref = master

        self.title("Sistema Facil - Area do Aluno")
        self.configure(bg=BRANCO_GELO)
        self.minsize(1100, 660)

        # Maximiza a janela
        self.state("zoomed")
        self.update_idletasks()

        self.secao_atual = "perfil"

        self._construir_sidebar()
        self._construir_topo()
        self._construir_area_central()

        self.after(150, lambda: aplicar_cursor_global(self))

        # Mostra perfil por padrao
        self._mostrar_perfil()

        # Ao fechar, volta para a tela inicial
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
        self.sidebar = tk.Frame(self, bg=AZUL_SIDEBAR, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        topo = tk.Frame(self.sidebar, bg=AZUL_SIDEBAR, pady=24)
        topo.pack(fill="x")

        logo_frame = tk.Frame(topo, bg=AZUL_SIDEBAR)
        logo_frame.pack()
        LogoSF(logo_frame, tamanho=44, cor_fundo=AZUL_SIDEBAR).pack(side="left",
                                                                    padx=4)
        tk.Label(logo_frame, text="Sistema Facil",
                 font=(FONTE_TITULO, 11, "bold"),
                 fg=BRANCO, bg=AZUL_SIDEBAR).pack(side="left", padx=4)

        # Subtitulo
        tk.Label(self.sidebar, text="AREA DO ALUNO",
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=AMARELO_VIBRANTE,
                 bg=AZUL_SIDEBAR).pack(pady=(0, 16))

        # Perfil mini
        perfil = tk.Frame(self.sidebar, bg="#2D3F66", pady=12)
        perfil.pack(fill="x", padx=12, pady=(0, 16))
        nome = self.usuario.get("nome_completo", "Aluno")
        matricula = self.usuario.get("matricula") or "S/M"
        tk.Label(perfil, text="👤", font=("Segoe UI Emoji", 24),
                 bg="#2D3F66", fg=AMARELO_VIBRANTE).pack()
        tk.Label(perfil, text=nome[:24],
                 font=(FONTE_TEXTO, 9, "bold"),
                 fg=BRANCO, bg="#2D3F66").pack()
        tk.Label(perfil, text=f"Matricula: {matricula}",
                 font=(FONTE_TEXTO, 8),
                 fg="#9AA3B5", bg="#2D3F66").pack()

        # Itens de menu
        self.itens_menu = [
            ("perfil", "👤", "Meu Perfil"),
            ("cursos", "📚", "Meus Cursos"),
            ("calendario", "📅", "Calendario"),
            ("materiais", "📥", "Materiais"),
            ("notas", "📊", "Notas e Frequencia"),
            ("mensagens", "💬", "Mensagens"),
            ("certificados", "🏆", "Certificados"),
            ("financeiro", "💳", "Financeiro"),
        ]

        self.botoes_menu = {}
        for chave, icone, texto in self.itens_menu:
            self._criar_item_menu(chave, icone, texto)

        # Logout
        tk.Frame(self.sidebar, bg="#0D1A3D", height=1).pack(fill="x",
                                                            pady=20, padx=12)
        self._criar_item_menu("sair", "🚪", "Sair", cor_acento=VERMELHO_ERRO)

    def _criar_item_menu(self, chave, icone, texto, cor_acento=None):
        item = tk.Frame(self.sidebar, bg=AZUL_SIDEBAR, cursor="hand2")
        item.pack(fill="x", padx=12, pady=2)

        cor_fg = cor_acento or "#D5DCE8"

        lbl_icone = tk.Label(item, text=icone,
                             font=("Segoe UI Emoji", 14),
                             bg=AZUL_SIDEBAR, fg=cor_fg, cursor="hand2")
        lbl_icone.pack(side="left", padx=(12, 8), pady=10)

        lbl_texto = tk.Label(item, text=texto,
                             font=(FONTE_TEXTO, 10),
                             bg=AZUL_SIDEBAR, fg=cor_fg,
                             cursor="hand2", anchor="w")
        lbl_texto.pack(side="left", fill="x", expand=True)

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

        # Atualiza visual do item ativo
        for chave, (item, ic, tx) in self.botoes_menu.items():
            if chave == secao:
                item.configure(bg=AZUL_PRIMARIO)
                ic.configure(bg=AZUL_PRIMARIO, fg=AMARELO_VIBRANTE)
                tx.configure(bg=AZUL_PRIMARIO, fg=BRANCO)
            else:
                item.configure(bg=AZUL_SIDEBAR)
                ic.configure(bg=AZUL_SIDEBAR,
                             fg=VERMELHO_ERRO if chave == "sair" else "#D5DCE8")
                tx.configure(bg=AZUL_SIDEBAR,
                             fg=VERMELHO_ERRO if chave == "sair" else "#D5DCE8")

        self.secao_atual = secao

        # Limpa area central e mostra a secao
        for widget in self.area_central.winfo_children():
            widget.destroy()

        funcoes = {
            "perfil": self._mostrar_perfil,
            "cursos": self._mostrar_cursos,
            "calendario": self._mostrar_calendario,
            "materiais": self._mostrar_materiais,
            "notas": self._mostrar_notas,
            "mensagens": self._mostrar_mensagens,
            "certificados": self._mostrar_certificados,
            "financeiro": self._mostrar_financeiro,
        }
        funcao = funcoes.get(secao)
        if funcao:
            funcao()

    # ============ TOPO ============
    def _construir_topo(self):
        self.topo = tk.Frame(self, bg=BRANCO, height=64,
                             highlightbackground=CINZA_CLARO,
                             highlightthickness=1)
        self.topo.pack(side="top", fill="x")
        self.topo.pack_propagate(False)

        # Boas vindas
        nome = self.usuario.get("nome_completo", "Aluno")
        primeiro = nome.split()[0] if nome else "Aluno"

        tk.Label(self.topo, text=f"Ola, {primeiro}! 👋",
                 font=(FONTE_TITULO, 14, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(side="left", padx=24)

        # Direita
        direita = tk.Frame(self.topo, bg=BRANCO)
        direita.pack(side="right", padx=24)

        tk.Label(direita, text="🔔",
                 font=("Segoe UI Emoji", 16),
                 bg=BRANCO, cursor="hand2").pack(side="left", padx=10)

        # Email institucional
        email_inst = self.usuario.get("email_institucional", "")
        if email_inst:
            tk.Label(direita, text=email_inst,
                     font=(FONTE_TEXTO, 9),
                     fg=CINZA_ESCURO, bg=BRANCO).pack(side="left", padx=8)

    # ============ AREA CENTRAL ============
    def _construir_area_central(self):
        self.area_central = tk.Frame(self, bg=BRANCO_GELO)
        self.area_central.pack(fill="both", expand=True)

    def _titulo_secao(self, titulo, subtitulo=""):
        frame = tk.Frame(self.area_central, bg=BRANCO_GELO, pady=20)
        frame.pack(fill="x", padx=30)
        tk.Label(frame, text=titulo,
                 font=(FONTE_TITULO, 22, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO,
                 anchor="w").pack(fill="x")
        if subtitulo:
            tk.Label(frame, text=subtitulo,
                     font=(FONTE_TEXTO, 10),
                     fg=CINZA_ESCURO, bg=BRANCO_GELO,
                     anchor="w").pack(fill="x")

    # ============ SECOES ============
    def _mostrar_perfil(self):
        self._titulo_secao("Meu Perfil", "Suas informacoes pessoais e academicas")

        container = tk.Frame(self.area_central, bg=BRANCO_GELO)
        container.pack(fill="both", expand=True, padx=30, pady=10)

        # Card perfil
        card = tk.Frame(container, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        card.pack(fill="x", pady=4)

        # Header colorido
        header = tk.Canvas(card, height=120, bg=AZUL_PRIMARIO,
                           highlightthickness=0)
        header.pack(fill="x")
        for i in range(120):
            ratio = i / 120
            r = int(60 + ratio * 25)
            g = int(80 + ratio * 30)
            b = int(125 + ratio * 35)
            cor = f"#{r:02x}{g:02x}{b:02x}"
            header.create_line(0, i, 1200, i, fill=cor)

        # Avatar
        avatar = tk.Frame(card, bg=AMARELO_VIBRANTE, width=110, height=110,
                          highlightbackground=BRANCO, highlightthickness=4)
        avatar.place(x=40, y=64)
        avatar.pack_propagate(False)
        tk.Label(avatar, text="👤", font=("Segoe UI Emoji", 50),
                 bg=AMARELO_VIBRANTE).pack(expand=True)

        # Info
        info_frame = tk.Frame(card, bg=BRANCO, pady=16, padx=24)
        info_frame.pack(fill="x", pady=(60, 16))

        # Linha 1: nome + matricula
        linha1 = tk.Frame(info_frame, bg=BRANCO)
        linha1.pack(fill="x", padx=(140, 0))
        tk.Label(linha1, text=self.usuario.get("nome_completo", "Aluno"),
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO).pack(side="left")

        badge = tk.Frame(linha1, bg=VERDE_CLARO,
                         highlightbackground=VERDE_SUCESSO,
                         highlightthickness=1)
        badge.pack(side="left", padx=12)
        tk.Label(badge, text=f"  ● ATIVO  ",
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=VERDE_SUCESSO, bg=VERDE_CLARO).pack(padx=4, pady=2)

        # Detalhes
        detalhes_grid = tk.Frame(info_frame, bg=BRANCO)
        detalhes_grid.pack(fill="x", padx=(140, 0), pady=(12, 0))

        campos = [
            ("📧 Email institucional",
             self.usuario.get("email_institucional", "Nao gerado")),
            ("📧 Email pessoal",
             self.usuario.get("email_cadastro", "")),
            ("🆔 Matricula",
             self.usuario.get("matricula") or "S/M"),
            ("📞 Telefone",
             self.usuario.get("telefone", "Nao informado")),
            ("📅 Cadastro",
             str(self.usuario.get("data_cadastro", ""))[:16]),
            ("👤 Tipo",
             self.usuario.get("tipo_conta", "aluno").title()),
        ]

        for i, (rotulo, valor) in enumerate(campos):
            linha = i // 2
            coluna = i % 2

            box = tk.Frame(detalhes_grid, bg=BRANCO, padx=10, pady=6)
            box.grid(row=linha, column=coluna, sticky="w", padx=4)

            tk.Label(box, text=rotulo,
                     font=(FONTE_TEXTO, 8, "bold"),
                     fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
            tk.Label(box, text=str(valor) or "Nao informado",
                     font=(FONTE_TEXTO, 11),
                     fg=PRETO_TEXTO, bg=BRANCO).pack(anchor="w")

    def _mostrar_cursos(self):
        self._titulo_secao("Meus Cursos",
                           "Acompanhe seus cursos matriculados")

        grid = tk.Frame(self.area_central, bg=BRANCO_GELO)
        grid.pack(fill="x", padx=30, pady=10)

        cursos_aluno = [
            ("Tecnico em Informatica", "65%", AZUL_PRIMARIO, "Em andamento"),
            ("Workshop Python", "100%", VERDE_SUCESSO, "Concluido"),
            ("Excel Avancado", "30%", AMARELO_VIBRANTE, "Em andamento"),
        ]

        for i, (nome, progresso, cor, status) in enumerate(cursos_aluno):
            card = tk.Frame(grid, bg=BRANCO,
                            highlightbackground=CINZA_CLARO,
                            highlightthickness=1, width=380)
            card.grid(row=0, column=i, padx=8, sticky="nsew")

            # Faixa
            tk.Frame(card, bg=cor, height=6).pack(fill="x")

            cont = tk.Frame(card, bg=BRANCO, padx=18, pady=18)
            cont.pack(fill="both", expand=True)

            tk.Label(cont, text="🎓", font=("Segoe UI Emoji", 28),
                     bg=BRANCO).pack(anchor="w")
            tk.Label(cont, text=nome,
                     font=(FONTE_TEXTO, 12, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO,
                     wraplength=320).pack(anchor="w", pady=(8, 4))
            tk.Label(cont, text=f"Status: {status}",
                     font=(FONTE_TEXTO, 9),
                     fg=CINZA_ESCURO, bg=BRANCO).pack(anchor="w")

            # Barra progresso
            barra_bg = tk.Frame(cont, bg=CINZA_CLARO, height=8)
            barra_bg.pack(fill="x", pady=(12, 4))
            tk.Frame(barra_bg, bg=cor, height=8,
                     width=int(int(progresso[:-1]) * 3.2)).pack(side="left",
                                                                fill="y")
            tk.Label(cont, text=f"Progresso: {progresso}",
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=PRETO_TEXTO, bg=BRANCO).pack(anchor="w", pady=(4, 0))

    def _mostrar_calendario(self):
        self._titulo_secao("Calendario", "Provas, atividades e datas importantes")

        cont = tk.Frame(self.area_central, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        cont.pack(fill="both", expand=True, padx=30, pady=10)

        eventos = [
            ("📝 Prova de Banco de Dados", "15/06/2025", "14:00", LARANJA_ALERTA),
            ("📚 Entrega Trabalho Python", "20/06/2025", "23:59", VERMELHO_ERRO),
            ("🎓 Aula de Redes", "22/06/2025", "19:00", AZUL_PRIMARIO),
            ("✏️ Prova de Algoritmos", "30/06/2025", "10:00", VERDE_SUCESSO),
        ]

        for titulo, data, hora, cor in eventos:
            evento = tk.Frame(cont, bg=BRANCO, pady=14, padx=20,
                              highlightbackground=CINZA_CLARO,
                              highlightthickness=1)
            evento.pack(fill="x", padx=12, pady=4)

            tk.Frame(evento, bg=cor, width=4).pack(side="left", fill="y",
                                                   padx=(0, 12))

            info = tk.Frame(evento, bg=BRANCO)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=titulo,
                     font=(FONTE_TEXTO, 11, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
            tk.Label(info, text=f"📅 {data}  🕐 {hora}",
                     font=(FONTE_TEXTO, 9),
                     fg=CINZA_ESCURO, bg=BRANCO).pack(anchor="w")

    def _mostrar_materiais(self):
        self._titulo_secao("Materiais", "Apostilas, exercicios e PDFs")

        grid = tk.Frame(self.area_central, bg=BRANCO_GELO)
        grid.pack(fill="x", padx=30, pady=10)

        materiais = [
            ("📄 Apostila Python.pdf", "2.4 MB", AZUL_PRIMARIO),
            ("📊 Exercicios SQL.pdf", "1.2 MB", VERDE_SUCESSO),
            ("📕 Livro Algoritmos.pdf", "5.8 MB", ROXO_DESTAQUE),
            ("📑 Slides Aula 5.pdf", "3.1 MB", LARANJA_ALERTA),
            ("📋 Lista Exercicios.pdf", "0.8 MB", ROSA_DESTAQUE),
            ("📘 Manual ERP.pdf", "4.5 MB", AMARELO_VIBRANTE),
        ]

        for i, (nome, tamanho, cor) in enumerate(materiais):
            linha = i // 3
            coluna = i % 3
            card = tk.Frame(grid, bg=BRANCO,
                            highlightbackground=CINZA_CLARO,
                            highlightthickness=1, padx=20, pady=18,
                            width=300, height=120)
            card.grid(row=linha, column=coluna, padx=8, pady=8, sticky="nsew")
            card.grid_propagate(False)

            tk.Label(card, text=nome,
                     font=(FONTE_TEXTO, 11, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w")
            tk.Label(card, text=f"💾 {tamanho}",
                     font=(FONTE_TEXTO, 9),
                     fg=CINZA_ESCURO, bg=BRANCO).pack(anchor="w", pady=4)
            BotaoModerno(card, texto="📥 Baixar",
                         comando=lambda n=nome: Notificacao.info(
                             self, f"Baixando {n}..."),
                         largura=120, altura=32,
                         cor_normal=cor, cor_hover=cor,
                         fonte_tamanho=9,
                         cor_fundo=BRANCO).pack(anchor="w", pady=(4, 0))

    def _mostrar_notas(self):
        self._titulo_secao("Notas e Frequencia",
                           "Suas avaliacoes e presencas nas aulas")

        cont = tk.Frame(self.area_central, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        cont.pack(fill="both", expand=True, padx=30, pady=10)

        # Cabecalho
        header = tk.Frame(cont, bg=AZUL_PRIMARIO)
        header.pack(fill="x")
        for col in ["Disciplina", "Nota 1", "Nota 2", "Media", "Frequencia",
                    "Status"]:
            tk.Label(header, text=col, font=(FONTE_TEXTO, 10, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=22, pady=10).pack(side="left", expand=True)

        notas = [
            ("Banco de Dados", "8.5", "9.0", "8.75", "95%", "Aprovado"),
            ("Programacao", "7.0", "8.0", "7.5", "88%", "Aprovado"),
            ("Redes", "6.5", "7.5", "7.0", "76%", "Aprovado"),
            ("Algoritmos", "8.0", "-", "8.0", "92%", "Em curso"),
        ]

        for n in notas:
            linha = tk.Frame(cont, bg=BRANCO,
                             highlightbackground=CINZA_CLARO,
                             highlightthickness=1)
            linha.pack(fill="x")
            cor_status = (VERDE_SUCESSO if n[5] == "Aprovado"
                          else AZUL_PRIMARIO)
            for i, valor in enumerate(n):
                fg = cor_status if i == 5 else PRETO_TEXTO
                peso = "bold" if i == 5 else "normal"
                tk.Label(linha, text=valor,
                         font=(FONTE_TEXTO, 10, peso),
                         fg=fg, bg=BRANCO,
                         padx=22, pady=12).pack(side="left", expand=True)

    def _mostrar_mensagens(self):
        self._titulo_secao("Mensagens", "Comunicados da instituicao")

        cont = tk.Frame(self.area_central, bg=BRANCO_GELO)
        cont.pack(fill="both", expand=True, padx=30, pady=10)

        msgs = [
            ("Prof. Carlos", "Material da prova de quinta-feira",
             "Pessoal, segue o material atualizado para a prova...",
             "ha 2h", AZUL_PRIMARIO),
            ("Coordenacao", "Reuniao de turma",
             "Lembrem-se da reuniao na proxima semana...",
             "ha 1d", VERDE_SUCESSO),
            ("Secretaria", "Renovacao de matricula",
             "O periodo de renovacao comeca em 01/07...",
             "ha 3d", LARANJA_ALERTA),
        ]

        for autor, titulo, prev, tempo, cor in msgs:
            card = tk.Frame(cont, bg=BRANCO,
                            highlightbackground=CINZA_CLARO,
                            highlightthickness=1, padx=20, pady=14)
            card.pack(fill="x", pady=4)

            topo = tk.Frame(card, bg=BRANCO)
            topo.pack(fill="x")

            tk.Label(topo, text=f"● {autor}",
                     font=(FONTE_TEXTO, 11, "bold"),
                     fg=cor, bg=BRANCO).pack(side="left")
            tk.Label(topo, text=tempo,
                     font=(FONTE_TEXTO, 9),
                     fg=CINZA_MEDIO, bg=BRANCO).pack(side="right")

            tk.Label(card, text=titulo,
                     font=(FONTE_TEXTO, 11, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(anchor="w", pady=(4, 2))
            tk.Label(card, text=prev,
                     font=(FONTE_TEXTO, 9),
                     fg=CINZA_ESCURO, bg=BRANCO,
                     wraplength=900, justify="left").pack(anchor="w")

    def _mostrar_certificados(self):
        self._titulo_secao("Certificados", "Seus certificados e declaracoes")

        grid = tk.Frame(self.area_central, bg=BRANCO_GELO)
        grid.pack(fill="x", padx=30, pady=10)

        certificados = [
            ("Workshop Python", "60h", "15/03/2025", VERDE_SUCESSO),
            ("Excel Avancado", "40h", "28/02/2025", AZUL_PRIMARIO),
            ("Lideranca Tech", "20h", "10/01/2025", ROXO_DESTAQUE),
        ]

        for i, (nome, horas, data, cor) in enumerate(certificados):
            card = tk.Frame(grid, bg=BRANCO,
                            highlightbackground=CINZA_CLARO,
                            highlightthickness=1, padx=20, pady=20)
            card.grid(row=0, column=i, padx=8, sticky="nsew")

            tk.Label(card, text="🏆", font=("Segoe UI Emoji", 36),
                     bg=BRANCO, fg=cor).pack()
            tk.Label(card, text=nome,
                     font=(FONTE_TEXTO, 11, "bold"),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(pady=(8, 2))
            tk.Label(card, text=f"⏱ {horas} • Concluido em {data}",
                     font=(FONTE_TEXTO, 9),
                     fg=CINZA_ESCURO, bg=BRANCO).pack(pady=(0, 12))
            BotaoModerno(card, texto="📥 Baixar PDF",
                         comando=lambda n=nome: Notificacao.sucesso(
                             self, f"Certificado de {n} baixado!"),
                         largura=160, altura=34,
                         cor_normal=cor, cor_hover=cor,
                         fonte_tamanho=9,
                         cor_fundo=BRANCO).pack()

    def _mostrar_financeiro(self):
        self._titulo_secao("Financeiro", "Mensalidades e pagamentos")

        cont = tk.Frame(self.area_central, bg=BRANCO,
                        highlightbackground=CINZA_CLARO,
                        highlightthickness=1)
        cont.pack(fill="both", expand=True, padx=30, pady=10)

        # Resumo
        resumo = tk.Frame(cont, bg=BRANCO_GELO, padx=30, pady=20)
        resumo.pack(fill="x")

        for titulo, valor, cor in [
            ("Total pago", "R$ 2.400,00", VERDE_SUCESSO),
            ("Pendente", "R$ 400,00", LARANJA_ALERTA),
            ("Proxima fatura", "10/07/2025", AZUL_PRIMARIO),
        ]:
            box = tk.Frame(resumo, bg=BRANCO, padx=20, pady=14,
                           highlightbackground=CINZA_CLARO,
                           highlightthickness=1)
            box.pack(side="left", padx=4, fill="x", expand=True)
            tk.Label(box, text=titulo, font=(FONTE_TEXTO, 9, "bold"),
                     fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
            tk.Label(box, text=valor, font=(FONTE_TITULO, 16, "bold"),
                     fg=cor, bg=BRANCO).pack(anchor="w")

        # Tabela
        header = tk.Frame(cont, bg=AZUL_PRIMARIO)
        header.pack(fill="x", pady=(20, 0))
        for col in ["Mes", "Vencimento", "Valor", "Status"]:
            tk.Label(header, text=col, font=(FONTE_TEXTO, 10, "bold"),
                     fg=BRANCO, bg=AZUL_PRIMARIO,
                     padx=22, pady=10).pack(side="left", expand=True)

        for mes, venc, valor, status in [
            ("Marco/25", "10/03/2025", "R$ 400,00", "Pago"),
            ("Abril/25", "10/04/2025", "R$ 400,00", "Pago"),
            ("Maio/25", "10/05/2025", "R$ 400,00", "Pago"),
            ("Junho/25", "10/06/2025", "R$ 400,00", "Pago"),
            ("Julho/25", "10/07/2025", "R$ 400,00", "Pendente"),
        ]:
            linha = tk.Frame(cont, bg=BRANCO,
                             highlightbackground=CINZA_CLARO,
                             highlightthickness=1)
            linha.pack(fill="x")
            cor_st = VERDE_SUCESSO if status == "Pago" else LARANJA_ALERTA
            for i, val in enumerate([mes, venc, valor, status]):
                tk.Label(linha, text=val,
                         font=(FONTE_TEXTO, 10,
                               "bold" if i == 3 else "normal"),
                         fg=cor_st if i == 3 else PRETO_TEXTO,
                         bg=BRANCO,
                         padx=22, pady=12).pack(side="left", expand=True)

    # ============ SAIR ============
    def _sair(self):
        controlador_autenticacao.encerrar_sessao()
        Notificacao.info(self, "Sessao encerrada. Ate logo!")
        self.after(800, self._fechar_e_voltar)

    def _fechar_e_voltar(self):
        try:
            if self.master_ref:
                self.master_ref.deiconify()
        except tk.TclError:
            pass
        self.destroy()
        # Se nao tinha master, abre nova pagina inicial
        if not self.master_ref:
            from app.visao.tela_pagina_inicial import TelaPaginaInicial
            TelaPaginaInicial().mainloop()

    def _ao_fechar(self):
        self._sair()
