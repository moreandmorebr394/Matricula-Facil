"""
Modelo de Venda.

Camada Model: CRUD de vendas vinculadas a leads.
"""
from banco_de_dados.conexao import obter_conexao


class ModeloVenda:

    @staticmethod
    def inserir(dados: dict) -> int:
        bd = obter_conexao()
        bd.executar(
            "INSERT INTO vendas "
            "(lead_id, valor, forma_pagamento, parcelas, status_pagamento, "
            " captador, observacoes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                int(dados.get("lead_id") or 0),
                float(dados.get("valor") or 0),
                dados.get("forma_pagamento") or "",
                int(dados.get("parcelas") or 1),
                dados.get("status_pagamento") or "NAO_PAGO",
                dados.get("captador") or "",
                dados.get("observacoes") or "",
            ),
        )
        return bd.ultimo_id()

    @staticmethod
    def listar() -> list:
        bd = obter_conexao()
        return bd.consultar(
            "SELECT v.*, l.nome_completo AS aluno_nome "
            "FROM vendas v "
            "LEFT JOIN leads l ON l.id = v.lead_id "
            "ORDER BY v.criado_em DESC"
        )

    @staticmethod
    def buscar_por_id(id_venda: int) -> dict | None:
        bd = obter_conexao()
        return bd.consultar_um(
            "SELECT v.*, l.nome_completo AS aluno_nome "
            "FROM vendas v LEFT JOIN leads l ON l.id = v.lead_id "
            "WHERE v.id = ?",
            (id_venda,),
        )

    @staticmethod
    def atualizar(id_venda: int, dados: dict) -> bool:
        bd = obter_conexao()
        bd.executar(
            "UPDATE vendas SET valor = ?, forma_pagamento = ?, parcelas = ?, "
            "status_pagamento = ?, captador = ?, observacoes = ? WHERE id = ?",
            (
                float(dados.get("valor") or 0),
                dados.get("forma_pagamento") or "",
                int(dados.get("parcelas") or 1),
                dados.get("status_pagamento") or "NAO_PAGO",
                dados.get("captador") or "",
                dados.get("observacoes") or "",
                id_venda,
            ),
        )
        return True

    @staticmethod
    def excluir(id_venda: int) -> bool:
        bd = obter_conexao()
        bd.executar("DELETE FROM vendas WHERE id = ?", (id_venda,))
        return True

    @staticmethod
    def faturamento_total() -> float:
        bd = obter_conexao()
        r = bd.consultar_um(
            "SELECT COALESCE(SUM(valor), 0) AS total FROM vendas "
            "WHERE status_pagamento = 'PAGO'"
        )
        return float(r["total"]) if r else 0.0

    @staticmethod
    def total_vendas() -> int:
        bd = obter_conexao()
        r = bd.consultar_um("SELECT COUNT(*) AS c FROM vendas")
        return r["c"] if r else 0
