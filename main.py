import random
import time
import threading
import tkinter as tk
from tkinter import simpledialog

import pygame
import sys

from square import Square
from communcation_socket import CommuncationSocket

BIG_LEFT_OFFSET = 200
WORD_LEN = 5
WIDTH, HEIGHT = 810, 810
FPS = 60
SMALL_SQUARE_X_OFFSET = 80
SMALL_SQUARE_Y_OFFSET = 580
BLACK = (43, 43, 43)
WHITE = (255, 255, 255)
GREEN = (84, 139, 76)


def show_input_dialog():
    user_input = simpledialog.askstring("Username", "Enter username:")
    return user_input


def parse_states(msg):
    status_per_letter = [i["status"] for i in msg["letters"]]
    res = []
    for i in status_per_letter:
        if i == "correct":
            res.append("green")
        elif i == "amarillo":
            res.append("yellow")
        elif i == "incorrecto":
            res.append("gray")
    return res


def parse_gamestate(msg, font, user):
    initial_y = 20
    res = []

    # Initial iteration for the title
    text = f"SCORES"
    text_object = font.render(text, True, WHITE)  # White color
    text_rect = text_object.get_rect(topleft=(10, initial_y))

    res.append((text_object, text_rect))

    for index, line in enumerate(msg):
        color = GREEN if user == line['name'] else WHITE
        text = f"{line['name']}: {line['score']}"
        text_object = font.render(text, True, color)
        text_rect = text_object.get_rect(topleft=(10, 30 * (index + 1) + initial_y))
        res.append((text_object, text_rect))

    return res


def clear_squares(squares, small_squares):
    for i in squares:
        i.letter = " "
        i.color = "blank"

    for i in small_squares:
        i.color = "blank"


def constant_read(comm_socket):
    while True:
        comm_socket.receive()
        print("leyo!")


def restart():
    current_try = 0
    this_word_index = 0


def black_overlay():
    """
    Esto esta aca pa no perderlo pq asi ta feo
    """
    # Create a semi-transparent black surface
    black_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    black_surface.fill((0, 0, 0, 128))  # 128 for R, G, B, and alpha (transparency)

    return black_surface
    # Blit the black surface onto the main screen


def main():
    # Before pygame even launches
    username = show_input_dialog()

    # Initialize Pygame
    pygame.init()
    comm = CommuncationSocket("127.0.0.1", 8080)
    comm.connect()
    threading.Thread(target=constant_read, args=[comm]).start()
    comm.send("Register", username)

    # Constants
    font = pygame.font.Font(None, 36)  # You can adjust the font size

    # Initialize screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WARDOL")
    clock = pygame.time.Clock()

    # initialize words
    with open("palabras.txt", "r") as f:
        palabras = f.read().split("\n")

    allowed_words = [i.upper() for i in palabras]

    # initialize squares
    squares = [Square(x, y, "blank", big_left_offset=BIG_LEFT_OFFSET) for y in range(6) for x in range(5)]

    # initialize small squares (the keyboard below)
    small_squares = []
    small_squares.extend(
        [Square(x, 0, "blank", SMALL_SQUARE_X_OFFSET, SMALL_SQUARE_Y_OFFSET, 40, 60, BIG_LEFT_OFFSET) for x in
         range(10)])
    small_squares.extend(
        [Square(x, 1, "blank", SMALL_SQUARE_X_OFFSET + 20, SMALL_SQUARE_Y_OFFSET + 2, 40, 60, BIG_LEFT_OFFSET) for x in
         range(9)])
    small_squares.extend(
        [Square(x, 2, "blank", SMALL_SQUARE_X_OFFSET + 66, SMALL_SQUARE_Y_OFFSET + 4, 40, 60, BIG_LEFT_OFFSET) for x in
         range(7)])

    # put a letter to every small square, and create a lookup dict
    small_squares_by_letter = {}
    for sq, let in zip(small_squares, "QWERTYUIOPASDFGHJKLZXCVBNM"):
        sq.letter = let
        small_squares_by_letter[let] = sq

    current_try = 0
    this_word_index = 0
    reset = False

    # game loop
    while True:
        if reset:
            time.sleep(3)
            current_try = 0
            this_word_index = 0
            clear_squares(squares, small_squares)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:

                # if word isn't fully typed then type letter on the same row
                if pygame.K_a <= event.key <= pygame.K_z:
                    if this_word_index < WORD_LEN:
                        squares[current_try * WORD_LEN + this_word_index].letter = chr(event.key).upper()
                        this_word_index += 1

                # if word isn't empty then erase one position
                if event.key == pygame.K_BACKSPACE:
                    if this_word_index > 0:
                        this_word_index -= 1
                        squares[current_try * WORD_LEN + this_word_index].letter = " "

                # if word is fully typed then send it to the server
                if event.key == pygame.K_RETURN:
                    if this_word_index == WORD_LEN:

                        first_index = current_try * WORD_LEN
                        word = "".join([squares[i].letter for i in range(first_index, first_index + WORD_LEN)])

                        if word in allowed_words:
                            this_word_index = 0
                            current_try += 1

                            # Send to the server for processing
                            comm.send("Attempt", word.lower())

                            while True:  # wait for the response. It's ok to be blocking since it's just milliseconds
                                try:
                                    msg = comm.queue_responses.pop()
                                    break
                                except IndexError:
                                    pass

                            states = parse_states(msg)
                            for i in range(WORD_LEN):
                                # Paint the squares according to the received states
                                this_square = squares[first_index + i]
                                this_square.color = states[i]

                                small_squares_by_letter[this_square.letter].keep_max_color(states[i])

        # Clear the screen
        screen.fill(BLACK)

        # Draw squares
        for i in squares:
            if i.color == "blank":
                pygame.draw.rect(screen, i.rgb, i.pygame_object, width=1)
            else:
                pygame.draw.rect(screen, i.rgb, i.pygame_object)

            if i.letter:
                text = font.render(i.letter, True, (255, 255, 255))  # White color
                text_rect = text.get_rect(center=i.pygame_object.center)
                screen.blit(text, text_rect)

        # Draw small squares
        for i in small_squares:
            pygame.draw.rect(screen, i.rgb, i.pygame_object, border_radius=3)

            if i.letter:
                text = font.render(i.letter, True, WHITE)  # White color
                text_rect = text.get_rect(center=i.pygame_object.center)
                screen.blit(text, text_rect)

        # Draw gamestate

        for text_object, text_rect in parse_gamestate(comm.gamestate, font, username):
            screen.blit(text_object, text_rect)
            print(text_object, text_rect)

        # Separation line
        # pygame.draw.line(screen, WHITE, (250, 0), (250, HEIGHT), 1)

        # Overlay negro para ponerle cartelitos arriba
        if False:
            screen.blit(black_overlay(), (0, 0))

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        clock.tick(FPS)


if __name__ == "__main__":
    main()
