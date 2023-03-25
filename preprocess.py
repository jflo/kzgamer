import cv2


def preprocess(frame):
    frame_blurred = cv2.GaussianBlur(frame, (5,5), 0)
    frame_gray = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(frame_gray, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    return thresh
