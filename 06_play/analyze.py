"""Hloubková analýza partie Stockfishem na max úrovni.

Načte PGN definovaný inline (PGN_INPUT), pro každou pozici spustí Stockfish
s plnými prostředky (Skill 20, plné Threads + Hash) a klasifikuje tahy podle
ztráty centipawnů (Lichess-style hranice). Výstupy do 06_play/:
    - game.pgn      (čistá partie)
    - analysis.md   (markdown analýza)

Spuštění:
    python 06_play/analyze.py
"""
import datetime
import io
import math
import os
from pathlib import Path

import chess
import chess.engine
import chess.pgn

# === Vstup ===================================================================

PGN_INPUT = """[Event "Casual Game"]
[Site "localhost"]
[Date "2026.05.16"]
[Round "-"]
[White "Player"]
[Black "Stockfish"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Be7 5. Nc3 d6 6. d3 b5 7. Bb3 Nf6 8. O-O
h6 9. Be3 O-O 10. Qd2 Bg4 11. Nd5 Nxd5 12. Bxd5 Qe8 13. a3 Rb8 14. h3 Bxf3 15.
gxf3 Bg5 16. Bxg5 hxg5 17. Qxg5 Qd8 18. Qg4 Ne7 19. Ba2 Rb6 20. Kh2 d5 21. Rg1
Rg6 22. Qh5 Rxg1 23. Rxg1 Qd6 24. Rg5 Rd8 25. Rxe5 f6 26. Bxd5+ Nxd5 27. exd5
Qxe5+ *"""

# === Konfigurace ============================================================

ANALYSIS_TIME = 2.0  # sekund na pozici (kompromis kvalita vs. čas)
HASH_MB = 256
SCRIPT_DIR = Path(__file__).resolve().parent
GAME_PGN_PATH = SCRIPT_DIR / "game.pgn"
ANALYSIS_MD_PATH = SCRIPT_DIR / "analysis.md"

# Hranice klasifikace v centipawnech (Lichess-style)
THRESHOLDS = [
    (300, "Blunder"),
    (100, "Mistake"),
    (50, "Inaccuracy"),
    (20, "OK"),
]


def classify(loss_cp: int) -> str:
    """Klasifikace tahu podle ztráty centipawnů (vždy nezáporná)."""
    for limit, label in THRESHOLDS:
        if loss_cp >= limit:
            return label
    return "Best"


# === Accuracy a performance rating (Lichess-style) ==========================

def win_pct(cp: int) -> float:
    """Centipawn skóre → win % (Lichess sigmoid).
    Cap mate skóre na ±1000cp, aby sigmoid nevybuchl pro extrémní hodnoty."""
    cp_clipped = max(-1000, min(1000, cp))
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * cp_clipped)) - 1)


def move_accuracy(win_before: float, win_after: float) -> float:
    """Accuracy jednoho tahu (Lichess formule). Vstupy = win% z perspektivy hrajícího."""
    diff = max(0.0, win_before - win_after)
    val = 103.1668 * math.exp(-0.04354 * diff) - 3.1669
    return max(0.0, min(100.0, val))


def overall_accuracy(rows: list[dict], color: str) -> float:
    """Průměrná accuracy hráče přes všechny jeho tahy."""
    accs = []
    for r in rows:
        if r["color"] != color:
            continue
        # Pro bílého: skóre z bílé perspektivy = jeho perspektiva.
        # Pro černého: invertuji znaménko, ať dostanu jeho win%.
        sign = 1 if color == "W" else -1
        wb = win_pct(sign * r["score_before"])
        wa = win_pct(sign * r["score_after"])
        accs.append(move_accuracy(wb, wa))
    return sum(accs) / len(accs) if accs else 0.0


def estimate_elo(accuracy: float) -> int:
    """Hrubý odhad ELO z accuracy %.
    Lineární mapování kalibrované přibližně podle Lichess dat:
        50% → 900,  70% → 1500,  80% → 1800,  90% → 2100,  100% → 2400.
    Není FIDE Performance rating — pouze odhad výkonu kvality."""
    return round(30 * accuracy - 600)


def verbal_eval(rows: list[dict], color: str, accuracy: float) -> str:
    """Krátké slovní hodnocení výkonu hráče (2-3 věty z hrubých statistik)."""
    own = [r for r in rows if r["color"] == color]
    n_blunders = sum(1 for r in own if r["klas"] == "Blunder")
    n_mistakes = sum(1 for r in own if r["klas"] == "Mistake")
    n_inacc = sum(1 for r in own if r["klas"] == "Inaccuracy")
    worst = max(own, key=lambda r: r["loss"]) if own else None

    # Verdikt podle accuracy bandů (orientačně podle Lichess kalibrace)
    if accuracy >= 90:
        verdict = "Vynikající přesnost — výkon na úrovni silného hráče."
    elif accuracy >= 80:
        verdict = "Velmi solidní výkon, jen drobné nepřesnosti."
    elif accuracy >= 70:
        verdict = "Slušný výkon s prostorem ke zlepšení."
    elif accuracy >= 60:
        verdict = "Průměrný výkon, několik důležitých chyb."
    else:
        verdict = "Slabší výkon — partii rozhodlo více chyb."

    # Stručný výčet kategorií chyb (české skloňování s 'krát')
    issues = []
    if n_blunders:
        issues.append(f"{n_blunders}× blunder")
    if n_mistakes:
        issues.append(f"{n_mistakes}× mistake")
    if n_inacc:
        issues.append(f"{n_inacc}× inaccuracy")
    issue_str = ", ".join(issues) if issues else "bez vážných chyb"

    sentences = [verdict, f"Statistika chyb: {issue_str}."]
    # Vypíchnout nejhorší tah jen pokud byl skutečně bolestivý (≥100cp)
    if worst and worst["loss"] >= 100:
        prefix = ".." if color == "B" else "."
        sentences.append(
            f"Klíčový moment: **{worst['move_no']}{prefix} {worst['san']}** "
            f"(ztráta {worst['loss']}cp, lépe **{worst['best_san']}**)."
        )
    return " ".join(sentences)


def fmt_score(cp: int) -> str:
    """Centipawn skóre → lidsky čitelné: '+1.23', '-0.50', '+M5'.
    Mate score je v python-chess.engine reprezentován velkou hodnotou
    (mate_score=10000 znamená že mat v 0 půltazích = ±10000)."""
    if abs(cp) >= 9000:
        mate_in = 10000 - abs(cp)
        return f"{'+' if cp > 0 else '-'}M{mate_in}"
    return f"{cp / 100:+.2f}"


def analyse_game(engine: chess.engine.SimpleEngine, game: chess.pgn.Game) -> list[dict]:
    """Projde tahy partie, vrátí list dictů s analýzou každého půltahu."""
    board = game.board()
    rows = []
    total = sum(1 for _ in game.mainline_moves())
    print(f"Analyzuji {total} půltahů (~{total * 2 * ANALYSIS_TIME:.0f}s)...")

    for ply, node in enumerate(game.mainline(), 1):
        move = node.move
        color = board.turn  # kdo táhne (před push)
        color_letter = "W" if color == chess.WHITE else "B"
        san = board.san(move)
        move_no = (ply + 1) // 2

        # 1) eval pozice PŘED tahem + nejlepší tah engine
        info_before = engine.analyse(board, chess.engine.Limit(time=ANALYSIS_TIME))
        score_before = info_before["score"].white().score(mate_score=10000)
        best_move = info_before["pv"][0] if info_before.get("pv") else None
        best_san = board.san(best_move) if best_move else "?"

        # 2) přehraj a změř pozici PO tahu
        board.push(move)
        info_after = engine.analyse(board, chess.engine.Limit(time=ANALYSIS_TIME))
        score_after = info_after["score"].white().score(mate_score=10000)

        # 3) ztráta z pohledu hrajícího (vždy nezáporná)
        # Pro bílého: ztráta = před - po (vyšší skóre = lepší pro W).
        # Pro černého: opačně (vyšší skóre = horší pro B).
        if color == chess.WHITE:
            loss = score_before - score_after
        else:
            loss = score_after - score_before
        loss = max(0, loss)

        klas = classify(loss)
        rows.append({
            "ply": ply,
            "move_no": move_no,
            "color": color_letter,
            "san": san,
            "score_before": score_before,  # eval pozice před tahem (pohled bílého)
            "score_after": score_after,    # eval pozice po tahu (pohled bílého)
            "loss": loss,
            "klas": klas,
            "best_san": best_san,
        })
        print(f"  {move_no:2}{color_letter} {san:8} eval={fmt_score(score_after):>7}  "
              f"loss={loss:>5}cp  {klas:<11} best={best_san}")

    return rows


def build_markdown(game: chess.pgn.Game, rows: list[dict]) -> str:
    """Sestaví markdown report ze surových analýz."""
    # Souhrn — počty klasifikací po hráčích
    cats = ["Best", "OK", "Inaccuracy", "Mistake", "Blunder"]
    w_stats = {c: 0 for c in cats}
    b_stats = {c: 0 for c in cats}
    for r in rows:
        (w_stats if r["color"] == "W" else b_stats)[r["klas"]] += 1

    # Klíčové chyby — Inaccuracy a horší
    key_errors = [r for r in rows if r["klas"] in ("Inaccuracy", "Mistake", "Blunder")]

    # Accuracy a performance per hráč
    w_acc = overall_accuracy(rows, "W")
    b_acc = overall_accuracy(rows, "B")
    w_perf = estimate_elo(w_acc)
    b_perf = estimate_elo(b_acc)
    w_verbal = verbal_eval(rows, "W", w_acc)
    b_verbal = verbal_eval(rows, "B", b_acc)
    white_name = game.headers.get("White", "?")
    black_name = game.headers.get("Black", "?")

    md = [
        "# Analýza partie",
        "",
        f"**Datum analýzy:** {datetime.date.today():%Y-%m-%d}",
        f"**Engine:** Stockfish (Skill 20, Threads={os.cpu_count() or '?'}, "
        f"Hash={HASH_MB}MB, {ANALYSIS_TIME}s/pozici)",
        f"**Bílý:** {white_name}",
        f"**Černý:** {black_name}",
        f"**Výsledek:** {game.headers.get('Result', '*')}",
        "",
        "## Hodnocení výkonu",
        "",
        "| Hráč | Accuracy | Perf. rating (odhad) |",
        "|------|---------:|---------------------:|",
        f"| Bílý ({white_name}) | {w_acc:.1f}% | ~{w_perf} |",
        f"| Černý ({black_name}) | {b_acc:.1f}% | ~{b_perf} |",
        "",
        "Accuracy podle Lichess formule (win% sigmoid). Performance rating je "
        "hrubý lineární odhad z accuracy (kalibrace: 50% ≈ 900, 80% ≈ 1800, "
        "100% ≈ 2400) — **není to FIDE Performance rating**, slouží jen jako "
        "indikace úrovně výkonu v této partii.",
        "",
        f"**Bílý ({white_name}):** {w_verbal}",
        "",
        f"**Černý ({black_name}):** {b_verbal}",
        "",
        "## Souhrn klasifikace tahů",
        "",
        "| Hráč | Best | OK | Inaccuracy | Mistake | Blunder |",
        "|------|-----:|---:|-----------:|--------:|--------:|",
        f"| Bílý | {w_stats['Best']} | {w_stats['OK']} | {w_stats['Inaccuracy']} | "
        f"{w_stats['Mistake']} | {w_stats['Blunder']} |",
        f"| Černý | {b_stats['Best']} | {b_stats['OK']} | {b_stats['Inaccuracy']} | "
        f"{b_stats['Mistake']} | {b_stats['Blunder']} |",
        "",
        "Hranice (ztráta centipawnů): Best <20, OK 20–49, Inaccuracy 50–99, "
        "Mistake 100–299, Blunder ≥300.",
        "",
        "## Klíčové chyby",
        "",
    ]

    if key_errors:
        for r in key_errors:
            prefix = ".." if r["color"] == "B" else "."
            md.append(
                f"- **{r['move_no']}{prefix} {r['san']}** "
                f"({r['klas']}, ztráta {r['loss']}cp) — "
                f"lepší: **{r['best_san']}**, "
                f"eval po hraném tahu: {fmt_score(r['score_after'])}"
            )
    else:
        md.append("(žádné chyby ≥50cp)")

    md += [
        "",
        "## Všechny tahy",
        "",
        "| # | Bílý | eval | klas | Černý | eval | klas |",
        "|--:|------|-----:|------|-------|-----:|------|",
    ]

    # Spáruj půltahy do řádků po celých tazích.
    by_move: dict[int, dict] = {}
    for r in rows:
        by_move.setdefault(r["move_no"], {})[r["color"]] = r
    for n in sorted(by_move):
        w = by_move[n].get("W")
        b = by_move[n].get("B")
        w_part = (f"{w['san']} | {fmt_score(w['score_after'])} | {w['klas']}"
                  if w else "— | — | —")
        b_part = (f"{b['san']} | {fmt_score(b['score_after'])} | {b['klas']}"
                  if b else "— | — | —")
        md.append(f"| {n} | {w_part} | {b_part} |")

    md.append("")
    return "\n".join(md)


def main() -> None:
    game = chess.pgn.read_game(io.StringIO(PGN_INPUT))
    if game is None:
        raise SystemExit("Selhalo parsování PGN")

    # Ulož čistou kopii PGN
    with open(GAME_PGN_PATH, "w", encoding="utf-8") as f:
        game.accept(chess.pgn.FileExporter(f))
    print(f"Uloženo: {GAME_PGN_PATH}")

    # Stockfish na max — full threads, hash, max skill
    engine = chess.engine.SimpleEngine.popen_uci("stockfish")
    try:
        engine.configure({
            "Skill Level": 20,
            "Hash": HASH_MB,
            "Threads": os.cpu_count() or 2,
        })
        rows = analyse_game(engine, game)
    finally:
        engine.quit()

    md = build_markdown(game, rows)
    ANALYSIS_MD_PATH.write_text(md, encoding="utf-8")
    print(f"\nUloženo: {ANALYSIS_MD_PATH}")


if __name__ == "__main__":
    main()
