"""
Sistema Fácil Educação - CRM de Alunos
Ponto de entrada principal do sistema
"""

import tkinter as tk
from telas.dashboard import TelaDashboard


def main():
    janela = tk.Tk()
    janela.title("Sistema Fácil Educação")
    janela.geometry("1366x768")
    janela.minsize(1200, 700)
    janela.configure(bg="#F0F2F5")

    # Centralizar janela
    janela.update_idletasks()
    w = janela.winfo_width()
    h = janela.winfo_height()
    x = (janela.winfo_screenwidth() // 2) - (w // 2)
    y = (janela.winfo_screenheight() // 2) - (h // 2)
    janela.geometry(f"+{x}+{y}")

    app = TelaDashboard(janela)
    app.pack(fill="both", expand=True)

    janela.mainloop()


if __name__ == "__main__":
    main()
