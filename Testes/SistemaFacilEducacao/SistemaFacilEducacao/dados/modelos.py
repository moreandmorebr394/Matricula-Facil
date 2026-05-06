"""Modelos de dados (data classes).

Modelos simples, sem dependencia de ORM, prontos para serializar em JSON.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


def _agora() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


@dataclass
class Lead:
    id: int = 0
    nome: str = ""
    data_nascimento: str = ""
    cpf: str = ""
    email: str = ""
    telefone: str = ""
    endereco: str = ""
    cidade: str = ""
    estado: str = ""
    curso_interesse: str = ""
    como_conheceu: str = ""
    captador: str = ""
    observacoes: str = ""
    status: str = "LEAD"  # LEAD, NEGOCIACAO, PAGO, NAO_PAGO, ALUNO_ATIVO
    data_cadastro: str = field(default_factory=_agora)

    def como_dicionario(self):
        return asdict(self)


@dataclass
class Venda:
    id: int = 0
    lead_id: int = 0
    nome_aluno: str = ""
    curso: str = ""
    valor: float = 0.0
    data: str = field(default_factory=_agora)
    captador: str = ""
    pago: bool = False
    forma_pagamento: str = ""


@dataclass
class Pagamento:
    id: int = 0
    venda_id: int = 0
    nome_aluno: str = ""
    valor: float = 0.0
    forma_pagamento: str = ""
    data: str = field(default_factory=_agora)
    comprovante: str = ""


@dataclass
class Turma:
    id: int = 0
    nome: str = ""
    curso: str = ""
    professor: str = ""
    horario: str = ""
    capacidade: int = 30
    alunos: list = field(default_factory=list)
    data_inicio: str = ""
    status: str = "ATIVA"


@dataclass
class Aula:
    id: int = 0
    turma_id: int = 0
    titulo: str = ""
    descricao: str = ""
    data: str = ""
    horario: str = ""
    professor: str = ""
    realizada: bool = False


@dataclass
class Frequencia:
    id: int = 0
    aula_id: int = 0
    aluno_nome: str = ""
    presente: bool = False
    data: str = ""


@dataclass
class Notificacao:
    id: int = 0
    titulo: str = ""
    mensagem: str = ""
    tipo: str = "INFO"  # INFO, SUCESSO, AVISO, ERRO
    lida: bool = False
    data: str = field(default_factory=_agora)
