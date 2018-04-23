#!/usr/bin/env python3

import sys
if sys.version_info < (3, 3):
    sys.stdout.write("Sorry, This module requires Python 3.3 (or higher), not Python 2.x. You are using Python {0}.{1}\n".format(sys.version_info[0],sys.version_info[1]))
    sys.exit(1)
    
from appJar import gui
import os
import time
import binascii
import lifxlan
import colorsys
from colour import Color
import math
import sys
from time import sleep
from lifxlan import BLUE, CYAN, GREEN, ORANGE, PINK, PURPLE, RED, YELLOW
from configobj import ConfigObj
import pickle as pkl
from random import randint
from platform import system
from PIL import Image
import appJar as aJ
import numpy as np
import cv2
from scipy.stats import itemfreq
from mss import mss

myos = system()
if (myos == 'Windows') or (myos == 'Darwin'):
    from PIL import ImageGrab
elif (myos == 'Linux'):
    import pyscreenshot as ImageGrab

if (myos == 'Windows'):
    mygreen = 'lime'
elif (myos == 'Darwin') or (myos == 'Linux') :
    mygreen = 'green'

def resource_path(relative_path):
    if (myos == 'Windows'):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = os.path.abspath(".")
        except Exception:
            base_path = sys._MEIPASS
        
        return os.path.join(base_path, relative_path)

    elif (myos == 'Darwin') or (myos == 'Linux') :
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path =  os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

DECIMATE = 1   # skip every DECIMATE number of pixels to speed up calculation
TRANSIENT_TIP = "If selected, return to the original color after the specified number of cycles. If not selected, set light to specified color"
PERIOD_TIP = "Period is the length of one cycle in milliseconds"
CYCLES_TIP = "Cycles is the number of times to repeat the waveform"
DUTY_CYCLE_TIP = "Duty Cycle is an integer between -32768 and 32767. Its effect is most obvious with the Pulse waveform. Set Duty Cycle to 0 to spend an equal amount of time on the original color and the new color. Set Duty Cycle to positive to spend more time on the original color. Set Duty Cycle to negative to spend more time on the new color"
EXPECTED_TIP = "Select 0 to find all available bulbs. Select any number to look for exactly that number of bulbs"
TRANSITION_TIME_TIP = "The time (in ms) that a color transition takes"
FOLLOW_DESKTOP_TIP = "Make your bulbs' color match your desktop"
DESKTOP_MODE_TIP = "Select between following the whole desktop screen or just a small portion of it (useful for letterbox movies)"
HUE_DELTA_TIP = "The amount the hue will change every interval (between 0 and 65535)"
CYCLE_INTERVAL_TIP = "The time (in ms) between each update"
CYCLE_SATURATION_TIP = "How saturated you want the hue to be (between 0 and 65535)"
EXPECTED_BULBS = 0
TRANSITION_TIME_DEFAULT = 400
CONFIG = resource_path("lights.ini")
PICKLE = resource_path("lifxList.pkl")
SCENE1_C = resource_path("scene1_c.pkl")
SCENE1_P = resource_path("scene1_p.pkl")
SCENE2_C = resource_path("scene2_c.pkl")
SCENE2_P = resource_path("scene2_p.pkl")
SCENE3_C = resource_path("scene3_c.pkl")
SCENE3_P = resource_path("scene3_p.pkl")
CYCLES = "Cycles"
TRANSITION_TIME = "Transition Time(ms)"
FOLLOW_DESKTOP = "Start Following Desktop"
DESKTOP_MODE = "Desktop Mode"
REGION_COLOR = "regioncolor"
MAX_SATURATION = "Max Saturation"
MAX_BRIGHTNESS = "Max Brightness"
COLOR_CYCLE = "Color Cycle"
CYCLE_INTERVAL = "Update Interval(ms)" #update interval
SCALE = "Scale"
CYCLE_INTERVAL_SCALE = CYCLE_INTERVAL + SCALE
HUE_DELTA = "Hue Delta"
HUE_DELTA_SCALE = HUE_DELTA + SCALE
TRANSITION_TIME2 = "Transition Time (ms)"
TRANSITION_TIME2_SCALE = TRANSITION_TIME2 + SCALE
START_COLOR_CYCLE = "Start Color Cycle"
CYCLE_COLOR = "CycleColor"


CYCLE_HUE_DELTA = 600
CYCLE_INTERVAL_MS = 2000

original_colors = {}
config = {}
bulbs = []
selected_bulb = 0
details = str(0)
gSelectAll = False
lan = 0
gExpectedBulbs = EXPECTED_BULBS
lifxList = []
lifxDict = {}
gwaveformcolor = "#FF0000"
is_follow = False
test_string = """

"""
original_colors1 = {}
original_powers1 = {}
original_colors2 = {}
original_powers2 = {}
original_colors3 = {}
original_powers3 = {}
r = None
selectedMode = "Whole Screen"
maxSaturation = False
maxBrightness = False
is_cycle = False
gCycleHue = 0
gCycleInterval = CYCLE_INTERVAL_MS
gCycleDelta = CYCLE_HUE_DELTA
gTransitionTime = TRANSITION_TIME_DEFAULT
gCycleSaturation = 65535
gCycleBrightness = 65535
gCycleKelvin = 3500

class App(aJ.gui):
    def __init__(self, *args, **kwargs):
        aJ.gui.__init__(self, *args, **kwargs)

    def winfo_screenheight(self):
        #   shortcut to height
        #   alternatively return self.topLevel.winfo_screenheight() since topLevel is Tk (root) instance!
        return self.appWindow.winfo_screenheight()

    def winfo_screenwidth(self):
        #   shortcut to width
        #   alternatively return self.topLevel.winfo_screenwidth() since topLevel is Tk (root) instance!
        return self.appWindow.winfo_screenwidth()



def SceneNameChanged(name):
    #print(name, "Entry changed")
    config[name] = app.getEntry(name)
    config.write()



def Scene(name):
    global original_colors1
    global original_powers1
    global original_colors2
    global original_powers2
    global original_colors3
    global original_powers3
    global lan
    global config

    print(name, "button pressed")
    if len(bulbs) < 1:
        app.errorBox("Error", "Error. No bulbs were found yet. Please click the 'Find Bulbs' button and try again.")
        return
    try:

        if name == 'Save Scene 1':
            print("Saving Scene 1")
            original_colors1 = lan.get_color_all_lights()
            original_powers1 = lan.get_power_all_lights()
            #print("colors:",original_colors)
            #print(type(original_colors1))
            pkl.dump(original_colors1, open(SCENE1_C, "wb" ))
            pkl.dump(original_powers1, open(SCENE1_P, "wb" ))


        elif name == 'Restore Scene 1':
            print("Restoring Scene 1")
            if (os.path.exists(SCENE1_C) and os.path.exists(SCENE1_P) ):
                original_colors1 = pkl.load(open(SCENE1_C, "rb"))
                original_powers1 = pkl.load(open(SCENE1_P, "rb"))

            if ( (len(original_colors1) == 0) or (len(original_powers1) == 0) ):
                print("Nothing saved yet.")
                return

            print("Restoring original color to all lights...")
            #print("colors:",original_colors)
            for light in original_colors1:
                light.set_color(original_colors1[light])

            sleep(1)

            print("Restoring original power to all lights...")
            for light in original_powers1:
                light.set_power(original_powers1[light])
        elif name == 'Save Scene 2':
            print("Saving Scene 2")
            original_colors2 = lan.get_color_all_lights()
            original_powers2 = lan.get_power_all_lights()
            #print("colors:",original_colors)
            pkl.dump(original_colors2, open(SCENE2_C, "wb" ))
            pkl.dump(original_powers2, open(SCENE2_P, "wb" ))


        elif name == 'Restore Scene 2':
            print("Restoring Scene 2")
            if (os.path.exists(SCENE2_C) and os.path.exists(SCENE2_P) ):
                original_colors2 = pkl.load(open(SCENE2_C, "rb"))
                original_powers2 = pkl.load(open(SCENE2_P, "rb"))

            if ( (len(original_colors2) == 0) or (len(original_powers2) == 0) ):
                print("Nothing saved yet.")
                return

            print("Restoring original color to all lights...")
            #print("colors:",original_colors)
            for light in original_colors2:
                light.set_color(original_colors2[light])

            sleep(1)

            print("Restoring original power to all lights...")
            for light in original_powers2:
                light.set_power(original_powers2[light])
        elif name == 'Save Scene 3':
            print("Saving Scene 3")
            original_colors3 = lan.get_color_all_lights()
            original_powers3 = lan.get_power_all_lights()
            #print("colors:",original_colors)
            pkl.dump(original_colors3, open(SCENE3_C, "wb" ))
            pkl.dump(original_powers3, open(SCENE3_P, "wb" ))

        elif name == 'Restore Scene 3':
            print("Restoring Scene 3")
            if (os.path.exists(SCENE3_C) and os.path.exists(SCENE3_P) ):
                original_colors3 = pkl.load(open(SCENE3_C, "rb"))
                original_powers3 = pkl.load(open(SCENE3_P, "rb"))

            if ( (len(original_colors3) == 0) or (len(original_powers3) == 0) ):
                print("Nothing saved yet.")
                return

            print("Restoring original color to all lights...")
            #print("colors:",original_colors)
            for light in original_colors3:
                light.set_color(original_colors3[light])

            sleep(1)

            print("Restoring original power to all lights...")
            for light in original_powers3:
                light.set_power(original_powers3[light])
    except Exception as e:
        print ("Ignoring error: ", str(e))
        app.errorBox("Error", str(e) + "\n\n Scene Operation failed. This feature is buggy and only works about 50% of the time. Sometimes, you can still save and restore a scene despite this error. If you keep getting this error and can not perform a 'Restore', try restarting the app then try again.")
        return



def updateSliders(hsbk):
    #print("h:",hsbk[0])
    #print("s:",hsbk[1])
    #print("b:",hsbk[2])
    #print("k:",hsbk[3])
    global gCycleHue
    global gCycleSaturation 
    global gCycleBrightness
    global gCycleKelvin

    app.setSpinBox("hueSpin", int(hsbk[0]), callFunction=False)
    app.setSpinBox("satSpin", int(hsbk[1]), callFunction=False)
    app.setSpinBox("briSpin", int(hsbk[2]), callFunction=False)
    app.setSpinBox("kelSpin", int(hsbk[3]), callFunction=False)
    app.setScale("hueScale", int(hsbk[0]), callFunction=False)
    app.setScale("satScale", int(hsbk[1]), callFunction=False)
    app.setScale("briScale", int(hsbk[2]), callFunction=False)
    app.setScale("kelScale", int(hsbk[3]), callFunction=False)
    
    rgb1 = hsv_to_rgb((hsbk[0]/65535), (hsbk[1]/65535), (hsbk[2]/65535));#print("rgb1:",rgb1)
    c = Color(rgb=(rgb1[0], rgb1[1], rgb1[2]))
    #print("c:",c)
    app.setLabelBg("bulbcolor", c.hex_l)
    gCycleHue = hsbk[0]
    gCycleSaturation = hsbk[1]
    gCycleBrightness = hsbk[2]
    gCycleKelvin = hsbk[3]

def RGBtoHSBK (RGB, temperature = 3500):
    cmax = max(RGB)
    cmin = min(RGB)
    cdel = cmax - cmin

    brightness = int((cmax/255) * 65535)

    if cdel != 0:
        saturation = int(((cdel) / cmax) * 65535)

        redc = (cmax - RGB[0]) / (cdel)
        greenc = (cmax - RGB[1]) / (cdel)
        bluec = (cmax - RGB[2]) / (cdel)

        if RGB[0] == cmax:
            hue = bluec - greenc
        else:
            if RGB[1] == cmax:
                hue = 2 + redc - bluec
            else:
                hue = 4 + greenc - redc

        hue = hue / 6
        if hue < 0:
            hue = hue + 1

        hue = int(hue*65535)
    else:
        saturation = 0
        hue = 0

    return (hue, saturation, brightness, temperature)



# function to convert the scale values to an RGB hex code
def getHSBK():

    global gCycleHue 
    global gCycleSaturation
    global gCycleBrightness
    global gCycleKelvin
    
    H = app.getScale("hueScale")
    S = app.getScale("satScale")
    B = app.getScale("briScale")
    K = app.getScale("kelScale")
    
    gCycleHue = int(H)
    gCycleSaturation = int(S)
    gCycleBrightness = int(B)
    gCycleKelvin = int(K)

    #RGB = "#"+str(R)+str(G)+str(B)

    return {'H':H, 'S':S,'B':B, 'K':K }


# funciton to update widgets
def updateHSB(name):
    # this stops the changes in slider/spin from constantly calling each other
    #print ("name:",name)


    # split the widget's name into the type & colour
    colour = name[0:3]
    widg = name[3:]

    # get the current RGB value
    HSBK = getHSBK()
    #print("HSB:",HSB,"type(HSB)",type(HSB))
    #print("H",HSB["H"])
    #print("S",HSB["S"])
    #print("B",HSB["B"])

    # depending on the type, get & set...
    if widg == "Scale":
        value = app.getScale(name)
        app.setSpinBox(colour + "Spin", value, callFunction = False)
    elif widg == "Spin":
        value = app.getSpinBox(name)
        app.setScale(colour + "Scale", value, callFunction = False)

    # update the label
    h = HSBK["H"] / 65535.0;#print("h:",h)
    s = HSBK["S"] / 65535.0;#print("s:",s)
    v = HSBK["B"] / 65535.0;#print("v:",v)
    k = HSBK["K"];#print("v:",v)

    rgb1 = hsv_to_rgb(h, s, v);#print("rgb1:",rgb1)
    c = Color(rgb=(rgb1[0], rgb1[1], rgb1[2]))
    #print("c:",c)
    app.setLabelBg("bulbcolor", c.hex_l)

    global selected_bulb
    bulbHSBK = [HSBK["H"],HSBK["S"],HSBK["B"],HSBK["K"]]
    #print ("bulbHSBK:",bulbHSBK)
    app.thread(updateBulbs, bulbHSBK )

    #app.setEntry("colCode", RGB)

def updateBulbs(bulbHSBK):
    try:
        
        if gSelectAll:
            lan.set_color_all_lights(bulbHSBK, duration=0, rapid=False)

        elif selected_bulb:
            #print("sending color",hsv)
            selected_bulb.set_color(bulbHSBK, duration=0, rapid=False)
    
    except Exception as e:
        print ("Ignoring error: ", str(e))
    

def selectAllPressed (name):
    global bulbs
    if len(bulbs) < 1:
        app.errorBox("Error", "Error. No bulbs were found yet. Please click the 'Find Bulbs' button and try again.")
        app.setCheckBox("Select All", ticked=False, callFunction=False)
        return

    global gSelectAll
    gSelectAll = app.getCheckBox("Select All")
    #print("gSelectAll:",gSelectAll)

def expectedPressed (name):
    global gExpectedBulbs
    global config
    gExpectedBulbs = int(app.getSpinBox("Expected Bulbs"))
    config['expectedbulbs'] = gExpectedBulbs
    config.write()
    print("gExpectedBulbs:",gExpectedBulbs)


def rgb_to_hsv(r, g, b):
    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, v = high, high, high

    d = high - low
    s = 0 if high == 0 else d / high

    if high == low:
        h = 0.0
    else:
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s, v


def hsv_to_rgb(h, s, v):
    i = math.floor(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)

    r, g, b = [
        (v, t, p),
        (q, v, p),
        (p, v, t),
        (p, q, v),
        (t, p, v),
        (v, p, q),
    ][int(i % 6)]

    return r, g, b

def modeChanged():
    global selectedMode
    selectedMode = (app.getOptionBox("Desktop Mode"))#;print("selectedMode: ",selectedMode)

def listChanged():
    app.clearTextArea("Result");  # TODO. Put this in another thread
    app.setTextArea("Result", "Loading bulb details")  # TODO. Put this in another thread
    selected = (app.getOptionBox("LIFX Bulbs"))#;print("selected: ",selected)
    global bulbs
    global selected_bulb
    global details
    try:
        for bulb in bulbs:
            if (bulb.label == selected):
                #print("Found selected bulb")
                selected_bulb = bulb
                details = str(selected_bulb)
                #print("type(bulb)",type(bulb))
                #print(bulb)
                #print("breaking")
                break
    except Exception as e:
        print ("Ignoring error: ", str(e))
        app.errorBox("Error", str(e))
        app.clearTextArea("Result");
        app.setTextArea("Result", str(e))

        return


    app.clearTextArea("Result")
    app.setTextArea("Result", details)

    try:
        if "Power: On" in details:
            #print ("BULB is ON")
            app.setButtonImage("Light", resource_path("bulb_on.gif"))
        elif "Power: Off" in details:
            #print ("BULB is OFF ")
            app.setButtonImage("Light", resource_path("bulb_off.gif"))
    except Exception as e:
        print ("Ignoring error:", str(e))

    app.setButton ( "Light", "Toggle " + selected )
    app.showButton("Light")
    color = bulb.get_color();#print(color[0],color[1],color[2]);
    h = color[0] / 65535.0;#print("h:",h)
    s = color[1] / 65535.0;#print("s:",s)
    v = color[2] / 65535.0;#print("v:",v)

    rgb1 = hsv_to_rgb(h, s, v);#print("rgb1:",rgb1)
    c = Color(rgb=(rgb1[0], rgb1[1], rgb1[2]))
    #print("c:",c)
    app.setLabelBg("bulbcolor", c.hex_l)
    updateSliders(color)


def finder():
    global bulbList
    global lan
    global gExpectedBulbs
    global config
    global lifxList
    global lifxDict
    global config
    bulbList.clear()
    bulbList.append("-Select Bulb-")
    try:
        global bulbs
        #print("finder().gExpectedBulbs:",gExpectedBulbs)
        lan = lifxlan.LifxLAN(int(gExpectedBulbs) if int(gExpectedBulbs) != 0 else None)
        bulbs = lan.get_lights()
        #print(type(bulbs))
        #print(bulbs[0].label)
        if len(bulbs) < 1:
            app.errorBox("Error", "No bulbs found. Please try again. If you switched WiFi networks, please re-start the app and try again.")
            app.setLabelBg("lbl2", "red")
            app.setLabel("lbl2", "Found 0 bulbs")
            return
        else:
            app.setLabelBg("lbl2", mygreen)
            app.hideLabel("f1")

        app.setLabel("lbl2", "Found " + str(len(bulbs)) + " bulbs")
        app.setCheckBox("Select All")
        #app.setSpinBox("Expected Bulbs", str(len(bulbs)))
        del lifxList[:]
        for bulb in bulbs:
            #print(".get_label()",bulb.get_label()) # this gets the actual label
            #print(".label:",bulb.label) # this returns None
            label = bulb.get_label()
            ip = bulb.ip_addr
            mac = bulb.mac_addr
            #print (label,ip,mac)
            lifxDict['label'] = label
            lifxDict['mac'] = mac
            lifxDict['ip'] = ip
            lifxList.append(lifxDict.copy())
            bulbList.append(label)
        app.changeOptionBox("LIFX Bulbs", bulbList, callFunction=False)
        app.showButton ( "Pick Color" )
        #print(lifxList)
        #config['bulbs'] = lifxList
        pkl.dump(lifxList, open(PICKLE, "wb" ))   #this pickles
#exit(0)
        #config.write()


    except Exception as e:
        print ("Ignoring error:", str(e))
        app.setLabelBg("lbl2", "gray")
        app.setLabel("lbl2", "Found 0 bulbs")
        app.errorBox("Error", str(e) + "\n\nPlease try again. If you keep getting this error, check/toggle your WiFi, ensure that 'Expected Bulbs' is either 0 or the number of bulbs you have and finally, try restarting the app")

#    config['bulbs'] = bulbs
#    config.write()
    print ("finder() Ended")

def press(name):
    global bulbs
    global details
    global gSelectAll
    global lan
    global gwaveformcolor
    global selected_bulb
    global gCycleHue
    global gCycleBrightness
    global gCycleSaturation
    

    #print(name, "button pressed")

    if (name == "Find Bulbs"):
        finder()
    elif (name == "All Off"):
        if len(bulbs) < 1:
            return
        lan.set_power_all_lights(False, rapid=True)
    elif (name == "All Random"):
        if len(bulbs) < 1:
            return
        selected = (app.getOptionBox("LIFX Bulbs"))
        for bulb in bulbs:
            hue = (randint(0, 65535))
            sat = (randint(40000, 65535))
            bulb.set_color([hue, sat, 65535, 3500], duration=0, rapid=True)
            if (bulb.label == selected):
                h = hue / 65535.0;#print("h:",h)
                s = sat / 65535.0;#print("s:",s)
                v = 1;#print("v:",v)
                rgb1 = hsv_to_rgb(h, s, v);#print("rgb1:",rgb1)
                c = Color(rgb=(rgb1[0], rgb1[1], rgb1[2]))
                app.setLabelBg("bulbcolor", c.hex_l)
                updateSliders([hue,sat,65535,3500])

    elif (name == "All On"):
        if len(bulbs) < 1:
            return
        lan.set_power_all_lights(True, rapid=True)
    elif (name == "All White"):
        if len(bulbs) < 1:
            return
        lan.set_color_all_lights([0,0,65535,3500], duration=0, rapid=True)
        updateSliders([0,0,65535,3500])
        app.setLabelBg("bulbcolor", "#FFFFFF")

    elif (name == "Execute"):
        waveform = app.getRadioButton("waveform")
        config['waveform'] = waveform
        if waveform == "Saw":
            waveform = 0
        elif waveform == "Sine":
            waveform = 1
        elif waveform == "HalfSine":
            waveform = 2
        elif waveform == "Triangle":
            waveform = 3
        elif waveform == "Pulse (Strobe)":
            waveform = 4
        #print ("waveform:",waveform)
        is_transient = app.getCheckBox("Transient")
        config['transient'] = is_transient
        
        if (is_transient):
            is_transient = 1
        else:
            is_transient = 0

        #print("is_transient:",is_transient)
        #pickedColor = app.getLabelBg("lblwaveformcolor")
        #print("gwaveformcolor:",gwaveformcolor)
        config['secondary_color'] = gwaveformcolor
        c = Color(str(gwaveformcolor))
        hsv = rgb_to_hsv(c.red, c.green, c.blue)
        #print("hsv:",hsv)
        bulbHSBK = [hsv[0] * 65535.0,hsv[1] * 65535.0,hsv[2] * 65535.0,3500]
        #print (bulbHSBK)
        period = app.getEntry("Period(ms)")
        cycles = app.getEntry(CYCLES)
        duty_cycle = app.getEntry("Duty Cycle")
        config['period'] = period
        config['cycles'] = cycles
        config['duty_cycle'] = duty_cycle
        config.write()
        
        #print("period:",period)
        #print("cycles:",cycles)
        #print("duty_cycle:",duty_cycle)

        if gSelectAll:
            lan.set_waveform_all_lights(is_transient, bulbHSBK, period, cycles, duty_cycle, waveform, [1])

        elif selected_bulb:
            #print("sending color",hsv)
            selected_bulb.set_waveform(is_transient, bulbHSBK, period, cycles, duty_cycle, waveform)
        else:
            app.errorBox("Error", "Error. No bulb was selected. Please select a bulb from the pull-down menu (or tick the 'Select All' checkbox) and try again.")
            return

    elif (name == "Secondary Color"):
        pickedColor = app.colourBox(colour="#FF0000")
        app.setLabelBg("lblwaveformcolor", pickedColor)
        gwaveformcolor = pickedColor
    elif (name == "Pick Color"):
        pickedColor = app.colourBox(colour="#FFFFFF")
        app.setLabelBg("bulbcolor", pickedColor)
        #print("pickedColor:",pickedColor)
        if pickedColor == None:
            return
        c = Color(str(pickedColor))
        hsv = rgb_to_hsv(c.red, c.green, c.blue)
        #print("hsv:",hsv)
        bulbHSBK = [hsv[0] * 65535.0,hsv[1] * 65535.0,hsv[2] * 65535.0,3500]
        gCycleHue = bulbHSBK[0]
        gCycleSaturation = bulbHSBK[1]
        gCycleBrightness = bulbHSBK[2]
        
        #print ("bulbHSBK:",bulbHSBK)
        updateBulbs(bulbHSBK)
        if gSelectAll:
            lan.set_color_all_lights(bulbHSBK, duration=0, rapid=False)
        elif selected_bulb:
            #print("sending color",hsv)
            selected_bulb.set_color(bulbHSBK, duration=0, rapid=False)
        else:
            app.errorBox("Error", "Error. No bulb was selected. Please select a bulb from the pull-down menu (or tick the 'Select All' checkbox) and try again.")
            return

        updateSliders(bulbHSBK)


    elif (name == "Light"):
        #print("selected: ",selected_bulb.label)
        #print("Power is Currently: {}".format(selected_bulb.power_level))
        try:
            onOff = selected_bulb.power_level;
        except Exception as e:
            print ("Ignoring error:", str(e))
            app.errorBox("Error", str(e) + "\n\nTry selecting a bulb from the list first.")
            return

        #selected_bulb.set_power(not selected_bulb.get_power(), duration=0, rapid=True)

        if "Power: Off" in details:
            selected_bulb.set_power(65535, duration=0, rapid=False)
            try:
                app.setButtonImage("Light", resource_path("bulb_on.gif"));#print("PowerOn");
            except Exception as e:
                print ("Ignoring error:", str(e))
            details = details.replace("Power: Off", "Power: On");
            app.clearTextArea("Result")
            app.setTextArea("Result", details)

        else:
            selected_bulb.set_power(0, duration=0, rapid=False)
            try:
                app.setButtonImage("Light", resource_path("bulb_off.gif"));#print("PowerOff");
            except Exception as e:
                print ("Ignoring error:", str(e))
            details = details.replace("Power: On", "Power: Off"); #print("details:\n",details)
            app.clearTextArea("Result")
            app.setTextArea("Result", details)

        app.setButton ( "Light", "Toggle " + (app.getOptionBox("LIFX Bulbs")) )
        app.showButton("Light")


        #listChanged()

def rainbow_press(name):
    global gExpectedBulbs
    global bulbs
    global lan
    #print ("len(bulbs):",len(bulbs))    
    try:
        print("Discovering lights...")
        lan = lifxlan.LifxLAN(int(gExpectedBulbs) if int(gExpectedBulbs) != 0 else None)
        if lan is None:
            print("Error finding bulbs")
            return
        bulbs = lan.get_lights()
        if len(bulbs) < 1:
            print("No bulbs found. Exiting.")
            return
        
        #print("lan:",lan,"type(lan):",type(lan))
        original_colors = lan.get_color_all_lights()
        original_powers = lan.get_power_all_lights()

        print("Turning on all lights...")
        lan.set_power_all_lights(True)
        sleep(1)

        print("Flashy fast rainbow")
        rainbow(lan, 0.4)

        #print("Smooth slow rainbow")
        #rainbow(lan, 1, smooth=True)
        print("Restoring original color to all lights...")
        for light in original_colors:
            light.set_color(original_colors[light])

        sleep(1)

        print("Restoring original power to all lights...")
        for light in original_powers:
            light.set_power(original_powers[light])
    except Exception as e:
        print ("Ignoring error:", str(e))

def rainbow(lan, duration_secs=0.5, smooth=False):
    colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
    transition_time_ms = duration_secs * 1000 if smooth else 500
    rapid = True if duration_secs < 1 else False
    for i in range(0, 3):
        for color in colors:
            lan.set_color_all_lights(color, transition_time_ms, rapid)
            sleep(duration_secs)

def maxPressed(name):
    global maxSaturation
    global maxBrightness
    
    if (name == MAX_SATURATION):
        maxSaturation = app.getCheckBox(MAX_SATURATION)
        print(name, " is ", maxSaturation)
        config['maxSaturation'] = maxSaturation
    elif (name == MAX_BRIGHTNESS):
        maxBrightness = app.getCheckBox(MAX_BRIGHTNESS)
        print(name, " is ", maxBrightness)
        config['maxBrightness']=maxBrightness
    
    config.write()
        
        
def followDesktop():
    global gSelectAll
    global lan
    global is_follow
    global selected_bulb
    global r
    global maxSaturation
    global maxBrightness
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    print("screen_width:", screen_width, " screen_height:", screen_height)
    print("Follow:", is_follow)
    duration = app.getEntry(TRANSITION_TIME)
    is_evening = app.getCheckBox("Evening Mode")
    config['transtime'] = duration
    config['is_evening'] = is_evening
    config.write()

    print("r:", r)
    print("Starting Loop")

    left = r[0]      # The x-offset of where your crop box starts
    top = r[1]    # The y-offset of where your crop box starts
    width = r[2]   # The width  of crop box
    height = r[3]    # The height of crop box
    box = (left, top, left + width, top + height)

    if (is_follow):
        app.hideEntry(TRANSITION_TIME)
        app.hideOptionBox(DESKTOP_MODE)
        app.showLabel(REGION_COLOR)
        app.hideCheckBox("Evening Mode")

    sct = mss()
    while (is_follow):
        start = time.time()
        try:
            # fast screenshot with mss module
            sct_img = sct.grab(box)
            image = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        except Exception as e:
            print ("Ignoring error:", str(e))

        try:
            # downsample to 1/10th and calculate average RGB color
            pixels = np.array(image, dtype=np.float32)
            pixels = pixels[::10,::10,:]
            pixels = np.transpose(pixels)
            dominant_color = [np.mean(channel) for channel in pixels]
            c = Color(rgb=(dominant_color[0]/255, dominant_color[1]/255, dominant_color[2]/255))
            app.setLabelBg(REGION_COLOR, c.hex_l)
            # get HSVK color from RGB color
            # during evenings, kelvin is 3500 (default value returned above)
            # during the daytime, saturated colors are still 3500 K,
            # but the whiter the color, the cooler, up to 5000 K
            (h, s, v, k) = RGBtoHSBK(dominant_color)
            if not is_evening:
                k = int(5000 - (s/65535 * 1500))
            if (maxSaturation) and (s > 6553):
                s = 65535
            if (maxBrightness) and (True):
                v = 65535
            bulbHSBK = [h, s, v, k]
            try:
                if gSelectAll:
                    lan.set_color_all_lights(bulbHSBK, duration=duration, rapid=True)
                elif selected_bulb:
                    selected_bulb.set_color(bulbHSBK, duration=duration, rapid=True)
                else:
                    app.errorBox("Error", "Error. No bulb was selected. Please select a bulb from the pull-down menu (or tick the 'Select All' checkbox) and try again.")
                    app.setCheckBox("FOLLOW_DESKTOP", False)
                    is_follow = False
                    return
            except Exception as e:
                print ("Ignoring error: ", str(e))
        except Exception as e:
            print("Ignoring error: ", str(e))

        # rate limit to prevent from spamming bulbs
        # the theoretical max speed that the bulbs can handle is one packet
        # every 0.05 seconds, but empirically I found that 0.1 sec looked better
        max_speed_sec = 0.1
        elapsed_time = time.time() - start
        wait_time = max_speed_sec - elapsed_time
        if wait_time > 0:
            sleep(wait_time)
        #print(elapsed_time, time.time()-start)
    print("Exiting loop")


def followDesktopPressed(name):
    global is_follow
    global r
    global selectedMode
    is_follow = app.getCheckBox(FOLLOW_DESKTOP)
    app.showEntry(TRANSITION_TIME)
    app.showOptionBox(DESKTOP_MODE)
    app.showCheckBox("Evening Mode")
    app.hideLabel(REGION_COLOR)

    if (is_follow):
        print("Pressed:", name, " Follow:", is_follow)
        if (selectedMode == "Whole Screen"):
            print("Doing Whole Screen processing")
            screen_width = app.winfo_screenwidth()
            screen_height = app.winfo_screenheight()
            r = (0, 0, screen_width, screen_height)
        else:
            print("Doing Partial Screen processing")

            app.setTransparency(0)
            app.infoBox("Select Region", "A new window entitled \"Screenshot\" will pop up. Drag a rectangle around the region of interest and press ENTER . This region's dominant color will be sent to the bulbs to match. To Cancel, press c .", parent=None)
            myos = system()
            image = ImageGrab.grab()
            if (myos == 'Linux') or (myos == 'Darwin'):
                print("Mac OS detected.")
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            elif (myos == 'Windows'):
                print("Windows OS detected.")
                open_cv_image = np.array(image)

            # Convert RGB to BGR
            im = open_cv_image[:,:,::-1].copy()

            if (myos == 'Linux') or (myos == 'Darwin'):
                screen_width = app.winfo_screenwidth()
                screen_height = app.winfo_screenheight()
                im = cv2.resize(im, (int(screen_width * 0.9), int(screen_height * 0.9)))
                cv2.namedWindow("Screenshot", cv2.WINDOW_AUTOSIZE)
                cv2.moveWindow("Screenshot", 0, 0)
                cv2.imshow("Screenshot", im)
            elif (myos == 'Windows'):
                cv2.namedWindow("Screenshot", cv2.WINDOW_NORMAL)

            r = cv2.selectROI("Screenshot", im, False)
            #cv2.waitKey()
            print ("r type:", type(r))
            print("r is", r)
            if not any(r):
                print("No region selected. Exiting")
                cv2.destroyAllWindows()
                app.setCheckBox(FOLLOW_DESKTOP, False)
                is_follow = False
                app.setTransparency(1)
                return
            #cv2.waitKey(0)
            cv2.destroyAllWindows()
            app.setTransparency(1)

        app.thread(followDesktop)

# This function gets run continuously every 2 seconds until activated, then it runs more frequently as set by user.

def ColorCycle():
    global is_cycle
    global gCycleHue
    global gCycleDelta
    global gSelectAll
    global selected_bulb
    global lan
    global gTransitionTime
    global gCycleSaturation
    global gCycleBrightness
    global gCycleKelvin
    global original_colors

    
    #print("is_cycle:", is_cycle, " gCycleInterval:", gCycleInterval, "gCycleDelta:", gCycleDelta, "gCycleHue:", gCycleHue, "originalColors:", original_colors)
    if is_cycle:

        #rgb1 = hsv_to_rgb(gCycleHue/65535, gCycleSaturation/65535, gCycleBrightness/65535);#print("rgb1:",rgb1)
        #c = Color(rgb=(rgb1[0], rgb1[1], rgb1[2]))
        
        
        try:
            if gSelectAll:
                #lan.set_color_all_lights(bulbHSBK,gTransitionTime, rapid=True)
                #print("------------------------------------------------")
                for light in original_colors:
                    newHue = (int(original_colors[light][0]) + int(gCycleDelta)) % 65535
                    #print("newHue:",newHue)
                    original_colors[light] = (newHue, original_colors[light][1], original_colors[light][2], original_colors[light][3])
                    bulbHSBK = [newHue, original_colors[light][1], original_colors[light][2], original_colors[light][3]]
                    #print (bulbHSBK)
                    light.set_color(bulbHSBK, gTransitionTime, rapid=True)
                    #print("------------------------------------------------")
                    
                
            elif selected_bulb:
                gCycleHue = (int(gCycleHue) + int(gCycleDelta)) % 65535
                bulbHSBK = [gCycleHue, gCycleSaturation, gCycleBrightness, gCycleKelvin]
                selected_bulb.set_color(bulbHSBK, gTransitionTime, rapid=True)
                updateSliders([gCycleHue, gCycleSaturation, gCycleBrightness, gCycleKelvin])
                #app.setLabelBg(CYCLE_COLOR, c.hex_l)
                
                
            else:
                app.errorBox("Error", "Error. No bulb was selected. Please select a bulb from the pull-down menu (or tick the 'Select All' checkbox) and try again.")
                app.setCheckBox(START_COLOR_CYCLE, False)
                is_follow = False
                return
        except Exception as e:
            print ("Ignoring error: ", str(e))

        #Update the GUI the appJar way
        #app.queueFunction(app.setLabelBg, CYCLE_COLOR, c.hex_l)
        #app.setLabelBg(CYCLE_COLOR, c.hex_l)
        
    else:
        app.setPollTime(CYCLE_INTERVAL_MS)
        

        
def ColorCyclePressed(name):
    
    global is_cycle
    global gCycleDelta
    global gCycleInterval
    global gTransitionTime
    global original_colors
    global lan
    
    #print("-------------------------\n",function_name(), "() name: ", name)
    
    if name==START_COLOR_CYCLE:
        is_cycle = app.getCheckBox(START_COLOR_CYCLE)
        original_colors = lan.get_color_all_lights()
        app.setPollTime(gCycleInterval)
        #for light in original_colors:
        #    original_colors[light] = original_colors[light] + (original_colors[light][0],)
            
        return
    

    #global gCycleSaturation
    is_scale = (name[-5:]=="Scale")
    #print("is_scale: ",is_scale)
    
    
    try:
        # depending on the type, get & set...
        if is_scale:
            value = app.getScale(name)
            #print("scale value:", value)
            app.setEntry(name[:-5], value, callFunction = False)
        else:
            value = app.getEntry(name)
            #print("entry value:", value)
            app.setScale(name + SCALE, value, callFunction = False)
            
        is_cycle = app.getCheckBox(START_COLOR_CYCLE)
        gCycleInterval = int(app.getEntry(CYCLE_INTERVAL))
        app.setPollTime(gCycleInterval)
        gCycleDelta = int(app.getEntry(HUE_DELTA))
        gTransitionTime = app.getEntry(TRANSITION_TIME2)
        #gCycleSaturation = int(app.getEntry(CYCLE_SATURATION))%65536
        #print( "type: ", type(original_colors))
    except Exception as e:
        print ("Ignoring error: ", str(e))
    
    #print("ColorCyclePressed()")

def function_name():
    return sys._getframe().f_back.f_code.co_name    
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------    
bulbList = ["-None-          "]

app = App("LIFX Controller")
#app = gui("LIFX Controller")
app.setStretch("both")
app.setResizable(True)
#app.setFont(12)
app.setFont(size=12, family="Arial")


app.setSticky("new")
app.setStretch("COLUMN")

app.startLabelFrame("", 0, 0)
app.setSticky("new")
app.startLabelFrame("Find", 0, 0)
app.setSticky("new")
app.setPadding(1)
app.addFlashLabel("f1", "Start here --->", 0, 0)
app.addButton("Find Bulbs", press, 0, 1)
expected_range = list(range(1, 20))
app.addLabelSpinBox ( "Expected Bulbs", list(reversed(range(20))), 0, 2 )
app.setSpinBox("Expected Bulbs", EXPECTED_BULBS)
gExpecteBulbs = app.getSpinBox("Expected Bulbs")
app.setSpinBoxChangeFunction("Expected Bulbs", expectedPressed)
app.setSpinBoxWidth("Expected Bulbs", 2)

app.setSpinBoxTooltip("Expected Bulbs", EXPECTED_TIP)
app.setLabelTooltip("Expected Bulbs", EXPECTED_TIP)

app.addLabel("lbl2", " ", 1, 0)
app.setLabelBg("lbl2", "white")
app.addNamedCheckBox("Select All Bulbs", "Select All", 1, 2)
app.setCheckBoxChangeFunction("Select All", selectAllPressed)

app.addOptionBox("LIFX Bulbs", bulbList, 1, 1)
app.setOptionBoxChangeFunction("LIFX Bulbs", listChanged)
app.setSticky("n")
try:
    app.addImageButton("Light", press, resource_path("bulb_off.gif"), 2, 2)
except Exception as e:
    print ("Ignoring error:", str(e))
    #app.errorBox("Error", str(e)+"\n\nTry selecting a bulb from the list first.")
    #return
app.setButton( "Light", "Toggle Selected" )
#app.setButtonHeight ( "Light", 40 )

#app.hideButton("Light")

app.stopLabelFrame() #Find

#app.setButtonImage("picker", resource_path("colorpicker.gif"), align=None)
###
app.setSticky("ne")
app.startLabelFrame("All LAN Bulbs", 0, 1)
app.setSticky("new")
app.addButton("All Off", press, 2, 2)
app.addButton("All On", press, 3, 2)
app.addButton("All White", press, 4, 2)
app.addButton("All Rainbow", rainbow_press, 5, 2)
app.addButton("All Random", press, 6, 2)
#app.addButton("All Waveform", rainbow_press,6,2)
app.stopLabelFrame() #"All LAN Bulbs"

#-------------------------------------------
app.setSticky("sew")
app.startLabelFrame("HSBK Values", 1, 0)
app.setSticky("news")
app.setPadding(5, 5)

app.addButton("Pick Color", press, 3, 3)
#app.hideButton ( "Pick Color" )


app.addLabel("hueLab", "Hue (H):", 0, 0)
app.addLabel("satLab", "Saturation (S):", 1, 0)
app.addLabel("briLab", "Brightness (B):", 2, 0)
app.addLabel("kelLab", "Kelvin (K) Warmth:", 3, 0)

app.setLabelAlign("hueLab", "left")
app.setLabelAlign("satLab", "left")
app.setLabelAlign("briLab", "left")
app.setLabelAlign("kelLab", "left")

app.addSpinBox("hueSpin", list(reversed(range(65536))), 0, 1)
app.addSpinBox("satSpin", list(reversed(range(65536))), 1, 1)
app.addSpinBox("briSpin", list(reversed(range(65536))), 2, 1)
app.addSpinBox("kelSpin", list(reversed(range(2500, 9001, 1))), 3, 1)

app.setSpinBox("hueSpin", 0)
app.setSpinBox("satSpin", 0)
app.setSpinBox("briSpin", 0)
app.setSpinBox("kelSpin", 3500)

app.setSpinBoxWidth("hueSpin", 5)
app.setSpinBoxWidth("satSpin", 5)
app.setSpinBoxWidth("briSpin", 5)
app.setSpinBoxWidth("kelSpin", 5)

app.setSpinBoxChangeFunction("hueSpin", updateHSB)
app.setSpinBoxChangeFunction("satSpin", updateHSB)
app.setSpinBoxChangeFunction("briSpin", updateHSB)
app.setSpinBoxChangeFunction("kelSpin", updateHSB)


app.addScale("hueScale", 0, 2)
app.addScale("satScale", 1, 2)
app.addScale("briScale", 2, 2)
app.addScale("kelScale", 3, 2)

app.setScaleRange("hueScale", 0, 65535)
app.setScaleRange("satScale", 0, 65535)
app.setScaleRange("briScale", 0, 65535)
app.setScaleRange("kelScale", 2500, 9000)

app.setScaleChangeFunction("hueScale", updateHSB)
app.setScaleChangeFunction("satScale", updateHSB)
app.setScaleChangeFunction("briScale", updateHSB)
app.setScaleChangeFunction("kelScale", updateHSB)

app.startLabelFrame("Bulb Color", 0, 3, 3, 3)
app.setSticky("news")
app.addLabel("bulbcolor", "", 0, 3, 3, 3)
app.setLabel("bulbcolor", " ")
app.setLabelHeight("bulbcolor", 5)
app.setLabelWidth("bulbcolor", 10)
app.setLabelBg("bulbcolor", "gray")
app.stopLabelFrame() # "Bulbs Color"

app.stopLabelFrame() # "HSBK Values"
app.stopLabelFrame() # topmost 

#-----------------------------------------------------
app.setSticky("new")
#-------------------------------------------

app.startLabelFrame(" ")

app.startTabbedFrame("TabbedFrame")
#---------------------------------------------------------------------------------------------------------
app.startTab("Bulbs Details")
#app.setSticky("news")
#app.startLabelFrame("Bulb Details")
#app.setSticky("ew")
#app.setStretch("both")
app.addScrolledTextArea("Result")
app.setTextAreaWidth("Result", 80)
app.setTextAreaHeight("Result", 23)
app.setTextArea("Result", test_string)
#app.stopLabelFrame()
app.stopTab() #"Bulbs Details"
#---------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------
app.startTab("Follow Desktop")
#app.startLabelFrame(FOLLOW_DESKTOP, 0, 0)
#app.setSticky("n")
modeList = ["-Select Region-      "]
modeList.append("Whole Screen")
modeList.append("Rectangular Region")
app.setSticky("w")
app.addCheckBox(FOLLOW_DESKTOP, 0, 0)
app.setCheckBoxChangeFunction(FOLLOW_DESKTOP, followDesktopPressed)
#app.setSticky("ew")
app.addOptionBox(DESKTOP_MODE, modeList, 2, 0)
app.setOptionBoxChangeFunction(DESKTOP_MODE, modeChanged)
app.setOptionBox(DESKTOP_MODE, "Whole Screen", callFunction=False)
app.addLabelEntry(TRANSITION_TIME, 2, 1)
app.setEntryWidth(TRANSITION_TIME, 6)
app.setEntry(TRANSITION_TIME, TRANSITION_TIME_DEFAULT)
#app.startLabelFrame("Region Color", 0, 3)
app.addCheckBox(MAX_SATURATION, 3, 0)
app.addCheckBox(MAX_BRIGHTNESS, 3, 1)
app.setCheckBoxChangeFunction(MAX_SATURATION, maxPressed)
app.setCheckBoxChangeFunction(MAX_BRIGHTNESS, maxPressed)
app.addCheckBox("Evening Mode",3,2)
#app.hideCheckBox(MAX_SATURATION)
#app.hideCheckBox(MAX_BRIGHTNESS)
app.addLabel(REGION_COLOR, "", 4, 0, colspan=5)
app.setLabel(REGION_COLOR, " Desktop Region's Dominant Color")
app.setLabelHeight(REGION_COLOR, 1)
app.setLabelBg(REGION_COLOR, "gray")
app.hideLabel(REGION_COLOR)


app.setEntryTooltip(TRANSITION_TIME, TRANSITION_TIME_TIP)
app.setLabelTooltip(TRANSITION_TIME, TRANSITION_TIME_TIP)
app.setCheckBoxTooltip(FOLLOW_DESKTOP, FOLLOW_DESKTOP_TIP)
app.setOptionBoxTooltip(DESKTOP_MODE, DESKTOP_MODE_TIP)

#app.stopLabelFrame() #FOLLOW_DESKTOP
app.stopTab() #"Follow Desktop"
#---------------------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------------
app.startTab("WaveForm")
#app.addLabel("l3", "Tab 3 Label")
#app.startLabelFrame("Waveform", 1, 1, 5, 1)
#app.setFrameWidth("Waveform",20)
#app.setSticky("news")
app.setSticky("w")

app.addRadioButton("waveform", "Saw")
app.addRadioButton("waveform", "Sine")
app.addRadioButton("waveform", "HalfSine")
app.addRadioButton("waveform", "Triangle")
app.addRadioButton("waveform", "Pulse (Strobe)")

app.setSticky("e")
app.addCheckBox("Transient", 0, 2)
app.setCheckBox("Transient")
app.addButton("Secondary Color", press, 1, 1)
app.addLabel("lblwaveformcolor", "     ", 1, 2)
app.setLabelBg("lblwaveformcolor", "#FF0000")
app.setLabelWidth("lblwaveformcolor", 20)
app.addLabelEntry("Period(ms)", 2, 2)
app.setEntryWidth("Period(ms)", 6)
app.setEntry("Period(ms)", "500")

app.addLabelEntry(CYCLES, 3, 2)
app.setEntryWidth(CYCLES, 6)
app.setEntry(CYCLES, "5")

app.addLabelEntry("Duty Cycle", 4, 2)
app.setEntryWidth("Duty Cycle", 6)
app.setEntry("Duty Cycle", "0")

app.setEntryTooltip("Duty Cycle", DUTY_CYCLE_TIP)
app.setLabelTooltip("Duty Cycle", DUTY_CYCLE_TIP)
app.setEntryTooltip("Cycles", CYCLES_TIP)
app.setLabelTooltip(CYCLES, CYCLES_TIP)
app.setEntryTooltip("Period(ms)", PERIOD_TIP)
app.setLabelTooltip("Period(ms)", PERIOD_TIP)
app.setCheckBoxTooltip("Transient", TRANSIENT_TIP)
app.setSticky("ew")

app.addButton("Execute", press, 5, 0, colspan=3)
app.setButtonBg("Execute", "cyan")

#app.stopLabelFrame() #"WaveForm"
app.stopTab() #"WaveForm"
#---------------------------------------------------------------------------------------------------------
app.startTab("Scenes")

#app.startLabelFrame("Scenes", 0, 1)
app.setSticky("news")
app.addEntry("Scene 1", 0, 0)
app.setEntryChangeFunction("Scene 1", SceneNameChanged)
app.addNamedButton("Save", "Save Scene 1", Scene, 0, 1)
app.addNamedButton("Restore", "Restore Scene 1", Scene, 0, 2)
app.addEntry("Scene 2", 1, 0)
app.setEntryChangeFunction("Scene 2", SceneNameChanged)
app.addNamedButton("Save", "Save Scene 2", Scene, 1, 1)
app.addNamedButton("Restore", "Restore Scene 2", Scene, 1, 2)
app.addEntry("Scene 3", 2, 0)
app.setEntryChangeFunction("Scene 3", SceneNameChanged)
app.addNamedButton("Save", "Save Scene 3", Scene, 2, 1)
app.addNamedButton("Restore", "Restore Scene 3", Scene, 2, 2)
#app.stopLabelFrame()

app.stopTab() #"Scenes"
#---------------------------------------------------------------------------------------------------------
app.startTab(COLOR_CYCLE)
app.setSticky("w")
app.addCheckBox(START_COLOR_CYCLE)
app.setCheckBoxChangeFunction(START_COLOR_CYCLE, ColorCyclePressed)
app.setSticky("ew")

app.startFrame("group")

app.addLabelEntry(CYCLE_INTERVAL, 1, 0); 
app.setEntryWidth(CYCLE_INTERVAL, 5)
app.addScale(CYCLE_INTERVAL_SCALE, 1, 1)
app.setScaleRange(CYCLE_INTERVAL_SCALE, 100, 2000)

app.addLabelEntry(HUE_DELTA, 2, 0)
app.setEntryWidth(HUE_DELTA, 5)
app.addScale(HUE_DELTA_SCALE, 2, 1)
app.setScaleRange(HUE_DELTA_SCALE, 1, 65534)


app.addLabelEntry(TRANSITION_TIME2, 3, 0)
app.setEntryWidth(TRANSITION_TIME2, 5)
app.addScale(TRANSITION_TIME2_SCALE, 3, 1)
app.setScaleRange(TRANSITION_TIME2_SCALE, 0, 2000)
app.stopFrame()

app.startLabelFrame("Note", row=5, column=0)
app.addLabel("note")
#app.setLabelWidth("note",60)
#app.setLabelHeight("note",30)

app.setLabel("note","\nRemember to set the Saturation and Brightness of your bulbs \n(i.e. pick a color) before starting the Color Cycle sequence.\nOnly the Hue will be changed.\n")

#app.setLabelAlign("note", "left")
app.stopLabelFrame()


#app.addLabelEntry(CYCLE_SATURATION,)
#app.setEntryChangeFunction(CYCLE_SATURATION, ColorCyclePressed)
#app.setEntry(CYCLE_SATURATION,65535)
#app.setEntryWidth(TRANSITION_TIME, 6)
app.setEntryChangeFunction(CYCLE_INTERVAL, ColorCyclePressed)
app.setEntryChangeFunction(HUE_DELTA, ColorCyclePressed)
app.setEntryChangeFunction(TRANSITION_TIME2, ColorCyclePressed)
app.setScaleChangeFunction(CYCLE_INTERVAL_SCALE, ColorCyclePressed)
app.setScaleChangeFunction(HUE_DELTA_SCALE, ColorCyclePressed)
app.setScaleChangeFunction(TRANSITION_TIME2_SCALE, ColorCyclePressed)
app.setEntry(CYCLE_INTERVAL,CYCLE_INTERVAL_MS)
app.setEntry(HUE_DELTA,CYCLE_HUE_DELTA)
app.setEntry(TRANSITION_TIME2, TRANSITION_TIME_DEFAULT)


app.setEntryTooltip(TRANSITION_TIME2, TRANSITION_TIME_TIP)
app.setLabelTooltip(TRANSITION_TIME2, TRANSITION_TIME_TIP)
app.setEntryTooltip(HUE_DELTA, HUE_DELTA_TIP)
app.setLabelTooltip(HUE_DELTA, HUE_DELTA_TIP)
app.setEntryTooltip(CYCLE_INTERVAL, CYCLE_INTERVAL_TIP)
app.setLabelTooltip(CYCLE_INTERVAL, CYCLE_INTERVAL_TIP)
#app.setLabelTooltip(CYCLE_SATURATION, CYCLE_SATURATION_TIP)

app.setSticky("ew")

#app.addLabel(CYCLE_COLOR, "")


app.registerEvent(ColorCycle)
app.setPollTime(int(CYCLE_INTERVAL_MS))


app.stopTab() #COLOR_CYCLE
#---------------------------------------------------------------------------------------------------------
app.stopTabbedFrame()

app.stopLabelFrame()# " "

print("Config path:", CONFIG)
print("path:",os.path.dirname(os.path.abspath(__file__) ))
if not os.path.exists(CONFIG):
    print("Creating .ini file")
    open(CONFIG, 'w').close()
    config = ConfigObj(CONFIG)
    config['expectedbulbs'] = 0
    config['Scene 1'] = "Scene 1"
    config['Scene 2'] = "Scene 2"
    config['Scene 3'] = "Scene 3"
    config['transtime'] = 200
    config['waveform'] = 'Saw'
    config['transient'] = True    
    config['period'] = 500
    config['cycles'] = 5
    config['duty_cycle'] = 0
    config['secondary_color'] = "#FF0000"
    config['maxSaturation'] = False
    config['maxBrightness'] = False
    config['is_evening'] = False
    config.write()


#print(".ini file exists")
config = ConfigObj(CONFIG)
print("config:", config)
if 'maxSaturation' in config:
    maxSaturation = (config['maxSaturation']=='True')
    app.setCheckBox(MAX_SATURATION,ticked=(config['maxSaturation']=='True'),callFunction=False)
if 'maxBrightness' in config:
    maxBrightness = (config['maxBrightness']=='True')
    app.setCheckBox(MAX_BRIGHTNESS,ticked=(config['maxBrightness']=='True'),callFunction=False)
if 'is_evening' in config:
    app.setCheckBox("Evening Mode",ticked=(config['is_evening']=='True'),callFunction=False)
if 'waveform' in config:
    app.setRadioButton("waveform",config['waveform'])
if 'transient' in config:
    app.setCheckBox("Transient",config['transient'])
if 'period' in config:
    app.setEntry("Period(ms)",config['period'])
if 'cycles' in config:
    app.setEntry(CYCLES,config['cycles'])
if 'duty_cycle' in config:
    app.setEntry("Duty Cycle",config['duty_cycle'])
if 'secondary_color' in config:
    app.setLabelBg("lblwaveformcolor", config['secondary_color'])
if 'expectedbulbs' in config:
    app.setSpinBox("Expected Bulbs", config['expectedbulbs'])
if 'transtime' in config:
    app.setEntry(TRANSITION_TIME, config['transtime'])
if 'Scene 1' in config:    
    app.setEntry("Scene 1", config["Scene 1"], callFunction=False)
if 'Scene 2' in config:    
    app.setEntry("Scene 2", config["Scene 2"], callFunction=False)
if 'Scene 3' in config:    
    app.setEntry("Scene 3", config["Scene 3"], callFunction=False)
#print("config['bulbs']:",config['bulbs'])
#print("type(config['bulbs']):",type(config['bulbs']))
if os.path.exists(PICKLE):
    bulbPickle = pkl.load(open(PICKLE, "rb"))   #this reads the pickle
    #print (bulbPickle)
    bulbList.clear()
    bulbList.append("-Select Bulb-")

    for i, bulb in enumerate(bulbPickle):
        #print ("mac:",bulb['mac']);
        light = lifxlan.Light(bulb['mac'], bulb['ip'])
        light.label = bulb['label']
        bulbs.append(light)
        bulbList.append(bulb['label'])

    if len(bulbs) > 0:
        app.clearOptionBox("LIFX Bulbs", callFunction=False)
        app.changeOptionBox("LIFX Bulbs", bulbList, callFunction=False)
        app.setLabelBg("lbl2", mygreen)
        app.hideLabel("f1")
        app.setLabel("lbl2", "Recalled " + str(len(bulbs)) + " bulbs")
        app.setCheckBox("Select All")


#light = Light("12:34:56:78:9a:bc", "192.168.1.42")
#print("bulbs:",bulbs)
lan = lifxlan.LifxLAN()

app.go()
