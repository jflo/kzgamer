import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QAction, QVBoxLayout, QTextEdit, QPushButton, QGridLayout, QMainWindow
from PyQt5.QtCore import QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QImage
try:
    import Queue as Queue
except:
    import queue as Queue


class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        self.setMinimumSize(image.size())
        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()


class MainWindow(QMainWindow):

    text_update = pyqtSignal(str)
    image_queue = Queue.Queue()     # Queue to hold images

    def __init__(self, parent=None):

        self.hitting_on = 4
        QMainWindow.__init__(self, parent)

        # Set up the user interface
        self.central = QWidget(self)
        self.setWindowTitle("Text Pane with Buttons")

        # Create a QVBoxLayout to organize the widgets vertically
        self.main_layout = QVBoxLayout()

        # Create the text pane for output
        self.text_pane = QTextEdit()
        self.text_pane.setReadOnly(True)
        self.disp = ImageWidget(self)
        self.main_layout.addWidget(self.disp)
        self.main_layout.addWidget(self.text_pane)


        # Create a QGridLayout to organize the buttons in a grid
        button_layout = QGridLayout()
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(0, 0, 0, 0)
        # Create buttons and add them to the grid layout
        for i in range(1, 7):
            button = QPushButton(str(i))
            button.clicked.connect(self.button_click_handler)
            row = (i - 1) // 3
            col = (i - 1) % 3
            button_layout.addWidget(button, row, col)

        # Add the button layout to the main layout
        self.main_layout.addLayout(button_layout)

        # Set the main layout for the main window

        self.central.setLayout(self.main_layout)
        self.setCentralWidget(self.central)

        self.mainMenu = self.menuBar()      # Menu bar
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(exitAction)

    def queue_image(self, frame):
        if frame is not None:
            self.image_queue.put(frame)
        else:
            print("frame empty")

    def show_image(self, imageq, display, scale):
        if not imageq.empty():
            image = imageq.get()
            if image is not None and len(image) > 0:
                #img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.display_image(image, display, scale)

    # Display an image, reduce size if required
    def display_image(self, img, display, scale=1):
        disp_size = img.shape[1]//scale, img.shape[0]//scale
        disp_bpl = disp_size[0] * 3
        if scale > 1:
            img = cv2.resize(img, disp_size,
                             interpolation=cv2.INTER_CUBIC)
        qimg = QImage(img.data, disp_size[0], disp_size[1],
                      disp_bpl, QImage.Format_RGB888)
        display.setImage(qimg)

    def button_click_handler(self):
        # Get the sender (button) and append its text to the text pane
        sender = self.sender()
        self.hitting_on = int(sender.text())
        self.text_pane.append(f"Hitting on {sender.text()}s")

    def log_roll(self, hits, numDice, sixes, bits):
        self.text_pane.append(f"{hits} on {numDice} dice, {sixes} exploded - {bits} bits of entropy collected")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.setWindowTitle("KZGamer")
    sys.exit(app.exec_())