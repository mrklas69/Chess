"""
Hra proti Stockfish enginu — CLI vstup + render do HTML s auto-refresh.

Spouštět z kořene repozitáře:
    python 06_play/play.py

Vyžaduje:
- python-chess (pip install python-chess)
- Stockfish v PATH (stáhni z https://stockfishchess.org/download/)
"""
import os
import sys
from pathlib import Path

import chess
import chess.engine
import chess.pgn

# Renderers.py je ve stejném adresáři — přidám ho do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from renderers import RENDERERS, THEMES_04, render_04  # noqa: E402

# Výstupní HTML soubor — drží se v 06_play/ ať se neválí v root repa
OUTPUT_FILE = Path("06_play/game.html")

# Auto-refresh prohlížeče — meta-refresh tag se obnovuje každé N sekund.
# 2s je kompromis: krátké zpoždění odezvy, ne moc blikání.
META_REFRESH_SECONDS = 2

# Limit Stockfish přemýšlení (sekundy na tah)
ENGINE_THINK_TIME = 0.5


# === HTML šablona =============================================================

def make_html_page(fragment: str, title: str, refresh: bool) -> str:
    """Zabalí render fragment do plné HTML stránky.
    refresh=False při konci hry, ať prohlížeč nepoletí dokola na statické pozici.
    """
    # f-string nemá podmíněné větve, takže refresh_tag spočítám zvlášť
    refresh_tag = (
        f'<meta http-equiv="refresh" content="{META_REFRESH_SECONDS}">'
        if refresh else ''
    )
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    {refresh_tag}
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .board-container {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="board-container">{fragment}</div>
</body>
</html>'''


def write_render(board: chess.Board, render_fn, title: str, refresh: bool) -> None:
    """Vygeneruje render aktuální pozice a zapíše do HTML souboru."""
    fragment = render_fn(board)
    page = make_html_page(fragment, title, refresh)
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(page, encoding="utf-8")


# === PGN tabulka ==============================================================

def pgn_table(board: chess.Board) -> str:
    """Vrátí PGN řetězec tahů z move_stacku, formát: '1. e4 e5  2. Nf3 Nc6 ...'.
    Bez hlaviček, bez komentářů — jen samotná notace.
    """
    if not board.move_stack:
        return "(zatím žádné tahy)"
    game = chess.pgn.Game.from_board(board)
    # StringExporter: headers=False vyloučí PGN hlavičky [Event "..."] atd.
    exporter = chess.pgn.StringExporter(
        headers=False, comments=False, variations=False
    )
    # PGN končí značkou výsledku ('*' = nedokončeno, '1-0' atd.) — pro interaktivní
    # view ji ořízneme, jinak po každém tahu vidíš rušivou '*' na konci
    text = game.accept(exporter).strip()
    return text.rstrip(' *').rstrip()


# === Parsování uživatelských tahů =============================================

def parse_move(board: chess.Board, move_str: str) -> chess.Move:
    """Pokusí se parsovat tah jako SAN ('Nf3'), fallback UCI ('g1f3').
    Vyhodí ValueError s popisným textem při neplatném tahu.
    """
    move_str = move_str.strip()
    # Nejdřív SAN — to je přirozenější pro lidi (Nf3, O-O, exd5)
    try:
        return board.parse_san(move_str)
    except (ValueError, chess.IllegalMoveError,
            chess.InvalidMoveError, chess.AmbiguousMoveError):
        pass
    # Fallback UCI (g1f3, e7e8q pro proměnu)
    try:
        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            return move
    except (ValueError, chess.InvalidMoveError):
        pass
    raise ValueError(f"Tah '{move_str}' není platný (zkus SAN jako 'Nf3' nebo UCI jako 'g1f3')")


# === Interaktivní setup =======================================================

def choose_renderer() -> int:
    """Menu volby stylu šachovnice. Vrátí číslo 1-5."""
    print("\nVyber styl šachovnice:")
    for key, (label, _) in RENDERERS.items():
        print(f"  {key}. {label}")
    while True:
        choice = input("Volba [1-5]: ").strip()
        if choice in {'1', '2', '3', '4', '5'}:
            return int(choice)
        print("Zadej číslo 1-5.")


def choose_theme_04() -> str:
    """Pokud zvolen styl 4, dotaž se na téma."""
    print("\nVyber barevné téma:")
    themes = list(THEMES_04.keys())
    for i, t in enumerate(themes, 1):
        print(f"  {i}. {t}")
    while True:
        choice = input(f"Volba [1-{len(themes)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(themes):
            return themes[int(choice) - 1]
        print(f"Zadej číslo 1-{len(themes)}.")


def choose_color() -> chess.Color:
    """Volba barvy hráče — bílý (default) nebo černý."""
    while True:
        # Walrus by tady šel, ale je to vzdělávací repo — explicitnější je lepší
        choice = input("\nHraješ za bílého nebo černého? [w/b, default w]: ").strip().lower()
        if choice == '' or choice == 'w':
            return chess.WHITE
        if choice == 'b':
            return chess.BLACK
        print("Zadej 'w' nebo 'b' (nebo Enter pro bílého).")


def choose_skill() -> int:
    """Stockfish Skill Level 0-20 (0 = nejslabší, 20 = max síla)."""
    while True:
        choice = input("\nÚroveň Stockfish [0-20, default 5]: ").strip() or '5'
        if choice.isdigit() and 0 <= int(choice) <= 20:
            return int(choice)
        print("Zadej číslo 0-20.")


# === Hlavní smyčka ============================================================

def main() -> None:
    print("=" * 60)
    print("HRA PROTI STOCKFISH")
    print("=" * 60)

    # Setup hry
    style = choose_renderer()
    if style == 4:
        theme = choose_theme_04()
        # Lambda zachytí 'theme' z closure — render_fn dostane jen board
        render_fn = lambda b: render_04(b, theme=theme)
    else:
        render_fn = RENDERERS[style][1]

    player_color = choose_color()
    skill = choose_skill()

    # Spuštění Stockfish — popen_uci hledá v PATH
    try:
        engine = chess.engine.SimpleEngine.popen_uci("stockfish")
    except FileNotFoundError:
        print("\nCHYBA: Stockfish nenalezen v PATH.")
        print("Stáhni z https://stockfishchess.org/download/")
        print("Po instalaci přidej cestu k stockfish.exe do PATH.")
        return

    engine.configure({"Skill Level": skill})

    board = chess.Board()
    color_name = 'bílého' if player_color == chess.WHITE else 'černého'
    print(f"\nHraješ za {color_name}, Stockfish skill {skill}.")
    print("Tahy: SAN ('Nf3', 'e4', 'O-O') nebo UCI ('g1f3', 'e2e4', 'e7e8q' = proměna).")
    print("Příkazy: 'quit' = ukončit, 'resign' = vzdát se.\n")

    # První render + otevření prohlížeče
    write_render(board, render_fn, "Hra", refresh=True)
    os.startfile(os.path.abspath(OUTPUT_FILE))

    resigned = False
    try:
        while not board.is_game_over():
            print(pgn_table(board))
            print()

            if board.turn == player_color:
                # Tah hráče
                turn_name = 'bílý' if board.turn == chess.WHITE else 'černý'
                move_str = input(f"Tvůj tah ({turn_name}): ").strip()
                if move_str.lower() in {'quit', 'q', 'exit'}:
                    print("Konec hry.")
                    return
                if move_str.lower() in {'resign', 'r'}:
                    print("Vzdal ses.")
                    resigned = True
                    break
                try:
                    move = parse_move(board, move_str)
                except ValueError as e:
                    print(f"  {e}")
                    continue
                board.push(move)
            else:
                # Tah enginu
                print("Stockfish přemýšlí...", flush=True)
                result = engine.play(board, chess.engine.Limit(time=ENGINE_THINK_TIME))
                print(f"  Stockfish: {board.san(result.move)}")
                board.push(result.move)

            # Po každém tahu (hráče i enginu) přegenerujeme HTML — browser refreshne sám
            write_render(board, render_fn, "Hra", refresh=True)

        # Konec hry — výsledek
        print("\n" + "=" * 60)
        print("KONEC HRY")
        print(pgn_table(board))
        outcome = board.outcome()
        if resigned:
            winner = 'černý' if player_color == chess.WHITE else 'bílý'
            print(f"Výsledek: vzdal ses, vyhrál {winner}.")
        elif outcome:
            # outcome.termination je enum (CHECKMATE, STALEMATE, INSUFFICIENT_MATERIAL, ...)
            print(f"Výsledek: {outcome.result()} — {outcome.termination.name}")
        print("=" * 60)
        # Finální render bez refresh — prohlížeč přestane blikat
        write_render(board, render_fn, "Konec hry", refresh=False)

    finally:
        # Engine musíme vždy ukončit, jinak zůstane subprocess viset
        engine.quit()


if __name__ == "__main__":
    main()
