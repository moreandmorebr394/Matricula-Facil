-- =====================================================================
-- Esquema do banco de dados Sistema Fácil (SF)
-- Compatível com MySQL 5.7+ / 8.0+ (WampServer)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS sistema_facil_sf
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sistema_facil_sf;

-- ---------------------------------------------------------------------
-- Tabela de usuários (alunos/clientes registrados via tela pública)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_publico VARCHAR(40) NOT NULL UNIQUE,
    nome_completo VARCHAR(150) NOT NULL,
    email_pessoal VARCHAR(180) NOT NULL UNIQUE,
    email_institucional VARCHAR(180) NOT NULL UNIQUE,
    telefone VARCHAR(30),
    senha_hash VARBINARY(180) NOT NULL,
    tipo_conta ENUM('aluno', 'cliente') NOT NULL DEFAULT 'aluno',
    primeiro_acesso TINYINT(1) NOT NULL DEFAULT 0,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    bloqueado TINYINT(1) NOT NULL DEFAULT 0,
    tentativas_falhas INT NOT NULL DEFAULT 0,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Tabela de leads / alunos cadastrados pelo administrador
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
    status ENUM('LEAD', 'NEGOCIACAO', 'PAGO', 'NAO_PAGO', 'ATIVO', 'CANCELADO')
        NOT NULL DEFAULT 'LEAD',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Tabela de vendas
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL DEFAULT 0,
    forma_pagamento VARCHAR(40),
    parcelas INT NOT NULL DEFAULT 1,
    status_pagamento ENUM('PAGO','NAO_PAGO','PARCIAL') NOT NULL DEFAULT 'NAO_PAGO',
    captador VARCHAR(120),
    observacoes TEXT,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vendas_lead FOREIGN KEY (lead_id) REFERENCES leads(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Tabela de pagamentos
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pagamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venda_id INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_pagamento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metodo VARCHAR(40),
    comprovante VARCHAR(255),
    CONSTRAINT fk_pagamentos_venda FOREIGN KEY (venda_id) REFERENCES vendas(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Tabela de turmas
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    curso VARCHAR(120) NOT NULL,
    turno ENUM('MANHA','TARDE','NOITE','INTEGRAL') NOT NULL DEFAULT 'MANHA',
    data_inicio VARCHAR(10),
    data_fim VARCHAR(10),
    capacidade INT NOT NULL DEFAULT 30,
    professor VARCHAR(120),
    sala VARCHAR(40),
    ativa TINYINT(1) NOT NULL DEFAULT 1,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Vínculo aluno x turma (matrículas)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS matriculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT NOT NULL,
    turma_id INT NOT NULL,
    data_matricula DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_matricula_lead FOREIGN KEY (lead_id) REFERENCES leads(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_matricula_turma FOREIGN KEY (turma_id) REFERENCES turmas(id)
        ON DELETE CASCADE,
    UNIQUE KEY uk_matricula (lead_id, turma_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Aulas
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS aulas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    turma_id INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT,
    data VARCHAR(10),
    horario VARCHAR(15),
    professor VARCHAR(120),
    realizada TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_aula_turma FOREIGN KEY (turma_id) REFERENCES turmas(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Frequência
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS frequencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aula_id INT NOT NULL,
    lead_id INT NOT NULL,
    presente TINYINT(1) NOT NULL DEFAULT 0,
    observacao VARCHAR(120),
    CONSTRAINT fk_freq_aula FOREIGN KEY (aula_id) REFERENCES aulas(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_freq_lead FOREIGN KEY (lead_id) REFERENCES leads(id)
        ON DELETE CASCADE,
    UNIQUE KEY uk_freq (aula_id, lead_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Funil de origem (visitantes/contadores)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS funil_origem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    referencia VARCHAR(20) NOT NULL,  -- "2024-05" formato AAAA-MM
    visitantes INT NOT NULL DEFAULT 0,
    leads INT NOT NULL DEFAULT 0,
    negociacoes INT NOT NULL DEFAULT 0,
    vendas INT NOT NULL DEFAULT 0,
    alunos_ativos INT NOT NULL DEFAULT 0,
    UNIQUE KEY uk_referencia (referencia)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Configurações do administrador (foto, preferências)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS configuracoes_administrador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chave VARCHAR(60) NOT NULL UNIQUE,
    valor TEXT
) ENGINE=InnoDB;
