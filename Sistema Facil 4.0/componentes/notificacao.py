"""
Sistema de notificacoes (Toast) que aparecem no canto e desaparecem
automaticamente em 2 segundos.

Uso:
    Notificacao.sucesso(janela, "Salvo com sucesso!")
    Notificacao.erro(janela, "Erro ao salvar")
    Notificacao.aviso(janela, "Atencao!")
    Notificacao.info(janela, "Informacao")
"""
import tkinter as tk
from componentes.cores import (
    BRANCO, PRETO_TEXTO, VERDE_SUCESSO, VERMELHO_ERRO,
    LARANJA_ALERTA, AZUL_PRIMARIO, FONTE_TEXTO
)


class Notificacao:
    """Toast de notificacao auto-destrutivo."""

    _ativos = []  # rastreia toasts ativos para empilhar

    CORES = {
        "sucesso": VERDE_SUCESSO,
        "erro": VERMELHO_ERRO,
        "aviso": LARANJA_ALERTA,
        "info": AZUL_PRIMARIO,
    }

    ICONES = {
        "sucesso": "✓",
        "erro": "✕",
        "aviso": "⚠",
        "info": "ℹ",
    }

    def __init__(self, master, mensagem, tipo="info", duracao_ms=2000, comando_desfazer=None):
        self.master = master
        self.mensagem = mensagem
        self.tipo = tipo
        self.comando_desfazer = comando_desfazer
        # Se tem comando desfazer, deixa mais tempo na tela
        self.duracao_ms = max(duracao_ms, 5000) if comando_desfazer else duracao_ms

        # Janela toplevel sem decoracao
        self.toplevel = tk.Toplevel(master)
        self.toplevel.overrideredirect(True)
        self.toplevel.attributes("-topmost", True)
        try:
            self.toplevel.attributes("-alpha", 0.0)
        except tk.TclError:
            pass

        cor_borda = self.CORES.get(tipo, AZUL_PRIMARIO)
        icone = self.ICONES.get(tipo, "ℹ")

        # Frame principal
        frame = tk.Frame(self.toplevel, bg=BRANCO, bd=0,
                         highlightbackground=cor_borda, highlightthickness=2)
        frame.pack(fill="both", expand=True)

        # Barra colorida lateral
        barra = tk.Frame(frame, bg=cor_borda, width=6)
        barra.pack(side="left", fill="y")

        # Conteudo
        conteudo = tk.Frame(frame, bg=BRANCO)
        conteudo.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        # Icone + mensagem
        linha = tk.Frame(conteudo, bg=BRANCO)
        linha.pack(fill="x")

        tk.Label(
            linha, text=icone,
            font=(FONTE_TEXTO, 16, "bold"),
            fg=cor_borda, bg=BRANCO
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            linha, text=mensagem,
            font=(FONTE_TEXTO, 10, "bold"),
            fg=PRETO_TEXTO, bg=BRANCO,
            wraplength=220 if comando_desfazer else 280, justify="left"
        ).pack(side="left", fill="x", expand=True)

        if comando_desfazer:
            # Botao Desfazer
            lbl_desfazer = tk.Label(
                linha, text="Desfazer",
                font=(FONTE_TEXTO, 10, "bold", "underline"),
                fg=AZUL_PRIMARIO, bg=BRANCO, cursor="hand2"
            )
            lbl_desfazer.pack(side="right", padx=(10, 0))

            def ao_clicar_desfazer(e):
                self._iniciar_destruir()
                try:
                    comando_desfazer()
                except Exception as ex:
                    print("Erro ao desfazer exclusao:", ex)

            lbl_desfazer.bind("<Button-1>", ao_clicar_desfazer)

        # Posiciona no canto superior direito do master
        self._posicionar()

        # Adiciona aos ativos
        Notificacao._ativos.append(self)

        # Animacao fade-in
        self._fade_in(0.0)

        # Auto-destruir
        self.toplevel.after(self.duracao_ms, self._iniciar_destruir)

        # Permite clicar para fechar (apenas se nao clicar no desfazer)
        for w in (frame, conteudo, linha):
            w.bind("<Button-1>", lambda e: self._iniciar_destruir())

    def _posicionar(self):
        """Posiciona o toast no canto superior direito do master."""
        self.toplevel.update_idletasks()
        try:
            self.master.update_idletasks()
            mx = self.master.winfo_rootx()
            my = self.master.winfo_rooty()
            mw = self.master.winfo_width()
        except tk.TclError:
            mx, my, mw = 0, 0, 1200

        largura = 380 if self.comando_desfazer else 320
        # Indice (para empilhar)
        indice = max(0, len(Notificacao._ativos))
        offset_y = my + 20 + (indice * 80)
        offset_x = mx + mw - (largura + 40)

        self.toplevel.geometry(f"{largura}x70+{offset_x}+{offset_y}")

    def _fade_in(self, alfa):
        try:
            self.toplevel.attributes("-alpha", alfa)
            if alfa < 1.0:
                self.toplevel.after(20, lambda: self._fade_in(min(1.0, alfa + 0.1)))
        except tk.TclError:
            pass

    def _iniciar_destruir(self):
        self._fade_out(1.0)

    def _fade_out(self, alfa):
        try:
            self.toplevel.attributes("-alpha", alfa)
            if alfa > 0:
                self.toplevel.after(20, lambda: self._fade_out(max(0, alfa - 0.1)))
            else:
                self._destruir()
        except tk.TclError:
            self._destruir()

    def _destruir(self):
        try:
            if self in Notificacao._ativos:
                Notificacao._ativos.remove(self)
            self.toplevel.destroy()
        except tk.TclError:
            pass

    # Metodos de classe para uso facil
    @classmethod
    def sucesso(cls, master, mensagem, comando_desfazer=None):
        return cls(master, mensagem, "sucesso", comando_desfazer=comando_desfazer)

    @classmethod
    def erro(cls, master, mensagem, comando_desfazer=None):
        return cls(master, mensagem, "erro", comando_desfazer=comando_desfazer)

    @classmethod
    def aviso(cls, master, mensagem, comando_desfazer=None):
        return cls(master, mensagem, "aviso", comando_desfazer=comando_desfazer)

    @classmethod
    def info(cls, master, mensagem, comando_desfazer=None):
        return cls(master, mensagem, "info", comando_desfazer=comando_desfazer)
