"""
Widget do logo SF.

Carrega o PNG do logo (com fundo transparente) processado a partir
do recurso e o exibe em um Label sobre qualquer cor de fundo.
"""
import os
import tkinter as tk

try:
    from PIL import Image, ImageTk
    _TEM_PIL = True
except ImportError:
    _TEM_PIL = False
    Image = None
    ImageTk = None


_DIRETORIO_RECURSOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recursos",
)


def caminho_recurso(nome: str) -> str:
    return os.path.join(_DIRETORIO_RECURSOS, nome)


class LogoSF(tk.Label):
    """Exibe o logo 'SF' redimensionado para o tamanho desejado.

    Mantém referência interna da PhotoImage para evitar coleta pelo GC.
    """

    def __init__(self, mestre, tamanho: int = 96, cor_fundo: str = "#FFFFFF", **kwargs):
        super().__init__(mestre, bg=cor_fundo, bd=0, highlightthickness=0, **kwargs)
        self._tamanho = tamanho
        self._cor_fundo = cor_fundo
        self._foto = None
        self._carregar()

    def _carregar(self):
        if not _TEM_PIL:
            self.configure(text="SF", font=("Arial", 24, "bold"), fg="#3C507D")
            return

        # Tenta buscar o tamanho mais próximo já gerado para qualidade
        for predefinido in ("logo_sf_160.png", "logo_sf_96.png", "logo_sf_48.png", "logo_sf.png"):
            caminho = caminho_recurso(predefinido)
            if os.path.exists(caminho):
                arquivo = caminho
                break
        else:
            self.configure(text="SF", font=("Arial", 24, "bold"), fg="#3C507D")
            return

        try:
            imagem = Image.open(arquivo).convert("RGBA")
            imagem = imagem.resize((self._tamanho, self._tamanho), Image.LANCZOS)

            # Compõe sobre o cor_fundo informado para evitar artefatos no Tk
            fundo = Image.new("RGBA", imagem.size, self._cor_fundo)
            composta = Image.alpha_composite(fundo, imagem).convert("RGB")
            self._foto = ImageTk.PhotoImage(composta)
            self.configure(image=self._foto, bg=self._cor_fundo)
        except Exception as exc:
            print("[LogoSF] erro ao carregar logo:", exc)
            self.configure(text="SF", font=("Arial", 24, "bold"), fg="#3C507D")
