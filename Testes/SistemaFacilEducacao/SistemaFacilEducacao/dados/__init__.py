"""Camada de dados: modelos e banco de dados."""
from .banco_dados import BancoDados
from .modelos import Lead, Venda, Pagamento, Turma, Aula, Frequencia, Notificacao

__all__ = [
    "BancoDados", "Lead", "Venda", "Pagamento",
    "Turma", "Aula", "Frequencia", "Notificacao",
]
