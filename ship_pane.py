import os
import json
import random
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

DISPLAY_ITEM_FLAGS = (~Qt.ItemFlag.ItemIsEditable)

class StaticItem(QStandardItem):
    def __init__(self, text: str | None):
        super().__init__()
        self.setFlags(DISPLAY_ITEM_FLAGS)
        if type(text) == str:
            self.setText(text)
        else:
            self.setText('')

class SpawnShipButton(QStandardItem):
    def __init__(self):
        super().__init__("Add ship")
        self.setFlags(DISPLAY_ITEM_FLAGS)
        icon = QIcon(ADD_ICON)
        self.setIcon(icon)

class SpawnDoorButton(QStandardItem):
    def __init__(self):
        super().__init__("Add door")
        self.setFlags(DISPLAY_ITEM_FLAGS)
        icon = QIcon(ADD_ICON)
        self.setIcon(icon)

class ColorButton(QStandardItem):
    def __init__(self, color: Qt.GlobalColor | QColor):
        super().__init__('')
        self.setFlags(DISPLAY_ITEM_FLAGS)
        if type(color) == Qt.GlobalColor:
            color = Qt.GlobalColor(color)
        elif type(color) == QColor:
            color = QColor(color)
        self.setIcon(QIcon(CustomIconEngine(color)))

class PatternButton(QStandardItem):
    def __init__(self, pattern: Qt.BrushStyle):
        super().__init__('')
        self.setFlags(DISPLAY_ITEM_FLAGS)
        self.setIcon(QIcon(CustomIconEngine(Qt.BrushStyle(pattern))))

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
        def add_item(key):
            key_item = QStandardItem(key)
            key_item.setEditable = False
            if key == "Color":
                value_item = ColorButton(random.randint(0, len(Qt.GlobalColor) - 1))
            elif key == "Pattern":
                pattern_arr = list(Qt.BrushStyle)
                pattern_arr.remove(Qt.BrushStyle.LinearGradientPattern)
                pattern_arr.remove(Qt.BrushStyle.RadialGradientPattern)
                pattern_arr.remove(Qt.BrushStyle.ConicalGradientPattern)
                pattern_arr.remove(Qt.BrushStyle.TexturePattern)
                pattern_arr.remove(Qt.BrushStyle.NoBrush)
                value_item = PatternButton(pattern_arr[random.randint(0, len(pattern_arr) - 1)])
            else:
                value_item = QStandardItem(str(''))
            self.appendRow([key_item, value_item])
        for key in port_items.SHIP_ATTR.keys(): add_item(key)

        # Add door spawning button
        self._door_button = SpawnDoorButton()
        self.appendRow(self._door_button)

    def add_door(self):
        self.removeRow(self._door_button.row())

        door = QStandardItem('')
        self.appendRow(door)

        # Add door items
        def add_item(key, value):
            key_item = StaticItem(key)
            door.appendRow([key_item, QStandardItem(str(value))])
        for key in port_items.DOOR_ATTR.keys():
            add_item(key, '')
        self._door_button = SpawnDoorButton()
        self.appendRow(self._door_button)

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
        elif button.__class__ == ColorButton:
            print("ColorDialog")
        elif button.__class__ == PatternButton:
            print("PatternDialog")