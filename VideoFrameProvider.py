import cv2
from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage


class VideoFrameProvider(QObject):
    new_frame = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()

    def overlay_info(self, frame, dice, blobs, message):
        markup_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        # Overlay blobs
        for b in blobs:
            pos = b.pt
            r = b.size / 2

            cv2.circle(markup_frame, (int(pos[0]), int(pos[1])),
                       int(r), (255, 0, 0), 2)

        # Overlay dice number
        for d in dice:
            # Get textsize for text centering
            textsize = cv2.getTextSize(
                str(d[0]), cv2.FONT_HERSHEY_PLAIN, 3, 2)[0]

            cv2.putText(markup_frame, str(d[0]),
                        (int(d[1] - textsize[0] / 2),
                         int(d[2] + textsize[1] / 2)),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

        messagePosition = (10,50)
        cv2.putText(markup_frame, message, messagePosition, cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0),2)

        h, w, c = markup_frame.shape
        converted = QImage(markup_frame.data, w, h, w*c, QImage.Format_RGB888)
        converted = converted.scaled(480, 480, 1)  # 1 keeps aspect ratio
        display_frame = QPixmap.fromImage(converted)

        self.new_frame.emit(display_frame)
        #q_image = QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QImage.Format_RGB888)
        #pixmap = QPixmap.fromImage(q_image)
        #self.new_frame.emit(pixmap)
