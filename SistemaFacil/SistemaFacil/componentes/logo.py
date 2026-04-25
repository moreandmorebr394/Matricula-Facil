# ============================================================
# componentes/logo.py — Logo SF desenhada em Canvas
# ============================================================
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os


def criar_logo_imagem(tamanho=60):
    """Cria a logo SF como uma imagem PIL com chapéu de formatura."""
    img = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    centro = tamanho // 2
    raio = tamanho // 2 - 2

    # Círculo externo azul escuro
    draw.ellipse(
        [centro - raio, centro - raio, centro + raio, centro + raio],
        outline="#112250", width=max(2, tamanho // 20)
    )
    # Círculo dourado
    raio_int = raio - max(3, tamanho // 15)
    draw.ellipse(
        [centro - raio_int, centro - raio_int, centro + raio_int, centro + raio_int],
        outline="#E0C58F", width=max(2, tamanho // 25)
    )
    # Fundo branco interno
    raio_bg = raio_int - max(2, tamanho // 20)
    draw.ellipse(
        [centro - raio_bg, centro - raio_bg, centro + raio_bg, centro + raio_bg],
        fill="#FFFFFF"
    )

    # Letras "SF"
    try:
        tamanho_fonte = int(tamanho * 0.38)
        font = ImageFont.truetype("arial.ttf", tamanho_fonte)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(tamanho * 0.38))
        except (OSError, IOError):
            font = ImageFont.load_default()

    # S em dourado
    s_x = centro - int(tamanho * 0.18)
    s_y = centro - int(tamanho * 0.12)
    draw.text((s_x, s_y), "S", fill="#E0C58F", font=font)

    # F em azul escuro
    f_x = centro + int(tamanho * 0.02)
    f_y = centro - int(tamanho * 0.15)
    draw.text((f_x, f_y), "F", fill="#112250", font=font)

    # Chapéu de formatura (simplificado)
    chap_x = centro + int(tamanho * 0.05)
    chap_y = centro - int(tamanho * 0.22)
    chap_w = int(tamanho * 0.22)
    chap_h = int(tamanho * 0.08)

    # Base do chapéu (losango)
    pontos_chapeu = [
        chap_x, chap_y,
        chap_x + chap_w, chap_y - chap_h // 2,
        chap_x + chap_w * 2, chap_y,
        chap_x + chap_w, chap_y + chap_h // 2,
    ]
    draw.polygon(pontos_chapeu, fill="#112250")

    # Borla
    borla_x = chap_x + chap_w + int(tamanho * 0.1)
    draw.line(
        [(borla_x, chap_y), (borla_x + int(tamanho * 0.02), chap_y + int(tamanho * 0.12))],
        fill="#E0C58F", width=max(1, tamanho // 30)
    )
    # Bolinha da borla
    b_raio = max(2, tamanho // 25)
    bx = borla_x + int(tamanho * 0.02)
    by = chap_y + int(tamanho * 0.12)
    draw.ellipse([bx - b_raio, by - b_raio, bx + b_raio, by + b_raio], fill="#E0C58F")

    return img


def carregar_logo(caminho_assets, tamanho=60):
    """
    Tenta carregar a logo do arquivo; se não existir, gera uma.
    Retorna um ImageTk.PhotoImage.
    """
    caminho_logo = os.path.join(caminho_assets, "logo_sf.png")
    try:
        if os.path.exists(caminho_logo):
            img = Image.open(caminho_logo).convert("RGBA")
            img = img.resize((tamanho, tamanho), Image.LANCZOS)
        else:
            img = criar_logo_imagem(tamanho)
    except Exception:
        img = criar_logo_imagem(tamanho)

    return ImageTk.PhotoImage(img)
