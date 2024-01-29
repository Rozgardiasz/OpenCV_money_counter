import sys

import cv2
import cvzone
import numpy as np

import gui
from constants import *

video = cv2.VideoCapture('testing_assets/test_video1.mp4')
video.set(3, 640)

first_frame_flag = True
fps = default_fps
x1, y1, x2, y2 = 0, 0, 0, 0
scale_area = 0  # proporcje monet w stosunku do kwadracika dla skali

detected_coins = []  # lista w której zapisane są wszystkie zczytane przez taśmociąg monety bez powórzeń


# -----------------------------------------------


def search_for_pln(area):
    if pln5_l_limit <= area <= pln5_u_limit:
        return 5

    if pln2_l_limit <= area <= pln2_u_limit:
        return 2

    if pln1_l_limit <= area <= pln1_u_limit:
        return 1

    if pln05_l_limit <= area <= pln05_u_limit:
        return 0.5

    if pln02_l_limit <= area <= pln02_u_limit:
        return 0.2

    if pln01_l_limit <= area <= pln01_u_limit:
        return 0.1

    if pln005_l_limit <= area <= pln005_u_limit:
        return 0.05

    if pln002_l_limit <= area <= pln002_u_limit:
        return 0.02

    if pln001_l_limit <= area <= pln001_u_limit:
        return 0.01

    return 0


def add_object(coin_to_add):
    if len(detected_coins) == 0:
        print(coin_to_add)
        detected_coins.append(coin_to_add)
    else:
        add_flag = True
        for current_coin in detected_coins:
            if current_coin[0] == coin_to_add[0] and \
                    current_coin[2] - deviation_y <= coin_to_add[2] <= current_coin[2] + deviation_y \
                    and coin_to_add[1] >= current_coin[1] + belt_speed:
                add_flag = False
                break
        if add_flag:
            print(coin_to_add)
            detected_coins.append(coin_to_add)


def find_border(img_bin):
    most_right_white = None
    most_left_white = None
    most_up_white = None
    most_down_white = None

    for i in range(len(img_bin)):
        for j in range(len(img_bin[i])):
            if img_bin[i][j] == 255:
                if j < len(img_bin[i]) - 1 and img_bin[i][j + 1] == 0 and (
                        most_right_white is None or j > most_right_white[1]):
                    most_right_white = (i, j)
                if j > 0 and img_bin[i][j - 1] == 0 and (most_left_white is None or j < most_left_white[1]):
                    most_left_white = (i, j)
                if i > 0 and img_bin[i - 1][j] == 0 and (most_up_white is None or i < most_up_white[0]):
                    most_up_white = (i, j)
                if i < len(img_bin) - 1 and img_bin[i + 1][j] == 0 and (
                        most_down_white is None or i > most_down_white[0]):
                    most_down_white = (i, j)

    return most_right_white[0], most_down_white[1], most_left_white[0], most_up_white[1]


def find_black_pixels(img_bin):
    most_up_black = None
    most_down_black = None
    most_left_black = None
    most_right_black = None

    for i in range(len(img_bin)):
        for j in range(len(img_bin[i])):
            if img_bin[i][j] == 0:  # Sprawdzanie czarnego piksela
                if most_up_black is None or i < most_up_black[1]:
                    most_up_black = (i, j)
                if most_down_black is None or i > most_down_black[1]:
                    most_down_black = (i, j)
                if most_left_black is None or j < most_left_black[0]:
                    most_left_black = (i, j)
                if most_right_black is None or j > most_right_black[0]:
                    most_right_black = (i, j)

    return most_left_black[0], most_up_black[1], most_right_black[0], most_down_black[1]


def preprocessing(frame_to_pre):
    pre_image = cv2.GaussianBlur(frame_to_pre, (5, 5), 3)
    pre_image = cv2.Canny(pre_image, 16, 255)
    kernel = np.ones((4, 4), np.uint8)
    pre_image = cv2.dilate(pre_image, kernel, iterations=1)
    pre_image = cv2.morphologyEx(pre_image, cv2.MORPH_CLOSE, kernel)
    return pre_image


def preprocessContours(frame):
    contour, _ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    conFound = []
    for cnt in contour:
        area = cv2.contourArea(cnt)
        if area > 100:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            cx, cy = x + (w // 2), y + (h // 2)
            conFound.append({"cnt": cnt, "area": area, "center": [cx, cy]})
    return conFound


import cv2

from constants import *
import tkinter as tk
from PIL import Image, ImageTk


def change_fps():
    global fps
    if fps == default_fps:
        fps = slowed_fps
    else:
        fps = default_fps




root = tk.Tk()
root.title("Real-time Object Detection")
def on_close():
    # Tutaj umieść kod, który ma zostać wykonany przed zamknięciem okna
    print("Zamykanie okna...")
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)



# Utwórz Canvas do umieszczenia dwóch obrazków obok siebie
canvas = tk.Canvas(root, width=600, height=300)
canvas.pack(padx=10, pady=10)

# Utwórz etykiety dla klatek i pre-klatek
label_fps = tk.Label(root, text="FPS: ")
label_fps.pack(pady=10)
label_first_coins = tk.Label(root, text="First Coins: ")
label_first_coins.pack(pady=10)

# Dodaj przycisk Change FPS do zmiany prędkości fps
change_fps_button = tk.Button(root, text="Change FPS", command=change_fps)
change_fps_button.pack(pady=10)

# Dodaj przycisk Quit do zamknięcia aplikacji
quit_button = tk.Button(root, text="Quit", command=root.destroy)
canvas.pack(padx=10, pady=10)


def print_gui(frame, pre_frame, detected_coins):
    # Konwertuj klatkę do formatu obsługiwanego przez tkinter
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_frame = Image.fromarray(frame_rgb)
    img_frame = ImageTk.PhotoImage(image=img_frame)

    # Konwertuj pre-klatkę do formatu obsługiwanego przez tkinter
    pre_frame_rgb = cv2.cvtColor(pre_frame, cv2.COLOR_BGR2RGB)
    img_preframe = Image.fromarray(pre_frame_rgb)
    img_preframe = ImageTk.PhotoImage(image=img_preframe)

    # Utwórz obrazki na Canvasie
    canvas.create_image(0, 0, anchor=tk.NW, image=img_frame)
    canvas.create_image(img_frame.width() + 10, 0, anchor=tk.NW, image=img_preframe)

    # Uaktualnij wartość fps
    label_fps.config(text=f"FPS: {fps}")

    # Uaktualnij wartość pierwszych monet
    first_coins_values = [coin[0] for coin in detected_coins]
    label_first_coins.config(text=f"First Coins: {first_coins_values}")

    # Uaktualnij GUI
    root.update_idletasks()
    root.update()


while True:
    success, frame = video.read()
    if not success:
        break
    if first_frame_flag:
        binary_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        retval, binary_frame = cv2.threshold(binary_frame, 90, 255, cv2.THRESH_BINARY)

        # x1, y1, x2, y2 = find_black_pixels(tresh_frame)
        # print(x1, y1, x2, y2)
        x1, y1, x2, y2 = find_border(binary_frame)
        print(x1, y1, x2, y2)
        scale_area = (x2 - x1) * (y2 - y1)
        print(scale_area)
        first_frame_flag = False

    frame = frame[x1:x2, y1:y2]
    pre_frame = preprocessing(frame)

    # initial contour processing

    for c in preprocessContours(pre_frame):
        corners = cv2.approxPolyDP(c['cnt'], 0.02 * cv2.arcLength(c['cnt'], True), True)
        corner_amount = len(corners)

        varY, varX = c["center"]
        pre_frame[varX - 5:varX + 5, varY - 5:varY + 5] = 255

        if corner_amount == 8:

            res = search_for_pln(scale_area / c['area'])
            if res != 0:
                # print(res, c['center'])
                coin = [res, c['center'][0], c['center'][1]]

                add_object(coin)

    delay = int(1000 / fps)
    print_gui(frame, pre_frame, detected_coins)

    cv2.waitKey(delay)

root.destroy()
