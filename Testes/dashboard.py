"""
Sistema Fácil Educação — Dashboard completo fiel ao design
Tabelas: aluno, curso, funcionario, venda
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
import hashlib
import math

# ─── Paleta ──────────────────────────────────────────────────────────────────
C_SIDEBAR    = "#1e2a4a"
C_SIDEBAR_H  = "#2d3f6b"
C_SIDEBAR_A  = "#162038"
C_BG         = "#f0f2f5"
C_WHITE      = "#ffffff"
C_BLUE       = "#2563eb"
C_BLUE_DARK  = "#1d4ed8"
C_TEXT       = "#111827"
C_MUTED      = "#6b7280"
C_BORDER     = "#e5e7eb"
C_GOLD       = "#f59e0b"
C_GREEN      = "#10b981"
C_ORANGE     = "#f97316"
C_RED        = "#ef4444"
C_PURPLE     = "#8b5cf6"
C_LIGHT_BLUE = "#dbeafe"
C_BADGE_LEAD = "#fef3c7"
C_BADGE_TEXT = "#92400e"
SIDEBAR_W    = 200

# ─── DB ──────────────────────────────────────────────────────────────────────
DB_CFG = dict(host="localhost", user="root", password="",
              database="sistema_facil", charset="utf8mb4",
              cursorclass=pymysql.cursors.DictCursor)

def conectar():
    return pymysql.connect(**DB_CFG)

def hash256(v):
    return hashlib.sha256(v.encode()).hexdigest()

def garantir_tabelas():
    try:
        con = pymysql.connect(host="localhost", user="root", password="",
                              database="sistema_facil", charset="utf8mb4")
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS aluno (
            id_aluno INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            data_nascimento VARCHAR(20),
            cpf VARCHAR(80),
            email VARCHAR(150),
            telefone VARCHAR(30),
            endereco VARCHAR(255),
            cidade VARCHAR(100),
            estado VARCHAR(5),
            curso_interesse VARCHAR(100),
            como_conheceu VARCHAR(80),
            captador VARCHAR(100),
            observacoes TEXT,
            status_lead VARCHAR(30) DEFAULT 'Lead',
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4""")
        cur.execute("""CREATE TABLE IF NOT EXISTS curso (
            id_curso INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            duracao VARCHAR(60),
            carga_horario VARCHAR(60),
            tipo_curso VARCHAR(40),
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4""")
        cur.execute("""CREATE TABLE IF NOT EXISTS funcionario (
            id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            email VARCHAR(150),
            endereco VARCHAR(255),
            CPF VARCHAR(80),
            telefone VARCHAR(30),
            senha VARCHAR(80),
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4""")
        cur.execute("""CREATE TABLE IF NOT EXISTS venda (
            id_venda INT AUTO_INCREMENT PRIMARY KEY,
            aluno_nome VARCHAR(200),
            curso VARCHAR(150),
            valor DECIMAL(10,2),
            forma_pagamento VARCHAR(60),
            status_venda VARCHAR(30) DEFAULT 'Pago',
            captador VARCHAR(100),
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4""")
        con.commit()
        con.close()
    except Exception as e:
        messagebox.showwarning("DB", f"Aviso ao criar tabelas:\n{e}")

# ─── Helpers ─────────────────────────────────────────────────────────────────
def escurecer(h, f=0.88):
    h = h.lstrip("#")
    r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return f"#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}"

def pill(parent, txt, bg, fg, cmd, padx=16, pady=8, size=10):
    b = tk.Label(parent, text=f" {txt} ", bg=bg, fg=fg,
                 font=("Segoe UI Semibold", size), cursor="hand2",
                 padx=padx, pady=pady)
    hov = escurecer(bg)
    b.bind("<Enter>", lambda _: b.configure(bg=hov))
    b.bind("<Leave>", lambda _: b.configure(bg=bg))
    b.bind("<Button-1>", lambda _: cmd())
    return b

def lbl(parent, text, size=10, bold=False, color=None, bg=None, **kw):
    color = color or C_TEXT
    bg    = bg    or parent.cget("bg")
    w = "bold" if bold else "normal"
    return tk.Label(parent, text=text, fg=color, bg=bg,
                    font=("Segoe UI", size, w), **kw)

def sep(parent, color=C_BORDER, h=1, padx=0, pady=0):
    tk.Frame(parent, bg=color, height=h).pack(fill="x", padx=padx, pady=pady)

def card(parent, padx=16, pady=12, **kw):
    return tk.Frame(parent, bg=C_WHITE,
                    highlightbackground=C_BORDER, highlightthickness=1,
                    padx=padx, pady=pady, **kw)

def entry_field(parent, textvariable=None, width=28, show=""):
    f = tk.Frame(parent, bg=C_WHITE, highlightbackground="#d1d5db",
                 highlightthickness=1)
    e = tk.Entry(f, textvariable=textvariable, font=("Segoe UI", 10),
                 bd=0, bg=C_WHITE, fg=C_TEXT, relief="flat",
                 insertbackground=C_BLUE, show=show, width=width)
    e.pack(fill="x", padx=8, ipady=5)
    e.bind("<FocusIn>",  lambda _: f.configure(highlightbackground=C_BLUE))
    e.bind("<FocusOut>", lambda _: f.configure(highlightbackground="#d1d5db"))
    return f, e

def modal_win(root, titulo, w, h):
    j = tk.Toplevel(root)
    j.title(titulo); j.configure(bg=C_WHITE)
    j.transient(root); j.grab_set(); j.resizable(False, False)
    root.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width()-w)//2
    y = root.winfo_rooty() + (root.winfo_height()-h)//2
    j.geometry(f"{w}x{h}+{max(x,0)}+{max(y,0)}")
    return j

def modal_form_field(parent, label_txt, key, store, oculto=False, width=34):
    lbl(parent, label_txt, size=9, color=C_MUTED).pack(anchor="w", pady=(8,2))
    v = tk.StringVar()
    f, e = entry_field(parent, textvariable=v, width=width, show="*" if oculto else "")
    f.pack(fill="x")
    store[key] = (v, e)

# ══════════════════════════════════════════════════════════════════════════════
# FUNIL (Canvas)
# ══════════════════════════════════════════════════════════════════════════════
def draw_funil(canvas, w, h, data):
    """data = [(label, value, color), ...]  decrescente"""
    canvas.delete("all")
    n      = len(data)
    total  = data[0][1] if data else 1
    top_w  = int(w * 0.85)
    min_w  = int(w * 0.30)
    step_h = (h - 30) // n
    x_c    = w // 2
    for i, (lbl_, val, color) in enumerate(data):
        pct  = val / total if total else 0
        cur_w = int(top_w - (top_w - min_w) * i / n)
        nxt_w = int(top_w - (top_w - min_w) * (i+1) / n)
        y0 = 10 + i * step_h
        y1 = y0 + step_h - 2
        pts = [x_c - cur_w//2, y0,
               x_c + cur_w//2, y0,
               x_c + nxt_w//2, y1,
               x_c - nxt_w//2, y1]
        canvas.create_polygon(pts, fill=color, outline="")
        canvas.create_text(x_c, (y0+y1)//2,
                           text=f"{lbl_}  {val:,}", fill="white",
                           font=("Segoe UI Semibold", 9))
        pct_txt = f"{pct*100:.1f}%"
        canvas.create_text(x_c + cur_w//2 + 28, (y0+y1)//2,
                           text=pct_txt, fill=C_MUTED,
                           font=("Segoe UI", 8))

# ══════════════════════════════════════════════════════════════════════════════
# PIZZA (Canvas)
# ══════════════════════════════════════════════════════════════════════════════
def draw_pizza(canvas, cx, cy, r, data):
    """data = [(label, value, color), ...]"""
    canvas.delete("all")
    total   = sum(v for _, v, _ in data) or 1
    angle   = -90.0
    for lbl_, val, color in data:
        sweep = 360 * val / total
        canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                          start=angle, extent=sweep,
                          fill=color, outline=C_WHITE, width=2)
        angle += sweep
    # Buraco central
    canvas.create_oval(cx-r//2, cy-r//2, cx+r//2, cy+r//2,
                       fill=C_WHITE, outline=C_WHITE)
    canvas.create_text(cx, cy, text=str(sum(v for _,v,_ in data)),
                       font=("Segoe UI Bold", 13), fill=C_TEXT)
    canvas.create_text(cx, cy+14, text="leads",
                       font=("Segoe UI", 8), fill=C_MUTED)

# ══════════════════════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Fácil Educação")
        self.geometry("1366x768")
        self.minsize(1280, 700)
        self.configure(bg=C_BG)
        self.update_idletasks()
        sw,sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-1366)//2}+{(sh-768)//2}")
        self._style()
        self._build()
        self.show("leads")

    def _style(self):
        s = ttk.Style()
        try: s.theme_use("clam")
        except: pass
        s.configure("SF.Treeview", background=C_WHITE, fieldbackground=C_WHITE,
                    foreground=C_TEXT, rowheight=34, font=("Segoe UI", 10),
                    borderwidth=0, relief="flat")
        s.configure("SF.Treeview.Heading", background="#f9fafb", foreground=C_MUTED,
                    font=("Segoe UI Semibold", 9), relief="flat", borderwidth=0)
        s.map("SF.Treeview", background=[("selected", C_LIGHT_BLUE)],
              foreground=[("selected", C_BLUE)])
        s.configure("SF.Vertical.TScrollbar", background=C_BORDER,
                    troughcolor=C_BG, arrowcolor=C_MUTED, borderwidth=0)
        s.configure("SF.TCombobox", fieldbackground=C_WHITE, background=C_WHITE,
                    foreground=C_TEXT, bordercolor="#d1d5db", padding=4)
        s.map("SF.TCombobox", fieldbackground=[("readonly", C_WHITE)],
              selectbackground=[("readonly", C_WHITE)],
              selectforeground=[("readonly", C_TEXT)],
              bordercolor=[("focus", C_BLUE)])

    def _build(self):
        self._sidebar = tk.Frame(self, bg=C_SIDEBAR, width=SIDEBAR_W)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._build_sidebar()
        self._content = tk.Frame(self, bg=C_BG)
        self._content.pack(side="left", fill="both", expand=True)
        self._current = None
        self._nav = {}

    def _build_sidebar(self):
        # Logo
        logo = tk.Frame(self._sidebar, bg=C_SIDEBAR)
        logo.pack(fill="x", padx=16, pady=(20, 16))
        ico = tk.Frame(logo, bg=C_BLUE, width=36, height=36)
        ico.pack(side="left"); ico.pack_propagate(False)
        tk.Label(ico, text="SF", bg=C_BLUE, fg="white",
                 font=("Segoe UI Black", 12)).pack(expand=True)
        t = tk.Frame(logo, bg=C_SIDEBAR)
        t.pack(side="left", padx=(10,0))
        tk.Label(t, text="Sistema Fácil", bg=C_SIDEBAR, fg="white",
                 font=("Segoe UI Semibold", 11)).pack(anchor="w")
        tk.Label(t, text="Educação", bg=C_SIDEBAR, fg="#93c5fd",
                 font=("Segoe UI", 8)).pack(anchor="w")

        tk.Frame(self._sidebar, bg="#2d3f6b", height=1).pack(fill="x", padx=12, pady=(0,8))

        items = [
            ("dashboard",  "⊞", "Dashboard"),
            ("leads",      "👤", "Leads / Alunos"),
            ("vendas",     "💰", "Vendas"),
            ("pagamentos", "💳", "Pagamentos"),
            ("turmas",     "🏫", "Turmas"),
            ("aulas",      "📚", "Aulas"),
            ("frequencia", "📋", "Frequência"),
            ("funil",      "📊", "Funil de Origem"),
            ("relatorios", "📈", "Relatórios"),
            ("config",     "⚙", "Configurações"),
        ]
        self._nav = {}
        for key, icon, label in items:
            row = tk.Frame(self._sidebar, bg=C_SIDEBAR, cursor="hand2")
            row.pack(fill="x", padx=8, pady=1)
            inner = tk.Frame(row, bg=C_SIDEBAR, padx=10, pady=9)
            inner.pack(fill="x")
            tk.Label(inner, text=icon, bg=C_SIDEBAR, fg="#94a3b8",
                     font=("Segoe UI", 11)).pack(side="left")
            lbl_w = tk.Label(inner, text=label, bg=C_SIDEBAR, fg="#cbd5e1",
                             font=("Segoe UI", 10), padx=8)
            lbl_w.pack(side="left")
            if key == "funil":
                tk.Label(inner, text="NOVO", bg="#1d4ed8", fg="white",
                         font=("Segoe UI", 7, "bold"),
                         padx=4, pady=1).pack(side="left")
            for w in (row, inner) + tuple(inner.winfo_children()):
                w.bind("<Enter>",   lambda e, r=row, i=inner: self._nav_hover(r, i, True))
                w.bind("<Leave>",   lambda e, r=row, i=inner: self._nav_hover(r, i, False))
                w.bind("<Button-1>", lambda e, k=key: self.show(k))
            self._nav[key] = (row, inner)

        # Sair
        tk.Frame(self._sidebar, bg="#2d3f6b", height=1).pack(
            fill="x", padx=12, side="bottom", pady=(0,4))
        sair_row = tk.Frame(self._sidebar, bg=C_SIDEBAR, cursor="hand2")
        sair_row.pack(fill="x", padx=8, pady=1, side="bottom")
        sair_inner = tk.Frame(sair_row, bg=C_SIDEBAR, padx=10, pady=9)
        sair_inner.pack(fill="x")
        tk.Label(sair_inner, text="🚪", bg=C_SIDEBAR, fg="#f87171",
                 font=("Segoe UI", 11)).pack(side="left")
        tk.Label(sair_inner, text="Sair", bg=C_SIDEBAR, fg="#f87171",
                 font=("Segoe UI", 10), padx=8).pack(side="left")
        for w in (sair_row, sair_inner):
            w.bind("<Button-1>", lambda _: self._sair())

    def _nav_hover(self, row, inner, on):
        bg = C_SIDEBAR_H if on else C_SIDEBAR
        if row in [self._nav.get(self._current, (None,))[0]]:
            return
        row.configure(bg=bg); inner.configure(bg=bg)
        for c in inner.winfo_children():
            try: c.configure(bg=bg)
            except: pass

    def _set_active(self, key):
        for k, (row, inner) in self._nav.items():
            bg = C_SIDEBAR_A if k == key else C_SIDEBAR
            row.configure(bg=bg); inner.configure(bg=bg)
            for c in inner.winfo_children():
                try: c.configure(bg=bg)
                except: pass

    def _sair(self):
        if messagebox.askyesno("Sair", "Encerrar o sistema?"):
            self.destroy()

    def show(self, key):
        self._current = key
        self._set_active(key)
        for w in self._content.winfo_children():
            w.destroy()
        pages = {
            "leads":      PageLeads,
            "dashboard":  PageDashboard,
            "turmas":     PageCursos,
            "config":     PageFuncionarios,
            "vendas":     lambda p: PageVazia(p, "💰 Vendas"),
            "pagamentos": lambda p: PageVazia(p, "💳 Pagamentos"),
            "aulas":      lambda p: PageVazia(p, "📚 Aulas"),
            "frequencia": lambda p: PageVazia(p, "📋 Frequência"),
            "funil":      lambda p: PageVazia(p, "📊 Funil de Origem"),
            "relatorios": lambda p: PageVazia(p, "📈 Relatórios"),
        }
        builder = pages.get(key)
        if builder:
            builder(self._content).pack(fill="both", expand=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA VAZIA
# ══════════════════════════════════════════════════════════════════════════════
class PageVazia(tk.Frame):
    def __init__(self, parent, titulo):
        super().__init__(parent, bg=C_BG)
        self._topbar(titulo)
        f = card(self); f.pack(fill="both", expand=True, padx=20, pady=(0,20))
        c = tk.Frame(f, bg=C_WHITE); c.place(relx=.5, rely=.5, anchor="center")
        tk.Label(c, text="🚧", bg=C_WHITE, font=("Segoe UI", 38)).pack()
        lbl(c, titulo, 16, True, C_TEXT, C_WHITE).pack(pady=(10,4))
        lbl(c, "Módulo em desenvolvimento.", 11, color=C_MUTED, bg=C_WHITE).pack()

    def _topbar(self, titulo):
        bar = tk.Frame(self, bg=C_WHITE,
                       highlightbackground=C_BORDER, highlightthickness=1, height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        tk.Label(bar, text=titulo, bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI Semibold", 14)).pack(side="left", padx=20, pady=14)
        tk.Label(bar, text="Administrador", bg=C_WHITE, fg=C_MUTED,
                 font=("Segoe UI", 10)).pack(side="right", padx=20)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
class PageDashboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._topbar()
        self._build()
        self.after(150, self._load)

    def _topbar(self):
        bar = tk.Frame(self, bg=C_WHITE,
                       highlightbackground=C_BORDER, highlightthickness=1, height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        tk.Label(bar, text="Dashboard", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI Semibold", 14)).pack(side="left", padx=20, pady=14)
        # Avatar
        av = tk.Frame(bar, bg=C_BLUE, width=32, height=32)
        av.pack(side="right", padx=20, pady=12)
        av.pack_propagate(False)
        tk.Label(av, text="AD", bg=C_BLUE, fg="white",
                 font=("Segoe UI Bold", 9)).pack(expand=True)
        tk.Label(bar, text="Administrador", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI Semibold", 10)).pack(side="right", padx=(0,8))
        tk.Label(bar, text="🔔", bg=C_WHITE, fg=C_MUTED,
                 font=("Segoe UI", 14)).pack(side="right", padx=(0,8))

    def _build(self):
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Stat cards
        row = tk.Frame(body, bg=C_BG); row.pack(fill="x", pady=(0,16))
        self._c_leads  = self._stat(row, "👤", "Leads (mês)", "—", C_BLUE)
        self._c_vendas = self._stat(row, "💰", "Vendas (mês)", "—", C_GREEN)
        self._c_cursos = self._stat(row, "🏫", "Cursos ativos", "—", C_ORANGE)
        self._c_rec    = self._stat(row, "💵", "Receita total", "—", C_PURPLE)

        # Tabela recentes
        c = card(body, padx=16, pady=12); c.pack(fill="both", expand=True)
        lbl(c, "Leads Recentes", 12, True).pack(anchor="w", pady=(0,10))
        cols = ("Nome","Curso","Captador","Status","Data")
        self.tree = self._treeview(c, cols, (200,160,130,80,120))
        self.tree.pack(fill="both", expand=True)

    def _stat(self, parent, icon, title, val, color):
        f = card(parent, padx=14, pady=12)
        f.pack(side="left", fill="both", expand=True, padx=(0,12))
        tk.Frame(f, bg=color, height=3).pack(fill="x")
        row = tk.Frame(f, bg=C_WHITE); row.pack(fill="x", pady=(10,0))
        tk.Label(row, text=icon, bg=C_WHITE, fg=color,
                 font=("Segoe UI", 18)).pack(side="left")
        t = tk.Frame(row, bg=C_WHITE); t.pack(side="left", padx=10)
        lbl(t, title, 9, color=C_MUTED, bg=C_WHITE).pack(anchor="w")
        v_lbl = lbl(t, val, 20, True, color, C_WHITE)
        v_lbl.pack(anchor="w")
        f.lbl = v_lbl
        return f

    def _treeview(self, parent, cols, widths):
        frame = tk.Frame(parent, bg=C_WHITE); frame.pack(fill="x")
        sb = ttk.Scrollbar(frame, orient="vertical", style="SF.Vertical.TScrollbar")
        sb.pack(side="right", fill="y")
        tv = ttk.Treeview(frame, columns=cols, show="headings",
                          style="SF.Treeview", yscrollcommand=sb.set, height=12)
        for c,w in zip(cols, widths):
            tv.heading(c, text=c); tv.column(c, width=w, anchor="w")
        tv.tag_configure("z", background="#f9fafb")
        tv.pack(fill="both", expand=True)
        sb.config(command=tv.yview)
        return tv

    def _load(self):
        try:
            con = conectar()
            with con.cursor() as cur:
                cur.execute("SELECT COUNT(*) as c FROM aluno WHERE MONTH(data_cadastro)=MONTH(NOW())")
                self._c_leads.lbl.configure(text=str(cur.fetchone()["c"]))
                cur.execute("SELECT COUNT(*) as c FROM venda WHERE MONTH(data_venda)=MONTH(NOW())")
                self._c_vendas.lbl.configure(text=str(cur.fetchone()["c"]))
                cur.execute("SELECT COUNT(*) as c FROM curso")
                self._c_cursos.lbl.configure(text=str(cur.fetchone()["c"]))
                cur.execute("SELECT COALESCE(SUM(valor),0) as t FROM venda")
                v = float(cur.fetchone()["t"])
                self._c_rec.lbl.configure(text=f"R${v:,.0f}")
                cur.execute("""SELECT nome, curso_interesse, captador, status_lead,
                    DATE_FORMAT(data_cadastro,'%d/%m/%Y') as dt
                    FROM aluno ORDER BY data_cadastro DESC LIMIT 30""")
                self.tree.delete(*self.tree.get_children())
                for i,r in enumerate(cur.fetchall()):
                    self.tree.insert("","end",
                        values=(r["nome"],r["curso_interesse"],r["captador"],
                                r["status_lead"],r["dt"]),
                        tags=("z",) if i%2==0 else ())
            con.close()
        except: pass


# ══════════════════════════════════════════════════════════════════════════════
# LEADS / ALUNOS  — layout 3 colunas fiel ao design
# ══════════════════════════════════════════════════════════════════════════════
class PageLeads(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._aluno_id = None
        self._build()
        self.after(200, self._load_recentes)

    # ── Top bar ───────────────────────────────────────────────────────────────
    def _build(self):
        # Topbar
        bar = tk.Frame(self, bg=C_WHITE,
                       highlightbackground=C_BORDER, highlightthickness=1, height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        left = tk.Frame(bar, bg=C_WHITE); left.pack(side="left", padx=20, pady=8)
        lbl(left, "Cadastro do Aluno (Lead)", 14, True, C_TEXT, C_WHITE).pack(anchor="w")
        crumb = tk.Frame(left, bg=C_WHITE); crumb.pack(anchor="w")
        lbl(crumb, "Leads", 9, color=C_BLUE, bg=C_WHITE).pack(side="left")
        lbl(crumb, " > Novo Cadastro", 9, color=C_MUTED, bg=C_WHITE).pack(side="left")
        # Avatar + nome
        av = tk.Frame(bar, bg=C_BLUE, width=30, height=30)
        av.pack(side="right", padx=20, pady=13); av.pack_propagate(False)
        tk.Label(av, text="AD", bg=C_BLUE, fg="white",
                 font=("Segoe UI Bold", 8)).pack(expand=True)
        lbl(bar, "Administrador", 10, True, C_TEXT, C_WHITE).pack(side="right", padx=(0,8))
        tk.Label(bar, text="🔔", bg=C_WHITE, fg=C_MUTED,
                 font=("Segoe UI", 13)).pack(side="right", padx=(0,4))

        # Body: 3 colunas
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=5)
        body.columnconfigure(1, weight=3)
        body.columnconfigure(2, weight=3)
        body.rowconfigure(0, weight=1)

        # Coluna 1 – formulário + tabela
        col1 = tk.Frame(body, bg=C_BG)
        col1.grid(row=0, column=0, sticky="nsew", padx=(12,6), pady=12)
        self._build_form(col1)
        self._build_tabela(col1)

        # Coluna 2 – resumo + jornada
        col2 = tk.Frame(body, bg=C_BG)
        col2.grid(row=0, column=1, sticky="nsew", padx=6, pady=12)
        self._build_resumo(col2)
        self._build_jornada(col2)

        # Coluna 3 – funil + pizza + resumo geral
        col3 = tk.Frame(body, bg=C_BG)
        col3.grid(row=0, column=2, sticky="nsew", padx=(6,12), pady=12)
        self._build_funil(col3)
        self._build_origem(col3)

    # ── Formulário ────────────────────────────────────────────────────────────
    def _build_form(self, parent):
        c = card(parent, padx=16, pady=14)
        c.pack(fill="x", pady=(0,10))
        lbl(c, "Cadastro do Aluno (Lead)", 12, True).pack(anchor="w", pady=(0,10))
        sep(c)

        self._v = {}

        # Linha Nome
        lbl(c, "Nome completo *", 9, color=C_MUTED).pack(anchor="w", pady=(8,2))
        f, e = entry_field(c, width=58); f.pack(fill="x")
        self._v["nome"] = tk.StringVar(); e.configure(textvariable=self._v["nome"])

        # Linha nascimento / CPF
        row = tk.Frame(c, bg=C_WHITE); row.pack(fill="x", pady=(8,0))
        left = tk.Frame(row, bg=C_WHITE); left.pack(side="left", fill="x", expand=True, padx=(0,8))
        right= tk.Frame(row, bg=C_WHITE); right.pack(side="left", fill="x", expand=True)
        lbl(left, "Data de nascimento", 9, color=C_MUTED).pack(anchor="w", pady=(0,2))
        self._v["nasc"] = tk.StringVar()
        f,e = entry_field(left, self._v["nasc"], 20); f.pack(fill="x")
        lbl(right,"CPF",9,color=C_MUTED).pack(anchor="w",pady=(0,2))
        self._v["cpf"] = tk.StringVar()
        f,e = entry_field(right, self._v["cpf"], 20); f.pack(fill="x")

        # Email / Telefone
        row2 = tk.Frame(c, bg=C_WHITE); row2.pack(fill="x", pady=(8,0))
        l2 = tk.Frame(row2, bg=C_WHITE); l2.pack(side="left", fill="x", expand=True, padx=(0,8))
        r2 = tk.Frame(row2, bg=C_WHITE); r2.pack(side="left", fill="x", expand=True)
        lbl(l2,"E-mail *",9,color=C_MUTED).pack(anchor="w",pady=(0,2))
        self._v["email"] = tk.StringVar()
        f,e=entry_field(l2,self._v["email"],26);f.pack(fill="x")
        lbl(r2,"Telefone / WhatsApp",9,color=C_MUTED).pack(anchor="w",pady=(0,2))
        self._v["tel"] = tk.StringVar()
        f,e=entry_field(r2,self._v["tel"],22);f.pack(fill="x")

        # Endereço
        lbl(c,"Endereço",9,color=C_MUTED).pack(anchor="w",pady=(8,2))
        self._v["end"] = tk.StringVar()
        f,e=entry_field(c,self._v["end"],58);f.pack(fill="x")

        # Cidade / Estado
        row3=tk.Frame(c,bg=C_WHITE);row3.pack(fill="x",pady=(8,0))
        l3=tk.Frame(row3,bg=C_WHITE);l3.pack(side="left",fill="x",expand=True,padx=(0,8))
        r3=tk.Frame(row3,bg=C_WHITE);r3.pack(side="left",fill="x")
        lbl(l3,"Cidade",9,color=C_MUTED).pack(anchor="w",pady=(0,2))
        self._v["cidade"]=tk.StringVar()
        f,e=entry_field(l3,self._v["cidade"],28);f.pack(fill="x")
        lbl(r3,"Estado",9,color=C_MUTED).pack(anchor="w",pady=(0,2))
        self._v["estado"]=tk.StringVar()
        cb=ttk.Combobox(r3,textvariable=self._v["estado"],
                        values=["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA",
                                "MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN",
                                "RO","RR","RS","SC","SE","SP","TO"],
                        width=6, state="readonly", style="SF.TCombobox",
                        font=("Segoe UI",10))
        cb.pack(fill="x", ipady=4)

        # Curso de interesse
        lbl(c,"Curso de interesse *",9,color=C_MUTED).pack(anchor="w",pady=(8,2))
        self._v["curso"]=tk.StringVar()
        ttk.Combobox(c,textvariable=self._v["curso"],
                     values=["Marketing Digital","Design Gráfico","Tráfego Pago",
                             "Social Media","Programação Web","Fotografia","UX/UI Design"],
                     state="readonly",style="SF.TCombobox",
                     font=("Segoe UI",10)).pack(fill="x",ipady=4)

        # Como conheceu / Captador
        row4=tk.Frame(c,bg=C_WHITE);row4.pack(fill="x",pady=(8,0))
        l4=tk.Frame(row4,bg=C_WHITE);l4.pack(side="left",fill="x",expand=True,padx=(0,8))
        r4=tk.Frame(row4,bg=C_WHITE);r4.pack(side="left",fill="x",expand=True)
        lbl(l4,"Como conheceu?",9,color=C_MUTED).pack(anchor="w",pady=(0,2))
        self._v["como"]=tk.StringVar()
        ttk.Combobox(l4,textvariable=self._v["como"],
                     values=["Instagram","Indicação","Google Ads","Facebook Ads",
                             "Site/Orgânico","YouTube","Outros"],
                     state="readonly",style="SF.TCombobox",
                     font=("Segoe UI",10)).pack(fill="x",ipady=4)
        lbl(r4,"Captador (vendedor) *",9,color=C_MUTED).pack(anchor="w",pady=(0,2))
        self._v["captador"]=tk.StringVar()
        f,e=entry_field(r4,self._v["captador"],24);f.pack(fill="x")

        # Observações
        lbl(c,"Observações",9,color=C_MUTED).pack(anchor="w",pady=(8,2))
        self._obs=tk.Text(c,font=("Segoe UI",10),height=3,bd=0,bg="#f9fafb",
                          relief="flat",fg=C_MUTED,
                          highlightbackground="#d1d5db",highlightthickness=1)
        self._obs.pack(fill="x")
        self._obs.insert("1.0","Interessado no curso noturno...")
        self._obs.bind("<FocusIn>", lambda _: (
            self._obs.configure(fg=C_TEXT,bg=C_WHITE),
            self._obs.delete("1.0","end")
        ) if self._obs.get("1.0","end").strip()=="Interessado no curso noturno..." else None)

        # Botões
        sep(c, pady=(10,0))
        brow=tk.Frame(c,bg=C_WHITE);brow.pack(fill="x",pady=(12,4))
        # Cancelar
        can=tk.Label(brow,text="  Cancelar  ",bg="#f3f4f6",fg=C_TEXT,
                     font=("Segoe UI Semibold",10),padx=12,pady=8,cursor="hand2",
                     highlightbackground=C_BORDER,highlightthickness=1)
        can.pack(side="left",padx=(0,10))
        can.bind("<Button-1>", lambda _: self._limpar())
        # Salvar
        sav=tk.Label(brow,text="  💾  Salvar Lead  ",bg=C_BLUE,fg="white",
                     font=("Segoe UI Semibold",10),padx=12,pady=8,cursor="hand2")
        sav.pack(side="left")
        sav.bind("<Enter>",lambda _:sav.configure(bg=C_BLUE_DARK))
        sav.bind("<Leave>",lambda _:sav.configure(bg=C_BLUE))
        sav.bind("<Button-1>",lambda _:self._salvar())

    # ── Tabela leads recentes ─────────────────────────────────────────────────
    def _build_tabela(self, parent):
        c = card(parent, padx=16, pady=12)
        c.pack(fill="x")
        row = tk.Frame(c, bg=C_WHITE); row.pack(fill="x", pady=(0,10))
        lbl(row, "Leads Recentes", 11, True).pack(side="left")
        lbl(row, "Ver todos os leads →", 9, color=C_BLUE, bg=C_WHITE,
            cursor="hand2").pack(side="right")

        cols = ("Nome","Curso","Captador","Status","Data")
        widths = (170, 130, 110, 70, 90)
        sb = ttk.Scrollbar(c, orient="vertical", style="SF.Vertical.TScrollbar")
        sb.pack(side="right", fill="y")
        self._tree = ttk.Treeview(c, columns=cols, show="headings",
                                   style="SF.Treeview", height=5,
                                   yscrollcommand=sb.set)
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="w")
        self._tree.tag_configure("z", background="#f9fafb")
        self._tree.bind("<Double-1>", self._selecionar)
        self._tree.pack(fill="x", side="left")
        sb.config(command=self._tree.yview)

    # ── Resumo do lead ────────────────────────────────────────────────────────
    def _build_resumo(self, parent):
        c = card(parent, padx=14, pady=12)
        c.pack(fill="x", pady=(0,10))
        lbl(c, "Resumo do Lead", 11, True).pack(anchor="w", pady=(0,8))
        sep(c)

        row1 = tk.Frame(c, bg=C_WHITE); row1.pack(fill="x", pady=(10,6))
        lbl(row1, "Status atual", 9, color=C_MUTED, bg=C_WHITE).pack(side="left")
        tk.Label(row1, text="  LEAD  ", bg=C_GOLD, fg="white",
                 font=("Segoe UI Semibold", 9),
                 padx=6, pady=2).pack(side="right")

        for icon, key, val in [
            ("🗓", "Data do cadastro:", "—"),
            ("👤", "Captador:", "—"),
            ("📚", "Curso de interesse:", "—"),
        ]:
            r = tk.Frame(c, bg=C_WHITE); r.pack(fill="x", pady=3)
            lbl(r, icon, 10, bg=C_WHITE).pack(side="left", padx=(0,6))
            lbl(r, key, 9, color=C_MUTED, bg=C_WHITE).pack(side="left")
            v = lbl(r, val, 9, color=C_TEXT, bg=C_WHITE)
            v.pack(side="right")
            if "cadastro" in key: self._lbl_data  = v
            if "Captador" in key: self._lbl_capt  = v
            if "interesse" in key: self._lbl_curso = v

    # ── Jornada ────────────────────────────────────────────────────────────────
    def _build_jornada(self, parent):
        c = card(parent, padx=14, pady=12)
        c.pack(fill="x")
        lbl(c, "Jornada do Aluno", 11, True).pack(anchor="w", pady=(0,8))
        sep(c)
        steps = [
            ("Cadastro do aluno (lead)", "Lead cadastrado no sistema."),
            ("Registro da venda (captador)", "Registrar negociação e definir cond."),
            ("Definição do status (Pago/Não)", "Definir se o aluno já está pago."),
            ("Registro do pagamento", "Registrar pagamento e emitir comprov."),
            ("Liberação para turma", "Liberar aluno para a turma."),
            ("Formação de turma", "Adicionar aluno à turma."),
            ("Início das aulas", "Aulas liberadas conforme calendário."),
            ("Controle de frequência", "Acompanhar presença nas aulas."),
        ]
        for i, (title, desc) in enumerate(steps):
            r = tk.Frame(c, bg=C_WHITE); r.pack(fill="x", pady=4)
            # Número
            num_f = tk.Frame(r, bg=C_BLUE if i==0 else "#e5e7eb",
                             width=22, height=22)
            num_f.pack(side="left", padx=(0,8)); num_f.pack_propagate(False)
            tk.Label(num_f, text=str(i+1),
                     bg=C_BLUE if i==0 else "#e5e7eb",
                     fg="white" if i==0 else C_MUTED,
                     font=("Segoe UI Semibold", 8)).pack(expand=True)
            txt = tk.Frame(r, bg=C_WHITE); txt.pack(side="left", fill="x", expand=True)
            lbl(txt, title, 9, True if i==0 else False,
                C_BLUE if i==0 else C_TEXT, C_WHITE).pack(anchor="w")
            lbl(txt, desc, 8, color=C_MUTED, bg=C_WHITE).pack(anchor="w")

    # ── Funil ─────────────────────────────────────────────────────────────────
    def _build_funil(self, parent):
        c = card(parent, padx=14, pady=12)
        c.pack(fill="x", pady=(0,10))
        row = tk.Frame(c, bg=C_WHITE); row.pack(fill="x", pady=(0,8))
        lbl(row, "Funil de Origem", 11, True).pack(side="left")
        lbl(row, "Período: Este mês →", 9, color=C_MUTED, bg=C_WHITE).pack(side="right")

        self._funil_canvas = tk.Canvas(c, bg=C_WHITE, highlightthickness=0,
                                        width=260, height=170)
        self._funil_canvas.pack(fill="x")

        data = [
            ("Visitantes", 1248, "#3b82f6"),
            ("Leads",      132,  "#10b981"),
            ("Negociações",62,   "#f59e0b"),
            ("Vendas",     38,   "#f97316"),
            ("Alunos Ativos",35, "#ef4444"),
        ]
        self._funil_canvas.bind("<Configure>",
            lambda e: draw_funil(self._funil_canvas, e.width, e.height, data))
        self.after(300, lambda: draw_funil(self._funil_canvas,
                                           self._funil_canvas.winfo_width() or 260,
                                           170, data))

    # ── Origem dos leads ──────────────────────────────────────────────────────
    def _build_origem(self, parent):
        c = card(parent, padx=14, pady=12)
        c.pack(fill="x", pady=(0,10))
        lbl(c, "Origem dos Leads", 11, True).pack(anchor="w", pady=(0,8))
        sep(c)

        pizza_data = [
            ("Instagram",    31.8, "#e11d48"),
            ("Indicação",    23.9, "#7c3aed"),
            ("Google Ads",   15.0, "#2563eb"),
            ("Facebook Ads", 12.0, "#0ea5e9"),
            ("Site/Orgânico",12.0, "#10b981"),
            ("Outros",        5.3, "#6b7280"),
        ]

        main = tk.Frame(c, bg=C_WHITE); main.pack(fill="x", pady=(8,0))
        self._pizza = tk.Canvas(main, bg=C_WHITE, highlightthickness=0,
                                 width=110, height=110)
        self._pizza.pack(side="left")
        self.after(400, lambda: draw_pizza(
            self._pizza, 55, 55, 50, pizza_data))

        # Legenda
        leg = tk.Frame(main, bg=C_WHITE); leg.pack(side="left", padx=(10,0), fill="y")
        for (label, pct, color) in pizza_data:
            r = tk.Frame(leg, bg=C_WHITE); r.pack(anchor="w", pady=1)
            tk.Label(r, text="●", bg=C_WHITE, fg=color,
                     font=("Segoe UI", 9)).pack(side="left")
            lbl(r, f"{label}  {pct:.1f}%", 8, color=C_MUTED, bg=C_WHITE).pack(side="left")

        lbl(c, "Ver relatório completo →", 9, color=C_BLUE, bg=C_WHITE,
            cursor="hand2").pack(anchor="e", pady=(8,0))

        # Resumo Geral
        self._build_resumo_geral(parent)

    def _build_resumo_geral(self, parent):
        c = card(parent, padx=14, pady=12)
        c.pack(fill="x")
        lbl(c, "Resumo Geral", 11, True).pack(anchor="w", pady=(0,8))
        sep(c)
        grid = tk.Frame(c, bg=C_WHITE); grid.pack(fill="x", pady=(10,0))

        stats = [
            ("👥", "132", "Leads\n(este mês)", C_BLUE),
            ("🛒", "38",  "Vendas\n(este mês)", C_GREEN),
            ("⏱", "R$ 18.750", "Receita\n(este mês)", C_ORANGE),
            ("📊", "28,8%", "Taxa de\nconversão", C_PURPLE),
        ]
        for i, (icon, val, label_, color) in enumerate(stats):
            col = i % 2
            row = i // 2
            f = tk.Frame(grid, bg="#f9fafb",
                         highlightbackground=C_BORDER, highlightthickness=1,
                         padx=10, pady=10)
            f.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            grid.columnconfigure(col, weight=1)
            tk.Label(f, text=icon, bg="#f9fafb", fg=color,
                     font=("Segoe UI", 18)).pack(anchor="w")
            lbl(f, val, 16, True, color, "#f9fafb").pack(anchor="w", pady=(4,0))
            lbl(f, label_, 8, color=C_MUTED, bg="#f9fafb").pack(anchor="w")

        self._lbl_leads_res = None

    # ── DB ────────────────────────────────────────────────────────────────────
    def _load_recentes(self):
        try:
            con = conectar()
            with con.cursor() as cur:
                cur.execute("""SELECT nome, curso_interesse, captador, status_lead,
                    DATE_FORMAT(data_cadastro,'%d/%m/%Y') as dt
                    FROM aluno ORDER BY data_cadastro DESC LIMIT 20""")
                self._tree.delete(*self._tree.get_children())
                for i,r in enumerate(cur.fetchall()):
                    self._tree.insert("","end",
                        values=(r["nome"],r["curso_interesse"],r["captador"],
                                r["status_lead"],r["dt"]),
                        tags=("z",) if i%2==0 else ())
            con.close()
        except: pass

    def _limpar(self):
        for v in self._v.values():
            v.set("")
        self._obs.delete("1.0","end")
        self._obs.insert("1.0","Interessado no curso noturno...")
        self._obs.configure(fg=C_MUTED)
        self._aluno_id = None

    def _salvar(self):
        nome = self._v["nome"].get().strip()
        if not nome:
            messagebox.showwarning("Atenção","O nome completo é obrigatório."); return
        obs = self._obs.get("1.0","end").strip()
        if obs == "Interessado no curso noturno...": obs = ""
        cpf_raw = self._v["cpf"].get().strip()
        try:
            con = conectar()
            with con.cursor() as cur:
                cur.execute("""INSERT INTO aluno
                    (nome,data_nascimento,cpf,email,telefone,
                     endereco,cidade,estado,curso_interesse,
                     como_conheceu,captador,observacoes,status_lead)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Lead')""",
                    (nome, self._v["nasc"].get(), hash256(cpf_raw) if cpf_raw else "",
                     self._v["email"].get(), self._v["tel"].get(),
                     self._v["end"].get(), self._v["cidade"].get(),
                     self._v["estado"].get(), self._v["curso"].get(),
                     self._v["como"].get(), self._v["captador"].get(), obs))
            con.commit(); con.close()
            messagebox.showinfo("Sucesso","Lead salvo com sucesso!")
            self._limpar(); self._load_recentes()
        except Exception as e:
            messagebox.showerror("Erro",f"Falha ao salvar:\n{e}")

    def _selecionar(self, event):
        sel = self._tree.selection()
        if not sel: return
        vals = self._tree.item(sel[0],"values")
        if vals:
            self._lbl_capt.configure(text=vals[2])
            self._lbl_curso.configure(text=vals[1])
            self._lbl_data.configure(text=vals[4])


# ══════════════════════════════════════════════════════════════════════════════
# CURSOS  (aba Turmas)
# ══════════════════════════════════════════════════════════════════════════════
class PageCursos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._dados = []
        self._build()
        self.after(150, self._load)

    def _build(self):
        bar = tk.Frame(self, bg=C_WHITE, highlightbackground=C_BORDER,
                       highlightthickness=1, height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        lbl(bar, "Turmas / Cursos", 14, True, C_TEXT, C_WHITE).pack(side="left", padx=20, pady=14)
        pill(bar, "+  Novo Curso", C_BLUE, "white", self._dlg_add).pack(side="right", padx=20, pady=12)
        pill(bar, "↺ Atualizar", C_GOLD, "white", self._load).pack(side="right", pady=12)

        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=16, pady=14)

        # Cards métricas
        mrow = tk.Frame(body, bg=C_BG); mrow.pack(fill="x", pady=(0,14))
        self._ct = self._mcard(mrow, "Total de Cursos",   C_BLUE)
        self._cc = self._mcard(mrow, "Cursos Técnicos",   C_ORANGE)
        self._cl = self._mcard(mrow, "Cursos Livres",     C_GREEN)

        # Painel tabela
        pan = card(body, padx=14, pady=12); pan.pack(fill="both", expand=True)
        cab = tk.Frame(pan, bg=C_WHITE); cab.pack(fill="x", pady=(0,8))
        lbl(cab, "Catálogo de Cursos", 12, True).pack(side="left")
        bw = tk.Frame(cab, bg="#f3f4f6", highlightbackground=C_BORDER,
                      highlightthickness=1); bw.pack(side="right")
        tk.Label(bw, text="🔍", bg="#f3f4f6", fg=C_MUTED,
                 font=("Segoe UI",11)).pack(side="left",padx=(8,4),pady=4)
        self._vbusca = tk.StringVar()
        self._vbusca.trace_add("write", lambda *_: self._filtrar())
        tk.Entry(bw, textvariable=self._vbusca, bd=0, bg="#f3f4f6",
                 fg=C_TEXT, font=("Segoe UI",10), width=24,
                 relief="flat").pack(side="left", padx=(0,8), pady=6, ipady=2)

        cols = ("ID","Nome","Duração","Carga Horária","Tipo")
        lrgs = (50, 250, 120, 140, 130)
        tw = tk.Frame(pan, bg=C_WHITE); tw.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(tw, orient="vertical", style="SF.Vertical.TScrollbar")
        sb.pack(side="right", fill="y")
        self._tree = ttk.Treeview(tw, columns=cols, show="headings",
                                   style="SF.Treeview", yscrollcommand=sb.set, height=14)
        for c,w in zip(cols,lrgs):
            self._tree.heading(c,text=c); self._tree.column(c,width=w,anchor="w")
        self._tree.tag_configure("z", background="#f9fafb")
        self._tree.pack(fill="both", expand=True)
        sb.config(command=self._tree.yview)

        rod = tk.Frame(pan, bg=C_WHITE); rod.pack(fill="x", pady=(8,0))
        self._lbl_st = lbl(rod, "—", 9, color=C_MUTED, bg=C_WHITE); self._lbl_st.pack(side="left")
        pill(rod, "✖ Excluir", C_RED,    "white", self._dlg_del).pack(side="right", padx=(6,0))
        pill(rod, "✎ Editar",  C_BLUE,   "white", self._dlg_edit).pack(side="right", padx=6)
        pill(rod, "🔍 Buscar", "#f3f4f6", C_TEXT, self._dlg_busca).pack(side="right")

    def _mcard(self, parent, titulo, cor):
        f = card(parent, padx=12, pady=10); f.pack(side="left", fill="x", expand=True, padx=(0,10))
        tk.Frame(f, bg=cor, height=3).pack(fill="x")
        lbl(f, titulo, 9, color=C_MUTED).pack(anchor="w", pady=(8,0))
        v = lbl(f, "—", 22, True, cor); v.pack(anchor="w")
        f.lbl = v; return f

    def _load(self):
        try:
            con = conectar()
            with con.cursor() as cur:
                cur.execute("SELECT id_curso,nome,duracao,carga_horario,tipo_curso FROM curso ORDER BY id_curso")
                self._dados = cur.fetchall()
            con.close(); self._popular(self._dados); self._cards(self._dados)
            self._lbl_st.configure(text=f"{len(self._dados)} curso(s).")
        except Exception as e: self._lbl_st.configure(text=f"Erro: {e}")

    def _popular(self, rows):
        self._tree.delete(*self._tree.get_children())
        for i,r in enumerate(rows):
            self._tree.insert("","end",
                values=(r["id_curso"],r["nome"],r["duracao"],
                        r["carga_horario"],r["tipo_curso"]),
                tags=("z",) if i%2==0 else ())

    def _filtrar(self):
        t = self._vbusca.get().lower()
        rows = self._dados if not t else [
            r for r in self._dados if t in r["nome"].lower()]
        self._popular(rows)

    def _cards(self, d):
        self._ct.lbl.configure(text=str(len(d)))
        self._cc.lbl.configure(text=str(sum(1 for r in d if str(r.get("tipo_curso","")).lower()=="tecnico")))
        self._cl.lbl.configure(text=str(sum(1 for r in d if str(r.get("tipo_curso","")).lower()=="livre")))

    # Modais CRUD
    def _dlg_add(self):
        j = modal_win(self.winfo_toplevel(), "Novo Curso", 480, 460)
        self._mform(j, "Novo Curso", "Preencha os dados do novo curso.", self._salvar_curso, j)

    def _mform(self, j, titulo, sub, cmd, jref):
        self._jref = jref
        cab = tk.Frame(j, bg=C_WHITE); cab.pack(fill="x", padx=30, pady=(24,0))
        lbl(cab, titulo, 14, True, C_BLUE, C_WHITE).pack(anchor="w")
        lbl(cab, sub, 9, color=C_MUTED, bg=C_WHITE).pack(anchor="w", pady=(2,0))
        sep(j, padx=30, pady=(12,0))
        form = tk.Frame(j, bg=C_WHITE); form.pack(fill="both", expand=True, padx=30, pady=(12,0))
        self._ce = {}
        for lbl_t, k in [("Nome do curso","nome"),("Duração","duracao"),("Carga Horária","carga_horario")]:
            modal_form_field(form, lbl_t, k, self._ce)
        lbl(form, "Tipo de Curso", 9, color=C_MUTED, bg=C_WHITE).pack(anchor="w", pady=(8,2))
        v = tk.StringVar(value="livre")
        cb = ttk.Combobox(form, textvariable=v, values=["capacitacao","livre","tecnico"],
                          state="readonly", style="SF.TCombobox", font=("Segoe UI",10))
        cb.pack(fill="x", ipady=4)
        self._ce["tipo_curso"] = (v, cb)
        sep(j, padx=30, pady=(12,0))
        br = tk.Frame(j, bg=C_WHITE); br.pack(fill="x", padx=30, pady=16)
        pill(br, "Cancelar", "#f3f4f6", C_TEXT, j.destroy).pack(side="right", padx=(8,0))
        pill(br, "Salvar", C_BLUE, "white", cmd).pack(side="right")

    def _salvar_curso(self):
        nome = self._ce["nome"][0].get().strip()
        if not nome: messagebox.showwarning("Atenção","Nome é obrigatório.",parent=self._jref); return
        try:
            con=conectar()
            with con.cursor() as cur:
                cur.execute("INSERT INTO curso (nome,duracao,carga_horario,tipo_curso) VALUES (%s,%s,%s,%s)",
                    (nome,self._ce["duracao"][0].get(),self._ce["carga_horario"][0].get(),self._ce["tipo_curso"][0].get()))
            con.commit(); con.close()
            messagebox.showinfo("Sucesso","Curso salvo!",parent=self._jref)
            self._jref.destroy(); self._load()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self._jref)

    def _dlg_busca(self):
        j = modal_win(self.winfo_toplevel(),"Buscar Curso",420,260)
        cab=tk.Frame(j,bg=C_WHITE);cab.pack(fill="x",padx=30,pady=(24,0))
        lbl(cab,"Buscar Curso",14,True,C_BLUE,C_WHITE).pack(anchor="w")
        form=tk.Frame(j,bg=C_WHITE);form.pack(fill="x",padx=30,pady=12)
        s={}; modal_form_field(form,"Nome do curso","nome",s)
        self._sb=s["nome"][1]; self._jbusca=j
        br=tk.Frame(j,bg=C_WHITE);br.pack(fill="x",padx=30,pady=8)
        pill(br,"Cancelar","#f3f4f6",C_TEXT,j.destroy).pack(side="right",padx=(8,0))
        pill(br,"Buscar",C_BLUE,"white",self._exec_busca).pack(side="right")

    def _exec_busca(self):
        t=self._sb.get().strip()
        try:
            con=conectar()
            with con.cursor() as cur:
                cur.execute("SELECT id_curso,nome,duracao,carga_horario,tipo_curso FROM curso WHERE nome LIKE %s",
                            (f"%{t}%",))
                self._dados=cur.fetchall()
            con.close(); self._popular(self._dados); self._jbusca.destroy()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self._jbusca)

    def _sel_id(self):
        sel=self._tree.selection()
        if not sel: messagebox.showwarning("Atenção","Selecione um curso."); return None
        return self._tree.item(sel[0],"values")[0]

    def _dlg_edit(self):
        cid=self._sel_id()
        if not cid: return
        j=modal_win(self.winfo_toplevel(),"Editar Curso",480,360)
        self._jref=j
        cab=tk.Frame(j,bg=C_WHITE);cab.pack(fill="x",padx=30,pady=(24,0))
        lbl(cab,"Editar Curso",14,True,C_BLUE,C_WHITE).pack(anchor="w")
        sep(j,padx=30,pady=(12,0))
        form=tk.Frame(j,bg=C_WHITE);form.pack(fill="x",padx=30,pady=12)
        self._ce={}
        for lt,k in [("Novo Nome","nome"),("Nova Duração","duracao"),("Nova Carga Horária","carga_horario")]:
            modal_form_field(form,lt,k,self._ce)
        sep(j,padx=30,pady=(12,0))
        br=tk.Frame(j,bg=C_WHITE);br.pack(fill="x",padx=30,pady=16)
        pill(br,"Cancelar","#f3f4f6",C_TEXT,j.destroy).pack(side="right",padx=(8,0))
        pill(br,"Atualizar",C_BLUE,"white",
             lambda: self._exec_edit(cid)).pack(side="right")

    def _exec_edit(self, cid):
        try:
            con=conectar()
            with con.cursor() as cur:
                cur.execute("UPDATE curso SET nome=%s,duracao=%s,carga_horario=%s WHERE id_curso=%s",
                    (self._ce["nome"][0].get(),self._ce["duracao"][0].get(),
                     self._ce["carga_horario"][0].get(),cid))
            con.commit(); con.close()
            messagebox.showinfo("Sucesso","Curso atualizado!",parent=self._jref)
            self._jref.destroy(); self._load()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self._jref)

    def _dlg_del(self):
        cid=self._sel_id()
        if not cid: return
        if not messagebox.askyesno("Confirmar",f"Excluir curso ID {cid}?"): return
        try:
            con=conectar()
            with con.cursor() as cur: cur.execute("DELETE FROM curso WHERE id_curso=%s",(cid,))
            con.commit(); con.close(); self._load()
        except Exception as e: messagebox.showerror("Erro",str(e))


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIONÁRIOS  (Configurações)
# ══════════════════════════════════════════════════════════════════════════════
class PageFuncionarios(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._dados = []
        self._build()
        self.after(150, self._load)

    def _build(self):
        bar = tk.Frame(self, bg=C_WHITE, highlightbackground=C_BORDER,
                       highlightthickness=1, height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        lbl(bar, "Configurações — Funcionários", 14, True, C_TEXT, C_WHITE).pack(side="left", padx=20, pady=14)
        pill(bar, "+  Novo Funcionário", C_BLUE, "white", self._dlg_add).pack(side="right", padx=20, pady=12)
        pill(bar, "↺ Atualizar", C_GOLD, "white", self._load).pack(side="right", pady=12)

        body = tk.Frame(self, bg=C_BG); body.pack(fill="both", expand=True, padx=16, pady=14)
        mrow = tk.Frame(body, bg=C_BG); mrow.pack(fill="x", pady=(0,14))
        self._ct = self._mcard(mrow, "Total", C_BLUE)
        self._ce = self._mcard(mrow, "Com E-mail", C_ORANGE)
        self._ct2= self._mcard(mrow, "Com Telefone", C_GREEN)

        pan = card(body, padx=14, pady=12); pan.pack(fill="both", expand=True)
        cab = tk.Frame(pan, bg=C_WHITE); cab.pack(fill="x", pady=(0,8))
        lbl(cab, "Quadro de Funcionários", 12, True).pack(side="left")
        bw = tk.Frame(cab, bg="#f3f4f6", highlightbackground=C_BORDER,
                      highlightthickness=1); bw.pack(side="right")
        tk.Label(bw, text="🔍", bg="#f3f4f6", fg=C_MUTED,
                 font=("Segoe UI",11)).pack(side="left",padx=(8,4),pady=4)
        self._vbusca = tk.StringVar()
        self._vbusca.trace_add("write", lambda *_: self._filtrar())
        tk.Entry(bw, textvariable=self._vbusca, bd=0, bg="#f3f4f6",
                 fg=C_TEXT, font=("Segoe UI",10), width=24,
                 relief="flat").pack(side="left", padx=(0,8), pady=6, ipady=2)

        cols = ("ID","Nome","E-mail","Endereço","CPF","Telefone")
        lrgs = (50, 200, 200, 200, 160, 120)
        tw = tk.Frame(pan, bg=C_WHITE); tw.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(tw, orient="vertical", style="SF.Vertical.TScrollbar")
        sb.pack(side="right", fill="y")
        self._tree = ttk.Treeview(tw, columns=cols, show="headings",
                                   style="SF.Treeview", yscrollcommand=sb.set, height=14)
        for c,w in zip(cols,lrgs):
            self._tree.heading(c,text=c); self._tree.column(c,width=w,anchor="w")
        self._tree.tag_configure("z", background="#f9fafb")
        self._tree.pack(fill="both", expand=True)
        sb.config(command=self._tree.yview)

        rod = tk.Frame(pan, bg=C_WHITE); rod.pack(fill="x", pady=(8,0))
        self._lbl_st = lbl(rod, "—", 9, color=C_MUTED, bg=C_WHITE); self._lbl_st.pack(side="left")
        pill(rod, "✖ Remover", C_RED,    "white", self._dlg_del).pack(side="right", padx=(6,0))
        pill(rod, "✎ Editar",  C_BLUE,   "white", self._dlg_edit).pack(side="right", padx=6)
        pill(rod, "🔍 Buscar", "#f3f4f6", C_TEXT, self._dlg_busca).pack(side="right")

    def _mcard(self, parent, titulo, cor):
        f = card(parent, padx=12, pady=10); f.pack(side="left", fill="x", expand=True, padx=(0,10))
        tk.Frame(f, bg=cor, height=3).pack(fill="x")
        lbl(f, titulo, 9, color=C_MUTED).pack(anchor="w", pady=(8,0))
        v = lbl(f, "—", 22, True, cor); v.pack(anchor="w")
        f.lbl = v; return f

    def _load(self):
        try:
            con = conectar()
            with con.cursor() as cur:
                cur.execute("SELECT id_funcionario,nome,email,endereco,CPF,telefone FROM funcionario ORDER BY id_funcionario")
                self._dados = cur.fetchall()
            con.close(); self._popular(self._dados); self._cards(self._dados)
            self._lbl_st.configure(text=f"{len(self._dados)} funcionário(s).")
        except Exception as e: self._lbl_st.configure(text=f"Erro: {e}")

    def _popular(self, rows):
        self._tree.delete(*self._tree.get_children())
        for i,r in enumerate(rows):
            self._tree.insert("","end",
                values=(r["id_funcionario"],r["nome"],r["email"] or "",
                        r["endereco"] or "",r["CPF"] or "",r["telefone"] or ""),
                tags=("z",) if i%2==0 else ())

    def _filtrar(self):
        t = self._vbusca.get().lower()
        rows = self._dados if not t else [
            r for r in self._dados if t in r["nome"].lower()]
        self._popular(rows)

    def _cards(self, d):
        self._ct.lbl.configure(text=str(len(d)))
        self._ce.lbl.configure(text=str(sum(1 for r in d if r.get("email"))))
        self._ct2.lbl.configure(text=str(sum(1 for r in d if r.get("telefone"))))

    def _dlg_add(self):
        j = modal_win(self.winfo_toplevel(), "Novo Funcionário", 480, 640)
        self._jref = j
        cab = tk.Frame(j, bg=C_WHITE); cab.pack(fill="x", padx=30, pady=(24,0))
        lbl(cab, "Novo Funcionário", 14, True, C_BLUE, C_WHITE).pack(anchor="w")
        lbl(cab, "CPF e senha são protegidos com SHA-256.", 9, color=C_MUTED, bg=C_WHITE).pack(anchor="w")
        sep(j, padx=30, pady=(12,0))
        form = tk.Frame(j, bg=C_WHITE); form.pack(fill="both", expand=True, padx=30, pady=12)
        self._fe = {}
        for lt, k, oculto in [
            ("Nome completo","nome",False),("E-mail","email",False),
            ("Endereço","endereco",False),("CPF","cpf",False),
            ("Telefone","telefone",False),("Senha","senha",True),("Confirmar Senha","senha2",True)]:
            modal_form_field(form, lt, k, self._fe, oculto)
        self._lbl_sv = lbl(form, "", 8, color=C_RED, bg=C_WHITE); self._lbl_sv.pack(anchor="w")
        def check(*_):
            s1,s2=self._fe["senha"][0].get(),self._fe["senha2"][0].get()
            if s2 and s1!=s2: self._lbl_sv.configure(text="Senhas não conferem.",fg=C_RED)
            elif s1 and s1==s2: self._lbl_sv.configure(text="✓ Senhas ok.",fg=C_GREEN)
            else: self._lbl_sv.configure(text="")
        self._fe["senha"][1].bind("<KeyRelease>",check)
        self._fe["senha2"][1].bind("<KeyRelease>",check)
        sep(j, padx=30, pady=(8,0))
        br = tk.Frame(j, bg=C_WHITE); br.pack(fill="x", padx=30, pady=14)
        pill(br,"Cancelar","#f3f4f6",C_TEXT,j.destroy).pack(side="right",padx=(8,0))
        pill(br,"Salvar",C_BLUE,"white",self._salvar_func).pack(side="right")

    def _salvar_func(self):
        nome = self._fe["nome"][0].get().strip()
        s1,s2 = self._fe["senha"][0].get(), self._fe["senha2"][0].get()
        if not nome: messagebox.showwarning("Atenção","Nome obrigatório.",parent=self._jref); return
        if s1 and s1!=s2: messagebox.showerror("Senha","Senhas não conferem.",parent=self._jref); return
        cpf = self._fe["cpf"][0].get().strip()
        try:
            con=conectar()
            with con.cursor() as cur:
                cur.execute("INSERT INTO funcionario (nome,email,endereco,CPF,telefone,senha) VALUES (%s,%s,%s,%s,%s,%s)",
                    (nome,self._fe["email"][0].get() or None,self._fe["endereco"][0].get(),
                     hash256(cpf) if cpf else "",self._fe["telefone"][0].get(),
                     hash256(s1) if s1 else ""))
            con.commit(); con.close()
            messagebox.showinfo("Sucesso","Funcionário cadastrado!",parent=self._jref)
            self._jref.destroy(); self._load()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self._jref)

    def _dlg_busca(self):
        j=modal_win(self.winfo_toplevel(),"Buscar Funcionário",420,260)
        cab=tk.Frame(j,bg=C_WHITE);cab.pack(fill="x",padx=30,pady=(24,0))
        lbl(cab,"Buscar Funcionário",14,True,C_BLUE,C_WHITE).pack(anchor="w")
        form=tk.Frame(j,bg=C_WHITE);form.pack(fill="x",padx=30,pady=12)
        s={}; modal_form_field(form,"Nome","nome",s)
        self._sb_f=s["nome"][1]; self._jbf=j
        br=tk.Frame(j,bg=C_WHITE);br.pack(fill="x",padx=30,pady=8)
        pill(br,"Cancelar","#f3f4f6",C_TEXT,j.destroy).pack(side="right",padx=(8,0))
        pill(br,"Buscar",C_BLUE,"white",self._exec_busca_f).pack(side="right")

    def _exec_busca_f(self):
        t=self._sb_f.get().strip()
        try:
            con=conectar()
            with con.cursor() as cur:
                cur.execute("SELECT id_funcionario,nome,email,endereco,CPF,telefone FROM funcionario WHERE nome LIKE %s",(f"%{t}%",))
                self._dados=cur.fetchall()
            con.close(); self._popular(self._dados); self._jbf.destroy()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self._jbf)

    def _sel_id(self):
        sel=self._tree.selection()
        if not sel: messagebox.showwarning("Atenção","Selecione um funcionário."); return None
        return self._tree.item(sel[0],"values")[0]

    def _dlg_edit(self):
        fid=self._sel_id()
        if not fid: return
        j=modal_win(self.winfo_toplevel(),"Editar Funcionário",480,400)
        self._jref=j
        cab=tk.Frame(j,bg=C_WHITE);cab.pack(fill="x",padx=30,pady=(24,0))
        lbl(cab,"Atualizar Cadastro",14,True,C_BLUE,C_WHITE).pack(anchor="w")
        sep(j,padx=30,pady=(12,0))
        form=tk.Frame(j,bg=C_WHITE);form.pack(fill="x",padx=30,pady=12)
        self._fe={}
        for lt,k,oc in [("Novo E-mail","email",False),("Novo Telefone","telefone",False),
                        ("Nova Senha (opcional)","senha",True),("Confirmar Senha","senha2",True)]:
            modal_form_field(form,lt,k,self._fe,oc)
        sep(j,padx=30,pady=(12,0))
        br=tk.Frame(j,bg=C_WHITE);br.pack(fill="x",padx=30,pady=14)
        pill(br,"Cancelar","#f3f4f6",C_TEXT,j.destroy).pack(side="right",padx=(8,0))
        pill(br,"Atualizar",C_BLUE,"white",lambda:self._exec_edit_f(fid)).pack(side="right")

    def _exec_edit_f(self, fid):
        s1,s2=self._fe["senha"][0].get(),self._fe["senha2"][0].get()
        if s1 and s1!=s2: messagebox.showerror("Senha","Senhas não conferem.",parent=self._jref); return
        try:
            con=conectar()
            with con.cursor() as cur:
                if s1:
                    cur.execute("UPDATE funcionario SET email=%s,telefone=%s,senha=%s WHERE id_funcionario=%s",
                        (self._fe["email"][0].get() or None,self._fe["telefone"][0].get(),hash256(s1),fid))
                else:
                    cur.execute("UPDATE funcionario SET email=%s,telefone=%s WHERE id_funcionario=%s",
                        (self._fe["email"][0].get() or None,self._fe["telefone"][0].get(),fid))
            con.commit(); con.close()
            messagebox.showinfo("Sucesso","Dados atualizados!",parent=self._jref)
            self._jref.destroy(); self._load()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self._jref)

    def _dlg_del(self):
        fid=self._sel_id()
        if not fid: return
        if not messagebox.askyesno("Confirmar",f"Remover funcionário ID {fid}?"): return
        try:
            con=conectar()
            with con.cursor() as cur: cur.execute("DELETE FROM funcionario WHERE id_funcionario=%s",(fid,))
            con.commit(); con.close(); self._load()
        except Exception as e: messagebox.showerror("Erro",str(e))


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    garantir_tabelas()
    App().mainloop()
