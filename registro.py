import re
import tkinter as tk
from tkinter import messagebox, font as tkfont


COR_AZUL_ESCURO = "#112250"
COR_AZUL_PAINEL = "#3C507D"
COR_AZUL_CLARO = "#5C6FA0"
COR_AZUL_DESTAQUE = "#1E3A8A"
COR_AZUL_HOVER = "#2A4BB5"
COR_DOURADO = "#E0C58F"
COR_DOURADO_ESCURO = "#C9A96A"
COR_AMARELO = "#F5B83D"
COR_BRANCO = "#FFFFFF"
COR_OFFWHITE = "#FBFAF7"
COR_CINZA_PLACEHOLDER = "#7A6B4F"
COR_TEXTO_SECUNDARIO = "#5A6B8C"


class CampoEntrada(tk.Frame):
    """Campo de entrada arredondado com ícone, placeholder e suporte a senha."""

    def __init__(
        self,
        master,
        placeholder,
        icone="",
        is_password=False,
        largura=360,
        altura=48,
        **kwargs,
    ):
        super().__init__(master, bg=COR_BRANCO, **kwargs)
        self.placeholder = placeholder
        self.is_password = is_password
        self.largura = largura
        self.altura = altura

        self.canvas = tk.Canvas(
            self,
            width=largura,
            height=altura,
            bg=COR_BRANCO,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        self._desenhar_fundo(borda=COR_DOURADO_ESCURO)

        if icone:
            self.canvas.create_text(
                20,
                altura // 2,
                text=icone,
                fill=COR_AZUL_ESCURO,
                font=("Segoe UI Symbol", 14, "bold"),
            )
            offset_x = 42
        else:
            offset_x = 18

        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.var,
            bd=0,
            relief="flat",
            bg=COR_DOURADO,
            fg=COR_AZUL_ESCURO,
            insertbackground=COR_AZUL_ESCURO,
            font=("Segoe UI", 11),
            highlightthickness=0,
        )
        entry_w = largura - offset_x - 18
        self.canvas.create_window(
            offset_x,
            altura // 2,
            anchor="w",
            window=self.entry,
            width=entry_w,
            height=altura - 16,
        )

        self._mostrar_placeholder()
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _desenhar_fundo(self, borda):
        self.canvas.delete("fundo")
        self._round_rect(
            2,
            2,
            self.largura - 2,
            self.altura - 2,
            r=14,
            fill=COR_DOURADO,
            outline=borda,
            width=1,
            tag="fundo",
        )
        self.canvas.tag_lower("fundo")

    def _round_rect(self, x1, y1, x2, y2, r=12, **kwargs):
        pontos = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.canvas.create_polygon(pontos, smooth=True, **kwargs)

    def _mostrar_placeholder(self):
        self.entry.config(fg=COR_CINZA_PLACEHOLDER, show="")
        self.var.set(self.placeholder)
        self._placeholder_ativo = True

    def _on_focus_in(self, _):
        if self._placeholder_ativo:
            self.var.set("")
            self.entry.config(fg=COR_AZUL_ESCURO)
            if self.is_password:
                self.entry.config(show="•")
            self._placeholder_ativo = False
        self._desenhar_fundo(borda=COR_AZUL_ESCURO)

    def _on_focus_out(self, _):
        if not self.var.get():
            self._mostrar_placeholder()
        self._desenhar_fundo(borda=COR_DOURADO_ESCURO)

    def get(self):
        if self._placeholder_ativo:
            return ""
        return self.var.get()


class BotaoArredondado(tk.Canvas):
    """Botão arredondado com efeito hover."""

    def __init__(
        self,
        master,
        texto,
        comando,
        largura=360,
        altura=50,
        cor=COR_AZUL_DESTAQUE,
        cor_hover=COR_AZUL_HOVER,
        cor_texto=COR_BRANCO,
        fonte=("Segoe UI", 12, "bold"),
        raio=14,
    ):
        super().__init__(
            master,
            width=largura,
            height=altura,
            bg=COR_BRANCO,
            highlightthickness=0,
            bd=0,
        )
        self.texto = texto
        self.comando = comando
        self.largura = largura
        self.altura = altura
        self.cor = cor
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.fonte = fonte
        self.raio = raio

        self._desenhar(cor)

        self.bind("<Enter>", lambda _: self._desenhar(self.cor_hover))
        self.bind("<Leave>", lambda _: self._desenhar(self.cor))
        self.bind("<Button-1>", lambda _: self.comando())

    def _desenhar(self, cor_fundo):
        self.delete("all")
        r = self.raio
        pontos = [
            r, 0,
            self.largura - r, 0,
            self.largura, 0,
            self.largura, r,
            self.largura, self.altura - r,
            self.largura, self.altura,
            self.largura - r, self.altura,
            r, self.altura,
            0, self.altura,
            0, self.altura - r,
            0, r,
            0, 0,
        ]
        self.create_polygon(pontos, smooth=True, fill=cor_fundo, outline=cor_fundo)
        self.create_text(
            self.largura // 2,
            self.altura // 2,
            text=self.texto,
            fill=self.cor_texto,
            font=self.fonte,
        )


class LogoSF(tk.Canvas):
    """Logo SF com chapéu de formatura desenhado no Canvas."""

    def __init__(self, master, tamanho=72):
        super().__init__(
            master,
            width=tamanho,
            height=tamanho,
            bg=COR_BRANCO,
            highlightthickness=0,
            bd=0,
        )
        self.tamanho = tamanho
        self._desenhar()

    def _desenhar(self):
        t = self.tamanho
        c = t / 2

        # círculo externo azul
        self.create_oval(2, 2, t - 2, t - 2, outline=COR_AZUL_ESCURO, width=2)
        # anel dourado
        margem = t * 0.09
        self.create_oval(
            margem, margem, t - margem, t - margem,
            outline=COR_AMARELO, width=2,
        )

        # letra S em dourado
        self.create_text(
            c - t * 0.14,
            c + t * 0.05,
            text="S",
            fill=COR_AMARELO,
            font=("Georgia", int(t * 0.50), "bold"),
        )
        # letra F em azul
        self.create_text(
            c + t * 0.16,
            c + t * 0.10,
            text="F",
            fill=COR_AZUL_ESCURO,
            font=("Georgia", int(t * 0.50), "bold"),
        )

        # chapéu de formatura
        cx = c + t * 0.02
        cy = c - t * 0.20
        meio = t * 0.18
        self.create_polygon(
            cx - meio, cy,
            cx, cy - meio * 0.55,
            cx + meio, cy,
            cx, cy + meio * 0.55,
            fill=COR_AZUL_ESCURO, outline=COR_AZUL_ESCURO,
        )
        # borla
        self.create_line(cx + meio * 0.7, cy, cx + meio * 0.95, cy + meio * 0.7,
                         fill=COR_AZUL_ESCURO, width=2)
        self.create_oval(
            cx + meio * 0.85, cy + meio * 0.55,
            cx + meio * 1.10, cy + meio * 0.85,
            fill=COR_AMARELO, outline=COR_AZUL_ESCURO,
        )


class PainelDireito(tk.Canvas):
    """Painel direito visual com formas geométricas, gradiente e textos."""

    def __init__(self, master, largura, altura):
        super().__init__(
            master,
            width=largura,
            height=altura,
            bg=COR_AZUL_PAINEL,
            highlightthickness=0,
            bd=0,
        )
        self.largura = largura
        self.altura = altura
        self.bind("<Configure>", self._on_resize)
        self._desenhar(largura, altura)

    def _on_resize(self, event):
        if event.width > 10 and event.height > 10:
            self.largura = event.width
            self.altura = event.height
            self._desenhar(event.width, event.height)

    def _desenhar(self, w, h):
        self.delete("all")

        # gradiente vertical leve (faixas horizontais)
        passos = 60
        for i in range(passos):
            t = i / passos
            r1, g1, b1 = 0x3C, 0x50, 0x7D
            r2, g2, b2 = 0x2A, 0x3B, 0x66
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            cor = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(h * i / passos)
            y1 = int(h * (i + 1) / passos) + 1
            self.create_rectangle(0, y0, w, y1, fill=cor, outline=cor)

        # blobs/círculos suaves de fundo
        self._circulo_suave(w * 0.15, h * 0.20, 180, COR_AZUL_CLARO, alpha_steps=6)
        self._circulo_suave(w * 0.85, h * 0.85, 220, COR_AZUL_CLARO, alpha_steps=6)

        # quadrados inclinados decorativos (molduras "vazias" simulando recortes)
        self._quadrado_inclinado(w * 0.25, h * 0.18, 130, 18, COR_AMARELO)
        self._quadrado_inclinado(w * 0.42, h * 0.12, 70, -12, COR_DOURADO)
        self._quadrado_inclinado(w * 0.78, h * 0.32, 150, -8, "#6478A8")
        self._quadrado_inclinado(w * 0.20, h * 0.78, 140, -14, "#6478A8")
        self._quadrado_inclinado(w * 0.88, h * 0.20, 60, 20, COR_AMARELO)
        self._quadrado_inclinado(w * 0.65, h * 0.88, 90, 10, COR_DOURADO)

        # blocos abstratos pequenos flutuantes
        for cx, cy, s in [
            (w * 0.10, h * 0.55, 28),
            (w * 0.55, h * 0.18, 22),
            (w * 0.92, h * 0.55, 30),
            (w * 0.50, h * 0.70, 26),
            (w * 0.30, h * 0.40, 18),
            (w * 0.70, h * 0.50, 20),
        ]:
            self.create_rectangle(
                cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2,
                fill="#7589B8", outline="",
            )

        # pontos discretos
        import random
        rng = random.Random(7)
        for _ in range(40):
            x = rng.uniform(0, w)
            y = rng.uniform(0, h)
            r = rng.choice([1, 2, 2, 3])
            self.create_oval(x, y, x + r, y + r, fill="#A8B5D6", outline="")

        # textos centrais
        cx = w / 2
        cy = h / 2
        self.create_text(
            cx, cy - 30,
            text="Seu futuro começa com\numa escolha simples",
            fill=COR_BRANCO,
            font=("Segoe UI", 26, "bold"),
            justify="center",
            width=w - 120,
        )
        self.create_text(
            cx, cy + 50,
            text=(
                "Descubra novas oportunidades, desenvolva habilidades\n"
                "e faça parte de uma comunidade de aprendizado moderna."
            ),
            fill="#D8DEEC",
            font=("Segoe UI", 12),
            justify="center",
            width=w - 160,
        )

        # rodapé sutil
        self.create_text(
            cx, h - 24,
            text="Sistema Fácil · Educação que transforma",
            fill="#B6BFD6",
            font=("Segoe UI", 9, "italic"),
        )

    def _circulo_suave(self, cx, cy, raio, cor, alpha_steps=5):
        for i in range(alpha_steps, 0, -1):
            r = raio * (i / alpha_steps)
            self.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=cor, outline="",
                stipple="gray25" if i > 1 else "gray12",
            )

    def _quadrado_inclinado(self, cx, cy, lado, angulo_graus, cor):
        import math
        ang = math.radians(angulo_graus)
        meio = lado / 2
        cantos = [(-meio, -meio), (meio, -meio), (meio, meio), (-meio, meio)]
        pontos = []
        for x, y in cantos:
            xr = x * math.cos(ang) - y * math.sin(ang) + cx
            yr = x * math.sin(ang) + y * math.cos(ang) + cy
            pontos.extend([xr, yr])
        # sombra
        sombra = [p + (6 if i % 2 == 0 else 6) for i, p in enumerate(pontos)]
        self.create_polygon(sombra, fill="#1E2C4B", outline="", stipple="gray25")
        self.create_polygon(pontos, fill=cor, outline="")


class SistemaFacilApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Fácil — Cadastro de Alunos")
        self.geometry("1180x720")
        self.minsize(1000, 640)
        self.configure(bg=COR_BRANCO)

        # grid 50/50
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_rowconfigure(0, weight=1)

        self._construir_lado_esquerdo()
        self._construir_lado_direito()

    # ---------- LADO ESQUERDO ----------
    def _construir_lado_esquerdo(self):
        esquerda = tk.Frame(self, bg=COR_OFFWHITE)
        esquerda.grid(row=0, column=0, sticky="nsew")

        container = tk.Frame(esquerda, bg=COR_OFFWHITE)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # cabeçalho com logo
        header = tk.Frame(container, bg=COR_OFFWHITE)
        header.pack(anchor="w", pady=(0, 18))

        LogoSF(header, tamanho=58).pack(side="left")
        textos_logo = tk.Frame(header, bg=COR_OFFWHITE)
        textos_logo.pack(side="left", padx=12)
        tk.Label(
            textos_logo,
            text="Sistema Fácil",
            bg=COR_OFFWHITE,
            fg=COR_AZUL_ESCURO,
            font=("Georgia", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            textos_logo,
            text="de Matrículas",
            bg=COR_OFFWHITE,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        # título
        tk.Label(
            container,
            text="Crie sua conta",
            bg=COR_OFFWHITE,
            fg=COR_AZUL_ESCURO,
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            container,
            text="Bem-vindo ao Sistema Fácil — preencha seus dados para começar.",
            bg=COR_OFFWHITE,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 22))

        # campos
        self.campo_nome = CampoEntrada(container, "Nome completo", icone="👤")
        self.campo_nome.pack(pady=6)

        self.campo_email = CampoEntrada(container, "E-mail", icone="✉")
        self.campo_email.pack(pady=6)

        self.campo_email2 = CampoEntrada(container, "Repetir e-mail", icone="✉")
        self.campo_email2.pack(pady=6)

        self.campo_senha = CampoEntrada(container, "Senha", icone="🔒", is_password=True)
        self.campo_senha.pack(pady=6)

        self.campo_senha2 = CampoEntrada(container, "Repetir senha", icone="🔒", is_password=True)
        self.campo_senha2.pack(pady=6)

        self.campo_telefone = CampoEntrada(container, "Telefone (com DDD)", icone="📞")
        self.campo_telefone.pack(pady=6)

        # botão cadastrar
        BotaoArredondado(
            container,
            texto="Cadastrar",
            comando=self._cadastrar,
            largura=360,
            altura=50,
        ).pack(pady=(20, 12))

        # links
        links = tk.Frame(container, bg=COR_OFFWHITE)
        links.pack(pady=(0, 4))

        tk.Label(
            links,
            text="Já tem uma conta?",
            bg=COR_OFFWHITE,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
        ).pack(side="left")
        link_entrar = tk.Label(
            links,
            text=" Entrar",
            bg=COR_OFFWHITE,
            fg=COR_AZUL_DESTAQUE,
            font=("Segoe UI", 10, "bold underline"),
            cursor="hand2",
        )
        link_entrar.pack(side="left")
        link_entrar.bind("<Button-1>", lambda _: messagebox.showinfo(
            "Entrar", "Tela de login em breve."
        ))

        ajuda = tk.Label(
            container,
            text="Precisa de ajuda? Fale conosco",
            bg=COR_OFFWHITE,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9, "underline"),
            cursor="hand2",
        )
        ajuda.pack(pady=(8, 0))
        ajuda.bind("<Button-1>", lambda _: messagebox.showinfo(
            "Ajuda", "Entre em contato: suporte@sistemafacil.com.br"
        ))

        tk.Label(
            container,
            text="© 2026 Sistema Fácil de Matrículas",
            bg=COR_OFFWHITE,
            fg="#9AA3B5",
            font=("Segoe UI", 8),
        ).pack(pady=(20, 0))

    # ---------- LADO DIREITO ----------
    def _construir_lado_direito(self):
        self.painel = PainelDireito(self, largura=590, altura=720)
        self.painel.grid(row=0, column=1, sticky="nsew")

    # ---------- AÇÕES ----------
    def _cadastrar(self):
        nome = self.campo_nome.get().strip()
        email = self.campo_email.get().strip()
        email2 = self.campo_email2.get().strip()
        senha = self.campo_senha.get()
        senha2 = self.campo_senha2.get()
        telefone = self.campo_telefone.get().strip()

        if not all([nome, email, email2, senha, senha2, telefone]):
            messagebox.showwarning(
                "Campos obrigatórios",
                "Por favor, preencha todos os campos para continuar.",
            )
            return

        if len(nome.split()) < 2:
            messagebox.showwarning(
                "Nome inválido",
                "Informe seu nome completo (nome e sobrenome).",
            )
            return

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            messagebox.showwarning("E-mail inválido", "Digite um e-mail válido.")
            return

        if email != email2:
            messagebox.showwarning(
                "E-mails diferentes", "Os e-mails informados não coincidem."
            )
            return

        if len(senha) < 8:
            messagebox.showwarning(
                "Senha curta", "A senha deve ter no mínimo 8 caracteres."
            )
            return

        if senha != senha2:
            messagebox.showwarning(
                "Senhas diferentes", "As senhas informadas não coincidem."
            )
            return

        digitos = re.sub(r"\D", "", telefone)
        if len(digitos) < 10:
            messagebox.showwarning(
                "Telefone inválido",
                "Informe um telefone válido com DDD (mínimo 10 dígitos).",
            )
            return

        messagebox.showinfo(
            "Cadastro realizado",
            f"Bem-vindo(a), {nome.split()[0]}!\n\n"
            "Sua conta no Sistema Fácil foi criada com sucesso.",
        )


if __name__ == "__main__":
    app = SistemaFacilApp()
    app.mainloop()
