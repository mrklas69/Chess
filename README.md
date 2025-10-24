# Chess
Šachové experimenty - generování šachových diagramů ve stylu LaTeX pomocí Python knihovny `python-chess`

## Přehled skriptů

Projekt obsahuje tři Python skripty pro různé styly vizualizace šachových pozic:

### 1. Základní chess.svg ([01_chess_svg/01_chess_svg.py](01_chess_svg/01_chess_svg.py))
Nejjednodušší varianta využívající standardní vektorové figurky z knihovny `python-chess`.

**Vlastnosti:**
- Barevná šachovnice (světlá #C3C6BE, tmavá #727FA2)
- Vektorové figurky
- Souřadnice (a-h, 1-8)
- Výstup: `01_chess_svg.svg`

**Spuštění:**
```bash
cd 01_chess_svg
python 01_chess_svg.py
```

### 2. LaTeX xskak styl ([02_xskak_latex/xskak_latex.py](02_xskak_latex/xskak_latex.py))
Replika stylu LaTeXového balíčku **xskak** - profesionální černobílý diagram se šrafováním tmavých polí.

**Vlastnosti:**
- Šrafování tmavých polí (13 diagonálních čar na políčko, jako v LaTeXu)
- PNG figurky USCF (z adresáře `02_xskak_latex/uscf/`)
- Černý rámeček kolem šachovnice
- Typewriter font pro souřadnice (Source Code Pro / Courier)
- Bílé pozadí pro celý obrázek
- Optimalizovaný viewBox pro správné zobrazení ve VS Code i prohlížečích
- Výstup: `xskak_latex.svg` (rozměry: 400×408px)

**Spuštění:**
```bash
cd 02_xskak_latex
python xskak_latex.py
```

### 3. Leipzig styl ([03_leipzig/03_leipzig.py](03_leipzig/03_leipzig.py))
Elegantní minimalistický diagram inspirovaný lipským šachovým typografickým stylem.

**Vlastnosti:**
- Šedá tmavá pole (#E1E1E1) bez šrafování
- PNG figurky Leipzig (z adresáře `03_leipzig/leipzig/`)
- Čisté bílé pozadí
- Jednoduché souřadnice
- Výstup: `03_leipzig.svg`

**Spuštění:**
```bash
cd 03_leipzig
python 03_leipzig.py
```

### 4. Chessboard Image modul ([04_chessboard_image/generate_image.py](04_chessboard_image/generate_image.py))
Využití specializované knihovny **chessboard_image** pro generování PNG obrázků šachovnic s různými barevnými tématy.

**Vlastnosti:**
- Generování PNG formátu (místo SVG)
- 5 různých barevných témat (alpha, wikipedia, uscf, wisteria, sakura)
- Zobrazení souřadnic (a-h, 1-8)
- Konfigurovatelná velikost (400×400px)
- Výstupy: `sicilian_defense_*.png` (pro každé téma)

**Šachová pozice:**
Sicilská obrana po 2 tazích:
```
1. e4 c5
```

**Spuštění:**
```bash
cd 04_chessboard_image
python generate_image.py
```

**Požadavky:**
```bash
pip install chessboard_image
```

## Požadavky
```bash
pip install python-chess
```
