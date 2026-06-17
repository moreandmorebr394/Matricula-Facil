"""
Modelo de Turmas - CRUD na tabela turmas.
"""
from banco_de_dados.conexao import obter_conexao, obter_cursor


def inserir_turma(dados):
    campos = [
        "nome_turma", "curso", "professor", "horario", "sala",
        "data_inicio", "data_fim", "capacidade_maxima",
        "alunos_matriculados", "status"
    ]
    valores = tuple(dados.get(c, None) for c in campos)
    placeholders = ",".join(["%s"] * len(campos))
    sql = f"INSERT INTO turmas ({','.join(campos)}) VALUES ({placeholders})"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        novo_id = cursor.lastrowid
        cursor.close()
    return novo_id


def listar_turmas():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute("SELECT * FROM turmas ORDER BY id DESC")
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def obter_turma(turma_id):
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(f"SELECT * FROM turmas WHERE id = %s", (turma_id,))
        resultado = cursor.fetchone()
        cursor.close()
    if resultado and not isinstance(resultado, dict):
        resultado = dict(resultado)
    return resultado


def atualizar_turma(turma_id, dados):
    if not dados:
        return
    campos = list(dados.keys())
    set_clausula = ", ".join([f"{c} = %s" for c in campos])
    valores = tuple(dados[c] for c in campos) + (turma_id,)
    sql = f"UPDATE turmas SET {set_clausula} WHERE id = %s"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        cursor.close()


def excluir_turma(turma_id):
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(f"DELETE FROM turmas WHERE id = %s", (turma_id,))
        cursor.close()


def total_turmas():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute("SELECT COUNT(*) FROM turmas")
        resultado = cursor.fetchone()
        cursor.close()
    return resultado[0] if resultado else 0
