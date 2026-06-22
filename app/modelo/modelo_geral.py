"""
Modelo de Frequencia (presencas/faltas) e Configuracoes do sistema.
"""
from banco_de_dados.conexao import obter_conexao, obter_cursor


# ============ FREQUENCIA ============

def registrar_frequencia(dados):
    campos = ["aula_id", "aluno_nome", "presente", "justificativa", "data_registro"]
    valores = tuple(dados.get(c, None) for c in campos)
    placeholders = ",".join(["%s"] * len(campos))
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
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(f"DELETE FROM frequencia WHERE id = %s", (freq_id,))
        cursor.close()


# ============ CONFIGURACOES ============

def obter_configuracao(chave, padrao=""):
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(
            "SELECT valor FROM configuracoes WHERE chave = %s",
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
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        # Verifica se existe
        cursor.execute(
            "SELECT id FROM configuracoes WHERE chave = %s", (chave,)
        )
        existe = cursor.fetchone()
        if existe:
            cursor.execute(
                "UPDATE configuracoes SET valor = %s WHERE chave = %s",
                (valor, chave)
            )
        else:
            cursor.execute(
                "INSERT INTO configuracoes (chave, valor) VALUES (%s, %s)",
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
    sql = ("INSERT INTO notificacoes (titulo, mensagem, tipo, destinatario) "
           "VALUES (%s, %s, %s, %s)")
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
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(
            "UPDATE notificacoes SET lida = 1 WHERE id = %s", (notif_id,)
        )
        cursor.close()


def contar_notificacoes_nao_lidas():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute("SELECT COUNT(*) FROM notificacoes WHERE lida = 0")
        resultado = cursor.fetchone()
        cursor.close()
    return resultado[0] if resultado else 0


def limpar_notificacoes():
    """Exclui todas as notificacoes do banco de dados."""
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute("DELETE FROM notificacoes")
        cursor.close()

