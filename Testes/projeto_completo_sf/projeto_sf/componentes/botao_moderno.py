"""
Botao moderno com bordas arredondadas, hover e clique animados.

Usa Canvas para desenhar bordas arredondadas (Tkinter padrao nao suporta).
"""
import tkinter as tk
from componentes.cores import (
    AZUL_PRIMARIO, AZUL_HOVER, BRANCO, FONTE_BOTAO, ALTURA_BOTAO
)


class BotaoModerno(tk.Canvas):
    """
    Botao com bordas arredondadas, animacao de hover e cor customizavel.

    Args:
        master: widget pai
        texto: texto do botao
        comando: callback ao clicar
        largura, altura: dimensoes em pixels
        cor_normal, cor_hover: cores de fundo
        cor_texto: cor do texto
        raio: raio das bordas arredondadas
        fonte_tamanho: tamanho da fonte
    """

    def __init__(self, master, texto="Botao", comando=None,
                 largura=200, altura=ALTURA_BOTAO,
                 cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                 cor_texto=BRANCO, raio=12, fonte_tamanho=11,
                 cor_fundo=None, **kwargs):

        # Detecta cor de fundo do pai automaticamente
        if cor_fundo is None:
            try:
                cor_fundo = master.cget("bg")
            except Exception:
                cor_fundo = BRANCO

        super().__init__(
            master,
            width=largura,
            height=altura,
            bg=cor_fundo,
            highlightthickness=0,
            bd=0,
            **kwargs
        )

        self.texto = texto
        self.comando = comando
        self.largura = largura
        self.altura = altura
        self.cor_normal = cor_normal
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.raio = raio
        self.fonte_tamanho = fonte_tamanho
        self._estado_hover = False
        self._habilitado = True

        self._desenhar(self.cor_normal)

        self.bind("<Enter>", self._ao_entrar)
        self.bind("<Leave>", self._ao_sair)
        self.bind("<Button-1>", self._ao_clicar)
        self.bind("<ButtonRelease-1>", self._ao_soltar)
        self.configure(cursor="hand2")

    def _desenhar(self, cor):
        """Desenha o botao com bordas arredondadas usando poligono suavizado."""
        self.delete("all")
        l, a, r = self.largura, self.altura, self.raio
        # Limita raio
        r = min(r, a // 2, l // 2)

        # Pontos do poligono arredondado
        pontos = [
            r, 0,
            l - r, 0,
            l, 0,
            l, r,
            l, a - r,
            l, a,
            l - r, a,
            r, a,
            0, a,
            0, a - r,
            0, r,
            0, 0
        ]
        self.create_polygon(pontos, fill=cor, outline=cor, smooth=True)

        # Texto centralizado
        self.create_text(
            l / 2, a / 2,
            text=self.texto,
            fill=self.cor_texto,
            font=(FONTE_BOTAO, self.fonte_tamanho, "bold")
        )

    def _ao_entrar(self, evento=None):
        if self._habilitado:
            self._estado_hover = True
            self._desenhar(self.cor_hover)

    def _ao_sair(self, evento=None):
        if self._habilitado:
            self._estado_hover = False
            self._desenhar(self.cor_normal)

    def _ao_clicar(self, evento=None):
        if self._habilitado:
            # Pequena animacao de "press"
            self._desenhar(self.cor_hover)

    def _ao_soltar(self, evento=None):
        if self._habilitado and self.comando:
            cor_final = self.cor_hover if self._estado_hover else self.cor_normal
            self._desenhar(cor_final)
            try:
                self.comando()
            except Exception as e:
                print(f"[Erro no botao] {e}")

    def configurar_texto(self, novo_texto):
        """Permite mudar o texto do botao em tempo de execucao."""
        self.texto = novo_texto
        cor = self.cor_hover if self._estado_hover else self.cor_normal
        self._desenhar(cor)

    def desabilitar(self):
        self._habilitado = False
        self.configure(cursor="")
        self._desenhar("#9CA3AF")

    def habilitar(self):
        self._habilitado = True
        self.configure(cursor="hand2")
        self._desenhar(self.cor_normal)
