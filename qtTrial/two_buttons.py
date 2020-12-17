" A gui for a music player using QT on python"
import sys
from PySide6.QtWidgets import (QPushButton, QApplication, QVBoxLayout, QDialog)

class Form(QDialog):
    "defines the buttons and the layouts and stuff"
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Player Control")

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
        self.button_next.clicked.connect(self.cmd_goto_next)
        self.button_prev.clicked.connect(self.cmd_goto_prev)


    def cmd_goto_prev(self): # self is required as an argument
        "actions when the previous button is pressed"
        print_direction("previous")


    def cmd_goto_next(self):
        "actions when the next button is pressed"
        print_direction("next")

# global
def print_direction(direction):
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
