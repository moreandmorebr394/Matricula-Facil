"""
Conexao com o banco de dados MySQL (WampServer).

Configure as credenciais abaixo conforme seu ambiente WampServer.
A senha padrao do MySQL no WampServer e vazia ("").
"""
from contextlib import contextmanager

# ==============================================================
# CONFIGURACAO DO BANCO MySQL (WampServer)
# ==============================================================
# Edite estes valores conforme seu ambiente:
CONFIG_MYSQL = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",          # WampServer padrao = senha vazia
    "database": "sistema_facil",
    "charset": "utf8mb4",
    "autocommit": False
}

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    _mysql_modulo_ok = True
except ImportError:
    raise ImportError("mysql-connector-python nao esta instalado. "
                      "Instale com: pip install mysql-connector-python")


@contextmanager
def obter_conexao():
    """
    Context manager que devolve uma conexao com o banco MySQL.
    Se o banco de dados nao existir, ele e criado automaticamente.
    Uso:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            ...
    """
    config_sem_db = CONFIG_MYSQL.copy()
    db_nome = config_sem_db.pop("database", "sistema_facil")
    
    # Conecta primeiro sem especificar o banco para garantir a existencia do schema
    conexao = mysql.connector.connect(**config_sem_db)
    cursor = conexao.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {db_nome} "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.close()
    
    # Seleciona o banco de dados
    conexao.database = db_nome
    
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        if conexao.is_connected():
            conexao.close()


def obter_cursor(conexao, dicionario=True):
    """Retorna um cursor do MySQL."""
    return conexao.cursor(dictionary=dicionario)
