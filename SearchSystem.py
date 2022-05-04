from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QTableView, QHeaderView, QComboBox
from PyQt5 import uic
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSortFilterProxyModel
import sys
import sqlite3

items_price = []
items_id = []
items_name = []

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

class Search(QMainWindow):
    def __init__(self):
        super(Search, self).__init__()

        #load the ui file
        uic.loadUi("Resources/UI/Search.ui", self)

        #Lists for purshase
        self.purshased_names = []
        self.purshased_prices = []
        self.purshased_amounts = []

        #connect to design widgets
        self.search_table = self.findChild(QTableView, "search_result_table")
        self.search_bar = self.findChild(QLineEdit, "search_bar")
        self.search_type_selector = self.findChild(QComboBox, "search_type_changer")
        self.refresh_button = self.findChild(QPushButton, "refresh_button")
        self.clear_button = self.findChild(QPushButton, "ClearButton")
        self.cartOpenImage = self.findChild(QPushButton , "ShopingOpen")

        #deign table
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.search_table.setSelectionBehavior(QTableView.SelectRows)
        self.search_table.doubleClicked.connect(self.AddItem)

        self.clear_button.clicked.connect(self.Clearbasket)
        #Set Purshase Page Image
        self.cartOpenImage.setStyleSheet("background-image : url(Resources/UI/Images/CartImage.png);")
        self.cartOpenImage.clicked.connect(self.OpenSellMenu)

        self.purshase_number = self.findChild(QLabel, "purshase_number")

        #Change between types of sorting
        self.search_type_selector.currentTextChanged.connect(lambda: self.LoadData())

        self.refresh_button.clicked.connect(self.LoadData)


        self.LoadData()
        self.showMaximized()


    def AddToModelList(self, row):
        #Check if Item already exist, then create if not
        if not row[0] in items_id:
            #add each item to a list
            items_name.append(row[1])
            items_id.append(row[0])
            items_price.append(row[2])
        else:
            #get the placement of item in the database
            m = items_id.index(row[0])
            #update the list if item already exists
            items_name[m] = row[1]
            items_id[m] = row[0]
            items_price[m] = row[2]

        #create the model
        self.model = QStandardItemModel(len(items_id),3)
        #set horizontal labels
        self.model.setHorizontalHeaderLabels(["ID", "Item Name", "Item Price"])     
        #return the model, and newly made lists

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

    def LoadData(self):
        items_id.clear()
        items_name.clear()
        items_price.clear()
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

    def AddItem(self):
        #get selected Item
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
        else: 
            return 
        #Add selected item to list
        #Check if item is purshased before
        if selected[1] in self.purshased_names:
            #If purshased before
            i = self.purshased_names.index(selected[1])
            self.purshased_amounts[i] += 1
        else:
            self.purshased_prices.append(selected[2])
            self.purshased_names.append(selected[1])
            self.purshased_amounts.append(1)
        n = str(int(self.purshase_number.text()) + 1)
        self.purshase_number.setText(n)
    
    def Clearbasket(self):
        self.purshased_names.clear()
        self.purshased_amounts.clear()
        self.purshased_prices.clear()
        self.purshase_number.setText('0')
    
    def OpenSellMenu(self):
        self.sellMenu = CheckOutPage(self.purshased_names, self.purshased_prices, self.purshased_amounts, self)

    def removeItem(self, index):
        if self.purshased_amounts[index] > 1:
            self.purshased_amounts[index] -= 1
        else:
            self.purshased_names.pop(index)
            self.purshased_amounts.pop(index)
            self.purshased_prices.pop(index)
        self.sellMenu.p_amount = self.purshased_amounts
        self.sellMenu.p_name = self.purshased_names
        self.sellMenu.p_price = self.purshased_prices
        self.sellMenu.LoadSearchBarTable()        
        

class CheckOutPage(QMainWindow):
    def __init__(self, purshased_name,purshased_price, purshased_amount, SearchPage):
        super(CheckOutPage, self).__init__()

        #load the ui file
        uic.loadUi("Resources/UI/Checkout.ui", self)
        
        #connect to design widgets
        self.search_table = self.findChild(QTableView, "search_result_table")
        self.search_bar = self.findChild(QLineEdit, "search_bar")
        self.search_type_selector = self.findChild(QComboBox, "search_type_changer")
        self.TotalPriceWidget = self.findChild(QLabel, "TotalPriceLabel")
        self.purshaseButton = self.findChild(QPushButton, "PurshaseButton")
        self.remmoveItemButton = self.findChild(QPushButton, "RemoveItem")

        self.searchpage = SearchPage

        self.purshaseButton.clicked.connect(self.Purshased)
        self.remmoveItemButton.clicked.connect(self.removeItem)

        #deign table
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.search_table.setSelectionBehavior(QTableView.SelectRows)
        
        self.p_name = purshased_name
        self.p_price = purshased_price
        self.p_amount = purshased_amount


        self.LoadSearchBarTable()
        self.GetDataInListForm()

        self.showMaximized()


    def LoadSearchBarTable(self):
        #create the model
        self.model = QStandardItemModel(len(self.p_name),3)
        #set horizontal labels
        self.model.setHorizontalHeaderLabels(["Name", "Price", "Amount Purshased"])   

        #get lists from function above and and add them into the model
        for row, name in  enumerate(self.p_name):
            item = QStandardItem(name)
            self.model.setItem(row,0,item)
        for row, price in enumerate(self.p_price):
            item = QStandardItem(str(price))
            self.model.setItem(row,1,item)
        for row, amount in enumerate(self.p_amount):
            item = QStandardItem(str(amount))
            self.model.setItem(row,2, item)
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
        self.GetSum()


    #use if making printable papers
    def GetDataInListForm(self):
        #getting data from table
        data = []
        for row in range(self.model.rowCount()):
            data.append([])
            for column in range(self.model.columnCount()):
                index = self.model.index(row, column)
                data[row].append(str(self.model.data(index)))

    def GetSum(self):
        price = 0
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 1)
            ItemP = self.model.data((index))
            index = self.model.index(row, 2)
            ItemN = self.model.data(index)
            ItemP = ItemP.replace(',','')
            ItemN = ItemN.replace(',', '')
            price += int(ItemN) * int(ItemP)
        price = str(format(price, ',d'))
        self.TotalPriceWidget.setText(price)

    def Purshased(self):
        cursor = conn.cursor()
        #Get all the Items
        sqlquery = "SELECT * FROM items"
        cursor.execute(sqlquery)
        items = cursor.fetchall()

        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)
            ItemName = self.model.data(index)
            #Accesss database to get the units left
            command = f" SELECT UnitsLeft FROM items WHERE ItemName = '{ItemName}'"
            cursor.execute(command)
            ItemsLeft = cursor.fetchone()
            index = self.model.index(row, 2)
            NumberToTakeOut = self.model.data(index)
            NumberToTakeOut = int(NumberToTakeOut)
            try:
                int(ItemsLeft[0])
                NewTotal = int(ItemsLeft[0]) - NumberToTakeOut
                if NewTotal >= 0:
                    NewTotal = str(NewTotal)
                    command = f"UPDATE items SET UnitsLeft = '{NewTotal}' WHERE ItemName = '{ItemName}'"
                    cursor.execute(command)
            except:
                pass
            
        conn.commit()
        cursor.close()
        self.p_price = []
        self.p_name = []
        self.p_amount = []
        self.LoadSearchBarTable()
        self.searchpage.Clearbasket()
        
    def removeItem(self):
        index = self.search_table.currentIndex()
        row = index.row()
        self.searchpage.removeItem(row)
if __name__ == "__main__":
    Create_table()
    #start the application
    app = QApplication(sys.argv)
    #open the main window
    UIWindow = Search()
    #start app loop
    app.exec_()
