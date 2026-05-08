"""
Gerenciador de sessão do usuário logado.
"""
import time


class GerenciadorSessao:
    """Mantém o estado do usuário autenticado durante a execução."""

    def __init__(self):
        self._usuario = None
        self._tipo = None              # 'aluno' | 'cliente' | 'administrador'
        self._inicio_sessao = None
        self._token = None

    def iniciar(self, usuario: dict, tipo: str, token: str = None):
        self._usuario = usuario
        self._tipo = tipo
        self._inicio_sessao = time.time()
        self._token = token

    def encerrar(self):
        self._usuario = None
        self._tipo = None
        self._inicio_sessao = None
        self._token = None

    @property
    def autenticado(self) -> bool:
        return self._usuario is not None

    @property
    def usuario(self) -> dict:
        return dict(self._usuario) if self._usuario else None

    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def eh_administrador(self) -> bool:
        return self._tipo == "administrador"

    @property
    def tempo_sessao_minutos(self) -> float:
        if not self._inicio_sessao:
            return 0
        return (time.time() - self._inicio_sessao) / 60.0
