"""
Controlador de Autenticação.

Camada Controller do MVC: regras de negócio entre View e Models.
"""
from configuracoes_admin import credenciais_admin
from modelos.modelo_usuario import ModeloUsuario
from utilitarios.criptografia import verificar_senha, calcular_forca_senha
from utilitarios.validadores import (
    validar_email,
    texto_nao_vazio,
    senhas_iguais,
    emails_iguais,
)


class ControladorAutenticacao:

    @staticmethod
    def autenticar_usuario(email: str, senha: str) -> tuple:
        """Autenticação para Aluno/Cliente.

        Retorna (sucesso, mensagem, dados_usuario).
        """
        if not validar_email(email):
            return False, "Informe um e-mail válido.", None
        if not senha:
            return False, "Informe sua senha.", None

        usuario = ModeloUsuario.autenticar(email, senha)
        if not usuario:
            return False, "Credenciais inválidas. Verifique e-mail e senha.", None
        if not usuario.get("ativo"):
            return False, "Conta inativa. Contate o administrador.", None

        return True, "Login realizado com sucesso!", usuario

    @staticmethod
    def autenticar_administrador(email: str, senha: str) -> tuple:
        """Autenticacao do administrador via arquivo de credenciais fixas.

        Procura o e-mail entre TODOS os administradores cadastrados
        em credenciais_admin.ADMINISTRADORES. Permite multiplos admins.
        """
        if not email or not senha:
            return False, "Preencha e-mail e senha do administrador.", None

        admin = credenciais_admin.buscar_administrador(email)
        if admin is None:
            return False, "E-mail administrativo nao reconhecido.", None

        if not verificar_senha(senha, admin["senha_hash"]):
            return False, "Senha administrativa incorreta.", None

        dados = {
            "id": 0,
            "nome_completo": admin.get("nome", "Administrador"),
            "email_pessoal": admin["email"],
            "email_institucional": admin["email"],
            "tipo_conta": "administrador",
            "permissoes": list(credenciais_admin.PERMISSOES_ADMIN),
        }
        return True, "Bem-vindo, administrador!", dados

    @staticmethod
    def autenticar_administrador_por_email(email: str) -> tuple:
        """Autenticacao do administrador apenas por e-mail (sem senha).

        Util quando a tela de acesso admin nao pede senha. Verifica se
        o e-mail informado pertence a um administrador cadastrado em
        credenciais_admin.ADMINISTRADORES.

        Retorna (sucesso, mensagem, dados_usuario).
        """
        if not email or not email.strip():
            return False, "Informe o e-mail do administrador.", None

        admin = credenciais_admin.buscar_administrador(email)
        if admin is None:
            return False, "E-mail administrativo nao reconhecido.", None

        dados = {
            "id": 0,
            "nome_completo": admin.get("nome", "Administrador"),
            "email_pessoal": admin["email"],
            "email_institucional": admin["email"],
            "tipo_conta": "administrador",
            "permissoes": list(credenciais_admin.PERMISSOES_ADMIN),
        }
        return True, "Bem-vindo, administrador!", dados

    @staticmethod
    def registrar_usuario(dados: dict) -> tuple:
        """Cadastra novo aluno/cliente.

        Retorna (sucesso, mensagem, dados_usuario).
        """
        nome = (dados.get("nome_completo") or "").strip()
        email = (dados.get("email_pessoal") or "").strip()
        email_repetir = (dados.get("email_repetir") or "").strip()
        senha = dados.get("senha") or ""
        senha_repetir = dados.get("senha_repetir") or ""
        telefone = (dados.get("telefone") or "").strip()
        tipo = dados.get("tipo_conta", "aluno")

        if not texto_nao_vazio(nome, 3):
            return False, "Informe seu nome completo (mín. 3 caracteres).", None
        if not validar_email(email):
            return False, "E-mail inválido.", None
        if not emails_iguais(email, email_repetir):
            return False, "Os e-mails informados não conferem.", None
        if len(senha) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres.", None
        if not senhas_iguais(senha, senha_repetir):
            return False, "As senhas informadas não conferem.", None

        forca, _ = calcular_forca_senha(senha)
        if forca < 2:
            return (
                False,
                "Senha muito fraca. Use letras, números e símbolos.",
                None,
            )

        try:
            usuario = ModeloUsuario.cadastrar(
                nome_completo=nome,
                email_pessoal=email,
                telefone=telefone,
                senha_pura=senha,
                tipo_conta=tipo,
            )
        except ValueError as exc:
            return False, str(exc), None
        except Exception as exc:
            return False, f"Erro ao cadastrar: {exc}", None

        return True, "Conta criada com sucesso!", usuario

    @staticmethod
    def alterar_senha_usuario(id_usuario: int, nova_senha: str) -> tuple:
        forca, _ = calcular_forca_senha(nova_senha)
        if forca < 2 or len(nova_senha) < 8:
            return False, "Nova senha muito fraca."
        ModeloUsuario.alterar_senha(id_usuario, nova_senha)
        return True, "Senha alterada com sucesso."
