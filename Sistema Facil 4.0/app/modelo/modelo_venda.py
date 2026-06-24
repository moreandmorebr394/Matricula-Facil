"""
Modelo de Vendas - CRUD na tabela vendas.
"""
from banco_de_dados.conexao import obter_conexao, obter_cursor


def inserir_venda(dados):
    campos = [
        "lead_id", "nome_aluno", "curso", "valor_total",
        "forma_pagamento", "parcelas", "status_pagamento",
        "vendedor", "observacoes"
    ]
    valores = tuple(dados.get(c, None) for c in campos)
    placeholders = ",".join(["%s"] * len(campos))
    sql = f"INSERT INTO vendas ({','.join(campos)}) VALUES ({placeholders})"

    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        novo_id = cursor.lastrowid
        cursor.close()
    return novo_id


def listar_vendas(limite=None):
    sql = "SELECT * FROM vendas ORDER BY id DESC"
    if limite:
        sql += f" LIMIT {int(limite)}"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(sql)
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def obter_venda(venda_id):
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(f"SELECT * FROM vendas WHERE id = %s", (venda_id,))
        resultado = cursor.fetchone()
        cursor.close()
    if resultado and not isinstance(resultado, dict):
        resultado = dict(resultado)
    return resultado


def atualizar_venda(venda_id, dados):
    if not dados:
        return
    campos = list(dados.keys())
    set_clausula = ", ".join([f"{c} = %s" for c in campos])
    valores = tuple(dados[c] for c in campos) + (venda_id,)
    sql = f"UPDATE vendas SET {set_clausula} WHERE id = %s"
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        cursor.close()


def excluir_venda(venda_id):
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(f"DELETE FROM vendas WHERE id = %s", (venda_id,))
        cursor.close()


def faturamento_total():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(
            "SELECT COALESCE(SUM(valor_total), 0) FROM vendas "
            "WHERE status_pagamento = 'Pago'"
        )
        resultado = cursor.fetchone()
        cursor.close()
    return float(resultado[0]) if resultado and resultado[0] else 0.0


def total_vendas():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute("SELECT COUNT(*) FROM vendas")
        resultado = cursor.fetchone()
        cursor.close()
    return resultado[0] if resultado else 0
