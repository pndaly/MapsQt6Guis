#!/usr/bin/env python3


# +
# import(s)
# -
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from pnd import *
from maps_status_indi import *

try:
    from pyindi2 import *
except:
    pass

import argparse
import platform
import sys


# +
# constant(s)
# -
__doc__ = """python3 maps_status_gui.py --help"""

AUTHOR = 'Phil Daly'
DATE = 20240319
EMAIL = 'pndaly@arizona.edu'
NAME = 'MAPS Status GUI'
VERSION = '0.0.0'

ITEMS_PER_TAB = 25
MODULES = [_ for _ in list(TAB_DATA.keys())]

DEFAULT_HOST = 'localhost'
DEFAULT_MODULE = MODULES[-1]
DEFAULT_PORT = 7624
DEFAULT_TIMEOUT = 5


# +
# class: MapsStatusGui()
# -
# noinspection PyArgumentList
class MapsStatusGui(QMainWindow):

    # +
    # (hidden) method: __init__()
    # -
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, 
                 module: str = DEFAULT_MODULE, log: logging.Logger = None) -> None:

        # get argument(s)
        self.host = host
        self.port = port
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

        # initialize (some) widget(s)
        self.__central_widget = None
        self.__connected_icon = QLabel()
        self.__connected_label = QLabel()
        self.__menubar = QMenuBar()
        self.__statusbar = QStatusBar()
        self.__timer = QTimer()
        self.__tabs = QTabWidget()

        # indi streams we wish to subscribe to
        self.__indi_streams = list(set([f"{_.split('.')[0]}.{_.split('.')[1]}"
                                        for _ in TAB_DATA.get(self.__module).keys()]))
        self.__indi_nelms = len([_ for _ in TAB_DATA.get(self.__module).keys()])

        # create user interface
        self.create_user_interface()

        # if we are not in simulation mode, connect to the indiserver
        if not self.__simulate:
            self.__pi = PyINDI2(verbose=False)

        self.__dump__('pars')
        self.__dump__('vars')

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
    def module(self) -> str:
        return f"{self.__module}"

    @module.setter
    def module(self, module: str = DEFAULT_MODULE) -> None:
        self.__module = module if module in MODULES else DEFAULT_MODULE

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
    def indi_streams(self) -> str:
        return f"{self.__indi_streams}"

    @property
    def indi_nelms(self) -> int:
        return int(self.__indi_nelms)

    # +
    # (hidden) method: __dump__()
    # -
    def __dump__(self, which: str = "pars") -> None:
        if which.lower().strip() == "pars":
            if self.__log:
                self.__log.debug(f"self='{self}', host={self.__host}, port={self.__port}, log={self.__log}")
        elif which.lower().strip() == "vars":
            if self.__log:
                self.__log.debug(f"self.__indi_streams={self.__indi_streams}, "
                                 f"self.__indi_nelms={self.__indi_nelms}, "
                                 f"self.__connected={self.__connected}, "
                                 f"self.__pi={self.__pi}, "
                                 f"self.__simulate={self.__simulate}, "
                                 f"self.__step={self.__step}")

    # +
    # (hidden) method: __create_tooltip__()
    # -
    def __create_tooltip__(self):
        QToolTip.setFont(QFont('Ariel', 10))
        self.setToolTip(f"{NAME}: {AUTHOR} ({EMAIL})\tVersion: {VERSION}\tRevision Date: {DATE}")
        self.setStyleSheet("""QToolTip { background-color: #E2FDDB; color: blue; border: solid 2px }""")

    # +
    # (hidden) method: __create_menu__()
    # -
    def __create_menu__(self):

        self.__action_connect = QAction(QIcon('plug-connect.png'), '&Connect', self)
        self.__action_connect.setShortcut(QKeySequence('Alt+C'))
        self.__action_connect.setStatusTip('Connect to IndiServer')
        self.__action_connect.triggered.connect(self.connect_to_indi)

        self.__action_disconnect = QAction(QIcon('plug-disconnect.png'), '&Disconnect', self)
        self.__action_disconnect.setShortcut('Alt+D')
        self.__action_disconnect.setStatusTip('Disconnect from IndiServer')
        self.__action_disconnect.triggered.connect(self.disconnect_from_indi)

        self.__action_about = QAction(QIcon('information-frame.png'), '&About', self)
        self.__action_about.setShortcut('Alt+A')
        self.__action_about.setStatusTip(f'About {NAME}')
        self.__action_about.triggered.connect(self.show_about)

        self.__action_quit = QAction(QIcon('cross-circle-frame.png'), '&Quit', self)
        self.__action_quit.setShortcut('Alt+Q')
        self.__action_quit.setStatusTip('Exit application')
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
        self.__action_simulate.setStatusTip('Toggle simulation')
        self.__action_simulate.setChecked(True)
        self.__action_simulate.triggered.connect(self.set_simulate)

        self.__menubar.setStyleSheet("""background-color: #AA0000; color: orange; border: solid 2px""")
        self.__simmenu = self.__menubar.addMenu('Simulate')
        self.__simmenu.addAction(self.__action_simulate)

    # +
    # (hidden) method: __create_status_bar__()
    # -
    def __create_status_bar__(self):
        self.__statusbar.setStyleSheet("background-color: #E2FDDB;")
        self.__statusbar.setFont(QFont("Bitstream Charter", 12, italic=True))
        self.__statusbar.showMessage("")
        self.setStatusBar(self.__statusbar)

    # +
    # (hidden) method: __create_tabbed__()
    # -
    def __create_tabbed__(self):
        self.__tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.__tabs.setMovable(True)
        if self.__module in TAB_DATA:

            # create a placeholder widget and insert into horizontal layout
            w = QWidget()
            h = QHBoxLayout(w)

            # create left and right group(s)
            right = QGroupBox('Value(s)')
            right.setStyleSheet(f"background-color: {TAB_COLORS.get(self.__module)};")
            right.setFont(QFont("Bitstream Charter", 12, italic=True))
            left = QGroupBox('Stream(s)')
            left.setStyleSheet(f"background-color: {TAB_COLORS.get(self.__module)};")
            left.setFont(QFont("Bitstream Charter", 12, italic=True))

            # add left and right group(s) into horizontal layout and create grid(s)
            h.addWidget(left)
            h.addWidget(right)
            rg = QGridLayout()        
            lg = QGridLayout()

            # populate gui
            _ic = 0
            for _k, _v in TAB_DATA[self.__module].items():

                # populate grid(s)
                _data = TAB_DATA[self.__module]
                _items = [_ for _ in list(_data.keys())]

                if isinstance(_data[_k]['label'], str) and _data[_k]['label'].strip() != '':
                    _data[_k]['label'] = QLabel(f"{_data[_k]['label']}")
                else:
                    _data[_k]['label'] = QLabel(f"{_k}")
                _data[_k]['label'].setToolTip(f"{_data[_k]['tooltip']}")

                _data[_k]['widget'] = QLabel(f"{_data[_k]['actval']} {_data[_k]['unit']}")
                lg.addWidget(_data[_k]['label'], _ic, 0)
                rg.addWidget(_data[_k]['widget'], _ic, 0)
                _ic += 1

                # set layout into group(s) and add tab
                right.setLayout(rg)
                left.setLayout(lg)
                self.__tabs.addTab(w, f"{TAB_NAMES.get(self.__module)}")

    # +
    # (hidden) method: __update_label__()
    # -
    def __update_label__(self, flag: bool = False, msg: str = ''):
        # self.__dump__("widgets")
        # self.__dump__("values")
        self.__connected = flag
        self.__connected_label.clear()
        self.__connected_label.setText(f"{msg:75s}")
        if flag:
            self.__connected_icon.setPixmap(QPixmap('plug-connect.png'))
            self.__connected_label.setStyleSheet("background-color: lightgreen;")
            self.__simulate = False
            self.__action_simulate.setChecked(False)
        else:
            self.__connected_icon.setPixmap(QPixmap('plug-disconnect.png'))
            self.__connected_label.setStyleSheet("background-color: red;")
            self.__simulate = True
            self.__action_simulate.setChecked(True)
        # self.__dump__("widgets")
        # self.__dump__("values")

    # +
    # method: create_user_interface()
    # -
    def create_user_interface(self):

        # create widget(s)
        self.__create_tooltip__()
        self.__create_menu__()
        self.__create_status_bar__()
        self.__create_tabbed__()

        self.__timer.timeout.connect(self.alarm)

        # show frame
        self.setMenuBar(self.__menubar)
        self.__menubar.setNativeMenuBar(False)
        self.setCentralWidget(self.__tabs)
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle(f"{NAME}")
        # self.show()

    # +
    # method: connect_to_indi()
    # -
    # noinspection PyBroadException
    def connect_to_indi(self):

        # connect to indi
        try:
            if self.__pi is None:
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
                self.__timer.start(2000)

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
            self.__timer.stop()
            # for _k, _v in self.__indi_values.items():
            #     _type = str(type(self.__indi_values))
            #     if 'float' in _type:
            #         self.__indi_values = {**self.__indi_values, **{_k: math.nan}}
            #     elif 'int' in _type:
            #         self.__indi_values = {**self.__indi_values, **{_k: -1}}
            #     else:
            #         self.__indi_values = {**self.__indi_values, **{_k: "unknown"}}
            # for _k, _v in self.__indi_values.items():
            #     self.__indi_widgets.get(_k).setText(f"{_v}")

    # +
    # method: set_simulate()
    # -
    def set_simulate(self, state):
        if state:
            self.__action_simulate.setStatusTip('Simulation mode enabled')
            self.__menubar.setStyleSheet("""background-color: #AA0000; color: orange; border: solid 2px""")
            self.__simulate = True
        else:
            self.__action_simulate.setStatusTip('Simulation mode disabled')
            self.__menubar.setStyleSheet("""background-color: #E2FDDB; color: blue; border: solid 2px""")
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
        _mbox.setText(f"\n{NAME}\nAuthor: {AUTHOR}\nEmail: {EMAIL}\nVersion: {VERSION}\nRevision Date: {DATE}\n\nPython: {platform.python_version()}\nQt6: {qVersion()}")
        _mbox.setStyleSheet("""background-color: #E2FDDB; color: blue; border: solid 2px""")
        _mbox.exec()

    # +
    # (over-ride) method: closeEvent()
    # -
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
        try:
            _ret = self.__pi.Q.get(block=True, timeout=DEFAULT_TIMEOUT)
        except queue.Empty:
            pass
        except Exception as _:
            if self.__log:
                self.__log.error(f"{_}")
        else:
            if self.__log:
                self.__log.debug(f"_ret={_ret}, type={type(_ret)}")
            # for _k, _v in _ret.items():
            #     if _k in self.__indi_values and _k in self.__indi_widgets:
            #         _type = str(type(self.__indi_values))
            #         if 'float' in _type:
            #             self.__indi_values = {**self.__indi_values, **{_k: float(_v)}}
            #             self.__indi_widgets.get(_k).setText(f"{float(_v)}")
            #         elif 'int' in _type:
            #             self.__indi_values = {**self.__indi_values, **{_k: int(_v)}}
            #             self.__indi_widgets.get(_k).setText(f"{int(_v)}")
            #         else:
            #             self.__indi_values = {**self.__indi_values, **{_k: f"{_v}"}}
            #             self.__indi_widgets.get(_k).setText(f"{_v}")
        self.__step += 1
        # self.__dump__('values')


# +
# function: execute()
# -
def execute(_host: str = DEFAULT_HOST, _port: int = DEFAULT_PORT, _module: str = DEFAULT_MODULE, _log: logging.Logger = None) -> None:
    app = QApplication([])
    _ = MapsStatusGui(host=_host, port=_port, module=_module, log=_log)
    _.show()
    sys.exit(app.exec())


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _p = argparse.ArgumentParser(description='maps status gui', formatter_class=argparse.RawTextHelpFormatter)
    _p.add_argument('--host', default=DEFAULT_HOST, help="""Host ['%(default)s']""")
    _p.add_argument('--port', default=DEFAULT_PORT, help="""Port [%(default)s]""")
    _p.add_argument('--module', default=DEFAULT_MODULE, help=f"""Module [%(default)s], choice of {MODULES}""")
    _a = _p.parse_args()

    # noinspection PyBroadException
    # try:
    execute(_host=_a.host.strip(), _port=int(_a.port), _module=_a.module.strip(), _log=UtilLogger(name='maps_status_gui', level='DEBUG').logger)
    # except Exception as _:
    #     print(f"{_}\nUse: {__doc__}")
