#works by getting all items from database and applying them in __init__()
#the calculatable items are made in other method
#after the player adjusts things the items are brought from UI and daved into dataBase
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QTableView, QHeaderView, QComboBox
from PyQt5 import uic
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QSortFilterProxyModel
import sys
import sqlite3
from os import path, replace
import json
from uuid import uuid4

items_price = []
items_id = []
items_name = []
items_purshase_price = []
items_pricing_method = []
items_units_left = []


#Connect to sql database
conn = sqlite3.connect('Resources/Data/store_items.db')

#Create the table if not exist
def Create_table():
    #Start Connection
    cursor = conn.cursor()
    #create the table
    cursor.execute(""" CREATE TABLE IF NOT EXISTS
    items
    (id INTEGER PRIMARY KEY AUTOINCREMENT, ItemName TEXT NOT NULL , Price TEXT NOT NULL, PurchasePrice TEXT, UnitsLeft TEXT, Pricing TEXT)""")
    #End connection
    cursor.close()

class EditSearch(QMainWindow):
    def __init__(self):
        super(EditSearch, self).__init__()

        #load the ui file
        uic.loadUi("Resources/UI/Inventory.ui", self)

        #connect to design widgets
        self.search_table = self.findChild(QTableView, "search_result_table")
        self.search_bar = self.findChild(QLineEdit, "search_bar")
        self.search_type_selector = self.findChild(QComboBox, "search_type_changer")
        self.refresh_button = self.findChild(QPushButton, "refresh_button")
        self.edit_table = self.findChild(QPushButton, "EditButton")
        self.RateInput = self.findChild(QLineEdit, "RateInput")
        self.TotalValueWidget = self.findChild(QLabel, "TotalValue")
        self.TotalProfitWidget = self.findChild(QLabel, "TotalProfit")

        #Put the current Exchange Rate
        filename = 'Resources/Data/additionalData.json'
        #Open file
        with open(filename, 'r') as f:
                #Modify Data
                data = json.load(f)
                try:
                    n = data['rate']
                    n = str(format(n, ',d'))
                    self.RateInput.setText(n)
                except:
                    data['rate'] = 0
                    n = str(data['rate'])
                    self.RateInput.setText(n)

        

        #deign table
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.search_table.setSelectionBehavior(QTableView.SelectRows)

        #Change between types of sorting
        self.search_type_selector.currentTextChanged.connect(lambda: self.LoadData())

        self.refresh_button.clicked.connect(self.LoadData)

        self.search_table.doubleClicked.connect(self.OpenEditMenu)
        self.edit_table.clicked.connect(self.OpenEditMenu)
        self.RateInput.returnPressed.connect(self.ChangeExchangeRate)

         #create the model
        self.model = QStandardItemModel(len(items_id),3)
        #set horizontal labels
        self.model.setHorizontalHeaderLabels(["ID", "Item Name", "Item Price", "Purshase Price", "Units Left", "Bought With"])     
        #return the model, and newly made lists

        self.LoadData()
        self.showMaximized()

    def AddToModelList(self, row):
        #Check if Item already exist, then create if not
        if not row[0] in items_id:
            #add each item to a list
            items_name.append(row[1])
            items_id.append(row[0])
            items_price.append(row[2])
            items_purshase_price.append(row[3])
            items_units_left.append(row[4])
            items_pricing_method.append(row[5])

        else:
            #get the placement of item in the database
            m = items_id.index(row[0])
            #update the list if item already exists
            items_name[m] = row[1]
            items_id[m] = row[0]
            items_price[m] = row[2]
            items_purshase_price[m] = row[3]
            items_units_left[m] = row[4]
            items_pricing_method[m] = row[5]


    def LoadSearchBarTable(self):
        #get lists from function above and and add them into the model
        for row, name in  enumerate(items_name):
            item = QStandardItem(name)
            self.model.setItem(row,1,item)
        for row, ID in enumerate(items_id):
            item = QStandardItem(str(ID))
            self.model.setItem(row,0,item)
        for row, price in enumerate(items_price):
            item = QStandardItem(str(price))
            self.model.setItem(row,2, item)
        for row, purshase_p in enumerate(items_purshase_price):
            item = QStandardItem(str(purshase_p))
            self.model.setItem(row,3, item)
        for row, units_l in enumerate(items_units_left):
            item = QStandardItem(str(units_l))
            self.model.setItem(row,4, item)
        for row, pricing_m in enumerate(items_pricing_method):
            item = QStandardItem(str(pricing_m).upper())
            self.model.setItem(row,5, item)

        #create the filter
        filter_proxy_model = QSortFilterProxyModel()
        #set the filter to work with the model
        filter_proxy_model.setSourceModel(self.model)
        #create the filtering mechanism
        filter_proxy_model.setFilterKeyColumn(self.search_type_selector.currentIndex())
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.search_bar.textChanged.connect(filter_proxy_model.setFilterRegExp)
        #apply the model graphically
        self.search_table.setModel(filter_proxy_model)
        self.GetSums()
    
    def ResetValues(self):
        items_price.clear()
        items_id.clear()
        items_name.clear()
        items_purshase_price.clear()
        items_pricing_method.clear()
        items_units_left.clear()

    def LoadData(self):
        self.ResetValues()
        #Update connection to query
        conn = sqlite3.connect('Resources/Data/store_items.db')
        cursor = conn.cursor()
        #Get all the Items
        sqlquery = "SELECT * FROM items"
        cursor.execute(sqlquery)
        conn.commit()
        records =  cursor.fetchall()
        #Make the table
        tablerow = 0
        #place all table items
        for row in (cursor.execute(sqlquery)):
            self.AddToModelList(row)
        if len(records) > 0:
            self.LoadSearchBarTable()

    def OpenEditMenu(self):
        
        if self.search_table.currentIndex().row() >= 0:
            index = self.search_table.currentIndex()
            row = index.row()
            #start connecion
            cursor = conn.cursor()
            #Get all the Items
            sqlquery = "SELECT * FROM items"
            cursor.execute(sqlquery)
            items = cursor.fetchall()
            #get selected row
            selected = items[row]
            #set the name
            self.Editor = ItemEditor(selected[1], selected[3], selected[2],selected[4], selected[5], self)
        else:
            return

    def ChangeExchangeRate(self):
        try:
            new_price = self.RateInput.text().replace(',','')
            new_price = int(new_price)

            #Enter fileName
            filename = 'Resources/Data/additionalData.json'
            #Open file
            with open(filename, 'r') as f:
                #Modify Data
                data = json.load(f)
                try:
                    old_price = data['rate']
                    data['rate'] = new_price
                except:
                    old_price = new_price
                    data['rate'] = new_price
            #Replace old data 
             #Create a new file in loactaion of old
            tempfile = path.join(path.dirname(filename), str(uuid4()))
            #put modified data in new file
            with open(tempfile, 'w') as f:
                json.dump(data, f, indent= 4)
            #Replace old and new files
            replace(tempfile, filename)

            #Get old and new and get change_factor
            Change_factor = new_price/ old_price
            #Get Items To Change
            #start connecion
            cursor = conn.cursor()
            #Get all the Items
            sqlquery = "SELECT * FROM items"
            #execute the commands
            cursor.execute(sqlquery)
            items = cursor.fetchall()


            #get the item and it's traits
            for item in items:
                #check if item is changable
                if item[5] == "usd":
                    #Get the numbers and change them
                    p = int(item[2].replace(',','')) * Change_factor
                    k = int(p)
                    k = str(format(k, ',d'))
                    n = item[1]
                    command1 = f"""UPDATE items
                           SET price = '{k}'
                           WHERE ItemName = '{n}' """
                    cursor.execute(command1)
                    conn.commit()
                    cursor.close()
                    self.LoadData()
        except:
            self.errorwindow = ErrorUI("Please Enter A Number", "OK")
       
       
    def GetSums(self):
        Totalvalue = 0
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 2)
            ItemP = self.model.data((index))
            index = self.model.index(row, 4)
            ItemN = self.model.data(index)
            ItemP = ItemP.replace(',','')
            ItemN = ItemN.replace(',', '')
            try:
                int(ItemN)
                Totalvalue += int(ItemN) * int(ItemP)
            except:
                pass
        Totalvalue = str(format(Totalvalue, ',d'))
        self.TotalValueWidget.setText(Totalvalue)

        Totalprofit = 0
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 2)
            ItemP = self.model.data((index))
            index = self.model.index(row, 4)
            ItemN = self.model.data(index)
            index = self.model.index(row, 3)
            ItemPP = self.model.data(index)
            ItemP = ItemP.replace(',','')
            ItemN = ItemN.replace(',', '')
            ItemPP = ItemPP.replace(',', '')
            try:
                int(ItemN)
                int(ItemPP)
                Totalprofit += (int(ItemP) - int(ItemPP)) * int(ItemN)
            except:
                pass
        Totalprofit = str(format(Totalprofit, ',d'))
        self.TotalProfitWidget.setText(Totalprofit)

        
class ItemEditor(QMainWindow):
    def __init__(self, name, pPrice, sPrice, unitsLeft, pricing_method, searchpage):
        super(ItemEditor,self).__init__()

        uic.loadUi("Resources/UI/ItemEditorFull.ui", self)

         #Creating The Edit Menu
        self.item_name = self.findChild(QLineEdit, "name_lineEdit")
        self.purshase_price = self.findChild(QLineEdit, "pPrice_lineEdit")
        self.sell_price = self.findChild(QLineEdit, "sPrice_lineEdit")
        self.pricing_method = self.findChild(QComboBox, "PricingSelector")
        self.unitsLeft = self.findChild(QLineEdit, "UnitsLeft_lineEdit")
        self.TotalValue = self.findChild(QLabel, "TotalValue")
        self.TotalProfit = self.findChild(QLabel, "TotalProfit")
        self.SaveButton = self.findChild(QPushButton, "SaveButton")
        self.ProfitPerItem = self.findChild(QLabel, "profit_per_item")

        #fix for empty input
        pPrice = self.CheckIfUsable(pPrice)
        sPrice = self.CheckIfUsable(sPrice)
        unitsLeft = self.CheckIfUsable(unitsLeft)

        self.searchpage = searchpage
       
        #Set old input in UI
        self.item_name.setText(name)
        self.purshase_price.setText(str(format(int(pPrice),',d')))
        self.sell_price.setText(str(format(int(sPrice),',d')))
        self.unitsLeft.setText(str(unitsLeft))
        #set pricing method in UI
        if pricing_method == "usd":
            self.pricing_method.setCurrentIndex(1)
        else:
            self.pricing_method.setCurrentIndex(0)
            
        #put the save button
        self.SaveButton.clicked.connect(self.SaveUpdates)

        self.LoadCalculatableInput()
    
        self.show()
        
    def LoadCalculatableInput(self):
        
        #make total value
        tv = self.MakeInt(self.sell_price.text()) * int(self.unitsLeft.text())
        tv = str(format(tv, ',d'))

        #make purshase price
        pp = self.MakeInt(self.purshase_price.text())

        #make profit per item
        ppp = self.MakeInt(self.sell_price.text()) - pp

        #make total profit
        tp = (ppp) * int(self.unitsLeft.text())
        tp = str(format(tp,',d'))
        ppp = str(format(ppp,',d'))

        #Apply changes to UI
        self.TotalValue.setText(tv)
        self.TotalProfit.setText(tp)
        self.ProfitPerItem.setText(ppp)

    def SaveUpdates(self):
        #Open Connection to server
        cursor = conn.cursor()
        #Get Items From UI
        sp = self.sell_price.text() 
        pp = self.purshase_price.text()
        ul = self.unitsLeft.text()  
        if self.pricing_method.currentIndex() == 0:
            pricing = "lbp"
        else:
            pricing = "usd"
        n = self.item_name.text()
        #Update the database
        command1 = f"""UPDATE items
                        SET price = '{sp}', PurchasePrice = '{pp}', UnitsLeft = '{ul}', Pricing = '{pricing}'
                       WHERE ItemName = '{n}' """
        cursor.execute(command1)
        conn.commit()
        cursor.close()
        self.close()
        self.searchpage.LoadData()

    def CheckIfUsable(self, n):
        try:
            n = self.MakeInt(n)
            return n
        except:
            return 0
        
    def MakeInt(self, n):
        n = str(n)
        n = n.replace(',', '')
        n = int(n)
        return n

    
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
    Create_table()
    #start the application
    app = QApplication(sys.argv)
    #open the main window
    UIWindow = EditSearch()
    #start app loop
    app.exec_()