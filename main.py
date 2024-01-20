import cv2
import cvzone
import numpy as np

# video = cv2.VideoCapture(1)
video = cv2.VideoCapture('testing_assets/Taśmociąg_bez kartki.mp4')
video.set(3, 640)
mouseX, mouseY = 0, 0
scale_square_area = 0


def search_for_pln(area):
    if 2.25 <= area <= 2.6:
        return 5

    if 2.65 <= area <= 2.8:
        return 2

    if 3 <= area <= 3.9:
        return 0.5

    return 0


def adjust_gamma(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)


def mouse_xy(event, x, y, flags, param):
    global mouseX, mouseY
    mouseX, mouseY = x, y


# def empty(a):
#     pass
#
#
# cv2.namedWindow("Settings")
# cv2.resizeWindow("Settings", 640, 240)
# cv2.createTrackbar("Threshold1", "Settings", 219, 255, empty)
# cv2.createTrackbar("Threshold2", "Settings", 233, 255, empty)

while True:
    success, image = video.read()
    # dla białego
    # image = cv2.convertScaleAbs(image, 2, 5)

    # dla ciemnego
    image = adjust_gamma(image, 0.4)

    pre_image = cv2.GaussianBlur(image, (5, 5), 3)

    # pre_image = cv2.Canny(pre_image, cv2.getTrackbarPos("Threshold1", "Settings"),
    #                       cv2.getTrackbarPos("Threshold2", "Settings"))
    pre_image = cv2.Canny(pre_image, 16, 255)

    kernel = np.ones((4, 4), np.uint8)
    pre_image = cv2.dilate(pre_image, kernel, iterations=1)

    pre_image = cv2.morphologyEx(pre_image, cv2.MORPH_CLOSE, kernel)

    contours_image, countors = cvzone.findContours(image, pre_image, minArea=20, sort=True)

    for c in countors:
        corners = cv2.approxPolyDP(c['cnt'], 0.02 * cv2.arcLength(c['cnt'], True), True)
        corner_amount = len(corners)

        varY, varX = c["center"]
        pre_image[varX - 5:varX + 5, varY - 5:varY + 5] = 255

        if (len(corners) == 4):
            scale_square_area = c['area']

        if c['area'] != 0 and corner_amount >= 8:
            res = search_for_pln(scale_square_area / c['area'])

            if res != 0:
               print(res)



    Stacked = cvzone.stackImages([contours_image, pre_image], 2, 1)
    cv2.imshow("Image", Stacked)
    cv2.setMouseCallback("Image", mouse_xy)
    cv2.setWindowTitle("Image", f"({mouseX}, {mouseY})")

    cv2.waitKey(1)
