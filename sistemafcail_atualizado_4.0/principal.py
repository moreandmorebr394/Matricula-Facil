"""
Sistema Facil (SF) - Sistema de Gestao Educacional
Arquivo principal de entrada do sistema.

Para rodar: python principal.py

Requisitos:
- Python 3.9+
- MySQL/WampServer rodando
- Bibliotecas: ver requisitos.txt
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

# Adiciona a raiz do projeto ao path para imports
RAIZ_PROJETO = os.path.dirname(os.path.abspath(__file__))
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from banco_de_dados.inicializar import inicializar_banco
from app.visao.tela_carregamento import TelaCarregamento
from app.visao.tela_pagina_inicial import TelaPaginaInicial


def iniciar_aplicacao():
    """Inicializa o banco de dados e abre a pagina inicial do sistema."""
    # 1. Abre a tela de carregamento estetica (Splash Screen)
    splash = TelaCarregamento()
    splash.mainloop()

    # 2. Inicializa o banco de dados
    try:
        inicializar_banco()
    except Exception as erro:
        # Mostra erro amigavel se o banco falhar (WampServer desligado, etc)
        raiz_erro = tk.Tk()
        raiz_erro.withdraw()
        messagebox.showerror(
            "Erro de Conexao com o Banco",
            "Nao foi possivel conectar ao MySQL.\n\n"
            f"Detalhe: {erro}\n\n"
            "Verifique se o WampServer esta rodando e se as credenciais "
            "em banco_de_dados/conexao.py estao corretas.\n\n"
            "O sistema sera aberto em modo offline (algumas funcoes podem nao funcionar)."
        )
        raiz_erro.destroy()

    # Inicia a tela inicial (vitrine para visitantes)
    app = TelaPaginaInicial()
    app.mainloop()


if __name__ == "__main__":
    iniciar_aplicacao()
