"""
Logo SF carregado da imagem logo_sf.png - transparente e profissional.
"""
import tkinter as tk
import os
from PIL import Image, ImageTk

class LogoSF(tk.Canvas):
    """
    Logo SF (Sistema Facil) - exibe a imagem logo_sf.png redimensionada.
    """

    def __init__(self, master, tamanho=80, cor_fundo="#FFFFFF", **kwargs):
        super().__init__(
            master,
            width=tamanho,
            height=tamanho,
            bg=cor_fundo,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.tamanho = tamanho
        self.cor_fundo = cor_fundo
        self._exibir_imagem()

    def _exibir_imagem(self):
        try:
            caminho_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo_sf.png")
            if os.path.exists(caminho_logo):
                img = Image.open(caminho_logo)
                # Redimensiona para o tamanho solicitado
                img = img.resize((self.tamanho, self.tamanho), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._photo_ref = photo  # Guarda referencia para evitar Garbage Collection
                self.create_image(self.tamanho // 2, self.tamanho // 2, image=photo, anchor="center")
            else:
                # Fallback caso a imagem nao seja encontrada
                self.create_oval(2, 2, self.tamanho - 2, self.tamanho - 2, fill="#E5E7EB", outline="")
                self.create_text(self.tamanho // 2, self.tamanho // 2, text="SF", fill="#1F2937", font=("Comic Sans MS", int(self.tamanho * 0.4), "bold"))
        except Exception as e:
            print("Erro ao exibir imagem do logo:", e)


def definir_icone_janela(janela):
    """Define o icone da janela usando a imagem logo_sf.png."""
    try:
        caminho_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo_sf.png")
        if os.path.exists(caminho_logo):
            img = Image.open(caminho_logo)
            photo = ImageTk.PhotoImage(img)
            # Mantem referencia na janela para evitar Garbage Collection
            janela._icone_img = photo
            janela.iconphoto(False, photo)
    except Exception as e:
        print("Erro ao definir icone da janela:", e)
