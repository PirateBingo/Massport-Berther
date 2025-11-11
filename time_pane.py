from PySide6.QtCore import *
from PySide6.QtWidgets import *
from superqt import *

import graphics_pane

class TimePane(QSplitter):
    def __init__(self):
        super().__init__()
        self.setObjectName("Ship Planner")
        self.setOrientation(Qt.Orientation.Vertical)
        self.calender = self.Calender(self)
        self.timeline_view = self.TimelineView(self)
        self.spawn_timeline = lambda date = QDate: self.calender.add_date(date)

    class Calender(QCalendarWidget):
        def __init__(self, parent: QObject=None):
            super().__init__(parent)
            self.date_dict = {}
            size_policy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding,
                                      QSizePolicy.Policy.Maximum)
            self.setSizePolicy(size_policy)
            #FIXME: Determine minimum size of calender naturally
            # Row height = 24px, Header height = 22 px, 24 * 7 + 22 = 190px?

        def add_date(self, date: QDate):
            self.date_dict.update(date, "roncrne")

        class DatePlan(QDate):
            def __init__(self, date: QDate):
                super().__init__(date)

    class TimelineView(QWidget):
        def __init__(self, parent: QObject=None):
            super().__init__(parent)
            self.ship_arr = []
            self._layout = QGridLayout()
            self._group_box = QGroupBox()
            self._group_box.setLayout(self._layout)

            scroll = QScrollArea()
            scroll.setWidget(self._group_box)
            scroll.setWidgetResizable(True)

            layout = QVBoxLayout(self)
            layout.addWidget(scroll)

            self._spawn_button = QPushButton("Add Ship: ", self)
            self._spawn_button.pressed.connect(self._spawn_timeline)
            self._layout.addWidget(self._spawn_button, 0, 0, 1, 1)

        @Slot()
        def _spawn_timeline(self):
            pos = self._layout.indexOf(self._spawn_button)
            button = self._layout.itemAt(pos).widget()
            self._layout.removeWidget(button)
            self._layout.addWidget(self.Timeline())
            self._layout.addWidget(button)

        class Timeline(QWidget):
            def __init__(self, parent: QObject=None):
                super().__init__(parent)
                self.slider = QRangeSlider(self, orientation=Qt.Orientation.Horizontal)
                self.left_bound = QTimeEdit(self)
                self.right_bound = QTimeEdit(self)
                self.ship_select = self.ShipSelect(self)
                self.bollard_select = self.BollardSelect(self)

                layout = QGridLayout(self)
                layout.addWidget(self.slider, 0, 0, 1, 2)
                layout.addWidget(self.left_bound, 1, 0, 1, 1)
                layout.addWidget(self.right_bound, 1, 1, 1, 1)
                layout.addWidget(self.ship_select, 0, 2, 1, 1)
                layout.addWidget(self.bollard_select, 1, 2, 1, 1)

            class ShipSelect(QListView):
                def __init__(self, parent: QObject):
                    super().__init__(parent)
                    self.setSelectionMode(self.SelectionMode.SingleSelection)

            class BollardSelect(QListView):
                def __init__(self, parent: QObject):
                    super().__init__(parent)
                    self.setSelectionMode(self.SelectionMode.MultiSelection)

                @Slot()
                def add_bollard(bollard):
                    print(bollard)