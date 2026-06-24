"""
Modelo de Usuario - operacoes CRUD na tabela usuarios.
Inclui criptografia de senhas com bcrypt.
"""
import random
import hashlib
from datetime import datetime
from banco_de_dados.conexao import obter_conexao, obter_cursor

# bcrypt e opcional - usa hashlib como fallback
try:
    import bcrypt
    _BCRYPT_OK = True
except ImportError:
    _BCRYPT_OK = False


def _hash_senha(senha):
    """Gera hash bcrypt da senha (ou SHA-256 como fallback)."""
    if _BCRYPT_OK:
        return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    # Fallback: SHA-256 com salt simples
    salt = "sf_salt_2025"
    return "sha256$" + hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()


def _verificar_senha(senha, hash_armazenado):
    """Verifica se a senha bate com o hash."""
    if not hash_armazenado:
        return False
    if hash_armazenado.startswith("sha256$"):
        salt = "sf_salt_2025"
        return ("sha256$" + hashlib.sha256(
            (salt + senha).encode("utf-8")).hexdigest()) == hash_armazenado
    if _BCRYPT_OK:
        try:
            return bcrypt.checkpw(senha.encode("utf-8"),
                                  hash_armazenado.encode("utf-8"))
        except Exception:
            return False
    return False


def gerar_email_institucional(matricula):
    """
    Gera email institucional no formato:
        aluno{matricula}@edu.pa.sistemafacil.br
    """
    return f"aluno{matricula}@edu.pa.sistemafacil.br"


def gerar_matricula():
    """Gera uma matricula aleatoria de 8 digitos."""
    return str(random.randint(10000000, 99999999))


def criar_usuario(nome, email, senha, telefone="", tipo="visitante"):
    """
    Cria um novo usuario. Retorna dict com matricula e email_institucional
    se for aluno.
    """
    senha_hash = _hash_senha(senha)
    matricula = None
    email_institucional = None

    if tipo == "aluno":
        matricula = gerar_matricula()
        email_institucional = gerar_email_institucional(matricula)

    sql = (
        "INSERT INTO usuarios "
        "(nome_completo, email_cadastro, email_institucional, senha_hash, "
        "telefone, tipo_conta, matricula, ativo, primeiro_acesso) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,1,0)"
    )
    parametros = (nome, email, email_institucional, senha_hash,
                  telefone, tipo, matricula)

    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(sql, parametros)
        novo_id = cursor.lastrowid
        cursor.close()

    return {
        "id": novo_id,
        "nome": nome,
        "email": email,
        "matricula": matricula,
        "email_institucional": email_institucional,
        "tipo": tipo,
    }


def autenticar(email, senha):
    """
    Autentica usuario por email/senha.
    Retorna dict do usuario ou None se invalido.
    """
    sql = (
        "SELECT * FROM usuarios "
        "WHERE (email_cadastro = %s OR email_institucional = %s) "
        "AND ativo = 1"
    )

    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(sql, (email, email))
        resultado = cursor.fetchone()
        cursor.close()

    if not resultado:
        return None

    # Converte dict se necessario
    if not isinstance(resultado, dict):
        resultado = dict(resultado)

    if _verificar_senha(senha, resultado.get("senha_hash", "")):
        # Atualiza ultimo acesso
        try:
            with obter_conexao() as conn:
                cur = obter_cursor(conn, dicionario=False)
                cur.execute(
                    "UPDATE usuarios SET ultimo_acesso = NOW() "
                    "WHERE id = %s",
                    (resultado["id"],)
                )
                cur.close()
        except Exception:
            pass
        return resultado
    return None


def email_existe(email):
    """Verifica se um email ja esta cadastrado."""
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(
            "SELECT id FROM usuarios WHERE email_cadastro = %s",
            (email,)
        )
        existe = cursor.fetchone() is not None
        cursor.close()
    return existe


def listar_usuarios(tipo=None):
    """Lista todos os usuarios (opcionalmente filtra por tipo)."""
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        if tipo:
            cursor.execute(
                "SELECT id, nome_completo, email_cadastro, email_institucional, "
                "matricula, tipo_conta, data_cadastro FROM usuarios "
                "WHERE tipo_conta = %s ORDER BY id DESC",
                (tipo,)
            )
        else:
            cursor.execute(
                "SELECT id, nome_completo, email_cadastro, email_institucional, "
                "matricula, tipo_conta, data_cadastro FROM usuarios "
                "ORDER BY id DESC"
            )
        resultados = cursor.fetchall()
        cursor.close()

    return [dict(r) if not isinstance(r, dict) else r for r in resultados]


def atualizar_senha(usuario_id, nova_senha):
    """Atualiza a senha de um usuario."""
    senha_hash = _hash_senha(nova_senha)
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(
            "UPDATE usuarios SET senha_hash = %s, primeiro_acesso = 0 "
            "WHERE id = %s",
            (senha_hash, usuario_id)
        )
        cursor.close()


def atualizar_foto_perfil(usuario_id, foto_base64):
    """Atualiza a foto de perfil do usuario (base64)."""
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)
        cursor.execute(
            "UPDATE usuarios SET foto_perfil = %s WHERE id = %s",
            (foto_base64, usuario_id)
        )
        cursor.close()


def obter_usuario_por_id(usuario_id):
    """Busca um usuario pelo id."""
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE id = %s", (usuario_id,)
        )
        resultado = cursor.fetchone()
        cursor.close()
    if resultado and not isinstance(resultado, dict):
        resultado = dict(resultado)
    return resultado
