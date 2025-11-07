import chess
import chess.svg
import os

# Výstupní soubor
OUTPUT_FILE = "chess_svg.svg"

# Vytvořit pozici základního postavení
board = chess.Board()

# Výstup do konzole
print(board)

# Výstup do obrázku
svg = chess.svg.board(
    board,
    size=400,
    coordinates=True,
    colors={
        "square light": "#C3C6BE",
        "square dark": "#727FA2",
        "margin": "#727FA2",
        "coord": "#000000"}
)

# Uložit
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(svg)

# Otevřít SVG soubor (ve výchozím programu nebo VS Code, pokud je asociován)
os.startfile(OUTPUT_FILE)
