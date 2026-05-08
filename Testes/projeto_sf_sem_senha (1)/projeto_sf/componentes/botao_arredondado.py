"""
Botão arredondado customizado em Canvas.

Tk não tem suporte nativo a bordas arredondadas; este componente
desenha um retângulo arredondado em um Canvas e responde a eventos
de hover/click com transições suaves.
"""
import tkinter as tk
from componentes import tema


class BotaoArredondado(tk.Canvas):

    def __init__(
        self,
        mestre,
        texto: str = "Botão",
        comando=None,
        cor_fundo: str = tema.AZUL_PRINCIPAL,
        cor_hover: str = tema.AZUL_HOVER,
        cor_press: str = tema.AZUL_PRESS,
        cor_texto: str = "#FFFFFF",
        largura: int = 220,
        altura: int = 44,
        raio: int = 14,
        fonte=None,
        **kwargs,
    ):
        super().__init__(
            mestre,
            width=largura,
            height=altura,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )
        self._texto = texto
        self._comando = comando
        self._cor_normal = cor_fundo
        self._cor_hover = cor_hover
        self._cor_press = cor_press
        self._cor_texto = cor_texto
        self._largura = largura
        self._altura = altura
        self._raio = raio
        self._fonte = fonte or tema.fonte_destaque(11)
        self._estado_atual = "normal"
        self._desabilitado = False

        # Faz o canvas adotar a cor do parent (transparência simulada)
        try:
            self.configure(bg=mestre.cget("bg"))
        except tk.TclError:
            pass

        self._desenhar(cor_fundo)
        self._registrar_eventos()

    # -----------------------------------------------------------------
    def _desenhar(self, cor: str):
        self.delete("all")
        l, a, r = self._largura, self._altura, self._raio
        # Polígono com cantos suaves (smooth=True)
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
            0, 0,
        ]
        self.create_polygon(
            pontos, smooth=True, fill=cor, outline=cor, tags="fundo",
        )
        self.create_text(
            l // 2,
            a // 2,
            text=self._texto,
            fill=self._cor_texto,
            font=self._fonte,
            tags="texto",
        )

    def _registrar_eventos(self):
        self.bind("<Enter>", self._ao_entrar)
        self.bind("<Leave>", self._ao_sair)
        self.bind("<Button-1>", self._ao_pressionar)
        self.bind("<ButtonRelease-1>", self._ao_soltar)

    def _ao_entrar(self, _evt=None):
        if self._desabilitado:
            return
        self.configure(cursor="hand2")
        self._desenhar(self._cor_hover)
        self._estado_atual = "hover"

    def _ao_sair(self, _evt=None):
        if self._desabilitado:
            return
        self.configure(cursor="")
        self._desenhar(self._cor_normal)
        self._estado_atual = "normal"

    def _ao_pressionar(self, _evt=None):
        if self._desabilitado:
            return
        self._desenhar(self._cor_press)
        self._estado_atual = "press"

    def _ao_soltar(self, _evt=None):
        if self._desabilitado:
            return
        self._desenhar(self._cor_hover)
        if callable(self._comando):
            try:
                self._comando()
            except Exception as exc:
                # Não derruba a UI - imprime no console
                print("[BotaoArredondado] erro no comando:", exc)

    # -----------------------------------------------------------------
    def alterar_texto(self, novo_texto: str):
        self._texto = novo_texto
        self.itemconfigure("texto", text=novo_texto)

    def desabilitar(self):
        self._desabilitado = True
        self._desenhar("#A0A8C0")
        self.itemconfigure("texto", fill="#FFFFFF")
        self.configure(cursor="")

    def habilitar(self):
        self._desabilitado = False
        self._desenhar(self._cor_normal)
        self.itemconfigure("texto", fill=self._cor_texto)
