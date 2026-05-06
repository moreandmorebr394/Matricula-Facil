## Estrutura do projeto

```
SistemaFacilEducacao/
├── principal.py              # ponto de entrada
├── config/                   # cores, fontes, configuracoes globais
│   ├── cores.py
│   ├── fontes.py
│   └── configuracoes.py
├── dados/                    # modelos + banco em JSON
│   ├── modelos.py
│   └── banco_dados.py
├── componentes/              # widgets reutilizaveis (botao, card, etc)
│   ├── botao.py
│   ├── card.py
│   ├── campo_entrada.py
│   ├── badge.py
│   ├── barra_lateral.py
│   └── cabecalho.py
├── utilitarios/              # graficos, animacoes, notificacoes
│   ├── graficos.py
│   ├── animacoes.py
│   └── notificacoes.py
├── telas/                    # telas (paginas) do app
│   ├── dashboard.py          # tela principal (replica do mockup)
│   ├── leads.py              # gestao de leads/alunos
│   ├── vendas.py
│   ├── pagamentos.py
│   ├── turmas.py
│   ├── aulas.py
│   ├── frequencia.py
│   ├── funil_origem.py
│   ├── relatorios.py
│   └── configuracoes_tela.py
└── recursos/                 # logo SF e arquivos de imagem
    ├── logo_sf.png
    ├── logo_sf_pequeno.png
    └── logo_sf_medio.png
```

Os dados sao salvos automaticamente em `dados_armazenados/` (criada na 1a execucao).

---

## Funcionalidades

- **Dashboard** com formulario de cadastro de lead, jornada do aluno, funil de origem, grafico pizza, leads recentes e resumo geral.
- **Leads** com filtros, tabela completa, edicao de status, exclusao e exportacao CSV.
- **Vendas** com indicadores, registro e historico.
- **Pagamentos** com filtros (todos / pagos / pendentes) e indicadores financeiros.
- **Turmas** em cards visuais coloridos, ocupacao animada, criacao e gestao de alunos.
- **Aulas** em duas colunas (agendadas / realizadas), criacao e marcacao.
- **Frequencia** com chamada por aula e calculo de presenca.
- **Funil de Origem** com analise visual detalhada e taxas de conversao.
- **Relatorios** com KPIs, grafico de barras animado por curso, distribuicao por status e exportacao CSV.
- **Configuracoes** com perfil, preferencias, info do sistema e zona de risco.
- **Notificacoes** (sino do header) com toasts em tempo real e modal de historico.
- **Perfil do Administrador** acessivel pelo header com atalhos rapidos.

---

## Estilo visual

- Fontes detectadas automaticamente: Segoe UI / Inter / Calibri / Helvetica.
- Cores principais: azul `#2563eb`, sidebar `#1e293b`, fundo `#f1f5f9`.
- Botoes com cantos arredondados e animacao de hover (interpolacao RGB).
- Animacoes: fade-in nas telas, contagem em valores, barras de progresso, toasts deslizantes.
- Logo SF (azul + amarelo) carregada do PNG do projeto.
