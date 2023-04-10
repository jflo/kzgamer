import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, \
    QPushButton, QTextEdit, QLabel, QSizePolicy, QSlider, QHBoxLayout
from PyQt5.QtGui import QFont
from KZGamer import KZGamerThread


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.kzgamer_thread = KZGamerThread(self)
        self.kzgamer_thread.new_roll.connect(self.log_roll)
        self.init_ui()
        self.kzgamer_thread.start()

    def init_ui(self):
        self.setWindowTitle("KZGamer")

        main_layout = QVBoxLayout()

        # game log pane
        self.log_pane = QTextEdit()
        self.log_pane.setReadOnly(True)
        main_layout.addWidget(self.log_pane)

        # output of the last roll
        self.last_roll_display = QLabel()
        self.last_roll_display.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.last_roll_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.last_roll_display.setMaximumHeight(14) # Set the maximum height to 14 pixels
        self.last_roll_display.setStyleSheet("font-size: 14px") # Set the font size to 14

        main_layout.addWidget(self.last_roll_display)

        # Slider for input control
        self.mode_slider = QSlider(QtCore.Qt.Horizontal)
        self.mode_slider.setMinimum(0)
        self.mode_slider.setMaximum(1)
        self.mode_slider.setTickInterval(1)
        self.mode_slider.setValue(1)

        # Labels for slider
        slider_labels_layout = QHBoxLayout()
        self.hit_label = QLabel("Hit/Damage")
        self.hit_label.setAlignment(QtCore.Qt.AlignRight)
        self.morale_label = QLabel("Morale")
        self.morale_label.setAlignment(QtCore.Qt.AlignLeft)

        slider_labels_layout.addWidget(self.hit_label)
        slider_labels_layout.addWidget(self.mode_slider)
        slider_labels_layout.addWidget(self.morale_label)
        self.last_roll_display.setText("Ready for rollin")

        main_layout.addLayout(slider_labels_layout)

        button_layout = QGridLayout()
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_size = 50

        for i in range(0, 12):
            button = QPushButton(str(i+1))
            button.clicked.connect(self.button_click_handler)
            row = int(i/6)
            col = (i+6)%6
            button.setMinimumSize(button_size, button_size)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            button_layout.addWidget(button, row, col)

        button_grid = QWidget()
        button_grid.setLayout(button_layout)
        self.mode_slider.setFixedWidth(int(button_grid.width()/3))
        self.mode_slider.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        main_layout.addWidget(button_grid)
        self.setLayout(main_layout)

        self.mode_slider.sliderReleased.connect(self.slider_released_handler)

    def button_click_handler(self):
        sender = self.sender()
        self.log_pane.append(f"hitting on {sender.text()}s")
        self.kzgamer_thread.target_selected(int(sender.text()))

    @pyqtSlot(object)
    def log_roll(self, message):
        self.last_roll_display.clear()
        self.last_roll_display.setText(message)
        self.log_pane.append(f"[{QtCore.QTime.currentTime().toString('hh:mm:ss')}] {message}")

    def slider_released_handler(self):
        if self.mode_slider.value() == 0:
            self.hit_label.setStyleSheet("font-weight: bold")
            self.morale_label.setStyleSheet("")
            self.log_pane.append("Setting Hit/Damage mode")
            for i in range(1, 13):
                button = self.findChild(QPushButton, str(i))
                if i <= 6:
                    button.setEnabled(True)
                else:
                    button.setEnabled(False)
            self.kzgamer_thread.mode_selected("Hit/Damage")
        else:
            self.morale_label.setStyleSheet("font-weight: bold")
            self.hit_label.setStyleSheet("")
            self.log_pane.append("Setting Morale mode")
            for i in range(1, 13):
                button = self.findChild(QPushButton, str(i))
                button.setEnabled(True)
            self.kzgamer_thread.mode_selected("Morale")

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

