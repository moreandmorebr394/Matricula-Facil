"""
Tela de Carregamento (Splash Screen) do Sistema Facil.
Exibida antes da inicializacao da interface grafica principal.
"""
import tkinter as tk
import random
from componentes.cores import (
    AZUL_SIDEBAR, BRANCO, AMARELO_VIBRANTE, FONTE_TITULO, FONTE_TEXTO
)
from componentes.logo_sf import LogoSF

class TelaCarregamento(tk.Tk):
    """Splash screen com animacao circular e porcentagem."""

    def __init__(self):
        super().__init__()
        
        # Remove bordas da janela
        self.overrideredirect(True)
        self.configure(bg=AZUL_SIDEBAR)
        
        # Dimensoes da splash
        self.largura = 500
        self.altura = 360
        self._centralizar()
        
        self.progresso = 0
        self._construir()
        self._iniciar_carregamento()

    def _centralizar(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - self.largura) // 2
        y = (sh - self.altura) // 2
        self.geometry(f"{self.largura}x{self.altura}+{x}+{y}")

    def _construir(self):
        # Canvas principal para desenhos
        self.canvas = tk.Canvas(
            self, width=self.largura, height=self.altura,
            bg=AZUL_SIDEBAR, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Gradiente ou fundo decorativo leve
        self.canvas.create_oval(
            -50, -50, 150, 150,
            fill="#23355c", outline=""
        )
        self.canvas.create_oval(
            self.largura - 120, self.altura - 120, self.largura + 80, self.altura + 80,
            fill="#23355c", outline=""
        )

        # Nome do sistema
        self.canvas.create_text(
            self.largura // 2, 70,
            text="Sistema Fácil",
            font=(FONTE_TITULO, 24, "bold"),
            fill=BRANCO
        )
        self.canvas.create_text(
            self.largura // 2, 100,
            text="SISTEMA DE GESTÃO EDUCACIONAL",
            font=(FONTE_TEXTO, 8, "bold"),
            fill=AMARELO_VIBRANTE
        )

        # Circulo de progresso (Donut/Anel)
        self.cx, self.cy = self.largura // 2, 200
        self.raio = 55
        
        # Circulo de fundo cinza/azul claro
        self.canvas.create_oval(
            self.cx - self.raio, self.cy - self.raio,
            self.cx + self.raio, self.cy + self.raio,
            outline="#2d3f66", width=8
        )

        # Arco de progresso ativo
        self.arco_progresso = self.canvas.create_arc(
            self.cx - self.raio, self.cy - self.raio,
            self.cx + self.raio, self.cy + self.raio,
            start=90, extent=0, outline=AMARELO_VIBRANTE,
            width=8, style="arc"
        )

        # Texto da porcentagem no centro do circulo
        self.texto_porcentagem = self.canvas.create_text(
            self.cx, self.cy,
            text="0%", font=(FONTE_TITULO, 16, "bold"),
            fill=BRANCO
        )

        # Texto de status do carregamento
        self.texto_status = self.canvas.create_text(
            self.largura // 2, 290,
            text="Inicializando componentes...",
            font=(FONTE_TEXTO, 10, "italic"),
            fill="#9CA3AF"
        )

        # Versao no rodape
        self.canvas.create_text(
            self.largura // 2, 335,
            text="v4.0.0 • Versão Premium",
            font=(FONTE_TEXTO, 8),
            fill="#4B5563"
        )

    def _iniciar_carregamento(self):
        status_msgs = [
            (10, "Inicializando banco de dados..."),
            (30, "Conectando ao servidor MySQL..."),
            (50, "Carregando paleta de cores e fontes..."),
            (70, "Carregando layouts e componentes da interface..."),
            (85, "Verificando permissões de administrador..."),
            (95, "Finalizando carregamento..."),
            (100, "Tudo pronto!")
        ]

        def atualizar():
            if self.progresso < 100:
                # Incrementa progresso aleatoriamente para efeito realista
                self.progresso += random.randint(1, 3)
                if self.progresso > 100:
                    self.progresso = 100

                # Atualiza arco de progresso no canvas (extensao negativa para ir sentido horario)
                extensao = -int(360 * (self.progresso / 100.0))
                self.canvas.itemconfigure(self.arco_progresso, extent=extensao)

                # Atualiza texto de porcentagem
                self.canvas.itemconfigure(self.texto_porcentagem, text=f"{self.progresso}%")

                # Atualiza mensagem de status conforme progresso
                msg_atual = "Carregando..."
                for prog_limite, msg in status_msgs:
                    if self.progresso <= prog_limite:
                        msg_atual = msg
                        break
                self.canvas.itemconfigure(self.texto_status, text=msg_atual)

                # Agenda proximo passo com tempo aleatorio para fluidez
                tempo_espera = random.randint(20, 45)
                self.after(tempo_espera, atualizar)
            else:
                # Progresso concluido, espera um momento para a transicao e encerra
                self.after(250, self.destroy)

        # Inicia o loop de atualizacao
        self.after(100, atualizar)
