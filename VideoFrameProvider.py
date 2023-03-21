import cv2
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage


class VideoFrameProvider(QObject):
    new_frame = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.frame = None

    def set_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape[:2]

        # Set the scaling factor
        scale_factor = 0.5

        # Calculate the new dimensions of the image
        new_height = int(height * scale_factor)
        new_width = int(width * scale_factor)

        # Resize the image using cv2.resize
        resized_img = cv2.resize(gray, (new_width, new_height))
        self.frame = resized_img

    def overlay_info(self, dice, blobs, message):
        # Overlay blobs
        for b in blobs:
            pos = b.pt
            r = b.size / 2

            cv2.circle(self.frame, (int(pos[0]), int(pos[1])),
                       int(r), (255, 0, 0), 2)

        # Overlay dice number
        for d in dice:
            # Get textsize for text centering
            textsize = cv2.getTextSize(
                str(d[0]), cv2.FONT_HERSHEY_PLAIN, 3, 2)[0]

            cv2.putText(self.frame, str(d[0]),
                        (int(d[1] - textsize[0] / 2),
                         int(d[2] + textsize[1] / 2)),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

        messagePosition = (10,50)
        cv2.putText(self.frame, message, messagePosition, cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0),2)
        q_image = QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.new_frame.emit(pixmap)
