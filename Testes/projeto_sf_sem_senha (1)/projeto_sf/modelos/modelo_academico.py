"""
Modelos auxiliares: Turmas, Aulas, Frequência, Pagamentos, Funil, Origem.
"""
from banco_de_dados.conexao import obter_conexao
from utilitarios.geradores import gerar_codigo_turma


# =====================================================================
class ModeloTurma:

    @staticmethod
    def inserir(dados: dict) -> int:
        bd = obter_conexao()
        codigo = dados.get("codigo") or gerar_codigo_turma(
            dados.get("curso", "Turma"),
        )
        bd.executar(
            "INSERT INTO turmas "
            "(codigo, curso, turno, data_inicio, data_fim, capacidade, "
            " professor, sala, ativa) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (
                codigo,
                dados.get("curso", ""),
                dados.get("turno", "MANHA"),
                dados.get("data_inicio", ""),
                dados.get("data_fim", ""),
                int(dados.get("capacidade") or 30),
                dados.get("professor", ""),
                dados.get("sala", ""),
            ),
        )
        return bd.ultimo_id()

    @staticmethod
    def listar() -> list:
        bd = obter_conexao()
        return bd.consultar("SELECT * FROM turmas ORDER BY criado_em DESC")

    @staticmethod
    def atualizar(id_turma: int, dados: dict) -> bool:
        bd = obter_conexao()
        bd.executar(
            "UPDATE turmas SET curso = ?, turno = ?, data_inicio = ?, "
            "data_fim = ?, capacidade = ?, professor = ?, sala = ?, ativa = ? "
            "WHERE id = ?",
            (
                dados.get("curso", ""),
                dados.get("turno", "MANHA"),
                dados.get("data_inicio", ""),
                dados.get("data_fim", ""),
                int(dados.get("capacidade") or 30),
                dados.get("professor", ""),
                dados.get("sala", ""),
                1 if dados.get("ativa", True) else 0,
                id_turma,
            ),
        )
        return True

    @staticmethod
    def excluir(id_turma: int) -> bool:
        bd = obter_conexao()
        bd.executar("DELETE FROM turmas WHERE id = ?", (id_turma,))
        return True

    @staticmethod
    def total() -> int:
        bd = obter_conexao()
        r = bd.consultar_um("SELECT COUNT(*) AS c FROM turmas")
        return r["c"] if r else 0


# =====================================================================
class ModeloAula:

    @staticmethod
    def inserir(dados: dict) -> int:
        bd = obter_conexao()
        bd.executar(
            "INSERT INTO aulas (turma_id, titulo, descricao, data, horario, "
            "professor, realizada) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                int(dados.get("turma_id") or 0),
                dados.get("titulo", ""),
                dados.get("descricao", ""),
                dados.get("data", ""),
                dados.get("horario", ""),
                dados.get("professor", ""),
                1 if dados.get("realizada") else 0,
            ),
        )
        return bd.ultimo_id()

    @staticmethod
    def listar(turma_id: int = None) -> list:
        bd = obter_conexao()
        if turma_id:
            return bd.consultar(
                "SELECT a.*, t.codigo AS turma_codigo "
                "FROM aulas a LEFT JOIN turmas t ON t.id = a.turma_id "
                "WHERE a.turma_id = ? ORDER BY a.data DESC",
                (turma_id,),
            )
        return bd.consultar(
            "SELECT a.*, t.codigo AS turma_codigo "
            "FROM aulas a LEFT JOIN turmas t ON t.id = a.turma_id "
            "ORDER BY a.data DESC"
        )

    @staticmethod
    def atualizar(id_aula: int, dados: dict) -> bool:
        bd = obter_conexao()
        bd.executar(
            "UPDATE aulas SET titulo = ?, descricao = ?, data = ?, "
            "horario = ?, professor = ?, realizada = ? WHERE id = ?",
            (
                dados.get("titulo", ""),
                dados.get("descricao", ""),
                dados.get("data", ""),
                dados.get("horario", ""),
                dados.get("professor", ""),
                1 if dados.get("realizada") else 0,
                id_aula,
            ),
        )
        return True

    @staticmethod
    def excluir(id_aula: int) -> bool:
        bd = obter_conexao()
        bd.executar("DELETE FROM aulas WHERE id = ?", (id_aula,))
        return True


# =====================================================================
class ModeloFrequencia:

    @staticmethod
    def registrar(aula_id: int, lead_id: int, presente: bool, observacao: str = ""):
        bd = obter_conexao()
        # SQLite/MySQL: tenta atualizar e, se 0 linhas, insere
        afetadas = bd.executar(
            "UPDATE frequencia SET presente = ?, observacao = ? "
            "WHERE aula_id = ? AND lead_id = ?",
            (1 if presente else 0, observacao, aula_id, lead_id),
        )
        if not afetadas:
            bd.executar(
                "INSERT INTO frequencia (aula_id, lead_id, presente, observacao) "
                "VALUES (?, ?, ?, ?)",
                (aula_id, lead_id, 1 if presente else 0, observacao),
            )
        return True

    @staticmethod
    def listar_por_aula(aula_id: int) -> list:
        bd = obter_conexao()
        return bd.consultar(
            "SELECT f.*, l.nome_completo "
            "FROM frequencia f LEFT JOIN leads l ON l.id = f.lead_id "
            "WHERE f.aula_id = ? ORDER BY l.nome_completo",
            (aula_id,),
        )

    @staticmethod
    def media_presenca_geral() -> float:
        bd = obter_conexao()
        r = bd.consultar_um(
            "SELECT AVG(presente) AS m FROM frequencia"
        )
        if not r or r["m"] is None:
            return 0.0
        return float(r["m"]) * 100


# =====================================================================
class ModeloPagamento:

    @staticmethod
    def inserir(dados: dict) -> int:
        bd = obter_conexao()
        bd.executar(
            "INSERT INTO pagamentos (venda_id, valor, metodo, comprovante) "
            "VALUES (?, ?, ?, ?)",
            (
                int(dados.get("venda_id") or 0),
                float(dados.get("valor") or 0),
                dados.get("metodo", ""),
                dados.get("comprovante", ""),
            ),
        )
        return bd.ultimo_id()

    @staticmethod
    def listar() -> list:
        bd = obter_conexao()
        return bd.consultar(
            "SELECT p.*, v.lead_id, l.nome_completo AS aluno_nome "
            "FROM pagamentos p "
            "LEFT JOIN vendas v ON v.id = p.venda_id "
            "LEFT JOIN leads l ON l.id = v.lead_id "
            "ORDER BY p.data_pagamento DESC"
        )

    @staticmethod
    def excluir(id_pagamento: int) -> bool:
        bd = obter_conexao()
        bd.executar("DELETE FROM pagamentos WHERE id = ?", (id_pagamento,))
        return True


# =====================================================================
class ModeloFunilOrigem:

    @staticmethod
    def obter_periodo(referencia: str) -> dict | None:
        bd = obter_conexao()
        return bd.consultar_um(
            "SELECT * FROM funil_origem WHERE referencia = ?",
            (referencia,),
        )

    @staticmethod
    def atualizar_periodo(referencia: str, dados: dict) -> bool:
        bd = obter_conexao()
        existe = bd.consultar_um(
            "SELECT id FROM funil_origem WHERE referencia = ?", (referencia,)
        )
        if existe:
            bd.executar(
                "UPDATE funil_origem SET visitantes = ?, leads = ?, "
                "negociacoes = ?, vendas = ?, alunos_ativos = ? "
                "WHERE referencia = ?",
                (
                    int(dados.get("visitantes", 0)),
                    int(dados.get("leads", 0)),
                    int(dados.get("negociacoes", 0)),
                    int(dados.get("vendas", 0)),
                    int(dados.get("alunos_ativos", 0)),
                    referencia,
                ),
            )
        else:
            bd.executar(
                "INSERT INTO funil_origem "
                "(referencia, visitantes, leads, negociacoes, vendas, alunos_ativos) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    referencia,
                    int(dados.get("visitantes", 0)),
                    int(dados.get("leads", 0)),
                    int(dados.get("negociacoes", 0)),
                    int(dados.get("vendas", 0)),
                    int(dados.get("alunos_ativos", 0)),
                ),
            )
        return True


# =====================================================================
class ModeloOrigemLeads:

    @staticmethod
    def listar() -> list:
        bd = obter_conexao()
        return bd.consultar(
            "SELECT * FROM origem_leads ORDER BY quantidade DESC"
        )

    @staticmethod
    def incrementar(origem: str, quantidade: int = 1) -> bool:
        bd = obter_conexao()
        afetadas = bd.executar(
            "UPDATE origem_leads SET quantidade = quantidade + ? WHERE origem = ?",
            (quantidade, origem),
        )
        if not afetadas:
            bd.executar(
                "INSERT INTO origem_leads (origem, quantidade) VALUES (?, ?)",
                (origem, quantidade),
            )
        return True

    @staticmethod
    def definir(origem: str, quantidade: int) -> bool:
        bd = obter_conexao()
        afetadas = bd.executar(
            "UPDATE origem_leads SET quantidade = ? WHERE origem = ?",
            (max(0, int(quantidade)), origem),
        )
        if not afetadas:
            bd.executar(
                "INSERT INTO origem_leads (origem, quantidade) VALUES (?, ?)",
                (origem, max(0, int(quantidade))),
            )
        return True


# =====================================================================
class ModeloConfiguracoes:

    @staticmethod
    def obter(chave: str, padrao=None) -> str:
        bd = obter_conexao()
        r = bd.consultar_um(
            "SELECT valor FROM configuracoes_administrador WHERE chave = ?",
            (chave,),
        )
        return r["valor"] if r and r.get("valor") is not None else padrao

    @staticmethod
    def definir(chave: str, valor: str) -> bool:
        bd = obter_conexao()
        afetadas = bd.executar(
            "UPDATE configuracoes_administrador SET valor = ? WHERE chave = ?",
            (valor, chave),
        )
        if not afetadas:
            bd.executar(
                "INSERT INTO configuracoes_administrador (chave, valor) VALUES (?, ?)",
                (chave, valor),
            )
        return True
