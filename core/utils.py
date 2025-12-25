from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import os
from django.conf import settings

def carregar_fonte(caminho, tamanho):
    try:
        return ImageFont.truetype(caminho, tamanho)
    except OSError:
        return ImageFont.load_default()

def quebrar_texto_por_largura(texto, fonte, largura_max, draw):
    linhas = []
    palavras = texto.split()
    linha_atual = ""

    for palavra in palavras:
        teste = f"{linha_atual} {palavra}".strip()
        largura_teste = draw.textlength(teste, font=fonte)

        if largura_teste <= largura_max:
            linha_atual = teste
        else:
            linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas


def gerar_imagem_post(post):
    largura, altura = 1200, 830

    # ===============================
    # 🔹 FUNDO
    # ===============================
    if post.imagem:
        fundo = Image.open(post.imagem.path).convert("RGB")
        fundo = fundo.resize((largura, altura), Image.LANCZOS)
        fundo = fundo.filter(ImageFilter.GaussianBlur(2))
    else:
        fundo = Image.new("RGB", (largura, altura), "#6C87FF")

    # ===============================
    # 🔹 OVERLAY GRADIENTE
    # ===============================
    overlay = Image.new("RGBA", (largura, altura))
    draw_overlay = ImageDraw.Draw(overlay)

    for y in range(altura):
        alpha = int(200 * (y / altura))
        draw_overlay.line(
            [(0, y), (largura, y)],
            fill=(0, 0, 0, alpha)
        )

    fundo = Image.alpha_composite(fundo.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(fundo)

    # ===============================
    # 🔹 FONTES (DOBRO DO TAMANHO, inclusive fallback)
    # ===============================
    fonte_path = os.path.join(
        settings.BASE_DIR, "static", "fonts", "Roboto-Bold.ttf"
    )

    try:
        # Fonte personalizada
        fonte_texto = ImageFont.truetype(fonte_path, 35)  # texto do post
        fonte_autor = ImageFont.truetype(fonte_path, 30)   # autor
    except OSError:
        # Fallback: aumentar tamanho manualmente
        fonte_texto = ImageFont.load_default()
        fonte_autor = ImageFont.load_default()

        # PIL não permite diretamente aumentar load_default, então podemos escalar:
        # cria uma “imagem temporária” para calcular o tamanho
        # ou usar ImageFont.truetype com fonte genérica se load_default falhar
        try:
            # Fonte genérica Arial como fallback grande
            fonte_texto = ImageFont.truetype("arial.ttf", 35)
            fonte_autor = ImageFont.truetype("arial.ttf", 30)
        except OSError:
            # Se nem Arial existir, mantém default, mas desenhando maior via escala
            pass


    # ===============================
    # 🔹 TEXTO (TOPO + LIMITES)
    # ===============================
    texto = post.conteudo.strip()[:220]  # <- limite atual: 460 caracteres

    padding_topo = 140
    padding_base = 260
    padding_lateral = 100

    largura_texto_max = largura - (padding_lateral * 2)

    linhas = quebrar_texto_por_largura(
        texto,
        fonte_texto,
        largura_texto_max,
        draw
    )

    altura_linha = 42
    altura_max_texto = altura - padding_topo - padding_base
    max_linhas = altura_max_texto // altura_linha
    linhas = linhas[:max_linhas]

    y = padding_topo

    for linha in linhas:
        x = padding_lateral  # NÃO centraliza mais
        draw.text((x, y), linha, font=fonte_texto, fill="white")
        y += altura_linha




    # ===============================
    # 🔹 AUTOR (TEXTO)
    # ===============================
    autor_texto = f"— {post.autor.username}"
    largura_autor = draw.textlength(autor_texto, font=fonte_autor)

    draw.text(
        ((largura - largura_autor) // 2, y + 20),
        autor_texto,
        font=fonte_autor,
        fill="#cbd5f5"
    )
    
    # ===============================
    # 🔹 AVATAR DO AUTOR (CIRCULAR)
    # ===============================
    avatar_path = None

    # Busca a imagem de perfil ou avatar
    if hasattr(post.autor, "perfil") and post.autor.perfil.foto_perfil:
        avatar_path = post.autor.perfil.foto_perfil.path
    elif hasattr(post.autor, "avatar") and post.autor.avatar:
        avatar_path = post.autor.avatar.path

    if avatar_path and os.path.exists(avatar_path):
        avatar = Image.open(avatar_path).convert("RGB")
        avatar = avatar.resize((96, 96), Image.LANCZOS)

        # Cria máscara circular para o avatar
        mask = Image.new("L", (96, 96), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 96, 96), fill=255)

        # 🔹 Define espaço entre o final do texto e o avatar
        espaco_texto_avatar = 60  # ajuste esse valor para mais ou menos respiro
        y_avatar = y + espaco_texto_avatar

        # Cola o avatar na imagem centralizado horizontalmente
        fundo.paste(
            avatar,
            ((largura - 96) // 2, y_avatar),
            mask
        )

    # ===============================
    # 🔹 LOGO DO SITE
    # ===============================
    logo_path = os.path.join(
        settings.BASE_DIR, "static", "images", "logo.png"
    )

    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((140, 140), Image.LANCZOS)
        fundo.paste(
            logo,
            (largura - logo.width - 40, 40),
            logo
        )

    # ===============================
    # 🔹 SALVAR
    # ===============================
    pasta_autor = os.path.join(
        settings.MEDIA_ROOT,
        "posts_share",
        post.autor.username
    )
    os.makedirs(pasta_autor, exist_ok=True)

    nome_arquivo = f"post_{post.id}.jpg"
    caminho = os.path.join(pasta_autor, nome_arquivo)

    fundo.convert("RGB").save(caminho, "JPEG", quality=93)

    return f"posts_share/{post.autor.username}/{nome_arquivo}"
