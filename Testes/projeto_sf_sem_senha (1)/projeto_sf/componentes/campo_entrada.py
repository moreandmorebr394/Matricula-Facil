"""
Campo de entrada arredondado.

Compõe um Canvas (para o fundo arredondado) com um Entry/Text dentro.
Possui placeholder, ícone opcional, indicador de erro e mostrar/ocultar
senha.
"""
import tkinter as tk
from componentes import tema


class CampoArredondado(tk.Frame):

    def __init__(
        self,
        mestre,
        placeholder: str = "",
        senha: bool = False,
        icone: str = "",          # caractere unicode opcional
        largura: int = 360,
        altura: int = 44,
        raio: int = 12,
        cor_fundo_pai: str = tema.OFFWHITE,
        cor_caixa: str = tema.AMARELO_INPUT,
        cor_caixa_foco: str = tema.AMARELO_INPUT_FOCO,
        cor_texto: str = tema.AZUL_ESCURO,
        cor_placeholder: str = "#7F6E47",
        permitir_toggle_senha: bool = True,
        **kwargs,
    ):
        super().__init__(mestre, bg=cor_fundo_pai, **kwargs)
        self._placeholder = placeholder
        self._senha = senha
        self._cor_caixa = cor_caixa
        self._cor_caixa_foco = cor_caixa_foco
        self._cor_texto = cor_texto
        self._cor_placeholder = cor_placeholder
        self._cor_fundo_pai = cor_fundo_pai
        self._largura = largura
        self._altura = altura
        self._raio = raio
        self._mostrar_senha = False
        self._tem_erro = False
        self._icone = icone
        self._permitir_toggle = permitir_toggle_senha and senha

        self.configure(width=largura, height=altura)
        self.pack_propagate(False)

        # Canvas com forma arredondada
        self._canvas = tk.Canvas(
            self,
            width=largura,
            height=altura,
            bg=cor_fundo_pai,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.place(x=0, y=0, width=largura, height=altura)
        self._desenhar_caixa(cor_caixa)

        # Frame interno transparente que conterá ícone+entry
        self._interno = tk.Frame(self, bg=cor_caixa)
        margem_esq = 14 if not icone else 38
        margem_dir = 14 if not self._permitir_toggle else 38
        self._interno.place(
            x=margem_esq,
            y=2,
            width=largura - margem_esq - margem_dir,
            height=altura - 4,
        )

        # Ícone (se houver)
        self._lbl_icone = None
        if icone:
            self._lbl_icone = tk.Label(
                self,
                text=icone,
                bg=cor_caixa,
                fg=tema.AZUL_ESCURO,
                font=tema.obter_fonte(13, "normal"),
            )
            self._lbl_icone.place(x=12, y=altura // 2, anchor="w")

        # Entry
        self._var = tk.StringVar()
        self._entry = tk.Entry(
            self._interno,
            textvariable=self._var,
            bd=0,
            relief="flat",
            bg=cor_caixa,
            fg=cor_placeholder,
            insertbackground=cor_texto,
            font=tema.fonte_corpo(11),
            highlightthickness=0,
        )
        if senha:
            # Não usar show='*' enquanto exibindo placeholder
            pass
        self._entry.pack(fill="both", expand=True)
        self._entry.insert(0, placeholder)
        self._entry.bind("<FocusIn>", self._ao_focar)
        self._entry.bind("<FocusOut>", self._ao_desfocar)

        # Botão olho para senha
        self._btn_olho = None
        if self._permitir_toggle:
            self._btn_olho = tk.Label(
                self,
                text="\u25CF\u25CF",   # ●● representa "ocultar"
                bg=cor_caixa,
                fg=tema.AZUL_ESCURO,
                font=tema.obter_fonte(10, "bold"),
                cursor="hand2",
            )
            self._btn_olho.place(
                x=largura - 14, y=altura // 2, anchor="e",
            )
            self._btn_olho.bind("<Button-1>", self._alternar_visualizacao_senha)

    # ------------------------------------------------------------- visual
    def _desenhar_caixa(self, cor: str):
        self._canvas.delete("caixa")
        l, a, r = self._largura, self._altura, self._raio
        pontos = [
            r, 0, l - r, 0, l, 0, l, r,
            l, a - r, l, a, l - r, a, r, a,
            0, a, 0, a - r, 0, r, 0, 0,
        ]
        self._canvas.create_polygon(
            pontos, smooth=True, fill=cor, outline=cor, tags="caixa",
        )
        # repinta filhos
        for w in (
            getattr(self, "_interno", None),
            getattr(self, "_entry", None),
            getattr(self, "_lbl_icone", None),
            getattr(self, "_btn_olho", None),
        ):
            if w is not None:
                try:
                    w.configure(bg=cor)
                except tk.TclError:
                    pass

    # ------------------------------------------------------------- foco
    def _ao_focar(self, _evt=None):
        if self._var.get() == self._placeholder and not self._tem_erro:
            self._var.set("")
            self._entry.configure(fg=self._cor_texto)
            if self._senha:
                self._entry.configure(show="*")
        self._desenhar_caixa(self._cor_caixa_foco)

    def _ao_desfocar(self, _evt=None):
        if not self._var.get():
            self._entry.configure(show="", fg=self._cor_placeholder)
            self._var.set(self._placeholder)
        self._desenhar_caixa(self._cor_caixa)

    def _alternar_visualizacao_senha(self, _evt=None):
        if self._var.get() == self._placeholder:
            return
        self._mostrar_senha = not self._mostrar_senha
        self._entry.configure(show="" if self._mostrar_senha else "*")
        if self._btn_olho:
            self._btn_olho.configure(
                text="\u00D7\u00D7" if self._mostrar_senha else "\u25CF\u25CF",
            )

    # -------------------------------------------------------- API pública
    def obter_valor(self) -> str:
        v = self._var.get()
        if v == self._placeholder:
            return ""
        return v

    def definir_valor(self, valor: str):
        self._var.set(valor or "")
        if valor:
            self._entry.configure(fg=self._cor_texto)
            if self._senha:
                self._entry.configure(show="*")
        else:
            self._entry.configure(show="", fg=self._cor_placeholder)
            self._var.set(self._placeholder)

    def marcar_erro(self):
        self._tem_erro = True
        self._desenhar_caixa("#FBE0E0")

    def limpar_erro(self):
        self._tem_erro = False
        self._desenhar_caixa(self._cor_caixa)

    def variavel(self) -> tk.StringVar:
        return self._var

    def widget_entry(self) -> tk.Entry:
        return self._entry
