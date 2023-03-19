from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QGridLayout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.hitting_on = 4
        # Set up the user interface
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Text Pane with Buttons")

        # Create a QVBoxLayout to organize the widgets vertically
        main_layout = QVBoxLayout()

        # Create the text pane for output
        self.text_pane = QTextEdit()
        self.text_pane.setReadOnly(True)
        main_layout.addWidget(self.text_pane)

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
        main_layout.addLayout(button_layout)

        # Set the main layout for the main window
        self.setLayout(main_layout)

    def button_click_handler(self):
        # Get the sender (button) and append its text to the text pane
        sender = self.sender()
        self.hitting_on = int(sender.text())
        self.text_pane.append(f"Hitting on {sender.text()}s")

    def log_roll(self, hits, numDice, sixes, bits):
        self.text_pane.append(f"{hits} on {numDice} dice, {sixes} exploded - {bits} bits of entropy collected")
