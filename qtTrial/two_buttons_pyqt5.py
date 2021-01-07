"A gui for a music player using QT on python."
import sys
from PyQt5.QtWidgets import (QPushButton, QApplication, QLabel, QVBoxLayout, QDialog)
# pip install pyqt5

class Form(QDialog):
    "defines the buttons and the layouts and stuff"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Player Control") # TODO: doesn't work on pyqt5

        # Create two buttons
        self.button_next = QPushButton("Next song")
        self.button_prev = QPushButton("Previous song")

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.button_next)
        layout.addWidget(self.button_prev)

        # Set dialog layout
        self.setLayout(layout)

        # Add button connection
        # pylint: disable=no-member
        self.button_next.clicked.connect(self.cmd_goto_next)
        self.button_prev.clicked.connect(self.cmd_goto_prev)


    @classmethod
    def cmd_goto_prev(cls):
        "actions when the previous button is pressed"
        cls.print_direction("previous")


    @classmethod
    def cmd_goto_next(cls):
        "actions when the next button is pressed"
        cls.print_direction("next")


    @classmethod
    def print_direction(cls, direction):
        "outputs on the console"
        print ("skipping to " + direction + " song ")


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)    
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
