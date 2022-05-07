import sqlite3
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QTableView, QHeaderView, QComboBox
from PyQt5 import uic
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QSortFilterProxyModel
import sys
from SearchSystem import Search

#Connect to sql database
conn = sqlite3.connect('Resources/Data/store_items.db')

#Create the table if not exist
def Create_table():
    #Connect to sql database
    conn = sqlite3.connect('Resources/Data/store_items.db')
    #Start Connection
    cursor = conn.cursor()
    #create the table
    cursor.execute(""" CREATE TABLE IF NOT EXISTS
    items
    (id TEXT, ItemName TEXT NOT NULL , Price TEXT NOT NULL, PurchasePrice TEXT, UnitsLeft TEXT, Pricing TEXT)""")
    #End connection
    cursor.close()

class AddItems(QMainWindow):
    def __init__(self):
        super(AddItems, self).__init__()

        Create_table()

        #load the ui file
        uic.loadUi("Resources/UI/ItemCreator.ui", self)

        #define my Widgets
        self.name_input = self.findChild(QLineEdit, "Name_lineEdit")
        self.price_input = self.findChild(QLineEdit, "Price_lineEdit")
        self.id_input = self.findChild(QLineEdit, "ID_lineEdit")
        self.create_button  = self.findChild(QPushButton, "Create_Button")
        self.data_table = self.findChild(QTableWidget, "item_table_widget")
        self.delete_button = self.findChild(QPushButton, "delete_item_button")

        #connect buttons
        self.create_button.clicked.connect(self.create_an_item)
        self.delete_button.clicked.connect(self.delete_an_item)

        #setup tables
        self.data_table.setHorizontalHeaderLabels(["ID", "Item Name", "Item Price"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)        

        #Start App
        self.LoadData(self.data_table)
        self.showMaximized()

    def create_an_item(self):
        cursor = conn.cursor()
        try:
            #Get User Input
            n = self.name_input.text()
            p = self.price_input.text().replace(',','')
            i = self.id_input.text()
            if i == "":
                i = "0"
            p = int(p)
            #Make More Readable
            p = str(format(p, ',d'))

        #Incase of input error
        except:
            self.name_input.setText("")
            self.price_input.setText("")
            self.id_input.seText("")
            self.warning = ErrorUI("Please Enter A Valid Input", "Ok")
            return

        #Update ussr input
        if(self.ItemExists(n)):
            command1 = f"""UPDATE items
                           SET Price = '{p}', id = '{i}'
                           WHERE ItemName = '{n}' """
            cursor.execute(command1)
            conn.commit()
            cursor.close()
            self.LoadData(self.data_table)
        #Create new user input
        else:
            #make the commands
            command1 = f"INSERT INTO items (id, ItemName, Price) VALUES('{i}','{n}','{p}')"
            command2 = "SELECT * from items"
            cursor.execute(command1)
            cursor.execute(command2)

            #Apply everythings
            conn.commit()
            cursor.close()
            #Update Table
            self.LoadData(self.data_table)

    def delete_an_item(self):
        try:
            #open connection
            cursor = conn.cursor()
            #make the deletion
            command1 = f"""
                    DELETE FROM items
                    WHERE ItemName = '{self.name_input.text()}'  """
            cursor.execute(command1)
            #update the database
            conn.commit()
            cursor.close()
            self.LoadData(self.data_table)
        except:
            self.warning = ErrorUI("Please Select An Item To Delete", "Ok")

    def LoadData(self, selected_table):
        #Update connection to query
        conn = sqlite3.connect('Resources/Data/store_items.db')
        cursor = conn.cursor()
        #Get all the Items
        sqlquery = "SELECT * FROM items"
        cursor.execute(sqlquery)
        conn.commit()
        records =  cursor.fetchall()
        #Make the table
        selected_table.setRowCount(len(records))
        
        tablerow = 0
        #place all table items
        for row in (cursor.execute(sqlquery)):
            #Apply changes for every item
            selected_table.setItem(tablerow, 0, QTableWidgetItem(str(row[0])))
            selected_table.setItem(tablerow, 1, QTableWidgetItem(row[1]))
            selected_table.setItem(tablerow, 2, QTableWidgetItem(str(row[2])))
            tablerow +=1

            #ad items to search bar
           #m, items_name, items_id, items_price = Search().AddToModelList(row)
        #if len(records) > 0:
            #Update the Search Table
            #Search().LoadSearchBarTable(m, self.search_bar, self.search_table,self.search_type_selector,items_name, items_id, items_price)
            #when user selects a table
        self.data_table.cellDoubleClicked.connect(self.TableClicked)

    def TableClicked(self):
        #Get clicked row
        c = self.data_table.currentRow()
        #start connecion
        cursor = conn.cursor()
        #Get all the Items
        sqlquery = "SELECT * FROM items"
        cursor.execute(sqlquery)
        items = cursor.fetchall()
        #get selected row
        self.selected = items[c]
        #set the name
        self.name_input.setText(self.selected[1])
        new_price = self.selected[2]
        new_price = new_price.replace(',','')
        self.price_input.setText(new_price)
        self.id_input.setText(self.selected[0])
        #end collection
        cursor.close()


    def ItemExists(self, name):
        #Get clicked row
        c = self.data_table.currentRow()
        #start connecion
        cursor = conn.cursor()
        #Get all the Items
        sqlquery = "SELECT * FROM items"
        cursor.execute(sqlquery)
        items = cursor.fetchall()
        #get selected row
        for row in items:
            if(row[1] == name):
                return True
        return False

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
    #create the table
    Create_table()
    #start the application
    app = QApplication(sys.argv)
    #open the main window
    UIWindow = AddItems()
    #start app loop
    app.exec_()
