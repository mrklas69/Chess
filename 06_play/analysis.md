# Analýza partie

**Datum analýzy:** 2026-05-16
**Engine:** Stockfish (Skill 20, Threads=16, Hash=256MB, 2.0s/pozici)
**Bílý:** Player
**Černý:** Stockfish
**Výsledek:** *

## Hodnocení výkonu

| Hráč | Accuracy | Perf. rating (odhad) |
|------|---------:|---------------------:|
| Bílý (Player) | 87.6% | ~2029 |
| Černý (Stockfish) | 89.5% | ~2085 |

Accuracy podle Lichess formule (win% sigmoid). Performance rating je hrubý lineární odhad z accuracy (kalibrace: 50% ≈ 900, 80% ≈ 1800, 100% ≈ 2400) — **není to FIDE Performance rating**, slouží jen jako indikace úrovně výkonu v této partii.

**Bílý (Player):** Velmi solidní výkon, jen drobné nepřesnosti. Statistika chyb: 1× blunder, 1× mistake, 3× inaccuracy. Klíčový moment: **25. Rxe5** (ztráta 668cp, lépe **Qg4**).

**Černý (Stockfish):** Velmi solidní výkon, jen drobné nepřesnosti. Statistika chyb: 2× mistake, 4× inaccuracy. Klíčový moment: **24.. Rd8** (ztráta 134cp, lépe **c6**).

## Souhrn klasifikace tahů

| Hráč | Best | OK | Inaccuracy | Mistake | Blunder |
|------|-----:|---:|-----------:|--------:|--------:|
| Bílý | 12 | 10 | 3 | 1 | 1 |
| Černý | 13 | 8 | 4 | 2 | 0 |

Hranice (ztráta centipawnů): Best <20, OK 20–49, Inaccuracy 50–99, Mistake 100–299, Blunder ≥300.

## Klíčové chyby

- **8.. h6** (Inaccuracy, ztráta 50cp) — lepší: **Na5**, eval po hraném tahu: +0.31
- **9. Be3** (Inaccuracy, ztráta 68cp) — lepší: **a3**, eval po hraném tahu: -0.36
- **9.. O-O** (Inaccuracy, ztráta 52cp) — lepší: **Na5**, eval po hraném tahu: +0.22
- **14. h3** (Inaccuracy, ztráta 82cp) — lepší: **Qc3**, eval po hraném tahu: -0.43
- **17.. Qd8** (Inaccuracy, ztráta 56cp) — lepší: **Nd4**, eval po hraném tahu: +0.45
- **22.. Rxg1** (Mistake, ztráta 128cp) — lepší: **Qd6**, eval po hraném tahu: +1.28
- **24. Rg5** (Inaccuracy, ztráta 76cp) — lepší: **Rg4**, eval po hraném tahu: +0.83
- **24.. Rd8** (Mistake, ztráta 134cp) — lepší: **c6**, eval po hraném tahu: +2.14
- **25. Rxe5** (Blunder, ztráta 668cp) — lepší: **Qg4**, eval po hraném tahu: -4.49
- **25.. f6** (Inaccuracy, ztráta 68cp) — lepší: **g6**, eval po hraném tahu: -3.94
- **26. Bxd5+** (Mistake, ztráta 116cp) — lepší: **f4**, eval po hraném tahu: -5.34

## Všechny tahy

| # | Bílý | eval | klas | Černý | eval | klas |
|--:|------|-----:|------|-------|-----:|------|
| 1 | e4 | +0.24 | Best | e5 | +0.23 | Best |
| 2 | Nf3 | +0.20 | Best | Nc6 | +0.24 | Best |
| 3 | Bb5 | +0.19 | Best | a6 | +0.35 | OK |
| 4 | Ba4 | +0.27 | Best | Be7 | +0.38 | Best |
| 5 | Nc3 | +0.07 | OK | d6 | +0.30 | OK |
| 6 | d3 | -0.09 | OK | b5 | -0.04 | Best |
| 7 | Bb3 | -0.14 | Best | Nf6 | +0.26 | OK |
| 8 | O-O | -0.18 | OK | h6 | +0.31 | Inaccuracy |
| 9 | Be3 | -0.36 | Inaccuracy | O-O | +0.22 | Inaccuracy |
| 10 | Qd2 | -0.15 | OK | Bg4 | +0.13 | OK |
| 11 | Nd5 | +0.05 | Best | Nxd5 | +0.15 | Best |
| 12 | Bxd5 | +0.09 | Best | Qe8 | +0.28 | Best |
| 13 | a3 | +0.04 | OK | Rb8 | +0.39 | OK |
| 14 | h3 | -0.43 | Inaccuracy | Bxf3 | -0.27 | Best |
| 15 | gxf3 | -0.25 | Best | Bg5 | -0.16 | Best |
| 16 | Bxg5 | -0.31 | Best | hxg5 | +0.00 | OK |
| 17 | Qxg5 | -0.24 | OK | Qd8 | +0.45 | Inaccuracy |
| 18 | Qg4 | +0.08 | OK | Ne7 | +0.50 | OK |
| 19 | Ba2 | +0.40 | OK | Rb6 | +0.64 | OK |
| 20 | Kh2 | +0.43 | Best | d5 | +0.44 | Best |
| 21 | Rg1 | +0.28 | Best | Rg6 | +0.25 | Best |
| 22 | Qh5 | +0.00 | OK | Rxg1 | +1.28 | Mistake |
| 23 | Rxg1 | +1.32 | Best | Qd6 | +1.53 | Best |
| 24 | Rg5 | +0.83 | Inaccuracy | Rd8 | +2.14 | Mistake |
| 25 | Rxe5 | -4.49 | Blunder | f6 | -3.94 | Inaccuracy |
| 26 | Bxd5+ | -5.34 | Mistake | Nxd5 | -5.76 | Best |
| 27 | exd5 | -6.03 | OK | Qxe5+ | -6.13 | Best |
