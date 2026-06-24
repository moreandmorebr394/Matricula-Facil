import random
import math
import tkinter as tk
from componentes.cores import AZUL_PRIMARIO, AZUL_ESCURO, AZUL_CLARO, AMARELO_VIBRANTE, BRANCO

class FundoAnimado:
    """
    Controlador de fundo animado para Tkinter Canvas.
    Substitui fundos de imagem estática por um gradiente azul dinâmico e
    partículas flutuantes estilo plexus conectadas por linhas finas.
    """
    def __init__(self, canvas, num_particulas=22):
        self.canvas = canvas
        self.num_particulas = num_particulas
        self.particulas = []
        self.rodando = False
        
        # Monitora a destruição do canvas para evitar chamadas após fechamento
        self.canvas.bind("<Destroy>", self.parar)
        self.canvas.bind("<Configure>", self.ao_redimensionar, add="+")
        
        # Executa redimensionamento inicial caso o canvas já tenha dimensões
        self.ao_redimensionar()

    def ao_redimensionar(self, event=None):
        if not self.canvas.winfo_exists():
            return
        self.desenhar_gradiente()
        self.inicializar_particulas()

    def desenhar_gradiente(self):
        if not self.canvas.winfo_exists():
            return
        self.canvas.delete("gradiente")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 20 or h <= 20:
            w = self.canvas.winfo_reqwidth() or 800
            h = self.canvas.winfo_reqheight() or 600
            if w <= 20: w = 800
            if h <= 20: h = 600

        # Gradiente do AZUL_PRIMARIO (#3C507D) para AZUL_ESCURO (#112250)
        # Desenhado em passos de 3px para alta performance
        passo = 3
        for i in range(0, h, passo):
            ratio = i / h
            r = int(60 + ratio * (17 - 60))
            g = int(80 + ratio * (34 - 80))
            b = int(125 + ratio * (80 - 125))
            cor = f"#{r:02x}{g:02x}{b:02x}"
            line = self.canvas.create_line(0, i, w, i, fill=cor, width=passo, tags="gradiente")
            self.canvas.tag_lower(line)

    def inicializar_particulas(self):
        if not self.canvas.winfo_exists():
            return
        # Limpa partículas anteriores do canvas
        self.canvas.delete("particula")
        self.canvas.delete("conexao")
        self.particulas = []

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 20 or h <= 20:
            w = self.canvas.winfo_reqwidth() or 800
            h = self.canvas.winfo_reqheight() or 600
            if w <= 20: w = 800
            if h <= 20: h = 600

        cores = [AZUL_CLARO, AMARELO_VIBRANTE, BRANCO, "#A5B4FC"]

        for _ in range(self.num_particulas):
            x = random.randint(10, w - 10)
            y = random.randint(10, h - 10)
            vx = random.uniform(-0.8, 0.8)
            vy = random.uniform(-0.8, 0.8)
            
            # Evita velocidade zero
            if abs(vx) < 0.15: vx = 0.2 if vx >= 0 else -0.2
            if abs(vy) < 0.15: vy = 0.2 if vy >= 0 else -0.2
            
            r = random.uniform(3, 7)
            cor = random.choice(cores)
            estilo = random.choice(["cheio", "vazado", "estrela"])

            if estilo == "cheio":
                p_id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=cor, outline="", tags="particula")
            elif estilo == "vazado":
                p_id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="", outline=cor, width=1.2, tags="particula")
            else:
                p_id = self.canvas.create_text(x, y, text=random.choice(["✦", "★"]), fill=cor, font=("Century Gothic", int(r * 2)), tags="particula")

            self.canvas.tag_lower(p_id)
            self.canvas.tag_raise(p_id, "gradiente")

            self.particulas.append({
                "id": p_id,
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "r": r,
                "estilo": estilo
            })

        if not self.rodando:
            self.rodando = True
            self.atualizar()

    def atualizar(self):
        if not self.rodando or not self.canvas.winfo_exists():
            return

        try:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            if w <= 20 or h <= 20:
                self.canvas.after(33, self.atualizar)
                return

            self.canvas.delete("conexao")

            # Atualiza e move as partículas
            for p in self.particulas:
                p["x"] += p["vx"]
                p["y"] += p["vy"]

                # Limites de borda com bounce
                if p["x"] - p["r"] < 0 or p["x"] + p["r"] > w:
                    p["vx"] *= -1
                    p["x"] = max(p["r"], min(w - p["r"], p["x"]))
                if p["y"] - p["r"] < 0 or p["y"] + p["r"] > h:
                    p["vy"] *= -1
                    p["y"] = max(p["r"], min(h - p["r"], p["y"]))

                # Reposiciona o elemento
                r = p["r"]
                if p["estilo"] in ["cheio", "vazado"]:
                    self.canvas.coords(p["id"], p["x"]-r, p["y"]-r, p["x"]+r, p["y"]+r)
                else:
                    self.canvas.coords(p["id"], p["x"], p["y"])

            # Efeito Plexus / Desenha as conexões
            n = len(self.particulas)
            for i in range(n):
                p1 = self.particulas[i]
                for j in range(i + 1, n):
                    p2 = self.particulas[j]
                    dist = math.hypot(p1["x"] - p2["x"], p1["y"] - p2["y"])
                    if dist < 120:
                        ratio = (120 - dist) / 120
                        # Graduação de cor por distância para simular opacidade
                        if ratio > 0.6:
                            cor_linha = "#4C5F8A"
                        elif ratio > 0.35:
                            cor_linha = "#32446A"
                        else:
                            cor_linha = "#203154"
                        
                        line = self.canvas.create_line(p1["x"], p1["y"], p2["x"], p2["y"], fill=cor_linha, width=1, tags="conexao")
                        self.canvas.tag_lower(line)
                        self.canvas.tag_raise(line, "gradiente")

            self.canvas.after(33, self.atualizar)

        except tk.TclError:
            # Janela ou Canvas foi fechado/destruído
            self.rodando = False

    def parar(self, event=None):
        self.rodando = False


def criar_retangulo_arredondado(canvas, x1, y1, x2, y2, raio=16, **kwargs):
    """Desenha um retângulo com cantos arredondados no canvas usando um polígono de alta resolução."""
    points = []
    # Canto superior direito
    for i in range(10):
        angle = math.radians(-90 + i * 10)
        points.append(x2 - raio + raio * math.cos(angle))
        points.append(y1 + raio + raio * math.sin(angle))
    # Canto inferior direito
    for i in range(10):
        angle = math.radians(i * 10)
        points.append(x2 - raio + raio * math.cos(angle))
        points.append(y2 - raio + raio * math.sin(angle))
    # Canto inferior esquerdo
    for i in range(10):
        angle = math.radians(90 + i * 10)
        points.append(x1 + raio + raio * math.cos(angle))
        points.append(y2 - raio + raio * math.sin(angle))
    # Canto superior esquerdo
    for i in range(10):
        angle = math.radians(180 + i * 10)
        points.append(x1 + raio + raio * math.cos(angle))
        points.append(y1 + raio + raio * math.sin(angle))
        
    return canvas.create_polygon(points, **kwargs)

