import chess
import chess.svg
import os

# Výstupní soubor
OUTPUT_FILE = "01_chess_svg.svg"

# Vytvořit pozici
board = chess.Board()
board.push_san("e4")
board.push_san("e5")
board.push_san("Nf3")
board.push_san("Nc6")
board.push_san("Bb5")
board.push_san("a6")

# Základní styl, jemně pozměněný
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
