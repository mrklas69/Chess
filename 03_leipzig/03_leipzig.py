import chess
import chess.svg
import re
import os
import base64

# Výstupní soubor
OUTPUT_FILE = "03_leipzig.svg"

# Vytvořit pozici
board = chess.Board()
board.push_san("e4")
board.push_san("e5")
board.push_san("Nf3")
board.push_san("Nc6")
board.push_san("Bb5")
board.push_san("a6")

# Funkce pro načtení PNG obrázku a převod na data URI
def load_piece_image(piece_path):
    with open(piece_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    return f'data:image/png;base64,{image_data}'

# Načíst všechny figurky z adresáře leipzig
piece_dir = './03_leipzig/leipzig'
piece_images = {}
piece_mapping = {
    'P': 'wP.png', 'N': 'wN.png', 'B': 'wB.png', 'R': 'wR.png', 'Q': 'wQ.png', 'K': 'wK.png',
    'p': 'bP.png', 'n': 'bN.png', 'b': 'bB.png', 'r': 'bR.png', 'q': 'bQ.png', 'k': 'bK.png'
}

for piece_symbol, filename in piece_mapping.items():
    piece_path = os.path.join(piece_dir, filename)
    if os.path.exists(piece_path):
        piece_images[piece_symbol] = load_piece_image(piece_path)

# Základní styl s bílými poli (zapneme souřadnice, pak je nahradíme šrafováním)
svg = chess.svg.board(
    board,
    size=400,
    coordinates=True,
    colors={
        "square light": "#ffffff",
        "square dark": "#E1E1E1",
        "margin": "#ffffff",
        "coord": "#000000"}
)

# Nahradit vektorové figurky PNG obrázky
def replace_pieces_with_images(svg_content, piece_images):
    # Odstranit všechny <use> elementy, které odkazují na figurky
    svg_content = re.sub(r'<use[^>]*href="#[^"]*"[^>]*transform="translate\([^)]*\)"[^/]*/>', '', svg_content)
    svg_content = re.sub(r'<use[^>]*transform="translate\([^)]*\)"[^>]*href="#[^"]*"[^/]*/>', '', svg_content)

    # Přidat nové <image> elementy pro figurky před </svg>
    pieces_svg = ''
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            file_idx = chess.square_file(square)
            rank_idx = chess.square_rank(square)
            x = 15 + file_idx * 45
            y = 15 + (7 - rank_idx) * 45
            piece_symbol = piece.symbol()
            padding = 3
            if piece_symbol in piece_images:
                pieces_svg += f'<image x="{x + padding}" y="{y + padding}" width="{45 - 2*padding}" height="{45 - 2*padding}" href="{piece_images[piece_symbol]}" />\n'

    svg_content = svg_content.replace('</svg>', pieces_svg + '</svg>')
    return svg_content

svg = replace_pieces_with_images(svg, piece_images)

# Uložit
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(svg)

# Otevřít SVG soubor (ve výchozím programu nebo VS Code, pokud je asociován)
os.startfile(OUTPUT_FILE)
