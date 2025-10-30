import os
import json
import random
import numpy as np
from operator import call

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

import port_items
from main import get_icon

COLUMN_COUNT = 2

ADD_ICON = get_icon("add")
ASTERISK_ICON = get_icon("asterisk")
INVALID_ICON = get_icon("invalid")
SIDE_ICONS = {port_items.Side.both: get_icon("sides_both"),
              port_items.Side.port: get_icon("sides_port"),
              port_items.Side.starboard: get_icon("sides_starboard")}
SHIP_DIR = os.path.join(os.getcwd(), "ships")
ship_path = lambda s = str: os.path.join(SHIP_DIR, s)

# List of allowed patterns for ships
pattern_arr = list(Qt.BrushStyle)
pattern_arr.remove(Qt.BrushStyle.LinearGradientPattern)
pattern_arr.remove(Qt.BrushStyle.RadialGradientPattern)
pattern_arr.remove(Qt.BrushStyle.ConicalGradientPattern)
pattern_arr.remove(Qt.BrushStyle.TexturePattern)
pattern_arr.remove(Qt.BrushStyle.NoBrush)

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

DISPLAY_ITEM_FLAGS = (~Qt.ItemFlag.ItemIsEditable | ~Qt.ItemFlag.ItemIsEditable)

class Label(QStandardItem):
    def __init__(self, item_text: str = None, item_type = None, isValid: bool = False):
        self.item_type = item_type
        self.item_text = item_text
        self.isValid = isValid
        super().__init__(self.item_text)

class StaticItem(Label):
    def __init__(self, text: str = None):
        self.item_text = text
        super().__init__(self.item_text)
        self.setEditable(False)
        self.setSelectable(False)
        if type(self.item_text) == str:
            self.setText(self.item_text)
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

class ColorButton(Label):
    def __init__(self, color: QColor):
        super().__init__(isValid=True)
        self.setFlags(DISPLAY_ITEM_FLAGS)
        self.update_color(color)

    def update_color(self, color: QColor):
        self.setIcon(StyleIcon(color))

class PatternButton(Label):
    def __init__(self, pattern: Qt.BrushStyle):
        super().__init__(isValid=True)
        self.setFlags(DISPLAY_ITEM_FLAGS)
        self.update_pattern(pattern)
    
    def update_pattern(self, pattern: Qt.BrushStyle):
        self.setIcon(StyleIcon(Qt.BrushStyle(pattern)))

class SideButton(Label):
    def __init__(self):
        super().__init__(isValid=True)
        self.setFlags(DISPLAY_ITEM_FLAGS)
        self.i = 0
        self.side = port_items.Side.both
        self.update_side()
    
    def update_side(self):
        icon = QIcon(SIDE_ICONS.get(self.side))
        self.setIcon(icon)
    
    def increment_side(self):
        self.i = (self.i + 1) % len(port_items.Side)
        self.side = port_items.Side(self.i)
        self.update_side()

class ShipItem(Label):
    def __init__(self, ship: port_items.Ship = None):

        # Add ship items
        for i, attr in enumerate(port_items.Ship.ShipAttr):
            
            # Offset name attribute (should be above these attributes)
            if i == 0:
                super().__init__('', attr.type)
                continue

            # Offset doors attribute (doors are nested below attributes)
            elif i == len(port_items.Ship.ShipAttr) - 1:
                continue

            # Attributes of the ship nested under the name
            else:
                rand_range = lambda x: random.randint(0, len(x) - 1)
                if attr.type == Qt.GlobalColor:
                    self.color = QColor(Qt.GlobalColor(rand_range(Qt.GlobalColor)))
                    value_item = ColorButton(self.color)
                elif attr.type == Qt.BrushStyle:
                    self.pattern = pattern_arr[rand_range(pattern_arr)]
                    value_item = PatternButton(self.pattern)
                else:
                    value_item = Label('', attr.type)
            self.appendRow([StaticItem(attr.string), value_item])

        # Add door spawning button
        self._door_button = SpawnDoorButton()
        self.appendRow([self._door_button, StaticItem()])

    def add_door(self):
        self.removeRow(self._door_button.row())

        #TODO: 
        door = Label('', list(port_items.Ship.Door.DoorAttr)[0])
        self.appendRow([door, StaticItem()])

        # Add door items
        for i, attr in enumerate(list(port_items.Ship.Door.DoorAttr)):
            if i == 0:
                continue
            key_item = StaticItem(attr.string)
            if attr.type == port_items.Side:
                value_item = SideButton()
            else:
                value_item = Label('', attr.type)
            door.appendRow([key_item, value_item])
        self._door_button = SpawnDoorButton()
        self.appendRow(self._door_button)

    def get_color(self):
        return self.color

    def set_color(self, color: QColor):
        self.color = color

    def get_pattern(self):
        return self.pattern

    def set_pattern(self, pattern: Qt.BrushStyle):
        self.pattern = pattern

class ShipModel(QStandardItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(0, COLUMN_COUNT, parent)
        self.setHorizontalHeaderLabels(['']*COLUMN_COUNT) # Empty headers
        self._read_ships()

        self._ship_button = SpawnShipButton()
        self.setItem(0, self._ship_button)
        self.setItem(0, 1, StaticItem())
        #TODO: implement function
        self.changeConnect = lambda: self.itemChanged.connect(self._check_value)
        self.changeDisconnect = lambda: self.itemChanged.disconnect()
        self.changeConnect()

    def _read_ships(self):
        for path in os.listdir(SHIP_DIR):
            if os.path.splitext(path)[1] == ".json":
                root = self.invisibleRootItem()
                root.appendRow([ShipItem(path), StaticItem()])

    # Load json data
    def _read_ship(self, json_path):
        if os.path.splitext(json_path)[1] != ".json":
            raise ValueError("Argued file is not a .json type")
        ship_dict = port_items.Ship(json_path)
        ship_name = os.path.splitext(os.path.basename(ship_dict))[0]
        ShipItem(ship_name)

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
        self.appendRow([ShipItem(), StaticItem()])
        self.appendRow([SpawnShipButton(), StaticItem()])

    def item_press(self, index: QModelIndex):
        button = self.itemFromIndex(index)
        if button.__class__ == SpawnShipButton:
            self._add_ship(button)
        elif button.__class__ == SpawnDoorButton:
            button.parent().add_door()
        elif button.__class__ == ColorButton:
            color_dialog = QColorDialog()
            color_dialog.exec()
            color = color_dialog.selectedColor()
            button.update_color(color)
        elif button.__class__ == PatternButton:
            pattern_dialog = PatternDialog()
            pattern_dialog.exec()
            pattern = pattern_dialog.return_pattern()
            button.update_pattern(pattern)
        elif button.__class__ == SideButton:
            button.increment_side()
    
    @Slot()
    def _check_value(self, item: Label):
        attr = self.itemFromIndex(self.indexFromItem(item).siblingAtColumn(0))
        try:
            item_value = call(item.item_type, item.text())
            if type(item_value) == item.item_type:
                item.isValid = True
            else:
                item.isValid = False
        except Exception as error:
            print(error)
            item.isValid = False
        if item.isValid:
            color = Qt.GlobalColor.green
        else:
            color = Qt.GlobalColor.red
        self.changeDisconnect()
        attr.setForeground(color)
        item.setForeground(color)
        self.changeConnect()

# Debug
x = port_items.Ship("Ship Test", 5, Qt.BrushStyle.Dense3Pattern, Qt.GlobalColor.gray, 5)
print(f"{x.ship_name}, {x.length}, {x.pattern}, {x.color}, {x.width}")
x = port_items.Ship.from_dict(
                    {"ship_name": "sdsd",
                     "length": 1.0,
                     "pattern": 1,
                     "color": 1,
                     "width": 1,
                     "ththt": {
                         "side": 1,
                         "bow_distance": 1,
                         "stern_distance": 1,
                         "width": 1,
                         "height": 1,
                         "height_above_waterline": 1
                     },
                     "sds": {
                         "side": 1,
                         "bow_distance": 1,
                         "stern_distance": 1,
                         "width": 1,
                         "height": 1,
                         "height_above_waterline": 1
                     }})
print(f"{x.ship_name}, {x.length}, {x.pattern}, {x.color}, {x.width}")
print(x.to_dict())
print(x.doors[0].to_dict())
print(x.get_height())