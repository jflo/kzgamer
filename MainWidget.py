import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QTextEdit, QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QFont
from KZGamer import KZGamerThread


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.kzgamer_thread = KZGamerThread(self)
        #if "--debug" in sys.argv:
        self.kzgamer_thread.vid_display.new_frame.connect(self.update_video_pane)
        self.kzgamer_thread.new_roll.connect(self.log_roll)
        self.init_ui()
        self.kzgamer_thread.start()

    def init_ui(self):
        self.setWindowTitle("KZGamer")

        main_layout = QVBoxLayout()
        # Video pane
        self.video_pane = QLabel()
        #self.video_pane.setFixedWidth(480)
        main_layout.addWidget(self.video_pane)

        # Text pane
        self.text_pane = QTextEdit()
        self.text_pane.setReadOnly(True)
        main_layout.addWidget(self.text_pane)

        button_layout = QGridLayout()
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_size = 50
        buton_font = QFont("Helvetica", 24)

        for i in range(1, 7):
            button = QPushButton(str(i))
            button.clicked.connect(self.button_click_handler)
            row = 0
            col = (i - 1)
            button.setMinimumSize(button_size, button_size)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            button_layout.addWidget(button, row, col)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def button_click_handler(self):
        sender = self.sender()
        self.text_pane.append(f"hitting on {sender.text()}s")
        self.kzgamer_thread.target_selected(int(sender.text()))

    @pyqtSlot(QPixmap)
    def update_video_pane(self, pixmap):
        self.video_pane.setPixmap(pixmap)

    @pyqtSlot(object)
    def log_roll(self, message):
        self.text_pane.append(message)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

