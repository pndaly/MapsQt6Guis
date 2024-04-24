# MAPS Qt6 GUIs

These are the status and control GUIs for part of the MAPS project on MMT.

## Installation

```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python3 -m pip install --upgrade pip
  python3 -m pip install numpy
  python3 -m pip install astropy
  python3 -m pip install colorlog
  python3 -m pip install pyqt6
```

NB: A virtual environment is *not* required so you can omit the first 2 above commands.


## Quick Start

To run the GUI:

```bash
  python3 maps_status_gui.py --help
```

An example of running mutliple GUIs, is:

```bash
  python3 maps_status_gui.py --module=Phil &

  python3 maps_status_gui.py --module=Time &

  python3 maps_status_gui.py --module=CyberPower &

  python3 maps_status_gui.py --module=Amali &
```


## Important Files

### maps_status_indi.py

This contains large data structures associated with INDI streams. If you edit this file, you should run the
sanity check(s) to ensure data integrity, consistency and validity by executing:

```bash
  python3 maps_status_indi.py
```

If it returns an error, please correct it before proceeding with any other development.

### maps_status_gui.py

This is the code that can build *any* GUI it knows about as defined in `maps_status_indi.py`.

Note that there is a simulation mode enabled at this time to allow software developers to 
run the code without the `indiserver` being present. This facility can be toggled on and off
but you should *not* assume that turning simulation off automatically connects the code to the
`indiserver`. It does not. It is also possible that this simulation mode behaviour will be changed
in a future release (including its removal when its utility is no longer valid).


## Personal GUIs

There is a section in `maps_status_indi.py` labelled as `Personal`. You can add a new section there that
creates *any* new GUI by picking and choosing the relevant data entries in the main dictionary. The example
provided is a data structure called `PND_STATUS_GUI`. After that is created, entries are made in the
TAB\_COLOR, TAB\_NAMES and TAB\_DATA structures to add the GUI to the main code. 
The key in each of these 3 data structures must be the same but the value can be altered as appropriate.

If you do change the `maps_status_indi.py` code, please check for data validity as detailed above.

+-------------------------------------------------------------------------------+

Last Modified: 20240421
Last Author:   Phil Daly (pndaly@arizona.edu)
