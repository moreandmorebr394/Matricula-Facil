# ============================================================
# configuracoes.py — Cores, fontes e constantes do Sistema Fácil
# ============================================================

# ── Paleta de cores ──────────────────────────────────────────
AZUL_ESCURO    = "#112250"
AZUL_MEDIO     = "#3C507D"
AZUL_CLARO     = "#4A6199"
AZUL_BOTAO     = "#2E4068"
AZUL_HOVER     = "#4D6BA3"
DOURADO        = "#E0C58F"
DOURADO_ESCURO = "#C9A85C"
DOURADO_CLARO  = "#F0D9A8"
BRANCO         = "#FFFFFF"
OFF_WHITE      = "#FAFAFA"
CINZA_CLARO    = "#E8E8E8"
CINZA_TEXTO    = "#7A8299"
VERMELHO_ERRO  = "#D94F4F"
VERDE_SUCESSO  = "#4CAF50"

# ── Fontes ───────────────────────────────────────────────────
# Família principal (disponível em Windows/Mac/Linux)
FONTE_FAMILIA      = "Segoe UI"
FONTE_ALTERNATIVA  = "Helvetica"
FONTE_FALLBACK     = "Arial"

# Tamanhos
FONTE_TITULO       = 28
FONTE_SUBTITULO    = 14
FONTE_CAMPO        = 13
FONTE_BOTAO        = 15
FONTE_LINK         = 12
FONTE_FRASE_GRANDE = 32
FONTE_SUBTEXTO     = 13

# ── Dimensões ────────────────────────────────────────────────
LARGURA_JANELA  = 1100
ALTURA_JANELA   = 680
RAIO_BORDA      = 12
PADDING_CAMPOS  = 15

# ── Textos ───────────────────────────────────────────────────
TEXTOS = {
    "registro": {
        "titulo": "Crie sua conta",
        "subtitulo": "Comece sua jornada no Sistema Fácil",
        "botao": "Cadastrar",
        "link_principal": "Já tem uma conta?",
        "link_acao": "Entrar",
        "link_ajuda": "Precisa de ajuda?",
        "aviso": "Todos os campos são obrigatórios",
        "frase_visual": "Seu futuro começa\ncom uma escolha\nsimples",
        "subtexto_visual": (
            "Descubra novas oportunidades, desenvolva\n"
            "habilidades e faça parte de uma comunidade\n"
            "de aprendizado moderna."
        ),
    },
    "login": {
        "titulo": "Faça login na\nsua conta",
        "subtitulo": "Acesse sua conta",
        "botao": "Entrar",
        "link_principal": "Não tem uma conta?",
        "link_acao": "Cadastre-se",
        "link_esqueceu": "Esqueci minha senha",
        "link_google": "Entrar com Google",
        "frase_visual": "Bem-vindo de volta\nao Sistema Fácil",
        "subtexto_visual": (
            "Acesse sua conta e continue\n"
            "sua jornada de aprendizado"
        ),
    },
}
