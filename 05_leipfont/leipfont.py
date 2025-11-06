#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Šachový diagram s LEIPFONT - HTML verze.
"""

import os
import webbrowser

def generate_html_board():
    # Mapování znaků Chess Leipzig
    pieces_position = "rnbqkbnr" + "pppppppp" + "........" + "........" + "........" + "........" + "PPPPPPPP" + "RNBQKBNR"
    
    # Mapování znaků figur
    pieces_char = {
        # Světlá pole
        ('R',0): 0x72, ('N',0): 0x6E, ('B',0): 0x62,
        ('Q',0): 0x71, ('K',0): 0x6B, ('P',0): 0x70,
        ('r',0): 0x74, ('n',0): 0x6D, ('b',0): 0x76,
        ('q',0): 0x77, ('k',0): 0x6C, ('p',0): 0x6F,
        ('.',0): 0x2A,
        # Tmavá pole
        ('R',1): 0x52, ('N',1): 0x4E, ('B',1): 0x42,
        ('Q',1): 0x51, ('K',1): 0x4B, ('P',1): 0x50,
        ('r',1): 0x54, ('n',1): 0x4D, ('b',1): 0x56,
        ('q',1): 0x57, ('k',1): 0x4C, ('p',1): 0x4F,
        ('.',1): 0x2B,         
    }
    
    # Okraje šachovnice
    corner_top_left = 0x31
    border_horizontal = 0x32    
    corner_top_right = 0x33
    border_vertical = 0x35
    corner_bottom_left = 0x37
    corner_bottom_right = 0x39
    
    # Souřadnice polí (a-h, 1-8) - obsahují již border
    files_with_top_border = [x for x in range(0xC8, 0xD0)] # a-h
    rows_with_right_border = [x for x in range(0xC0, 0xC8)] # 1-8
    
    # Vytvoření HTML
    html = """<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Šachový diagram</title>
    <style>
        @font-face {
            font-family: 'ChessLeipzig';
            src: local('LEIPFONT'),
                 url('file:///C:/Windows/Fonts/LEIPFONT.TTF') format('truetype');
        }
        
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        
        .board-container {
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .board {
            font-family: 'ChessLeipzig', monospace;
            font-size: 48px;
            line-height: 1.0;
            white-space: pre;
        }
    </style>
</head>
<body>
    <div class="board-container">
        <div class="board">"""
    
    # Horní okraj
    html += chr(corner_top_left)
    for _ in range(8):
        html += chr(border_horizontal)
    html += chr(corner_top_right) + "\n"
    
    # Generování šachovnice s čísly řad vlevo (již obsahují levý border)
    idx = 0
    for row in range(8):
        rank = 8 - row  # 8, 7, 6, ..., 1
        
        # Číslo řady (obsahuje levý border)
        html += chr(rows_with_right_border[rank - 1])
        
        # Pole šachovnice
        for col in range(8):
            piece = pieces_position[idx]
            is_light = (row + col) % 2 == 1
            square_type = 0 if is_light else 1
            
            char_code = pieces_char.get((piece, square_type), 0x3F)
            html += chr(char_code)
            idx += 1
        
        # Pravý okraj
        html += chr(border_vertical)
        html += "\n"
    
    # Dolní okraj
    html += chr(corner_bottom_left)
    for file_char in files_with_top_border:
        html += chr(file_char)
    html += chr(corner_bottom_right) + "\n"
    
    html += """</div>
    </div>
</body>
</html>"""
    
    return html


def main():
    html_content = generate_html_board()
    
    output_file = "leipzig.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    abs_path = os.path.abspath(output_file)
    
    print(f"✅ HTML soubor vytvořen: {output_file}")
    print(f"Cesta: {abs_path}")
    
    try:
        webbrowser.open('file://' + abs_path)
        print("🌐 Otevírám v prohlížeči...")
    except:
        print("Otevřete soubor ručně v prohlížeči.")


if __name__ == "__main__":
    main()