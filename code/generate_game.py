#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Скрипт для отображения шахматного дуатлона на основе партий в шахматы и го.
Детальное описание: nevmenandr.github.io/duathlon

'''


import os
import sys
import chess.pgn
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
from sente import sgf

LINES = {str(x): x - 1 for x in range(1, 10)}

PIECES = {
    "r": "♜b",
    "n": "♞b",
    "b": "♗b",
    "q": "♛b",
    "k": "♚b",
    "p": "♙b",
    "R": "♜w",
    "N": "♞w",
    "B": "♗w",
    "Q": "♛w",
    "K": "♚w",
    "P": "♙w",
}

COLORS = {"b": (0, 0, 0), "w": (255, 255, 255)}

cell_size = 60
size = 8 * cell_size + cell_size * 2
font2_size = 24

font = font_manager.FontProperties(family="sans-serif", weight="normal")
file = font_manager.findfont(font)
font = ImageFont.truetype(file, 54, encoding="UTF-8")
font2 = ImageFont.truetype(file, font2_size, encoding="UTF-8")


def catch_pieces(board):
    picture = []
    board = str(board)
    board = board.replace(" ", "")
    board = board.replace("\n", "")
    for (i, cell) in enumerate(board):
        if cell not in PIECES:
            continue
        line = i // 8  # + 1
        row = i - line * 8
        picture.append((PIECES[cell], line, row))
    return picture


def chess_parsing(game):
    chess_game = []
    board = game.board()
    chess_game.append(catch_pieces(board))
    for move in game.mainline_moves():
        board.push(move)
        chess_game.append(catch_pieces(board))
    return chess_game


def picture_move(num, move, target_dir, go_game=""):
    img = Image.new("RGB", (size, size), (255, 186, 82))
    draw = ImageDraw.Draw(img)
    line = 0
    for line in range(8):
        for x in range(8):
            if line % 2 == 0:
                if x % 2 != 0:
                    draw.rectangle(
                        (
                            x * cell_size + cell_size,
                            line * cell_size + cell_size,
                            x * cell_size + cell_size * 2,
                            line * cell_size + cell_size * 2,
                        ),
                        fill=(112, 8, 8),
                    )
            else:
                if x % 2 == 0:
                    draw.rectangle(
                        (
                            x * cell_size + cell_size,
                            line * cell_size + cell_size,
                            x * cell_size + cell_size * 2,
                            line * cell_size + cell_size * 2,
                        ),
                        fill=(112, 8, 8),
                    )

    draw.line(
        (cell_size, cell_size, cell_size * 9, cell_size), fill=(112, 8, 8), width=1
    )
    draw.line(
        (cell_size * 9, cell_size, cell_size * 9, cell_size * 9),
        fill=(112, 8, 8),
        width=1,
    )
    draw.line(
        (cell_size * 9, cell_size * 9, cell_size, cell_size * 9),
        fill=(112, 8, 8),
        width=1,
    )
    draw.line(
        (cell_size, cell_size * 9, cell_size, cell_size), fill=(112, 8, 8), width=1
    )

    for i in range(3, 8, 2):
        for j in range(3, 8, 2):
            draw.text(
                (cell_size * i - 13, cell_size * j - 23), "*", (0, 0, 0), font=font
            )

    draw.line((0, 0, size, 0), fill=(236, 168, 37), width=30)
    draw.line((size, 0, size, size), fill=(236, 168, 37), width=30)
    draw.line((size, size, 0, size), fill=(236, 168, 37), width=30)
    draw.line((0, size, 0, 0), fill=(236, 168, 37), width=30)

    for x in range(8):
        draw.text(
            (cell_size * (x + 1) + font2_size, cell_size * 9 + 5),
            chr(x + 65),
            (112, 8, 8),
            font=font2,
        )

    for p in move:
        piece = p[0][0]
        color = p[0][1]
        line = p[1]
        row = p[2]
        draw.text(
            (cell_size + cell_size * row + 6, cell_size + cell_size * line),
            piece,
            COLORS[color],
            font=font,
        )

    if go_game:
        for stone in go_game:
            draw.text(
                (cell_size * stone[1] + 37, cell_size * stone[0] + 30),
                "⚫",
                COLORS[stone[2]],
                font=font,
            )

    str_num = str(num)
    nulls = 3 - len(str_num)

    img.save(os.path.join(target_dir, "{}{}.png".format("0" * nulls, num)))


def stones_detect(game):
    stones = []
    ln = 0
    rw = 0
    for x in game:
        if x in LINES:
            ln = LINES[x]
            rw = 0
        elif x == "A":
            break
        elif x == "." or x == "*":
            rw += 1
        elif x == "⚫":
            rw += 1
            stones.append((ln, rw - 1, "b"))
        elif x == "⚪":
            rw += 1
            stones.append((ln, rw - 1, "w"))
    return stones


def game_go_diff(move, file):
    game = sgf.load(file)
    sequence = game.get_default_sequence()
    game.play_sequence(sequence[:move])
    str_game = str(game)
    str_game = str_game.replace(" ", "")
    return stones_detect(str_game)


def go_parsing(file):
    '''Как оказалось, не существует способа с помощью модуля sente однажды
открыть файл и затем получить из него ходы по отдельности. Пришлось открывать
файл столько раз, сколько сделано ходов'''
    
    go = sgf.load(file)
    sequence = go.get_default_sequence()
    game_length = len(sequence)
    game_states = []
    for move in range(1, game_length + 1):
        game_states.append(game_go_diff(move, file))
    return game_states


def main():
    '''Скрипт при запуске принимает на вход три аргумента: файл PGN,
файл SGF и директория, в которую будут записываться картинки с изображением
доски после каждого хода.
Если аргументы не указаны, берутся значения по умолчанию. 

'''
    if len(sys.argv) == 4:
        pgn_file = sys.argv[1]
        sgf_file = sys.argv[2]
        target_dir = sys.argv[3]
    else:
        pgn_file = "1.pgn"
        sgf_file = "1.sgf"
        target_dir = "chess-gif"
    pgn = open(pgn_file)
    game = chess.pgn.read_game(pgn)
    chess_game = chess_parsing(game)
    go_game = go_parsing(sgf_file)

    if len(chess_game) - len(go_game) > 0:
        chess_game = chess_game[: len(go_game) + 1]
    elif len(go_game) - len(chess_game) > 0:
        go_game = go_game[: len(chess_game) + 1]

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    ii = 0
    for i, move in enumerate(chess_game):
        if not i:
            picture_move(i, move, target_dir)
        else:
            ii += 1
            if i == 1:
                picture_move(ii, move, target_dir)
            else:
                picture_move(ii, move, target_dir, go_game=go_game[i - 2])
            ii += 1
            picture_move(ii, move, target_dir, go_game=go_game[i - 1])


if __name__ == "__main__":
    main()
