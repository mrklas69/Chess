"""
Generování šachovnic v různých barevných tématech.
Používá pouze python-chess (SVG výstup místo PNG).
"""

import chess
import chess.svg
import os

# Sicilská obrana po 1.e4 c5
SICILIAN_FEN = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"

# Barevná témata: (světlé pole, tmavé pole)
THEMES = {
    "alpha":     ("#f0d9b5", "#b58863"),
    "wikipedia": ("#FFCE9E", "#D18B47"),
    "uscf":      ("#C3C6BE", "#727FA2"),
    "wisteria":  ("#F5F0FF", "#967BB6"),
    "sakura":    ("#FFFFFF", "#FFCAD8"),
}

board = chess.Board(SICILIAN_FEN)

# Uložíme si název prvního souboru, ať na konci nemusíme duplikovat znalost
# o tom, jaký klíč je první v THEMES (dict v Pythonu 3.7+ drží pořadí vložení).
first_output = None

for theme_name, (light, dark) in THEMES.items():
    # Vygenerování SVG s python-chess
    svg = chess.svg.board(
        board,
        size=400,
        coordinates=True,
        colors={
            "square light": light,
            "square dark": dark,
            "margin": light,
            "coord": "#000000",
        },
    )

    output_file = f"sicilian_defense_{theme_name}.svg"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Vytvořen: {output_file}")

    if first_output is None:
        first_output = output_file

# Otevřít první vygenerovaný soubor jako ukázku
os.startfile(os.path.abspath(first_output))
