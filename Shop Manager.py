from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QDial
import sys 
from subprocess import Popen
from subprocess import PIPE, run
from PyQt5 import uic





class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        #load the ui file
        uic.loadUi("Resources/UI/Index.ui", self)

        #variablesz
        self.LoadName = "SearchSystem"

        #Load widgets
        self.selector = self.findChild(QDial, "Chooser")
        self.Selcted_text = self.findChild(QLabel, "Selected_text")
        self.button = self.findChild(QPushButton, "Select_button")

        #Assign widget functions
        self.selector.valueChanged.connect(self.ChangeLabelValue)
        self.button.clicked.connect(self.Loadpage)

        self.showMaximized()
        #Show app

    def ChangeLabelValue(self):
        #Get dial value
        self.selected_value = self.selector.value()

        #assign shown text according to dial
        if self.selected_value >= 40 and self.selected_value <= 58:
            self.LoadName = "Search System"
        elif self.selected_value >= 33 and self.selected_value < 40:
            self.LoadName = "Stuff To Get"
        elif self.selected_value >=15 and self.selected_value < 33:
            self.LoadName = "Add/Delete Items"
        elif self.selected_value > 33 and self.selected_value <=68:
            self.LoadName = "Backup"
        elif self.selected_value >68 and self.selected_value <= 83:
            self.LoadName = "Manage Inventory"
        else:
            self.LoadName = ""

        #self.Selcted_text.setText(str(self.selected_value))
        self.Selcted_text.setText(self.LoadName)
        
    def Loadpage(self):
        if self.LoadName == "Search System":
            run("SearchSystem.exe")
        elif self.LoadName == "Add/Delete Items":
            run("ItemCreator.exe")
        elif self.LoadName == "Manage Inventory":
            run("Inventorymanager.exe")
        elif self.LoadName == "Backup":
            run("Extras.exe")
            
        elif self.LoadName == "Stuff To Get":
            run("ToGetList.exe")
        else:
            pass
            
        
if __name__ == "__main__":
    #start the application
    app = QApplication(sys.argv)
    #open the main window
    UIWindow = UI()
    #start app loop
    app.exec_()
