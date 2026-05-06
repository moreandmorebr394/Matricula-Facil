"""Campos de entrada estilizados (label superior + input).

Disponibiliza:
- CampoEntrada: input de texto comum
- CampoSelecao: dropdown (Combobox)
- CampoTextoLongo: textarea (Text)
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from config.cores import Cores
from config.fontes import Fontes


class CampoEntrada(tk.Frame):
    """Campo de texto com label posicionado acima."""

    def __init__(self, master, rotulo: str = "", placeholder: str = "",
                 obrigatorio: bool = False, valor_inicial: str = "",
                 largura: int = 28, **kwargs):
        super().__init__(master, bg=Cores.CARD_FUNDO, **kwargs)

        texto_rotulo = rotulo + (" *" if obrigatorio else "")
        self.label = tk.Label(
            self, text=texto_rotulo, bg=Cores.CARD_FUNDO,
            fg=Cores.TEXTO_LABEL, font=Fontes.LABEL_INPUT, anchor="w",
        )
        self.label.pack(fill="x", anchor="w", pady=(0, 4))

        # Wrapper para simular borda mais espessa quando focado
        self.wrapper = tk.Frame(
            self, bg=Cores.INPUT_BORDA,
            highlightthickness=0, bd=0,
        )
        self.wrapper.pack(fill="x")

        self.entrada = tk.Entry(
            self.wrapper, bd=0, relief="flat",
            bg=Cores.INPUT_FUNDO, fg=Cores.INPUT_TEXTO,
            font=Fontes.CORPO, width=largura, insertbackground=Cores.TEXTO_PRIMARIO,
        )
        self.entrada.pack(fill="x", padx=1, pady=1, ipady=8, ipadx=10)

        self.placeholder = placeholder
        self._mostrando_placeholder = False
        if placeholder and not valor_inicial:
            self._aplicar_placeholder()

        if valor_inicial:
            self.entrada.insert(0, valor_inicial)

        self.entrada.bind("<FocusIn>", self._ao_focar)
        self.entrada.bind("<FocusOut>", self._ao_desfocar)

    def _aplicar_placeholder(self):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, self.placeholder)
        self.entrada.configure(fg=Cores.INPUT_PLACEHOLDER)
        self._mostrando_placeholder = True

    def _ao_focar(self, _e):
        if self._mostrando_placeholder:
            self.entrada.delete(0, "end")
            self.entrada.configure(fg=Cores.INPUT_TEXTO)
            self._mostrando_placeholder = False
        self.wrapper.configure(bg=Cores.INPUT_BORDA_FOCO)

    def _ao_desfocar(self, _e):
        if not self.entrada.get().strip() and self.placeholder:
            self._aplicar_placeholder()
        self.wrapper.configure(bg=Cores.INPUT_BORDA)

    def obter(self) -> str:
        if self._mostrando_placeholder:
            return ""
        return self.entrada.get().strip()

    def definir(self, valor: str):
        self._mostrando_placeholder = False
        self.entrada.configure(fg=Cores.INPUT_TEXTO)
        self.entrada.delete(0, "end")
        self.entrada.insert(0, valor)

    def limpar(self):
        self.entrada.delete(0, "end")
        if self.placeholder:
            self._aplicar_placeholder()


class CampoSelecao(tk.Frame):
    """Dropdown estilizado usando ttk.Combobox."""

    def __init__(self, master, rotulo: str = "", opcoes: Optional[List[str]] = None,
                 obrigatorio: bool = False, valor_inicial: str = "",
                 placeholder: str = "Selecione...", **kwargs):
        super().__init__(master, bg=Cores.CARD_FUNDO, **kwargs)

        texto = rotulo + (" *" if obrigatorio else "")
        tk.Label(
            self, text=texto, bg=Cores.CARD_FUNDO,
            fg=Cores.TEXTO_LABEL, font=Fontes.LABEL_INPUT, anchor="w",
        ).pack(fill="x", anchor="w", pady=(0, 4))

        self.variavel = tk.StringVar(value=valor_inicial or placeholder)
        self.placeholder = placeholder
        self.opcoes = opcoes or []

        estilo = ttk.Style()
        try:
            estilo.theme_use("default")
        except Exception:
            pass
        estilo.configure(
            "Sistema.TCombobox",
            fieldbackground=Cores.INPUT_FUNDO,
            background=Cores.INPUT_FUNDO,
            foreground=Cores.INPUT_TEXTO,
            borderwidth=1,
            relief="flat",
            padding=6,
        )

        self.combo = ttk.Combobox(
            self, textvariable=self.variavel,
            values=self.opcoes, state="readonly",
            font=Fontes.CORPO, style="Sistema.TCombobox",
        )
        self.combo.pack(fill="x", ipady=4)

    def obter(self) -> str:
        valor = self.variavel.get().strip()
        if valor == self.placeholder:
            return ""
        return valor

    def definir(self, valor: str):
        self.variavel.set(valor)


class CampoTextoLongo(tk.Frame):
    """Area de texto multilinha (textarea)."""

    def __init__(self, master, rotulo: str = "", altura: int = 4,
                 placeholder: str = "", obrigatorio: bool = False, **kwargs):
        super().__init__(master, bg=Cores.CARD_FUNDO, **kwargs)
        texto = rotulo + (" *" if obrigatorio else "")
        tk.Label(
            self, text=texto, bg=Cores.CARD_FUNDO,
            fg=Cores.TEXTO_LABEL, font=Fontes.LABEL_INPUT, anchor="w",
        ).pack(fill="x", anchor="w", pady=(0, 4))

        self.wrapper = tk.Frame(self, bg=Cores.INPUT_BORDA)
        self.wrapper.pack(fill="x")

        self.texto = tk.Text(
            self.wrapper, height=altura, bd=0, relief="flat",
            bg=Cores.INPUT_FUNDO, fg=Cores.INPUT_TEXTO,
            font=Fontes.CORPO, wrap="word", padx=10, pady=8,
            insertbackground=Cores.TEXTO_PRIMARIO,
        )
        self.texto.pack(fill="both", padx=1, pady=1)

        self.placeholder = placeholder
        self._mostrando_placeholder = False
        if placeholder:
            self._aplicar_placeholder()

        self.texto.bind("<FocusIn>", self._ao_focar)
        self.texto.bind("<FocusOut>", self._ao_desfocar)

    def _aplicar_placeholder(self):
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", self.placeholder)
        self.texto.configure(fg=Cores.INPUT_PLACEHOLDER)
        self._mostrando_placeholder = True

    def _ao_focar(self, _e):
        if self._mostrando_placeholder:
            self.texto.delete("1.0", "end")
            self.texto.configure(fg=Cores.INPUT_TEXTO)
            self._mostrando_placeholder = False
        self.wrapper.configure(bg=Cores.INPUT_BORDA_FOCO)

    def _ao_desfocar(self, _e):
        if not self.texto.get("1.0", "end").strip() and self.placeholder:
            self._aplicar_placeholder()
        self.wrapper.configure(bg=Cores.INPUT_BORDA)

    def obter(self) -> str:
        if self._mostrando_placeholder:
            return ""
        return self.texto.get("1.0", "end").strip()

    def definir(self, valor: str):
        self._mostrando_placeholder = False
        self.texto.configure(fg=Cores.INPUT_TEXTO)
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", valor)
