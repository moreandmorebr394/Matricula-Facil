"""
Controlador de Autenticacao.
Intermediario entre a Visao (telas de login/registro) e o Modelo (banco).

Faz validacoes, formatacoes e regras de negocio.
"""
import re
from app.modelo import modelo_usuario
from configuracoes_admin import credenciais_admin

# Tenta importar bcrypt
try:
    import bcrypt
    _BCRYPT_OK = True
except ImportError:
    _BCRYPT_OK = False


# Sessao em memoria (simples - 1 admin por vez)
_sessao_atual = {
    "logado": False,
    "tipo": None,           # "admin", "aluno", "visitante"
    "nome": None,
    "email": None,
    "id": None,
    "matricula": None,
}


def obter_sessao():
    return dict(_sessao_atual)


def encerrar_sessao():
    global _sessao_atual
    _sessao_atual = {
        "logado": False, "tipo": None, "nome": None,
        "email": None, "id": None, "matricula": None,
    }


def validar_email(email):
    """Valida formato de email."""
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(padrao, email) is not None


def validar_senha(senha):
    """Verifica forca da senha. Retorna (valida, mensagem)."""
    if len(senha) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    return True, "OK"


def validar_telefone(telefone):
    """Aceita formatos com ou sem mascara."""
    digitos = re.sub(r"\D", "", telefone)
    return len(digitos) >= 10


def registrar_aluno(nome, email, repetir_email, senha, repetir_senha,
                    telefone, tipo="aluno"):
    """
    Registra um novo aluno ou visitante.
    Retorna (sucesso, mensagem, dados_usuario)
    """
    # Validacoes
    if not nome or len(nome.strip()) < 3:
        return False, "Nome completo deve ter pelo menos 3 caracteres", None

    if not validar_email(email):
        return False, "Email invalido", None

    if email != repetir_email:
        return False, "Os emails nao coincidem", None

    if senha != repetir_senha:
        return False, "As senhas nao coincidem", None

    senha_ok, msg = validar_senha(senha)
    if not senha_ok:
        return False, msg, None

    if telefone and not validar_telefone(telefone):
        return False, "Telefone invalido", None

    if modelo_usuario.email_existe(email):
        return False, "Este email ja esta cadastrado", None

    if tipo not in ("aluno", "visitante"):
        tipo = "visitante"

    try:
        dados = modelo_usuario.criar_usuario(
            nome=nome.strip(),
            email=email.strip().lower(),
            senha=senha,
            telefone=telefone.strip() if telefone else "",
            tipo=tipo
        )
        return True, "Cadastro realizado com sucesso!", dados
    except Exception as e:
        return False, f"Erro ao cadastrar: {e}", None


def autenticar_usuario(email, senha):
    """
    Autentica um usuario comum (aluno/visitante).
    Retorna (sucesso, mensagem, dados_usuario)
    """
    global _sessao_atual

    if not email or not senha:
        return False, "Preencha email e senha", None

    email_limpo = email.strip().lower()
    usuario = modelo_usuario.autenticar(email_limpo, senha)

    if not usuario:
        return False, "Email ou senha invalidos", None

    if not usuario.get("ativo", 1):
        return False, "Conta desativada. Contate o administrador.", None

    _sessao_atual = {
        "logado": True,
        "tipo": usuario.get("tipo_conta", "visitante"),
        "nome": usuario.get("nome_completo"),
        "email": usuario.get("email_cadastro"),
        "id": usuario.get("id"),
        "matricula": usuario.get("matricula"),
        "email_institucional": usuario.get("email_institucional"),
    }
    return True, f"Bem-vindo(a), {usuario.get('nome_completo')}!", usuario


def autenticar_admin(email, senha):
    """
    Autentica o administrador comparando com credenciais fixas.
    Retorna (sucesso, mensagem)
    """
    global _sessao_atual

    if not email or not senha:
        return False, "Preencha email e senha"

    email_limpo = email.strip().lower()

    # Compara email
    if email_limpo != credenciais_admin.EMAIL_ADMIN.lower():
        return False, "Acesso negado. Credenciais administrativas invalidas."

    # Verifica senha (bcrypt primeiro, depois fallback)
    senha_ok = False
    if _BCRYPT_OK:
        try:
            hash_armazenado = credenciais_admin.SENHA_ADMIN_HASH.encode("utf-8")
            senha_ok = bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado)
        except Exception:
            senha_ok = False

    # Fallback (se bcrypt falhar ou nao estiver instalado)
    if not senha_ok:
        senha_fallback = getattr(
            credenciais_admin, "SENHA_ADMIN_FALLBACK", None
        )
        if senha_fallback and senha == senha_fallback:
            senha_ok = True

    if not senha_ok:
        return False, "Acesso negado. Credenciais administrativas invalidas."

    from app.modelo import modelo_geral
    try:
        nome_exibido = modelo_geral.obter_configuracao("nome_admin", credenciais_admin.NOME_ADMIN)
        email_exibido = modelo_geral.obter_configuracao("email_admin", credenciais_admin.EMAIL_ADMIN)
    except Exception:
        nome_exibido = credenciais_admin.NOME_ADMIN
        email_exibido = credenciais_admin.EMAIL_ADMIN

    _sessao_atual = {
        "logado": True,
        "tipo": "admin",
        "nome": nome_exibido,
        "email": email_exibido,
        "id": 0,
        "matricula": None,
    }
    return True, f"Bem-vindo, {nome_exibido}!"
