"""
=============================================================================
   CREDENCIAIS ADMINISTRATIVAS DO SISTEMA FÁCIL (SF)
=============================================================================

Este arquivo guarda as credenciais de TODOS os administradores que podem
acessar o painel administrativo do sistema.

A senha NUNCA é armazenada em texto puro - apenas o hash bcrypt.

-----------------------------------------------------------------------------
   COMO VER A SENHA E O E-MAIL ATUAL?
-----------------------------------------------------------------------------
   - Veja a lista ADMINISTRADORES abaixo.
   - O e-mail está em texto claro (campo "email").
   - A senha NÃO pode ser recuperada (é hash de mão única).
     A senha padrão do administrador principal é: Admin@SF2026

-----------------------------------------------------------------------------
   COMO ALTERAR A SENHA DE UM ADMINISTRADOR EXISTENTE?
-----------------------------------------------------------------------------
   Passo 1: Abra o terminal na pasta do projeto e execute:

       python gerar_senha_admin.py

       (ele vai pedir a nova senha e mostrar o hash)

   Passo 2: Copie o hash que aparece (começa com $2b$12$...)
   Passo 3: Cole-o no campo "senha_hash" do administrador desejado abaixo.

-----------------------------------------------------------------------------
   COMO ADICIONAR UM NOVO ADMINISTRADOR?
-----------------------------------------------------------------------------
   1. Gere o hash da senha (mesmo passo acima):

       python gerar_senha_admin.py

   2. Copie a entrada de exemplo abaixo, descomente, e ajuste os campos:

       {
           "email": "joao@sistemafacil.pa.br",
           "nome":  "Joao Silva",
           "senha_hash": b"$2b$12$.....cole_o_hash_aqui.....",
       },

   3. Salve o arquivo. Pronto - o novo admin ja pode entrar.

-----------------------------------------------------------------------------
   COMO REMOVER UM ADMINISTRADOR?
-----------------------------------------------------------------------------
   Apague (ou comente com '#') a entrada dele na lista ADMINISTRADORES.

=============================================================================
"""

# =============================================================================
# LISTA DE ADMINISTRADORES
# =============================================================================
# Cada administrador e um dicionario com:
#   - email      : e-mail de login (nao diferencia maiuscula/minuscula)
#   - nome       : nome de exibicao no painel
#   - senha_hash : hash bcrypt da senha (sempre como bytes - prefixo b"...")
# =============================================================================
ADMINISTRADORES = [
    # -------------------------------------------------------------------------
    # ADMINISTRADOR PRINCIPAL (padrao do sistema)
    # E-mail: admin@sistemafacil.pa.br
    # Senha:  Admin@SF2026
    # -------------------------------------------------------------------------
    {
        "email": "admin@sistemafacil.pa.br",
        "nome":  "Administrador Principal",
        "senha_hash": b"$2b$12$I2Qa2qLDD0pmE35USz76iuFM7as.wX9fluIOrRHU70dNhvqh/UA16",
    },

    # -------------------------------------------------------------------------
    # EXEMPLO: Para adicionar outro administrador, copie o bloco abaixo,
    # remova o '#' do comeco de cada linha e ajuste os campos.
    # -------------------------------------------------------------------------
    # {
    #     "email": "outro.admin@sistemafacil.pa.br",
    #     "nome":  "Nome do Outro Admin",
    #     "senha_hash": b"$2b$12$.....cole_o_hash_aqui.....",
    # },
]


# =============================================================================
# CONFIGURACOES GERAIS DE ACESSO
# =============================================================================
PERMISSOES_ADMIN = (
    "criar_lead",
    "editar_lead",
    "excluir_lead",
    "criar_turma",
    "editar_turma",
    "excluir_turma",
    "registrar_pagamento",
    "registrar_venda",
    "ver_relatorios",
    "exportar_dados",
    "alterar_configuracoes",
)

TENTATIVAS_MAXIMAS_LOGIN = 5
TEMPO_BLOQUEIO_MINUTOS = 10


# =============================================================================
# COMPATIBILIDADE COM O CODIGO ANTIGO
# =============================================================================
# Mantem os nomes EMAIL_ADMIN, NOME_ADMIN, SENHA_ADMIN_HASH apontando
# para o primeiro administrador da lista (administrador principal).
# Nao edite esta secao - edite os dados do admin principal acima.
# =============================================================================
if ADMINISTRADORES:
    EMAIL_ADMIN = ADMINISTRADORES[0]["email"]
    NOME_ADMIN = ADMINISTRADORES[0]["nome"]
    SENHA_ADMIN_HASH = ADMINISTRADORES[0]["senha_hash"]
else:
    EMAIL_ADMIN = ""
    NOME_ADMIN = "Administrador"
    SENHA_ADMIN_HASH = b""


# =============================================================================
# FUNCOES AUXILIARES (usadas pelo controlador de autenticacao)
# =============================================================================
def buscar_administrador(email: str):
    """Procura um administrador pelo e-mail (case-insensitive).

    Retorna o dicionario do admin ou None se nao encontrado.
    """
    if not email:
        return None
    email_norm = email.strip().lower()
    for adm in ADMINISTRADORES:
        if adm.get("email", "").strip().lower() == email_norm:
            return adm
    return None


def listar_emails_admin() -> list:
    """Retorna a lista de e-mails de todos os administradores cadastrados."""
    return [a.get("email", "") for a in ADMINISTRADORES]
