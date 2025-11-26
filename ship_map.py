import os

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import *

import port_items

PEN = Qt.PenStyle.SolidLine
STYLE = Qt.BrushStyle.Dense2Pattern
COLOR = 0xdfcfbf

SCENE_WIDTH = 3500
SCENE_HEIGHT = 1000

PORT_ID = "port"
BOLLARD_ID = "bollard"
WATER_TREE_ID = "water_tree"
get_svg = lambda s = str: os.path.join(os.getcwd(), "geometry", f"{s}.svg")

ZOOM_IN_SHORTCUT = QKeyCombination(Qt.KeyboardModifier.ControlModifier,
                                   Qt.Key.Key_Equal)
ZOOM_OUT_SHORTCUT = QKeyCombination(Qt.KeyboardModifier.ControlModifier,
                                    Qt.Key.Key_Minus)

class ShipMap(QGraphicsView):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)

        # Scene Initialization
        self._scene = QGraphicsScene(parent)
        self.setScene(self._scene)
        self._scene_rect = QRectF(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        self.setSceneRect(self._scene_rect)

        # Configurations
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._scene.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        # Background
        port_items.Outline(self)
        port_items.Ocean(self)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        index = event.source().selectedIndexes()[0]
        ship = event.source().model().itemFromIndex(index)

    #TODO: Create side shell plan view with integrated "auto scroll down" thing
    # def resizeEvent(self, event):
    #     self.verticalScrollBar().setValue(self.sceneRect().height())
    #     return super().resizeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.keyCombination() == ZOOM_IN_SHORTCUT:
            self.zoom_in()
        if event.keyCombination() == ZOOM_OUT_SHORTCUT:
            self.zoom_out()
    
    def zoom_in(self):
        self.scale(2, 2)

    def zoom_out(self):
        self.scale(1/2, 1/2)