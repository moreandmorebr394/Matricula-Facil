"""
Geradores de identificadores institucionais.
"""
import random
import string
import time


def gerar_email_institucional(tipo: str = "aluno") -> str:
    """Gera um email institucional aleatório.

    Exemplos:
        aluno53756265@edu.pa.sistemafacil.br
        cliente91234812@edu.pa.sistemafacil.br
    """
    tipo = (tipo or "aluno").strip().lower() or "aluno"
    numero = "".join(random.choices(string.digits, k=8))
    return f"{tipo}{numero}@edu.pa.sistemafacil.br"


def gerar_id_usuario(prefixo: str = "USR") -> str:
    """Gera um ID alfanumérico de usuário."""
    timestamp = int(time.time() * 1000) % 10_000_000
    aleatorio = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefixo}-{timestamp}-{aleatorio}"


def gerar_senha_temporaria(tamanho: int = 10) -> str:
    """Gera uma senha temporária aleatória."""
    base = string.ascii_letters + string.digits + "!@#$%&*"
    while True:
        s = "".join(random.choices(base, k=tamanho))
        if (any(c.islower() for c in s)
                and any(c.isupper() for c in s)
                and any(c.isdigit() for c in s)):
            return s


def gerar_codigo_turma(curso: str) -> str:
    """Gera código único para turma com base no curso."""
    sigla = "".join(p[0] for p in curso.split() if p)[:3].upper() or "TUR"
    sufixo = "".join(random.choices(string.digits, k=4))
    return f"{sigla}-{sufixo}"
