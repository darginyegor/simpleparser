import requests
from bs4 import BeautifulSoup
import sys
import json
import time
from PyQt5 import QtCore, QtGui, QtWidgets,  uic
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class App(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi('ui/main.ui', self)
        self.setWindowTitle('SimpleParser')
        self.catalog = Catalog('https://orangebattery.ru/category')
        self.refreshButton.clicked.connect(self.update_catalog)
        self.catalogTreeWidget.itemClicked.connect(self.display_product)

    def load(self):
        try:
            f = open('catalog.cache')
            self.catalog.data[0] = json.load(f)
            f.close()
            self.updateLabel.setText('Последнее обновление: ' + time.ctime(self.catalog.data[0]['updated']))
            self.to_tree_level(self.catalog.data[0]['children'], self.catalogTreeWidget, 1)
        except FileNotFoundError:
            self.update_catalog()

    def cache(self):
        f = open('catalog.cache', 'w')
        json.dump(self.catalog.data[0], f, indent='\n', ensure_ascii=False)
        f.close()

    def update_catalog(self):
        self.catalog = Catalog('https://orangebattery.ru/category')
        self.catalogTreeWidget.clear()
        self.refreshButton.setDisabled(True)
        self.catalog.parse()
        self.to_tree_level(self.catalog.data[0]['children'], self.catalogTreeWidget, 1)
        self.updateLabel.setText('Последнее обновление: ' + time.ctime(self.catalog.data[0]['updated']))
        self.cache()
        self.refreshButton.setDisabled(False)

    def to_tree_level(self, list_, target, is_root=0):
        for i in list_:
            item = QTreeWidgetItem()
            item.setText(0, i['name'])
            target.addTopLevelItem(item) if is_root else target.addChild(item)
            if 'children' in i:
                self.to_tree_level(i['children'], item)
            else:
                item.description = i['description']

    def display_product(self, product):
        self.productDisplay.setText(str(product.description))


class Catalog:
    def __init__(self, url: str):
        self.data = [{'name:': 'root', 'url': url, 'products': 0, 'categories': 0}]
        self.url = url

    @staticmethod
    def __load_children(target):
        for i in target:
            response = requests.get(i['url'], verify=False)
            soup = BeautifulSoup(response.text, 'lxml').find(id='content')
            children = []  # [{'url': i.a['href']} for i in soup.find_all(class_='col-md-4')]
            if soup.find(class_='col-md-4 text-center'):
                for j in soup.find_all(class_='col-md-4 text-center'):
                    child = {'url': j.a['href'], 'name': j.find('h4').text}
                    children.append(child)
                i['children'] = children
                Catalog.__load_children(i['children'])
            elif soup.find(class_='product-list'):
                for j in soup.find_all(class_='product-list'):
                    a = j.find(class_='caption').a
                    child = {'url': a['href'], 'name': a.text, 'description': j.text}
                    children.append(child)
                    print('New product found: ' + child['name'])
                i['children'] = children

    def parse(self):
        Catalog.__load_children(self.data)
        self.data[0]['updated'] = time.time()


myApp = QtWidgets.QApplication(sys.argv)
mw = App()
mw.show()
mw.load()
sys.exit(myApp.exec_())