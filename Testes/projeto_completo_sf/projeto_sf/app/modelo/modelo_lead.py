"""
Modelo de Lead/Aluno (CRM educacional).
Operacoes CRUD na tabela leads.
"""
from banco_de_dados.conexao import obter_conexao, obter_cursor, usando_mysql


def _p():
    return "%s" if usando_mysql() else "?"


def inserir_lead(dados):
    """
    Insere um novo lead. Retorna o ID criado.

    dados: dict com keys: nome_completo, data_nascimento, cpf, email, telefone,
                          endereco, cidade, estado, curso_interesse,
                          como_conheceu, captador, observacoes, status
    """
    p = _p()
    campos = [
        "nome_completo", "data_nascimento", "cpf", "email", "telefone",
        "endereco", "cidade", "estado", "curso_interesse",
        "como_conheceu", "captador", "observacoes", "status"
    ]
    valores = tuple(dados.get(c, "") for c in campos)
    placeholders = ",".join([p] * len(campos))
    sql = f"INSERT INTO leads ({','.join(campos)}) VALUES ({placeholders})"

    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        novo_id = cursor.lastrowid
        cursor.close()
    return novo_id


def listar_leads(limite=None, filtro_status=None):
    """Lista todos os leads (mais recentes primeiro)."""
    p = _p()
    sql = "SELECT * FROM leads"
    params = []
    if filtro_status:
        sql += f" WHERE status = {p}"
        params.append(filtro_status)
    sql += " ORDER BY id DESC"
    if limite:
        sql += f" LIMIT {int(limite)}"

    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(sql, tuple(params))
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def obter_lead(lead_id):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(f"SELECT * FROM leads WHERE id = {p}", (lead_id,))
        resultado = cursor.fetchone()
        cursor.close()
    if resultado and not isinstance(resultado, dict):
        resultado = dict(resultado)
    return resultado


def atualizar_lead(lead_id, dados):
    """Atualiza os campos de um lead."""
    p = _p()
    if not dados:
        return
    campos = list(dados.keys())
    set_clausula = ", ".join([f"{c} = {p}" for c in campos])
    valores = tuple(dados[c] for c in campos) + (lead_id,)
    sql = f"UPDATE leads SET {set_clausula} WHERE id = {p}"

    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, valores)
        cursor.close()


def excluir_lead(lead_id):
    p = _p()
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(f"DELETE FROM leads WHERE id = {p}", (lead_id,))
        cursor.close()


def contar_leads_por_status():
    """Retorna contagem de leads agrupados por status."""
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(
            "SELECT status, COUNT(*) as total FROM leads GROUP BY status"
        )
        resultados = cursor.fetchall()
        cursor.close()
    return {
        (r["status"] if isinstance(r, dict) else r["status"]): (
            r["total"] if isinstance(r, dict) else r["total"]
        )
        for r in resultados
    }


def contar_leads_por_origem():
    """Retorna contagem de leads agrupados por origem."""
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(
            "SELECT como_conheceu, COUNT(*) as total FROM leads "
            "WHERE como_conheceu IS NOT NULL AND como_conheceu != '' "
            "GROUP BY como_conheceu"
        )
        resultados = cursor.fetchall()
        cursor.close()
    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def total_leads():
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute("SELECT COUNT(*) FROM leads")
        resultado = cursor.fetchone()
        cursor.close()
    return resultado[0] if resultado else 0
