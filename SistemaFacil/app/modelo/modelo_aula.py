"""
Modelo de Aulas - CRUD na tabela aulas.
"""
from banco_de_dados.conexao import obter_conexao, obter_cursor, usando_mysql


def _p():
    return "%s" if usando_mysql() else "?"


def inserir_aula(dados):
    p = _p()
    campos = [
        "turma_id", "titulo", "descricao", "data_aula",
        "horario_inicio", "horario_fim", "professor", "sala", "status"
    ]
    valores = tuple(dados.get(c, None) for c in campos)
    placeholders = ",".join([p] * len(campos))
    sql = f"INSERT INTO aulas ({','.join(campos)}) VALUES ({placeholders})"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        novo_id = cursor.lastrowid
        cursor.close()
    return novo_id


def listar_aulas():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute("SELECT * FROM aulas ORDER BY id DESC")
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def obter_aula(aula_id):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(f"SELECT * FROM aulas WHERE id = {p}", (aula_id,))
        resultado = cursor.fetchone()
        cursor.close()
    if resultado and not isinstance(resultado, dict):
        resultado = dict(resultado)
    return resultado


def atualizar_aula(aula_id, dados):
    p = _p()
    if not dados:
        return
    campos = list(dados.keys())
    set_clausula = ", ".join([f"{c} = {p}" for c in campos])
    valores = tuple(dados[c] for c in campos) + (aula_id,)
    sql = f"UPDATE aulas SET {set_clausula} WHERE id = {p}"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        cursor.close()


def excluir_aula(aula_id):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(f"DELETE FROM aulas WHERE id = {p}", (aula_id,))
        cursor.close()


def total_aulas():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute("SELECT COUNT(*) FROM aulas")
        resultado = cursor.fetchone()
        cursor.close()
    return resultado[0] if resultado else 0
