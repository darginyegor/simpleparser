import unittest
import validictory
import sys
from main import Catalog, App
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class TestCatalogMethods(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog('https://orangebattery.ru/category')
        self.catalog_schema = {
            "properties": {
                "updated" : {
                    "type": "number"
                },
                "children": {
                    "type": "array",
                    "uniqueItems": True
                },
                'categories': {
                    "type": "integer"
                },
                'products': {
                    "type": "integer"
                }
            }
        }
        self.product_schema = {
            'properties': {
                'description': {
                    'type': 'string',
                    'minLength': 100
                },
                'thumb': {
                    'type': 'any'
                },
                'name': {
                    'type': 'string'
                },
                'price': {
                    'type': 'string',
                    'minLength': 2

                }
            }
        }
        self.catalog_example = {
            'name:': 'root',
            'url': 'http://some.url.ru',
            'products': 2,
            'categories': 1,
            'children': [
                {
                    "name": 'Category1',
                    'url': 'http://some.url.ru/category1',
                    'children': [
                        {
                            "name": 'Product1',
                            'url': 'http://some.url.ru/category1/product1',
                        },
                        {
                            "name": 'Product2',
                            'url': 'http://some.url.ru/category1/product2',
                        }
                    ]
                }
            ]
        }

    def test_parse(self):
        self.catalog.parse()
        self.assertIsNone(validictory.validate(self.catalog.data, self.catalog_schema))

    def test_get_product(self):
        url = 'http://orangebattery.ru/dt_12045'
        self.assertIsNone(validictory.validate(self.catalog.get_product(url), self.product_schema))

    def test_cache(self):
        self.catalog.data = self.catalog_example
        self.catalog.cache('test_cache.cache')
        f = open('test_cache.cache').read()
        self.assertIsNotNone(f)

    def test_load(self):
        self.catalog.load('test_load.cache')
        self.assertIsNone(validictory.validate(self.catalog.data, self.catalog_schema))


# class TestAppMethods(unittest.TestCase):
#     def setUp(self):
#         myApp = QtWidgets.QApplication(sys.argv)
#         self.app = App()
#         self.tree = QTreeWidget()
#         self.catalog_example = {
#             'name:': 'root',
#             'url': 'http://some.url.ru',
#             'products': 2,
#             'categories': 1,
#             'children': [
#                 {
#                     "name": 'Category1',
#                     'url': 'http://some.url.ru/category1',
#                     'children': [
#                         {
#                             "name": 'Product1',
#                             'url': 'http://some.url.ru/category1/product1',
#                         },
#                         {
#                             "name": 'Product2',
#                             'url': 'http://some.url.ru/category1/product2',
#                         }
#                     ]
#                 }
#             ]
#         }
#         self.app.to_tree_level(self.catalog_example['children'], self.tree, 1)
#
#     def test_to_tree_level(self):
#         tree_example = QTreeWidget()
#         tree_category1 = QTreeWidgetItem()
#         tree_category1.setText(0, 'Category1')
#         tree_product1 = QTreeWidgetItem()
#         tree_product1.setText(0, 'Product1')
#         tree_product2 = QTreeWidgetItem()
#         tree_product2.setText(0, 'Product2')
#         tree_example.addTopLevelItem(tree_category1)
#         tree_category1.addChildren([tree_product1, tree_product2])
#         self.assertEqual(self.tree, tree_example)
#
#
# if __name__ == '__main__':
#     unittest.main()
