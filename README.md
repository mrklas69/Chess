# Chess

Šachové experimenty - generování šachových diagramů různými technikami v Pythonu.

## Přehled řešení

Projekt obsahuje pět Python skriptů, každý demonstruje jiný přístup k vizualizaci šachové pozice:

| #  | Řešení           | Technologie                 | Výstup | Pozice                                      | Figurky                  |
| -- | ---------------- | --------------------------- | ------ | ------------------------------------------- | ------------------------ |
| 01 | chess_svg        | `python-chess` SVG          | SVG    | Základní postavení                          | Vektorové (vestavěné)    |
| 02 | xskak_latex      | `python-chess` + úpravy SVG | SVG    | Ruy Lopez (1.e4 e5 2.Jf3 Jc6 3.Ss5 a6)    | PNG (USCF sada)          |
| 03 | leipzig          | `python-chess` + úpravy SVG | SVG    | Ruy Lopez (1.e4 e5 2.Jf3 Jc6 3.Ss5 a6)    | PNG (Leipzig sada)       |
| 04 | chessboard_image | `python-chess` SVG          | SVG    | Sicilská obrana (1.e4 c5)                   | 5 barevných témat        |
| 05 | leipfont         | Čistý Python (bez knihoven) | HTML   | Italská hra (1.e4 e5 2.Jf3 Jc6 3.Sc4 Sc5) | Font Chess Leipzig (TTF) |

### 1. Základní chess.svg ([01_chess_svg/chess_svg.py](01_chess_svg/chess_svg.py))

Nejjednodušší varianta využívající standardní vektorové figurky z knihovny `python-chess`.

**Vlastnosti:**

- Barevná šachovnice (světlá #C3C6BE, tmavá #727FA2)
- Vektorové figurky
- Souřadnice (a-h, 1-8)
- Výstup: `chess_svg.svg`

**Spuštění:**

```bash
cd 01_chess_svg
python chess_svg.py
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
- Výstup: `xskak_latex.svg` (rozměry: 400x408px)

**Spuštění:**

```bash
cd 02_xskak_latex
python xskak_latex.py
```

### 3. Leipzig styl ([03_leipzig/leipzig.py](03_leipzig/leipzig.py))

Elegantní minimalistický diagram inspirovaný lipským šachovým typografickým stylem.

**Vlastnosti:**

- Šedá tmavá pole (#E1E1E1) bez šrafování
- PNG figurky Leipzig (z adresáře `03_leipzig/leipzig/`)
- Čisté bílé pozadí
- Jednoduché souřadnice
- Výstup: `leipzig.svg`

**Spuštění:**

```bash
cd 03_leipzig
python leipzig.py
```

### 4. Barevná témata ([04_chessboard_image/generate_image.py](04_chessboard_image/generate_image.py))

Stejná pozice v 5 různých barevných tématech pomocí `python-chess`.

**Vlastnosti:**

- 5 barevných témat (alpha, wikipedia, uscf, wisteria, sakura)
- Vektorové figurky (vestavěné v python-chess)
- Souřadnice (a-h, 1-8)
- Výstupy: `sicilian_defense_*.svg` (pro každé téma)

**Spuštění:**

```bash
cd 04_chessboard_image
python generate_image.py
```

### 5. Leipzig font - HTML ([05_leipfont/leipfont.py](05_leipfont/leipfont.py))

Generování šachovnice pomocí speciálního šachového fontu **Chess Leipzig** (LEIPFONT.TTF). Zcela odlišný přístup - místo grafiky se diagram skládá ze znaků fontu.

**Vlastnosti:**

- Žádná závislost na `python-chess` ani jiných knihovnách
- Mapování figur na znaky fontu (rozlišení světlých/tmavých polí)
- Okraje a souřadnice zabudované ve znacích fontu
- Výstup: `leipzig.html`
- Vyžaduje nainstalovaný font LEIPFONT.TTF (v `C:\Windows\Fonts\`)

**Spuštění:**

```bash
cd 05_leipfont
python leipfont.py
```

## Požadavky

```bash
pip install python-chess        # pro řešení 01, 02, 03, 04
```

Řešení 05 vyžaduje nainstalovaný font **Chess Leipzig** (LEIPFONT.TTF) ve Windows.

## Poznámka k výstupním souborům

Výstupní soubory se generují do aktuálního pracovního adresáře (CWD). Pokud skripty spouštíte z kořene repozitáře, výstupy se uloží tam.
