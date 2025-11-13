import sys
import os

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from superqt import *

import ship_map
import ship_editor
import ship_planner

PROGRAM_NAME = "Flynn Cruiseport Planner"

get_icon = lambda s: os.path.join(os.getcwd(), "icons", f"{s}.png")
LOGO = get_icon("logo")

#FIXME: Redundant
PALLETTE_MASSPORT = QPalette()
PALLETTE_MASSPORT.setColor(QPalette.ColorRole.Highlight, QColor(0, 57 * 1.5, 168 * 1.5))
PALLETTE_MASSPORT.setColor(QPalette.ColorRole.Accent, QColor(0, 57 * 1.5, 168 * 1.5))
PALLETTE_MASSPORT.setColor(QPalette.ColorRole.AlternateBase, QColor(0, 57, 168))
PALLETTE_MASSPORT.setColor(QPalette.ColorRole.Light, QColor(0, 57 * 1.5, 168 * 1.5))

class DockWidget(QDockWidget):
    def __init__(self, widget: QWidget):
        super().__init__()
        self.setWidget(widget)
        self.setWindowTitle(widget.objectName())

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set icon and window title
        logo = QIcon(LOGO)
        self.setWindowIcon(logo)
        self.setWindowTitle(PROGRAM_NAME)

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        QIcon.setThemeName("Material Symbols Outlined")

        # Setup widgets
        self.setCentralWidget(ship_map.ShipMap())
        
        # pane = ship_editor.ShipPane() 
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,
                           DockWidget(ship_editor.ShipView()))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,
                           DockWidget(ship_planner.Timeline()))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,
                           DockWidget(ship_planner.Scheduler()))

if __name__ == "__main__":
    app = QApplication()
    app.setPalette(PALLETTE_MASSPORT)
    window = Window()
    window.show()
    sys.exit(app.exec())