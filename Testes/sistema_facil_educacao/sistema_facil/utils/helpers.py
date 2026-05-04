"""
utils/helpers.py — Funções auxiliares e componentes visuais reutilizáveis
"""

import tkinter as tk
from tkinter import ttk
from utils.tema import *


def card(pai, **kwargs):
    """Frame com visual de card (fundo branco, borda suave)."""
    bd_cor  = kwargs.pop("bd_cor", CINZA_BORDA)
    bg      = kwargs.pop("bg", CINZA_CARD)
    pad     = kwargs.pop("pad", PAD_CARD)
    f = tk.Frame(pai, bg=bg,
                 highlightbackground=bd_cor,
                 highlightthickness=1,
                 **kwargs)
    return f


def label_titulo(pai, texto, **kwargs):
    bg = kwargs.pop("bg", pai.cget("bg"))
    return tk.Label(pai, text=texto, font=FONTE_SUBTITULO,
                    fg=TEXTO_HEADER, bg=bg, **kwargs)


def label_secao(pai, texto, **kwargs):
    bg = kwargs.pop("bg", pai.cget("bg"))
    return tk.Label(pai, text=texto, font=FONTE_SECAO,
                    fg=TEXTO_HEADER, bg=bg, **kwargs)


def label_normal(pai, texto, **kwargs):
    bg = kwargs.pop("bg", pai.cget("bg"))
    return tk.Label(pai, text=texto, font=FONTE_NORMAL,
                    fg=TEXTO_LABEL, bg=bg, **kwargs)


def label_pequena(pai, texto, **kwargs):
    bg = kwargs.pop("bg", pai.cget("bg"))
    return tk.Label(pai, text=texto, font=FONTE_PEQUENA,
                    fg=CINZA_TEXTO, bg=bg, **kwargs)


def entrada(pai, placeholder="", width=20, **kwargs):
    """Campo de entrada estilizado."""
    var = tk.StringVar(value=placeholder)
    e = tk.Entry(pai, textvariable=var, font=FONTE_NORMAL,
                 bg=BRANCO, fg=CINZA_ESCURO,
                 relief="flat",
                 highlightbackground=CINZA_BORDA,
                 highlightcolor=AZUL_PRIMARIO,
                 highlightthickness=1,
                 insertbackground=AZUL_PRIMARIO,
                 width=width, **kwargs)
    e._placeholder = placeholder
    e._var = var

    def on_focus_in(evt):
        if var.get() == placeholder:
            var.set("")
            e.config(fg=CINZA_ESCURO)
    def on_focus_out(evt):
        if not var.get():
            var.set(placeholder)
            e.config(fg="#AABBD4")

    e.config(fg="#AABBD4")
    e.bind("<FocusIn>",  on_focus_in)
    e.bind("<FocusOut>", on_focus_out)
    return e


def botao_primario(pai, texto, comando=None, **kwargs):
    width = kwargs.pop("width", 14)
    btn = tk.Button(pai, text=texto, font=FONTE_NORMAL_B,
                    bg=AZUL_PRIMARIO, fg=BRANCO,
                    relief="flat", cursor="hand2",
                    activebackground="#1440C0",
                    activeforeground=BRANCO,
                    padx=12, pady=6,
                    width=width,
                    command=comando, **kwargs)
    return btn


def botao_secundario(pai, texto, comando=None, **kwargs):
    width = kwargs.pop("width", 12)
    btn = tk.Button(pai, text=texto, font=FONTE_NORMAL_B,
                    bg="#E2E8F0", fg=CINZA_ESCURO,
                    relief="flat", cursor="hand2",
                    activebackground="#CBD5E0",
                    activeforeground=CINZA_ESCURO,
                    padx=12, pady=6,
                    width=width,
                    command=comando, **kwargs)
    return btn


def badge(pai, texto, cor_bg=AZUL_PRIMARIO, cor_fg=BRANCO, **kwargs):
    bg_pai = kwargs.pop("bg_pai", pai.cget("bg"))
    f = tk.Frame(pai, bg=cor_bg, padx=6, pady=2)
    tk.Label(f, text=texto, font=FONTE_PEQUENA_B,
             bg=cor_bg, fg=cor_fg).pack()
    return f


def separador(pai, cor=CINZA_BORDA, **kwargs):
    return tk.Frame(pai, bg=cor, height=1, **kwargs)


def combo(pai, opcoes, width=18, **kwargs):
    style = ttk.Style()
    style.configure("Custom.TCombobox",
                    fieldbackground=BRANCO,
                    background=BRANCO,
                    foreground=CINZA_ESCURO,
                    arrowcolor=AZUL_PRIMARIO)
    cb = ttk.Combobox(pai, values=opcoes, width=width,
                      font=FONTE_NORMAL,
                      state="readonly",
                      style="Custom.TCombobox",
                      **kwargs)
    if opcoes:
        cb.current(0)
    return cb
