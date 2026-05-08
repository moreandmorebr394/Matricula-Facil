"""
Camada de conexão com o banco de dados.

Tenta conectar ao MySQL (WampServer / MySQL Workbench).
Caso o MySQL não esteja disponível, faz fallback automático para
um banco SQLite local em `banco_de_dados/sf_local.db`, para que o
sistema continue plenamente funcional em modo demonstração.
"""
import os
import sqlite3

try:
    import mysql.connector
    from mysql.connector import Error as ErroMySQL
    _TEM_MYSQL = True
except ImportError:
    mysql = None
    ErroMySQL = Exception
    _TEM_MYSQL = False

from configuracoes_admin import configuracao_banco as cfg


# ---------------------------------------------------------------------
# Adaptador para tornar SQLite e MySQL transparentes para o código
# ---------------------------------------------------------------------
class AdaptadorBanco:
    """Adapta SQLite/MySQL para uma interface comum.

    Métodos:
        executar(sql, parametros=None)             -> insere/atualiza/deleta
        consultar(sql, parametros=None)            -> retorna lista de dicts
        consultar_um(sql, parametros=None)         -> retorna um dict ou None
        executar_muitos(sql, lista_parametros)     -> bulk
        ultimo_id()                                -> último id inserido
        fechar()
    """

    PLACEHOLDER = "?"  # SQLite usa '?', MySQL usa '%s' - será substituído

    def __init__(self, conexao, tipo: str):
        self._conexao = conexao
        self.tipo = tipo  # 'mysql' ou 'sqlite'
        if tipo == "mysql":
            self.PLACEHOLDER = "%s"
        else:
            self.PLACEHOLDER = "?"
        self._ultimo_id = None

    def _adaptar_sql(self, sql: str) -> str:
        """Converte os placeholders ? para o estilo do BD ativo."""
        if self.tipo == "mysql":
            return sql.replace("?", "%s")
        return sql

    def executar(self, sql: str, parametros: tuple = None):
        cursor = self._cursor()
        try:
            cursor.execute(self._adaptar_sql(sql), parametros or ())
            self._conexao.commit()
            self._ultimo_id = (
                cursor.lastrowid if hasattr(cursor, "lastrowid") else None
            )
            return cursor.rowcount
        finally:
            cursor.close()

    def executar_muitos(self, sql: str, lista_parametros):
        cursor = self._cursor()
        try:
            cursor.executemany(self._adaptar_sql(sql), lista_parametros)
            self._conexao.commit()
            return cursor.rowcount
        finally:
            cursor.close()

    def consultar(self, sql: str, parametros: tuple = None):
        cursor = self._cursor(dicionario=True)
        try:
            cursor.execute(self._adaptar_sql(sql), parametros or ())
            linhas = cursor.fetchall()
            if self.tipo == "sqlite":
                return [dict(row) for row in linhas]
            return list(linhas)
        finally:
            cursor.close()

    def consultar_um(self, sql: str, parametros: tuple = None):
        resultados = self.consultar(sql, parametros)
        return resultados[0] if resultados else None

    def ultimo_id(self):
        return self._ultimo_id

    def fechar(self):
        try:
            self._conexao.close()
        except Exception:
            pass

    def _cursor(self, dicionario: bool = False):
        if self.tipo == "mysql":
            return self._conexao.cursor(dictionary=dicionario)
        # SQLite
        if dicionario:
            self._conexao.row_factory = sqlite3.Row
        else:
            self._conexao.row_factory = None
        return self._conexao.cursor()


# ---------------------------------------------------------------------
# Estado global de conexão (singleton simples)
# ---------------------------------------------------------------------
_INSTANCIA: AdaptadorBanco | None = None
_TIPO_USADO: str = "indefinido"


def _conectar_mysql() -> AdaptadorBanco | None:
    if not _TEM_MYSQL:
        return None
    try:
        conexao = mysql.connector.connect(
            host=cfg.HOST_BANCO,
            port=cfg.PORTA_BANCO,
            user=cfg.USUARIO_BANCO,
            password=cfg.SENHA_BANCO,
            database=cfg.NOME_BANCO,
            charset=cfg.CHARSET_BANCO,
            connection_timeout=cfg.TIMEOUT_CONEXAO,
            autocommit=False,
        )
        return AdaptadorBanco(conexao, "mysql")
    except ErroMySQL:
        return None


def _conectar_sqlite() -> AdaptadorBanco:
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(diretorio, "sf_local.db")
    conexao = sqlite3.connect(caminho, check_same_thread=False)
    conexao.execute("PRAGMA foreign_keys = ON;")
    return AdaptadorBanco(conexao, "sqlite")


def obter_conexao() -> AdaptadorBanco:
    """Retorna a instância única de conexão."""
    global _INSTANCIA, _TIPO_USADO
    if _INSTANCIA is not None:
        return _INSTANCIA

    instancia = _conectar_mysql()
    if instancia is None:
        instancia = _conectar_sqlite()
        _TIPO_USADO = "sqlite"
    else:
        _TIPO_USADO = "mysql"

    _INSTANCIA = instancia
    return _INSTANCIA


def tipo_banco_ativo() -> str:
    return _TIPO_USADO


def encerrar_conexao():
    global _INSTANCIA
    if _INSTANCIA is not None:
        _INSTANCIA.fechar()
        _INSTANCIA = None
