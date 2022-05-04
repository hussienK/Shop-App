from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox
from PyQt5 import uic
import sys
import sqlite3

def Create_table():
    conn = sqlite3.connect('Resources/Data/MyList.db')
    cursor = conn.cursor()
    command = """CREATE TABLE IF NOT EXISTS toget_list
    (
        list_item TEXT
        )"""
    cursor.execute(command)
    cursor.close()
class ToGetList(QMainWindow):
    def __init__(self):
        super(ToGetList, self).__init__()

        #load the ui file
        uic.loadUi("Resources/UI/ToDoList.ui", self)

        self.AddItemButton = self.findChild(QPushButton, 'addItem_pushButton')
        self.DeleteItemButton = self.findChild(QPushButton, 'delleteItem_pushbutton')
        self.ClearListButton = self.findChild(QPushButton, 'clearList_pushNutton')
        self.ItemLineEdit = self.findChild(QLineEdit, 'AddItem_LineEdit')
        self.ListView = self.findChild(QListWidget, 'myList_lineWidget')
        self.SaveButton = self.findChild(QPushButton, 'Save_Button')

        self.AddItemButton.clicked.connect(self.AddItem)
        self.DeleteItemButton.clicked.connect(self.DeleteItem)
        self.ClearListButton.clicked.connect(self.ClearList)
        self.SaveButton.clicked.connect(self.SaveList)

        self.grab_all()
        self.show()

    def AddItem(self):
        item = self.ItemLineEdit.text()
        self.ListView.addItem(item)
        self.ItemLineEdit.setText("")

    def DeleteItem(self):
        clicked = self.ListView.currentRow()
        self.ListView.takeItem(clicked)

    def ClearList(self):
        self.ListView.clear()

    def SaveList(self):
        conn =  sqlite3.connect('Resources/Data/MyList.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM toget_list;',)
        items = []
        for index in range(self.ListView.count()):
            items.append(self.ListView.item(index))
        
        for item in items:
            n = str(item.text())
            print(n)
            command = f"INSERT INTO toget_list VALUES ('{n}')"
            cursor.execute(command)
        conn.commit()
        conn.close()

        msg = QMessageBox()
        msg.setWindowTitle("Saved TO DataBase!")
        msg.setText("Your List Has Been Saved!")
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_()

    def grab_all(self):
        conn =  sqlite3.connect('Resources/Data/MyList.db')
        cursor = conn.cursor()
        command = 'SELECT * FROM toget_list'
        cursor.execute(command)

        records = cursor.fetchall()
        conn.commit()
        conn.close()
        for record in records:
            self.ListView.addItem(str(record[0]))



if __name__ == "__main__":
    Create_table()
    #start the application
    app = QApplication(sys.argv)
    #open the main window
    UIWindow = ToGetList()
    #start app loop
    app.exec_()