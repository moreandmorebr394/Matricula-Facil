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
    Uso:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            ...
    """
    conexao = mysql.connector.connect(**CONFIG_MYSQL)
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
