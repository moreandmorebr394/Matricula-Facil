"""Header (cabecalho) do sistema.

Contem:
- Titulo e breadcrumb da pagina atual
- Botao de notificacoes (com badge de quantidade nao lida)
- Avatar e dados do administrador (clicavel)
"""
import tkinter as tk
from typing import Callable, Optional

from config.configuracoes import Configuracoes
from config.cores import Cores
from config.fontes import Fontes
from .botao import BotaoIcone


class Cabecalho(tk.Frame):
    def __init__(self, master, ao_clicar_notificacoes: Callable,
                 ao_clicar_perfil: Callable):
        super().__init__(
            master, bg=Cores.HEADER_FUNDO,
            height=Configuracoes.ALTURA_HEADER,
        )
        self.pack_propagate(False)
        self.ao_clicar_notificacoes = ao_clicar_notificacoes
        self.ao_clicar_perfil = ao_clicar_perfil

        # Linha de borda inferior
        borda = tk.Frame(self, bg=Cores.HEADER_BORDA, height=1)
        borda.pack(side="bottom", fill="x")

        # ----- LADO ESQUERDO -----
        esquerdo = tk.Frame(self, bg=Cores.HEADER_FUNDO)
        esquerdo.pack(side="left", fill="y", padx=24)

        self.titulo_label = tk.Label(
            esquerdo, text="Cadastro do Aluno (Lead)",
            bg=Cores.HEADER_FUNDO, fg=Cores.TEXTO_PRIMARIO,
            font=Fontes.TITULO_GRANDE,
        )
        self.titulo_label.pack(anchor="w", pady=(14, 0))

        self.breadcrumb_label = tk.Label(
            esquerdo, text="Leads  ›  Novo Cadastro",
            bg=Cores.HEADER_FUNDO, fg=Cores.TEXTO_TERCIARIO,
            font=Fontes.PEQUENO,
        )
        self.breadcrumb_label.pack(anchor="w")

        # ----- LADO DIREITO -----
        direito = tk.Frame(self, bg=Cores.HEADER_FUNDO)
        direito.pack(side="right", fill="y", padx=24)

        self.botao_notificacao = BotaoIcone(
            direito, simbolo="🔔",
            comando=self.ao_clicar_notificacoes,
            tamanho=40,
            badge_texto="3",
            cor_badge="#ef4444",
        )
        self.botao_notificacao.pack(side="right", padx=(0, 14), pady=15)

        # Bloco do perfil
        self.bloco_perfil = tk.Frame(direito, bg=Cores.HEADER_FUNDO, cursor="hand2")
        self.bloco_perfil.pack(side="right", pady=15)

        avatar = tk.Canvas(
            self.bloco_perfil, width=40, height=40,
            highlightthickness=0, bd=0, bg=Cores.HEADER_FUNDO,
        )
        avatar.pack(side="left", padx=(0, 10))
        avatar.create_oval(2, 2, 38, 38, fill=Cores.BOTAO_PRIMARIO, outline="")
        avatar.create_text(20, 21, text="A", fill=Cores.BRANCO,
                           font=(Fontes.FAMILIA, 16, "bold"))

        textos = tk.Frame(self.bloco_perfil, bg=Cores.HEADER_FUNDO)
        textos.pack(side="left")
        tk.Label(
            textos, text=Configuracoes.USUARIO_NOME,
            bg=Cores.HEADER_FUNDO, fg=Cores.TEXTO_PRIMARIO,
            font=Fontes.CORPO_NEGRITO,
        ).pack(anchor="w")
        tk.Label(
            textos, text=Configuracoes.USUARIO_EMAIL,
            bg=Cores.HEADER_FUNDO, fg=Cores.TEXTO_TERCIARIO,
            font=Fontes.MICRO,
        ).pack(anchor="w")

        seta = tk.Label(
            self.bloco_perfil, text="▾",
            bg=Cores.HEADER_FUNDO, fg=Cores.TEXTO_TERCIARIO,
            font=(Fontes.FAMILIA, 12),
        )
        seta.pack(side="left", padx=(8, 0))

        # Vincular clique em todos os filhos para abrir perfil
        for w in (self.bloco_perfil, avatar, *textos.winfo_children(),
                  *self.bloco_perfil.winfo_children(), seta):
            w.bind("<Button-1>", lambda _e: self.ao_clicar_perfil())

    def atualizar_titulo(self, titulo: str, breadcrumb: str = ""):
        self.titulo_label.configure(text=titulo)
        self.breadcrumb_label.configure(text=breadcrumb)

    def atualizar_quantidade_notificacoes(self, quantidade: int):
        texto = str(quantidade) if quantidade > 0 else None
        self.botao_notificacao.atualizar_badge(texto)
