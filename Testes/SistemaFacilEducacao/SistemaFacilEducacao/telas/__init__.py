"""Telas (paginas) do sistema."""
from .dashboard import TelaDashboard
from .leads import TelaLeads
from .vendas import TelaVendas
from .pagamentos import TelaPagamentos
from .turmas import TelaTurmas
from .aulas import TelaAulas
from .frequencia import TelaFrequencia
from .funil_origem import TelaFunilOrigem
from .relatorios import TelaRelatorios
from .configuracoes_tela import TelaConfiguracoes

__all__ = [
    "TelaDashboard", "TelaLeads", "TelaVendas", "TelaPagamentos",
    "TelaTurmas", "TelaAulas", "TelaFrequencia", "TelaFunilOrigem",
    "TelaRelatorios", "TelaConfiguracoes",
]
