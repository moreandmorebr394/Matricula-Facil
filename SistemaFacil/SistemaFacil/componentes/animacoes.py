# ============================================================
# componentes/animacoes.py — Animações e efeitos visuais
# ============================================================
import tkinter as tk
import math
import random


class AnimacaoCursor:
    """Rastro pontilhado que segue o cursor do mouse."""

    def __init__(self, canvas, cor="#E0C58F", num_pontos=12, raio_max=4):
        self.canvas = canvas
        self.cor = cor
        self.num_pontos = num_pontos
        self.raio_max = raio_max
        self.pontos = []
        self.ids_pontos = []
        self.ativo = True

        for i in range(num_pontos):
            oid = canvas.create_oval(0, 0, 0, 0, fill=cor, outline="", state="hidden")
            self.ids_pontos.append(oid)
            self.pontos.append({"x": 0, "y": 0, "vida": 0})

        self.canvas.bind("<Motion>", self._ao_mover)
        self._animar()

    def _ao_mover(self, evento):
        # Adiciona um ponto novo na posição do cursor
        for i in range(self.num_pontos - 1, 0, -1):
            self.pontos[i] = self.pontos[i - 1].copy()
        self.pontos[0] = {"x": evento.x, "y": evento.y, "vida": 1.0}

    def _animar(self):
        if not self.ativo:
            return
        for i, ponto in enumerate(self.pontos):
            if ponto["vida"] > 0:
                ponto["vida"] -= 0.06
                raio = self.raio_max * ponto["vida"] * (1 - i / self.num_pontos)
                raio = max(0.5, raio)
                x, y = ponto["x"], ponto["y"]
                self.canvas.coords(
                    self.ids_pontos[i],
                    x - raio, y - raio, x + raio, y + raio,
                )
                # Opacidade simulada com cor
                intensidade = int(255 * ponto["vida"])
                cor = f"#{intensidade:02x}{int(intensidade * 0.78):02x}{int(intensidade * 0.56):02x}"
                try:
                    self.canvas.itemconfig(self.ids_pontos[i], fill=cor, state="normal")
                except tk.TclError:
                    pass
            else:
                self.canvas.itemconfig(self.ids_pontos[i], state="hidden")
        self.canvas.after(30, self._animar)

    def parar(self):
        self.ativo = False


class FormasGeometricas:
    """Formas geométricas flutuantes animadas no painel visual."""

    def __init__(self, canvas, largura, altura):
        self.canvas = canvas
        self.largura = largura
        self.altura = altura
        self.formas = []
        self.ativo = True
        self._criar_formas()
        self._animar()

    def _criar_formas(self):
        cores = ["#4A6199", "#E0C58F", "#5B75B0", "#D4B06A", "#6883BD"]
        for _ in range(8):
            tamanho = random.randint(20, 55)
            x = random.randint(0, self.largura)
            y = random.randint(0, self.altura)
            cor = random.choice(cores)
            vel_x = random.uniform(-0.3, 0.3)
            vel_y = random.uniform(-0.3, 0.3)
            rotacao = random.uniform(0, 360)
            vel_rot = random.uniform(-0.5, 0.5)
            opacidade = random.uniform(0.3, 0.7)

            # Desenhar quadrado rotacionado
            oid = self._desenhar_quadrado(x, y, tamanho, rotacao, cor, opacidade)
            self.formas.append({
                "id": oid, "x": x, "y": y, "tamanho": tamanho,
                "vel_x": vel_x, "vel_y": vel_y, "rotacao": rotacao,
                "vel_rot": vel_rot, "cor": cor, "opacidade": opacidade,
            })

    def _desenhar_quadrado(self, cx, cy, tamanho, angulo, cor, opacidade):
        """Desenha um quadrado rotacionado como polígono."""
        rad = math.radians(angulo)
        pontos = []
        for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            px = dx * tamanho / 2
            py = dy * tamanho / 2
            rx = px * math.cos(rad) - py * math.sin(rad)
            ry = px * math.sin(rad) + py * math.cos(rad)
            pontos.extend([cx + rx, cy + ry])

        # Simular opacidade misturando cor com o fundo (#3C507D)
        r_bg, g_bg, b_bg = 0x3C, 0x50, 0x7D
        r_fg = int(cor[1:3], 16)
        g_fg = int(cor[3:5], 16)
        b_fg = int(cor[5:7], 16)
        r = int(r_bg * (1 - opacidade) + r_fg * opacidade)
        g = int(g_bg * (1 - opacidade) + g_fg * opacidade)
        b = int(b_bg * (1 - opacidade) + b_fg * opacidade)
        cor_mix = f"#{r:02x}{g:02x}{b:02x}"

        return self.canvas.create_polygon(pontos, fill=cor_mix, outline="", smooth=False)

    def _animar(self):
        if not self.ativo:
            return
        for forma in self.formas:
            forma["x"] += forma["vel_x"]
            forma["y"] += forma["vel_y"]
            forma["rotacao"] += forma["vel_rot"]

            # Rebater nas bordas
            if forma["x"] < -30 or forma["x"] > self.largura + 30:
                forma["vel_x"] *= -1
            if forma["y"] < -30 or forma["y"] > self.altura + 30:
                forma["vel_y"] *= -1

            # Redesenhar
            self.canvas.delete(forma["id"])
            forma["id"] = self._desenhar_quadrado(
                forma["x"], forma["y"], forma["tamanho"],
                forma["rotacao"], forma["cor"], forma["opacidade"]
            )

        self.canvas.after(50, self._animar)

    def parar(self):
        self.ativo = False


class LinhasPontilhadas:
    """Linhas pontilhadas decorativas animadas."""

    def __init__(self, canvas, largura, altura):
        self.canvas = canvas
        self.largura = largura
        self.altura = altura
        self.linhas = []
        self.offset = 0
        self.ativo = True
        self._criar_linhas()
        self._animar()

    def _criar_linhas(self):
        # Linhas diagonais sutis
        posicoes = [
            (0, self.altura * 0.3, self.largura * 0.4, 0),
            (self.largura * 0.6, self.altura, self.largura, self.altura * 0.5),
            (0, self.altura * 0.8, self.largura * 0.3, self.altura),
        ]
        for x1, y1, x2, y2 in posicoes:
            oid = self.canvas.create_line(
                x1, y1, x2, y2,
                fill="#4A6199", dash=(6, 8), width=1,
                stipple=""
            )
            self.linhas.append(oid)

    def _animar(self):
        if not self.ativo:
            return
        self.offset = (self.offset + 1) % 14
        for oid in self.linhas:
            try:
                self.canvas.itemconfig(oid, dash=(6, 8), dashoffset=self.offset)
            except tk.TclError:
                pass
        self.canvas.after(80, self._animar)

    def parar(self):
        self.ativo = False
