"""
Controlador de Leads / Alunos.

Recebe dados da view, valida e chama o ModeloLead.
"""
from modelos.modelo_aluno import ModeloLead
from modelos.modelo_academico import ModeloOrigemLeads
from utilitarios.validadores import (
    texto_nao_vazio,
    validar_cpf,
    validar_email,
    validar_data,
)


CURSOS_DISPONIVEIS = (
    "Técnico em Enfermagem",
    "Técnico em Segurança do Trabalho",
    "Técnico em Informática",
    "Técnico em Administração",
    "Técnico em Secretaria Escolar",
    "Administração",
    "Bombeiro Civil",
)

ORIGENS_DISPONIVEIS = (
    "Instagram",
    "Indicação",
    "Google Ads",
    "Facebook Ads",
    "Site / Orgânico",
    "Outros",
)

ESTADOS_BRASIL = (
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT",
    "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO",
    "RR", "SC", "SP", "SE", "TO",
)

CAPTADORES_PADRAO = (
    "Maria Santos",
    "João Pereira",
    "Carlos Lima",
    "Ana Beatriz",
    "Pedro Henrique",
)


class ControladorLead:

    @staticmethod
    def cadastrar_lead(dados: dict) -> tuple:
        """Cadastra um lead novo. Retorna (sucesso, mensagem, id)."""
        if not texto_nao_vazio(dados.get("nome_completo"), 3):
            return False, "Informe o nome completo do aluno.", None

        email = dados.get("email", "")
        if email and not validar_email(email):
            return False, "E-mail inválido.", None

        cpf = dados.get("cpf", "")
        if cpf and not validar_cpf(cpf):
            return False, "CPF inválido. Verifique os dígitos.", None

        data_nasc = dados.get("data_nascimento", "")
        if data_nasc and not validar_data(data_nasc):
            return False, "Data de nascimento inválida (use dd/mm/aaaa).", None

        try:
            id_lead = ModeloLead.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao cadastrar lead: {exc}", None

        # incrementa origem do lead
        origem = dados.get("como_conheceu") or ""
        if origem:
            try:
                ModeloOrigemLeads.incrementar(origem, 1)
            except Exception:
                pass

        return True, "Lead cadastrado com sucesso!", id_lead

    @staticmethod
    def atualizar_lead(id_lead: int, dados: dict) -> tuple:
        if not texto_nao_vazio(dados.get("nome_completo"), 3):
            return False, "Informe o nome completo do aluno."
        cpf = dados.get("cpf", "")
        if cpf and not validar_cpf(cpf):
            return False, "CPF inválido."
        data_nasc = dados.get("data_nascimento", "")
        if data_nasc and not validar_data(data_nasc):
            return False, "Data de nascimento inválida."
        try:
            ModeloLead.atualizar(id_lead, dados)
        except Exception as exc:
            return False, f"Erro ao atualizar: {exc}"
        return True, "Dados atualizados com sucesso!"

    @staticmethod
    def excluir_lead(id_lead: int) -> tuple:
        try:
            ModeloLead.excluir(id_lead)
        except Exception as exc:
            return False, f"Erro ao excluir: {exc}"
        return True, "Lead removido com sucesso."

    @staticmethod
    def listar_leads(filtro_status: str = None, busca: str = None) -> list:
        return ModeloLead.listar(filtro_status, busca)

    @staticmethod
    def alterar_status(id_lead: int, novo_status: str) -> tuple:
        try:
            ModeloLead.alterar_status(id_lead, novo_status)
        except Exception as exc:
            return False, f"Erro ao alterar status: {exc}"
        return True, f"Status alterado para {novo_status}."

    @staticmethod
    def buscar_lead(id_lead: int) -> dict | None:
        return ModeloLead.buscar_por_id(id_lead)

    @staticmethod
    def total_leads() -> int:
        return ModeloLead.total()

    @staticmethod
    def contagem_status() -> dict:
        return ModeloLead.contar_por_status()
