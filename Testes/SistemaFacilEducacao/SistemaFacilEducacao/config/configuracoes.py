"""Configuracoes gerais do aplicativo."""
import os


class Configuracoes:
    NOME_SISTEMA = "Sistema Facil Educacao"
    VERSAO = "1.0.0"

    # Janela
    LARGURA_INICIAL = 1400
    ALTURA_INICIAL = 820
    LARGURA_MINIMA = 1200
    ALTURA_MINIMA = 700
    TITULO_JANELA = "Sistema Facil Educacao - CRM Educacional"

    # Sidebar
    LARGURA_SIDEBAR = 220

    # Header
    ALTURA_HEADER = 70

    # Animacoes
    DURACAO_ANIMACAO_MS = 180
    INTERVALO_ANIMACAO_MS = 15

    # Caminhos
    PASTA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PASTA_RECURSOS = os.path.join(PASTA_RAIZ, "recursos")
    PASTA_DADOS = os.path.join(PASTA_RAIZ, "dados_armazenados")
    LOGO_PEQUENO = os.path.join(PASTA_RECURSOS, "logo_sf_pequeno.png")
    LOGO_MEDIO = os.path.join(PASTA_RECURSOS, "logo_sf_medio.png")
    LOGO_ORIGINAL = os.path.join(PASTA_RECURSOS, "logo_sf.png")

    # Usuario administrador padrao
    USUARIO_NOME = "Administrador"
    USUARIO_EMAIL = "admin@sistemafacil.com"
