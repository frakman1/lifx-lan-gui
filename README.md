# lifx-lan-gui
LIFX LAN GUI Controller using [appJar](https://github.com/jarvisteach/appJar) 

![image](https://user-images.githubusercontent.com/5826484/36191726-7e19c35a-112c-11e8-824e-2029b144dc26.png)

# Pre-Compiled Binaries

If you just want to run this app and not faff around with git and python, then go straight to the [releases](https://github.com/frakman1/lifx-lan-gui/releases) page and download the pre-compiled Mac or Windows binaries. 

### Prerequisites

`git`, `python3` and `pip3` must already be installed.

# Installation Instructions
```bash
$git clone https://github.com/frakman1/lifx-lan-gui.git
$cd lifx-lan-gui/
$pip3 install appJar
$pip3 install lifxlan
$pip3 install colour
$pip3 install configobj
```
# Run Instructions
```bash
$python3 lights.py
```

# Supported Platforms

Currently tested on both `Windows` and `Mac`. It should work on other platforms that appJar/tkinter supports as well but with no guarantees.
