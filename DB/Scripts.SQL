CREATE TABLE aluno (
id_aluno INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
nome VARCHAR(100) NOT NULL,
email VARCHAR(100) UNIQUE,
endereco VARCHAR(80) NOT NULL,
CPF CHAR(11) NOT NULL UNIQUE,
telefone VARCHAR(11) NOT NULL
);

CREATE TABLE pagamento (
id_pagamento INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
valor_pago DECIMAL(10, 2) NOT NULL,
data_paga DATE NOT NULL,
forma_paga ENUM('Credito', 'Debito', 'Pix', 'Especie') NOT NULL,
parcela TINYINT
);

CREATE TABLE curso (
id_curso INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
nome VARCHAR (100),
duracao TIME NOT NULL,
carga_horario TINYINT NOT NULL,
tipo_curso ENUM('capacitacao', 'livre', 'tecnico') NOT NULL,
FOREIGN KEY (valor_pago) REFERENCES Pagamento(valor_pago)
);

CREATE TABLE turma(
id_turma INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
turno ENUM ('manha', 'tarde', 'noite'),
data_inicio DATE NOT NULL,
turma_status ENUM ('andamento', 'completo') NOT NULL,
FOREIGN KEY (ID_Curso) REFERENCES Curso (ID_Curso)
);

CREATE TABLE venda (
id_venda INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
FOREIGN KEY (turma_status) REFERENCES Turma(id_turma),
FOREIGN KEY (id_aluno) REFERENCES Aluno(id_aluno),
FOREIGN KEY (id_turma) REFERENCES Turma(id_turma)
);

CREATE TABLE funcionario (
id_funcionario INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
nome VARCHAR(100) NOT NULL,
email VARCHAR(100) UNIQUE,
endereco VARCHAR(80) NOT NULL,
CPF CHAR(11) NOT NULL UNIQUE,
telefone VARCHAR(11) NOT NULL,
senha VARCHAR(100) NOT NULL,
FOREIGN KEY (ID_Venda) REFERENCES Venda(ID_Venda)
);
