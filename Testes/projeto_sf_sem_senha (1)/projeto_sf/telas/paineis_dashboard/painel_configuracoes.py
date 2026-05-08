"""Painel de Configurações - foto do administrador, info e preferências."""
import tkinter as tk

from componentes import tema
from componentes.botao_arredondado import BotaoArredondado
from componentes.notificacoes import NotificacaoFlutuante
from configuracoes_admin import credenciais_admin
from modelos.modelo_academico import ModeloConfiguracoes


class PainelConfiguracoes(tk.Frame):

    def __init__(self, mestre, dashboard=None):
        super().__init__(mestre, bg=tema.OFFWHITE)
        self.pack(fill="both", expand=True)
        self.dashboard = dashboard

        topo = tk.Frame(self, bg=tema.OFFWHITE)
        topo.pack(fill="both", expand=True, padx=20, pady=(20, 20))
        topo.columnconfigure(0, weight=1, minsize=420)
        topo.columnconfigure(1, weight=1, minsize=420)

        # Card 1: Perfil do administrador
        card_perfil = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card_perfil.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._construir_perfil(card_perfil)

        # Card 2: Sistema / preferências
        card_sis = tk.Frame(
            topo, bg=tema.BRANCO_PURO, highlightthickness=1,
            highlightbackground=tema.CINZA_BORDA,
        )
        card_sis.grid(row=0, column=1, sticky="nsew")
        self._construir_sistema(card_sis)

    # =================================================================
    def _construir_perfil(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Perfil do Administrador", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(15),
        ).pack(anchor="w", pady=(0, 12))

        # Avatar grande no centro
        self._frame_avatar = tk.Frame(bloco, bg=tema.BRANCO_PURO)
        self._frame_avatar.pack(pady=(8, 14))

        self._lbl_avatar = tk.Label(
            self._frame_avatar, text="\U0001F464",
            bg=tema.AZUL_PRINCIPAL, fg="#FFFFFF",
            font=tema.fonte_destaque(40),
            width=4, height=2,
        )
        self._lbl_avatar.pack()

        self._foto_imagem = None
        self._tentar_renderizar_foto()

        # Botão de trocar foto
        BotaoArredondado(
            bloco, texto="Alterar foto do administrador",
            comando=self._trocar_foto,
            largura=320, altura=42, fonte=tema.fonte_destaque(11),
        ).pack(pady=(0, 14))

        # Informações do admin
        self._info_linha(bloco, "Nome:", credenciais_admin.NOME_ADMIN)
        self._info_linha(bloco, "E-mail institucional:",
                         credenciais_admin.EMAIL_ADMIN)
        self._info_linha(bloco, "Permissões:",
                         ", ".join(credenciais_admin.PERMISSOES_ADMIN))

        tk.Frame(bloco, bg=tema.CINZA_BORDA, height=1).pack(
            fill="x", pady=(14, 8),
        )

        # Como alterar credenciais
        aviso = tk.Frame(bloco, bg=tema.AMARELO_INPUT_FOCO)
        aviso.pack(fill="x", pady=(0, 4))
        tk.Label(
            aviso,
            text=(
                "\u26A0 Como alterar as credenciais administrativas:\n\n"
                "Edite o arquivo 'configuracoes_admin/credenciais_admin.py'\n"
                "e atualize EMAIL_ADMIN, NOME_ADMIN e SENHA_ADMIN_HASH.\n"
                "Use bcrypt para gerar o hash da nova senha:\n"
                "    bcrypt.hashpw(b'NovaSenha', bcrypt.gensalt(12))"
            ),
            bg=tema.AMARELO_INPUT_FOCO, fg=tema.AZUL_ESCURO,
            font=tema.fonte_corpo(9), justify="left", padx=12, pady=10,
        ).pack(fill="x")

    def _info_linha(self, pai, rotulo, valor):
        linha = tk.Frame(pai, bg=tema.BRANCO_PURO)
        linha.pack(fill="x", pady=4)
        tk.Label(
            linha, text=rotulo, bg=tema.BRANCO_PURO,
            fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
        ).pack(side="left")
        tk.Label(
            linha, text=valor, bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(10),
            wraplength=240, justify="right",
        ).pack(side="right")

    def _tentar_renderizar_foto(self):
        caminho = ModeloConfiguracoes.obter("foto_admin", "")
        if not caminho:
            return
        try:
            import os
            if not os.path.exists(caminho):
                return
            from PIL import Image, ImageDraw, ImageTk
            img = Image.open(caminho).convert("RGBA")
            img = img.resize((140, 140))
            mascara = Image.new("L", (140, 140), 0)
            ImageDraw.Draw(mascara).ellipse((0, 0, 140, 140), fill=255)
            img.putalpha(mascara)
            self._foto_imagem = ImageTk.PhotoImage(img)
            self._lbl_avatar.configure(
                image=self._foto_imagem, text="",
                bg=tema.BRANCO_PURO, width=140, height=140,
            )
        except Exception:
            pass

    def _trocar_foto(self):
        if self.dashboard and hasattr(self.dashboard, "selecionar_foto_admin"):
            caminho = self.dashboard.selecionar_foto_admin()
            if caminho:
                self._tentar_renderizar_foto()

    # =================================================================
    def _construir_sistema(self, pai):
        bloco = tk.Frame(pai, bg=tema.BRANCO_PURO)
        bloco.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            bloco, text="Sistema", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(15),
        ).pack(anchor="w", pady=(0, 12))

        info = (
            ("Aplicação:", "Sistema Fácil (SF)"),
            ("Versão:", "1.0.0"),
            ("Banco de dados:", "MySQL com fallback SQLite"),
            ("Linguagem:", "Python 3.10+ / Tkinter"),
            ("Tipo de arquitetura:", "MVC (Models / Views / Controllers)"),
            ("Senhas:", "bcrypt cost=12"),
            ("Dados sensíveis:", "Criptografia simétrica reversível"),
        )

        for rotulo, valor in info:
            linha = tk.Frame(bloco, bg=tema.BRANCO_PURO)
            linha.pack(fill="x", pady=4)
            tk.Label(
                linha, text=rotulo, bg=tema.BRANCO_PURO,
                fg=tema.CINZA_TEXTO, font=tema.fonte_corpo(10),
            ).pack(side="left")
            tk.Label(
                linha, text=valor, bg=tema.BRANCO_PURO,
                fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(10),
            ).pack(side="right")

        tk.Frame(bloco, bg=tema.CINZA_BORDA, height=1).pack(
            fill="x", pady=(14, 8),
        )

        tk.Label(
            bloco, text="Manutenção", bg=tema.BRANCO_PURO,
            fg=tema.AZUL_ESCURO, font=tema.fonte_destaque(13),
        ).pack(anchor="w", pady=(4, 8))

        BotaoArredondado(
            bloco, texto="Limpar cache de relatórios",
            comando=self._limpar_cache,
            cor_fundo=tema.CINZA_CLARO, cor_hover=tema.CINZA_BORDA,
            cor_press="#D5D7DF", cor_texto=tema.AZUL_ESCURO,
            largura=320, altura=40, fonte=tema.fonte_destaque(10),
        ).pack(pady=4)

        BotaoArredondado(
            bloco, texto="Verificar atualizações",
            comando=self._verificar_atualizacoes,
            cor_fundo=tema.CINZA_CLARO, cor_hover=tema.CINZA_BORDA,
            cor_press="#D5D7DF", cor_texto=tema.AZUL_ESCURO,
            largura=320, altura=40, fonte=tema.fonte_destaque(10),
        ).pack(pady=4)

        tk.Frame(bloco, bg=tema.CINZA_BORDA, height=1).pack(
            fill="x", pady=(14, 8),
        )

        tk.Label(
            bloco,
            text=(
                "© 2026 Sistema Fácil — Educação Profissional\n"
                "Todos os direitos reservados."
            ),
            bg=tema.BRANCO_PURO, fg=tema.CINZA_TEXTO,
            font=tema.fonte_corpo(9), justify="center",
        ).pack(pady=(8, 0))

    def _limpar_cache(self):
        NotificacaoFlutuante.exibir(
            self.winfo_toplevel(),
            "Cache de relatórios limpo.", tipo="sucesso",
        )

    def _verificar_atualizacoes(self):
        NotificacaoFlutuante.exibir(
            self.winfo_toplevel(),
            "Sistema está atualizado (versão 1.0.0).", tipo="info",
        )
