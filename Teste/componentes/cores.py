"""
Paleta de cores e constantes visuais do Sistema Facil.

Todas as cores sao em formato HEX de 6 digitos (sem canal alpha) para
compatibilidade total com Tkinter, que nao aceita hex de 8 digitos.

Inspirado em UI moderna de startups educacionais (SENAC, SENAI etc).
"""

# ==============================================================
# CORES PRINCIPAIS DA MARCA
# ==============================================================
AZUL_PRIMARIO = "#3C507D"        # Azul principal do logo SF
AZUL_ESCURO = "#112250"          # Texto e elementos escuros
AZUL_HOVER = "#2D3F66"           # Hover dos botoes azuis
AZUL_CLARO = "#5A7AB8"           # Detalhes e destaques
AZUL_SIDEBAR = "#1E2A47"         # Sidebar do dashboard

AMARELO_DOURADO = "#E0C58F"      # Amarelo do logo (campos)
AMARELO_VIBRANTE = "#F5C518"     # Amarelo vibrante para destaques
AMARELO_HOVER = "#D4B76B"        # Hover de elementos amarelos

# ==============================================================
# CORES NEUTRAS / BACKGROUND
# ==============================================================
BRANCO = "#FFFFFF"
BRANCO_GELO = "#FAFAFA"          # Fundo principal
CINZA_FUNDO = "#F4F6FA"          # Fundo dos cards
CINZA_CLARO = "#E5E9F0"          # Bordas suaves
CINZA_MEDIO = "#9CA3AF"          # Texto secundario
CINZA_ESCURO = "#4B5563"         # Texto principal claro
PRETO_TEXTO = "#1F2937"          # Texto preto suave

# ==============================================================
# CORES DE ESTADO / FEEDBACK
# ==============================================================
VERDE_SUCESSO = "#10B981"        # Sucesso, aprovado
VERDE_CLARO = "#D1FAE5"          # Background verde claro
VERMELHO_ERRO = "#EF4444"        # Erro, excluir
VERMELHO_CLARO = "#FEE2E2"       # Background vermelho claro
LARANJA_ALERTA = "#F59E0B"       # Aviso, pendente
LARANJA_CLARO = "#FEF3C7"        # Background laranja claro
ROXO_DESTAQUE = "#8B5CF6"        # Categorias especiais
ROSA_DESTAQUE = "#EC4899"        # Categorias especiais

# Lista de cores recomendada para graficos (ex: pizza, barras)
CORES_GRAFICOS = [
    AZUL_PRIMARIO,
    VERDE_SUCESSO,
    AMARELO_VIBRANTE,
    ROXO_DESTAQUE,
    ROSA_DESTAQUE,
    LARANJA_ALERTA,
    AZUL_CLARO,
]

# ==============================================================
# CORES DO FUNIL DE VENDAS
# ==============================================================
FUNIL_VISITANTES = "#3C507D"     # Azul - visitantes
FUNIL_LEADS = "#10B981"          # Verde - leads
FUNIL_NEGOCIACAO = "#F5C518"     # Amarelo - negociacao
FUNIL_VENDAS = "#8B5CF6"         # Roxo - vendas
FUNIL_ATIVOS = "#EC4899"         # Rosa - alunos ativos

# ==============================================================
# TIPOGRAFIA
# ==============================================================
# Fontes profissionais (com fallback caso nao estejam instaladas)
FONTE_TITULO = "Comic Sans MS"
FONTE_TEXTO = "Comic Sans MS"
FONTE_BOTAO = "Comic Sans MS"
FONTE_MONO = "Comic Sans MS"

# Tamanhos
TAM_TITULO_GRANDE = 28
TAM_TITULO = 20
TAM_SUBTITULO = 14
TAM_TEXTO = 11
TAM_PEQUENO = 9

# ==============================================================
# DIMENSOES E ESPACAMENTOS
# ==============================================================
RAIO_BORDA = 12
PADDING_PADRAO = 16
ALTURA_INPUT = 42
ALTURA_BOTAO = 44
LARGURA_SIDEBAR = 230
ALTURA_HEADER = 64
