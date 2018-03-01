# lifx-lan-gui
A simple LIFX Desktop app that uses [appJar](https://github.com/jarvisteach/appJar) for the GUI and [lifxlan](https://github.com/mclarkk/lifxlan) for the underlying driver.

![image](https://user-images.githubusercontent.com/5826484/36358189-e43de388-14d7-11e8-99c8-dca0ee02d76d.png)

# Pre-Compiled Binaries

If you just want to run this app and not faff around with git and python, then go straight to the [releases](https://github.com/frakman1/lifx-lan-gui/releases) page and download the pre-compiled Mac or Windows binaries. 

# Installation Instructions
### Prerequisites

`git`, `python3` and `pip3` must already be installed.
```bash
$git clone https://github.com/frakman1/lifx-lan-gui.git
$cd lifx-lan-gui/
$pip3 install appJar
$pip3 install lifxlan
$pip3 install colour
$pip3 install configobj
$pip3 install numpy
$pip3 install opencv-python
$pip3 install scipy
```
*hint: If you get errors installing the above due to some missing dependency, then try downloading its precompiled package from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/) and pip install its .whl file. e.g.:*<br>
```bash
$pip3 install netifaces‑0.10.6‑cp36‑cp36m‑win_amd64.whl
```

# Run Instructions
```bash
$python3 lights.py
```

# Supported Platforms

Currently tested on both `Windows` and `Mac`. It should work on other platforms that appJar/tkinter supports as well but with no guarantees.


### Packaging notes:
- Windows:
`pyinstaller --add-data "*.gif;."  --icon=lifxgui.ico  --onefile -F -w lights.py`
- Mac:
`pyinstaller --add-data "*.gif:."  --icon=lifxgui.ico  --onefile -F -c lights.py`
