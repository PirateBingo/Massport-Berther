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
