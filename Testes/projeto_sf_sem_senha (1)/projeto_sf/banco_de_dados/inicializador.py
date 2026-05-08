"""
Inicializador do banco de dados.

Cria as tabelas em MySQL ou SQLite (fallback) caso ainda não existam.
"""
from banco_de_dados import conexao as bd


# Esquemas no formato compatível com SQLite e MySQL.
# Diferenças tratadas dinamicamente abaixo.
TABELAS = [
    ("usuarios", """
        CREATE TABLE IF NOT EXISTS usuarios (
            id {AUTOINC} PRIMARY KEY,
            id_publico VARCHAR(40) NOT NULL UNIQUE,
            nome_completo VARCHAR(150) NOT NULL,
            email_pessoal VARCHAR(180) NOT NULL UNIQUE,
            email_institucional VARCHAR(180) NOT NULL UNIQUE,
            telefone VARCHAR(30),
            senha_hash {BLOB} NOT NULL,
            tipo_conta VARCHAR(20) NOT NULL DEFAULT 'aluno',
            primeiro_acesso INTEGER NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 1,
            bloqueado INTEGER NOT NULL DEFAULT 0,
            tentativas_falhas INTEGER NOT NULL DEFAULT 0,
            criado_em {DATETIME} NOT NULL DEFAULT {AGORA},
            atualizado_em {DATETIME} NOT NULL DEFAULT {AGORA}
        )
    """),
    ("leads", """
        CREATE TABLE IF NOT EXISTS leads (
            id {AUTOINC} PRIMARY KEY,
            nome_completo VARCHAR(150) NOT NULL,
            data_nascimento VARCHAR(10),
            cpf_cifrado TEXT,
            email VARCHAR(180),
            telefone VARCHAR(30),
            endereco VARCHAR(255),
            cidade VARCHAR(80),
            estado VARCHAR(2),
            curso_interesse VARCHAR(120),
            como_conheceu VARCHAR(80),
            captador VARCHAR(120),
            observacoes TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'LEAD',
            criado_em {DATETIME} NOT NULL DEFAULT {AGORA},
            atualizado_em {DATETIME} NOT NULL DEFAULT {AGORA}
        )
    """),
    ("vendas", """
        CREATE TABLE IF NOT EXISTS vendas (
            id {AUTOINC} PRIMARY KEY,
            lead_id INTEGER NOT NULL,
            valor DECIMAL(10,2) NOT NULL DEFAULT 0,
            forma_pagamento VARCHAR(40),
            parcelas INTEGER NOT NULL DEFAULT 1,
            status_pagamento VARCHAR(20) NOT NULL DEFAULT 'NAO_PAGO',
            captador VARCHAR(120),
            observacoes TEXT,
            criado_em {DATETIME} NOT NULL DEFAULT {AGORA}
        )
    """),
    ("pagamentos", """
        CREATE TABLE IF NOT EXISTS pagamentos (
            id {AUTOINC} PRIMARY KEY,
            venda_id INTEGER NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            data_pagamento {DATETIME} NOT NULL DEFAULT {AGORA},
            metodo VARCHAR(40),
            comprovante VARCHAR(255)
        )
    """),
    ("turmas", """
        CREATE TABLE IF NOT EXISTS turmas (
            id {AUTOINC} PRIMARY KEY,
            codigo VARCHAR(20) NOT NULL UNIQUE,
            curso VARCHAR(120) NOT NULL,
            turno VARCHAR(20) NOT NULL DEFAULT 'MANHA',
            data_inicio VARCHAR(10),
            data_fim VARCHAR(10),
            capacidade INTEGER NOT NULL DEFAULT 30,
            professor VARCHAR(120),
            sala VARCHAR(40),
            ativa INTEGER NOT NULL DEFAULT 1,
            criado_em {DATETIME} NOT NULL DEFAULT {AGORA}
        )
    """),
    ("matriculas", """
        CREATE TABLE IF NOT EXISTS matriculas (
            id {AUTOINC} PRIMARY KEY,
            lead_id INTEGER NOT NULL,
            turma_id INTEGER NOT NULL,
            data_matricula {DATETIME} NOT NULL DEFAULT {AGORA}
        )
    """),
    ("aulas", """
        CREATE TABLE IF NOT EXISTS aulas (
            id {AUTOINC} PRIMARY KEY,
            turma_id INTEGER NOT NULL,
            titulo VARCHAR(150) NOT NULL,
            descricao TEXT,
            data VARCHAR(10),
            horario VARCHAR(15),
            professor VARCHAR(120),
            realizada INTEGER NOT NULL DEFAULT 0
        )
    """),
    ("frequencia", """
        CREATE TABLE IF NOT EXISTS frequencia (
            id {AUTOINC} PRIMARY KEY,
            aula_id INTEGER NOT NULL,
            lead_id INTEGER NOT NULL,
            presente INTEGER NOT NULL DEFAULT 0,
            observacao VARCHAR(120)
        )
    """),
    ("funil_origem", """
        CREATE TABLE IF NOT EXISTS funil_origem (
            id {AUTOINC} PRIMARY KEY,
            referencia VARCHAR(20) NOT NULL UNIQUE,
            visitantes INTEGER NOT NULL DEFAULT 0,
            leads INTEGER NOT NULL DEFAULT 0,
            negociacoes INTEGER NOT NULL DEFAULT 0,
            vendas INTEGER NOT NULL DEFAULT 0,
            alunos_ativos INTEGER NOT NULL DEFAULT 0
        )
    """),
    ("configuracoes_administrador", """
        CREATE TABLE IF NOT EXISTS configuracoes_administrador (
            id {AUTOINC} PRIMARY KEY,
            chave VARCHAR(60) NOT NULL UNIQUE,
            valor TEXT
        )
    """),
    ("origem_leads", """
        CREATE TABLE IF NOT EXISTS origem_leads (
            id {AUTOINC} PRIMARY KEY,
            origem VARCHAR(80) NOT NULL UNIQUE,
            quantidade INTEGER NOT NULL DEFAULT 0
        )
    """),
]


def _placeholders_para_tipo(tipo: str) -> dict:
    if tipo == "mysql":
        return {
            "AUTOINC": "INT AUTO_INCREMENT",
            "BLOB": "VARBINARY(180)",
            "DATETIME": "DATETIME",
            "AGORA": "CURRENT_TIMESTAMP",
        }
    return {
        "AUTOINC": "INTEGER",
        "BLOB": "BLOB",
        "DATETIME": "TIMESTAMP",
        "AGORA": "CURRENT_TIMESTAMP",
    }


def inicializar_banco_de_dados() -> tuple:
    """Inicializa o banco. Retorna (sucesso, mensagem)."""
    try:
        adaptador = bd.obter_conexao()
    except Exception as exc:
        return False, str(exc)

    placeholders = _placeholders_para_tipo(adaptador.tipo)

    try:
        for _, ddl in TABELAS:
            sql = ddl.format(**placeholders)
            adaptador.executar(sql)

        _semear_dados_iniciais(adaptador)
        return True, f"Banco inicializado ({adaptador.tipo})"
    except Exception as exc:
        return False, f"Erro ao criar tabelas: {exc}"


def _semear_dados_iniciais(adaptador) -> None:
    """Insere dados de exemplo na primeira execução."""
    # Funil do mês atual
    from datetime import datetime
    referencia = datetime.now().strftime("%Y-%m")
    existe = adaptador.consultar_um(
        "SELECT id FROM funil_origem WHERE referencia = ?",
        (referencia,),
    )
    if not existe:
        adaptador.executar(
            "INSERT INTO funil_origem "
            "(referencia, visitantes, leads, negociacoes, vendas, alunos_ativos) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (referencia, 1248, 132, 62, 38, 35),
        )

    # Origens dos leads (semeadas só se vazio)
    total_origens = adaptador.consultar_um(
        "SELECT COUNT(*) AS c FROM origem_leads"
    )
    if not total_origens or total_origens.get("c", 0) == 0:
        origens_iniciais = [
            ("Instagram", 42),
            ("Indicação", 31),
            ("Google Ads", 24),
            ("Facebook Ads", 18),
            ("Site / Orgânico", 10),
            ("Outros", 7),
        ]
        for nome, qtd in origens_iniciais:
            adaptador.executar(
                "INSERT INTO origem_leads (origem, quantidade) VALUES (?, ?)",
                (nome, qtd),
            )
