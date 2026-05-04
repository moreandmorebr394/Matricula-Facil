"""
componentes/header.py — Barra superior com notificações e perfil
"""

import tkinter as tk
from utils.tema import *


class Header(tk.Frame):
    def __init__(self, pai, titulo_pagina="Dashboard",
                 subtitulo="", **kwargs):
        super().__init__(pai, bg=BRANCO,
                         highlightbackground=CINZA_BORDA,
                         highlightthickness=1,
                         height=ALTURA_HEADER, **kwargs)
        self.pack_propagate(False)
        self._construir(titulo_pagina, subtitulo)
        self._notif_count = 3

    def _construir(self, titulo, subtitulo):
        # ─ Esquerda: breadcrumb / título ─
        esq = tk.Frame(self, bg=BRANCO)
        esq.pack(side="left", fill="y", padx=20)

        self._lbl_titulo = tk.Label(
            esq, text=titulo,
            font=("Segoe UI", 15, "bold"),
            fg=TEXTO_HEADER, bg=BRANCO)
        self._lbl_titulo.pack(anchor="w", pady=(10, 0))

        if subtitulo:
            partes = subtitulo.split(" / ")
            f_bread = tk.Frame(esq, bg=BRANCO)
            f_bread.pack(anchor="w")
            for i, p in enumerate(partes):
                cor = CINZA_TEXTO if i < len(partes)-1 else AZUL_PRIMARIO
                tk.Label(f_bread, text=p, font=FONTE_PEQUENA,
                         fg=cor, bg=BRANCO).pack(side="left")
                if i < len(partes)-1:
                    tk.Label(f_bread, text=" › ", font=FONTE_PEQUENA,
                             fg=CINZA_TEXTO, bg=BRANCO).pack(side="left")

        # ─ Direita: notificações + perfil ─
        dir_ = tk.Frame(self, bg=BRANCO)
        dir_.pack(side="right", fill="y", padx=20)

        # Notificações
        f_notif = tk.Frame(dir_, bg=BRANCO, cursor="hand2")
        f_notif.pack(side="left", pady=12, padx=(0, 16))
        c = tk.Canvas(f_notif, width=36, height=36,
                      bg=BRANCO, highlightthickness=0)
        c.pack()
        c.create_oval(2, 2, 34, 34, fill="#EBF0FB", outline="")
        c.create_text(18, 18, text="🔔", font=("Segoe UI", 13))
        c.create_oval(22, 4, 34, 16, fill=VERMELHO, outline=BRANCO, width=1)
        c.create_text(28, 10, text="3", font=("Segoe UI", 7, "bold"),
                      fill=BRANCO)

        # Separador
        tk.Frame(dir_, bg=CINZA_BORDA, width=1).pack(side="left",
                                                      fill="y",
                                                      pady=12)

        # Perfil
        f_perfil = tk.Frame(dir_, bg=BRANCO, cursor="hand2", padx=12)
        f_perfil.pack(side="left", fill="y")

        # Avatar
        c2 = tk.Canvas(f_perfil, width=34, height=34,
                       bg=BRANCO, highlightthickness=0)
        c2.pack(side="left", pady=12)
        c2.create_oval(1, 1, 33, 33, fill=AZUL_PRIMARIO, outline="")
        c2.create_text(17, 17, text="AD", font=("Segoe UI", 10, "bold"),
                       fill=BRANCO)

        txt = tk.Frame(f_perfil, bg=BRANCO)
        txt.pack(side="left", padx=(8, 4), fill="y")
        tk.Label(txt, text="Administrador",
                 font=FONTE_NORMAL_B,
                 fg=TEXTO_HEADER, bg=BRANCO).pack(anchor="w", pady=(13, 0))
        tk.Label(txt, text="admin@sistemafacil.com",
                 font=FONTE_PEQUENA,
                 fg=CINZA_TEXTO, bg=BRANCO).pack(anchor="w")

        tk.Label(f_perfil, text="▾",
                 font=FONTE_NORMAL, fg=CINZA_TEXTO,
                 bg=BRANCO).pack(side="left")
