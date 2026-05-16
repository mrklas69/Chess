# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Účel projektu

Vzdělávací sandbox — pět nezávislých Python skriptů (01–05), z nichž každý generuje šachový diagram **jinou technikou**. Jde o porovnání přístupů, ne o produkční nástroj. Detailní přehled jednotlivých řešení viz `README.md`.

Šestý adresář `06_play/` je interaktivní hra proti Stockfish, která reuses (kopií, ne importem) renderery z 01–05.

## Spouštění

Skripty se spouštějí ručně, **z kořene repozitáře**:

```bash
python 01_chess_svg/chess_svg.py
python 02_xskak_latex/xskak_latex.py
python 03_leipzig/leipzig.py
python 04_chessboard_image/generate_image.py
python 05_leipfont/leipfont.py
python 06_play/play.py
```

Pozor: `README.md` v instrukcích používá `cd 0X_... && python ...`, ale to **rozbije** řešení 02 a 03 — viz níže.

Závislosti:
- `pip install python-chess` — pro řešení 01–04, 06
- Řešení 05 nepoužívá žádnou knihovnu, ale vyžaduje font Chess Leipzig nainstalovaný ve Windows na `C:\Windows\Fonts\LEIPFONT.TTF`
- Řešení 06 vyžaduje **Stockfish** v PATH (<https://stockfishchess.org/download/>)

## Architektura a vzory

- **Číslované adresáře `0X_*`** odpovídají samostatným řešením. Skripty 01–05 se navzájem nesdílejí ani neimportují — žádný společný util modul. Když měníš jeden přístup, ostatních se to netýká.
- **`06_play/renderers.py`** je výjimka, ale neporušuje princip: skripty 01–05 zůstávají nedotčené. `06_play` má **vlastní kopii** render logiky (5 funkcí), aby mohlo dynamicky vybírat styl v runtime. Když změníš chování v 0X, musíš ho promítnout do `06_play/renderers.py` ručně — divergence je cena za samostatnost 01–05.
- **Hardcoded relativní cesty k assetům:** `02_xskak_latex/xskak_latex.py` a `03_leipzig/leipzig.py` čtou PNG figurky z `./02_xskak_latex/uscf` resp. `./03_leipzig/leipzig`. Cesta je relativní ke **CWD**, ne ke skriptu — proto musí běžet z kořene. Pokud měníš strukturu adresářů, oprav i tyto cesty (`piece_dir = '...'`).
- **Společný pattern 02 + 03:** vygeneruj SVG přes `chess.svg.board()` s bílými poli → odstraň vektorové `<use>` figurky regexem → vlož `<image>` elementy s PNG data URI (base64). Když přidáváš podobné řešení s PNG figurkami, drž se tohoto postupu kvůli konzistenci.
- **Výstupy jdou do CWD** (kořene repozitáře). `.gitignore` ignoruje `*.svg`, `*.png`, `*.html` — výstupy se necommitují, jen zdrojové PNG figurky v podadresářích (ty .gitignore přesto vidí jako ignorované, ale jsou už trackované z dřívějška).
- **`os.startfile(...)` na konci každého skriptu** automaticky otevře výsledek — Windows-only. Skripty nejsou cross-platform a nemá smysl je takovými dělat (uživatel pracuje výhradně na Windows).

## Konvence

- Komentáře v kódu **česky** (viz globální `~/.claude/CLAUDE.md`).
- Identifikátory, názvy souborů a barevné konstanty anglicky.
- Hex barvy se opakují napříč skripty (např. `#727FA2` jako tmavé pole) — pokud se rozhodneš pro DRY refaktor, vědomá volba je necentralizovat, protože každé řešení má být **čitelně samostatné**.
