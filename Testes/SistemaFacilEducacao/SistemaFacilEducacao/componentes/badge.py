"""Badge: pequeno selo colorido para indicar status."""
import tkinter as tk

from config.cores import Cores
from config.fontes import Fontes


class Badge(tk.Canvas):
    """Selo arredondado para exibir status (ex: LEAD, PAGO, NOVO)."""

    MAPEAMENTO = {
        "LEAD": (Cores.STATUS_LEAD_FUNDO, Cores.STATUS_LEAD_TEXTO),
        "NEGOCIACAO": (Cores.STATUS_NEGOCIACAO_FUNDO, Cores.STATUS_NEGOCIACAO_TEXTO),
        "PAGO": (Cores.STATUS_PAGO_FUNDO, Cores.STATUS_PAGO_TEXTO),
        "NAO_PAGO": (Cores.STATUS_NAO_PAGO_FUNDO, Cores.STATUS_NAO_PAGO_TEXTO),
        "NAO PAGO": (Cores.STATUS_NAO_PAGO_FUNDO, Cores.STATUS_NAO_PAGO_TEXTO),
        "ALUNO_ATIVO": (Cores.STATUS_PAGO_FUNDO, Cores.STATUS_PAGO_TEXTO),
        "ATIVO": (Cores.STATUS_PAGO_FUNDO, Cores.STATUS_PAGO_TEXTO),
        "NOVO": (Cores.BADGE_NOVO_FUNDO, Cores.BADGE_NOVO_TEXTO),
        "INFO": (Cores.STATUS_LEAD_FUNDO, Cores.STATUS_LEAD_TEXTO),
        "SUCESSO": (Cores.STATUS_PAGO_FUNDO, Cores.STATUS_PAGO_TEXTO),
        "AVISO": (Cores.STATUS_NEGOCIACAO_FUNDO, Cores.STATUS_NEGOCIACAO_TEXTO),
        "ERRO": (Cores.STATUS_NAO_PAGO_FUNDO, Cores.STATUS_NAO_PAGO_TEXTO),
    }

    def __init__(self, master, texto: str, status: str = None,
                 cor_fundo: str = None, cor_texto: str = None,
                 cor_canvas: str = None, fonte=None, **kwargs):
        self.texto = texto.upper()
        chave = (status or texto).upper().replace("Ã", "A").replace("Ç", "C")
        if chave in self.MAPEAMENTO:
            self.cor_fundo, self.cor_texto = self.MAPEAMENTO[chave]
        else:
            self.cor_fundo = cor_fundo or Cores.STATUS_LEAD_FUNDO
            self.cor_texto = cor_texto or Cores.STATUS_LEAD_TEXTO
        self.fonte = fonte or Fontes.BADGE

        # Calcula largura aproximada
        largura = max(48, 16 + len(self.texto) * 7)
        altura = 22

        bg = cor_canvas
        if bg is None and hasattr(master, "cget"):
            try:
                bg = master.cget("bg")
            except Exception:
                bg = Cores.CARD_FUNDO
        bg = bg or Cores.CARD_FUNDO

        super().__init__(
            master, width=largura, height=altura,
            highlightthickness=0, bd=0, bg=bg, **kwargs,
        )
        self._desenhar(largura, altura)

    def _desenhar(self, largura, altura):
        # Retangulo arredondado com create_polygon smooth
        raio = altura / 2
        pontos = [
            raio, 0, largura - raio, 0,
            largura, 0, largura, raio,
            largura, altura - raio, largura, altura,
            largura - raio, altura, raio, altura,
            0, altura, 0, altura - raio,
            0, raio, 0, 0,
        ]
        self.create_polygon(pontos, fill=self.cor_fundo, smooth=True, outline="")
        self.create_text(
            largura / 2, altura / 2 + 1, text=self.texto,
            fill=self.cor_texto, font=self.fonte,
        )
