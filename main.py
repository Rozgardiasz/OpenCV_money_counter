import cv2
import numpy as np
import gui_module
from constants import *

gui = gui_module.GUI()
video = cv2.VideoCapture('testing_assets/video3.mp4')

video.set(3, 640)
first_frame_flag = True
x1, y1, x2, y2 = 0, 0, 0, 0
fps = default_fps
scale_area = 0  # proporcje monet w stosunku do kwadracika dla skali

detected_coins = []  # lista w której zapisane są wszystkie zczytane przez taśmociąg monety bez powórzeń


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


# Funkcja dodająca monety do listy, sprawdzając duplikaty i kierunek ruchu taśmociągu
def add_object(coin_to_add):
    if len(detected_coins) == 0:
        print(coin_to_add)
        detected_coins.append(coin_to_add)
    else:
        add_flag = True
        for current_coin in detected_coins:
            if current_coin[2] - deviation_y <= coin_to_add[2] <= current_coin[2] + deviation_y \
                    and coin_to_add[1] >= current_coin[1] + belt_speed and current_coin[0] == coin_to_add[0]:
                add_flag = False
                break
        if add_flag:
            print(coin_to_add)
            detected_coins.append(coin_to_add)


# Funkcja znajdująca współrzędne najbardziej oddalonych czarnych pikseli w pierwszej klatce
def find_black_pixels(img_bin):
    most_up_black = None
    most_down_black = None
    most_left_black = None
    most_right_black = None

    for i in range(len(img_bin)):
        for j in range(len(img_bin[i])):
            if img_bin[i][j] == 0:  # poszukiwanie czterech najbardziej oddalonych w każdym kierunku czarnych pikseli
                if most_up_black is None or i < most_up_black[1]:
                    most_up_black = (i, j)
                if most_down_black is None or i > most_down_black[1]:
                    most_down_black = (i, j)
                if most_left_black is None or j < most_left_black[0]:
                    most_left_black = (i, j)
                if most_right_black is None or j > most_right_black[0]:
                    most_right_black = (i, j)

    return most_left_black[0], most_up_black[1], most_right_black[0], most_down_black[1]


# Funkcja przetwarzająca klatkę przed detekcją konturów
def preprocessing(frame_to_pre):
    # Wygładza klatkę, aplikuje detekcję krawędzi, wykonuje dylatację i morfologiczne zamknięcie
    pre_image = cv2.GaussianBlur(frame_to_pre, (5, 5), 3)
    pre_image = cv2.Canny(pre_image, 16, 255)
    kernel = np.ones((4, 4), np.uint8)
    pre_image = cv2.dilate(pre_image, kernel, iterations=1)
    pre_image = cv2.morphologyEx(pre_image, cv2.MORPH_CLOSE, kernel)
    return pre_image


# Funkcja identyfikująca kontury i ich cechy
def preprocess_contours(frame_to_con):
    # Znajduje kontury w przetworzonej klatce, odrzuca małe kontury
    # Zwraca listę słowników zawierających informacje o konturach
    contour, _ = cv2.findContours(frame_to_con, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
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


while True:
    success, frame = video.read()
    if not success:
        break
    if first_frame_flag:
        binary_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        retval, binary_frame = cv2.threshold(binary_frame, 90, 255, cv2.THRESH_BINARY)

        x1, y1, x2, y2 = find_black_pixels(binary_frame)
        print(x1, y1, x2, y2)

        scale_area = (x2 - x1) * (y2 - y1)
        print(scale_area)
        first_frame_flag = False

    frame = frame[x1:x2, y1:y2]
    pre_frame = preprocessing(frame)

    for c in preprocess_contours(pre_frame):
        corners = cv2.approxPolyDP(c['cnt'], 0.02 * cv2.arcLength(c['cnt'], True), True)
        corner_amount = len(corners)

        varY, varX = c["center"]
        pre_frame[varX - 5:varX + 5, varY - 5:varY + 5] = 255

        if corner_amount == 8:

            res = search_for_pln(scale_area / c['area'])
            if res != 0:
                coin = [res, c['center'][0], c['center'][1]]

                add_object(coin)

    delay = int(1000 / gui.fps)
    gui.update_gui(frame, pre_frame, detected_coins)
    cv2.waitKey(delay)

gui.root.destroy()
