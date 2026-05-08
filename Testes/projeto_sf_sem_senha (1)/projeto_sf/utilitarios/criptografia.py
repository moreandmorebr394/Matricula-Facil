"""
Utilitários de criptografia.

Usa bcrypt para hashing seguro de senhas.
Caso bcrypt não esteja instalado, faz fallback para hashlib (PBKDF2).
"""
import os
import hashlib
import hmac
import secrets


try:
    import bcrypt
    _TEM_BCRYPT = True
except ImportError:
    bcrypt = None
    _TEM_BCRYPT = False


def gerar_hash_senha(senha_pura: str) -> bytes:
    """Gera hash bcrypt da senha (ou PBKDF2 como fallback)."""
    if not isinstance(senha_pura, str) or not senha_pura:
        raise ValueError("Senha não pode ser vazia.")

    if _TEM_BCRYPT:
        return bcrypt.hashpw(senha_pura.encode("utf-8"), bcrypt.gensalt(rounds=12))

    # Fallback: PBKDF2-HMAC-SHA256
    sal = secrets.token_bytes(16)
    derivada = hashlib.pbkdf2_hmac("sha256", senha_pura.encode("utf-8"), sal, 200_000)
    return b"pbkdf2$" + sal.hex().encode() + b"$" + derivada.hex().encode()


def verificar_senha(senha_pura: str, hash_armazenado) -> bool:
    """Verifica se a senha corresponde ao hash."""
    if hash_armazenado is None or not senha_pura:
        return False

    if isinstance(hash_armazenado, str):
        hash_armazenado = hash_armazenado.encode("utf-8")

    # Detecta fallback PBKDF2
    if hash_armazenado.startswith(b"pbkdf2$"):
        try:
            _, sal_hex, hash_hex = hash_armazenado.decode().split("$")
            sal = bytes.fromhex(sal_hex)
            esperado = bytes.fromhex(hash_hex)
            calculado = hashlib.pbkdf2_hmac(
                "sha256", senha_pura.encode("utf-8"), sal, 200_000
            )
            return hmac.compare_digest(calculado, esperado)
        except Exception:
            return False

    if _TEM_BCRYPT:
        try:
            return bcrypt.checkpw(senha_pura.encode("utf-8"), hash_armazenado)
        except Exception:
            return False

    return False


def gerar_token_aleatorio(tamanho: int = 32) -> str:
    """Gera token hexadecimal aleatório seguro."""
    return secrets.token_hex(tamanho)


def criptografar_dado_sensivel(texto: str) -> str:
    """Criptografia simples (ofuscação) para dados sensíveis exibidos.

    Para criptografia real de dados em repouso utilize um esquema com
    chave (Fernet/AES). Aqui aplicamos um XOR + base64 só para
    impedir leitura casual em arquivos de log/cache.
    """
    if not texto:
        return ""
    chave = b"SF-SistemaFacilEducacao-2026"
    bruto = texto.encode("utf-8")
    cifrado = bytes(b ^ chave[i % len(chave)] for i, b in enumerate(bruto))
    import base64
    return base64.b64encode(cifrado).decode("ascii")


def descriptografar_dado_sensivel(cifrado: str) -> str:
    if not cifrado:
        return ""
    import base64
    try:
        bruto = base64.b64decode(cifrado.encode("ascii"))
    except Exception:
        return ""
    chave = b"SF-SistemaFacilEducacao-2026"
    decifrado = bytes(b ^ chave[i % len(chave)] for i, b in enumerate(bruto))
    try:
        return decifrado.decode("utf-8")
    except UnicodeDecodeError:
        return ""


def calcular_forca_senha(senha: str) -> tuple:
    """Avalia a força da senha e retorna (pontuacao 0-4, descricao)."""
    if not senha:
        return 0, "Vazia"

    pontos = 0
    if len(senha) >= 8:
        pontos += 1
    if len(senha) >= 12:
        pontos += 1
    if any(c.islower() for c in senha) and any(c.isupper() for c in senha):
        pontos += 1
    if any(c.isdigit() for c in senha):
        pontos += 1
    if any(not c.isalnum() for c in senha):
        pontos += 1

    pontos = min(pontos, 4)
    rotulos = {0: "Muito fraca", 1: "Fraca", 2: "Média", 3: "Forte", 4: "Muito forte"}
    return pontos, rotulos[pontos]
