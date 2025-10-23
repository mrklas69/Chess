import chess
import chess.svg
import re

# Vytvořit pozici
board = chess.Board()
board.push_san("e4")
board.push_san("e5")
board.push_san("Nf3")
board.push_san("Nc6")
board.push_san("Bb5")
board.push_san("a6")

# Základní styl s bílými poli (zapneme souřadnice, pak je nahradíme)
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

# Šrafování: souvislé diagonální čáry
# Pro plynulé navázání přidáme více čar do patternu
hatching_pattern = '''
<pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="3.46" height="3.46">
  <rect width="3.46" height="3.46" fill="#ffffff"/>
  <path d="M-1,1 l2,-2 M0,3.46 l3.46,-3.46 M2.46,4.46 l2,-2" style="stroke:#000000; stroke-width:0.5" />
</pattern>
'''

# CSS styly pro font souřadnic - typewriter styl
typewriter_style = '''
<style>
  .coordinates {
    font-family: 'Source Code Pro', Courier, monospace;
    font-weight: normal;
    font-size: 16px;
    fill: #000000;
  }
</style>
'''

# Vložit pattern a styly za první <defs> tag
svg = svg.replace('<defs>', '<defs>' + hatching_pattern + typewriter_style, 1)

# Odstranit původní vektorové souřadnice (jsou to <g> elementy s fill a stroke)
# Odstraníme všechny <g transform="translate(...)" fill="#000000" stroke="#000000">
svg = re.sub(r'<g transform="translate\([^"]+\)" fill="#[0-9a-f]+" stroke="#[0-9a-f]+"><path d="[^"]+"\s*/></g>', '', svg)

# Přidat vlastní text souřadnice s typewriter fontem
# S coordinates=True má SVG viewBox="0 0 390 390" a šachovnice začíná na 15,15
# Písmena a-h na dolním okraji (y pozice pod šachovnicí)
files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
coordinates_svg = ''
for i, letter in enumerate(files):
    x = 15 + i * 45 + 22.5  # margin + střed pole
    y = 386 # pod šachovnicí, ale viditelně
    coordinates_svg += f'<text x="{x}" y="{y}" text-anchor="middle" class="coordinates">{letter}</text>\n'

# Čísla 1-8 na levém okraji (x pozice vlevo od šachovnice)
for i in range(8):
    number = str(i + 1)
    x = 7  # více vlevo od šachovnice
    y = 15 + 360 - i * 45 - 22.5 + 5  # margin + výška - offset + vertikální zarovnání
    coordinates_svg += f'<text x="{x}" y="{y}" text-anchor="middle" class="coordinates">{number}</text>\n'

# Vložit souřadnice před konec SVG
svg = svg.replace('</svg>', coordinates_svg + '</svg>')

# Nahradit fill u všech tmavých polí
svg = re.sub(
    r'class="square dark([^"]*)"([^>]*)fill="#ffffff"',
    r'class="square dark\1"\2fill="url(#diagonalHatch)"',
    svg
)

# Uložit
with open("srafovani.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("SVG s LaTeX-ovým šrafováním vytvořeno!")