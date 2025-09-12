import sys
import os

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from superqt import *

import ship_pane
import graphics_pane
import time_pane

PROGRAM_NAME = "Flynn Cruiseport Planner"

get_icon = lambda s: os.path.join(os.getcwd(), "icons", f"{s}.png")
LOGO = get_icon("logo")

#FIXME: Redundant
PALLETTE_MASSPORT = QPalette()
PALLETTE_MASSPORT.setColor(QPalette.ColorRole.Highlight, QColor(0, 57 * 1.5, 168 * 1.5))
PALLETTE_MASSPORT.setColor(QPalette.ColorRole.Accent, QColor(0, 57 * 1.5, 168 * 1.5))
PALLETTE_MASSPORT.setColor(QPalette.ColorRole.AlternateBase, QColor(0, 57, 168))
PALLETTE_MASSPORT.setColor(QPalette.ColorRole.Light, QColor(0, 57 * 1.5, 168 * 1.5))

class Window(QSplitter):
    def __init__(self):
        super().__init__(childrenCollapsible=False,
                         orientation=Qt.Orientation.Vertical)

        # Set icon and window title
        logo = QIcon(LOGO)
        self.setWindowIcon(logo)
        self.setWindowTitle(PROGRAM_NAME)

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # Setup widgets
        self._time_pane = time_pane.TimePane(self)
        self._ship_pane = ship_pane.ShipPane(self)
        self._graphics_pane = graphics_pane.GraphicsPane(self)
        self.addWidget(self._ship_pane)
        self.addWidget(self._time_pane)
        self.addWidget(self._graphics_pane)

        #FIXME: Probably inefficient
        # Get rid of dangling splitters
        def delete_splitter(splitter: QSplitterHandle):
            splitter.moveSplitter(-self.screen().availableSize().height())
            splitter.setDisabled(True)
        splitter_arr = []
        for widget in self.children():
            if type(widget) is QSplitterHandle:
                splitter_arr.append(widget)
        delete_splitter(splitter_arr[1])
        delete_splitter(splitter_arr[3])

        # Initialize JSON model
        # self._model = ship_pane.ShipModel()
        # self._ship_pane._ship_view.setModel(self._model)

if __name__ == "__main__":
    app = QApplication()
    app.setPalette(PALLETTE_MASSPORT)
    window = Window()
    window.show()
    sys.exit(app.exec())