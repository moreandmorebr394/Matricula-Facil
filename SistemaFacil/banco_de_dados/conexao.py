"""
Conexao com o banco de dados MySQL (WampServer).

Configure as credenciais abaixo conforme seu ambiente WampServer.
A senha padrao do MySQL no WampServer e vazia ("").

Em caso de falha de conexao MySQL, o sistema usa SQLite como fallback
(arquivo local) para nao travar a aplicacao.
"""
import os
import sqlite3
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

# Caminho do banco SQLite (fallback offline)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_SQLITE = os.path.join(RAIZ, "banco_de_dados", "sistema_facil.db")

# Flag interna - setada na primeira tentativa
_USAR_MYSQL = None
_mysql_disponivel = False

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    _mysql_modulo_ok = True
except ImportError:
    _mysql_modulo_ok = False


def testar_mysql():
    """Tenta conectar no MySQL e retorna True se funcionar."""
    global _USAR_MYSQL, _mysql_disponivel

    if not _mysql_modulo_ok:
        _USAR_MYSQL = False
        return False

    try:
        conexao_teste = mysql.connector.connect(
            host=CONFIG_MYSQL["host"],
            port=CONFIG_MYSQL["port"],
            user=CONFIG_MYSQL["user"],
            password=CONFIG_MYSQL["password"],
            connection_timeout=3
        )
        if conexao_teste.is_connected():
            cursor = conexao_teste.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {CONFIG_MYSQL['database']} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            conexao_teste.commit()
            cursor.close()
            conexao_teste.close()
            _USAR_MYSQL = True
            _mysql_disponivel = True
            return True
    except Exception:
        pass

    _USAR_MYSQL = False
    return False


def usando_mysql():
    """Retorna True se o sistema estiver usando MySQL."""
    if _USAR_MYSQL is None:
        testar_mysql()
    return bool(_USAR_MYSQL)


@contextmanager
def obter_conexao():
    """
    Context manager que devolve uma conexao com o banco.
    Uso:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            ...
    """
    if usando_mysql():
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
    else:
        # Fallback SQLite
        conexao = sqlite3.connect(CAMINHO_SQLITE)
        conexao.row_factory = sqlite3.Row
        try:
            yield conexao
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()


def obter_cursor(conexao, dicionario=True):
    """Retorna um cursor adequado ao banco em uso."""
    if usando_mysql():
        return conexao.cursor(dictionary=dicionario)
    return conexao.cursor()


def converter_query(query):
    """
    Converte uma query MySQL (placeholders %s) para SQLite (placeholders ?).
    Tambem ajusta tipos especificos do MySQL.
    """
    if usando_mysql():
        return query
    # SQLite usa ? em vez de %s
    query_sqlite = query.replace("%s", "?")
    # Ajustes de tipo (compatibilidade)
    query_sqlite = query_sqlite.replace("AUTO_INCREMENT", "AUTOINCREMENT")
    query_sqlite = query_sqlite.replace("INT PRIMARY KEY AUTOINCREMENT",
                                        "INTEGER PRIMARY KEY AUTOINCREMENT")
    query_sqlite = query_sqlite.replace("DATETIME", "TEXT")
    query_sqlite = query_sqlite.replace("ENGINE=InnoDB", "")
    query_sqlite = query_sqlite.replace("DEFAULT CHARSET=utf8mb4", "")
    return query_sqlite
