import cv2
import cvzone
import numpy as np

video = cv2.VideoCapture(0)
video.set(3, 640)
mouseX,mouseY = 0,0

def mouse_xy(event, x, y, flags, param):
    global mouseX,mouseY
    mouseX,mouseY = x,y

while True:
    success, image = video.read()

    pre_image = cv2.GaussianBlur(image, (5, 5), 3)
    pre_image = cv2.Canny(pre_image,64, 255)
    kernel = np.ones((4, 4), np.uint8)
    pre_image = cv2.dilate(pre_image, kernel, iterations=1)

    pre_image = cv2.morphologyEx(pre_image, cv2.MORPH_CLOSE, kernel)

    contours_image, countors = cvzone.findContours(image, pre_image, minArea=20, sort=True)

    for c in countors:
        varY, varX = c["center"]
        pre_image[varX-5:varX+5, varY-5:varY+5] = 255

    Stacked = cvzone.stackImages([contours_image, pre_image], 2, 1)
    cv2.imshow("Image", Stacked)
    cv2.setMouseCallback("Image", mouse_xy)
    cv2.setWindowTitle("Image",f"({mouseX}, {mouseY})")

    cv2.waitKey(1)
