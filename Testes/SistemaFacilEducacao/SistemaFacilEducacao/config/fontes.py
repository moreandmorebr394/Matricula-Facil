"""Tipografia padronizada do sistema.

Usa fontes profissionais do tipo sans-serif (sem italico).
A familia padrao tenta usar Segoe UI (Windows) / Inter / Calibri.
Nada de fontes genericas como Times ou Comic Sans.
"""

import tkinter.font as tkfont


def familia_disponivel():
    """Retorna a primeira familia disponivel da lista de preferencia."""
    preferidas = [
        "Segoe UI",
        "Inter",
        "SF Pro Display",
        "Calibri",
        "Helvetica Neue",
        "Arial",
        "DejaVu Sans",
        "Liberation Sans",
    ]
    try:
        familias = set(tkfont.families())
    except Exception:
        familias = set()
    for nome in preferidas:
        if nome in familias:
            return nome
    return "TkDefaultFont"


class Fontes:
    FAMILIA = "Segoe UI"  # ajustado em tempo de execucao por aplicar()

    # Titulos
    TITULO_GIGANTE = ("Segoe UI", 28, "bold")
    TITULO_GRANDE = ("Segoe UI", 22, "bold")
    TITULO = ("Segoe UI", 16, "bold")
    TITULO_CARD = ("Segoe UI", 14, "bold")
    SUBTITULO = ("Segoe UI", 12, "bold")

    # Corpo
    CORPO_GRANDE = ("Segoe UI", 12)
    CORPO = ("Segoe UI", 11)
    CORPO_NEGRITO = ("Segoe UI", 11, "bold")
    PEQUENO = ("Segoe UI", 10)
    PEQUENO_NEGRITO = ("Segoe UI", 10, "bold")
    MICRO = ("Segoe UI", 9)
    MICRO_NEGRITO = ("Segoe UI", 9, "bold")

    # Especiais
    BADGE = ("Segoe UI", 9, "bold")
    BOTAO = ("Segoe UI", 11, "bold")
    LABEL_INPUT = ("Segoe UI", 10)
    LOGO_TEXTO = ("Segoe UI", 14, "bold")
    LOGO_SUBTEXTO = ("Segoe UI", 9)
    NUMERO_GRANDE = ("Segoe UI", 26, "bold")
    NUMERO_MEDIO = ("Segoe UI", 18, "bold")
    SIDEBAR_ITEM = ("Segoe UI", 11)
    PERCENTUAL = ("Segoe UI", 11, "bold")

    @classmethod
    def aplicar(cls):
        """Detecta a familia disponivel e atualiza todas as constantes."""
        familia = familia_disponivel()
        cls.FAMILIA = familia
        atributos = [
            "TITULO_GIGANTE", "TITULO_GRANDE", "TITULO", "TITULO_CARD", "SUBTITULO",
            "CORPO_GRANDE", "CORPO", "CORPO_NEGRITO",
            "PEQUENO", "PEQUENO_NEGRITO", "MICRO", "MICRO_NEGRITO",
            "BADGE", "BOTAO", "LABEL_INPUT",
            "LOGO_TEXTO", "LOGO_SUBTEXTO",
            "NUMERO_GRANDE", "NUMERO_MEDIO",
            "SIDEBAR_ITEM", "PERCENTUAL",
        ]
        for atributo in atributos:
            valor = getattr(cls, atributo)
            novo = (familia,) + valor[1:]
            setattr(cls, atributo, novo)
        return familia
