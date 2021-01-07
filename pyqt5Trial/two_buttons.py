"A gui for a music player using QT on python."
import sys
from PyQt5.QtWidgets import (QPushButton, QApplication, QVBoxLayout, QDialog)
from PyQt5.QtCore import (Qt)
# pip install pyqt5
# or on rasp:
# sudo apt-get update
# sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools
#
# pylint issue: "python.linting.pylintArgs": [
#    "--extension-pkg-whitelist=PyQt5"
#],

class Form(QDialog):
    "defines the buttons and the layouts and stuff"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Player')
        self.setMinimumWidth(180) # in px. To make sure the title is displayed
        window_flags = Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        self.setWindowFlags(window_flags) # remove the help-question mark button on the window

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
