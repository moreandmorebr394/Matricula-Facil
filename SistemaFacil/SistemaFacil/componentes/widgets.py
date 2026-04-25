# ============================================================
# componentes/widgets.py — Widgets customizados (inputs, botões)
# ============================================================
import tkinter as tk
from configuracoes import *


class CampoInput(tk.Frame):
    """Campo de entrada estilizado com ícone, placeholder e borda arredondada."""

    def __init__(self, master, placeholder="", icone="", mostrar="", largura=320, **kw):
        super().__init__(master, bg=OFF_WHITE, **kw)
        self.placeholder = placeholder
        self.mostrar_char = mostrar
        self._focado = False

        # Frame externo simulando borda arredondada
        self.frame_ext = tk.Frame(self, bg=DOURADO, padx=2, pady=2)
        self.frame_ext.pack(fill="x", pady=4)

        # Frame interno
        self.frame_int = tk.Frame(self.frame_ext, bg=DOURADO_CLARO, padx=10, pady=8)
        self.frame_int.pack(fill="x")

        # Ícone
        if icone:
            self.lbl_icone = tk.Label(
                self.frame_int, text=icone, font=("Segoe UI", 12),
                bg=DOURADO_CLARO, fg=AZUL_ESCURO
            )
            self.lbl_icone.pack(side="left", padx=(0, 8))

        # Entry
        self.entry = tk.Entry(
            self.frame_int,
            font=(FONTE_FAMILIA, FONTE_CAMPO),
            bg=DOURADO_CLARO,
            fg=CINZA_TEXTO,
            insertbackground=AZUL_ESCURO,
            relief="flat",
            border=0,
            width=largura // 10,
        )
        if mostrar:
            self.entry.config(show="")  # Mostra placeholder primeiro
        self.entry.insert(0, placeholder)
        self.entry.pack(side="left", fill="x", expand=True)

        # Eventos
        self.entry.bind("<FocusIn>", self._ao_focar)
        self.entry.bind("<FocusOut>", self._ao_desfocar)
        self.frame_ext.bind("<Enter>", self._hover_on)
        self.frame_ext.bind("<Leave>", self._hover_off)

    def _ao_focar(self, e):
        self._focado = True
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg=AZUL_ESCURO)
            if self.mostrar_char:
                self.entry.config(show=self.mostrar_char)
        self.frame_ext.config(bg=AZUL_MEDIO)

    def _ao_desfocar(self, e):
        self._focado = False
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=CINZA_TEXTO, show="")
        self.frame_ext.config(bg=DOURADO)

    def _hover_on(self, e):
        if not self._focado:
            self.frame_ext.config(bg=DOURADO_ESCURO)

    def _hover_off(self, e):
        if not self._focado:
            self.frame_ext.config(bg=DOURADO)

    def obter_valor(self):
        val = self.entry.get()
        return "" if val == self.placeholder else val


class BotaoPrincipal(tk.Canvas):
    """Botão estilizado com efeito hover e bordas arredondadas."""

    def __init__(self, master, texto="", comando=None, largura=320, altura=45, **kw):
        super().__init__(
            master, width=largura, height=altura,
            bg=OFF_WHITE, highlightthickness=0, **kw
        )
        self.texto = texto
        self.comando = comando
        self.largura = largura
        self.altura = altura
        self.cor_atual = AZUL_BOTAO
        self._hover = False
        self._pressed = False

        self._desenhar()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _desenhar(self):
        self.delete("all")
        r = 12
        w, h = self.largura, self.altura
        cor = self.cor_atual

        # Retângulo arredondado
        self.create_arc(0, 0, r * 2, r * 2, start=90, extent=90, fill=cor, outline=cor)
        self.create_arc(w - r * 2, 0, w, r * 2, start=0, extent=90, fill=cor, outline=cor)
        self.create_arc(0, h - r * 2, r * 2, h, start=180, extent=90, fill=cor, outline=cor)
        self.create_arc(w - r * 2, h - r * 2, w, h, start=270, extent=90, fill=cor, outline=cor)
        self.create_rectangle(r, 0, w - r, h, fill=cor, outline=cor)
        self.create_rectangle(0, r, w, h - r, fill=cor, outline=cor)

        # Texto
        self.create_text(
            w // 2, h // 2, text=self.texto,
            fill=BRANCO, font=(FONTE_FAMILIA, FONTE_BOTAO, "bold")
        )

        # Brilho sutil no hover
        if self._hover and not self._pressed:
            self.create_rectangle(
                0, 0, w, 3, fill=DOURADO, outline=""
            )

    def _on_enter(self, e):
        self._hover = True
        self.cor_atual = AZUL_HOVER
        self._desenhar()
        self.config(cursor="hand2")

    def _on_leave(self, e):
        self._hover = False
        self._pressed = False
        self.cor_atual = AZUL_BOTAO
        self._desenhar()

    def _on_press(self, e):
        self._pressed = True
        self.cor_atual = AZUL_ESCURO
        self._desenhar()

    def _on_release(self, e):
        self._pressed = False
        self.cor_atual = AZUL_HOVER if self._hover else AZUL_BOTAO
        self._desenhar()
        if self.comando and self._hover:
            self.comando()


class LinkClicavel(tk.Label):
    """Label que funciona como link clicável."""

    def __init__(self, master, texto="", comando=None, cor=AZUL_MEDIO,
                 cor_hover=AZUL_CLARO, tamanho=FONTE_LINK, negrito=False, **kw):
        peso = "bold" if negrito else "normal"
        super().__init__(
            master, text=texto,
            font=(FONTE_FAMILIA, tamanho, peso),
            fg=cor, bg=OFF_WHITE, cursor="hand2", **kw
        )
        self.comando = comando
        self.cor = cor
        self.cor_hover = cor_hover

        self.bind("<Enter>", lambda e: self.config(fg=self.cor_hover))
        self.bind("<Leave>", lambda e: self.config(fg=self.cor))
        self.bind("<Button-1>", lambda e: self.comando() if self.comando else None)


class AvisoLabel(tk.Frame):
    """Label de aviso/validação com ícone."""

    def __init__(self, master, texto="", tipo="info", **kw):
        super().__init__(master, bg=OFF_WHITE, **kw)
        cores = {
            "info": (CINZA_TEXTO, "ℹ"),
            "erro": (VERMELHO_ERRO, "⚠"),
            "sucesso": (VERDE_SUCESSO, "✓"),
        }
        cor, icone = cores.get(tipo, cores["info"])

        tk.Label(
            self, text=icone, font=(FONTE_FAMILIA, 10),
            fg=cor, bg=OFF_WHITE
        ).pack(side="left", padx=(0, 5))

        tk.Label(
            self, text=texto, font=(FONTE_FAMILIA, 10),
            fg=cor, bg=OFF_WHITE
        ).pack(side="left")
