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

# Základní styl s bílými poli
svg = chess.svg.board(
    board,
    size=400,
    coordinates=True,
    colors={
        "square light": "#ffffff",
        "square dark": "#ffffff",
        "margin": "#ffffff",
        "coord": "#ff00ff"}
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
  text {
    font-family: 'Courier New', Courier, monospace !important;
    font-weight: bold;
    letter-spacing: 0.05em;
  }
</style>
'''

# Vložit pattern a styly za první <defs> tag
svg = svg.replace('<defs>', '<defs>' + hatching_pattern + typewriter_style, 1)

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