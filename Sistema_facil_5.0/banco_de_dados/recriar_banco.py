"""
Script para recriar o banco de dados MySQL 'sistema_facil'.
ATENCAO: Isso deletara todas as tabelas e dados existentes no banco e as recriara do zero
com o esquema atualizado correto compativel com o Sistema Facil 2.0.
"""
import sys
import os

# Adiciona a raiz do projeto ao python path para garantir imports
RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

import mysql.connector
from banco_de_dados.conexao import CONFIG_MYSQL
from banco_de_dados.inicializar import inicializar_banco

def recriar_banco():
    print("Iniciando processo de recriacao do banco de dados...")
    config_sem_db = CONFIG_MYSQL.copy()
    db_nome = config_sem_db.pop("database", "sistema_facil")
    
    try:
        # Conecta sem banco de dados para poder deletar o banco atual
        conexao = mysql.connector.connect(**config_sem_db)
        cursor = conexao.cursor()
        
        # Deleta o banco antigo se existir
        cursor.execute(f"DROP DATABASE IF EXISTS {db_nome}")
        print(f"[OK] Banco de dados antigo '{db_nome}' deletado (se existia).")
        
        cursor.close()
        conexao.close()
        
        # Agora inicializa o banco novamente (isso cria o banco e as tabelas com o novo esquema)
        print("Criando o banco de dados e tabelas com o esquema correto...")
        inicializar_banco()
        print("\n[SUCESSO] O banco de dados foi recriado com sucesso com todas as colunas corretas!")
        print("Agora voce ja pode iniciar o aplicativo principal.py sem o erro 'field list'.")
        
    except Exception as e:
        print(f"\n[ERRO] Ocorreu uma falha ao recriar o banco de dados: {e}")
        print("Certifique-se de que o WampServer/MySQL esta rodando localmente.")

if __name__ == "__main__":
    recriar_banco()
