"""
Sistema de mascaras automaticas para campos de entrada.

Aplica mascaras como CPF (000.000.000-00), data (DD/MM/AAAA),
telefone ((00) 00000-0000) automaticamente conforme o usuario digita.
"""
import re


def aplicar_mascara_cpf(entry_widget):
    """
    Aplica mascara de CPF (000.000.000-00) em um Entry Tkinter.
    """
    def ao_digitar(evento):
        # Ignora teclas de navegacao
        if evento.keysym in ("Left", "Right", "Up", "Down", "Tab",
                             "BackSpace", "Delete", "Home", "End"):
            return

        valor = entry_widget.get()
        digitos = re.sub(r"\D", "", valor)[:11]  # max 11 digitos

        formatado = ""
        for i, c in enumerate(digitos):
            if i == 3 or i == 6:
                formatado += "."
            elif i == 9:
                formatado += "-"
            formatado += c

        if formatado != valor:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, formatado)
            entry_widget.icursor("end")

    entry_widget.bind("<KeyRelease>", ao_digitar)


def aplicar_mascara_data(entry_widget):
    """
    Aplica mascara de data (DD/MM/AAAA) em um Entry Tkinter.
    """
    def ao_digitar(evento):
        if evento.keysym in ("Left", "Right", "Up", "Down", "Tab",
                             "BackSpace", "Delete", "Home", "End"):
            return

        valor = entry_widget.get()
        digitos = re.sub(r"\D", "", valor)[:8]  # max 8 digitos

        formatado = ""
        for i, c in enumerate(digitos):
            if i == 2 or i == 4:
                formatado += "/"
            formatado += c

        if formatado != valor:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, formatado)
            entry_widget.icursor("end")

    entry_widget.bind("<KeyRelease>", ao_digitar)


def aplicar_mascara_telefone(entry_widget):
    """
    Aplica mascara de telefone ((00) 00000-0000) em um Entry Tkinter.
    """
    def ao_digitar(evento):
        if evento.keysym in ("Left", "Right", "Up", "Down", "Tab",
                             "BackSpace", "Delete", "Home", "End"):
            return

        valor = entry_widget.get()
        digitos = re.sub(r"\D", "", valor)[:11]  # max 11 digitos

        formatado = ""
        for i, c in enumerate(digitos):
            if i == 0:
                formatado += "("
            elif i == 2:
                formatado += ") "
            elif i == 7 and len(digitos) == 11:
                formatado += "-"
            elif i == 6 and len(digitos) <= 10:
                formatado += "-"
            formatado += c

        if formatado != valor:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, formatado)
            entry_widget.icursor("end")

    entry_widget.bind("<KeyRelease>", ao_digitar)


def aplicar_mascara_dinheiro(entry_widget):
    """
    Aplica mascara de dinheiro (R$ 0,00).
    """
    def ao_digitar(evento):
        if evento.keysym in ("Left", "Right", "Up", "Down", "Tab",
                             "BackSpace", "Delete", "Home", "End"):
            return

        valor = entry_widget.get()
        digitos = re.sub(r"\D", "", valor)
        if not digitos:
            return

        # Converte para float (centavos)
        numero = int(digitos) / 100
        formatado = f"R$ {numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        if formatado != valor:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, formatado)
            entry_widget.icursor("end")

    entry_widget.bind("<KeyRelease>", ao_digitar)
