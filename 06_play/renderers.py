"""
Render funkce pro hru proti enginu. Každá funkce vezme chess.Board a vrátí
HTML fragment (string), který se vloží do <body>.

Logika je zkopírována z odpovídajících 0X skriptů — úmyslná duplikace per
CLAUDE.md (skripty 01-05 mají být samostatné, nedotčené). Když změníš
chování v 0X, musíš ho promítnout sem ručně.
"""
import base64
import re
from pathlib import Path

import chess
import chess.svg

# Cesty k PNG assetům jsou relativní k tomuto souboru, ne k CWD.
# Tím skript funguje z libovolného adresáře, ne jen z root repa.
_REPO_ROOT = Path(__file__).resolve().parent.parent

# Mapování symbolů python-chess (KQRBNP, kqrbnp) na názvy PNG souborů.
# Sdílené 02 i 03 mají stejné názvy figurek (wP.png, bK.png, ...).
_PIECE_FILES = {
    'P': 'wP.png', 'N': 'wN.png', 'B': 'wB.png',
    'R': 'wR.png', 'Q': 'wQ.png', 'K': 'wK.png',
    'p': 'bP.png', 'n': 'bN.png', 'b': 'bB.png',
    'r': 'bR.png', 'q': 'bQ.png', 'k': 'bK.png',
}


# === 01: Základní python-chess SVG ============================================

def render_01(board: chess.Board) -> str:
    """Základní python-chess SVG (USCF modré barvy)."""
    return chess.svg.board(
        board,
        size=400,
        coordinates=True,
        colors={
            "square light": "#C3C6BE",
            "square dark": "#727FA2",
            "margin": "#727FA2",
            "coord": "#000000",
        },
    )


# === Sdílené utility pro 02 a 03 ==============================================

def _load_pieces(piece_dir: Path) -> dict[str, str]:
    """Načte 12 PNG figurek z adresáře, vrátí mapu symbol → data URI."""
    pieces = {}
    for sym, fname in _PIECE_FILES.items():
        # read_bytes() vyhodí FileNotFoundError pokud soubor chybí — to je OK,
        # crash je lepší než tichý fail (stejný princip jako v 02/03 po cleanu)
        data = (piece_dir / fname).read_bytes()
        b64 = base64.b64encode(data).decode('utf-8')
        pieces[sym] = f'data:image/png;base64,{b64}'
    return pieces


def _replace_pieces_with_images(svg: str, board: chess.Board,
                                pieces: dict[str, str], padding: int) -> str:
    """Společný pattern 02+03: vyhodí <use> figurky a vloží <image> z PNG."""
    # Odstranit všechny vektorové figurky bez ohledu na pořadí atributů
    svg = re.sub(r'<use\b[^/]*?/>', '', svg)

    # Vykreslit PNG figurky na správné souřadnice (15px margin, 45px pole)
    pieces_svg = ''
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            file_idx = chess.square_file(square)
            rank_idx = chess.square_rank(square)
            x = 15 + file_idx * 45
            y = 15 + (7 - rank_idx) * 45  # rank 0 (řada 1) je dole
            sym = piece.symbol()
            if sym in pieces:
                pieces_svg += (
                    f'<image x="{x + padding}" y="{y + padding}" '
                    f'width="{45 - 2 * padding}" height="{45 - 2 * padding}" '
                    f'href="{pieces[sym]}" />\n'
                )

    return svg.replace('</svg>', pieces_svg + '</svg>')


# Cache PNG assetů — načti jednou per session, ne při každém tahu.
# Bez cache by se 12 souborů base64-kódovalo opakovaně (zbytečná práce).
_pieces_uscf_cache: dict[str, str] | None = None
_pieces_leipzig_cache: dict[str, str] | None = None


# === 02: xskak LaTeX styl =====================================================

def render_02(board: chess.Board) -> str:
    """xskak LaTeX styl: bílá pole, šrafovaná tmavá, PNG USCF figurky."""
    global _pieces_uscf_cache
    if _pieces_uscf_cache is None:
        _pieces_uscf_cache = _load_pieces(_REPO_ROOT / "02_xskak_latex" / "uscf")

    # Bílá pole pro oba typy — tmavá se přebarví patternem níže
    svg = chess.svg.board(
        board, size=400, coordinates=True,
        colors={
            "square light": "#ffffff", "square dark": "#ffffff",
            "margin": "#ffffff", "coord": "#000000",
        },
    )

    # Pattern šrafování (13 čar na políčko, jako LaTeX xskak)
    pattern_size = 6.78
    hatching = f'''
<pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="{pattern_size}" height="{pattern_size}">
  <rect width="{pattern_size}" height="{pattern_size}" fill="#ffffff"/>
  <path d="M-1,1 l2,-2 M0,{pattern_size} l{pattern_size},-{pattern_size} M{pattern_size-1},{pattern_size+1} l2,-2" style="stroke:#727FA2; stroke-width:1" />
</pattern>
'''
    # Typewriter font pro souřadnice (přebije default sans-serif)
    typewriter = '''
<style>
  .coordinates {
    font-family: 'Source Code Pro', Courier, monospace;
    font-weight: normal;
    font-size: 18px;
    fill: #000000;
  }
</style>
'''
    svg = svg.replace('<defs>', '<defs>' + hatching + typewriter, 1)

    # Bílé pozadí pod celou plochou (pro případ tmavého theme prohlížeče)
    white_bg = '<rect x="0" y="0" width="390" height="398" fill="#ffffff"/>\n'
    svg = svg.replace('</defs>', '</defs>' + white_bg, 1)

    # Zvětšit výšku o 8px aby se vešly souřadnice
    svg = svg.replace('height="400"', 'height="408"')
    svg = svg.replace('viewBox="0 0 390 390"', 'viewBox="0 0 390 398"')

    # Odstranit defaultní souřadnice (sans-serif) — nahradíme typewriter verzí
    svg = re.sub(
        r'<g transform="translate\([^"]+\)" fill="#[0-9a-f]+" stroke="#[0-9a-f]+"><path d="[^"]+"\s*/></g>',
        '', svg,
    )

    # Vlastní souřadnice typewriter fontem
    coords = ''
    for i, letter in enumerate("abcdefgh"):
        x = 15 + i * 45 + 22.5  # střed pole
        coords += f'<text x="{x}" y="391" text-anchor="middle" class="coordinates">{letter}</text>\n'
    for i in range(8):
        y = 15 + 360 - i * 45 - 22.5 + 5  # vertikální zarovnání baseline
        coords += f'<text x="7" y="{y}" text-anchor="middle" class="coordinates">{i + 1}</text>\n'

    border = '<rect x="15" y="15" width="360" height="360" fill="none" stroke="#000000" stroke-width="1"/>\n'
    svg = svg.replace('</svg>', border + coords + '</svg>')

    # Přebarvit tmavá pole patternem (původně bílá, teď šrafovaná)
    svg = re.sub(
        r'class="square dark([^"]*)"([^>]*)fill="#ffffff"',
        r'class="square dark\1"\2fill="url(#diagonalHatch)"',
        svg,
    )

    return _replace_pieces_with_images(svg, board, _pieces_uscf_cache, padding=1)


# === 03: Leipzig styl =========================================================

def render_03(board: chess.Board) -> str:
    """Leipzig styl: šedá tmavá pole, PNG Leipzig figurky."""
    global _pieces_leipzig_cache
    if _pieces_leipzig_cache is None:
        _pieces_leipzig_cache = _load_pieces(_REPO_ROOT / "03_leipzig" / "leipzig")

    svg = chess.svg.board(
        board, size=400, coordinates=True,
        colors={
            "square light": "#ffffff", "square dark": "#E1E1E1",
            "margin": "#ffffff", "coord": "#000000",
        },
    )
    return _replace_pieces_with_images(svg, board, _pieces_leipzig_cache, padding=3)


# === 04: Barevná témata =======================================================

# Témata duplicit s 04_chessboard_image/generate_image.py — vědomé zkopírování
# (per CLAUDE.md: skripty 0X jsou samostatné, 06_play je další samostatná jednotka)
THEMES_04 = {
    "alpha":     ("#f0d9b5", "#b58863"),
    "wikipedia": ("#FFCE9E", "#D18B47"),
    "uscf":      ("#C3C6BE", "#727FA2"),
    "wisteria":  ("#F5F0FF", "#967BB6"),
    "sakura":    ("#FFFFFF", "#FFCAD8"),
}


def render_04(board: chess.Board, theme: str = "uscf") -> str:
    """Barevné téma — default 'uscf' (modré), na výběr 5 témat."""
    light, dark = THEMES_04[theme]
    return chess.svg.board(
        board, size=400, coordinates=True,
        colors={
            "square light": light, "square dark": dark,
            "margin": light, "coord": "#000000",
        },
    )


# === 05: Chess Leipzig font (HTML) ============================================

def render_05(board: chess.Board) -> str:
    """Chess Leipzig font — HTML fragment se @font-face. Vyžaduje LEIPFONT.TTF."""
    # Mapování (symbol, typ_pole) → ASCII kód znaku ve fontu.
    # Typ pole: 0 = malé písmeno (jedna varianta), 1 = velké písmeno (druhá varianta).
    # Font Chess Leipzig má pro každou figuru dvě varianty znaků podle pozadí.
    pieces_char = {
        ('R', 0): 0x72, ('N', 0): 0x6E, ('B', 0): 0x62,
        ('Q', 0): 0x71, ('K', 0): 0x6B, ('P', 0): 0x70,
        ('r', 0): 0x74, ('n', 0): 0x6D, ('b', 0): 0x76,
        ('q', 0): 0x77, ('k', 0): 0x6C, ('p', 0): 0x6F,
        ('.', 0): 0x2A,
        ('R', 1): 0x52, ('N', 1): 0x4E, ('B', 1): 0x42,
        ('Q', 1): 0x51, ('K', 1): 0x4B, ('P', 1): 0x50,
        ('r', 1): 0x54, ('n', 1): 0x4D, ('b', 1): 0x56,
        ('q', 1): 0x57, ('k', 1): 0x4C, ('p', 1): 0x4F,
        ('.', 1): 0x2B,
    }
    # Okraje šachovnice (numerická klávesnice: 1=levý-horní roh, 9=pravý-dolní)
    corner_tl, corner_tr = 0x31, 0x33
    corner_bl, corner_br = 0x37, 0x39
    border_h, border_v = 0x32, 0x35
    # Souřadnicové znaky — viz cleanup commit 67bbd6d pro vysvětlení
    bottom_edge_files = list(range(0xC8, 0xD0))  # a-h s horním borderem
    left_edge_ranks = list(range(0xC0, 0xC8))    # 1-8 s pravým borderem

    # Sestavení desky řádek po řádku — řada 8 nahoře, řada 1 dole
    lines = [chr(corner_tl) + chr(border_h) * 8 + chr(corner_tr)]
    for row_idx in range(8):
        rank = 7 - row_idx  # 7 (řada 8) → 0 (řada 1)
        rank_label = chr(left_edge_ranks[rank])
        row_chars = []
        for file_idx in range(8):
            sq = chess.square(file_idx, rank)
            piece = board.piece_at(sq)
            sym = piece.symbol() if piece else '.'
            # Pozn.: tato podmínka reprodukuje chování 05_leipfont/leipfont.py
            # (matematicky odpovídá "tmavé pole" v standardní konvenci, ale font
            # Chess Leipzig používá inverzní mapování barev — proto se to neopravuje)
            is_light = (row_idx + file_idx) % 2 == 1
            square_type = 0 if is_light else 1
            code = pieces_char.get((sym, square_type), 0x3F)
            row_chars.append(chr(code))
        lines.append(rank_label + ''.join(row_chars) + chr(border_v))
    lines.append(chr(corner_bl) + ''.join(chr(c) for c in bottom_edge_files) + chr(corner_br))
    board_str = '\n'.join(lines)

    # HTML fragment s vloženým @font-face (style v body je platný HTML5)
    return f'''<style>
@font-face {{
    font-family: 'ChessLeipzig';
    src: local('LEIPFONT'),
         url('file:///C:/Windows/Fonts/LEIPFONT.TTF') format('truetype');
}}
.board-leipfont {{
    font-family: 'ChessLeipzig', monospace;
    font-size: 48px;
    line-height: 1.0;
    white-space: pre;
}}
</style>
<div class="board-leipfont">{board_str}</div>'''


# === Dispatch tabulka =========================================================

# Klíč: číslo stylu (1-5). Hodnota: (popisek pro menu, render funkce).
# Pro styl 4 (témata) volá play.py přímo render_04(board, theme=...) — proto má
# v dispatch tabulce default theme přes lambda fallback v play.py.
RENDERERS = {
    1: ("Základní python-chess SVG (01)", render_01),
    2: ("xskak LaTeX styl, šrafování + USCF PNG (02)", render_02),
    3: ("Leipzig styl, šedá + Leipzig PNG (03)", render_03),
    4: ("Barevná témata, na výběr 5 (04)", render_04),
    5: ("Chess Leipzig font, HTML (05)", render_05),
}
