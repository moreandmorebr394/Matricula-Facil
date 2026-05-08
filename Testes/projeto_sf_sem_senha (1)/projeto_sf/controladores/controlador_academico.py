"""
Controladores de Vendas, Pagamentos, Turmas, Aulas, Frequência e Funil.
"""
from modelos.modelo_venda import ModeloVenda
from modelos.modelo_academico import (
    ModeloTurma,
    ModeloAula,
    ModeloFrequencia,
    ModeloPagamento,
    ModeloFunilOrigem,
    ModeloOrigemLeads,
)
from modelos.modelo_aluno import ModeloLead


class ControladorVenda:

    @staticmethod
    def registrar_venda(dados: dict) -> tuple:
        if not dados.get("lead_id"):
            return False, "Informe o aluno (lead) da venda.", None
        try:
            valor = float(dados.get("valor") or 0)
        except (TypeError, ValueError):
            return False, "Valor inválido.", None
        if valor < 0:
            return False, "Valor não pode ser negativo.", None
        try:
            id_venda = ModeloVenda.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao registrar venda: {exc}", None

        # Atualiza status do lead correspondente
        try:
            status_pagamento = dados.get("status_pagamento", "NAO_PAGO")
            if status_pagamento == "PAGO":
                ModeloLead.alterar_status(int(dados["lead_id"]), "PAGO")
            else:
                ModeloLead.alterar_status(int(dados["lead_id"]), "NEGOCIACAO")
        except Exception:
            pass

        return True, "Venda registrada com sucesso!", id_venda

    @staticmethod
    def listar_vendas() -> list:
        return ModeloVenda.listar()

    @staticmethod
    def atualizar_venda(id_venda: int, dados: dict) -> tuple:
        try:
            ModeloVenda.atualizar(id_venda, dados)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Venda atualizada."

    @staticmethod
    def excluir_venda(id_venda: int) -> tuple:
        try:
            ModeloVenda.excluir(id_venda)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Venda removida."

    @staticmethod
    def faturamento() -> float:
        return ModeloVenda.faturamento_total()

    @staticmethod
    def total() -> int:
        return ModeloVenda.total_vendas()


# =====================================================================
class ControladorTurma:

    TURNOS = ("MANHA", "TARDE", "NOITE", "INTEGRAL")

    @staticmethod
    def cadastrar(dados: dict) -> tuple:
        if not dados.get("curso"):
            return False, "Informe o curso.", None
        try:
            id_turma = ModeloTurma.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao criar turma: {exc}", None
        return True, "Turma criada com sucesso!", id_turma

    @staticmethod
    def listar() -> list:
        return ModeloTurma.listar()

    @staticmethod
    def atualizar(id_turma: int, dados: dict) -> tuple:
        try:
            ModeloTurma.atualizar(id_turma, dados)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Turma atualizada."

    @staticmethod
    def excluir(id_turma: int) -> tuple:
        try:
            ModeloTurma.excluir(id_turma)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Turma excluída."


# =====================================================================
class ControladorAula:

    @staticmethod
    def cadastrar(dados: dict) -> tuple:
        if not dados.get("turma_id"):
            return False, "Informe a turma da aula.", None
        if not dados.get("titulo"):
            return False, "Informe o título da aula.", None
        try:
            id_aula = ModeloAula.inserir(dados)
        except Exception as exc:
            return False, f"Erro: {exc}", None
        return True, "Aula cadastrada!", id_aula

    @staticmethod
    def listar(turma_id: int = None) -> list:
        return ModeloAula.listar(turma_id)

    @staticmethod
    def atualizar(id_aula: int, dados: dict) -> tuple:
        try:
            ModeloAula.atualizar(id_aula, dados)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Aula atualizada."

    @staticmethod
    def excluir(id_aula: int) -> tuple:
        try:
            ModeloAula.excluir(id_aula)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Aula excluída."


# =====================================================================
class ControladorFrequencia:

    @staticmethod
    def registrar(aula_id: int, lead_id: int, presente: bool, observacao: str = ""):
        try:
            ModeloFrequencia.registrar(aula_id, lead_id, presente, observacao)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Frequência registrada."

    @staticmethod
    def por_aula(aula_id: int) -> list:
        return ModeloFrequencia.listar_por_aula(aula_id)

    @staticmethod
    def media_geral() -> float:
        return ModeloFrequencia.media_presenca_geral()


# =====================================================================
class ControladorPagamento:

    METODOS = ("Dinheiro", "PIX", "Cartão de Débito", "Cartão de Crédito",
               "Boleto", "Transferência")

    @staticmethod
    def registrar(dados: dict) -> tuple:
        if not dados.get("venda_id"):
            return False, "Informe a venda.", None
        try:
            valor = float(dados.get("valor") or 0)
        except (TypeError, ValueError):
            return False, "Valor inválido.", None
        if valor <= 0:
            return False, "Valor deve ser maior que zero.", None
        try:
            id_p = ModeloPagamento.inserir(dados)
        except Exception as exc:
            return False, f"Erro: {exc}", None
        return True, "Pagamento registrado!", id_p

    @staticmethod
    def listar() -> list:
        return ModeloPagamento.listar()

    @staticmethod
    def excluir(id_pagamento: int) -> tuple:
        try:
            ModeloPagamento.excluir(id_pagamento)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Pagamento removido."


# =====================================================================
class ControladorFunil:

    @staticmethod
    def obter_periodo(referencia: str) -> dict:
        dados = ModeloFunilOrigem.obter_periodo(referencia)
        return dados or {
            "referencia": referencia,
            "visitantes": 0,
            "leads": 0,
            "negociacoes": 0,
            "vendas": 0,
            "alunos_ativos": 0,
        }

    @staticmethod
    def atualizar_periodo(referencia: str, dados: dict) -> tuple:
        try:
            ModeloFunilOrigem.atualizar_periodo(referencia, dados)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Funil atualizado."

    @staticmethod
    def origens() -> list:
        return ModeloOrigemLeads.listar()

    @staticmethod
    def definir_origem(origem: str, quantidade: int) -> tuple:
        try:
            ModeloOrigemLeads.definir(origem, quantidade)
        except Exception as exc:
            return False, f"Erro: {exc}"
        return True, "Origem atualizada."
