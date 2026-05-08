"""
Utilitários de validação de campos.
"""
import re


REGEX_EMAIL = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
REGEX_TELEFONE = re.compile(r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$")
REGEX_CPF = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
REGEX_DATA = re.compile(r"^\d{2}/\d{2}/\d{4}$")


def validar_email(email: str) -> bool:
    if not email:
        return False
    return bool(REGEX_EMAIL.match(email.strip()))


def validar_telefone(telefone: str) -> bool:
    if not telefone:
        return False
    apenas_digitos = re.sub(r"\D", "", telefone)
    return 10 <= len(apenas_digitos) <= 11


def validar_cpf(cpf: str) -> bool:
    """Valida CPF com algoritmo dos dígitos verificadores."""
    if not cpf:
        return False
    apenas_digitos = re.sub(r"\D", "", cpf)
    if len(apenas_digitos) != 11:
        return False
    if apenas_digitos == apenas_digitos[0] * 11:
        return False

    # Cálculo do primeiro dígito
    soma = sum(int(apenas_digitos[i]) * (10 - i) for i in range(9))
    dig1 = (soma * 10 % 11) % 10
    if dig1 != int(apenas_digitos[9]):
        return False

    # Cálculo do segundo dígito
    soma = sum(int(apenas_digitos[i]) * (11 - i) for i in range(10))
    dig2 = (soma * 10 % 11) % 10
    return dig2 == int(apenas_digitos[10])


def validar_data(data: str) -> bool:
    if not data or not REGEX_DATA.match(data):
        return False
    try:
        dia, mes, ano = map(int, data.split("/"))
    except ValueError:
        return False
    if not (1 <= mes <= 12):
        return False
    if not (1 <= dia <= 31):
        return False
    if not (1900 <= ano <= 2100):
        return False
    return True


def formatar_cpf_progressivo(texto: str) -> str:
    """Formata CPF enquanto digita: 000.000.000-00."""
    digitos = re.sub(r"\D", "", texto)[:11]
    resultado = ""
    for i, d in enumerate(digitos):
        if i == 3 or i == 6:
            resultado += "."
        elif i == 9:
            resultado += "-"
        resultado += d
    return resultado


def formatar_data_progressivo(texto: str) -> str:
    """Formata data enquanto digita: dd/mm/aaaa."""
    digitos = re.sub(r"\D", "", texto)[:8]
    resultado = ""
    for i, d in enumerate(digitos):
        if i == 2 or i == 4:
            resultado += "/"
        resultado += d
    return resultado


def formatar_telefone_progressivo(texto: str) -> str:
    """Formata telefone enquanto digita: (11) 99999-9999."""
    digitos = re.sub(r"\D", "", texto)[:11]
    if not digitos:
        return ""
    resultado = "("
    for i, d in enumerate(digitos):
        if i == 2:
            resultado += ") "
        elif i == 7 and len(digitos) == 11:
            resultado += "-"
        elif i == 6 and len(digitos) <= 10:
            resultado += "-"
        resultado += d
    return resultado


def texto_nao_vazio(texto: str, minimo: int = 1) -> bool:
    return bool(texto) and len(texto.strip()) >= minimo


def emails_iguais(e1: str, e2: str) -> bool:
    return (e1 or "").strip().lower() == (e2 or "").strip().lower()


def senhas_iguais(s1: str, s2: str) -> bool:
    return (s1 or "") == (s2 or "")
