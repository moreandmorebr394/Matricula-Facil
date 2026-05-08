"""
Notificações flutuantes (toasts) e animações utilitárias.
"""
import tkinter as tk
from componentes import tema


# =====================================================================
# Toast / notificação
# =====================================================================
class NotificacaoFlutuante:
    """Exibe uma notificação que desaparece automaticamente.

    Uso:
        NotificacaoFlutuante.exibir(janela_pai, "Lead criado!", tipo="sucesso")
    """

    CORES = {
        "sucesso": (tema.VERDE_SUCESSO, "\u2714"),
        "erro": (tema.VERMELHO_ERRO, "\u2716"),
        "alerta": (tema.LARANJA_ALERTA, "\u26A0"),
        "info": (tema.AZUL_PRINCIPAL, "\u2139"),
    }

    @classmethod
    def exibir(
        cls,
        pai: tk.Misc,
        mensagem: str,
        tipo: str = "sucesso",
        duracao_ms: int = 2000,
    ):
        try:
            cor, icone = cls.CORES.get(tipo, cls.CORES["info"])

            janela = tk.Toplevel(pai)
            janela.overrideredirect(True)
            janela.attributes("-topmost", True)
            try:
                janela.attributes("-alpha", 0.0)
            except tk.TclError:
                pass

            largura, altura = 360, 56

            # Posição: canto inferior direito da janela pai
            pai.update_idletasks()
            x_pai = pai.winfo_rootx()
            y_pai = pai.winfo_rooty()
            w_pai = pai.winfo_width() or 1200
            h_pai = pai.winfo_height() or 700
            x = x_pai + w_pai - largura - 24
            y = y_pai + h_pai - altura - 32
            janela.geometry(f"{largura}x{altura}+{x}+{y}")

            quadro = tk.Frame(janela, bg=cor)
            quadro.pack(fill="both", expand=True)

            tk.Label(
                quadro,
                text=icone,
                bg=cor,
                fg="#FFFFFF",
                font=tema.obter_fonte(18, "bold"),
            ).pack(side="left", padx=(16, 8))

            tk.Label(
                quadro,
                text=mensagem,
                bg=cor,
                fg="#FFFFFF",
                font=tema.fonte_destaque(11),
                anchor="w",
                justify="left",
                wraplength=260,
            ).pack(side="left", fill="both", expand=True, padx=(0, 12))

            # Animação de fade-in
            cls._fade(janela, alvo=0.95, passo=0.08, sentido=+1)

            # Agenda destruição com fade-out
            def _ocultar():
                cls._fade(janela, alvo=0.0, passo=0.08, sentido=-1)
                pai.after(220, lambda: cls._destruir_seguro(janela))

            pai.after(duracao_ms, _ocultar)

        except Exception as exc:
            print("[NotificacaoFlutuante] erro:", exc)

    @staticmethod
    def _destruir_seguro(janela):
        try:
            if janela.winfo_exists():
                janela.destroy()
        except Exception:
            pass

    @staticmethod
    def _fade(janela, alvo: float, passo: float, sentido: int):
        try:
            atual = janela.attributes("-alpha")
        except tk.TclError:
            return
        try:
            if sentido > 0 and atual < alvo:
                janela.attributes("-alpha", min(alvo, atual + passo))
                janela.after(20, lambda: NotificacaoFlutuante._fade(janela, alvo, passo, sentido))
            elif sentido < 0 and atual > alvo:
                janela.attributes("-alpha", max(alvo, atual - passo))
                janela.after(20, lambda: NotificacaoFlutuante._fade(janela, alvo, passo, sentido))
        except tk.TclError:
            pass


# =====================================================================
# Animação de cursor (rastro)
# =====================================================================
class RastroCursor:
    """Pequeno rastro que segue o cursor sobre uma janela.

    Desenha pontos pontilhados que decaem com o tempo. Útil em telas
    de marketing/branding (login, registro). Para evitar peso, só roda
    enquanto estiver vinculado.
    """

    def __init__(self, raiz: tk.Misc, cor: str = "#F4C430", quantidade: int = 14):
        self._raiz = raiz
        self._cor = cor
        self._quantidade = quantidade
        self._pontos = []     # lista de Toplevels
        self._ativo = False
        self._tarefa = None

    def iniciar(self):
        if self._ativo:
            return
        self._ativo = True
        # Cria as bolinhas (Toplevels minúsculos)
        for i in range(self._quantidade):
            try:
                t = tk.Toplevel(self._raiz)
                t.overrideredirect(True)
                try:
                    t.attributes("-topmost", True)
                    t.attributes("-alpha", 0.0)
                except tk.TclError:
                    pass
                tam = max(2, 9 - i // 2)
                t.geometry(f"{tam}x{tam}+0+0")
                t.configure(bg=self._cor)
                self._pontos.append({"win": t, "tam": tam})
            except Exception:
                pass

        self._raiz.bind("<Motion>", self._mover, add="+")

    def _mover(self, evento):
        if not self._ativo or not self._pontos:
            return
        # Empurra novas posições e desloca as antigas
        for i in range(len(self._pontos) - 1, 0, -1):
            ant = self._pontos[i - 1]["win"]
            atual = self._pontos[i]["win"]
            try:
                geo = ant.geometry()
                # geo no formato '6x6+x+y'
                partes = geo.split("+")
                if len(partes) >= 3:
                    atual.geometry(f"{self._pontos[i]['tam']}x{self._pontos[i]['tam']}+{partes[1]}+{partes[2]}")
                    try:
                        atual.attributes("-alpha", max(0.05, 0.85 - i * 0.06))
                    except tk.TclError:
                        pass
            except tk.TclError:
                pass
        # Atualiza o primeiro ponto na posição do cursor
        try:
            x = evento.x_root
            y = evento.y_root
            primeiro = self._pontos[0]["win"]
            tam = self._pontos[0]["tam"]
            primeiro.geometry(f"{tam}x{tam}+{x}+{y}")
            try:
                primeiro.attributes("-alpha", 0.85)
            except tk.TclError:
                pass
        except (IndexError, tk.TclError):
            pass

    def parar(self):
        self._ativo = False
        for p in self._pontos:
            try:
                p["win"].destroy()
            except Exception:
                pass
        self._pontos.clear()
        try:
            self._raiz.unbind("<Motion>")
        except tk.TclError:
            pass


# =====================================================================
# Linhas pontilhadas decorativas (animadas)
# =====================================================================
class LinhasPontilhadasAnimadas:
    """Desenha linhas pontilhadas se movendo num Canvas.

    Usado como decoração de fundo nas telas de login/registro para dar
    sensação de movimento sutil.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        cor: str = "#FFFFFF",
        quantidade: int = 6,
    ):
        self._canvas = canvas
        self._cor = cor
        self._quantidade = quantidade
        self._linhas = []
        self._tarefa = None
        self._ativo = False

    def iniciar(self):
        if self._ativo:
            return
        self._ativo = True
        self._canvas.update_idletasks()
        largura = self._canvas.winfo_width() or 600
        altura = self._canvas.winfo_height() or 600

        import random
        for _ in range(self._quantidade):
            x = random.randint(40, max(80, largura - 40))
            y = random.randint(40, max(80, altura - 40))
            comprimento = random.randint(50, 130)
            inclinacao = random.choice([-1, 1])
            id_linha = self._canvas.create_line(
                x, y, x + comprimento, y + (comprimento * inclinacao // 4),
                fill=self._cor,
                width=1,
                dash=(2, 6),
            )
            self._linhas.append({
                "id": id_linha,
                "vx": random.choice([-1, 1]),
                "vy": random.choice([-1, 1]),
                "largura": largura,
                "altura": altura,
            })

        self._animar()

    def _animar(self):
        if not self._ativo:
            return
        for linha in self._linhas:
            try:
                self._canvas.move(linha["id"], linha["vx"], linha["vy"])
                coords = self._canvas.coords(linha["id"])
                if not coords:
                    continue
                x1, y1, x2, y2 = coords
                w = self._canvas.winfo_width() or linha["largura"]
                h = self._canvas.winfo_height() or linha["altura"]
                if x1 < 0 or x2 > w:
                    linha["vx"] *= -1
                if y1 < 0 or y2 > h:
                    linha["vy"] *= -1
            except tk.TclError:
                continue
        self._tarefa = self._canvas.after(50, self._animar)

    def parar(self):
        self._ativo = False
        if self._tarefa:
            try:
                self._canvas.after_cancel(self._tarefa)
            except tk.TclError:
                pass


# =====================================================================
# Fade-in para janelas
# =====================================================================
def fade_in_janela(janela: tk.Misc, duracao_ms: int = 240):
    try:
        janela.attributes("-alpha", 0.0)
    except tk.TclError:
        return

    passos = 16
    incremento = 1.0 / passos

    def _passo(i=0):
        try:
            valor = min(1.0, incremento * (i + 1))
            janela.attributes("-alpha", valor)
        except tk.TclError:
            return
        if i + 1 < passos:
            janela.after(int(duracao_ms / passos), lambda: _passo(i + 1))

    _passo()
