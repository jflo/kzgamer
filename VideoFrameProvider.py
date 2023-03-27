import cv2
from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage


class VideoFrameProvider(QObject):
    new_frame = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()

    def show_frame(self, frame):
        if len(frame.shape) == 3:
            output_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif len(frame.shape) == 2:
            output_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        else:
            output_frame = frame

        h, w, c = output_frame.shape
        qimg = QImage(output_frame.data, w, h, w*c, QImage.Format_RGB888)
        scaled = qimg.scaledToWidth(900)
        pixmap = QPixmap.fromImage(scaled)
        self.new_frame.emit(pixmap)

    def overlay_info(self, frame, dice, blobs, message):
        markup_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        # Overlay blobs
        for b in blobs:
            pos = b.pt
            r = b.size / 2

            cv2.circle(markup_frame, (int(pos[0]), int(pos[1])),
                       int(r), (255, 0, 0), 10)

        # Overlay dice number
        for d in dice:
            # Get textsize for text centering
            textsize = cv2.getTextSize(
                str(d[0]), cv2.FONT_HERSHEY_PLAIN, 12, 2)[0]

            cv2.putText(markup_frame, str(d[0]),
                        (int(d[1] - textsize[0] / 2),
                         int(d[2] + textsize[1] / 2)),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 10)

        print(f"{message}, {len(dice)} dice on {len(blobs)} blobs")
        messagePosition = (250,250)
        cv2.putText(markup_frame, message, messagePosition, cv2.FONT_HERSHEY_PLAIN, 12, (255,0,0),10)

        self.show_frame(markup_frame)
        cv2.imwrite("frame.png", markup_frame)

