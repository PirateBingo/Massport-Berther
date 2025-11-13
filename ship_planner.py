from PySide6.QtCore import *
from PySide6.QtWidgets import *

import ship_map

SECONDS_IN_DAY = 60 * 60 * 24

class Timeline(QWidget):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self.setObjectName("Timeline")
        self.date_dict = {}
        self.setLayout(QGridLayout(self))
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,
                            QSizePolicy.Policy.Maximum)

        # Calender
        self.calender = QCalendarWidget(self)
        self.layout().addWidget(self.calender, 0, 0, 1, 3)

        # Time slider
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setRange(0, SECONDS_IN_DAY - 1)
        self.layout().addWidget(self.slider, 1, 0, 1, 2)

        # Time Edit
        self.time_edit = QTimeEdit(self)
        self.layout().addWidget(self.time_edit, 1, 2, 1, 1)

        # Initialize variables from initial values of calender and time edit
        self.date = self.calender.selectedDate()
        self.time = self.time_edit.time()

        # Connect signals after time and date are assigned
        self.connect_time_edit = lambda: self.time_edit.timeChanged.connect(lambda x: self.update_time(x))
        self.disconnect_time_edit = lambda: self.time_edit.timeChanged.disconnect()

        self.connect_slider = lambda: self.slider.valueChanged.connect(lambda x: self.update_time(x))
        self.disconnect_slider = lambda: self.slider.valueChanged.disconnect()

        self.connect_time_edit()
        self.connect_slider()

    def update_time(self, time: QTime | int):
        if type(time) == QTime:
            time: QTime
            self.time = time.hour() * 3600 + time.minute() * 60 + time.second()

            # Change time edit value
            self.disconnect_slider()
            self.slider.setValue(self.time)
            self.connect_slider()

        elif type(time) == int:
            time: int
            h = time // 3600
            m = time % 3600 // 60
            s = time % 60
            self.time = QTime(h, m, s)

            # Change time slider value
            self.disconnect_time_edit()
            self.time_edit.setTime(self.time)
            self.connect_time_edit()

    def get_date(self):
        return self.calender.selectedDate()

    def get_time(self):
        return  self.time_edit.time()

class Scheduler(QWidget):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self.setObjectName("Scheduler")
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,
                            QSizePolicy.Policy.Preferred)
        self.ship_arr = []
        self._layout = QGridLayout()
        self._group_box = QGroupBox()
        self._group_box.setLayout(self._layout)

        scroll = QScrollArea()
        scroll.setSizePolicy(QSizePolicy.Policy.Minimum,
                                QSizePolicy.Policy.Expanding)
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
        self._layout.addWidget(self.ShipSlot())
        self._layout.addWidget(button)

    class ShipSlot(QWidget):
        def __init__(self, parent: QObject=None):
            super().__init__(parent)
            self.left_bound = QTimeEdit(self)
            self.right_bound = QTimeEdit(self)
            self.ship_select = self.ShipSelect(self)
            self.bollard_select = self.BollardSelect(self)

            layout = QGridLayout(self)
            layout.addWidget(self.left_bound, 0, 0, 1, 1)
            layout.addWidget(self.right_bound, 0, 1, 1, 1)
            layout.addWidget(self.ship_select, 2, 0, 1, 1)
            layout.addWidget(self.bollard_select, 2, 1, 1, 1)

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