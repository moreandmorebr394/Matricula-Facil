"""
Tema visual central do Sistema Fácil.

Concentra todas as cores, fontes e medidas usadas pela interface.
Manter um único ponto de verdade evita inconsistência entre telas.
"""
import tkinter.font as tkfont


# ---------------------------------------------------------------------
# Paleta principal (sempre 6 dígitos hex - sem canal alpha)
# ---------------------------------------------------------------------
AZUL_PRINCIPAL = "#3C507D"
AZUL_ESCURO = "#112250"
AZUL_HOVER = "#4F65A1"
AZUL_PRESS = "#2F406A"
AMARELO_DOURADO = "#F4C430"
AMARELO_INPUT = "#E0C58F"
AMARELO_INPUT_FOCO = "#EAD49E"

BRANCO_PURO = "#FFFFFF"
OFFWHITE = "#FAFAFA"
CINZA_CLARO = "#F1F2F6"
CINZA_BORDA = "#E4E6EE"
CINZA_TEXTO = "#6C7184"
CINZA_TITULO = "#2A2F45"

VERDE_SUCESSO = "#2BB673"
VERMELHO_ERRO = "#E74C3C"
LARANJA_ALERTA = "#F39C12"

# Cores específicas do funil
FUNIL_VISITANTES = "#3D7BC2"
FUNIL_LEADS = "#3FB16A"
FUNIL_NEGOCIACOES = "#F1C232"
FUNIL_VENDAS = "#9B59B6"
FUNIL_ATIVOS = "#E91E63"

# Cores do gráfico de origem
ORIGEM_CORES = (
    "#7E57C2", "#26A69A", "#42A5F5", "#3F51B5",
    "#FFA726", "#90A4AE",
)

# Sidebar
SIDEBAR_FUNDO = "#112250"
SIDEBAR_FUNDO_HOVER = "#1A2D5C"
SIDEBAR_TEXTO = "#FFFFFF"
SIDEBAR_TEXTO_INATIVO = "#A8B0CB"
SIDEBAR_ATIVO = "#3C507D"

# Status badges
COR_STATUS = {
    "LEAD": "#3D7BC2",
    "NEGOCIACAO": "#F1C232",
    "PAGO": "#2BB673",
    "NAO_PAGO": "#E74C3C",
    "ATIVO": "#9B59B6",
    "CANCELADO": "#6C7184",
}


# ---------------------------------------------------------------------
# Fontes
# ---------------------------------------------------------------------
def obter_fonte(tamanho=11, peso="normal"):
    """Retorna uma família de fonte moderna disponível no sistema.

    Tenta Inter, Segoe UI Variable, Segoe UI, SF Pro, Helvetica Neue
    e cai em Arial como último recurso.
    """
    candidatas = (
        "Inter", "Segoe UI Variable", "Segoe UI", "SF Pro Display",
        "Helvetica Neue", "Helvetica", "Arial",
    )
    disponiveis = set(tkfont.families())
    escolhida = "Arial"
    for fam in candidatas:
        if fam in disponiveis:
            escolhida = fam
            break
    return (escolhida, tamanho, peso)


def fonte_titulo(tamanho=22):
    return obter_fonte(tamanho, "bold")


def fonte_subtitulo(tamanho=13):
    return obter_fonte(tamanho, "normal")


def fonte_corpo(tamanho=11):
    return obter_fonte(tamanho, "normal")


def fonte_destaque(tamanho=11):
    return obter_fonte(tamanho, "bold")


# ---------------------------------------------------------------------
# Medidas padrão
# ---------------------------------------------------------------------
RAIO_BORDA = 14
PADDING_PADRAO = 16
PADDING_CARD = 24
ESPACAMENTO_CAMPO = 12
