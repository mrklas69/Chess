"""
Webový server pro hru proti Stockfish s drag-and-drop ovládáním v prohlížeči.

Spouštět z kořene repozitáře:
    python 06_play/play.py

Vyžaduje:
- python-chess (pip install python-chess)
- Stockfish v PATH

Server běží na http://localhost:8000 a sám otevře prohlížeč.
Ctrl+C ukončí.
"""
import datetime
import http.server
import json
import os
import sys
import urllib.parse
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

import chess
import chess.engine
import chess.pgn

# Renderers.py je ve stejném adresáři — přidám do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from renderers import RENDERERS, THEMES_04, render_04  # noqa: E402

PORT = 8000
ENGINE_THINK_TIME = 0.5  # sekundy přemýšlení Stockfish na tah

# Font pro styl 5 — servírujeme ho z HTTP, protože prohlížeč blokuje
# načítání file:/// zdrojů ze stránky doručené přes http://
LEIPFONT_PATH = Path('C:/Windows/Fonts/LEIPFONT.TTF')


# === Globální stav hry =======================================================

@dataclass
class GameState:
    """Single-user lokální server drží jednu hru v paměti.
    Lock kvůli souběhu (BaseHTTPRequestHandler je single-threaded, ale jistota neuškodí).
    """
    board: chess.Board = field(default_factory=chess.Board)
    style: int = 1  # 1-5 = klíč v RENDERERS
    theme: str = "uscf"  # používá se jen pro styl 4
    player_color: chess.Color = chess.WHITE
    skill: int = 5
    engine: chess.engine.SimpleEngine | None = None
    resigned: bool = False
    lock: Lock = field(default_factory=Lock)

    def render_fn(self):
        """Vrátí render funkci podle aktuální volby stylu/tématu."""
        if self.style == 4:
            # Lambda zachytí self.theme — render_04 chce 2 argumenty
            return lambda b: render_04(b, theme=self.theme)
        return RENDERERS[self.style][1]


_state = GameState()


# === Helpery pro stav hry ====================================================

def render_board_html(state: GameState) -> str:
    """Vygeneruje HTML fragment desky aktuální pozice ve zvoleném stylu."""
    return state.render_fn()(state.board)


def status_text(state: GameState) -> str:
    """Krátký lidsky čitelný status pro sidebar."""
    if state.resigned:
        winner = 'černý' if state.player_color == chess.WHITE else 'bílý'
        return f"Vzdal ses — vyhrál {winner}."
    outcome = state.board.outcome()
    if outcome:
        # outcome.termination je enum (CHECKMATE, STALEMATE, ...)
        return f"Konec: {outcome.result()} ({outcome.termination.name})"
    if state.board.turn == state.player_color:
        color = 'bílý' if state.board.turn == chess.WHITE else 'černý'
        check = " (ŠACH!)" if state.board.is_check() else ""
        return f"Tvůj tah ({color}){check}"
    return "Stockfish přemýšlí..."


def pgn_text(state: GameState) -> str:
    """PGN tabulka tahů bez hlaviček, bez závěrečné značky '*'."""
    if not state.board.move_stack:
        return "(žádné tahy)"
    game = chess.pgn.Game.from_board(state.board)
    exp = chess.pgn.StringExporter(headers=False, comments=False, variations=False)
    text = game.accept(exp).strip()
    # '*' je PGN značka "nedokončeno" — pro rozjetou hru rušivá, oříznem
    return text.rstrip(' *').rstrip()


def _pgn_result(state: GameState) -> str:
    """Spočítá PGN výsledek: '1-0', '0-1', '1/2-1/2' nebo '*' (nedokončeno)."""
    # Resign: vyhrává soupeř (z perspektivy hráče)
    if state.resigned:
        return "0-1" if state.player_color == chess.WHITE else "1-0"
    outcome = state.board.outcome()
    return outcome.result() if outcome else "*"


def pgn_full(state: GameState) -> str:
    """Kompletní PGN se Seven Tag Roster — pro stažení partie ze sidebaru.
    Tahy bere stejně jako pgn_text, ale přidává hlavičky a výsledek."""
    game = chess.pgn.Game.from_board(state.board)
    player_white = state.player_color == chess.WHITE
    # Seven Tag Roster v pořadí předepsaném PGN standardem
    game.headers["Event"] = "Casual Game"
    game.headers["Site"] = "localhost"
    game.headers["Date"] = datetime.date.today().strftime("%Y.%m.%d")
    game.headers["Round"] = "-"
    game.headers["White"] = "Player" if player_white else f"Stockfish (skill {state.skill})"
    game.headers["Black"] = f"Stockfish (skill {state.skill})" if player_white else "Player"
    game.headers["Result"] = _pgn_result(state)
    exp = chess.pgn.StringExporter(headers=True, comments=False, variations=False)
    return game.accept(exp)


# === HTML šablony ============================================================

def render_setup_page() -> str:
    """Setup formulář — volba stylu, tématu (pro 04), barvy, skill levelu."""
    style_options = ''.join(
        f'<option value="{k}">{label}</option>'
        for k, (label, _) in RENDERERS.items()
    )
    theme_options = ''.join(f'<option value="{t}">{t}</option>' for t in THEMES_04)
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Šachy — Setup</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; background: #f0f0f0; }}
        .card {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ margin-top: 0; }}
        label {{ display: block; margin: 15px 0 5px; font-weight: bold; }}
        select, input {{ width: 100%; padding: 8px; font-size: 14px; box-sizing: border-box; }}
        button {{ margin-top: 25px; width: 100%; padding: 12px; background: #4CAF50; color: white; border: 0; cursor: pointer; font-size: 16px; border-radius: 5px; }}
        button:hover {{ background: #45a049; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Nová hra</h1>
        <form method="POST" action="/start">
            <label for="style">Styl šachovnice:</label>
            <select name="style" id="style" onchange="document.getElementById('theme_row').style.display = this.value==='4' ? 'block' : 'none'">
                {style_options}
            </select>
            <div id="theme_row" style="display:none">
                <label for="theme">Téma (jen pro styl 4):</label>
                <select name="theme" id="theme">{theme_options}</select>
            </div>
            <label for="color">Hraješ za:</label>
            <select name="color" id="color">
                <option value="w">Bílý</option>
                <option value="b">Černý</option>
            </select>
            <label for="skill">Úroveň Stockfish (0-20):</label>
            <input type="number" name="skill" id="skill" value="5" min="0" max="20">
            <button type="submit">Začít hru</button>
        </form>
    </div>
</body>
</html>'''


# Vanilla JS klient — drag-and-drop nad SVG figurkami + text input form.
# Vložen do herní stránky jako jeden velký <script> blok.
DRAG_JS = r'''
let dragState = null;
let uiLocked = false;  // brání odeslání druhého tahu, dokud první nedoběhne

async function sendMove(payload) {
    if (uiLocked) return;
    uiLocked = true;
    try {
        const r = await fetch('/api/move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload),
        });
        const data = await r.json();
        if (!data.ok) {
            alert('Neplatný tah: ' + (data.error || '?'));
            return;
        }
        document.getElementById('board').innerHTML = data.board_html;
        document.getElementById('status').textContent = data.status;
        document.getElementById('pgn').textContent = data.pgn;
        attachDragHandlers();
        document.getElementById('move-input').focus();
    } finally {
        uiLocked = false;
    }
}

// Text input form — vždy přítomný, jediná možnost vstupu pro styl 5 (font HTML)
document.getElementById('move-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('move-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    sendMove({move: text});
});

// Drag-and-drop přes vlastní mousedown/move/up handlery (HTML5 native DnD
// na SVG <image> není napříč prohlížeči spolehlivé)
function attachDragHandlers() {
    const svg = document.querySelector('#board svg');
    if (!svg) return;  // styl 5 nemá SVG, jen font HTML — drag nedostupný
    svg.querySelectorAll('image').forEach(img => {
        img.addEventListener('mousedown', startDrag);
    });
}

// Převede SVG souřadnice (x, y v px) na 'e4' notaci.
// Render používá 15px margin a 45px velikost pole, řada 1 je dole.
function svgToSquare(x, y) {
    const file = Math.floor((x - 15) / 45);
    const rank = 7 - Math.floor((y - 15) / 45);
    if (file < 0 || file > 7 || rank < 0 || rank > 7) return null;
    return 'abcdefgh'[file] + (rank + 1);
}

function startDrag(e) {
    if (uiLocked) return;
    e.preventDefault();
    const img = e.currentTarget;
    const svg = img.ownerSVGElement;
    const origX = parseFloat(img.getAttribute('x'));
    const origY = parseFloat(img.getAttribute('y'));
    // Střed figury (padding 1-3px navíc, ale 22.5 je střed pole)
    const from = svgToSquare(origX + 22.5, origY + 22.5);
    if (!from) return;

    img.style.opacity = '0.5';
    dragState = {img, svg, from, origX, origY, startX: e.clientX, startY: e.clientY};
    document.addEventListener('mousemove', dragMove);
    document.addEventListener('mouseup', dragEnd);
}

function dragMove(e) {
    if (!dragState) return;
    // Pohyb figury v SVG souřadnicích — převedeme delta z client coords přes CTM
    const svg = dragState.svg;
    const ctm = svg.getScreenCTM();
    if (!ctm) return;
    const scale = ctm.a;  // SVG je čtvercové, scale x == scale y
    const dx = (e.clientX - dragState.startX) / scale;
    const dy = (e.clientY - dragState.startY) / scale;
    dragState.img.setAttribute('x', dragState.origX + dx);
    dragState.img.setAttribute('y', dragState.origY + dy);
}

function dragEnd(e) {
    if (!dragState) return;
    document.removeEventListener('mousemove', dragMove);
    document.removeEventListener('mouseup', dragEnd);

    // Spočítej cílové pole z pozice myši v SVG souřadnicích
    const svg = dragState.svg;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgPt = pt.matrixTransform(svg.getScreenCTM().inverse());
    const to = svgToSquare(svgPt.x, svgPt.y);

    dragState.img.style.opacity = '';
    const from = dragState.from;
    // Vrátit figuru na původní pozici (server pošle pravdivý render, ať si vyžádá)
    dragState.img.setAttribute('x', dragState.origX);
    dragState.img.setAttribute('y', dragState.origY);
    dragState = null;

    if (to && to !== from) {
        sendMove({from: from, to: to});
    }
}

// Vzdání hry — POST /api/resign po potvrzení. Po úspěchu disable tlačítka,
// ať uživatel nemůže vzdát podruhé (backend by stejně vrátil error).
async function resignGame() {
    if (uiLocked) return;
    if (!confirm('Opravdu vzdát partii?')) return;
    uiLocked = true;
    try {
        const r = await fetch('/api/resign', {method: 'POST'});
        const data = await r.json();
        if (!data.ok) {
            alert('Nelze vzdát: ' + (data.error || '?'));
            return;
        }
        document.getElementById('status').textContent = data.status;
        document.getElementById('pgn').textContent = data.pgn;
        document.getElementById('resign-btn').disabled = true;
    } finally {
        uiLocked = false;
    }
}

attachDragHandlers();
'''


def render_game_page(state: GameState) -> str:
    """Herní stránka — deska vlevo, sidebar (status, input, PGN, nová hra) vpravo."""
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Šachy proti Stockfish</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            margin: 0;
            padding: 20px;
            display: flex;
            gap: 30px;
            justify-content: center;
            min-height: 100vh;
            box-sizing: border-box;
        }}
        #board {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            user-select: none;  /* zabraň selekci textu při drag */
        }}
        .sidebar {{
            min-width: 250px;
            max-width: 400px;
        }}
        .status {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            font-size: 16px;
            font-weight: bold;
        }}
        .pgn {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            white-space: pre-wrap;
            margin-bottom: 10px;
            max-height: 300px;
            overflow-y: auto;
            font-size: 14px;
        }}
        form {{ margin-bottom: 10px; display: flex; gap: 5px; }}
        input[type="text"] {{ flex: 1; padding: 8px; font-size: 14px; }}
        form button {{ padding: 8px 15px; cursor: pointer; }}
        /* Sdílený styl pro akční tlačítka v dolní části sidebaru.
           Funguje pro <a> i <button> — proto reset border/font. */
        .action {{
            display: block;
            box-sizing: border-box;
            width: 100%;
            text-align: center;
            padding: 10px;
            margin-bottom: 8px;
            color: white;
            text-decoration: none;
            border: 0;
            border-radius: 5px;
            font-family: inherit;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
        }}
        .action.download {{ background: #2196F3; }}
        .action.download:hover {{ background: #1976D2; }}
        .action.resign {{ background: #ff9800; }}
        .action.resign:hover {{ background: #f57c00; }}
        .action.resign:disabled {{ background: #ccc; cursor: not-allowed; }}
        .action.new-game {{ background: #f44336; }}
        .action.new-game:hover {{ background: #d32f2f; }}
        #board svg image {{ cursor: grab; }}
    </style>
</head>
<body>
    <div id="board">{render_board_html(state)}</div>
    <div class="sidebar">
        <div class="status" id="status">{status_text(state)}</div>
        <form id="move-form">
            <input type="text" id="move-input" placeholder="Nf3 nebo e2e4" autofocus autocomplete="off">
            <button type="submit">Tah</button>
        </form>
        <div class="pgn" id="pgn">{pgn_text(state)}</div>
        <a class="action download" href="/api/pgn" download="game.pgn">Stáhnout PGN</a>
        <button class="action resign" id="resign-btn" onclick="resignGame()">Vzdát se</button>
        <a class="action new-game" href="/">Nová hra</a>
    </div>
    <script>{DRAG_JS}</script>
</body>
</html>'''


# === HTTP handler ============================================================

class Handler(http.server.BaseHTTPRequestHandler):
    """Routing: GET /, GET /game, POST /start, POST /api/move."""

    def _send(self, status: int, body, content_type: str = 'text/html; charset=utf-8') -> None:
        """Pošle response s body (str nebo bytes)."""
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        body_bytes = body.encode('utf-8') if isinstance(body, str) else body
        self.send_header('Content-Length', str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def _redirect(self, location: str) -> None:
        """303 See Other — správný status pro POST→GET redirect."""
        self.send_response(303)
        self.send_header('Location', location)
        self.end_headers()

    def _json(self, data: dict) -> None:
        self._send(200, json.dumps(data), 'application/json; charset=utf-8')

    def log_message(self, fmt, *args):
        # Tichý log — default by spamoval konzoli každým requestem
        pass

    # === GET ===
    def do_GET(self) -> None:
        if self.path == '/':
            self._send(200, render_setup_page())
        elif self.path == '/game':
            with _state.lock:
                if _state.engine is None:
                    # Nikdo nezačal hru — redirect na setup
                    self._redirect('/')
                    return
                self._send(200, render_game_page(_state))
        elif self.path == '/leipfont.ttf':
            # Font pro styl 5; read_bytes vyhodí FileNotFoundError → 404
            try:
                data = LEIPFONT_PATH.read_bytes()
            except FileNotFoundError:
                self._send(404, b'font not found', 'text/plain')
                return
            self._send(200, data, 'font/ttf')
        elif self.path == '/api/pgn':
            # Stažení partie. Funguje i pro rozjetou hru (Result="*") i po
            # skončení/rezignaci. Content-Disposition donutí browser stáhnout
            # soubor místo zobrazení.
            with _state.lock:
                if _state.engine is None:
                    self._send(404, b'no game', 'text/plain')
                    return
                pgn_bytes = pgn_full(_state).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-chess-pgn; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="game.pgn"')
            self.send_header('Content-Length', str(len(pgn_bytes)))
            self.end_headers()
            self.wfile.write(pgn_bytes)
        else:
            self._send(404, '<h1>404</h1>')

    # === POST ===
    def do_POST(self) -> None:
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else ''

        if self.path == '/start':
            form = urllib.parse.parse_qs(body)
            self._handle_start(form)
        elif self.path == '/api/move':
            payload = json.loads(body) if body else {}
            self._handle_move(payload)
        elif self.path == '/api/resign':
            self._handle_resign()
        else:
            self._send(404, '<h1>404</h1>')

    def _handle_start(self, form: dict) -> None:
        """Inicializace nové hry — restart engine, reset boardu."""
        with _state.lock:
            # Ukončit starý engine, pokud běží (předchozí hra)
            if _state.engine is not None:
                try:
                    _state.engine.quit()
                except Exception:
                    pass
                _state.engine = None

            _state.board = chess.Board()
            _state.resigned = False
            # parse_qs vrací list, bere se první hodnota; všechny mají defaulty
            _state.style = int(form.get('style', ['1'])[0])
            _state.theme = form.get('theme', ['uscf'])[0]
            _state.player_color = chess.WHITE if form.get('color', ['w'])[0] == 'w' else chess.BLACK
            _state.skill = int(form.get('skill', ['5'])[0])

            try:
                _state.engine = chess.engine.SimpleEngine.popen_uci('stockfish')
                _state.engine.configure({"Skill Level": _state.skill})
            except FileNotFoundError:
                self._send(500,
                    '<h1>Stockfish nenalezen v PATH</h1>'
                    '<p>Stáhni z <a href="https://stockfishchess.org/download/">stockfishchess.org</a> '
                    'a přidej do PATH.</p><p><a href="/">Zpět</a></p>')
                return

            # Hraje-li hráč černého, engine táhne první
            if _state.board.turn != _state.player_color:
                self._engine_move()

        self._redirect('/game')

    def _handle_move(self, payload: dict) -> None:
        """API endpoint pro tah — JSON in, JSON out."""
        with _state.lock:
            if _state.engine is None:
                self._json({'ok': False, 'error': 'Engine není připraven, začni novou hru'})
                return
            if _state.board.is_game_over() or _state.resigned:
                self._json({'ok': False, 'error': 'Hra už skončila'})
                return
            if _state.board.turn != _state.player_color:
                self._json({'ok': False, 'error': 'Není tvůj tah'})
                return

            # Dvě varianty payloadu: drag ({from,to}) nebo text ({move})
            try:
                if 'from' in payload and 'to' in payload:
                    move = self._parse_drag(_state.board, payload['from'], payload['to'])
                elif 'move' in payload:
                    move = self._parse_text(_state.board, payload['move'])
                else:
                    raise ValueError("Chybí 'from'+'to' nebo 'move'")
            except ValueError as e:
                self._json({'ok': False, 'error': str(e)})
                return

            _state.board.push(move)

            # Engine reakce, pokud hra ještě běží
            if not _state.board.is_game_over():
                self._engine_move()

            self._json({
                'ok': True,
                'board_html': render_board_html(_state),
                'pgn': pgn_text(_state),
                'status': status_text(_state),
                'game_over': _state.board.is_game_over(),
            })

    def _handle_resign(self) -> None:
        """Hráč vzdává partii — nastaví flag, vrátí update JSON jako /api/move."""
        with _state.lock:
            if _state.engine is None:
                self._json({'ok': False, 'error': 'Není rozjetá hra'})
                return
            if _state.board.is_game_over() or _state.resigned:
                self._json({'ok': False, 'error': 'Hra už skončila'})
                return
            _state.resigned = True
            self._json({
                'ok': True,
                'pgn': pgn_text(_state),
                'status': status_text(_state),
                'game_over': True,
            })

    def _engine_move(self) -> None:
        """Stockfish táhne. Volat výhradně pod _state.lock."""
        result = _state.engine.play(_state.board, chess.engine.Limit(time=ENGINE_THINK_TIME))
        _state.board.push(result.move)

    @staticmethod
    def _parse_drag(board: chess.Board, src: str, dst: str) -> chess.Move:
        """Drag pošle 'e2' a 'e4' — zkusíme UCI bez i s proměnou na dámu.
        UI neumí výběr proměny, default = dáma (nejčastější volba).
        """
        for promo_suffix in ['', 'q']:
            uci = src + dst + promo_suffix
            try:
                move = chess.Move.from_uci(uci)
                if move in board.legal_moves:
                    return move
            except ValueError:
                continue
        raise ValueError(f"Tah {src}-{dst} není platný")

    @staticmethod
    def _parse_text(board: chess.Board, move_str: str) -> chess.Move:
        """Text input: zkus SAN ('Nf3'), pak UCI ('g1f3', 'e7e8q')."""
        s = move_str.strip()
        try:
            return board.parse_san(s)
        except (ValueError, chess.IllegalMoveError,
                chess.InvalidMoveError, chess.AmbiguousMoveError):
            pass
        try:
            move = chess.Move.from_uci(s)
            if move in board.legal_moves:
                return move
        except (ValueError, chess.InvalidMoveError):
            pass
        raise ValueError(f"Tah '{s}' není platný (zkus SAN jako 'Nf3' nebo UCI jako 'g1f3')")


# === Entry point =============================================================

def main() -> None:
    server = http.server.HTTPServer(('localhost', PORT), Handler)
    url = f'http://localhost:{PORT}/'
    print(f"Server běží na {url}")
    print("Ctrl+C ukončí server.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer ukončen.")
    finally:
        # Vždy zavři engine subprocess, jinak by zůstal viset
        if _state.engine is not None:
            try:
                _state.engine.quit()
            except Exception:
                pass


if __name__ == '__main__':
    main()
