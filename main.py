import requests
from bs4 import BeautifulSoup
import sys
import json
import time
from PyQt5 import QtCore, QtGui, QtWidgets,  uic
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QPixmap, QImage
import threading


class App(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi('ui/main.ui', self)
        self.setWindowTitle('SimpleParser')
        self.catalog = Catalog('https://orangebattery.ru/category')
        self.refreshButton.clicked.connect(self.start_updating)
        self.catalogTreeWidget.itemClicked.connect(self.display_product)

    # Загрузка кэшированного каталога
    def load(self):
        try:
            f = open('catalog.cache')
            self.catalog.data = json.load(f)
            f.close()
            self.updateLabel.setText('Последнее обновление: ' + time.ctime(self.catalog.data['updated']))
            self.productCounter.setText(str(self.catalog.data['products']))
            self.categoryCounter.setText(str(self.catalog.data['categories']))
            self.to_tree_level(self.catalog.data['children'], self.catalogTreeWidget, 1)
        except FileNotFoundError:
            self.update_catalog()

    # Сохранение каталога в кэш
    def cache(self):
        f = open('catalog.cache', 'w')
        json.dump(self.catalog.data, f, indent='\n', ensure_ascii=False)
        f.close()

    def start_updating(self):
        self.updateLabel.setText('Обновление каталога...')
        self.productCounter.setText('...')
        self.categoryCounter.setText('...')
        self.refreshButton.setDisabled(True)
        self.catalog = Catalog('https://orangebattery.ru/category')
        self.catalogTreeWidget.clear()
        t = threading.Thread(target=self.update_catalog)
        t.start()

    # Обновление каталога
    def update_catalog(self):
        try:
            self.catalog.parse()
            self.to_tree_level(self.catalog.data['children'], self.catalogTreeWidget, 1)
            self.updateLabel.setText('Последнее обновление: ' + time.ctime(self.catalog.data['updated']))
            self.cache()
        except requests.exceptions.ConnectionError:
            self.show_message('Ошибка', 'Ошибка обновления')
        self.refreshButton.setDisabled(False)
        self.productCounter.setText(str(self.catalog.data['products']))
        self.categoryCounter.setText(str(self.catalog.data['categories']))

    # Преобрахование массива в уровень дерева QTreeWidget
    def to_tree_level(self, list_, target, is_root=0):
        for i in list_:
            item = QTreeWidgetItem()
            item.setText(0, i['name'])
            target.addTopLevelItem(item) if is_root else target.addChild(item)
            if 'children' in i:
                self.to_tree_level(i['children'], item)
            else:
                item.url = i['url']

    # Отображение сведений о продукте
    def display_product(self, item):
        try:
            product = (self.catalog.get_product(item))
        except requests.exceptions.ConnectionError:
            self.show_message('Ошибка',
                              'Ошибка получения данных. Обновите каталог или проверье подключение к интернету!')
            return
        thumbnail_img = QImage.fromData(product['thumb'])
        thumbnail_pixmap = QPixmap.fromImage(thumbnail_img)
        self.productDisplay.setHtml(product['description'])
        self.productThumbLabel.setPixmap(thumbnail_pixmap.scaled(192, 192))
        self.productName.setText(item.text(0))
        self.productPrice.setText('Цена: ' + product['price'] + ' р.')

    @staticmethod
    def disable(*args):
        for element in args:
            element.setDisabled(True)

    @staticmethod
    def enable(*args):
        for element in args:
            element.setDisabled(False)

    @staticmethod
    def show_message(title, msg):
        print('Message: ' + msg)
        mb = QtWidgets.QMessageBox()
        mb.setWindowTitle(title)
        mb.setText(msg)
        mb.exec()

    @staticmethod
    def show_error(title, msg):
        print('Message: ' + msg)
        mb = QtWidgets.QErrorMessage()
        mb.setWindowTitle(title)
        mb.setText(msg)
        mb.exec()


class Catalog:
    def __init__(self, url: str):
        self.data = {'name:': 'root',
                     'url': url,
                     'products': 0,
                     'categories': 0}
        self.url = url

    # Рекурсивный парсинг дочерних элементов
    def __parse_children(self, target):
        for i in target:
            response = requests.get(i['url'], verify=False)
            soup = BeautifulSoup(response.text, 'lxml').find(id='content')
            children = []
            if soup.find(class_='col-md-4 text-center'):
                for j in soup.find_all(class_='col-md-4 text-center'):
                    child = {'url': j.a['href'] + '?limit=100', 'name': j.find('h4').text}
                    children.append(child)
                    self.data['categories'] += 1
                i['children'] = children
                self.__parse_children(i['children'])
            elif soup.find(class_='product-list'):
                for j in soup.find_all(class_='product-list'):
                    a = j.find(class_='caption').a
                    child = {'url': a['href'], 'name': a.text, 'description': j.text}
                    children.append(child)
                    print('New product found: ' + child['name'])
                    self.data['products'] += 1
                i['children'] = children

    # Парсинг каталога
    def parse(self):
        self.__parse_children([self.data])
        self.data['updated'] = time.time()

    def get_product(self, item):
        response = requests.get(item.url, verify=False)
        soup = BeautifulSoup(response.text, 'lxml').find(id='content')
        description = str(soup.find(id='tab-description')) + str(soup.find(id='tab-specification'))
        price = soup.find(class_='rubel').text
        name = ''
        thumb_url = soup.find(class_='thumbnail')['href']
        thumbnail = requests.get(thumb_url, verify=False)
        product = {
                    'description': description,
                    'thumb': thumbnail.content,
                    'name': name,
                    'price': price
                   }
        return product


def main():
    myApp = QtWidgets.QApplication(sys.argv)
    app = App()
    app.show()
    app.load()
    sys.exit(myApp.exec_())

main()
