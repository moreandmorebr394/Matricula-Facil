"""
Controladores do dashboard CRM.
Cada controlador faz validacoes e repassa para o modelo correspondente.
"""
import re
from app.modelo import (
    modelo_lead, modelo_venda, modelo_pagamento,
    modelo_turma, modelo_aula, modelo_geral
)


# ============ LEADS ============

def validar_cpf(cpf):
    """Valida formato basico do CPF (apenas formato, nao calculo)."""
    digitos = re.sub(r"\D", "", cpf or "")
    return len(digitos) == 11


def formatar_cpf(cpf):
    """Formata CPF como 000.000.000-00."""
    d = re.sub(r"\D", "", cpf or "")
    if len(d) == 11:
        return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"
    return cpf


def formatar_data(data):
    """Formata data como DD/MM/AAAA."""
    d = re.sub(r"\D", "", data or "")
    if len(d) == 8:
        return f"{d[0:2]}/{d[2:4]}/{d[4:8]}"
    return data


def salvar_lead(dados):
    """
    Salva um lead. Retorna (sucesso, mensagem, id_lead).
    """
    if not dados.get("nome_completo") or len(dados["nome_completo"].strip()) < 3:
        return False, "Nome completo obrigatorio", None

    # Formata CPF e data
    if dados.get("cpf"):
        dados["cpf"] = formatar_cpf(dados["cpf"])
    if dados.get("data_nascimento"):
        dados["data_nascimento"] = formatar_data(dados["data_nascimento"])

    # Status padrao
    if not dados.get("status"):
        dados["status"] = "LEAD"

    try:
        novo_id = modelo_lead.inserir_lead(dados)
        modelo_geral.criar_notificacao(
            "Novo Lead Cadastrado",
            f"O lead '{dados['nome_completo']}' foi adicionado ao funil.",
            "sucesso"
        )
        return True, "Lead salvo com sucesso!", novo_id
    except Exception as e:
        return False, f"Erro ao salvar lead: {e}", None


def listar_leads(limite=None):
    return modelo_lead.listar_leads(limite=limite)


def obter_lead(lead_id):
    return modelo_lead.obter_lead(lead_id)


def atualizar_lead(lead_id, dados):
    try:
        if dados.get("cpf"):
            dados["cpf"] = formatar_cpf(dados["cpf"])
        if dados.get("data_nascimento"):
            dados["data_nascimento"] = formatar_data(dados["data_nascimento"])
        modelo_lead.atualizar_lead(lead_id, dados)
        return True, "Lead atualizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao atualizar: {e}"


def excluir_lead(lead_id):
    try:
        modelo_lead.excluir_lead(lead_id)
        return True, "Lead excluido com sucesso!"
    except Exception as e:
        return False, f"Erro ao excluir: {e}"


def estatisticas_leads():
    """Retorna dict com estatisticas para o dashboard."""
    return {
        "total": modelo_lead.total_leads(),
        "por_status": modelo_lead.contar_leads_por_status(),
        "por_origem": modelo_lead.contar_leads_por_origem(),
    }


# ============ VENDAS ============

def salvar_venda(dados):
    if not dados.get("nome_aluno"):
        return False, "Nome do aluno obrigatorio", None
    if not dados.get("curso"):
        return False, "Curso obrigatorio", None
    if not dados.get("valor_total"):
        return False, "Valor total obrigatorio", None

    try:
        # Limpa valor (R$ X,XX -> X.XX)
        valor_str = str(dados["valor_total"])
        valor_str = valor_str.replace("R$", "").replace(" ", "")
        valor_str = valor_str.replace(".", "").replace(",", ".")
        dados["valor_total"] = float(valor_str)
    except ValueError:
        return False, "Valor total invalido", None

    try:
        novo_id = modelo_venda.inserir_venda(dados)
        modelo_geral.criar_notificacao(
            "Nova Venda Registrada",
            f"Venda para '{dados['nome_aluno']}' no valor de "
            f"R$ {dados['valor_total']:.2f}",
            "sucesso"
        )
        return True, "Venda registrada com sucesso!", novo_id
    except Exception as e:
        return False, f"Erro ao salvar venda: {e}", None


def listar_vendas():
    return modelo_venda.listar_vendas()


def atualizar_venda(venda_id, dados):
    try:
        if "valor_total" in dados and dados["valor_total"]:
            valor_str = str(dados["valor_total"]).replace("R$", "").replace(" ", "")
            valor_str = valor_str.replace(".", "").replace(",", ".")
            dados["valor_total"] = float(valor_str)
        modelo_venda.atualizar_venda(venda_id, dados)
        return True, "Venda atualizada com sucesso!"
    except Exception as e:
        return False, f"Erro: {e}"


def excluir_venda(venda_id):
    try:
        modelo_venda.excluir_venda(venda_id)
        return True, "Venda excluida com sucesso!"
    except Exception as e:
        return False, f"Erro: {e}"


# ============ PAGAMENTOS ============

def salvar_pagamento(dados):
    if not dados.get("nome_aluno"):
        return False, "Nome do aluno obrigatorio", None
    if not dados.get("valor"):
        return False, "Valor obrigatorio", None

    try:
        valor_str = str(dados["valor"]).replace("R$", "").replace(" ", "")
        valor_str = valor_str.replace(".", "").replace(",", ".")
        dados["valor"] = float(valor_str)
    except ValueError:
        return False, "Valor invalido", None

    try:
        novo_id = modelo_pagamento.inserir_pagamento(dados)
        return True, "Pagamento registrado!", novo_id
    except Exception as e:
        return False, f"Erro: {e}", None


def listar_pagamentos():
    return modelo_pagamento.listar_pagamentos()


def excluir_pagamento(p_id):
    try:
        modelo_pagamento.excluir_pagamento(p_id)
        return True, "Pagamento excluido!"
    except Exception as e:
        return False, f"Erro: {e}"


# ============ TURMAS ============

def salvar_turma(dados):
    if not dados.get("nome_turma"):
        return False, "Nome da turma obrigatorio", None
    if not dados.get("curso"):
        return False, "Curso obrigatorio", None

    try:
        novo_id = modelo_turma.inserir_turma(dados)
        return True, "Turma criada com sucesso!", novo_id
    except Exception as e:
        return False, f"Erro: {e}", None


def listar_turmas():
    return modelo_turma.listar_turmas()


def atualizar_turma(turma_id, dados):
    try:
        modelo_turma.atualizar_turma(turma_id, dados)
        return True, "Turma atualizada!"
    except Exception as e:
        return False, f"Erro: {e}"


def excluir_turma(turma_id):
    try:
        modelo_turma.excluir_turma(turma_id)
        return True, "Turma excluida!"
    except Exception as e:
        return False, f"Erro: {e}"


# ============ AULAS ============

def salvar_aula(dados):
    if not dados.get("titulo"):
        return False, "Titulo da aula obrigatorio", None
    try:
        novo_id = modelo_aula.inserir_aula(dados)
        return True, "Aula criada com sucesso!", novo_id
    except Exception as e:
        return False, f"Erro: {e}", None


def listar_aulas():
    return modelo_aula.listar_aulas()


def atualizar_aula(aula_id, dados):
    try:
        modelo_aula.atualizar_aula(aula_id, dados)
        return True, "Aula atualizada!"
    except Exception as e:
        return False, f"Erro: {e}"


def excluir_aula(aula_id):
    try:
        modelo_aula.excluir_aula(aula_id)
        return True, "Aula excluida!"
    except Exception as e:
        return False, f"Erro: {e}"


# ============ FREQUENCIA ============

def salvar_frequencia(dados):
    try:
        novo_id = modelo_geral.registrar_frequencia(dados)
        return True, "Frequencia registrada!", novo_id
    except Exception as e:
        return False, f"Erro: {e}", None


def listar_frequencia():
    return modelo_geral.listar_frequencia()


# ============ DASHBOARD GERAL ============

def estatisticas_gerais():
    """Retorna dict com todas estatisticas para o dashboard."""
    return {
        "total_leads": modelo_lead.total_leads(),
        "total_vendas": modelo_venda.total_vendas(),
        "total_turmas": modelo_turma.total_turmas(),
        "total_aulas": modelo_aula.total_aulas(),
        "faturamento": modelo_venda.faturamento_total(),
        "recebido": modelo_pagamento.total_recebido(),
        "leads_por_status": modelo_lead.contar_leads_por_status(),
        "leads_por_origem": modelo_lead.contar_leads_por_origem(),
    }
