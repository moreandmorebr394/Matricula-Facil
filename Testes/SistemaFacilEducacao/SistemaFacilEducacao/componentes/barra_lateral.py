"""Barra lateral fixa com navegacao principal.

Contem:
- Logo SF
- Lista de itens com icones (caracteres simbolicos) + texto
- Indicador visual do item ativo
- Animacao suave em hover
- Badge "Novo" no item Funil de Origem
"""
import tkinter as tk
from typing import Callable, Optional

from config.configuracoes import Configuracoes
from config.cores import Cores
from config.fontes import Fontes


class _ItemSidebar(tk.Canvas):
    """Item individual da barra lateral - desenhado em canvas para
    permitir cantos arredondados e badges customizados."""

    def __init__(self, master, simbolo: str, rotulo: str,
                 chave: str, ao_clicar: Callable,
                 badge: Optional[str] = None, ativo: bool = False):
        super().__init__(
            master,
            width=Configuracoes.LARGURA_SIDEBAR - 24,
            height=42,
            highlightthickness=0, bd=0,
            bg=Cores.SIDEBAR_FUNDO,
        )
        self.simbolo = simbolo
        self.rotulo = rotulo
        self.chave = chave
        self.ao_clicar = ao_clicar
        self.badge = badge
        self.ativo = ativo

        self._desenhar()
        self.bind("<Enter>", self._entrar)
        self.bind("<Leave>", self._sair)
        self.bind("<Button-1>", self._clicar)

    def _desenhar(self):
        self.delete("all")
        largura = int(self["width"])
        altura = int(self["height"])

        if self.ativo:
            cor_fundo = Cores.SIDEBAR_ATIVO
            cor_texto = Cores.SIDEBAR_TEXTO_ATIVO
        else:
            cor_fundo = Cores.SIDEBAR_FUNDO
            cor_texto = Cores.SIDEBAR_TEXTO

        if self.ativo:
            raio = 9
            pontos = [
                raio, 0, largura - raio, 0,
                largura, 0, largura, raio,
                largura, altura - raio, largura, altura,
                largura - raio, altura, raio, altura,
                0, altura, 0, altura - raio,
                0, raio, 0, 0,
            ]
            self.create_polygon(pontos, fill=cor_fundo, smooth=True, outline="")

        # Icone (caracter simbolico)
        self.create_text(
            22, altura / 2, text=self.simbolo, fill=cor_texto,
            font=(Fontes.FAMILIA, 14), anchor="center",
        )
        # Rotulo
        self.create_text(
            48, altura / 2, text=self.rotulo, fill=cor_texto,
            font=Fontes.SIDEBAR_ITEM, anchor="w",
        )

        # Badge "Novo"
        if self.badge:
            largura_badge = 14 + len(self.badge) * 6
            x_inicio = largura - largura_badge - 14
            r = 9
            pontos_b = [
                x_inicio + r, altura / 2 - r,
                x_inicio + largura_badge - r, altura / 2 - r,
                x_inicio + largura_badge, altura / 2 - r,
                x_inicio + largura_badge, altura / 2,
                x_inicio + largura_badge, altura / 2 + r,
                x_inicio + largura_badge - r, altura / 2 + r,
                x_inicio + r, altura / 2 + r,
                x_inicio, altura / 2 + r,
                x_inicio, altura / 2,
                x_inicio, altura / 2 - r,
            ]
            self.create_polygon(pontos_b, fill=Cores.BADGE_NOVO_FUNDO,
                                smooth=True, outline="")
            self.create_text(
                x_inicio + largura_badge / 2, altura / 2,
                text=self.badge, fill=Cores.BADGE_NOVO_TEXTO,
                font=Fontes.BADGE,
            )

    def _entrar(self, _e):
        if not self.ativo:
            self.configure(bg=Cores.SIDEBAR_HOVER)
            self._redesenhar_fundo_hover()
        self.configure(cursor="hand2")

    def _sair(self, _e):
        self.configure(bg=Cores.SIDEBAR_FUNDO)
        self.configure(cursor="")
        self._desenhar()

    def _redesenhar_fundo_hover(self):
        self.delete("all")
        largura = int(self["width"])
        altura = int(self["height"])
        raio = 9
        pontos = [
            raio, 0, largura - raio, 0,
            largura, 0, largura, raio,
            largura, altura - raio, largura, altura,
            largura - raio, altura, raio, altura,
            0, altura, 0, altura - raio,
            0, raio, 0, 0,
        ]
        self.create_polygon(pontos, fill=Cores.SIDEBAR_HOVER, smooth=True, outline="")
        self.create_text(22, altura / 2, text=self.simbolo,
                         fill=Cores.SIDEBAR_TEXTO_ATIVO,
                         font=(Fontes.FAMILIA, 14), anchor="center")
        self.create_text(48, altura / 2, text=self.rotulo,
                         fill=Cores.SIDEBAR_TEXTO_ATIVO,
                         font=Fontes.SIDEBAR_ITEM, anchor="w")
        if self.badge:
            self._redesenhar_badge(largura, altura)

    def _redesenhar_badge(self, largura, altura):
        largura_badge = 14 + len(self.badge) * 6
        x_inicio = largura - largura_badge - 14
        r = 9
        pontos_b = [
            x_inicio + r, altura / 2 - r,
            x_inicio + largura_badge - r, altura / 2 - r,
            x_inicio + largura_badge, altura / 2 - r,
            x_inicio + largura_badge, altura / 2,
            x_inicio + largura_badge, altura / 2 + r,
            x_inicio + largura_badge - r, altura / 2 + r,
            x_inicio + r, altura / 2 + r,
            x_inicio, altura / 2 + r,
            x_inicio, altura / 2,
            x_inicio, altura / 2 - r,
        ]
        self.create_polygon(pontos_b, fill=Cores.BADGE_NOVO_FUNDO,
                            smooth=True, outline="")
        self.create_text(
            x_inicio + largura_badge / 2, altura / 2,
            text=self.badge, fill=Cores.BADGE_NOVO_TEXTO, font=Fontes.BADGE,
        )

    def _clicar(self, _e):
        if self.ao_clicar:
            self.ao_clicar(self.chave)

    def definir_ativo(self, ativo: bool):
        self.ativo = ativo
        self._desenhar()


class BarraLateral(tk.Frame):
    """Barra lateral completa, com logo, navegacao e botao Sair."""

    # Cada item: (chave, simbolo, rotulo, badge)
    ITENS = [
        ("dashboard", "⌂", "Dashboard", None),
        ("leads", "👥", "Leads / Alunos", None),
        ("vendas", "🛒", "Vendas", None),
        ("pagamentos", "💳", "Pagamentos", None),
        ("turmas", "🎓", "Turmas", None),
        ("aulas", "📘", "Aulas", None),
        ("frequencia", "📅", "Frequencia", None),
        ("funil", "▼", "Funil de Origem", "novo"),
        ("relatorios", "📊", "Relatorios", None),
        ("configuracoes", "⚙", "Configuracoes", None),
    ]

    def __init__(self, master, ao_navegar: Callable[[str], None],
                 ao_sair: Callable[[], None], logo_imagem=None):
        super().__init__(
            master, bg=Cores.SIDEBAR_FUNDO,
            width=Configuracoes.LARGURA_SIDEBAR,
        )
        self.pack_propagate(False)
        self.ao_navegar = ao_navegar
        self.ao_sair_callback = ao_sair
        self.itens_widgets = {}

        self._construir_logo(logo_imagem)
        self._construir_itens()
        self._construir_botao_sair()

    def _construir_logo(self, imagem):
        topo = tk.Frame(self, bg=Cores.SIDEBAR_GRADIENTE, height=80)
        topo.pack(fill="x")
        topo.pack_propagate(False)

        wrapper = tk.Frame(topo, bg=Cores.SIDEBAR_GRADIENTE)
        wrapper.pack(side="left", padx=14, pady=14)

        if imagem is not None:
            self._referencia_logo = imagem
            tk.Label(
                wrapper, image=imagem, bg=Cores.SIDEBAR_GRADIENTE, bd=0,
            ).pack(side="left")
        else:
            # Fallback: caixa SF estilizada
            cnv = tk.Canvas(wrapper, width=48, height=48,
                            highlightthickness=0, bd=0,
                            bg=Cores.SIDEBAR_GRADIENTE)
            cnv.pack(side="left")
            cnv.create_oval(2, 2, 46, 46, fill=Cores.LOGO_AZUL, outline="")
            cnv.create_text(24, 24, text="SF", fill=Cores.LOGO_AMARELO,
                            font=(Fontes.FAMILIA, 16, "bold"))
            self._referencia_logo = None

        textos = tk.Frame(topo, bg=Cores.SIDEBAR_GRADIENTE)
        textos.pack(side="left", pady=14)
        tk.Label(
            textos, text="Sistema Facil",
            bg=Cores.SIDEBAR_GRADIENTE, fg=Cores.BRANCO,
            font=Fontes.LOGO_TEXTO,
        ).pack(anchor="w")
        tk.Label(
            textos, text="Educacao",
            bg=Cores.SIDEBAR_GRADIENTE, fg=Cores.LOGO_AMARELO,
            font=Fontes.LOGO_SUBTEXTO,
        ).pack(anchor="w")

        # Linha divisoria
        tk.Frame(self, bg=Cores.SIDEBAR_DIVISOR, height=1).pack(fill="x")

    def _construir_itens(self):
        container = tk.Frame(self, bg=Cores.SIDEBAR_FUNDO)
        container.pack(fill="both", expand=True, padx=12, pady=10)

        for chave, simbolo, rotulo, badge in self.ITENS:
            item = _ItemSidebar(
                container,
                simbolo=simbolo, rotulo=rotulo,
                chave=chave, ao_clicar=self._ao_clicar_item,
                badge=badge, ativo=(chave == "dashboard"),
            )
            item.pack(pady=2)
            self.itens_widgets[chave] = item

    def _construir_botao_sair(self):
        rodape = tk.Frame(self, bg=Cores.SIDEBAR_FUNDO)
        rodape.pack(side="bottom", fill="x", padx=12, pady=14)

        # Linha divisoria
        tk.Frame(rodape, bg=Cores.SIDEBAR_DIVISOR, height=1).pack(
            fill="x", pady=(0, 10)
        )

        sair = _ItemSidebar(
            rodape, simbolo="⎋", rotulo="Sair",
            chave="sair", ao_clicar=lambda _: self.ao_sair_callback(),
            badge=None, ativo=False,
        )
        sair.pack()

    def _ao_clicar_item(self, chave: str):
        self.definir_ativo(chave)
        self.ao_navegar(chave)

    def definir_ativo(self, chave: str):
        for nome, item in self.itens_widgets.items():
            item.definir_ativo(nome == chave)
