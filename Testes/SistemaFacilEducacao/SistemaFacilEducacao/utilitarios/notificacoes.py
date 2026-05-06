"""Notificacoes temporarias estilo "toast" no canto da tela."""
import tkinter as tk
from typing import List

from config.cores import Cores
from config.fontes import Fontes


class GerenciadorNotificacoes:
    """Mostra mensagens flutuantes no canto superior direito.

    Uso:
        gerenciador = GerenciadorNotificacoes(janela_raiz)
        gerenciador.mostrar("Lead salvo!", tipo="SUCESSO")
    """

    CORES_FUNDO = {
        "SUCESSO": Cores.NOTIF_SUCESSO_FUNDO,
        "ERRO": Cores.NOTIF_ERRO_FUNDO,
        "INFO": Cores.NOTIF_INFO_FUNDO,
        "AVISO": Cores.NOTIF_AVISO_FUNDO,
    }
    ICONES = {
        "SUCESSO": "✓",
        "ERRO": "✕",
        "INFO": "ℹ",
        "AVISO": "⚠",
    }

    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.toasts_ativos: List[tk.Toplevel] = []

    def mostrar(self, mensagem: str, tipo: str = "INFO",
                duracao_ms: int = 3500, titulo: str = ""):
        toast = tk.Toplevel(self.raiz)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        try:
            toast.attributes("-alpha", 0.0)
        except Exception:
            pass

        cor_fundo = self.CORES_FUNDO.get(tipo, Cores.NOTIF_INFO_FUNDO)
        toast.configure(bg=cor_fundo)

        moldura = tk.Frame(toast, bg=cor_fundo, padx=18, pady=12)
        moldura.pack()

        icone = self.ICONES.get(tipo, "ℹ")
        tk.Label(
            moldura, text=icone, bg=cor_fundo, fg=Cores.NOTIF_TEXTO,
            font=(Fontes.FAMILIA, 18, "bold"),
        ).pack(side="left", padx=(0, 12))

        textos = tk.Frame(moldura, bg=cor_fundo)
        textos.pack(side="left")
        if titulo:
            tk.Label(
                textos, text=titulo, bg=cor_fundo,
                fg=Cores.NOTIF_TEXTO, font=Fontes.CORPO_NEGRITO,
            ).pack(anchor="w")
        tk.Label(
            textos, text=mensagem, bg=cor_fundo, fg=Cores.NOTIF_TEXTO,
            font=Fontes.PEQUENO, justify="left", wraplength=320,
        ).pack(anchor="w")

        # Posicionar no canto superior direito da janela
        self.raiz.update_idletasks()
        x_raiz = self.raiz.winfo_rootx()
        y_raiz = self.raiz.winfo_rooty()
        largura_raiz = self.raiz.winfo_width()
        toast.update_idletasks()
        largura_toast = toast.winfo_width()
        altura_toast = toast.winfo_height()

        # Empilhar abaixo de outros toasts ativos
        deslocamento_y = sum(
            t.winfo_height() + 10 for t in self.toasts_ativos if t.winfo_exists()
        )
        x = x_raiz + largura_raiz - largura_toast - 24
        y = y_raiz + 90 + deslocamento_y
        toast.geometry(f"+{x}+{y}")

        self.toasts_ativos.append(toast)
        self._fade_in(toast, 0.0)
        toast.after(duracao_ms, lambda: self._fade_out(toast))

    def _fade_in(self, toast: tk.Toplevel, alpha: float):
        if not toast.winfo_exists():
            return
        try:
            toast.attributes("-alpha", min(alpha, 0.97))
        except Exception:
            pass
        if alpha < 0.97:
            toast.after(20, lambda: self._fade_in(toast, alpha + 0.12))

    def _fade_out(self, toast: tk.Toplevel, alpha: float = 0.97):
        if not toast.winfo_exists():
            return
        try:
            toast.attributes("-alpha", max(alpha, 0.0))
        except Exception:
            pass
        if alpha > 0.0:
            toast.after(25, lambda: self._fade_out(toast, alpha - 0.12))
        else:
            try:
                toast.destroy()
            except Exception:
                pass
            if toast in self.toasts_ativos:
                self.toasts_ativos.remove(toast)
