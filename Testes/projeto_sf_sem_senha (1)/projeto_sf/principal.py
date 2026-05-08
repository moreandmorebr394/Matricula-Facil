"""
Sistema Fácil (SF) - Sistema de Gestão Educacional
Arquivo principal de execução

Para executar:
    python principal.py

Requisitos:
    - Python 3.10+
    - MySQL Workbench / WampServer rodando
    - Pacotes em requirements.txt instalados
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox

# Garante que o diretório do projeto esteja no caminho de imports
DIRETORIO_PROJETO = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_PROJETO not in sys.path:
    sys.path.insert(0, DIRETORIO_PROJETO)

from banco_de_dados.inicializador import inicializar_banco_de_dados
from telas.tela_login import TelaLogin
from utilitarios.sessao import GerenciadorSessao


def principal():
    """Inicia a aplicação."""
    # Tenta inicializar o banco. Se falhar, exibe alerta mas mantém modo offline.
    sucesso, mensagem = inicializar_banco_de_dados()
    if not sucesso:
        raiz_temp = tk.Tk()
        raiz_temp.withdraw()
        messagebox.showwarning(
            "Banco de Dados",
            (
                "Não foi possível conectar ao MySQL.\n\n"
                f"Detalhes: {mensagem}\n\n"
                "Verifique se o WampServer está ativo e o MySQL "
                "está rodando na porta 3306.\n\n"
                "O sistema iniciará em modo offline (dados em "
                "memória) para fins de demonstração."
            ),
        )
        raiz_temp.destroy()

    sessao = GerenciadorSessao()
    aplicacao = TelaLogin(sessao=sessao)
    aplicacao.executar()


if __name__ == "__main__":
    principal()
