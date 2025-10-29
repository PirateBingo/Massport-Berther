import weakref
import os
import json
import numpy as np
import typing
import enum
from operator import call

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
class Side(enum.Enum):
    port = 0 # Left side
    starboard = enum.auto() # Right side
    both = enum.auto()

class ShipEnum(enum.Enum):
    def __init__(self, index, type, string):
        self.index = index
        self.type = type
        self.string = string

class Ship(PortItem):
    class Door():
        class DoorAttr(ShipEnum):
            door_name = (enum.auto(), str, "Door Name")
            side = (enum.auto(), Side, "Side")
            bow_distance = (enum.auto(), float, "Bow Distance")
            stern_distance = (enum.auto(), float, "Stern Distance")
            width = (enum.auto(), float, "Width")
            height = (enum.auto(), float, "Height")
            height_above_waterline = (enum.auto(), float, "Height Above Waterline")

        def __init__(self, *args):
            door = {}
            for i, arg in enumerate(args):
                attr = list(self.DoorAttr)[i]
                door.update({attr.name: arg})
                if i > len(self.DoorAttr):
                    raise IndexError("Too many arguments provided")
            self.from_dict(door)

        @classmethod
        def from_dict(cls, door: dict | str, name: str) -> typing.Self:
            for i, door_key in enumerate(cls.DoorAttr):
                if i <= len(cls.DoorAttr) - 1:
                    try:
                        door_attr = list(cls.DoorAttr)[i]
                        if i == 0:
                            door_val = name
                        else:
                            door_val = door[door_key.name]
                        door_val = call(door_attr.type, door_val)
                        setattr(cls, door_attr.name, door_val)
                    except Exception as error:
                        raise error
            return cls.__new__(cls)

        def to_dict(self):
            d = {}
            for i, attr in enumerate(self.DoorAttr):
                if i == 0:
                    door_name = getattr(self, attr.name)
                else:
                    d.update({attr.name: getattr(self, attr.name)})
            return {door_name: d}

        #TODO: Implement
        def __eq__(self, door):
            if type(door) != self.__class__:
                raise ValueError("Cannot compare Ship to non-Ship type")
            return self.__dict__() == door.__dict__()

    class ShipAttr(ShipEnum):
        ship_name = (enum.auto(), str, "Ship Name")
        length = (enum.auto(), float, "Length")
        pattern = (enum.auto(), Qt.BrushStyle, "Pattern")
        color = (enum.auto(), Qt.GlobalColor, "Color")
        width = (enum.auto(), float, "Width")
        doors = (enum.auto(), dict, "Doors")

    # Convert arguments to dict; don't accept doors
    def __init__(self, *args):
        ship = {}
        for i, arg in enumerate(args):
            attr = list(self.ShipAttr)[i]
            ship.update({attr.name: arg})
            if i > len(self.ShipAttr):
                raise IndexError("Too many arguments provided")
        self.from_dict(ship)

    @classmethod
    def from_dict(cls, ship: dict | str) -> typing.Self:
        # If given json file, load into dict
        if type(ship) is str:
            if os.path.splitext(ship)[1] != ".json":
                raise ValueError("Argued file is not a .json type")
            else:
                path = os.path.splitext(os.path.basename(ship))[0]
                with open(path, "r+") as json_file:
                    ship_dict = json.load(json_file)

        # Use dict if given
        else:
            ship_dict = ship

        # Try to convert dict to new ship object
        cls.doors = []
        try:
            for i, ship_key in enumerate(ship_dict.keys()):
                ship_val = ship_dict[ship_key]
                ship_attr = list(cls.ShipAttr)[min(i, len(cls.ShipAttr) - 1)]
                if i < len(cls.ShipAttr) - 1:

                    try:
                        ship_val = call(ship_attr.type, ship_val)
                        setattr(cls, ship_attr.name, ship_val)
                    except Exception as error:
                        raise error

                else:
                    door_name = list(ship_dict.keys())[i]
                    cls.doors.append(cls.Door.from_dict(ship_val, door_name)) # type: ignore

            return cls.__new__(cls)

        except Exception as error:
            raise error

    def to_dict(self):
        d = {}
        for attr in self.ShipAttr:
            d.update({attr.name: getattr(self, attr.name)})
        return d
    
    # TODO: Create function that checks if a ship can be implemented and saved
    def isComplete(self):
        pass
    
    #TODO:
    def __eq__(self, ship):
        pass

    def add_door(self, door: Door):
        np.append(self.doors, door)
        self.calc_height()

    def get_height(self):
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
