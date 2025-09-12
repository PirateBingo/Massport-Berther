import weakref
import os
import json
import numpy as np
import typing
from enum import Enum

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtSvgWidgets import *

# import graphics_pane

PEN = Qt.PenStyle.SolidLine
STYLE = Qt.BrushStyle.Dense2Pattern
COLOR = 0xdfcfbf

SCENE_WIDTH = 4050
SCENE_HEIGHT = 1100

PORT_ID = "port"
BOLLARD_ID = "bollard"
WATER_TREE_ID = "water_tree"

get_svg = lambda s = str: os.path.join(os.getcwd(), 
                                       "geometry",
                                       f"{s}.svg")

#TODO: Fenders, Bollards, Water Trees
class PortItem(QGraphicsSvgItem):
    def __init__(self, graphics_view: QGraphicsView, path: str,
                 x: float, y: float, z_val: int = 0):
        super().__init__(path, x=x, y=y)
        self._graph = weakref.ref(graphics_view)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
                     QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(z_val)

        # Show item
        graphics_view.scene().addItem(self)
        self.show()

    def paint(self, painter: QPainter, option, widget):
        # Draw shape
        self.renderer().render(painter, QRectF(0, 0, SCENE_WIDTH, SCENE_HEIGHT))

class Bollard(PortItem):
    def __init__(self, graphics_view: QGraphicsView, x: float, y: float):
        super().__init__(graphics_view, get_svg(BOLLARD_ID), x=x, y=y)
        #FIXME:
        # self.connect(str(Bollard), graphics_view.TimePane.TimelineView.Timeline.BollardSelect.add_bollard)

class Supply(PortItem):
    def __init__(self, graphics_view: QGraphicsView,):
        super().__init__(graphics_view, get_svg(PORT_ID), x=0, y=0)

class WaterTree(PortItem):
    def __init__(self, graphics_view: QGraphicsView, x: float, y: float):
        super().__init__(graphics_view, get_svg(WATER_TREE_ID), x=x, y=y)

# class Obstruction(PortItem):
#     def __init__(self, ship_map: GraphicsPane.ShipMap):
#         super().__init__(ship_map, get_svg(PORT_ID), x=0, y=0)

class Port(PortItem):
    def __init__(self, graphics_view: QGraphicsView,):
        super().__init__(graphics_view, get_svg(PORT_ID), x=0, y=0)

# https://en.wikipedia.org/wiki/Port_and_starboard
class Side(Enum):
    port = 0 # Left side
    starboard = 1 # Right side
    both = 2

DOOR_ATTR = {"Side": Side,
             "Bow Distance": float,
             "Stern Distance": float,
             "Width": float,
             "Height": float,
             "Height Above Waterline": float}
class Door(QGraphicsRectItem):
    def __init__(self, name: str, side: Side, bow_distance: float,
                 stern_distance: float, width: float, height: float,
                 height_above_waterline: float):
        super().__init__()
        self.name = name
        self.side = side
        self.bow_distance = bow_distance
        self.stern_distance = stern_distance
        self.width = width
        self.height = height
        self.height_above_waterline = height_above_waterline

    def __dict__(self):
        return {"name": self.name,
                "side": self.side,
                "bow_distance": self.bow_distance,
                "stern_distance": self.stern_distance,
                "width": self.width,
                "height": self.height,
                "height_above_waterline": self.height_above_waterline}

    def __eq__(self, door):
        if type(door) != self.__class__:
            raise ValueError("Cannot compare Ship to non-Ship type")
        return self.__dict__() == door.__dict__()

SHIP_ATTR = {"Length": float,
             "Pattern": Qt.BrushStyle,
             "Color": Qt.GlobalColor,
             "Width": np.array(Door)}

class Ship(PortItem):
    @typing.overload
    def __init__(self, name: str, length: float,
                 pattern: Qt.BrushStyle, color: Qt.GlobalColor):
        super().__init__()
        self.name = name
        self.length = length
        self.pattern = pattern
        self.color = color
        self.doors = np.array(object=Door)
        self._sanitize_attributes()

    def __init__(self, ship: dict | str):
        # Load json data
        super().__init__()
        if type(ship) is str:
            self.name = os.path.splitext(os.path.basename(ship))[0]
            self.doors = []
            if os.path.splitext(ship)[1] != ".json":
                raise ValueError("Argued file is not a .json type")
            else:
                with open(ship, "r+") as json_file:
                    ship = json.load(json_file)

        for ship_key in enumerate(ship.keys()):
            if ship_key[1] == "length":
                self.length = ship[ship_key[1]]
            elif ship_key[1] == "pattern":
                self.pattern = ship[ship_key[1]]
            elif ship_key[1] == "color":
                self.color = ship[ship_key[1]]

            # Parse doors; door object names always start with "door"
            elif str(ship_key[1][:4]).lower() == "door":
                name = ship_key[1]
                for door_key in enumerate(ship[ship_key[1]]):
                    if door_key[1] == "side":
                        side = ship[ship_key[1]][door_key[1]]
                    if door_key[1] == "bow_distance":
                        bow_distance = ship[ship_key[1]][door_key[1]]
                    if door_key[1] == "stern_distance":
                        stern_distance = ship[ship_key[1]][door_key[1]]
                    if door_key[1] == "width":
                        width = ship[ship_key[1]][door_key[1]]
                    if door_key[1] == "height":
                        height = ship[ship_key[1]][door_key[1]]
                    if door_key[1] == "height_above_waterline":
                        height_above_waterline = ship[ship_key[1]][door_key[1]]
                self.doors.append(Door(name=name,
                                       side=side,
                                       bow_distance=bow_distance,
                                       stern_distance=stern_distance,
                                       width=width,
                                       height=height,
                                       height_above_waterline=height_above_waterline))
        self._sanitize_attributes()

    def _sanitize_attributes(self):
        try:
            self.name = str(self.name)
            self.length = float(self.length)
            self.pattern = (Qt.BrushStyle(int(self.pattern) % len(Qt.BrushStyle))
                            if type(self.pattern) is int
                            else Qt.BrushStyle(self.pattern))
            self.color =  QColor(self.color)
        except ValueError as error:
            raise ValueError(f"{error}\n Ship was given incorrect value type")
        except NameError as error:
            raise NameError(f"{error}\n Ship never given value for argument")
        except Exception:
            raise Exception

        if len(self.doors) == 0:
            print("Door array is empty")
            self.doorless = True
        elif any([type(door) is not Door for door in self.doors]):
            raise ValueError("Door array contains non-door types")
        else:
            self.doorless = False
            self.height = max([door.height_above_waterline
                               for door in self.doors])

    def __dict__(self):
        return {"name": self.name,
                "length": self.length,
                "pattern": self.pattern,
                "color": self.color,
                "height": self.height,
                "doors": [door for door in self.doors]}
    
    def __eq__(self, ship):
        if type(ship) != self.__class__:
            raise ValueError("Cannot compare Ship to non-Ship type")
        else:
            if (self.name == ship.name and
                self.length == ship.length and
                self.pattern == ship.pattern and
                self.color == ship.color and
                self.height == ship.height and
                len(self.doors) == len(ship.doors) and
                all([self.doors[i] == ship.doors[i] for i in range(len(self.doors))])):
                return True
            else:
                return False

    def add_door(self, door: Door):
        np.append(self.doors, door)
        self.calc_height()

    def calc_height(self):
        self.height = self.doors.max()
        
    #TODO:
    def render(self, graphWidget: QGraphicsView, scene: QGraphicsScene,
                x: float, y: float, w: float, h: float):
        # super().__init__(x, y, w, h)

        self._graph = weakref.ref(graphWidget)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsRectItem.CacheMode.DeviceCoordinateCache)
        self.setZValue(1)

        # Show item
        scene.addItem(self)
        self.show()

    def paint(self, painter: QPainter, option, widget):
        painter.setPen(QPen(PEN))
        painter.setBrush(QBrush(COLOR, STYLE))
        painter.drawRect(self.rect())
