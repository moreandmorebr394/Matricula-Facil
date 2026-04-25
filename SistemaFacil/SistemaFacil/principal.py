# ============================================================
# principal.py — Aplicação Principal do Sistema Fácil
# ============================================================
# 
# COMO RODAR:
#   1. Instale as dependências:
#      pip install Pillow
#
#   2. Execute:
#      python principal.py
#
# ============================================================

import tkinter as tk
from tkinter import font as tkfont
import sys
import os
import math

# Garantir que o diretório do projeto esteja no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from configuracoes import *
from componentes.logo import carregar_logo
from componentes.animacoes import AnimacaoCursor
from telas.registro import TelaRegistro
from telas.login import TelaLogin


class SistemaFacilApp:
    """Aplicação principal do Sistema Fácil."""

    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Sistema Fácil — Plataforma Educacional")
        self.janela.configure(bg=AZUL_ESCURO)

        # ── Dimensões e posição centralizada ──
        self.janela.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}")
        self.janela.minsize(900, 600)
        self._centralizar_janela()

        # ── Ícone (tenta usar a logo) ──
        try:
            caminho_assets = os.path.join(os.path.dirname(__file__), "assets")
            from PIL import Image, ImageTk
            ico_img = Image.open(os.path.join(caminho_assets, "logo_sf.png"))
            ico_img = ico_img.resize((32, 32), Image.LANCZOS)
            self.icone = ImageTk.PhotoImage(ico_img)
            self.janela.iconphoto(True, self.icone)
        except Exception:
            pass

        # ── Fontes ──
        self._configurar_fontes()

        # ── Carregar logo ──
        caminho_assets = os.path.join(os.path.dirname(__file__), "assets")
        try:
            self.logo_img = carregar_logo(caminho_assets, tamanho=60)
        except Exception:
            self.logo_img = None

        # ── Container principal ──
        self.container = tk.Frame(self.janela, bg=AZUL_ESCURO)
        self.container.pack(fill="both", expand=True)

        # ── Cursor animado global ──
        self._setup_cursor_animation()

        # ── Telas ──
        self.tela_atual = None
        self.telas = {}

        # ── Animação de entrada (fade-in) ──
        self.janela.attributes("-alpha", 0.0)
        self._fade_in(0.0)

        # Iniciar na tela de login
        self.janela.after(300, lambda: self.mostrar_tela("login"))

    def _centralizar_janela(self):
        self.janela.update_idletasks()
        tela_l = self.janela.winfo_screenwidth()
        tela_a = self.janela.winfo_screenheight()
        x = (tela_l - LARGURA_JANELA) // 2
        y = (tela_a - ALTURA_JANELA) // 2
        self.janela.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{x}+{y}")

    def _configurar_fontes(self):
        """Configura fontes profissionais disponíveis no sistema."""
        fontes_disponiveis = tkfont.families()
        
        # Ordem de preferência de fontes profissionais
        preferencias = [
            "Segoe UI", "SF Pro Display", "Helvetica Neue",
            "Helvetica", "Arial", "DejaVu Sans"
        ]
        
        global FONTE_FAMILIA
        for fonte in preferencias:
            if fonte in fontes_disponiveis:
                FONTE_FAMILIA = fonte
                break

    def _setup_cursor_animation(self):
        """Overlay transparente para animação do cursor."""
        self.cursor_canvas = tk.Canvas(
            self.janela, bg=AZUL_ESCURO,
            highlightthickness=0
        )
        # O canvas do cursor fica como overlay
        # Não empacota para não interferir no layout
        # Em vez disso, usamos bind na janela principal
        self._cursor_pontos = []
        self._cursor_ids = []
        self._num_pontos = 8

        self.janela.bind("<Motion>", self._cursor_mover)

    def _cursor_mover(self, evento):
        """Efeito de cursor com pontos que seguem o mouse."""
        # Gerenciado pelas telas individuais com seus canvas
        pass

    def _fade_in(self, alpha):
        """Animação de fade-in na abertura."""
        if alpha < 1.0:
            alpha += 0.05
            self.janela.attributes("-alpha", min(alpha, 1.0))
            self.janela.after(20, lambda: self._fade_in(alpha))
        else:
            self.janela.attributes("-alpha", 1.0)

    def mostrar_tela(self, nome):
        """Alterna entre telas com transição suave."""
        # Destruir tela atual
        if self.tela_atual:
            if hasattr(self.tela_atual, "destruir_animacoes"):
                self.tela_atual.destruir_animacoes()
            self.tela_atual.destroy()

        # Criar nova tela
        if nome == "registro":
            self.tela_atual = TelaRegistro(self.container, self, self.logo_img)
        elif nome == "login":
            self.tela_atual = TelaLogin(self.container, self, self.logo_img)
        else:
            return

        # Transição com fade
        self.tela_atual.pack(fill="both", expand=True)
        self._animar_entrada()

    def _animar_entrada(self):
        """Animação de entrada da tela (slide suave)."""
        # Efeito visual sutil na transição
        if self.tela_atual:
            self.tela_atual.update_idletasks()

    def executar(self):
        """Inicia o loop principal da aplicação."""
        print("=" * 50)
        print("  Sistema Fácil — Plataforma Educacional")
        print("  Versão 1.0")
        print("=" * 50)
        print(f"  Fonte: {FONTE_FAMILIA}")
        print(f"  Resolução: {LARGURA_JANELA}x{ALTURA_JANELA}")
        print("=" * 50)
        self.janela.mainloop()


# ── Ponto de entrada ─────────────────────────────────────────
if __name__ == "__main__":
    app = SistemaFacilApp()
    app.executar()
