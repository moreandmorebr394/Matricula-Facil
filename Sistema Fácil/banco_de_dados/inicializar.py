"""
Inicializador do banco de dados MySQL.

Cria todas as tabelas necessarias se elas ainda nao existirem.
"""
from banco_de_dados.conexao import obter_conexao, obter_cursor


# Definicoes das tabelas em SQL MySQL
TABELAS = {
    "usuarios": """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome_completo VARCHAR(150) NOT NULL,
            email_cadastro VARCHAR(150) UNIQUE NOT NULL,
            email_institucional VARCHAR(150),
            senha_hash VARCHAR(255) NOT NULL,
            telefone VARCHAR(30),
            tipo_conta VARCHAR(20) NOT NULL DEFAULT 'visitante',
            matricula VARCHAR(20),
            foto_perfil LONGTEXT,
            primeiro_acesso INT DEFAULT 0,
            ativo INT DEFAULT 1,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_acesso DATETIME
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    "leads": """
        CREATE TABLE IF NOT EXISTS leads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome_completo VARCHAR(150) NOT NULL,
            data_nascimento VARCHAR(15),
            cpf VARCHAR(20),
            email VARCHAR(150),
            telefone VARCHAR(30),
            endereco VARCHAR(255),
            cidade VARCHAR(100),
            estado VARCHAR(50),
            curso_interesse VARCHAR(100),
            como_conheceu VARCHAR(50),
            captador VARCHAR(100),
            observacoes TEXT,
            status VARCHAR(30) DEFAULT 'LEAD',
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    "vendas": """
        CREATE TABLE IF NOT EXISTS vendas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lead_id INT,
            nome_aluno VARCHAR(150) NOT NULL,
            curso VARCHAR(100) NOT NULL,
            valor_total DECIMAL(10,2) NOT NULL,
            forma_pagamento VARCHAR(50),
            parcelas INT DEFAULT 1,
            status_pagamento VARCHAR(30) DEFAULT 'Pendente',
            vendedor VARCHAR(100),
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            observacoes TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    "pagamentos": """
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            venda_id INT,
            nome_aluno VARCHAR(150),
            valor DECIMAL(10,2) NOT NULL,
            data_pagamento VARCHAR(15),
            forma_pagamento VARCHAR(50),
            parcela_numero INT DEFAULT 1,
            status VARCHAR(30) DEFAULT 'Pago',
            observacoes TEXT,
            data_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    "turmas": """
        CREATE TABLE IF NOT EXISTS turmas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome_turma VARCHAR(100) NOT NULL,
            curso VARCHAR(100) NOT NULL,
            professor VARCHAR(100),
            horario VARCHAR(50),
            sala VARCHAR(30),
            data_inicio VARCHAR(15),
            data_fim VARCHAR(15),
            capacidade_maxima INT DEFAULT 30,
            alunos_matriculados INT DEFAULT 0,
            status VARCHAR(30) DEFAULT 'Em Formacao',
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    "aulas": """
        CREATE TABLE IF NOT EXISTS aulas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            turma_id INT,
            titulo VARCHAR(150) NOT NULL,
            descricao TEXT,
            data_aula VARCHAR(15),
            horario_inicio VARCHAR(10),
            horario_fim VARCHAR(10),
            professor VARCHAR(100),
            sala VARCHAR(30),
            status VARCHAR(30) DEFAULT 'Agendada',
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    "frequencia": """
        CREATE TABLE IF NOT EXISTS frequencia (
            id INT AUTO_INCREMENT PRIMARY KEY,
            aula_id INT,
            aluno_nome VARCHAR(150),
            presente INT DEFAULT 0,
            justificativa TEXT,
            data_registro VARCHAR(15)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    "notificacoes": """
        CREATE TABLE IF NOT EXISTS notificacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(150) NOT NULL,
            mensagem TEXT,
            tipo VARCHAR(30) DEFAULT 'info',
            lida INT DEFAULT 0,
            destinatario VARCHAR(150),
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    "configuracoes": """
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chave VARCHAR(100) UNIQUE NOT NULL,
            valor TEXT,
            descricao VARCHAR(255),
            data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
}


CONFIGURACOES_INICIAIS = [
    ("nome_instituicao", "Sistema Facil Educacao", "Nome da instituicao"),
    ("email_contato", "contato@sistemafacil.pa.br", "Email de contato"),
    ("telefone_contato", "(91) 3000-0000", "Telefone de contato"),
    ("endereco", "Belem, Para - Brasil", "Endereco da instituicao"),
    ("foto_admin", "", "Foto do perfil do admin (base64)"),
    ("nome_admin", "Administrador Master", "Nome exibido do admin"),
]


def inicializar_banco():
    """Cria todas as tabelas e insere dados iniciais se nao existirem."""
    with obter_conexao() as conexao:
        cursor = obter_cursor(conexao, dicionario=False)

        # Cria cada tabela
        for nome_tabela, sql in TABELAS.items():
            try:
                cursor.execute(sql)
            except Exception as e:
                print(f"[Aviso] Falha ao criar tabela {nome_tabela}: {e}")

        # Insere configuracoes iniciais
        for chave, valor, descricao in CONFIGURACOES_INICIAIS:
            try:
                cursor.execute(
                    "INSERT IGNORE INTO configuracoes (chave, valor, descricao) "
                    "VALUES (%s, %s, %s)",
                    (chave, valor, descricao)
                )
            except Exception:
                pass

        cursor.close()

    print("[OK] Banco MySQL/WampServer inicializado com sucesso.")


if __name__ == "__main__":
    inicializar_banco()
