"""
Modelo de Pagamentos - CRUD na tabela pagamentos.
"""
from banco_de_dados.conexao import obter_conexao, obter_cursor, usando_mysql


def _p():
    return "%s" if usando_mysql() else "?"


def inserir_pagamento(dados):
    p = _p()
    campos = [
        "venda_id", "nome_aluno", "valor", "data_pagamento",
        "forma_pagamento", "parcela_numero", "status", "observacoes"
    ]
    valores = tuple(dados.get(c, None) for c in campos)
    placeholders = ",".join([p] * len(campos))
    sql = f"INSERT INTO pagamentos ({','.join(campos)}) VALUES ({placeholders})"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        novo_id = cursor.lastrowid
        cursor.close()
    return novo_id


def listar_pagamentos():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute("SELECT * FROM pagamentos ORDER BY id DESC")
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def obter_pagamento(pagamento_id):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(f"SELECT * FROM pagamentos WHERE id = {p}", (pagamento_id,))
        resultado = cursor.fetchone()
        cursor.close()
    if resultado and not isinstance(resultado, dict):
        resultado = dict(resultado)
    return resultado


def atualizar_pagamento(pagamento_id, dados):
    p = _p()
    if not dados:
        return
    campos = list(dados.keys())
    set_clausula = ", ".join([f"{c} = {p}" for c in campos])
    valores = tuple(dados[c] for c in campos) + (pagamento_id,)
    sql = f"UPDATE pagamentos SET {set_clausula} WHERE id = {p}"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        cursor.close()


def excluir_pagamento(pagamento_id):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(f"DELETE FROM pagamentos WHERE id = {p}", (pagamento_id,))
        cursor.close()


def total_recebido():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(
            "SELECT COALESCE(SUM(valor), 0) FROM pagamentos WHERE status = 'Pago'"
        )
        resultado = cursor.fetchone()
        cursor.close()
    return float(resultado[0]) if resultado and resultado[0] else 0.0
