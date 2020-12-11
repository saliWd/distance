import sys
from PySide6.QtWidgets import (QLineEdit, QPushButton, QApplication, QVBoxLayout, QDialog)
    
class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Player Control")
        # Create widgets
        # self.edit = QLineEdit("Write my name here..")
        self.buttonNext = QPushButton("Next song")
        self.buttonNext.direction = "next"
        self.buttonPrev = QPushButton("Previous song")
        self.buttonPrev.direction = "previous"
        
        # Create layout and add widgets
        layout = QVBoxLayout()
        # layout.addWidget(self.edit)
        layout.addWidget(self.buttonNext)
        layout.addWidget(self.buttonPrev)
        # Set dialog layout
        self.setLayout(layout)
        
        # Add button connection
        self.buttonNext.clicked.connect(self.cmdGoto)
        self.buttonPrev.clicked.connect(self.cmdGotoLast)
        
    # Greets the user
    # def greetings(self):
    #   print ("Hello {}".format(self.edit.text()))    

    def cmdGotoLast(self): # self is required as an argument
      print ("skipping to previous song ")    
        
    def cmdGoto(self):
      print ("skipping to " + self.buttonNext.direction + " song ") # does not help that much as I need to specify the buttonNext   
    


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())