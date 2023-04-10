import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, \
    QPushButton, QRadioButton, QTextEdit, QLabel, QSizePolicy, QSlider, QHBoxLayout
from PyQt5.QtGui import QFont
from KZGamer import KZGamerThread


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.kzgamer_thread = KZGamerThread(self)
        self.kzgamer_thread.new_roll.connect(self.log_roll)
        self.button_grid = QWidget()
        self.button_layout = QGridLayout()
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

         # Add the radio buttons for the mode input
        mode_label = QLabel("Mode:")
        mode_label.setFont(QFont("Helvetica", 14))
        self.hit_damage_radio = QRadioButton("Hit/Damage")
        self.morale_radio = QRadioButton("Morale")
        self.hit_damage_radio.toggled.connect(self.hit_damage_mode)
        self.morale_radio.toggled.connect(self.morale_mode)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.hit_damage_radio)
        mode_layout.addWidget(self.morale_radio)

        main_layout.addLayout(mode_layout)

        
        self.button_layout.setSpacing(0)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        button_size = 50

        for i in range(0, 12):
            button = QPushButton(str(i+1))
            button.setObjectName(str(i+1))
            button.clicked.connect(self.button_click_handler)
            row = int(i/6)
            col = (i+6)%6
            button.setMinimumSize(button_size, button_size)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            self.button_layout.addWidget(button, row, col)

        
        self.button_grid.setLayout(self.button_layout)
        self.morale_radio.setChecked(True) # Set Hit/Damage mode as the default
        main_layout.addWidget(self.button_grid)
        self.setLayout(main_layout)

    def button_click_handler(self):
        sender = self.sender()
        self.log_pane.append(f"hitting on {sender.text()}s")
        self.kzgamer_thread.target_selected(int(sender.text()))

    @pyqtSlot(object)
    def log_roll(self, message):
        self.last_roll_display.clear()
        self.last_roll_display.setText(message)
        self.log_pane.append(f"[{QtCore.QTime.currentTime().toString('hh:mm:ss')}] {message}")

    def hit_damage_mode(self, checked):
        if checked:
            self.log_pane.append("Setting Hit/Damage mode")
            for i in range(1, 13):
                button = self.button_grid.findChild(QPushButton, str(i))
                if i <= 6:
                    button.setEnabled(True)
                else:
                    button.setEnabled(False)
            self.kzgamer_thread.mode_selected("Hit/Damage")
            
    def morale_mode(self, checked):
        if checked:
            self.log_pane.append("Setting Morale mode")
            for i in range(1, 13):
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

