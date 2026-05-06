"""Botoes personalizados com animacao de hover.

Usa tk.Canvas para desenhar retangulos com cantos arredondados,
algo que o widget Button padrao do tkinter nao oferece.
"""
import tkinter as tk
from typing import Callable, Optional

from config.cores import Cores
from config.fontes import Fontes


class _BotaoArredondado(tk.Canvas):
    """Botao desenhado em Canvas com cantos arredondados e animacao de cor."""

    def __init__(
        self,
        master,
        texto: str = "",
        comando: Optional[Callable] = None,
        cor_fundo: str = Cores.BOTAO_PRIMARIO,
        cor_hover: str = Cores.BOTAO_PRIMARIO_HOVER,
        cor_texto: str = Cores.BRANCO,
        largura: int = 140,
        altura: int = 38,
        raio: int = 8,
        fonte=None,
        **kwargs,
    ):
        super().__init__(
            master,
            width=largura,
            height=altura,
            highlightthickness=0,
            bd=0,
            bg=master.cget("bg") if hasattr(master, "cget") else Cores.CARD_FUNDO,
            **kwargs,
        )

        self.texto = texto
        self.comando = comando
        self.cor_fundo = cor_fundo
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.cor_atual = cor_fundo
        self.largura = largura
        self.altura = altura
        self.raio = raio
        self.fonte = fonte or Fontes.BOTAO
        self._habilitado = True

        self._desenhar()
        self.bind("<Enter>", self._ao_entrar)
        self.bind("<Leave>", self._ao_sair)
        self.bind("<Button-1>", self._ao_clicar)
        self.bind("<ButtonRelease-1>", self._ao_soltar)

    def _desenhar_retangulo_arredondado(self, x1, y1, x2, y2, raio, cor, tag):
        # Sequencia de pontos para desenhar um retangulo com cantos arredondados
        pontos = [
            x1 + raio, y1,
            x1 + raio, y1,
            x2 - raio, y1,
            x2 - raio, y1,
            x2, y1,
            x2, y1 + raio,
            x2, y1 + raio,
            x2, y2 - raio,
            x2, y2 - raio,
            x2, y2,
            x2 - raio, y2,
            x2 - raio, y2,
            x1 + raio, y2,
            x1 + raio, y2,
            x1, y2,
            x1, y2 - raio,
            x1, y2 - raio,
            x1, y1 + raio,
            x1, y1 + raio,
            x1, y1,
        ]
        self.create_polygon(pontos, fill=cor, smooth=True, tags=tag, outline="")

    def _desenhar(self):
        self.delete("all")
        self._desenhar_retangulo_arredondado(
            1, 1, self.largura - 1, self.altura - 1, self.raio,
            self.cor_atual, "fundo",
        )
        self.create_text(
            self.largura / 2, self.altura / 2,
            text=self.texto, fill=self.cor_texto, font=self.fonte, tags="texto",
        )

    def _animar_para(self, cor_destino: str):
        # Animacao simples por etapas, sem dependencia externa.
        atual = self.cor_atual
        passos = 6
        deltas = self._calcular_deltas(atual, cor_destino, passos)
        self._aplicar_etapa(atual, cor_destino, deltas, 0, passos)

    def _calcular_deltas(self, c1, c2, passos):
        r1, g1, b1 = self._hex_para_rgb(c1)
        r2, g2, b2 = self._hex_para_rgb(c2)
        return [
            (r2 - r1) / passos,
            (g2 - g1) / passos,
            (b2 - b1) / passos,
        ]

    def _aplicar_etapa(self, inicial, final, deltas, etapa, passos):
        if etapa >= passos:
            self.cor_atual = final
            self._desenhar()
            return
        r0, g0, b0 = self._hex_para_rgb(inicial)
        r = int(r0 + deltas[0] * (etapa + 1))
        g = int(g0 + deltas[1] * (etapa + 1))
        b = int(b0 + deltas[2] * (etapa + 1))
        self.cor_atual = f"#{r:02x}{g:02x}{b:02x}"
        self._desenhar()
        self.after(15, lambda: self._aplicar_etapa(inicial, final, deltas, etapa + 1, passos))

    @staticmethod
    def _hex_para_rgb(hex_color: str):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def _ao_entrar(self, _evento):
        if not self._habilitado:
            return
        self.configure(cursor="hand2")
        self._animar_para(self.cor_hover)

    def _ao_sair(self, _evento):
        if not self._habilitado:
            return
        self.configure(cursor="")
        self._animar_para(self.cor_fundo)

    def _ao_clicar(self, _evento):
        if not self._habilitado:
            return
        # Pequeno "afunda"
        self.cor_atual = self.cor_hover
        self._desenhar()

    def _ao_soltar(self, _evento):
        if not self._habilitado:
            return
        self.cor_atual = self.cor_hover
        self._desenhar()
        if self.comando:
            self.comando()

    # API publica
    def configurar_texto(self, texto: str):
        self.texto = texto
        self._desenhar()

    def habilitar(self, habilitado: bool = True):
        self._habilitado = habilitado
        if habilitado:
            self.cor_atual = self.cor_fundo
        else:
            self.cor_atual = "#94a3b8"
        self._desenhar()


class BotaoPrimario(_BotaoArredondado):
    def __init__(self, master, texto="Confirmar", comando=None, **kwargs):
        super().__init__(
            master, texto=texto, comando=comando,
            cor_fundo=Cores.BOTAO_PRIMARIO,
            cor_hover=Cores.BOTAO_PRIMARIO_HOVER,
            cor_texto=Cores.BRANCO, **kwargs,
        )


class BotaoSecundario(_BotaoArredondado):
    def __init__(self, master, texto="Cancelar", comando=None, **kwargs):
        super().__init__(
            master, texto=texto, comando=comando,
            cor_fundo=Cores.BOTAO_SECUNDARIO,
            cor_hover=Cores.BOTAO_SECUNDARIO_HOVER,
            cor_texto=Cores.BOTAO_SECUNDARIO_TEXTO, **kwargs,
        )


class BotaoSucesso(_BotaoArredondado):
    def __init__(self, master, texto="Salvar", comando=None, **kwargs):
        super().__init__(
            master, texto=texto, comando=comando,
            cor_fundo=Cores.BOTAO_SUCESSO,
            cor_hover=Cores.BOTAO_SUCESSO_HOVER,
            cor_texto=Cores.BRANCO, **kwargs,
        )


class BotaoPerigo(_BotaoArredondado):
    def __init__(self, master, texto="Excluir", comando=None, **kwargs):
        super().__init__(
            master, texto=texto, comando=comando,
            cor_fundo=Cores.BOTAO_PERIGO,
            cor_hover=Cores.BOTAO_PERIGO_HOVER,
            cor_texto=Cores.BRANCO, **kwargs,
        )


class BotaoIcone(tk.Canvas):
    """Botao circular desenhado em Canvas (para icones de header)."""

    def __init__(self, master, simbolo="?", comando=None, tamanho=38,
                 cor_fundo="#f1f5f9", cor_hover="#e2e8f0",
                 cor_texto=Cores.TEXTO_PRIMARIO, fonte=None,
                 badge_texto: Optional[str] = None,
                 cor_badge: str = "#ef4444", **kwargs):
        super().__init__(
            master, width=tamanho, height=tamanho,
            highlightthickness=0, bd=0,
            bg=master.cget("bg") if hasattr(master, "cget") else Cores.HEADER_FUNDO,
            **kwargs,
        )
        self.simbolo = simbolo
        self.comando = comando
        self.tamanho = tamanho
        self.cor_fundo = cor_fundo
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.fonte = fonte or (Fontes.FAMILIA, 16)
        self.cor_atual = cor_fundo
        self.badge_texto = badge_texto
        self.cor_badge = cor_badge

        self._desenhar()
        self.bind("<Enter>", self._ao_entrar)
        self.bind("<Leave>", self._ao_sair)
        self.bind("<Button-1>", self._ao_clicar)

    def _desenhar(self):
        self.delete("all")
        s = self.tamanho
        self.create_oval(2, 2, s - 2, s - 2, fill=self.cor_atual, outline="")
        self.create_text(
            s / 2, s / 2 + 1, text=self.simbolo,
            fill=self.cor_texto, font=self.fonte,
        )
        if self.badge_texto:
            r = 9
            cx, cy = s - r - 1, r + 1
            self.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=self.cor_badge, outline=Cores.HEADER_FUNDO, width=2,
            )
            self.create_text(
                cx, cy, text=self.badge_texto,
                fill=Cores.BRANCO, font=(Fontes.FAMILIA, 8, "bold"),
            )

    def atualizar_badge(self, texto: Optional[str]):
        self.badge_texto = texto if texto and texto != "0" else None
        self._desenhar()

    def _ao_entrar(self, _e):
        self.cor_atual = self.cor_hover
        self.configure(cursor="hand2")
        self._desenhar()

    def _ao_sair(self, _e):
        self.cor_atual = self.cor_fundo
        self.configure(cursor="")
        self._desenhar()

    def _ao_clicar(self, _e):
        if self.comando:
            self.comando()
