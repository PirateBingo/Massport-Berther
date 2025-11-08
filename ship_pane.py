import os
import json
import random
import numpy as np
import enum
from operator import call

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

import port_items
from main import get_icon

# https://en.wikipedia.org/wiki/Port_and_starboard
class Side(enum.Enum):
    port = 0 # Left side
    starboard = enum.auto() # Right side
    both = enum.auto()

COLUMN_COUNT = 2

ADD_ICON = get_icon("add")
ASTERISK_ICON = get_icon("asterisk")
INVALID_ICON = get_icon("invalid")
SIDE_ICONS = {Side.both: get_icon("sides_both"),
              Side.port: get_icon("sides_port"),
              Side.starboard: get_icon("sides_starboard")}
SHIP_DIR = os.path.join(os.getcwd(), "ships")
ship_path = lambda s = str: os.path.join(SHIP_DIR, s)

# List of allowed patterns for ships
pattern_arr = list(Qt.BrushStyle)
pattern_arr.remove(Qt.BrushStyle.LinearGradientPattern)
pattern_arr.remove(Qt.BrushStyle.RadialGradientPattern)
pattern_arr.remove(Qt.BrushStyle.ConicalGradientPattern)
pattern_arr.remove(Qt.BrushStyle.TexturePattern)
pattern_arr.remove(Qt.BrushStyle.NoBrush)

class StyleIcon(QIcon):
    class IconEngine(QIconEngine):
        def __init__(self, value: QColor | Qt.BrushStyle):
            super().__init__()
            self.value = value

        def paint(self, painter: QPainter, rect, mode, state):
            brush = QBrush()
            if type(self.value) == Qt.BrushStyle:
                brush.setColor(Qt.GlobalColor.white)
                brush.setStyle(self.value)
            elif type(self.value) == QColor:
                brush.setColor(self.value)
                brush.setStyle(Qt.BrushStyle.SolidPattern)
            painter.fillRect(rect, brush)

        def pixmap(self, size: QSize, mode, state):
            pixmap = QPixmap(size)
            painter = QPainter(pixmap)
            self.paint(painter, pixmap.rect(), mode, state)
            painter.end()
            return pixmap

    def __init__(self, value: QColor | Qt.BrushStyle):
        super().__init__(self.IconEngine(value))

class PatternDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.Popup)
        self.setModal(True)
        self.setWindowTitle("Select Pattern")

        self.button = QPushButton("Ok")
        self.button.setEnabled(False)
        self.button.pressed.connect(self.return_pattern)

        self.list = QTableWidget()
        self.list.setRowCount(len(pattern_arr))
        self.list.setColumnCount(2)
        self.list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.list.verticalHeader().hide()
        self.list.horizontalHeader().hide()
        for i in enumerate(pattern_arr):
            label = QTableWidgetItem(i[1].name)
            label.setFlags(Qt.ItemFlag.ItemIsSelectable)
            self.list.setItem(i[0], 0, label)

            item = QTableWidgetItem(StyleIcon(i[1]), '')
            item.setFlags(~Qt.ItemFlag.ItemIsEditable)
            self.list.setItem(i[0], 1, item)
        self.list.itemSelectionChanged.connect(self.item_selected)

        self.setLayout(QGridLayout())
        self.layout().addWidget(self.list, 0, 0, 1, 3)
        self.layout().addWidget(self.button, 1, 1, 1, 1)
    
    @Slot()
    def item_selected(self):
        if len(self.list.selectedItems()) == 0:
            self.button.setEnabled(False)
        else:
            self.button.setEnabled(True)

    @Slot()
    def return_pattern(self) -> Qt.BrushStyle:
        self.accept()
        return Qt.BrushStyle(pattern_arr[self.list.selectedItems()[0].row()])

class WarningDialog(QDialog):
    def __init__(self, text: str):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.Popup)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("Warning")

        # Define warning message
        self.message = QLabel(text)

        # Define "ok" button
        self.button = QPushButton("Ok")
        self.button.pressed.connect(lambda: self.done(1))
        self.button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.button.setFocus()

        # Layout Configuration
        self.setLayout(QGridLayout())
        self.layout().addWidget(self.message, 1, 1, 1, 1)
        self.layout().addWidget(self.button, 2, 1, 1, 1)

DISPLAY_ITEM_FLAGS = (~Qt.ItemFlag.ItemIsEditable | ~Qt.ItemFlag.ItemIsEditable)

class Label(QStandardItem):
    def __init__(self, item_text: str = None, item_type = None, isValid: bool = False):
        self.item_type = item_type
        self.item_text = item_text
        self.isValid = isValid
        super().__init__(self.item_text)

class StaticItem(Label):
    def __init__(self, text: str = None):
        self.item_text = text if type(text) == str else ''
        super().__init__(self.item_text)
        self.setEditable(False)
        self.setSelectable(False)
        self.setText(self.item_text)

class AddShipButton(QStandardItem):
    def __init__(self):
        super().__init__("Add ship")
        self.setFlags(DISPLAY_ITEM_FLAGS)
        icon = QIcon(ADD_ICON)
        self.setIcon(icon)

class AddDoorButton(QStandardItem):
    def __init__(self):
        super().__init__("Add door")
        self.setFlags(DISPLAY_ITEM_FLAGS)
        icon = QIcon(ADD_ICON)
        self.setIcon(icon)

class ColorButton(Label):
    def __init__(self, color: QColor | None = None):
        super().__init__(item_type=QColor, isValid=True)
        self.setFlags(DISPLAY_ITEM_FLAGS)
        if color == None:
            self.update_color(QColor(Qt.GlobalColor(random.randint(0, len(Qt.GlobalColor) - 1))))
        else:    
            self.update_color(color)

    def update_color(self, color: QColor):
        self.setIcon(StyleIcon(color))

class PatternButton(Label):
    def __init__(self, pattern: Qt.BrushStyle | None = None):
        super().__init__(item_type=Qt.BrushStyle, isValid=True)
        self.setFlags(DISPLAY_ITEM_FLAGS)
        if pattern == None:
            self.update_pattern(pattern_arr[random.randint(0, len(pattern_arr) - 1)])
        else:
            self.update_pattern(pattern)
    
    def update_pattern(self, pattern: Qt.BrushStyle):
        self.setIcon(StyleIcon(Qt.BrushStyle(pattern)))

class SideButton(Label):
    def __init__(self):
        super().__init__(item_type=Side, isValid=True)
        self.setFlags(DISPLAY_ITEM_FLAGS)
        self.i = 0
        self.side = Side.both
        self.update_side()
    
    def update_side(self):
        icon = QIcon(SIDE_ICONS.get(self.side))
        self.setIcon(icon)
    
    def increment_side(self):
        self.i = (self.i + 1) % len(Side)
        self.side = Side(self.i)
        self.update_side()

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

class ShipModel(QStandardItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(0, COLUMN_COUNT, parent)
        self.setHorizontalHeaderLabels([''] * COLUMN_COUNT) # Empty headers
        self.change_connect = lambda: self.itemChanged.connect(lambda x: self.check_ships())
        self.change_disconnect = lambda: self.itemChanged.disconnect()
        self._add_ship_button_append()
        self.change_connect()

    def item_press(self, index: QModelIndex):
        button = self.itemFromIndex(index)
        if button.__class__ == AddShipButton:
            self.add_ship()
        elif button.__class__ == AddDoorButton:
            ship: Ship
            ship = button.parent()
            ship.add_door()
        elif button.__class__ == PatternButton:
            button: PatternButton
            pattern_dialog = PatternDialog()
            pattern_dialog.exec()
            pattern = pattern_dialog.return_pattern()
            button.update_pattern(pattern)
        elif button.__class__ == ColorButton:
            button: ColorButton
            color_dialog = QColorDialog()
            color_dialog.exec()
            color = color_dialog.selectedColor()
            button.update_color(color)
        elif button.__class__ == SideButton:
            button: SideButton
            button.increment_side()

    def add_ship(self, name: str | None = None):
        self.removeRow(self.add_ship_button.row())
        if type(name == None):
            Ship(self, f"Ship {self.rowCount() + 1}")
        elif type(name == str):
            Ship(self, name)
        self._add_ship_button_append()
        self.check_ships()

    def _add_ship_button_append(self):
        self.add_ship_button = AddShipButton()
        self.appendRow(self.add_ship_button)

    @Slot()
    def check_ships(self):
        i = 0
        while True:
            item = self.item(i, 0)
            if item == None or item.__class__ == AddShipButton:
                break
            else:
                ship: Ship
                ship = item
                ship.check()
            i += 1

    def _check_value(self, item: QStandardItem):
        if item.__class__ == AddShipButton:
            pass 
        #TODO: Ship and Door name checking
        elif item.__class__ == Ship or item.__class__ == Ship.Door:
           pass
        else:
            ship_item: Ship.ShipItem
            self.change_disconnect()
            ship_item = self.itemFromIndex(item.index().siblingAtColumn(0))
            ship_item.check_valid()
            self.change_connect()

class Ship(QStandardItem):
    class ShipItem(QStandardItem):
        def __init__(self, parent: QStandardItem, name: str, json_name: str, typing):
            super().__init__(name)
            self.name = name
            self.json_name = json_name
            self.typing = typing
            self.valid = False

            # Add to model
            if self.typing == Qt.BrushStyle:
                entry = PatternButton()
            elif self.typing == QColor:
                entry = ColorButton()
            elif self.typing == Side:
                entry = SideButton()
            else:
                entry = QStandardItem()
            parent.appendRow([self, entry])
            self.setText(self.name)

        def check_valid(self) -> bool:
            try:
                item = self.model().itemFromIndex(self.index().siblingAtColumn(1))
                if(item.__class__ == ColorButton or
                   item.__class__ == PatternButton or
                   item.__class__ == SideButton):
                    self.isValid = True
                else:
                    if item.text() == '':
                        self.isValid = False
                    else:
                        item_value = call(self.typing, item.text())
                        if type(item_value) == self.typing:
                            self.isValid = True
                        else:
                            self.isValid = False
            except Exception as error:
                self.isValid = False
                WarningDialog(str(error)).exec()
            if self.isValid:
                color = Qt.GlobalColor.green
            else:
                color = Qt.GlobalColor.red
                item.clearData()
            self.setForeground(color)

    class Door(ShipItem):
        def __init__(self, parent: QStandardItem, name: str):
            super().__init__(parent, name, name, type(self))
            parent.ShipItem(self, "Side", "side", Side)
            parent.ShipItem(self, "Bow Distance", "bow_distance", float)
            parent.ShipItem(self, "Stern Distance", "stern_distance", float)
            parent.ShipItem(self, "Width", "width", float)
            parent.ShipItem(self, "Height", "height", float)

    def __init__(self, parent: QStandardItemModel, name: str):
        super().__init__(name)
        parent.setItem(parent.rowCount(), 0, self)
        self._init_vals()

    def _init_vals(self):
        self.ShipItem(self, "Length", "length", float)
        self.ShipItem(self, "Pattern", "pattern", Qt.BrushStyle)
        self.ShipItem(self, "Color", "color", QColor)
        self.ShipItem(self, "Width", "width", float)
        self._add_door_button_append()
    
    def _add_door_button_append(self):
        self.add_door_button = AddDoorButton()
        self.appendRow(self.add_door_button)
    
    def add_door(self, name: str | None = None):
        self.removeRow(self.rowCount() - 1)
        if type(name == None):
            # Change 3 if more ship variables added
            self.Door(self, f"Door {self.rowCount() - 3}") 
        elif type(name == str):
            self.Door(self, name)
        self._add_door_button_append()
        self.check()
    
    def check(self):
        self.model().change_disconnect()
        i = 0
        while True:
            item = self.child(i, 0)
            if item.__class__ == Ship.ShipItem:
                item: Ship.ShipItem
                item.check_valid()
            elif item.__class__ == Ship.Door:
                j = 0
                while True:
                    door_item = item.child(j, 0)
                    if door_item.__class__ == Ship.ShipItem:
                        door_item: Ship.ShipItem
                        door_item.check_valid()
                    else:
                        break
                    j += 1
            else:
                break
            i += 1
        self.model().change_connect()

# # Debug
# x = port_items.Ship("Ship Test", 5, Qt.BrushStyle.Dense3Pattern, Qt.GlobalColor.gray, 5)
# print(f"{x.ship_name}, {x.length}, {x.pattern}, {x.color}, {x.width}")
# x = port_items.Ship.from_dict(
#                     {"ship_name": "sdsd",
#                      "length": 1.0,
#                      "pattern": 1,
#                      "color": 1,
#                      "width": 1,
#                      "ththt": {
#                          "side": 1,
#                          "bow_distance": 1,
#                          "stern_distance": 1,
#                          "width": 1,
#                          "height": 1,
#                          "height_above_waterline": 1
#                      },
#                      "sds": {
#                          "side": 1,
#                          "bow_distance": 1,
#                          "stern_distance": 1,
#                          "width": 1,
#                          "height": 1,
#                          "height_above_waterline": 1
#                      }})
# print(f"{x.ship_name}, {x.length}, {x.pattern}, {x.color}, {x.width}")
# print(x.to_dict())
# print(x.doors[0].to_dict())
# print(x.get_height())
# debug_message = "DEBUG END"
# print(debug_message.rjust(82 - len(debug_message)))