import os
import json
import random
import numpy as np
import enum
import typing
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

LABEL_FLAGS = (Qt.ItemFlag.ItemIsEnabled)
LABEL_SELECTABLE_FLAGS = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
ENTRY_FLAGS = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
SHIP_FLAGS = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)

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
            label.setFlags(LABEL_FLAGS)
            self.list.setItem(i[0], 0, label)

            item = QTableWidgetItem(StyleIcon(i[1]), '')
            item.setFlags(LABEL_SELECTABLE_FLAGS)
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

class Label(QStandardItem):
    def __init__(self, text: str = None):
        self.item_text = text if type(text) == str else ''
        super().__init__(self.item_text)
        self.setFlags(LABEL_FLAGS)

class Entry(QStandardItem):
    def __init__(self):
        super().__init__('')
        self.setFlags(ENTRY_FLAGS)
class AddShipButton(QStandardItem):
    def __init__(self):
        super().__init__("Add ship")
        self.setFlags(LABEL_SELECTABLE_FLAGS)
        icon = QIcon(ADD_ICON)
        self.setIcon(icon)

class AddDoorButton(QStandardItem):
    def __init__(self):
        super().__init__("Add door")
        self.setFlags(LABEL_SELECTABLE_FLAGS)
        icon = QIcon(ADD_ICON)
        self.setIcon(icon)

class ValueButton(QStandardItem):
    def __init__(self, typing):
        super().__init__('')
        self.setFlags(LABEL_SELECTABLE_FLAGS)
        self.typing = typing
        self.value = None

    def set_value(self, value):
        self.value = call(self.typing, value)
        self.setIcon(StyleIcon(self.value))

class ColorButton(ValueButton):
    def __init__(self, color: QColor | None = None):
        super().__init__(QColor)
        if color == None:
            self.set_value(Qt.GlobalColor(random.randint(0, len(Qt.GlobalColor) - 1)))
        else:    
            self.set_value(color)

class PatternButton(ValueButton):
    def __init__(self, pattern: Qt.BrushStyle | None = None):
        super().__init__(Qt.BrushStyle)
        if pattern == None:
            self.set_value(pattern_arr[random.randint(0, len(pattern_arr) - 1)])
        else:
            self.set_value(pattern)

class SideButton(ValueButton):
    def __init__(self, side: Side | None = None):
        super().__init__(Side)
        self.i = 0
        if side == None:
            self.set_value(Side.both)
        else:
            self.set_value(Side(side))
        self._update_side()

    @typing.override
    def set_value(self, value):
        if type(value) != self.typing:
            try:
                value = call(self.typing, value)
            except Exception:
                raise TypeError(f"{self.__class__} takes {self.typing} type")
        self.value = value

    def _update_side(self):
        icon = QIcon(SIDE_ICONS.get(self.value))
        self.setIcon(icon)

    def increment_side(self):
        self.i = (self.i + 1) % len(Side)
        self.value = Side(self.i)
        self._update_side()

class ShipView(QTreeView):
    def __init__(self):
        super().__init__(wordWrap=True, expandsOnDoubleClick=True,
                         uniformRowHeights=True)
        self.setModel(ShipModel(self))
        self.setObjectName("Editor")
        self.clicked.connect(self.model().item_press)

        self.setDragEnabled(True)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(True)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setSelectionMode(self.SelectionMode.SingleSelection)

        # Debug
        # x = Ship(self.model(), "Ship Test", 5, Qt.BrushStyle.Dense4Pattern,
        #             Qt.GlobalColor.blue, 5,
        #             {"sds": {"side": 2,
        #                     "bow_distance": 1,
        #                     "stern_distance": 1,
        #                     "width": 1,
        #                     "height": 1,
        #                     "height_above_waterline": 1}})
        #TODO: Enforce equal column widths

class ShipModel(QStandardItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(0, COLUMN_COUNT, parent)
        self.setHorizontalHeaderLabels([''] * COLUMN_COUNT) # Empty headers
        self._add_ship_button_append()

        # Check the validity of the ship after it's been changed
        self.change_connect = lambda: self.itemChanged.connect(lambda x: self.check_ships())
        self.change_disconnect = lambda: self.itemChanged.disconnect()
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
            button.set_value(pattern)
        elif button.__class__ == ColorButton:
            button: ColorButton
            color_dialog = QColorDialog()
            color_dialog.exec()
            color = color_dialog.selectedColor()
            button.set_value(color)
        elif button.__class__ == SideButton:
            button: SideButton
            button.increment_side()

    def add_ship(self, name: str | None = None):
        if type(name == None):
            Ship(self, f"Ship {self.rowCount()}")
        elif type(name == str):
            Ship(self, name)
        self.check_ships()

    def _add_ship_button_append(self):
        self.add_ship_button = AddShipButton()
        self.appendRow([self.add_ship_button, Label()])

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
        def __init__(self, parent: QStandardItem, name: str, typing):
            super().__init__(name)
            self.setFlags(LABEL_FLAGS)
            self.parent_item = parent
            self.name = name
            self.text_name = name.replace('_', ' ').capitalize()
            self.typing = typing
            self.valid = False

            # Set Name
            self.setText(self.text_name)
            self._add_item()

        # Add item to ship; add special button instead of an entry if necessary
        def _add_item(self):
            if self.typing == Qt.BrushStyle:
                self.entry = PatternButton()
            elif self.typing == QColor:
                self.entry = ColorButton()
            elif self.typing == Side:
                self.entry = SideButton()
            else:
                self.entry = Entry()
            self.parent_item.appendRow([self, self.entry])

        def check_valid(self) -> bool:
            try:
                item = self.model().itemFromIndex(self.index().siblingAtColumn(1))
                if(item.__class__ == ColorButton or
                   item.__class__ == PatternButton or
                   item.__class__ == SideButton):
                    self.valid = True
                else:
                    if item.text() == '':
                        self.valid = False
                    else:
                        item_value = call(self.typing, item.text())
                        if type(item_value) == self.typing:
                            self.valid = True
                        else:
                            self.valid = False
            except Exception as error:
                self.valid = False
                WarningDialog(str(error)).exec()
            if self.valid:
                color = Qt.GlobalColor.green
            else:
                color = Qt.GlobalColor.red
                item.setText('')
            self.setForeground(color)
            return self.valid

    class Door(ShipItem):
        def __init__(self, parent: QStandardItem, name: str):
            super().__init__(parent, name, type(self))
            parent.ShipItem(self, "side", Side)
            parent.ShipItem(self, "bow_distance", float)
            parent.ShipItem(self, "stern_distance", float)
            parent.ShipItem(self, "width", float)
            parent.ShipItem(self, "height", float)
            parent.ShipItem(self, "height_above_waterline", float)
            self.valid = False

        # Add door to ship, but make the entry element unchangeable
        @typing.override
        def _add_item(self):
            self.parent_item.appendRow([self, Label()])

        def is_valid(self) -> bool:
            return self.valid

        def set_valid(self, b: bool):
            self.valid = b

            # Change color to green if valid, red if invalid
            if self.is_valid():
                self.setForeground(Qt.GlobalColor.green)
            else:
                self.setForeground(Qt.GlobalColor.red)

    def __init__(self, parent: QStandardItemModel, name: str, *args):
        parent.removeRow(parent.add_ship_button.row())
        super().__init__(name)
        self.setFlags(SHIP_FLAGS)

        row = parent.rowCount()
        parent.setItem(row, 0, self)
        parent.setItem(row, 1, Label())
        self._init_vals()
        parent._add_ship_button_append()

        if len(args) == 0:
            self.valid = False
        else:
            for i, arg in enumerate(args):
                if i < self.ship_item_count():
                    # Set text value if normal entry, else assumed to be ValueButton
                    child = self.child(i, 1)
                    #FIXME: Integrate error checking
                    if self.child(i, 1).__class__ == Entry:
                        child: Entry
                        child.setText(str(arg))
                    else:
                        child: ValueButton
                        child.set_value(arg)
                else:
                    if type(arg) == dict:
                        arg: dict
                        name = list(arg.keys())[0]
                        door = self.Door(self, name)
                        #FIXME: Integrate error checking
                        for i, key in enumerate(arg[name]):
                            child = door.child(i, 1)
                            value = arg.get(name)[key]
                            if child.__class__ == Entry:
                                child: Entry
                                child.setText(str(value))
                            else:
                                child: ValueButton
                                child.set_value(value)
                    else:
                        raise TypeError(f"Door arguments must be type dict, not {type(arg)}")
        self.add_door_button_append()
        self.check()

    def _init_vals(self):
        self.ShipItem(self, "length", float)
        self.ShipItem(self, "pattern", Qt.BrushStyle)
        self.ShipItem(self, "color", QColor)
        self.ShipItem(self, "width", float)

    #TODO: Implement
    @classmethod
    def from_json(self, s: dict | str):
        pass

    def ship_item_count(self) -> int:
        count = 0
        for i in range(self.rowCount()):
            if type(self.child(i, 0)) != Ship.ShipItem:
                return count
            else:
                count += 1
        return count

    def add_door_button_append(self):
        self.add_door_button = AddDoorButton()
        self.appendRow([self.add_door_button, Label()])

    def add_door(self, name: str | None = None):
        self.removeRow(self.rowCount() - 1)
        if type(name == None):
            # TODO: Add "autoname" bool, set to true until changed by user
            # So if a door is removed, the other door's numbers will be adjusted
            self.Door(self, f"Door {self.rowCount() - self.ship_item_count() + 1}")
        elif type(name == str):
            self.Door(self, name)
        self.add_door_button_append()
        self.check()

    def is_valid(self) -> bool:
        return self.valid

    def set_valid(self, b: bool):
        # Check if ship has at least one door
        i = 0
        has_doors: bool
        has_doors = False
        while True:
            child = self.child(i, 0)
            if child == None:
                break
            elif type(child) == self.Door:
                has_doors = True
            i += 1

        # Set invalid if ship has no doors, even if method argued true
        self.valid = b and has_doors

        # Change color to green if valid, red if invalid
        if self.is_valid():
            self.setForeground(Qt.GlobalColor.green)
        else:
            self.setForeground(Qt.GlobalColor.red)

    def check(self):
        self.model().change_disconnect()
        ship_valid = True
        i = 0
        while True:
            item = self.child(i, 0)
            if item.__class__ == Ship.ShipItem:
                item: Ship.ShipItem
                if not item.check_valid():
                    ship_valid = False
            elif item.__class__ == Ship.Door:
                j = 0
                item: Ship.Door
                door_valid = True
                while True:
                    door_item = item.child(j, 0)
                    if door_item.__class__ == Ship.ShipItem:
                        door_item: Ship.ShipItem
                        if not door_item.check_valid():
                            door_valid = False
                            ship_valid = False
                    else:
                        break
                    j += 1
                item.set_valid(door_valid)
            else:
                break
            i += 1
        self.set_valid(ship_valid)
        self.model().change_connect()
    
    class ShipGraphic(port_items.PortItem):
        def __init__(self):
            super().__init__()
