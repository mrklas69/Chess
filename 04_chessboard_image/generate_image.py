import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import chessboard_image as cbi
sicilian_fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"
cbi.generate_image(sicilian_fen, "sicilian_defense_alpha.png", show_coordinates=True, size=400, theme_name="alpha")
cbi.generate_image(sicilian_fen, "sicilian_defense_wikipedia.png", show_coordinates=True, size=400, theme_name="wikipedia")
cbi.generate_image(sicilian_fen, "sicilian_defense_uscf.png", show_coordinates=True, size=400, theme_name="uscf")
cbi.generate_image(sicilian_fen, "sicilian_defense_wisteria.png", show_coordinates=True, size=400, theme_name="wisteria")
cbi.generate_image(sicilian_fen, "sicilian_defense_sakura.png", show_coordinates=True, size=400, theme_name="sakura")