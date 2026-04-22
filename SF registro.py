"""
Sistema Facil de Matriculas - Tela de Cadastro
Aplicacao desktop em Tkinter

Como rodar:
    python sistema_facil.py

Requisitos:
    - Python 3.8+
    - Pillow (opcional, para exibir a logo PNG):  pip install pillow
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False


# ----------------- Paleta de cores (Navy + Dourado) -----------------
NAVY        = "#163A5F"
NAVY_DARK   = "#0F2A47"
NAVY_LIGHT  = "#1F4D7A"
GOLD        = "#F4B528"
GOLD_DARK   = "#D89A14"
WHITE       = "#FFFFFF"
CREAM       = "#FAF8F3"
GRAY_BG     = "#F4F5F7"
GRAY_BORDER = "#D6DAE0"
GRAY_TEXT   = "#5B6470"
DARK_TEXT   = "#1A2332"
ERROR_RED   = "#D14343"


# ----------------- Mascaras -----------------
def mask_cpf(value: str) -> str:
    digits = re.sub(r"\D", "", value)[:11]
    out = digits
    if len(digits) > 9:
        out = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    elif len(digits) > 6:
        out = f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
    elif len(digits) > 3:
        out = f"{digits[:3]}.{digits[3:]}"
    return out


def mask_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)[:11]
    if len(digits) > 10:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) > 6:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    if len(digits) > 2:
        return f"({digits[:2]}) {digits[2:]}"
    return digits


def mask_date(value: str) -> str:
    digits = re.sub(r"\D", "", value)[:8]
    if len(digits) > 4:
        return f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
    if len(digits) > 2:
        return f"{digits[:2]}/{digits[2:]}"
    return digits


# ----------------- Validacoes -----------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_cpf(cpf: str) -> bool:
    digits = re.sub(r"\D", "", cpf)
    if len(digits) != 11 or digits == digits[0] * 11:
        return False
    for i in (9, 10):
        s = sum(int(digits[j]) * ((i + 1) - j) for j in range(i))
        d = (s * 10) % 11 % 10
        if d != int(digits[i]):
            return False
    return True


def validate_date(text: str) -> bool:
    try:
        datetime.strptime(text, "%d/%m/%Y")
        return True
    except ValueError:
        return False


# ----------------- Widgets customizados -----------------
class RoundedEntry(tk.Frame):
    """Entry com borda arredondada simulada e foco visivel."""

    def __init__(self, master, placeholder="", show=None, width=28, **kw):
        super().__init__(master, bg=WHITE, highlightthickness=1,
                         highlightbackground=GRAY_BORDER,
                         highlightcolor=NAVY)
        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.var,
            font=("Segoe UI", 11),
            bd=0,
            relief="flat",
            bg=WHITE,
            fg=DARK_TEXT,
            insertbackground=NAVY,
            width=width,
            show=show or "",
        )
        self.entry.pack(fill="x", padx=12, pady=10)
        self.placeholder = placeholder
        self._show = show or ""
        self._has_placeholder = False
        self._set_placeholder()

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _set_placeholder(self):
        if not self.var.get():
            self._has_placeholder = True
            self.entry.config(fg=GRAY_TEXT, show="")
            self.var.set(self.placeholder)

    def _clear_placeholder(self):
        if self._has_placeholder:
            self.var.set("")
            self.entry.config(fg=DARK_TEXT, show=self._show)
            self._has_placeholder = False

    def _on_focus_in(self, _):
        self._clear_placeholder()
        self.config(highlightbackground=NAVY, highlightthickness=2)

    def _on_focus_out(self, _):
        self.config(highlightbackground=GRAY_BORDER, highlightthickness=1)
        self._set_placeholder()

    def get(self) -> str:
        return "" if self._has_placeholder else self.var.get()

    def set(self, value: str):
        self._has_placeholder = False
        self.entry.config(fg=DARK_TEXT, show=self._show)
        self.var.set(value)

    def set_error(self, on: bool):
        color = ERROR_RED if on else GRAY_BORDER
        self.config(highlightbackground=color)


class HoverButton(tk.Button):
    def __init__(self, master, bg, hover_bg, fg, **kw):
        super().__init__(master, bg=bg, fg=fg, activebackground=hover_bg,
                         activeforeground=fg, bd=0, relief="flat",
                         cursor="hand2", **kw)
        self._bg = bg
        self._hover = hover_bg
        self.bind("<Enter>", lambda _: self.config(bg=self._hover))
        self.bind("<Leave>", lambda _: self.config(bg=self._bg))


# ----------------- Painel direito decorativo -----------------
class RightPanel(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg=NAVY, highlightthickness=0, **kw)
        self.bind("<Configure>", self._draw)

    def _draw(self, event):
        self.delete("all")
        w, h = event.width, event.height

        # Fundo gradiente simulado com retangulos
        for i in range(0, h, 4):
            ratio = i / max(h, 1)
            r = int(int(NAVY[1:3], 16) * (1 - ratio * 0.25) +
                    int(NAVY_DARK[1:3], 16) * ratio * 0.25)
            g = int(int(NAVY[3:5], 16) * (1 - ratio * 0.25) +
                    int(NAVY_DARK[3:5], 16) * ratio * 0.25)
            b = int(int(NAVY[5:7], 16) * (1 - ratio * 0.25) +
                    int(NAVY_DARK[5:7], 16) * ratio * 0.25)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_rectangle(0, i, w, i + 4, fill=color, outline=color)

        # Formas geometricas decorativas
        self.create_rectangle(w * 0.55, h * 0.12, w * 0.72, h * 0.30,
                              fill=GOLD, outline="")
        self.create_rectangle(w * 0.74, h * 0.16, w * 0.82, h * 0.24,
                              fill=GOLD_DARK, outline="")
        self.create_rectangle(w * 0.62, h * 0.55, w * 0.78, h * 0.72,
                              fill=NAVY_LIGHT, outline="")
        self.create_rectangle(w * 0.18, h * 0.62, w * 0.32, h * 0.78,
                              fill=GOLD, outline="")
        self.create_rectangle(w * 0.82, h * 0.78, w * 0.92, h * 0.88,
                              fill=NAVY_LIGHT, outline="")

        # Pontos / dots
        for x, y in [(0.15, 0.20), (0.20, 0.25), (0.25, 0.20),
                     (0.85, 0.50), (0.90, 0.55), (0.85, 0.60)]:
            self.create_oval(w * x - 4, h * y - 4, w * x + 4, h * y + 4,
                             fill=GOLD, outline="")

        # Headline e texto
        self.create_text(
            w / 2, h * 0.42,
            text="Seu futuro\ncomeça aqui",
            fill=WHITE,
            font=("Segoe UI", 32, "bold"),
            justify="center",
        )
        self.create_text(
            w / 2, h * 0.50,
            text="Faça parte da nossa comunidade educacional\n"
                 "e dê o próximo passo na sua carreira.",
            fill="#C9D6E5",
            font=("Segoe UI", 11),
            justify="center",
        )

        # Linha decorativa
        self.create_rectangle(w * 0.45, h * 0.45, w * 0.55, h * 0.452,
                              fill=GOLD, outline="")


# ----------------- App principal -----------------
class SistemaFacilApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Fácil de Matrículas - Cadastro")
        self.geometry("1100x720")
        self.minsize(900, 640)
        self.configure(bg=WHITE)

        # Estilo ttk para combobox
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox",
                        fieldbackground=WHITE,
                        background=WHITE,
                        foreground=DARK_TEXT,
                        bordercolor=GRAY_BORDER,
                        lightcolor=GRAY_BORDER,
                        darkcolor=GRAY_BORDER,
                        arrowcolor=NAVY,
                        padding=6)

        self._build_layout()

    # ---------------- Layout ----------------
    def _build_layout(self):
        container = tk.Frame(self, bg=WHITE)
        container.pack(fill="both", expand=True)

        # Coluna esquerda - formulario
        left = tk.Frame(container, bg=WHITE)
        left.pack(side="left", fill="both", expand=True)

        # Coluna direita - painel visual
        right = RightPanel(container, width=520)
        right.pack(side="right", fill="both", expand=True)

        self._build_form(left)

    def _build_form(self, parent):
        # Scroll container
        canvas = tk.Canvas(parent, bg=WHITE, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical",
                                 command=canvas.yview)
        inner = tk.Frame(canvas, bg=WHITE)

        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(window_id, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scroll
        def _on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_wheel)

        # ----- Conteudo do form -----
        wrap = tk.Frame(inner, bg=WHITE)
        wrap.pack(padx=60, pady=40, fill="x")

        # Cabecalho com logo
        header = tk.Frame(wrap, bg=WHITE)
        header.pack(fill="x", anchor="w")

        logo_path = os.path.join(os.path.dirname(__file__), "sf_logo.png")
        if PIL_OK and os.path.exists(logo_path):
            img = Image.open(logo_path).resize((48, 48), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img)
            tk.Label(header, image=self._logo_img, bg=WHITE).pack(side="left")
        else:
            tk.Label(header, text="SF", bg=NAVY, fg=GOLD,
                     font=("Segoe UI", 18, "bold"),
                     width=3, height=1).pack(side="left")

        brand = tk.Frame(header, bg=WHITE)
        brand.pack(side="left", padx=12)
        tk.Label(brand, text="Sistema Fácil",
                 font=("Segoe UI", 13, "bold"),
                 bg=WHITE, fg=NAVY).pack(anchor="w")
        tk.Label(brand, text="de Matrículas",
                 font=("Segoe UI", 11),
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w")

        # Titulo
        tk.Label(wrap, text="Crie sua conta",
                 font=("Segoe UI", 26, "bold"),
                 bg=WHITE, fg=DARK_TEXT).pack(anchor="w", pady=(28, 4))
        tk.Label(wrap, text="Cadastre-se para iniciar sua jornada educacional.",
                 font=("Segoe UI", 11),
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor="w", pady=(0, 24))

        # Campos
        self.fields = {}
        self._add_field(wrap, "nome", "Nome completo", "João da Silva")
        self._add_field(wrap, "email", "E-mail", "joao@exemplo.com")

        row = tk.Frame(wrap, bg=WHITE)
        row.pack(fill="x", pady=(0, 14))
        self._add_field(row, "cpf", "CPF", "000.000.000-00",
                        side="left", expand=True, padx=(0, 8))
        self._add_field(row, "telefone", "Telefone", "(00) 00000-0000",
                        side="left", expand=True, padx=(8, 0))

        row2 = tk.Frame(wrap, bg=WHITE)
        row2.pack(fill="x", pady=(0, 14))
        self._add_field(row2, "nascimento", "Data de nascimento",
                        "dd/mm/aaaa", side="left", expand=True, padx=(0, 8))
        self._add_combo(row2, "curso", "Curso de interesse",
                        ["Técnico em Informática", "Administração",
                         "Design Gráfico", "Marketing Digital", "Enfermagem"],
                        side="left", expand=True, padx=(8, 0))

        row3 = tk.Frame(wrap, bg=WHITE)
        row3.pack(fill="x", pady=(0, 14))
        self._add_field(row3, "senha", "Senha", "••••••••",
                        show="•", side="left", expand=True, padx=(0, 8))
        self._add_field(row3, "confirmar", "Confirmar senha", "••••••••",
                        show="•", side="left", expand=True, padx=(8, 0))

        # Mascaras automaticas
        self.fields["cpf"].entry.bind("<KeyRelease>",
                                      lambda e: self._apply_mask("cpf", mask_cpf))
        self.fields["telefone"].entry.bind("<KeyRelease>",
                                           lambda e: self._apply_mask("telefone", mask_phone))
        self.fields["nascimento"].entry.bind("<KeyRelease>",
                                             lambda e: self._apply_mask("nascimento", mask_date))

        # Termos
        self.terms_var = tk.BooleanVar()
        terms = tk.Frame(wrap, bg=WHITE)
        terms.pack(fill="x", pady=(6, 18), anchor="w")
        tk.Checkbutton(terms, variable=self.terms_var,
                       bg=WHITE, activebackground=WHITE,
                       fg=NAVY, selectcolor=WHITE,
                       cursor="hand2").pack(side="left")
        tk.Label(terms,
                 text="Li e aceito os termos de uso e a política de privacidade.",
                 bg=WHITE, fg=GRAY_TEXT,
                 font=("Segoe UI", 10)).pack(side="left")

        # Botao principal
        btn = HoverButton(wrap, bg=NAVY, hover_bg=NAVY_DARK, fg=WHITE,
                          text="Cadastrar",
                          font=("Segoe UI", 12, "bold"),
                          padx=24, pady=12,
                          command=self._submit)
        btn.pack(fill="x", pady=(0, 14))

        # Link login
        link = tk.Frame(wrap, bg=WHITE)
        link.pack(anchor="w")
        tk.Label(link, text="Já tem uma conta?",
                 bg=WHITE, fg=GRAY_TEXT,
                 font=("Segoe UI", 10)).pack(side="left")
        login_lbl = tk.Label(link, text=" Entrar",
                             bg=WHITE, fg=NAVY,
                             cursor="hand2",
                             font=("Segoe UI", 10, "bold underline"))
        login_lbl.pack(side="left")
        login_lbl.bind("<Button-1>",
                       lambda _: messagebox.showinfo(
                           "Entrar", "Tela de login ainda não implementada."))

    # ---------------- Helpers de campo ----------------
    def _add_field(self, parent, key, label, placeholder,
                   show=None, side=None, expand=False, padx=0):
        col = tk.Frame(parent, bg=WHITE)
        if side:
            col.pack(side=side, fill="x", expand=expand, padx=padx)
        else:
            col.pack(fill="x", pady=(0, 14))

        tk.Label(col, text=label, bg=WHITE, fg=DARK_TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        entry = RoundedEntry(col, placeholder=placeholder, show=show)
        entry.pack(fill="x")
        self.fields[key] = entry

    def _add_combo(self, parent, key, label, options,
                   side=None, expand=False, padx=0):
        col = tk.Frame(parent, bg=WHITE)
        if side:
            col.pack(side=side, fill="x", expand=expand, padx=padx)
        else:
            col.pack(fill="x", pady=(0, 14))

        tk.Label(col, text=label, bg=WHITE, fg=DARK_TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        var = tk.StringVar()
        combo = ttk.Combobox(col, textvariable=var, values=options,
                             state="readonly", font=("Segoe UI", 11))
        combo.set("Selecione um curso")
        combo.pack(fill="x", ipady=6)
        self.fields[key] = combo

    def _apply_mask(self, key, fn):
        field = self.fields[key]
        if field._has_placeholder:
            return
        cur = field.var.get()
        new = fn(cur)
        if new != cur:
            field.var.set(new)
            field.entry.icursor("end")

    # ---------------- Submissao ----------------
    def _get(self, key):
        f = self.fields[key]
        if isinstance(f, RoundedEntry):
            return f.get().strip()
        return f.get().strip()

    def _set_error(self, key, on):
        f = self.fields[key]
        if isinstance(f, RoundedEntry):
            f.set_error(on)

    def _submit(self):
        errors = []

        nome = self._get("nome")
        email = self._get("email")
        cpf = self._get("cpf")
        tel = self._get("telefone")
        nasc = self._get("nascimento")
        curso = self._get("curso")
        senha = self._get("senha")
        conf = self._get("confirmar")

        # Reset errors
        for k in ("nome", "email", "cpf", "telefone",
                  "nascimento", "senha", "confirmar"):
            self._set_error(k, False)

        if len(nome) < 3:
            errors.append("Informe seu nome completo.")
            self._set_error("nome", True)
        if not EMAIL_RE.match(email):
            errors.append("E-mail inválido.")
            self._set_error("email", True)
        if not validate_cpf(cpf):
            errors.append("CPF inválido.")
            self._set_error("cpf", True)
        if len(re.sub(r"\D", "", tel)) < 10:
            errors.append("Telefone inválido.")
            self._set_error("telefone", True)
        if not validate_date(nasc):
            errors.append("Data de nascimento inválida (use dd/mm/aaaa).")
            self._set_error("nascimento", True)
        if curso == "Selecione um curso" or not curso:
            errors.append("Selecione um curso de interesse.")
        if len(senha) < 8:
            errors.append("A senha deve ter pelo menos 8 caracteres.")
            self._set_error("senha", True)
        if senha != conf:
            errors.append("As senhas não conferem.")
            self._set_error("confirmar", True)
        if not self.terms_var.get():
            errors.append("Você precisa aceitar os termos de uso.")

        if errors:
            messagebox.showerror("Verifique os campos",
                                 "\n".join(f"• {e}" for e in errors))
            return

        messagebox.showinfo(
            "Cadastro realizado",
            f"Bem-vindo(a), {nome.split()[0]}!\n\n"
            f"Sua matrícula no curso de {curso} foi recebida.\n"
            "Em breve você receberá um e-mail de confirmação.",
        )


if __name__ == "__main__":
    app = SistemaFacilApp()
    app.mainloop()
