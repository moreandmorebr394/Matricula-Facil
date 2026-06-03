"""
Campo de entrada (Input) moderno com bordas arredondadas, label,
icone e suporte a mostrar/ocultar senha.
"""
import tkinter as tk
from componentes.cores import (
    AMARELO_DOURADO, BRANCO, AZUL_PRIMARIO, CINZA_MEDIO, CINZA_ESCURO,
    PRETO_TEXTO, FONTE_TEXTO, AZUL_ESCURO, CINZA_CLARO
)


class CampoEntrada(tk.Frame):
    """
    Campo de entrada moderno com label superior, bordas arredondadas
    e suporte a icone e mostrar/ocultar senha.

    Args:
        master: widget pai
        label: texto do label superior
        icone: emoji ou caractere usado como icone (string)
        senha: True para campo de senha (com botao mostrar)
        largura: largura em pixels
        cor_fundo_pai: cor de fundo do pai
        cor_campo: cor do campo (default amarelo dourado)
        placeholder: texto cinza dentro quando vazio
    """

    def __init__(self, master, label="Campo", icone="",
                 senha=False, largura=380,
                 cor_fundo_pai=BRANCO, cor_campo=AMARELO_DOURADO,
                 placeholder="", **kwargs):
        super().__init__(master, bg=cor_fundo_pai, **kwargs)

        self.label_texto = label
        self.icone = icone
        self.senha = senha
        self.largura = largura
        self.cor_fundo_pai = cor_fundo_pai
        self.cor_campo = cor_campo
        self.placeholder = placeholder
        self._mostrando_senha = False

        # Label superior
        self.lbl = tk.Label(
            self, text=label,
            font=(FONTE_TEXTO, 10, "bold"),
            fg=AZUL_ESCURO, bg=cor_fundo_pai, anchor="w"
        )
        self.lbl.pack(fill="x", padx=4, pady=(0, 4))

        # Container do campo (Canvas para borda arredondada)
        self.altura_campo = 44
        self.canvas = tk.Canvas(
            self, width=largura, height=self.altura_campo,
            bg=cor_fundo_pai, highlightthickness=0, bd=0
        )
        self.canvas.pack()

        self._desenhar_fundo(cor_campo)

        # Container interno para os widgets do campo
        self.container = tk.Frame(self.canvas, bg=cor_campo)
        self.canvas.create_window(
            largura / 2, self.altura_campo / 2,
            window=self.container,
            width=largura - 24, height=self.altura_campo - 8
        )

        # Icone (se fornecido)
        if icone:
            self.lbl_icone = tk.Label(
                self.container, text=icone,
                font=("Segoe UI Emoji", 14),
                bg=cor_campo, fg=AZUL_ESCURO
            )
            self.lbl_icone.pack(side="left", padx=(2, 6))

        # Entry
        self.var = tk.StringVar()
        char_show = "*" if senha else ""
        self.entry = tk.Entry(
            self.container,
            textvariable=self.var,
            font=(FONTE_TEXTO, 11),
            bg=cor_campo, fg=PRETO_TEXTO,
            relief="flat", bd=0,
            insertbackground=AZUL_ESCURO,
            show=char_show
        )
        self.entry.pack(side="left", fill="both", expand=True)

        # Botao mostrar/ocultar senha
        if senha:
            self.btn_olho = tk.Label(
                self.container, text="👁",
                font=("Segoe UI Emoji", 12),
                bg=cor_campo, fg=AZUL_ESCURO,
                cursor="hand2"
            )
            self.btn_olho.pack(side="right", padx=(6, 2))
            self.btn_olho.bind("<Button-1>", self._alternar_senha)

        # Placeholder
        if placeholder:
            self._aplicar_placeholder()
            self.entry.bind("<FocusIn>", self._remover_placeholder)
            self.entry.bind("<FocusOut>", self._aplicar_placeholder)

        # Animacao de foco (borda azul ao focar)
        self.entry.bind("<FocusIn>", self._ao_focar, add="+")
        self.entry.bind("<FocusOut>", self._ao_desfocar, add="+")

    def _desenhar_fundo(self, cor):
        """Desenha o fundo arredondado do campo."""
        self.canvas.delete("fundo")
        l, a, r = self.largura, self.altura_campo, 12
        pontos = [
            r, 0, l - r, 0, l, 0, l, r,
            l, a - r, l, a, l - r, a, r, a,
            0, a, 0, a - r, 0, r, 0, 0
        ]
        self.canvas.create_polygon(
            pontos, fill=cor, outline=cor, smooth=True, tags="fundo"
        )

    def _ao_focar(self, _=None):
        # Borda azul sutil ao focar (redesenha com outline azul)
        self.canvas.delete("fundo")
        l, a, r = self.largura, self.altura_campo, 12
        pontos = [
            r, 0, l - r, 0, l, 0, l, r,
            l, a - r, l, a, l - r, a, r, a,
            0, a, 0, a - r, 0, r, 0, 0
        ]
        self.canvas.create_polygon(
            pontos, fill=self.cor_campo, outline=AZUL_PRIMARIO,
            width=2, smooth=True, tags="fundo"
        )

    def _ao_desfocar(self, _=None):
        self._desenhar_fundo(self.cor_campo)

    def _alternar_senha(self, _=None):
        self._mostrando_senha = not self._mostrando_senha
        self.entry.configure(show="" if self._mostrando_senha else "*")
        self.btn_olho.configure(text="🙈" if self._mostrando_senha else "👁")

    def _aplicar_placeholder(self, _=None):
        if not self.var.get():
            self.entry.configure(fg=CINZA_MEDIO)
            self.var.set(self.placeholder)
            self._placeholder_ativo = True

    def _remover_placeholder(self, _=None):
        if getattr(self, "_placeholder_ativo", False):
            self.var.set("")
            self.entry.configure(fg=PRETO_TEXTO)
            self._placeholder_ativo = False

    def obter(self):
        """Retorna o valor digitado (string vazia se for placeholder)."""
        valor = self.var.get()
        if getattr(self, "_placeholder_ativo", False):
            return ""
        return valor.strip()

    def definir(self, valor):
        """Define o valor do campo."""
        self._placeholder_ativo = False
        self.entry.configure(fg=PRETO_TEXTO)
        self.var.set(valor)

    def limpar(self):
        self.var.set("")
        if self.placeholder:
            self._aplicar_placeholder()
