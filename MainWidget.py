import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, \
    QPushButton, QRadioButton, QTextEdit, QLabel, QSizePolicy, QSlider, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap, QImage
from KZGamer import KZGamerThread


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.kzgamer_thread = KZGamerThread(self)
        self.kzgamer_thread.vid_display.new_frame.connect(self.update_video_pane)
        self.kzgamer_thread.new_roll.connect(self.log_roll)
        self.kzgamer_thread.log.connect(self.log_message)
        self.button_grid = QWidget()
        self.button_layout = QGridLayout()
        self.init_ui()
        self.kzgamer_thread.start()
        

    def init_ui(self):
        self.setWindowTitle("KZGamer")

        main_layout = QVBoxLayout()
        # Video pane
        self.video_pane = QLabel()
        #self.video_pane.setFixedWidth(480)
        main_layout.addWidget(self.video_pane)
        # game log pane
        self.log_pane = QTextEdit()
        self.log_pane.setReadOnly(True)
        main_layout.addWidget(self.log_pane)

        # output of the last roll
        self.last_roll_display = QLabel()
        self.last_roll_display.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.last_roll_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.last_roll_display.setMaximumHeight(32) # Set the maximum height to 14 pixels
        self.last_roll_display.setStyleSheet("font-size: 28px") # Set the font size to 14

        main_layout.addWidget(self.last_roll_display)

         # Add the radio buttons for the mode input

        radio_button_size = "25px"
        radio_button_font_size = "18px"
        self.hit_damage_radio = QRadioButton("Hit/Damage")
        self.hit_damage_radio.setStyleSheet(f"QRadioButton::indicator {{ width: {radio_button_size}; height: {radio_button_size}; font-size: {radio_button_font_size}; }}")
        self.morale_radio = QRadioButton("Morale")
        self.morale_radio.setStyleSheet(f"QRadioButton::indicator {{ width: {radio_button_size}; height: {radio_button_size}; font-size: {radio_button_font_size}; }}")
        self.hit_damage_radio.toggled.connect(self.hit_damage_mode)
        self.morale_radio.toggled.connect(self.morale_mode)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.hit_damage_radio)
        mode_layout.addWidget(self.morale_radio)

        main_layout.addLayout(mode_layout)

        
        self.button_layout.setSpacing(0)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        button_size = 50

        button_font = QFont()
        button_font.setPixelSize(18)

        for i in range(0, 10):
            button = QPushButton(str(i+1))
            button.setObjectName(str(i+1))
            button.clicked.connect(self.button_click_handler)
            row = int(i/6)
            col = (i+6)%6
            button.setMinimumSize(button_size, button_size)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            button.setFont(button_font)
            self.button_layout.addWidget(button, row, col)

        
        self.button_grid.setLayout(self.button_layout)
        self.morale_radio.setChecked(True) # Set Hit/Damage mode as the default
        self.last_roll_display.setMaximumWidth(self.button_grid.width())
        main_layout.addWidget(self.button_grid)
        self.setLayout(main_layout)

    def button_click_handler(self):
        sender = self.sender()
        self.log_roll(f"hitting on {sender.text()}s")
        self.kzgamer_thread.target_selected(int(sender.text()))

    @pyqtSlot(QPixmap)
    def update_video_pane(self, pixmap):
        self.video_pane.setPixmap(pixmap)

    @pyqtSlot(object)
    def log_roll(self, message):

        log_message = "NOOP"
        if isinstance(message, list):
            color_to_log = message[1]
            log_message = message[0]
        else:
            log_message = message
            color_to_log = "#000000"

        self.last_roll_display.clear()
        self.last_roll_display.setStyleSheet(f"color: {color_to_log}; font-size: 28px")
        self.last_roll_display.setText(log_message)
        self.log_message(log_message)

    def log_message(self, message):
        self.log_pane.append(f"[{QtCore.QTime.currentTime().toString('hh:mm:ss')}] {message}")

    def hit_damage_mode(self, checked):
        if checked:
            self.log_roll("rolling Hit/Damage")
            for i in range(1, 11):
                button = self.button_grid.findChild(QPushButton, str(i))
                if i <= 6:
                    button.setEnabled(True)
                else:
                    button.setEnabled(False)
            self.kzgamer_thread.mode_selected("Hit/Damage")
            
    def morale_mode(self, checked):
        if checked:
            self.log_roll("rolling Morale")
            for i in range(1, 11):
                button = self.button_grid.findChild(QPushButton, str(i))
                button.setEnabled(True)
            self.kzgamer_thread.mode_selected("Morale")

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

