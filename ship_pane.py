import os
import json

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

import port_items

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
            self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            
        #TODO: Enforce equal column widths

class ShipItem(port_items.Ship, QStandardItem):
    def __init__(self, path):
        port_items.Ship.__init__(self, ship_path(path))

        # Initialize root element for name
        name_item = QStandardItem(self.__dict__()["name"])
        name_item.setEditable(False)
        name_item.setDragEnabled(True)
        name_item.setDropEnabled(True)
        QStandardItem.__init__(self, name_item)

        # Add ship items
        def add_item(key, value):
            key_item = QStandardItem(key)
            key_item.setEditable = False
            self.appendRow([key_item, QStandardItem(str(value))])
        for key in self.__dict__().keys():
            if type(self.__dict__()[key]) != list:
                if key != "name":
                    add_item(key, self.__dict__()[key])

            # Add ship's doors and their properties
            else:
                for door in self.__dict__()[key]:
                    door_item = QStandardItem(door.__dict__()["name"])
                    door_item.setEditable(False)
                    self.appendRow(door_item)
                    for door_key in door.__dict__():
                        if door_key != "name":
                            door_attr = QStandardItem(door_key)
                            door_attr.setEditable(True)
                            door_item.appendRow([
                            door_attr, QStandardItem(str(door.__dict__()[door_key]))])

class ShipModel(QStandardItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(0, 2, parent)
        self.setHorizontalHeaderLabels(['','']) # Empty headers
        self.setItem
        self.ship_arr = []
        self._read_ships()
        self.itemChanged.connect(lambda a = QStandardItem: print(a.index()))

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