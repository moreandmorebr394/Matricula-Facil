"""
Painel visual decorativo lateral usado nas telas de Login/Registro.

Desenha o fundo azul, formas geométricas inclinadas, partículas e
um título com subtítulo. Funciona como "lado direito da tela de
registro" e "lado esquerdo da tela de login" (igual identidade,
posições diferentes).
"""
import random
import tkinter as tk
from componentes import tema
from componentes.notificacoes import LinhasPontilhadasAnimadas


class PainelVisualLateral(tk.Frame):

    def __init__(
        self,
        mestre,
        titulo: str,
        subtitulo: str,
        codigo_decorativo: str = "#3C507D",
        **kwargs,
    ):
        super().__init__(mestre, bg=tema.AZUL_PRINCIPAL, **kwargs)

        self._canvas = tk.Canvas(
            self,
            bg=tema.AZUL_PRINCIPAL,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack(fill="both", expand=True)

        self._titulo = titulo
        self._subtitulo = subtitulo
        self._codigo = codigo_decorativo
        self._linhas_animadas = LinhasPontilhadasAnimadas(
            self._canvas,
            cor="#FFFFFF",
            quantidade=5,
        )

        self._canvas.bind("<Configure>", self._redesenhar)

    def _redesenhar(self, evento=None):
        self._canvas.delete("all")
        largura = self._canvas.winfo_width()
        altura = self._canvas.winfo_height()
        if largura < 50 or altura < 50:
            return

        # Gradiente vertical leve (faixas sobrepostas)
        passos = 60
        for i in range(passos):
            t = i / passos
            cor = self._misturar(tema.AZUL_PRINCIPAL, tema.AZUL_ESCURO, t * 0.55)
            y0 = int(altura * t)
            y1 = int(altura * (i + 1) / passos)
            self._canvas.create_rectangle(
                0, y0, largura, y1 + 1, fill=cor, outline=cor,
            )

        # Quadrados geométricos inclinados
        random.seed(7)  # sempre o mesmo padrão
        formas = [
            (0.10, 0.10, 80, "#4F65A1"),
            (0.85, 0.18, 60, "#F4C430"),
            (0.05, 0.55, 50, tema.AZUL_HOVER),
            (0.78, 0.65, 90, "#4F65A1"),
            (0.45, 0.15, 30, "#F4C430"),
            (0.35, 0.85, 60, tema.AZUL_HOVER),
            (0.15, 0.78, 40, "#F4C430"),
        ]
        for fx, fy, t, cor in formas:
            x = int(largura * fx)
            y = int(altura * fy)
            # quadrado rotacionado: usar polígono inclinado
            ang = random.uniform(-0.5, 0.5)
            pts = self._quadrado_inclinado(x, y, t, ang)
            self._canvas.create_polygon(pts, fill=cor, outline=cor, smooth=False)

        # Círculos pequenos (partículas)
        for _ in range(18):
            cx = random.randint(0, largura)
            cy = random.randint(0, altura)
            r = random.randint(2, 5)
            cor = random.choice(["#FFFFFF", "#F4C430", "#A8B0CB"])
            self._canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r, fill=cor, outline=cor,
            )

        # Texto pequeno do código
        self._canvas.create_text(
            48, int(altura * 0.30),
            text=self._codigo,
            fill="#A8B0CB",
            font=tema.obter_fonte(11, "normal"),
            anchor="w",
        )
        # Título principal (multilinha automática)
        self._canvas.create_text(
            48, int(altura * 0.42),
            text=self._titulo,
            fill="#FFFFFF",
            font=tema.fonte_titulo(28),
            anchor="w",
            width=largura - 96,
        )
        # Subtítulo
        self._canvas.create_text(
            48, int(altura * 0.65),
            text=self._subtitulo,
            fill="#D2D9EE",
            font=tema.fonte_subtitulo(13),
            anchor="w",
            width=largura - 96,
        )

        # animação de linhas pontilhadas (re-iniciada a cada resize)
        self._linhas_animadas.parar()
        self._linhas_animadas = LinhasPontilhadasAnimadas(
            self._canvas, cor="#FFFFFF", quantidade=5,
        )
        self._linhas_animadas.iniciar()

    @staticmethod
    def _quadrado_inclinado(x: int, y: int, lado: int, angulo_rad: float):
        import math
        meio = lado // 2
        cos_a = math.cos(angulo_rad)
        sen_a = math.sin(angulo_rad)
        pts_locais = [(-meio, -meio), (meio, -meio), (meio, meio), (-meio, meio)]
        pts_globais = []
        for px, py in pts_locais:
            xr = px * cos_a - py * sen_a
            yr = px * sen_a + py * cos_a
            pts_globais.extend([x + xr, y + yr])
        return pts_globais

    @staticmethod
    def _misturar(cor1: str, cor2: str, t: float) -> str:
        c1 = tuple(int(cor1[i:i + 2], 16) for i in (1, 3, 5))
        c2 = tuple(int(cor2[i:i + 2], 16) for i in (1, 3, 5))
        m = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
        return "#%02X%02X%02X" % m
