# lifx-lan-gui
A simple LIFX Desktop (Windows, Linux and Mac) app that uses [appJar](https://github.com/jarvisteach/appJar) for the GUI and [lifxlan](https://github.com/mclarkk/lifxlan) for the underlying driver. 


![image](https://user-images.githubusercontent.com/5826484/37431281-310a6868-27ab-11e8-85a2-6259068ed837.png)

# Pre-Compiled Binaries

If you just want to run this app and not faff around with git and python, then go straight to the [releases](https://github.com/frakman1/lifx-lan-gui/releases) page and download the pre-compiled Mac or Windows binaries. 

# Installation Instructions
### Prerequisites
This is a Python 3 project (I  use Python 3.6). Your default `python` command might already point to `python3`
. However, if you run both python 2.X and 3.X on the same machine like I do, you might have two separate commands (python for 2.x and python3 for 3.x). Similarly for `pip` and `pip3`. That is why I explicitly use `python3` and `pip3` in my instructions. Your setup may be slightly different.

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
$pip3 install pillow
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

Currently tested on `Windows 7 & 10, 64bit`, `Linux (Ubuntu 14.04.1-32bit)` and `Mac (Sierra)`. 


### Packaging notes:
- Windows:
`pyinstaller --add-data "*.gif;."  --icon=lifxgui.ico  --onefile -F -w lights.py`
- Mac:
`pyinstaller --add-data "*.gif:."  --icon=lifxgui.ico  --onefile -F -c lights.py`
