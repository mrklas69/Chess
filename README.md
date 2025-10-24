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

### 2. LaTeX xskak styl ([02_xskak_latex/02_xskak_latex.py](02_xskak_latex/02_xskak_latex.py))
Replika stylu LaTeXového balíčku **xskak** - profesionální černobílý diagram se šrafováním tmavých polí.

**Vlastnosti:**
- Šrafování tmavých polí (13 diagonálních čar na políčko, jako v LaTeXu)
- PNG figurky USCF (z adresáře `02_xskak_latex/uscf/`)
- Černý rámeček kolem šachovnice
- Typewriter font pro souřadnice (Source Code Pro / Courier)
- Bílé pozadí
- Výstup: `02_xskak_latex.svg`

**Spuštění:**
```bash
cd 02_xskak_latex
python 02_xskak_latex.py
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

## Kořenový skript ([srafovani.py](srafovani.py))
Původní experimentální skript s plnou konfigurací šrafování a různými barevnými tématy.

**Vlastnosti:**
- Šrafování tmavých polí s přesným výpočtem hustoty čar
- PNG figurky USCF (z adresáře `uscf/`)
- Konfigurovatelné barevné téma (chess24, metro, leipzig, wikipedia, dilena, uscf, symbol)
- Typewriter font pro souřadnice
- Margin v barvě #727FA2
- Výstup: `srafovani.svg`

**Spuštění:**
```bash
python srafovani.py
```

## Šachová pozice
Všechny skripty generují stejnou pozici - **Španělská partie (Ruy Lopez)** po 6 tazích:
```
1. e4 e5
2. Nf3 Nc6
3. Bb5 a6
```

## Požadavky
```bash
pip install python-chess
```
