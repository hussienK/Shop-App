from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt5 import uic
import sys
from os import path, replace, getcwd
import json
from uuid import uuid4
from shutil import copyfile

class Extrasmenu(QMainWindow):
    def __init__(self):
        super(Extrasmenu, self).__init__()
        uic.loadUi("Resources/UI/Extras.ui", self)

        self.GetDirButton = self.findChild(QPushButton, "GetDirbutton")
        self.DirLineEdit = self.findChild(QLineEdit, "DirectoryLineEdit")
        self.createbackupButton = self.findChild(QPushButton, 'CreateBackupButton')
        self.GetbackupDirButton = self.findChild(QPushButton, 'GetBackupDirButton')
        self.ChangeCurrentData = self.findChild(QPushButton, 'LoadBackupButton')
        self.BackupLocatioEdit = self.findChild(QLineEdit, 'BackupDirLineEdit')

        filename = 'Resources/Data/additionalData.json'
     
        self.GetDirButton.clicked.connect(self.GetDirectory)
        self.createbackupButton.clicked.connect(self.CreateBackup)
        self.GetbackupDirButton.clicked.connect(self.GetBackupLocation)
        self.ChangeCurrentData.clicked.connect(self.ApplyNewBackup)
        #load the ui file

        self.backupLocation = ''

        self.show()

    def GetDirectory(self):
        input_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', path.expanduser("User"))
        self.DirLineEdit.setText(input_dir)
        
        

    def CreateBackup(self):
        target_path = f'{self.DirLineEdit.text()}/store_items.db'
        original_path = 'Resources/Data/store_items.db'
        try:
            copyfile(original_path, target_path)
        except:
            self.Error = ErrorUI("Please Enter A Valid Direcotory", "OK")

    def GetBackupLocation(self):
        input_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', path.expanduser("User"))
        self.BackupLocatioEdit.setText(input_dir)


    def ApplyNewBackup(self):
        input_dir = self.BackupLocatioEdit.text()
        #Enter fileName
        new_data = f"{input_dir}/store_items.db"
        old_data = 'Resources/Data/store_items.db'

        print(new_data)
        print(old_data)
        try:
            copyfile(new_data, old_data)
        except:
            self.Error = ErrorUI("Please Enter A Valid Direcotory", "OK")
#Create the error UI
class ErrorUI(QMainWindow):
    def __init__(self, text,button_text):
        super(ErrorUI,self).__init__()
        #read the design file
        uic.loadUi("Resources/UI/Error.ui",self)
        #get the buttins
        self.exit_b = self.findChild(QPushButton, 'exit_button')
        self.exit_t = self.findChild(QLabel, "error_label")
        #Set the text
        self.exit_t.setText(text)
        self.exit_b.setText(button_text)

        #close the app
        self.exit_b.clicked.connect(self.exit)

        self.show()

    def exit(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UiWindow = Extrasmenu()
    app.exec_()
