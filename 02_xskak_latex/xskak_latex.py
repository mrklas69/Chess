import chess
import chess.svg
import re
import os
import base64

# Výstupní soubor
OUTPUT_FILE = "xskak_latex.svg"

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

# Načíst všechny figurky z adresáře uscf
piece_dir = './02_xskak_latex/uscf'
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
        "square dark": "#ffffff",
        "margin": "#ffffff",
        "coord": "#000000"}
)

# Šrafování: 13 čar na políčko (jako v LaTeXu xskak)
pattern_size = 6.78
hatching_pattern = f'''
<pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="{pattern_size}" height="{pattern_size}">
  <rect width="{pattern_size}" height="{pattern_size}" fill="#ffffff"/>
  <path d="M-1,1 l2,-2 M0,{pattern_size} l{pattern_size},-{pattern_size} M{pattern_size-1},{pattern_size+1} l2,-2" style="stroke:#727FA2; stroke-width:1" />
</pattern>
'''

# CSS styly pro font souřadnic - typewriter styl
typewriter_style = '''
<style>
  .coordinates {
    font-family: 'Source Code Pro', Courier, monospace;
    font-weight: normal;
    font-size: 18px;
    fill: #000000;
  }
</style>
'''

# Vložit pattern a styly za první <defs> tag
svg = svg.replace('<defs>', '<defs>' + hatching_pattern + typewriter_style, 1)

# Přidat bílé pozadí hned za <defs>...</defs>
white_background = '<rect x="0" y="0" width="390" height="398" fill="#ffffff"/>\n'
svg = svg.replace('</defs>', '</defs>' + white_background, 1)

# Zvětšit výšku SVG o 8px, aby se zobrazily všechny souřadnice
svg = re.sub(r'height="400"', r'height="408"', svg)
# Upravit viewBox, aby odpovídal nové výšce
svg = re.sub(r'viewBox="0 0 390 390"', r'viewBox="0 0 390 398"', svg)

# Odstraníme všechny <g transform="translate(...)" fill="#000000" stroke="#000000">
svg = re.sub(r'<g transform="translate\([^"]+\)" fill="#[0-9a-f]+" stroke="#[0-9a-f]+"><path d="[^"]+"\s*/></g>', '', svg)

# Písmena a-h na dolním okraji (y pozice pod šachovnicí)
files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
coordinates_svg = ''
for i, letter in enumerate(files):
    x = 15 + i * 45 + 22.5  # margin + střed pole
    y = 391
    coordinates_svg += f'<text x="{x}" y="{y}" text-anchor="middle" class="coordinates">{letter}</text>\n'

# Čísla 1-8 na levém okraji (x pozice vlevo od šachovnice)
for i in range(8):
    number = str(i + 1)
    x = 7
    y = 15 + 360 - i * 45 - 22.5 + 5  # margin + výška - offset + vertikální zarovnání
    coordinates_svg += f'<text x="{x}" y="{y}" text-anchor="middle" class="coordinates">{number}</text>\n'

# Přidat černý rámeček kolem šachovnice (2px silný)
border_svg = '<rect x="15" y="15" width="360" height="360" fill="none" stroke="#000000" stroke-width="1"/>\n'

# Vložit rámeček a souřadnice před konec SVG
svg = svg.replace('</svg>', border_svg + coordinates_svg + '</svg>')

# Nahradit fill u všech tmavých polí
svg = re.sub(
    r'class="square dark([^"]*)"([^>]*)fill="#ffffff"',
    r'class="square dark\1"\2fill="url(#diagonalHatch)"',
    svg
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
