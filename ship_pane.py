import os
import json
import numpy as np

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

import port_items
from main import get_icon

ADD_ICON = get_icon("add")
ASTERISK_ICON = get_icon("asterisk")
INVALID_ICON = get_icon("invalid")

SHIP_DIR = os.path.join(os.getcwd(), "ships")
ship_path = lambda s = str: os.path.join(SHIP_DIR, s)

class ShipPane(QFrame):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self._ship_view = self.ShipView(parent)

    class ShipView(QTreeView):
        def __init__(self, parent: QObject=None):
            super().__init__(parent, wordWrap=True, expandsOnDoubleClick=True,
                             uniformRowHeights=True)
            self.setModel(ShipModel(self))
            self.clicked.connect(self.model().item_press)
        #TODO: Enforce equal column widths

# class ShipItem(QStandardItem, port_items.Ship):
#     def __init__(self, path: str | None = None):
#         port_items.Ship.__init__(self, ship_path(path) if type(path) is str else None)

#         # Initialize root element for name
#         name_item = QStandardItem(self.__dict__()["name"])
#         name_item.setEditable(False)
#         name_item.setDragEnabled(True)
#         name_item.setDropEnabled(True)
#         QStandardItem.__init__(self, name_item)

#         # Add ship items
#         def add_item(key, value):
#             key_item = QStandardItem(key)
#             key_item.setEditable = False
#             self.appendRow([key_item, QStandardItem(str(value))])
#         for key in self.__dict__().keys():
#             if type(self.__dict__()[key]) != list:
#                 if key != "name":
#                     add_item(key, self.__dict__()[key])

#             # Add ship's doors and their properties
#             else:
#                 for door in self.__dict__()[key]:
#                     door_item = QStandardItem(door.__dict__()["name"])
#                     door_item.setEditable(False)
#                     self.appendRow(door_item)
#                     for door_key in door.__dict__():
#                         if door_key != "name":
#                             door_attr = QStandardItem(door_key)
#                             door_attr.setEditable(True)
#                             door_item.appendRow([
#                             door_attr, 
#                             QStandardItem(str(door.__dict__()[door_key]))])
#         self.isValid = True
class SpawnShipButton(QStandardItem):
    def __init__(self):
        super().__init__("Add ship")
        icon = QIcon(ADD_ICON)
        self.setIcon(icon)

class SpawnDoorButton(QStandardItem):
    def __init__(self):
        super().__init__("Add door")
        icon = QIcon(ADD_ICON)
        self.setIcon(icon)

class CustomIconEngine(QIconEngine):
    def __init__(self, special_value: Qt.GlobalColor | Qt.BrushStyle):
        self.special_value = special_value
        super().__init__()

    def paint(self, painter: QPainter, rect, mode, state):
        brush = QBrush()
        if type(self.special_value) == Qt.BrushStyle:
            brush.setColor(Qt.GlobalColor.gray)
            brush.setStyle(self.special_value)
        elif type(self.special_value) == Qt.GlobalColor:
            brush.setColor(self.special_value)
            brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.fillRect(rect, brush)

    def pixmap(self, size: QSize, mode, state):
        pixmap = QPixmap(size)
        painter = QPainter(pixmap)
        self.paint(painter, pixmap.rect(), mode, state)
        painter.end()
        return pixmap

class ShipItem(QStandardItem):
    def __init__(self,
                 ship: port_items.Ship = None,
                 color: Qt.GlobalColor = None,
                 pattern: Qt.BrushStyle = None):
        # Initialize root element for name
        super().__init__('')
        self.setFlags(Qt.ItemFlag.ItemIsEditable |
                      Qt.ItemFlag.ItemIsDragEnabled | 
                      Qt.ItemFlag.ItemIsDropEnabled)

        # Add ship items
        def add_item(key, special_value: Qt.GlobalColor | Qt.BrushStyle = None):
            key_item = QStandardItem(key)
            key_item.setEditable = False
            value_item = QStandardItem(str(''))
            if type(special_value) != None:
                value_item.setIcon(QIcon(CustomIconEngine(special_value)))
            self.appendRow([key_item, value_item])
        for key in port_items.SHIP_ATTR.keys():
            if key == "Pattern":
                special_value = Qt.BrushStyle.Dense3Pattern
            elif key == "Color":
                special_value = Qt.GlobalColor.blue
            else:
                special_value = None
            add_item(key, special_value)

        # Add door spawning button
        self._door_button = SpawnDoorButton()
        self.appendRow(self._door_button)

    def add_door(self):
        self.removeRow(self._door_button.row())

        door = QStandardItem('')
        self.appendRow(door)

        # Add door items
        def add_item(key, value):
            key_item = QStandardItem(key)
            key_item.setEditable = False
            door.appendRow([key_item, QStandardItem(str(value))])
        for key in port_items.DOOR_ATTR.keys():
            add_item(key, '')
        self._door_button = SpawnDoorButton()
        self.appendRow(self._door_button)

        #     # Add ship's doors and their properties
        #     else:
        #         for door in self.__dict__()[key]:
        #             door_item = QStandardItem(door.__dict__()["name"])
        #             door_item.setEditable(False)
        #             self.appendRow(door_item)
        #             for door_key in door.__dict__():
        #                 if door_key != "name":
        #                     door_attr = QStandardItem(door_key)
        #                     door_attr.setEditable(True)
        #                     door_item.appendRow([
        #                     door_attr, 
        #                     QStandardItem(str(door.__dict__()[door_key]))])
        # self.isValid = True

class ShipModel(QStandardItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(0, 2, parent)
        self.setHorizontalHeaderLabels(['','']) # Empty headers
        self._read_ships()
        self._ship_button = SpawnShipButton()
        self.setItem(0, self._ship_button)
        # self.itemChanged.connect(lambda a = QStandardItem: print(a.index())) #TODO: implement function

    def _read_ships(self):
        for path in os.listdir(SHIP_DIR):
            if os.path.splitext(path)[1] == ".json":
                root = self.invisibleRootItem()
                root.appendRow(ShipItem(path))

    def _read_ship(self, json_path):
        # Load json data
        if os.path.splitext(json_path)[1] != ".json":
            raise ValueError("Argued file is not a .json type")
        ship_dict = port_items.Ship(json_path)
        ship_name = os.path.splitext(os.path.basename(ship_dict))[0]
        ship_item = ShipItem(ship_name)

    def _write_ship(self, ship: port_items.Ship):
        path = ship_path(ship._name)
        if os.path.isfile(path):
            #TODO: Handle duplicate file names
            pass

        if len(ship._doors) == 0:
            #TODO: Handle door null set
            pass

        # Write file
        with open(path, "w+") as json_file: self._json = json.load(json_file)   

    def _add_ship(self, button: SpawnShipButton):
        self.removeRow(button.row())
        self.appendRow(ShipItem())
        self.appendRow(SpawnShipButton())

    def item_press(self, index: QModelIndex):
        button = self.itemFromIndex(index)
        if button.__class__ == SpawnShipButton:
            self._add_ship(button)
        elif button.__class__ == SpawnDoorButton:
            button.parent().add_door()