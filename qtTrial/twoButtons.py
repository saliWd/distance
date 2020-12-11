import sys
from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication, QVBoxLayout, QDialog)
    
class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Player Control")
        
        # Create two buttons
        self.buttonNext = QPushButton("Next song") # self.buttonNext.direction = "next" # does not help
        self.buttonPrev = QPushButton("Previous song")        
        
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.buttonNext)
        layout.addWidget(self.buttonPrev)

        # Set dialog layout
        self.setLayout(layout)
        
        # Add button connection
        self.buttonNext.clicked.connect(self.cmdGotoNext)
        self.buttonPrev.clicked.connect(self.cmdGotoPrev)
        
    def cmdGotoPrev(self): # self is required as an argument      
      printDirection("previous")
        
    def cmdGotoNext(self):
      printDirection("next")

# global
def printDirection(direction):
  print ("skipping to " + direction + " song ")    

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())