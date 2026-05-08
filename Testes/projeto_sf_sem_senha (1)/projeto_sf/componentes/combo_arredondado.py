"""
Combobox arredondado seguindo o tema do sistema.

Usa ttk.Combobox com estilo customizado (não dá para arredondar canto
real do combobox no Tk, mas conseguimos um visual consistente).
"""
import tkinter as tk
from tkinter import ttk
from componentes import tema


class ComboArredondado(tk.Frame):

    _ESTILO_CRIADO = False

    def __init__(
        self,
        mestre,
        opcoes: list,
        valor_inicial: str = "",
        largura: int = 360,
        altura: int = 44,
        cor_fundo_pai: str = tema.OFFWHITE,
        cor_caixa: str = tema.AMARELO_INPUT,
        ao_alterar=None,
        **kwargs,
    ):
        super().__init__(mestre, bg=cor_fundo_pai, **kwargs)
        self.configure(width=largura, height=altura)
        self.pack_propagate(False)

        self._largura = largura
        self._altura = altura
        self._cor_caixa = cor_caixa

        # fundo arredondado (canvas)
        self._canvas = tk.Canvas(
            self,
            width=largura,
            height=altura,
            bg=cor_fundo_pai,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.place(x=0, y=0, width=largura, height=altura)
        self._desenhar_caixa()

        ComboArredondado._garantir_estilo()
        self._var = tk.StringVar(value=valor_inicial)
        self._combo = ttk.Combobox(
            self,
            textvariable=self._var,
            values=list(opcoes),
            font=tema.fonte_corpo(11),
            state="readonly",
            style="SF.TCombobox",
        )
        self._combo.place(x=12, y=4, width=largura - 24, height=altura - 8)
        if ao_alterar:
            self._combo.bind(
                "<<ComboboxSelected>>",
                lambda _e: ao_alterar(self._var.get()),
            )

    @classmethod
    def _garantir_estilo(cls):
        if cls._ESTILO_CRIADO:
            return
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure(
            "SF.TCombobox",
            fieldbackground=tema.AMARELO_INPUT,
            background=tema.AMARELO_INPUT,
            foreground=tema.AZUL_ESCURO,
            arrowcolor=tema.AZUL_ESCURO,
            bordercolor=tema.AMARELO_INPUT,
            lightcolor=tema.AMARELO_INPUT,
            darkcolor=tema.AMARELO_INPUT,
            selectbackground=tema.AMARELO_INPUT_FOCO,
            selectforeground=tema.AZUL_ESCURO,
            relief="flat",
            borderwidth=0,
        )
        estilo.map(
            "SF.TCombobox",
            fieldbackground=[("readonly", tema.AMARELO_INPUT)],
            background=[("readonly", tema.AMARELO_INPUT)],
            foreground=[("readonly", tema.AZUL_ESCURO)],
        )
        cls._ESTILO_CRIADO = True

    def _desenhar_caixa(self):
        self._canvas.delete("caixa")
        l, a, r = self._largura, self._altura, 12
        pontos = [
            r, 0, l - r, 0, l, 0, l, r,
            l, a - r, l, a, l - r, a, r, a,
            0, a, 0, a - r, 0, r, 0, 0,
        ]
        self._canvas.create_polygon(
            pontos,
            smooth=True,
            fill=self._cor_caixa,
            outline=self._cor_caixa,
            tags="caixa",
        )

    def obter_valor(self) -> str:
        return self._var.get()

    def definir_valor(self, valor: str):
        self._var.set(valor or "")

    def definir_opcoes(self, opcoes: list):
        self._combo.configure(values=list(opcoes))
