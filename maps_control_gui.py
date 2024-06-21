#!/usr/bin/env python3


# +
# import(s)
# -
from colors import *
from pnd import *
from maps_indi import *

# noinspection PyBroadException
try:
    # noinspection PyUnresolvedReferences
    from pyindi2 import *
except:
    pass

import argparse
import platform
import queue
import sys

QT_VERSION = int(os.getenv("QT_VERSION",  -1))
if QT_VERSION == 5:
    # noinspection PyPackageRequirements
    from PyQt5.QtCore import *
    # noinspection PyPackageRequirements
    from PyQt5.QtWidgets import *
    # noinspection PyPackageRequirements
    from PyQt5.QtGui import *
elif QT_VERSION == 6:
    # noinspection PyPackageRequirements
    from PyQt6.QtCore import *
    # noinspection PyPackageRequirements
    from PyQt6.QtWidgets import *
    # noinspection PyPackageRequirements
    from PyQt6.QtGui import *
else:
    color_print(msg='ERROR: Qt version not supported', color='red', height=2)
    sys.exit(0)


# +
# constant(s)
# -
__doc__ = """python3 maps_control_gui.py --help"""
AUTHOR = 'Phil Daly'
DATE = 20240612
EMAIL = 'pndaly@arizona.edu'
MODULES = [_ for _ in list(TAB_DATA.keys())]
NAME = 'MAPS Control GUI'
VERSION = '1.0.0'


# +
# default(s)
# -
DEFAULT_DELAY = 2000
DEFAULT_HOST = 'localhost'
DEFAULT_ITEMS = 25
DEFAULT_MODULE = MODULES[0]
DEFAULT_PORT = 7624
DEFAULT_TIMEOUT = 5


# +
# class: MapsControlGui()
# -
# noinspection PyArgumentList,PyUnresolvedReferences,PyShadowingNames
class MapsControlGui(QMainWindow):

    # +
    # (hidden) method: __init__()
    # -
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, 
                 items: int = DEFAULT_ITEMS, delay: int = DEFAULT_DELAY,
                 fg: str = DEFAULT_FG, bg: str = DEFAULT_BG,
                 module: str = DEFAULT_MODULE, log: logging.Logger = None) -> None:

        # get argument(s)
        self.host = host
        self.port = port
        self.items = items
        self.delay = delay
        self.fg = fg
        self.bg = bg
        self.module = module
        self.log = log

        # initialize the super class
        super().__init__(parent=None)

        # initialize variable(s)
        self.__action_connect = None
        self.__action_disconnect = None
        self.__action_about = None
        self.__action_quit = None
        self.__action_simulate = None
        self.__connected = False
        self.__filemenu = None
        self.__simmenu = None
        self.__pi = None
        self.__simulate = True
        self.__step = 0
        self.__lcds = {}
        self.__slds = {}
        self.__vals = {}

        # initialize (some) widget(s)
        self.__connected_icon = QLabel()
        self.__connected_label = QLabel()
        self.__menubar = QMenuBar()
        self.__timer = QTimer()
        self.__tabs = QTabWidget()

        # indi streams we wish to subscribe to, but  we only want writable elements
        _streams = [(_k, _v) for _k, _v in TAB_DATA.get(self.__module).items() if 'w' in _v['permission']]
        self.__indi_streams = list(set([f"{_[0].split('.')[0]}.{_[0].split('.')[1]}" for _ in _streams]))
        self.__indi_nelms = len(_streams)
        self.__indi_pages = int(math.ceil(self.__indi_nelms / self.__items))
        if self.__indi_pages == 0:
            self.__indi_pages += 1

        if self.__log:
            self.__log.info(f"_streams={_streams}")
            self.__log.info(f"self.__indi_streams={self.__indi_streams}")
            self.__log.info(f"self.__indi_nelms={self.__indi_nelms}")
            self.__log.info(f"self.__indi_pages={self.__indi_pages}")

        # if we have nothing, just return
        if self.__indi_nelms == 0:
            if self.__log:
                self.__log.warning(f"No (writeable) controls selected")
            return

        # create user interface
        self.create_user_interface()

        # if we are not in simulation mode, connect to the indiserver
        if not self.__simulate:
            self.__pi = PyINDI2(verbose=False)

        self.__dump__('pars')
        self.__dump__('vars')
        self.__timer.start(self.__delay)

    # +
    # decorator(s)
    # -
    @property
    def host(self) -> str:
        return f"{self.__host}"

    @host.setter
    def host(self, host: str = DEFAULT_HOST) -> None:
        self.__host = host if host.strip() != '' else DEFAULT_HOST

    @property
    def port(self) -> int:
        return int(self.__port)

    @port.setter
    def port(self, port: int = DEFAULT_PORT) -> None:
        self.__port = port if port > 0 else DEFAULT_PORT

    @property
    def items(self) -> int:
        return int(self.__items)

    @items.setter
    def items(self, items: int = DEFAULT_ITEMS) -> None:
        self.__items = items if items > 0 else DEFAULT_ITEMS

    @property
    def delay(self) -> int:
        return int(self.__delay)

    @delay.setter
    def delay(self, delay: int = DEFAULT_DELAY) -> None:
        self.__delay = delay if delay > 0 else DEFAULT_DELAY

    @property
    def module(self) -> str:
        return f"{self.__module}"

    @module.setter
    def module(self, module: str = DEFAULT_MODULE) -> None:
        self.__module = module if module in MODULES else DEFAULT_MODULE

    @property
    def fg(self) -> str:
        return f"{self.__fg}"

    # noinspection PyShadowingNames
    @fg.setter
    def fg(self, fg: str = DEFAULT_FG) -> None:
        self.__fg = fg if fg in CNAMES_R else DEFAULT_FG

    @property
    def bg(self) -> str:
        return f"{self.__bg}"

    # noinspection PyShadowingNames
    @bg.setter
    def bg(self, bg: str = DEFAULT_BG) -> None:
        self.__bg = bg if bg in CNAMES_R else DEFAULT_BG

    @property
    def log(self) -> str:
        return f"{self.__log}"

    @log.setter
    def log(self, log: logging.Logger = None) -> None:
        self.__log = log

    # +
    # variable getter(s)
    # -
    @property
    def connected(self) -> bool:
        return self.__connected

    @property
    def pi(self) -> str:
        return f"{self.__pi}"

    @property
    def simulate(self) -> bool:
        return self.__simulate

    @property
    def step(self) -> int:
        return self.__step

    @property
    def indi_nelms(self) -> int:
        return int(self.__indi_nelms)

    @property
    def indi_pages(self) -> int:
        return self.__indi_pages

    @property
    def indi_streams(self) -> str:
        return f"{self.__indi_streams}"

    @property
    def lcds(self) -> dict:
        return self.__lcds

    @property
    def slds(self) -> dict:
        return self.__slds

    @property
    def vals(self) -> dict:
        return self.__vals

    # +
    # (hidden) method: __dump__()
    # -
    def __dump__(self, which: str = "pars") -> None:
        if which.lower().strip() == "pars":
            if self.__log:
                self.__log.debug(f"self='{self}', host='{self.__host}', port={self.__port}, "
                                 f"items={self.__items}, delay={self.__delay}, "
                                 f"fg={self.__fg}, bg={self.__bg}, "
                                 f"module='{self.__module}', log={self.__log}")
        elif which.lower().strip() == "vars":
            if self.__log:
                self.__log.debug(f"self.__indi_streams={self.__indi_streams}, "
                                 f"self.__indi_nelms={self.__indi_nelms}, "
                                 f"self.__indi_pages={self.__indi_pages}, "
                                 f"self.__connected={self.__connected}, "
                                 f"self.__pi={self.__pi}, "
                                 f"self.__simulate={self.__simulate}, "
                                 f"self.__step={self.__step}")

    # +
    # (hidden) method: __create_menu__()
    # -
    def __create_menu__(self):

        self.__action_connect = QAction(QIcon('plug-connect.png'), '&Connect', self)
        self.__action_connect.setShortcut(QKeySequence('Alt+C'))
        self.__action_connect.triggered.connect(self.connect_to_indi)

        self.__action_disconnect = QAction(QIcon('plug-disconnect.png'), '&Disconnect', self)
        self.__action_disconnect.setShortcut('Alt+D')
        self.__action_disconnect.triggered.connect(self.disconnect_from_indi)

        self.__action_about = QAction(QIcon('information-frame.png'), '&About', self)
        self.__action_about.setShortcut('Alt+A')
        self.__action_about.triggered.connect(self.show_about)

        self.__action_quit = QAction(QIcon('cross-circle-frame.png'), '&Quit', self)
        self.__action_quit.setShortcut('Alt+Q')
        self.__action_quit.triggered.connect(self.close)

        self.__filemenu = self.__menubar.addMenu('File')
        self.__filemenu.addSection('INDI Control(s)')
        self.__filemenu.addAction(self.__action_connect)
        self.__filemenu.addAction(self.__action_disconnect)
        self.__filemenu.addSection('GUI Control(s)')
        self.__filemenu.addAction(self.__action_about)
        self.__filemenu.addAction(self.__action_quit)

        self.__action_simulate = QAction('&Simulate', self, checkable=True)
        self.__action_simulate.setShortcut('Alt+S')
        self.__action_simulate.setChecked(True)
        self.__action_simulate.triggered.connect(self.set_simulate)

        self.__menubar.setStyleSheet(f"background-color: '{ALARMRED}'; color:'{ALARMORANGE}'; border: solid 2px;")
        self.__simmenu = self.__menubar.addMenu('Simulate')
        self.__simmenu.addAction(self.__action_simulate)

    # +
    # (hidden) method: __create_tabbed__()
    # -
    def __create_tabbed__(self):
        self.__tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.__tabs.setMovable(True)
        if self.__module in TAB_DATA:

            key_vals = [(_k, _v) for _k, _v in TAB_DATA[self.__module].items()]
            key_pages, self.__indi_pages, self.__items = self.split_keyvals(_list=key_vals, _pages=self.__indi_pages, _chunk=self.__items)

            for _ip in range(self.__indi_pages):
                tab_name = f"{TAB_NAMES.get(self.__module)} {_ip}"

                # create a placeholder widget and insert into horizontal layout
                w = QWidget()
                h = QHBoxLayout(w)

                # create left, right and middle group(s)
                right = QGroupBox('Control(s)')
                right.setStyleSheet(f"background-color: '{self.__fg}'; color: '{self.__bg}';")  # reverse video!
                right.setFont(QFont("Bitstream Charter", 12, italic=True))

                left = QGroupBox('Stream(s)')
                left.setStyleSheet(f"background-color: '{self.__bg}'; color: '{self.__fg}';")
                left.setFont(QFont("Bitstream Charter", 12, italic=True))

                middle = QGroupBox('Value(s)')
                middle.setStyleSheet(f"background-color: '{self.__bg}'; color: '{self.__fg}';")
                middle.setFont(QFont("Bitstream Charter", 12, italic=True))

                h.addWidget(left)
                h.addWidget(middle)
                h.addWidget(right)

                # create right, middle and left grid(s)
                rg = QGridLayout()
                mg = QGridLayout()
                lg = QGridLayout()

                rg.setHorizontalSpacing(0)
                rg.setVerticalSpacing(0)
                mg.setHorizontalSpacing(0)
                mg.setVerticalSpacing(0)
                lg.setHorizontalSpacing(0)
                lg.setVerticalSpacing(0)

                # populate gui
                _ic = 0
                for _k, _v in key_pages[_ip]:

                    # if the key is empty, we use it for padding
                    if _k == '':
                        _ = QLabel()
                        lg.addWidget(_, _ic, 0)
                        mg.addWidget(_, _ic, 0)
                        rg.addWidget(_, _ic, 0)

                    # populate grid(s)
                    else:
                        _data = TAB_DATA[self.__module]
                        _items = [_ for _ in list(_data.keys())]

                        if isinstance(_data[_k]['label'], str) and _data[_k]['label'].strip() != '':
                            if _data[_k]['unit'].strip() == '':
                                _data[_k]['label'] = QLabel(f"{_data[_k]['label']}")
                            else:
                                _data[_k]['label'] = QLabel(f"{_data[_k]['label']} [{_data[_k]['unit']}]")
                        elif isinstance(_data[_k]['label'], str) and _data[_k]['label'].strip() == '':
                            _data[_k]['label'] = QLabel(f"")
                        else:
                            if _data[_k]['unit'].strip() == '':
                                _data[_k]['label'] = QLabel(f"{_k}")
                            else:
                                _data[_k]['label'] = QLabel(f"{_k} [{_data[_k]['unit']}]")
                        _data[_k]['label'].setToolTip(f"{_data[_k]['tooltip']}")

                        self.__vals = {**self.__vals, **{_k: QLabel(f"{_data[_k]['actval']}")}}

                        # float or int tuple
                        _n1 = None
                        if ('float' in _data[_k]['datatype'] or 'int' in _data[_k]['datatype']) and \
                           (isinstance(_data[_k]['datarange'], tuple) and len(_data[_k]['datarange']) == 2):
                            
                            _min, _max = _data[_k]['datarange']
                            _onepc = (_max - _min) / 100.0
                            _half = _min + ((_max - _min) / 2.0)
                            _data[_k]['widget'] = QSlider(Qt.Orientation.Horizontal, self)
                            _data[_k]['widget'].setWindowTitle(_k)
                            _data[_k]['widget'].setToolTip(f"{_k}")
                            _data[_k]['widget'].setFocusPolicy(Qt.FocusPolicy.NoFocus)
                            _data[_k]['widget'].setMinimum(int(round(_min)))
                            _data[_k]['widget'].setMaximum(int(round(_max)))
                            _data[_k]['widget'].setValue(int(round(_half)))
                            _data[_k]['widget'].setSingleStep(int(round(_onepc)))
                            _data[_k]['widget'].setTickInterval(int(round(_onepc*10.0)))
                            _data[_k]['widget'].setTickPosition(QSlider.TickPosition.TicksBelow)
                            _data[_k]['widget'].valueChanged.connect(self.slider_value_changed)
                            _data[_k]['widget'].sliderReleased.connect(self.slider_button_released)

                            self.__lcds = {**self.__lcds, **{_k: QLCDNumber()}}
                            self.__lcds[_k].setStyleSheet(f"background-color: f'{self.__fg}'; color: f'{self.__bg}'; border: 1px solid #808080;")  # reverse video!
                            self.__lcds[_k].display(int(round(_half)))
                            self.__lcds[_k].setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
                            self.__slds = {**self.__slds, **{_k: (_min, _max, _half, _onepc)}}

                            lg.addWidget(_data[_k]['label'], _ic, 0)
                            mg.addWidget(self.__vals[_k], _ic, 0)
                            rg.addWidget(_data[_k]['widget'], _ic, 0)
                            if self.__lcds[_k] is not None:
                                rg.addWidget(self.__lcds[_k], _ic, 1)

                        # list
                        elif isinstance(_data[_k]['datarange'], list) and len(_data[_k]['datarange']) > 0:

                            _data[_k]['widget'] = QWidget()
                            _data[_k]['widget'].setWindowTitle(_k)
                            h = QHBoxLayout(_data[_k]['widget'])
                            for _i, _j in enumerate(_data[_k]['datarange']):
                                _btn = QRadioButton(f"{_j}")
                                _btn.setWindowTitle(_k)
                                _btn.setToolTip(f"{_k}")
                                _btn.toggled.connect(self.radio_toggled)
                                h.addWidget(_btn)

                            lg.addWidget(_data[_k]['label'], _ic, 0)
                            mg.addWidget(self.__vals[_k], _ic, 0)
                            rg.addWidget(_data[_k]['widget'], _ic, 0)

                        # str
                        else:
                            self.__lcds = {**self.__lcds, **{_k: None}}
                            self.__slds = {**self.__slds, **{_k: (math.nan, math.nan, math.nan, math.nan)}}
                            _data[_k]['widget'] = QLineEdit()
                            _data[_k]['widget'].setWindowTitle(_k)
                            _data[_k]['widget'].setToolTip(f"{_k}")
                            # _data[_k]['widget'].setStyleSheet("""QLineEdit { background-color: f'{self.__fg}'; color: f'{self.__bg}'; }""")  #  reverse video!
                            _data[_k]['widget'].setStyleSheet(f"background-color: f'{self.__fg}'; color: f'{self.__bg}';")  # reverse video!
                            _data[_k]['widget'].returnPressed.connect(self.line_edit_clicked)

                            lg.addWidget(_data[_k]['label'], _ic, 0)
                            mg.addWidget(self.__vals[_k], _ic, 0)
                            rg.addWidget(_data[_k]['widget'], _ic, 0)

                    # set layout into group(s) and add tab
                    right.setLayout(rg)
                    middle.setLayout(mg)
                    left.setLayout(lg)

                    self.__tabs.addTab(w, tab_name)
                    _ic += 1

    # +
    # method: line_edit_clicked() - SEND TO INDI!
    # -
    def line_edit_clicked(self):
        try:
            value = self.sender().text().strip()
            title = self.sender().windowTitle().strip()
            datatype = TAB_DATA[self.__module][title].get('datatype', '').strip()
            if self.__log:
                self.__log.debug(f"title='{title}', value='{value}', datatype='{datatype}'")

            if 'float' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', float({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, float(value), timeout=DEFAULT_TIMEOUT)
            elif 'int' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', int({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, int(value), timeout=DEFAULT_TIMEOUT)
            elif 'bool' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', bool({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, bool(value), timeout=DEFAULT_TIMEOUT)
            elif 'binary' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', f'{value.encode('utf-8')}', timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, f"{value.encode('utf-8')}", timeout=DEFAULT_TIMEOUT)
            else:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', f'{value}', timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, f"{value}", timeout=DEFAULT_TIMEOUT)

        except Exception as _:
            if self.__log:
                self.__log.error(f"failure in line_edit_clicked(), error='{_}'")

    # +
    # method: radio_toggled() - SEND TO INDI!
    # -
    def radio_toggled(self):
        try:
            value = self.sender().text()
            title = self.sender().windowTitle().strip()
            datatype = TAB_DATA[self.__module][title].get('datatype', '').strip()
            if self.__log:
                self.__log.debug(f"title='{title}', value='{value}', datatype='{datatype}'")

            if 'float' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', float({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, float(value), timeout=DEFAULT_TIMEOUT)
            elif 'int' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', int({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, int(value), timeout=DEFAULT_TIMEOUT)
            elif 'bool' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', bool({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, bool(value), timeout=DEFAULT_TIMEOUT)
            elif 'binary' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', f'{value.encode('utf-8')}', timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, f"{value.encode('utf-8')}", timeout=DEFAULT_TIMEOUT)
            else:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', f'{value}', timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, f"{value}", timeout=DEFAULT_TIMEOUT)

        except Exception as _:
            if self.__log:
                self.__log.error(f"failure in radio_toggled(), error='{_}'")

    # +
    # method: slider_button_released() - SEND TO INDI!
    # -
    def slider_button_released(self):
        try:
            value = self.sender().value()
            title = self.sender().windowTitle().strip()
            datatype = TAB_DATA[self.__module][title].get('datatype', '').strip()
            if self.__log:
                self.__log.debug(f"title='{title}', value='{value}', datatype='{datatype}'")

            if 'float' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', float({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, float(value), timeout=DEFAULT_TIMEOUT)
            elif 'int' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', int({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, int(value), timeout=DEFAULT_TIMEOUT)
            elif 'bool' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', bool({value}), timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, bool(value), timeout=DEFAULT_TIMEOUT)
            elif 'binary' in datatype:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', f'{value.encode('utf-8')}', timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, f"{value.encode('utf-8')}", timeout=DEFAULT_TIMEOUT)
            else:
                if self.__log:
                    self.__log.info(f"calling setINDI('{title}', f'{value}', timeout=DEFAULT_TIMEOUT)")
                if not self.__simulate and hasattr('setINDI', self.__pi):
                    self.__pi.setINDI(title, f"{value}", timeout=DEFAULT_TIMEOUT)

        except Exception as _:
            if self.__log:
                self.__log.error(f"failure in slider_button_released(), error='{_}'")

    # +
    # method: slider_value_changed()
    # -
    def slider_value_changed(self):

        # initialize variable(s)
        # value, sender, title = None, '', ''
        w, n = None, None
        _min, _max, _half, _onepc = math.nan, math.nan, math.nan, math.nan

        # get value(s) from sender (caller)
        value = self.sender().value()
        sender = self.sender()
        title = self.sender().windowTitle().strip()
        if self.__log:
            self.__log.warning(f"{title} slider value changed to {value}")

        # get n if we know about it and update display
        if title in self.__lcds:
            n = self.__lcds.get(title, None)
        if n is not None:
            n.display(value)

        # get limits if we know about them
        if title in self.__slds:
            _min, _max, _half, _onepc = self.__slds.get(title, (math.nan, math.nan, math.nan, math.nan))

        # get w if we know about it and update gui
        if title in TAB_DATA[self.__module]:
            w = TAB_DATA[self.__module].get('widget', sender)
        if w is not None:
            # cold
            if value < _min:
                w.setStyleSheet(f"background-color: '{BLUE}'; color: '{YELLOW}';")
            # hot
            elif value > _max:
                w.setStyleSheet(f"background-color: '{RED}'; color: '{YELLOW}';")
            # normal
            else:
                w.setStyleSheet(f"background-color: '{self.__fg}'; color: '{self.__bg}';")  # reverse video!

    # +
    # (hidden) method: __update_label__()
    # -
    def __update_label__(self, flag: bool = False, msg: str = ''):
        self.__connected = flag
        self.__connected_label.clear()
        self.__connected_label.setText(f"{msg:75s}")
        if flag:
            self.__connected_icon.setPixmap(QPixmap('plug-connect.png'))
            self.__connected_label.setStyleSheet(f"background-color: '{LIGHTGREEN}'; color: '{BLUE}';")
            self.__simulate = False
            self.__action_simulate.setChecked(False)
        else:
            self.__connected_icon.setPixmap(QPixmap('plug-disconnect.png'))
            self.__connected_label.setStyleSheet(f"background-color: '{RED}'; color: '{YELLOW}';")
            self.__simulate = True
            self.__action_simulate.setChecked(True)

    # +
    # method: create_user_interface()
    # -
    def create_user_interface(self):

        # create widget(s)
        self.__create_menu__()
        self.__create_tabbed__()

        self.__timer.timeout.connect(self.alarm)

        # show frame
        self.setMenuBar(self.__menubar)
        self.__menubar.setNativeMenuBar(False)
        self.setCentralWidget(self.__tabs)
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle(f"{NAME}")

    # +
    # method: connect_to_indi()
    # -
    # noinspection PyBroadException
    def connect_to_indi(self):

        # connect to indi
        try:
            if self.__pi is None:
                # noinspection PyUnresolvedReferences
                self.__pi = PyINDI2(verbose=False)
        except Exception as _e0:
            self.__update_label__(False, f"failed to connect to indi, error='{_e0}'")
            self.__pi = None
        else:

            # subscribe to streams
            self.__update_label__(True, f"connected to indi OK")
            try:
                for _idx, _elem in enumerate(self.__indi_streams):
                    _dev, _nam = _elem.split('.')
                    if self.__log:
                        self.__log.debug(f"subscribing to streams, device='{_dev}', name='{_nam}'")
                    self.__pi.sub(device=_dev, name=_nam)
            except Exception as _e1:
                self.__update_label__(False, f"failed to subscribe to streams, error='{_e1}'")
            else:
                if self.__log:
                    self.__log.debug(f"subscribed to {self.__pi.subs}")
                self.__update_label__(True, "subscribed to streams OK")
                # self.__timer.start(self.__delay)

    # +
    # method: disconnect_from_indi()
    # -
    def disconnect_from_indi(self):
        try:
            for _idx, _elem in enumerate(self.__indi_streams):
                _dev, _nam = _elem.split('.')
                if self.__log:
                    self.__log.error(f"unsubscribing from device='{_dev}', name='{_nam}'")
                self.__pi.unsub(device=_dev, name=_nam)
        except Exception as _:
            self.__update_label__(False, f"Failed to disconnect from indi streams, error='{_}'")
        else:
            self.__update_label__(False, "Disconnected from INDI")
            # self.__timer.stop()

    # +
    # method: set_simulate()
    # -
    def set_simulate(self, state):
        if state:
            self.__menubar.setStyleSheet(f"background-color: '{ALARMRED}'; color: '{ALARMORANGE}'; border: solid 2px;")
            self.__simulate = True
        else:
            self.__menubar.setStyleSheet(f"background-color: '{PALEGREEN}'E2FDDB; color: '{BLUE}'; border: solid 2px;")
            self.__simulate = False

    # +
    # method: show_about()
    # -
    @staticmethod
    def show_about():
        _mbox = QMessageBox()
        _mbox.setFont(QFont('Times New Roman', 12))
        _mbox.setIcon(QMessageBox.Icon.Information)
        _mbox.setWindowTitle(f"{NAME}")
        _mbox.setWindowIcon(QIcon('information-frame.png'))
        _mbox.setText(f"\n{NAME}\nAuthor: {AUTHOR}\nEmail: {EMAIL}\nVersion: {VERSION}\nRevision Date: {DATE}\n\nPython: {platform.python_version()}\nQt: {qVersion()}")
        _mbox.setStyleSheet(f"background-color: '{PALEGREEN}'; color: '{BLUE}'; border: solid 2px;")
        _mbox.exec()

    # +
    # (over-ride) method: closeEvent()
    # -
    # noinspection PyPep8Naming,PyMethodOverriding
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Quit Confirmation", "Are you sure you want to quit?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    # +
    # method:alarm()
    # -
    def alarm(self):
        self.__step += 1
        _actval, _widget, _type, _value = None, None, None, None
        if self.__simulate:
            TAB_DATA[self.__module] = update_dictionary(_dict=TAB_DATA[self.__module])
            for _k, _v in TAB_DATA[self.__module].items():
                _actval = _v['actval']
                _type = _v['datatype'].strip().lower()
                _widget = self.__vals[_k] if _k in self.__vals else None
                _value = _widget.text() if hasattr(_widget, 'text') else None
                if hasattr(_widget, 'setText'):
                    if 'float' in _type and float(_value) != float(_actval):
                        _widget.setText(f"{float(_actval)}")
                    elif 'int' in _type and int(_value) != int(_actval):
                        _widget.setText(f"{int(_actval)}")
                    elif 'bool' in _type:
                        _widget.setText(f"{bool(_actval)}")
                    elif 'binary' in _type:
                        _widget.setText(f"{_actval('utf-8')}")
                    else:
                        _widget.setText(f"{_actval}")
                    _min, _max = _v['datarange'] if len(_v['datarange']) == 2 else (-math.nan, math.nan)

                    # change label if running hot, cold, or normal
                    if isinstance(_v['datarange'], tuple) and len(_v['datarange']) == 2:
                        _min, _max = _v['datarange']
                        # cold
                        if float(_actval) < _min: 
                            if self.__log:
                                self.__log.warning(f"{_k} value too cold! {_actval} < {_min}")
                            _widget.setStyleSheet(f"background-color: '{BLUE}'; color: '{YELLOW}';")
                        # hot
                        elif float(_actval) > _max: 
                            if self.__log:
                                self.__log.warning(f"{_k} value too hot! {_actval} > {_max}")
                            _widget.setStyleSheet(f"background-color: '{RED}'; color: '{YELLOW}';")
                        # normal
                        else:
                            _widget.setStyleSheet(f"background-color: '{self.__bg}'; color: '{self.__fg}';")
                    elif isinstance(_v['datarange'], list):
                        # invalid
                        if _actval not in _v['datarange']:
                            _widget.setStyleSheet(f"background-color: '{YELLOW}'; color: '{BLUE}';")
                        # normal
                        else:
                            _widget.setStyleSheet(f"background-color: '{self.__bg}'; color: '{self.__fg}';")

        else:
            try:
                _ret = self.__pi.Q.get(block=True, timeout=DEFAULT_TIMEOUT)
            except queue.Empty:
                pass
            except Exception as _:
                if self.__log:
                    self.__log.error(f"{_}")
                    if not self.__connected:
                        self.__log.error(f"You are not connected to the IndiServer!")
            else:
                if self.__log:
                    self.__log.debug(f"_ret={_ret}, type={type(_ret)}")
                for _k, _v in _ret.items():
                    if _k in TAB_DATA[self.__module]:
                        _type = TAB_DATA[_k]['datatype']
                        _widget = self.__vals[_k]
                        if hasattr(_widget, 'setText'):
                            if 'float' in _type:
                                TAB_DATA[_k]['actval'] = float(_v)
                                _widget.setText(f"{float(_v)}")
                            elif 'int' in _type:
                                TAB_DATA[_k]['actval'] = int(_v)
                                _widget.setText(f"{int(_v)}")
                            elif 'bool' in _type:
                                TAB_DATA[_k]['actval'] = bool(_v)
                                _widget.setText(f"{bool(_v)}")
                            elif 'binary' in _type:
                                TAB_DATA[_k]['actval'] = f"{_v.encode('utf-8')}"
                                _widget.setText(f"{_v.encode('utf-8')}")
                            else:
                                TAB_DATA[_k]['actval'] = f"{_v}"
                                _widget.setText(f"{_v}")

                    # change label if running hot, cold, or normal
                    if isinstance(_v['datarange'], tuple) and len(_v['datarange']) == 2:
                        _min, _max = _v['datarange']
                        # noinspection PyTypeChecker
                        if float(_actval) < _min:
                            if self.__log:
                                self.__log.warning(f"{_k} value too cold! {_actval} < {_min}")
                            _widget.setStyleSheet(f"background-color: '{BLUE}'; color: '{YELLOW}';")
                        elif float(_actval) > _max: 
                            if self.__log:
                                self.__log.warning(f"{_k} value too hot! {_actval} > {_max}")
                            _widget.setStyleSheet(f"background-color: '{RED}'; color: '{YELLOW}';")
                        else:
                            _widget.setStyleSheet(f"background-color: '{self.__bg}'; color: '{self.__fg}';")
                    elif isinstance(_v['datarange'], list):
                        if _actval not in _v['datarange']:
                            _widget.setStyleSheet(f"background-color: '{YELLOW}'; color: '{BLUE}';")
                        else:
                            _widget.setStyleSheet(f"background-color: '{self.__bg}'; color: '{self.__fg}';")

    # +
    # function: split_list()
    # -
    # noinspection PyBroadException
    @staticmethod
    def split_keyvals(_list: list = None, _pages: int = 0, _chunk: int = DEFAULT_ITEMS) -> tuple:
        try:
            # adjust page(s)
            if _pages * _chunk < len(_list):
                _pages += 1
            # pad to boundary
            _list += [('', {})] * ((_pages * _chunk) - len(_list))
            # create new list
            _nlist = []
            for _i in range(0, len(_list), _chunk):
                _nlist.append(_list[_i:_i+_chunk])
            return _nlist, _pages, _chunk
        except:
            return _list, -1, -2


# +
# function: execute()
# -
def execute(_host: str = DEFAULT_HOST, _port: int = DEFAULT_PORT,
            _items: int = DEFAULT_ITEMS, _delay: int = DEFAULT_DELAY,
            _fg: str = DEFAULT_FG, _bg: str = DEFAULT_BG,
            _module: str = DEFAULT_MODULE, _log: logging.Logger = None) -> None:
    app = QApplication([])
    _ = MapsControlGui(host=_host, port=_port, items=_items, delay=_delay, fg=_fg, bg=_bg, module=_module, log=_log)
    if _.indi_nelms != 0:
        _.show()
        sys.exit(app.exec())


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _p = argparse.ArgumentParser(description='maps control gui', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--host', default=DEFAULT_HOST, help="""Host ['%(default)s']""")
    _p.add_argument('--port', default=DEFAULT_PORT, help="""Port [%(default)s]""")
    _p.add_argument('--module', default=DEFAULT_MODULE, help=f"""Module [%(default)s], choice of {MODULES}""")
    _p.add_argument('--delay', default=DEFAULT_DELAY, help=f"""Delay Period (ms) [%(default)s]""")
    _p.add_argument('--items', default=DEFAULT_ITEMS, help=f"""Items / Tab [%(default)s]""")
    _p.add_argument('--fg', default=DEFAULT_FG, help=f"""Foreground color [%(default)s]""")
    _p.add_argument('--bg', default=DEFAULT_BG, help=f"""Background color [%(default)s]""")
    _a = _p.parse_args()

    # noinspection PyBroadException
    try:
        execute(_host=_a.host.strip(), _port=int(_a.port),
                _items=int(_a.items), _delay=int(_a.delay),
                _fg=_a.fg.strip(), _bg=_a.bg.strip(), _module=_a.module.strip(),
                _log=UtilLogger(name='maps_control_gui', level='DEBUG').logger)
    except Exception as _:
        print(f"{_}\nUse: {__doc__}")
