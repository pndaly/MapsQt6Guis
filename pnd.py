#!/usr/bin/env python3


# +
# import(s)
# -
from astropy.coordinates import AltAz
from astropy.coordinates import EarthLocation
from astropy.coordinates import get_body
from astropy.time import Time
from astropy import units as u
from datetime import datetime
from datetime import timedelta
from typing import Any

import hashlib
import logging
import logging.config
import math
import os
import platform
import random


# +
# initialize
# -
random.seed(os.getpid())


# +
# constant(s)
# -
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 7624
DEFAULT_TIMEOUT = 5
DEGREE = u'\u00b0'
FALSE_VALUES = [0, False, '0', 'false', 'f', 'FALSE', 'F']
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
ISO_PATTERN = '[0-9]{4}-[0-9]{2}-[0-9]{2}[ T?][0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}'
LOG_CLR_FMT = '%(log_color)s%(asctime)-20s line:%(lineno)-5d %(message)s'
LOG_CSL_FMT = '%(asctime)-20s line:%(lineno)-5d %(message)s'
LOG_FIL_FMT = '%(asctime)-20s line:%(lineno)-5d %(message)s'
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
MAX_BYTES = 9223372036854775807
MICRON = u'\u03bc'
SUPPORTED_COLORS = ['black', 'blue', 'cyan', 'green', 'magenta', 'red', 'yellow']
TRUE_VALUES = [1, True, '1', 'true', 't', 'TRUE', 'T']


# +
# telescope(s)
# -
BOK_ELEVATION_FEET = 6795.0
BOK_ELEVATION_METRES = BOK_ELEVATION_FEET * 0.3048
BOK_LATITUDE_DEGREES = 31.9629
BOK_LONGITUDE_DEGREES = -111.6004
KUIPER_ELEVATION_FEET = 8235.0
KUIPER_ELEVATION_METRES = KUIPER_ELEVATION_FEET * 0.3048
KUIPER_LATITUDE_DEGREES = 32.4165
KUIPER_LONGITUDE_DEGREES = -110.7345
LBT_ELEVATION_FEET = 10567.0
LBT_ELEVATION_METRES = LBT_ELEVATION_FEET * 0.3048
LBT_LATITUDE_DEGREES = 32.7016
LBT_LONGITUDE_DEGREES = -109.8719
MMT_ELEVATION_FEET = 8585.0
MMT_ELEVATION_METRES = MMT_ELEVATION_FEET * 0.3048
MMT_LATITUDE_DEGREES = 31.6883
MMT_LONGITUDE_DEGREES = -110.8850
VATT_ELEVATION_FEET = 10469.0
VATT_ELEVATION_METRES = VATT_ELEVATION_FEET * 0.3048
VATT_LATITUDE_DEGREES = 32.7016
VATT_LONGITUDE_DEGREES = -109.8719


# +
# function(s)
# -
# noinspection PyBroadException
def get_isot(ndays: float = 0.0) -> str:
    """returns the offset date in isot format or an empty string"""
    try:
        return (datetime.now() + timedelta(days=ndays)).isoformat()
    except:
        return f''


# noinspection PyBroadException
def get_utc(ndays: float = 0.0) -> str:
    """returns the offset utc date in isot format or an empty string"""
    try:
        return (datetime.utcnow() + timedelta(days=ndays)).isoformat()
    except:
        return f''


# noinspection PyBroadException
def get_jd(ndays: float = 0.0) -> float:
    """returns an offset jd or NaN"""
    try:
        return float(Time(get_isot(ndays)).jd)
    except:
        return math.nan


# noinspection PyBroadException
def isot_to_jd(isot: str = '') -> float:
    """returns jd from date in isot format or NaN"""
    try:
        return float(Time(isot).jd)
    except:
        return math.nan


# noinspection PyBroadException
def jd_to_isot(jd: float = math.nan) -> str:
    """returns the date in isot format from jd or an empty string"""
    try:
        return Time(jd, format='jd', precision=6).isot
    except:
        return f''


# noinspection PyBroadException
def get_unix(ndays: float = 0.0) -> int:
    """returns the unix time date or -1"""
    try:
        _now = isot_to_jd(get_utc(ndays=ndays))
        _then = isot_to_jd('1970-01-01T00:00:00.00')
        return int(round((_now - _then)*86400.0))
    except:
        return -1


# noinspection PyBroadException
def get_lst(lat: float = MMT_LATITUDE_DEGREES, lon: float = MMT_LONGITUDE_DEGREES, ele: float = MMT_ELEVATION_METRES) -> str:
    """returns lst or an empty string"""
    try:
        _obs = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=ele*u.m)
        _time = Time(get_utc(), scale='utc', location=_obs)
        _h, _m, _s = _time.sidereal_time('mean').hms
        return f"{int(_h):02d}:{int(_m):02d}:{float(_s):05.2f}"
    except:
        return ''


# noinspection PyBroadException
def get_moon(lat: float = MMT_LATITUDE_DEGREES, lon: float = MMT_LONGITUDE_DEGREES, ele: float = MMT_ELEVATION_METRES) -> tuple:
    """returns moon alt, az or (NaN, NaN)"""
    try:
        _obs = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=ele*u.m)
        _time = Time(get_utc(), scale='utc', location=_obs)
        _moon = get_body('moon', _time)
        _altaz = _moon.transform_to(AltAz(obstime=_time, location=_obs))
        return _altaz.alt.value, _altaz.az.value
    except:
        return math.nan, math.nan


# noinspection PyBroadException
def get_sun(lat: float = MMT_LATITUDE_DEGREES, lon: float = MMT_LONGITUDE_DEGREES, ele: float = MMT_ELEVATION_METRES) -> tuple:
    """returns sun alt, az or (NaN, NaN)"""
    try:
        _obs = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=ele*u.m)
        _time = Time(get_utc(), scale='utc', location=_obs)
        _moon = get_body('sun', _time)
        _altaz = _moon.transform_to(AltAz(obstime=_time, location=_obs))
        return _altaz.alt.value, _altaz.az.value
    except:
        return math.nan, math.nan


# noinspection PyBroadException
def get_hash() -> str:
    """returns a random hash string or an empty string"""
    try:
        return hashlib.sha256(get_isot().encode('utf-8')).hexdigest()
    except:
        return f''


# noinspection PyBroadException
def color_print(msg: str = "", color: str = SUPPORTED_COLORS[0], height: int = 1) -> None:
    """prints a message in single or double height characters if the terminal supports control codes"""
    _clr = color if color in SUPPORTED_COLORS else SUPPORTED_COLORS[0]
    _siz = height if height in (1, 2) else 1
    _dict = {
        "black_1": f"\033[0;30m{msg}\033[0m",
        "blue_1": f"\033[0;34m{msg}\033[0m",
        "cyan_1": f"\033[0;36m{msg}\033[0m",
        "green_1": f"\033[0;32m{msg}\033[0m",
        "magenta_1": f"\033[0;35m{msg}\033[0m",
        "red_1": f"\033[0;31m{msg}\033[0m",
        "yellow_1": f"\033[0;33m{msg}\033[0m",
        "black_2": f"\033[0;30m\033#3{msg}\n\033#4{msg}\033[0m",
        "blue_2": f"\033[0;34m\033#3{msg}\n\033#4{msg}\033[0m",
        "cyan_2": f"\033[0;36m\033#3{msg}\n\033#4{msg}\033[0m",
        "green_2": f"\033[0;32m\033#3{msg}\n\033#4{msg}\033[0m",
        "magenta_2": f"\033[0;35m\033#3{msg}\n\033#4{msg}\033[0m",
        "red_2": f"\033[0;31m\033#3{msg}\n\033#4{msg}\033[0m",
        "yellow_2": f"\033[0;33m\033#3{msg}\n\033#4{msg}\033[0m"
    }
    print(_dict.get(f"{_clr}_{_siz}", ""))


# noinspection PyBroadException
def flatten_dictionary(_dict: Any = None, _sep: str = '.', _pre: str = '') -> dict:
    """returns a flattened dictionary or {}"""
    try:
        return {
            f"{_pre}{_sep}{_k1}" if _pre else _k1: _v1
            for _k2, _v2 in _dict.items()
            for _k1, _v1 in flatten_dictionary(_v2, _sep, _k2).items()
        } if isinstance(_dict, dict) else {_pre: _dict}
    except:
        return {}


# +
# class: CustomException()
# use: raise CustomException(errnum=-2, extra='Something bad happened!')
# -
class CustomException(Exception):
    """raise custom exception from pre-defined dictionary"""

    # +
    # class variable(s)
    # -
    error_dictionary = { 
        0: 'OK', 
        -1: 'Undefined error', 
        -2: 'Incorrect arguments',
        -3: 'Incorrect datatype', 
        -4: 'Data out of range'
    }
    error_number = [_ for _ in error_dictionary.keys()]
    error_text = [_ for _ in error_dictionary.values()]
    pv = f'{platform.python_version()}'

    # +
    # (hidden) method: __init__()
    # -
    def __init__(self, errnum: int = -1, extra: str = ''):
        self.errnum = errnum
        self.extra = extra
        self.__errstr = f"code={self.__errnum}, message='{self.error_dictionary.get(self.__errnum, -1)}', " \
                        f"extra='{extra}', python_version='{self.pv}'"
        super().__init__(self.__errstr)

    # +
    # decorator(s)
    # -
    @property
    def errnum(self) -> int:
        return int(self.__errnum)

    @errnum.setter
    def errnum(self, errnum: int = -1) -> None:
        self.__errnum = errnum if errnum in self.error_number else -1

    @property
    def extra(self) -> str:
        return f"{self.__extra}"

    @extra.setter
    def extra(self, extra: str = '') -> None:
        self.__extra = extra

    @property
    def errstr(self) -> str:
        return f"{self.__errstr}"


# +
# class: UtilLogger()
# use: log = UtilLogger(name='CustomLogger', level='DEBUG').logger
#      log.debug(f"Logger is working")
# -
class UtilLogger(object):
    """returns a singleton class logging object"""

    # +
    # (hidden) method: __init__()
    # -
    def __init__(self, name: str = '', level: str = LOG_LEVELS[0]) -> None:

        # get arguments(s)
        self.name = name
        self.level = level

        # define some variables and initialize them
        self.__msg = None
        self.__logfile = f'/tmp/{self.__name}.log'

        # logger dictionary
        sassy_logger_dictionary = {

            # logging version
            'version': 1,

            # do not disable any existing loggers
            'disable_existing_loggers': False,

            # use the same formatter for everything
            'formatters': {
                'SassyColoredFormatter': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': LOG_CLR_FMT,
                    'log_colors': {
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'white,bg_red',
                    }
                },
                'SassyConsoleFormatter': {
                    'format': LOG_CSL_FMT
                },
                'SassyFileFormatter': {
                    'format': LOG_FIL_FMT
                }
            },

            # define file and console handlers
            'handlers': {
                'colored': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'SassyColoredFormatter',
                    'level': self.__level,
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'SassyConsoleFormatter',
                    'level': self.__level,
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'backupCount': 10,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'SassyFileFormatter',
                    'filename': self.__logfile,
                    'level': self.__level,
                    'maxBytes': MAX_BYTES
                }
            },

            # make this logger use file and console handlers
            'loggers': {
                self.__name: {
                    'handlers': ['colored', 'file'],
                    'level': self.__level,
                    'propagate': True
                }
            }
        }

        # configure logger
        logging.config.dictConfig(sassy_logger_dictionary)

        # get logger
        self.logger = logging.getLogger(self.__name)

    # +
    # decorator(s)
    # -
    @property
    def name(self) -> str:
        return f"{self.__name}"

    @name.setter
    def name(self, name: str = '') -> None:
        self.__name = name if name.strip() != '' else os.getenv('USER')

    @property
    def level(self) -> str:
        return f"{self.__level}"

    @level.setter
    def level(self, level: str = '') -> None:
        self.__level = level.strip().upper() if level.strip().upper() in LOG_LEVELS else LOG_LEVELS[0]
