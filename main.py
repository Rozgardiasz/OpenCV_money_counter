import cv2
import cvzone
import numpy as np

# video = cv2.VideoCapture(1)
video = cv2.VideoCapture('testing_assets/otwor_v2.mp4')
video.set(3, 640)

# współrzędne kursora
mouse_x, mouse_y = 0, 0

frame_number = 0
belt_speed = 0  # offset przesunięć współrzędnej x obiektów na taśmociągu pomiędzy klatkami
fps = 10
deviation_y = 3  # dopuszczalny odchył pomiędzy współrzędną y tego samego obiektu w różnych klatkach (możemy umieścić telefon krzywo i wtedy potencjalnie szły by lekko na ukos)
detected_objects_per_frame = {}  # słownik składający się z numeru klatki i listy wykrytej w niej obiektów (samych monet)
all_detected_objects = []  # lista w której zapisane są wszystkie zczytane przez taśmociąg monety bez powórzeń


# proporcje monet w stosunku do kwadracika dla skali
scale_area = 0

# zlotowki -------------------------------------
pln5_u_limit = 0
pln5_l_limit = 0

pln2_u_limit = 18.020
pln2_l_limit = 17.786

pln1_u_limit = 0
pln1_l_limit = 0

# grosze >10
pln05_u_limit = 20.026
pln05_l_limit = 19.790

pln02_u_limit = 0
pln02_l_limit = 0

pln01_u_limit = 0
pln01_l_limit = 0

# grosze <10
pln005_u_limit = 0
pln005_l_limit = 0

pln002_u_limit = 0
pln002_l_limit = 0

pln001_u_limit = 0
pln001_l_limit = 0


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


def remove_same_objects(list1, list2):
    copy_list2 = []
    for object2 in list2:
        add_flag = True
        for object1 in list1:
            if object1['center'][1] - deviation_y <= object2['center'][1] <= object1['center'][1] + deviation_y and \
                    object2['center'][0] > object1['center'][0] + belt_speed:
                add_flag = False
                break

        if add_flag:
            copy_list2.append(object2)
    return copy_list2


def adjust_gamma(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)


# ustawienie aktualnych współrzędnych w tytule w celu lepszego debuggowania
def mouse_xy(event, x, y, flags, param):
    global mouse_x, mouse_y
    mouse_x, mouse_y = x, y


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


def preprocessing(frame):
    pre_image = cv2.GaussianBlur(frame, (5, 5), 3)
    pre_image = cv2.Canny(pre_image, 16, 255)
    kernel = np.ones((4, 4), np.uint8)
    pre_image = cv2.dilate(pre_image, kernel, iterations=1)
    pre_image = cv2.morphologyEx(pre_image, cv2.MORPH_CLOSE, kernel)
    return pre_image


first_frame_flag = True
x1, y1, x2, y2 = 0, 0, 0, 0

while True:
    success, frame = video.read()
    detected_objects_per_frame[frame_number] = []

    if first_frame_flag == True:
        tresh_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        retval, tresh_frame = cv2.threshold(tresh_frame, 90, 255, cv2.THRESH_BINARY)
        x1, y1, x2, y2 = find_border(tresh_frame)
        print(x1, y1, x2, y2)
        scale_area = (x2-x1) * (y2-y1)
        print(scale_area)
        first_frame_flag = False

    frame = frame[x1:x2, y1:y2]
    pre_frame = preprocessing(frame)

    contours_image, countours = cvzone.findContours(frame, pre_frame, minArea=20, sort=True)

    for c in countours:
        corners = cv2.approxPolyDP(c['cnt'], 0.02 * cv2.arcLength(c['cnt'], True), True)
        corner_amount = len(corners)

        varY, varX = c["center"]
        pre_frame[varX - 5:varX + 5, varY - 5:varY + 5] = 255

        if c['area'] != 0 and corner_amount == 8:



            res = search_for_pln(scale_area / c['area'])
            if res != 0:
                print(res)
                detected_objects_per_frame[frame_number].append(
                    c)  # dodanie monety do listy odpowiadającej aktualnej klatce

    if len(detected_objects_per_frame) > 2:  # usuwanie list z poprzednich klatek (do porównania potrzebne są tylko dwie)
        keys_to_remove = list(detected_objects_per_frame.keys())[:-2]
        for key in keys_to_remove:
            detected_objects_per_frame.pop(key)

    if len(detected_objects_per_frame) > 1:  # usuwanie powtórzonych elementów, a następnie dodawanie nowych do zbiorczej listy
        if frame_number == 1:
            # print("1:",len(all_detected_objects))
            # print("2:",len(detected_objects_per_frame[1]))
            detected_objects_per_frame[1] = remove_same_objects(detected_objects_per_frame[0],
                                                                detected_objects_per_frame[1])
            # print("3:",len(detected_objects_per_frame[1]))
            all_detected_objects.extend(detected_objects_per_frame[0])
            # print("4:", len(all_detected_objects))

        if frame_number == 2:
            # print("1:",len(all_detected_objects))
            # print("2:",len(detected_objects_per_frame[2]))
            detected_objects_per_frame[2] = remove_same_objects(detected_objects_per_frame[1],
                                                                detected_objects_per_frame[2])
            # print("3:",len(detected_objects_per_frame[2]))
            all_detected_objects.extend(detected_objects_per_frame[1])
            # print("4:", len(all_detected_objects))

        if frame_number == 0:
            # print("1:",len(all_detected_objects))
            # print("2:",len(detected_objects_per_frame[0]))
            detected_objects_per_frame[0] = remove_same_objects(detected_objects_per_frame[2],
                                                                detected_objects_per_frame[0])
            # print("3:",len(detected_objects_per_frame[0]))
            all_detected_objects.extend(detected_objects_per_frame[2])
            # print("4:", len(all_detected_objects))
            # Wprowadź opóźnienie na podstawie liczby klatek na sekundę

        delay = int(1000 / fps)

        # Oczekuj na klawisz "Tab", aby przełączyć między 30 i 60 FPS
        key = cv2.waitKeyEx(delay)
        if key == 9:  # Kod klawisza Tab
            if fps == 60:
                fps = 10
            else:
                fps = 60
            print("zmieniono fps na ",fps)
        # Wciśnięcie klawisza "Esc" kończy pętlę
        elif key == 27:
            break



    frame_number += 1
    if frame_number > 2:  # jest to tutaj po to żeby nie przekroczyć maksymalnej wartości
        frame_number = 0

    Stacked = cvzone.stackImages([contours_image, pre_frame], 2, 1)
    cv2.imshow("Image", Stacked)

    # ustawienie aktualnych współrzędnych w tytule w celu lepszego debuggowania
    cv2.setMouseCallback("Image", mouse_xy)
    cv2.setWindowTitle("Image", f"({mouse_x}, {mouse_y})")

    # print(len(all_detected_objects))
    cv2.waitKey(1)
