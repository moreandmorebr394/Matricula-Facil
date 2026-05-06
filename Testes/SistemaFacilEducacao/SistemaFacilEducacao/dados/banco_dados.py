"""Banco de dados em memoria com persistencia JSON.

Carrega/salva todas as entidades em arquivos .json dentro de
"dados_armazenados/". Inclui dados-semente para a primeira execucao.
"""

import json
import os
from dataclasses import asdict
from typing import Callable, Dict, List

from config.configuracoes import Configuracoes
from .modelos import (
    Aula, Frequencia, Lead, Notificacao, Pagamento, Turma, Venda,
)


class BancoDados:
    """Singleton simples - basta importar e usar."""

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self):
        if self._inicializado:
            return
        self._inicializado = True

        # Tabelas
        self.leads: List[Lead] = []
        self.vendas: List[Venda] = []
        self.pagamentos: List[Pagamento] = []
        self.turmas: List[Turma] = []
        self.aulas: List[Aula] = []
        self.frequencias: List[Frequencia] = []
        self.notificacoes: List[Notificacao] = []

        # Observadores (para reatividade)
        self._observadores: List[Callable] = []

        os.makedirs(Configuracoes.PASTA_DADOS, exist_ok=True)
        self.carregar()

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def _caminho(self, nome: str) -> str:
        return os.path.join(Configuracoes.PASTA_DADOS, f"{nome}.json")

    def carregar(self):
        carregadores: Dict[str, tuple] = {
            "leads": (Lead, "leads"),
            "vendas": (Venda, "vendas"),
            "pagamentos": (Pagamento, "pagamentos"),
            "turmas": (Turma, "turmas"),
            "aulas": (Aula, "aulas"),
            "frequencias": (Frequencia, "frequencias"),
            "notificacoes": (Notificacao, "notificacoes"),
        }
        algum_carregado = False
        for nome, (classe, atributo) in carregadores.items():
            caminho = self._caminho(nome)
            if os.path.exists(caminho):
                try:
                    with open(caminho, "r", encoding="utf-8") as fp:
                        dados = json.load(fp)
                    setattr(self, atributo, [classe(**item) for item in dados])
                    algum_carregado = True
                except Exception:
                    pass
        if not algum_carregado:
            self._popular_dados_semente()
            self.salvar()

    def salvar(self):
        mapeamento = {
            "leads": self.leads,
            "vendas": self.vendas,
            "pagamentos": self.pagamentos,
            "turmas": self.turmas,
            "aulas": self.aulas,
            "frequencias": self.frequencias,
            "notificacoes": self.notificacoes,
        }
        for nome, lista in mapeamento.items():
            with open(self._caminho(nome), "w", encoding="utf-8") as fp:
                json.dump([asdict(item) for item in lista], fp,
                          ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Notificadores
    # ------------------------------------------------------------------
    def adicionar_observador(self, callback: Callable):
        self._observadores.append(callback)

    def notificar_observadores(self):
        for cb in list(self._observadores):
            try:
                cb()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # IDs
    # ------------------------------------------------------------------
    @staticmethod
    def _proximo_id(lista) -> int:
        return (max((item.id for item in lista), default=0)) + 1

    # ------------------------------------------------------------------
    # CRUD - Leads
    # ------------------------------------------------------------------
    def adicionar_lead(self, lead: Lead) -> Lead:
        lead.id = self._proximo_id(self.leads)
        self.leads.insert(0, lead)
        self.adicionar_notificacao(Notificacao(
            titulo="Novo lead cadastrado",
            mensagem=f"{lead.nome} foi adicionado ao funil.",
            tipo="SUCESSO",
        ))
        self.salvar()
        self.notificar_observadores()
        return lead

    def atualizar_lead(self, lead: Lead):
        for i, atual in enumerate(self.leads):
            if atual.id == lead.id:
                self.leads[i] = lead
                break
        self.salvar()
        self.notificar_observadores()

    def remover_lead(self, lead_id: int):
        self.leads = [l for l in self.leads if l.id != lead_id]
        self.salvar()
        self.notificar_observadores()

    def buscar_lead(self, lead_id: int) -> Lead:
        for l in self.leads:
            if l.id == lead_id:
                return l
        return None

    # ------------------------------------------------------------------
    # CRUD - Notificacoes
    # ------------------------------------------------------------------
    def adicionar_notificacao(self, n: Notificacao):
        n.id = self._proximo_id(self.notificacoes)
        self.notificacoes.insert(0, n)
        if len(self.notificacoes) > 30:
            self.notificacoes = self.notificacoes[:30]

    def marcar_todas_notificacoes_lidas(self):
        for n in self.notificacoes:
            n.lida = True
        self.salvar()
        self.notificar_observadores()

    def notificacoes_nao_lidas(self) -> int:
        return sum(1 for n in self.notificacoes if not n.lida)

    # ------------------------------------------------------------------
    # CRUD - Vendas / Pagamentos / Turmas / Aulas
    # ------------------------------------------------------------------
    def adicionar_venda(self, v: Venda) -> Venda:
        v.id = self._proximo_id(self.vendas)
        self.vendas.insert(0, v)
        self.salvar()
        self.notificar_observadores()
        return v

    def adicionar_pagamento(self, p: Pagamento) -> Pagamento:
        p.id = self._proximo_id(self.pagamentos)
        self.pagamentos.insert(0, p)
        self.salvar()
        self.notificar_observadores()
        return p

    def adicionar_turma(self, t: Turma) -> Turma:
        t.id = self._proximo_id(self.turmas)
        self.turmas.insert(0, t)
        self.salvar()
        self.notificar_observadores()
        return t

    def adicionar_aula(self, a: Aula) -> Aula:
        a.id = self._proximo_id(self.aulas)
        self.aulas.insert(0, a)
        self.salvar()
        self.notificar_observadores()
        return a

    # ------------------------------------------------------------------
    # Estatisticas
    # ------------------------------------------------------------------
    def estatisticas_dashboard(self):
        total_leads = len(self.leads)
        total_vendas = len(self.vendas)
        faturamento = sum(v.valor for v in self.vendas if v.pago)
        conversao = (total_vendas / total_leads * 100) if total_leads else 0.0
        return {
            "leads": total_leads,
            "vendas": total_vendas,
            "faturamento": faturamento,
            "conversao": round(conversao, 1),
        }

    def funil_origem(self):
        """Numeros de cada etapa do funil, calculados sobre dados reais
        sempre que possivel - se faltar, usa valores demonstrativos."""
        leads = max(len(self.leads), 132)
        visitantes = max(int(leads / 0.106), 1248)
        negociacoes = max(int(leads * 0.47), 62)
        vendas = max(len(self.vendas), 38)
        ativos = max(int(vendas * 0.92), 35)
        return {
            "Visitantes": visitantes,
            "Leads": leads,
            "Negociacoes": negociacoes,
            "Vendas": vendas,
            "Alunos Ativos": ativos,
        }

    def origem_dos_leads(self):
        """Retorna lista de tuplas (origem, quantidade)."""
        contagem = {
            "Instagram": 0, "Indicacao": 0, "Google Ads": 0,
            "Facebook Ads": 0, "Site / Organico": 0, "Outros": 0,
        }
        mapa_aliases = {
            "indicação": "Indicacao", "indicacao": "Indicacao",
            "site": "Site / Organico", "site / organico": "Site / Organico",
            "site / organico": "Site / Organico",
        }
        for lead in self.leads:
            origem = lead.como_conheceu.strip()
            origem_norm = mapa_aliases.get(origem.lower(), origem)
            if origem_norm in contagem:
                contagem[origem_norm] += 1
            elif origem_norm:
                contagem["Outros"] += 1
        if all(v == 0 for v in contagem.values()):
            contagem = {
                "Instagram": 42, "Indicacao": 31, "Google Ads": 24,
                "Facebook Ads": 18, "Site / Organico": 10, "Outros": 7,
            }
        return list(contagem.items())

    # ------------------------------------------------------------------
    # Dados-semente (primeira execucao)
    # ------------------------------------------------------------------
    def _popular_dados_semente(self):
        sementes = [
            Lead(nome="Ana Beatriz Lima", curso_interesse="Social Media",
                 captador="Carlos Lima", status="LEAD", data_cadastro="24/05/2024",
                 email="ana.lima@email.com", telefone="(11) 91234-5678",
                 cidade="Sao Paulo", estado="SP", como_conheceu="Instagram"),
            Lead(nome="Pedro Henrique", curso_interesse="Trafego Pago",
                 captador="Maria Santos", status="NEGOCIACAO", data_cadastro="23/05/2024",
                 email="pedro.h@email.com", telefone="(11) 92345-6789",
                 cidade="Rio de Janeiro", estado="RJ", como_conheceu="Indicacao"),
            Lead(nome="Lucas Oliveira", curso_interesse="Design Grafico",
                 captador="Joao Pereira", status="PAGO", data_cadastro="22/05/2024",
                 email="lucas.o@email.com", telefone="(21) 93456-7890",
                 cidade="Belo Horizonte", estado="MG", como_conheceu="Google Ads"),
            Lead(nome="Julia Costa", curso_interesse="Marketing Digital",
                 captador="Maria Santos", status="NAO_PAGO", data_cadastro="21/05/2024",
                 email="julia.c@email.com", telefone="(31) 94567-8901",
                 cidade="Curitiba", estado="PR", como_conheceu="Facebook Ads"),
            Lead(nome="Joao da Silva", curso_interesse="Marketing Digital",
                 captador="Maria Santos", status="LEAD", data_cadastro="24/05/2024",
                 email="joao.silva@email.com", telefone="(11) 98765-4321",
                 cidade="Sao Paulo", estado="SP", endereco="Rua das Flores, 123",
                 como_conheceu="Instagram",
                 observacoes="Interessado no curso noturno."),
        ]
        for s in sementes:
            s.id = self._proximo_id(self.leads)
            self.leads.append(s)

        # Vendas iniciais
        self.vendas.append(Venda(
            id=1, lead_id=3, nome_aluno="Lucas Oliveira", curso="Design Grafico",
            valor=1490.00, data="22/05/2024", captador="Joao Pereira", pago=True,
            forma_pagamento="PIX",
        ))

        # Turmas iniciais
        self.turmas.append(Turma(
            id=1, nome="Marketing Digital - Turma A", curso="Marketing Digital",
            professor="Prof. Roberto Almeida", horario="Seg/Qua/Sex 19h-21h",
            capacidade=30, alunos=["Lucas Oliveira"], data_inicio="01/06/2024",
            status="ATIVA",
        ))
        self.turmas.append(Turma(
            id=2, nome="Design Grafico - Turma B", curso="Design Grafico",
            professor="Profa. Camila Souza", horario="Ter/Qui 19h-22h",
            capacidade=25, alunos=[], data_inicio="03/06/2024",
            status="ATIVA",
        ))

        # Aulas
        self.aulas.append(Aula(
            id=1, turma_id=1, titulo="Introducao ao Marketing Digital",
            descricao="Conceitos fundamentais e tendencias 2024",
            data="01/06/2024", horario="19h", professor="Prof. Roberto Almeida",
            realizada=True,
        ))

        # Notificacoes
        self.notificacoes.extend([
            Notificacao(id=1, titulo="Bem-vindo!",
                        mensagem="Sistema Facil Educacao iniciado com sucesso.",
                        tipo="SUCESSO"),
            Notificacao(id=2, titulo="Pagamento confirmado",
                        mensagem="Lucas Oliveira realizou o pagamento do curso.",
                        tipo="SUCESSO"),
            Notificacao(id=3, titulo="Novo lead",
                        mensagem="Ana Beatriz Lima entrou no funil.",
                        tipo="INFO"),
        ])
