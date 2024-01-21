import cv2
import cvzone
import numpy as np

# współrzędne kursora
mouse_x, mouse_y = 0, 0

# video = cv2.VideoCapture(1)
video = cv2.VideoCapture('testing_assets/Taśmociąg_bez kartki.mp4')
video.set(3, 640)

frame_number = 0
belt_speed = 0  # offset przesunięć współrzędnej x obiektów na taśmociągu pomiędzy klatkami
deviation_y = 3  # dopuszczalny odchył pomiędzy współrzędną y tego samego obiektu w różnych klatkach (możemy umieścić telefon krzywo i wtedy potencjalnie szły by lekko na ukos)
detected_objects_per_frame = {}  # słownik składający się z numeru klatki i listy wykrytej w niej obiektów (samych monet)
all_detected_objects = []  # lista w której zapisane są wszystkie zczytane przez taśmociąg monety bez powórzeń

# proporcje monet w stosunku do kwadracika dla skali
scale_square_area = 0
# zlotowki -------------------------------------
pln5_u_limit = 2.6
pln5_l_limit = 2.25

pln2_u_limit = 3
pln2_l_limit = 2.65

pln1_u_limit = 2.7
pln1_l_limit = 2.55

# grosze >10
pln05_u_limit = 3.45
pln05_l_limit = 3.2

pln02_u_limit = 4.4
pln02_l_limit = 4.2

pln01_u_limit = 5.45
pln01_l_limit = 5

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
            if object1['center'][1] - deviation_y <= object2['center'][1] <= object1['center'][1] + deviation_y and object2['center'][0] > object1['center'][0] + belt_speed:
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


# def empty(a):
#     pass
# cv2.namedWindow("Settings")
# cv2.resizeWindow("Settings", 640, 240)
# cv2.createTrackbar("Threshold1", "Settings", 219, 255, empty)
# cv2.createTrackbar("Threshold2", "Settings", 233, 255, empty)

def preprocessing(frame):
    # # dla białego
    # frame = cv2.convertScaleAbs(frame, 2, 5)
    # dla ciemnego
    frame = adjust_gamma(frame, 0.4)
    pre_image = cv2.GaussianBlur(frame, (5, 5), 3)
    # pre_image = cv2.Canny(pre_image, cv2.getTrackbarPos("Threshold1", "Settings"),
    #                       cv2.getTrackbarPos("Threshold2", "Settings"))
    pre_image = cv2.Canny(pre_image, 16, 255)
    kernel = np.ones((4, 4), np.uint8)
    pre_image = cv2.dilate(pre_image, kernel, iterations=1)
    pre_image = cv2.morphologyEx(pre_image, cv2.MORPH_CLOSE, kernel)
    return pre_image


while True:
    success, frame = video.read()
    detected_objects_per_frame[frame_number] = []

    pre_image = preprocessing(frame)
    contours_image, countors = cvzone.findContours(frame, pre_image, minArea=20, sort=True)

    for c in countors:
        corners = cv2.approxPolyDP(c['cnt'], 0.02 * cv2.arcLength(c['cnt'], True), True)
        corner_amount = len(corners)

        varY, varX = c["center"]
        pre_image[varX - 5:varX + 5, varY - 5:varY + 5] = 255

        if len(corners) == 4:
            scale_square_area = c['area']

        if c['area'] != 0 and corner_amount >= 8:
            res = search_for_pln(scale_square_area / c['area'])
            if res != 0:
                detected_objects_per_frame[frame_number].append(c) #dodanie monety do listy odpowiadającej aktualnej klatce

    if len(detected_objects_per_frame) > 2:  # usuwanie list z poprzednich klatek (do porównania potrzebne są tylko dwie)
        keys_to_remove = list(detected_objects_per_frame.keys())[:-2]
        for key in keys_to_remove:
            detected_objects_per_frame.pop(key)

    if len(detected_objects_per_frame) > 1: #usuwanie powtórzonych elementów, a następnie dodawanie nowych do zbiorczej listy
        if frame_number == 1:
            # print("1:",len(all_detected_objects))
            # print("2:",len(detected_objects_per_frame[1]))
            detected_objects_per_frame[1] = remove_same_objects(detected_objects_per_frame[0], detected_objects_per_frame[1])
            # print("3:",len(detected_objects_per_frame[1]))
            all_detected_objects.extend(detected_objects_per_frame[0])
            # print("4:", len(all_detected_objects))

        if frame_number == 2:
            # print("1:",len(all_detected_objects))
            # print("2:",len(detected_objects_per_frame[2]))
            detected_objects_per_frame[2] = remove_same_objects(detected_objects_per_frame[1], detected_objects_per_frame[2])
            # print("3:",len(detected_objects_per_frame[2]))
            all_detected_objects.extend(detected_objects_per_frame[1])
            # print("4:", len(all_detected_objects))

        if frame_number == 0:
            # print("1:",len(all_detected_objects))
            # print("2:",len(detected_objects_per_frame[0]))
            detected_objects_per_frame[0] = remove_same_objects(detected_objects_per_frame[2], detected_objects_per_frame[0])
            # print("3:",len(detected_objects_per_frame[0]))
            all_detected_objects.extend(detected_objects_per_frame[2])
            # print("4:", len(all_detected_objects))




    frame_number += 1
    if frame_number > 2:  # jest to tutaj po to żeby nie przekroczyć maksymalnej wartości
        frame_number = 0

    Stacked = cvzone.stackImages([contours_image, pre_image], 2, 1)
    cv2.imshow("Image", Stacked)

    # ustawienie aktualnych współrzędnych w tytule w celu lepszego debuggowania
    cv2.setMouseCallback("Image", mouse_xy)
    cv2.setWindowTitle("Image", f"({mouse_x}, {mouse_y})")

    print(len(all_detected_objects))
    cv2.waitKey(1)

