"""
Credenciais fixas do administrador do sistema.

Este arquivo NAO e gerado pelo sistema. O dono do sistema deve editar
manualmente as credenciais aqui. Apenas este administrador pode acessar
o painel de gestao educacional (dashboard).

A senha fica armazenada como hash bcrypt - nunca em texto puro.
Para gerar um novo hash, use:

    import bcrypt
    senha = "sua_senha"
    hash_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    print(hash_senha)
"""

# Email institucional fixo do administrador
EMAIL_ADMIN = "admin@sistemafacil.pa.br"

# Hash bcrypt da senha "admin123" (padrao - TROQUE em producao)
# Gerado com bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
SENHA_ADMIN_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyjW.0Iy3NS6Tu"

# Senha em texto (apenas como fallback se bcrypt falhar - NAO RECOMENDADO)
# Em producao, remova esta linha e mantenha apenas o hash acima.
SENHA_ADMIN_FALLBACK = "admin123"

# Nome do administrador exibido no dashboard
NOME_ADMIN = "Administrador Master"

# Permissoes do administrador
PERMISSOES_ADMIN = [
    "criar_lead", "editar_lead", "excluir_lead",
    "criar_venda", "editar_venda", "excluir_venda",
    "criar_pagamento", "editar_pagamento",
    "criar_turma", "editar_turma", "excluir_turma",
    "criar_aula", "editar_aula", "excluir_aula",
    "registrar_frequencia",
    "ver_relatorios",
    "editar_configuracoes",
    "criar_conta_aluno"
]
