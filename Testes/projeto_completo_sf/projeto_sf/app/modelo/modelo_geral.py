"""
Modelo de Frequencia (presencas/faltas) e Configuracoes do sistema.
"""
from banco_de_dados.conexao import obter_conexao, obter_cursor, usando_mysql


def _p():
    return "%s" if usando_mysql() else "?"


# ============ FREQUENCIA ============

def registrar_frequencia(dados):
    p = _p()
    campos = ["aula_id", "aluno_nome", "presente", "justificativa", "data_registro"]
    valores = tuple(dados.get(c, None) for c in campos)
    placeholders = ",".join([p] * len(campos))
    sql = f"INSERT INTO frequencia ({','.join(campos)}) VALUES ({placeholders})"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        novo_id = cursor.lastrowid
        cursor.close()
    return novo_id


def listar_frequencia():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute("SELECT * FROM frequencia ORDER BY id DESC")
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def excluir_frequencia(freq_id):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(f"DELETE FROM frequencia WHERE id = {p}", (freq_id,))
        cursor.close()


# ============ CONFIGURACOES ============

def obter_configuracao(chave, padrao=""):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(
            f"SELECT valor FROM configuracoes WHERE chave = {p}",
            (chave,)
        )
        resultado = cursor.fetchone()
        cursor.close()
    if not resultado:
        return padrao
    if isinstance(resultado, dict):
        return resultado.get("valor") or padrao
    return resultado["valor"] if resultado["valor"] else padrao


def salvar_configuracao(chave, valor):
    """Insere ou atualiza uma configuracao."""
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        # Verifica se existe
        cursor.execute(
            f"SELECT id FROM configuracoes WHERE chave = {p}", (chave,)
        )
        existe = cursor.fetchone()
        if existe:
            cursor.execute(
                f"UPDATE configuracoes SET valor = {p} WHERE chave = {p}",
                (valor, chave)
            )
        else:
            cursor.execute(
                f"INSERT INTO configuracoes (chave, valor) VALUES ({p}, {p})",
                (chave, valor)
            )
        cursor.close()


def listar_configuracoes():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute("SELECT chave, valor, descricao FROM configuracoes")
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


# ============ NOTIFICACOES ============

def criar_notificacao(titulo, mensagem, tipo="info", destinatario=None):
    p = _p()
    sql = (f"INSERT INTO notificacoes (titulo, mensagem, tipo, destinatario) "
           f"VALUES ({p}, {p}, {p}, {p})")
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, (titulo, mensagem, tipo, destinatario))
        cursor.close()


def listar_notificacoes(apenas_nao_lidas=False, limite=20):
    sql = "SELECT * FROM notificacoes"
    if apenas_nao_lidas:
        sql += " WHERE lida = 0"
    sql += f" ORDER BY id DESC LIMIT {int(limite)}"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(sql)
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def marcar_notificacao_lida(notif_id):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(
            f"UPDATE notificacoes SET lida = 1 WHERE id = {p}", (notif_id,)
        )
        cursor.close()


def contar_notificacoes_nao_lidas():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute("SELECT COUNT(*) FROM notificacoes WHERE lida = 0")
        resultado = cursor.fetchone()
        cursor.close()
    return resultado[0] if resultado else 0
