#!/usr/bin/env python3

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

myos = system()
if (myos == 'Windows') or (myos == 'Darwin'):
    from PIL import ImageGrab
elif (myos == 'Linux'):
    import pyscreenshot as ImageGrab


 

DECIMATE  = 1   # skip every DECIMATE number of pixels to speed up calculation
TRANSIENT_TIP = "If selected, return to the original color after the specified number of cycles. If not selected, set light to specified color"
PERIOD_TIP = "Period is the length of one cycle in milliseconds"
CYCLES_TIP = "Cycles is the number of times to repeat the waveform"
DUTY_CYCLE_TIP = "Duty Cycle is an integer between -32768 and 32767. Its effect is most obvious with the Pulse waveform. Set Duty Cycle to 0 to spend an equal amount of time on the original color and the new color. Set Duty Cycle to positive to spend more time on the original color. Set Duty Cycle to negative to spend more time on the new color"
EXPECTED_TIP = "Select 0 to find all available bulbs. Select any number to look for exactly that number of bulbs"
DURATION_TIP = "The time (in ms) that a color transition takes"
FOLLOW_DESKTOP_TIP = "Make your bulbs' color match your desktop"
EXPECTED_BULBS = 2
DURATION_DEFAULT = 200
CONFIG = "lights.ini"
PICKLE = "lifxList.pkl"
SCENE1_C = "scene1_c.pkl"
SCENE1_P = "scene1_p.pkl"
SCENE2_C = "scene2_c.pkl"
SCENE2_P = "scene2_p.pkl"
SCENE3_C = "scene3_c.pkl"
SCENE3_P = "scene3_p.pkl"
CYCLES = "Cycles"
alreadyDone = False
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
    print(name, "Entry changed")
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
                original_colors1 = pkl.load(open(SCENE1_C , "rb"))   
                original_powers1 = pkl.load(open(SCENE1_P , "rb"))   
        
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
                original_colors2 = pkl.load(open(SCENE2_C , "rb"))   
                original_powers2 = pkl.load(open(SCENE2_P , "rb"))   
        
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
                original_colors3 = pkl.load(open(SCENE3_C , "rb"))   
                original_powers3 = pkl.load(open(SCENE3_P , "rb"))   
        
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
        app.errorBox("Error", str(e)+"\n\n Scene Operation failed. This feature is buggy and only works about 50% of the time. Sometimes, you can still save and restore a scene despite this error. If you keep getting this error and can not perform a 'Restore', try restarting the app then try again.")
        return        
    
    

def updateSliders(hsbk):
    #print("h:",hsbk[0])
    #print("s:",hsbk[1])
    #print("b:",hsbk[2])
    #print("k:",hsbk[3])
    
    app.setSpinBox("hueSpin", int(hsbk[0]),callFunction=False)
    app.setSpinBox("satSpin", int(hsbk[1]),callFunction=False)
    app.setSpinBox("briSpin", int(hsbk[2]),callFunction=False)
    app.setSpinBox("kelSpin", int(hsbk[3]),callFunction=False)
    app.setScale("hueScale", int(hsbk[0]),callFunction=False)    
    app.setScale("satScale", int(hsbk[1]),callFunction=False)    
    app.setScale("briScale", int(hsbk[2]),callFunction=False)    
    app.setScale("kelScale", int(hsbk[3]),callFunction=False)    
    

# function to convert the scale values to an RGB hex code
def getHSB():
    H = app.getScale("hueScale")
    S = app.getScale("satScale")
    B = app.getScale("briScale")
    K = app.getScale("kelScale")

    #RGB = "#"+str(R)+str(G)+str(B)

    return {'H':H, 'S':S ,'B':B, 'K':K }


# funciton to update widgets
def updateHSB(name):
    # this stops the changes in slider/spin from constantly calling each other
    #print ("name:",name)
    global alreadyDone
    if alreadyDone:
        alreadyDone = False
        return
    else:
        alreadyDone = True

    # split the widget's name into the type & colour
    colour = name[0:3]
    widg = name[3:]
    
    # get the current RGB value
    HSB = getHSB()
    #print("HSB:",HSB,"type(HSB)",type(HSB))
    #print("H",HSB["H"])
    #print("S",HSB["S"])
    #print("B",HSB["B"])

    # depending on the type, get & set...
    if widg == "Scale":
        value = app.getScale(name)
        app.setSpinBox(colour+"Spin", value)
    elif widg == "Spin":
        value = app.getSpinBox(name)
        app.setScale(colour+"Scale", value)

    # update the label
    h = HSB["H"]/65535.0;#print("h:",h)
    s = HSB["S"]/65535.0;#print("s:",s)
    v = HSB["B"]/65535.0;#print("v:",v)
    k = HSB["K"];#print("v:",v)

    rgb1= hsv_to_rgb(h,s,v);#print("rgb1:",rgb1)
    c = Color(rgb=(rgb1[0], rgb1[1], rgb1[2])) 
    #print("c:",c)
    app.setLabelBg("bulbcolor", c.hex_l)
    
    global selected_bulb
    bulbHSBK = [HSB["H"],HSB["S"],HSB["B"],k]
    #print ("bulbHSBK:",bulbHSBK)
    
    if gSelectAll:
        lan.set_color_all_lights(bulbHSBK, duration=0, rapid=False)
        
    elif selected_bulb:
        #print("sending color",hsv)
        selected_bulb.set_color(bulbHSBK, duration=0, rapid=False)
    
    #app.setEntry("colCode", RGB)


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
    gExpectedBulbs = app.getSpinBox("Expected Bulbs")
    config['expectedbulbs'] = gExpectedBulbs
    config.write()
    #print("gExpectedBulbs:",gExpectedBulbs)

    
def rgb_to_hsv(r, g, b):
    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, v = high, high, high

    d = high - low
    s = 0 if high == 0 else d/high

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
    i = math.floor(h*6)
    f = h*6 - i
    p = v * (1-s)
    q = v * (1-f*s)
    t = v * (1-(1-f)*s)

    r, g, b = [
        (v, t, p),
        (q, v, p),
        (p, v, t),
        (p, q, v),
        (t, p, v),
        (v, p, q),
    ][int(i%6)]

    return r, g, b


def listChanged():
    app.clearTextArea("Result");
    app.setTextArea("Result", "Loading bulb details")
    selected =  (app.getOptionBox("LIFX Bulbs"))#;print("selected: ",selected)
    global bulbs
    global selected_bulb
    global details
    try:
        for bulb in bulbs:
            if (bulb.label == selected):
                #print("Found selected bulb")
                selected_bulb = bulb
                details =str(selected_bulb)
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
            app.setButtonImage("Light","bulb_on.gif")
        elif "Power: Off" in details:
            #print ("BULB is OFF ")
            app.setButtonImage("Light","bulb_off.gif")
    except Exception as e:
        print ("Ignoring error:", str(e))
    
    app.setButton ( "Light", "Toggle "+selected )    
    app.showButton("Light")
    color = bulb.get_color();#print(color[0],color[1],color[2]); 
    h = color[0]/65535.0;#print("h:",h)
    s = color[1]/65535.0;#print("s:",s)
    v = color[2]/65535.0;#print("v:",v)

    rgb1= hsv_to_rgb(h,s,v);#print("rgb1:",rgb1)
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
            app.errorBox("Error", "No bulbs found. Please try again.")
            app.setLabelBg("lbl2","red")
            app.setLabel("lbl2", "Found 0 bulbs")
            return
        else:
            app.setLabelBg("lbl2","green")
            app.hideLabel("f1")
        
        app.setLabel("lbl2", "Found "+str(len(bulbs))+" bulbs")
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
            lifxDict['label']=label
            lifxDict['mac']=mac
            lifxDict['ip']=ip
            lifxList.append(lifxDict.copy())
            bulbList.append(label)
        app.changeOptionBox("LIFX Bulbs", bulbList,callFunction=False)
        app.showButton ( "Pick Color" )
        #print(lifxList)
        #config['bulbs'] = lifxList
        pkl.dump(lifxList, open(PICKLE, "wb" ))   #this pickles
#exit(0)        
        #config.write()
        
    
    except Exception as e:
        print ("Ignoring error:", str(e))
        app.setLabelBg("lbl2","gray")
        app.setLabel("lbl2", "Found 0 bulbs")
        app.errorBox("Error", str(e)+"\n\nPlease try again. If you keep getting this error, check/toggle your WiFi, ensure that 'Expected Bulbs' is either 0 or the number of bulbs you have and finally, try restarting the app")
        
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
    
    #print(name, "button pressed")
    
    if (name == "Find Bulbs") :
        finder()
    elif (name == "All Off"):
        if len(bulbs) < 1:
            return
        lan.set_power_all_lights(False, rapid=True)
    elif (name == "All Random"):
        if len(bulbs) < 1:
            return
        selected =  (app.getOptionBox("LIFX Bulbs"))
        for bulb in bulbs:
            hue = (randint(0, 65535))
            sat = (randint(40000, 65535))
            bulb.set_color([hue, sat, 65535, 3500],duration=0, rapid=True)     
            if (bulb.label == selected):
                h = hue/65535.0;#print("h:",h)
                s = sat/65535.0;#print("s:",s)
                v = 1;#print("v:",v)
                rgb1= hsv_to_rgb(h,s,v);#print("rgb1:",rgb1)
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
        lan.set_color_all_lights([0,0,65535,3500],duration=0, rapid=True)     
        updateSliders([0,0,65535,3500])
        app.setLabelBg("bulbcolor", "#FFFFFF")
           
    elif (name == "Execute") :
        waveform = app.getRadioButton("waveform")
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
        if (is_transient):
            is_transient = 1
        else:
            is_transient = 0
            
        #print("is_transient:",is_transient)
        #pickedColor = app.getLabelBg("lblwaveformcolor")
        
        c = Color(str(gwaveformcolor))
        hsv = rgb_to_hsv(c.red,c.green,c.blue)
        #print("hsv:",hsv)
        bulbHSBK = [hsv[0]*65535.0,hsv[1]*65535.0,hsv[2]*65535.0,3500]
        #print (bulbHSBK)
        period = app.getEntry("Period(ms)")
        cycles = app.getEntry(CYCLES)
        duty_cycle = app.getEntry("Duty Cycle")
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
        
    elif (name == "Secondary Color") :
        pickedColor = app.colourBox(colour="#FF0000")
        app.setLabelBg("lblwaveformcolor", pickedColor)
        gwaveformcolor = pickedColor
    elif (name == "Pick Color") :
        pickedColor = app.colourBox(colour="#FFFFFF")
        app.setLabelBg("bulbcolor", pickedColor)
        #print("pickedColor:",pickedColor)
        if pickedColor == None:
            return
        c = Color(str(pickedColor))
        hsv = rgb_to_hsv(c.red,c.green,c.blue)
        #print("hsv:",hsv)
        bulbHSBK = [hsv[0]*65535.0,hsv[1]*65535.0,hsv[2]*65535.0,3500]
        #print ("bulbHSBK:",bulbHSBK)
        if gSelectAll:
            lan.set_color_all_lights(bulbHSBK, duration=0, rapid=False)
        elif selected_bulb:
            #print("sending color",hsv)
            selected_bulb.set_color(bulbHSBK, duration=0, rapid=False)
        else:
            app.errorBox("Error", "Error. No bulb was selected. Please select a bulb from the pull-down menu (or tick the 'Select All' checkbox) and try again.")
            return
        
        updateSliders(bulbHSBK)

        
    elif (name == "Light") :
        #print("selected: ",selected_bulb.label)
        #print("Power is Currently: {}".format(selected_bulb.power_level))
        try:
            onOff = selected_bulb.power_level; 
        except Exception as e:
            print ("Ignoring error:", str(e))
            app.errorBox("Error", str(e)+"\n\nTry selecting a bulb from the list first.")
            return
            
        #selected_bulb.set_power(not selected_bulb.get_power(), duration=0, rapid=True)
        
        if "Power: Off" in details:
            selected_bulb.set_power(65535, duration=0, rapid=False)
            try:
                app.setButtonImage("Light","bulb_on.gif");#print("PowerOn");
            except Exception as e:
                print ("Ignoring error:", str(e))
            details = details.replace("Power: Off", "Power: On"); 
            app.clearTextArea("Result")
            app.setTextArea("Result", details)
            
        else:
            selected_bulb.set_power(0, duration=0, rapid=False)
            try:
                app.setButtonImage("Light","bulb_off.gif");#print("PowerOff");
            except Exception as e:
                print ("Ignoring error:", str(e))
            details = details.replace("Power: On", "Power: Off"); #print("details:\n",details)
            app.clearTextArea("Result")
            app.setTextArea("Result", details)
            
        app.setButton ( "Light", "Toggle "+(app.getOptionBox("LIFX Bulbs")) )
        app.showButton("Light")
        
        
        #listChanged()

def rainbow_press(name):
    print("Discovering lights...")
    lan = lifxlan.LifxLAN(EXPECTED_BULBS)
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

def rainbow(lan, duration_secs=0.5, smooth=False):
    colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
    transition_time_ms = duration_secs*1000 if smooth else 500
    rapid = True if duration_secs < 1 else False
    for i in range(0,3):
        for color in colors:
            lan.set_color_all_lights(color, transition_time_ms, rapid)
            sleep(duration_secs)


def followDesktop():
    global gSelectAll
    global lan
    global is_follow
    global selected_bulb
    global r
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    print("screen_width:",screen_width," screen_height:",screen_height)
    print("Follow:",is_follow)  
    mysize = 128, 128
    duration = app.getEntry("Duration")
    print("r:",r)
    print("Starting Loop")
    
    while (is_follow):
     #input("Press Enter to continue...")
     app.hideEntry("Duration")
     # Clear colour accumulators 
     red   = 0
     green = 0
     blue  = 0
 
     left   = r[0]      # The x-offset of where your crop box starts
     top    = r[1]    # The y-offset of where your crop box starts
     width  = r[2]   # The width  of crop box
     height = r[3]    # The height of crop box
     box    = (left, top, left+width, top+height)

     # take a screenshot
     image = ImageGrab.grab(bbox=box)
     #image.show()
     #image.thumbnail(mysize)
     #image.show()
     #with mss() as sct:
     #   monitor = {'top': top, 'left': left, 'width': width, 'height': height}
     #   im = sct.grab(monitor)
     #   img = cv2.imread(im)
        
     #printscreen_numpy = np.array(image.getdata(),dtype='uint8').reshape((image.size[1],image.size[0],3)) 
     img = np.array(image.convert('RGB'))
     #cv2.imshow("window",printscreen_numpy)
     #cv2.waitKey(0)
     #img = cv2.imread(im)
     #start = time.clock()
     
     #average_color = [img[:, :, i].mean() for i in range(img.shape[-1])]
     
     arr = np.float32(img)
     pixels = arr.reshape((-1, 3))
     n_colors = 1
     criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
     flags = cv2.KMEANS_RANDOM_CENTERS
     _, labels, centroids = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
     palette = np.uint8(centroids)
     quantized = palette[labels.flatten()]
     quantized = quantized.reshape(img.shape)
     dominant_color = palette[np.argmax(itemfreq(labels)[:, -1])]
     #print ("time1:",time.clock() - start)
     #print ("average_color: ",average_color)
     #print("dominant_color: ",dominant_color)
     
     '''
     #start = time.clock()
     width, height = image.size
     for y in range(0, height, DECIMATE):  #loop over the height
         for x in range(0, width, DECIMATE):  #loop over the width 
             #print "\n coordinates   x:%d y:%d \n" % (x,y)
             color = image.getpixel((x, y))  #grab a pixel
             # calculate sum of each component (RGB)
             red = red + color[0]
             green = green + color[1]
             blue = blue + color[2]
             #print red + " " +  green + " " + blue
             #print "\n totals   red:%s green:%s blue:%s\n" % (red,green,blue)
             #print color
     #print(time.clock())

     # calculate the averages
     red = (( red / ( (height/DECIMATE) * (width/DECIMATE) ) ) )/255.0
     green = ((green / ( (height/DECIMATE) * (width/DECIMATE) ) ) )/255.0
     blue = ((blue / ( (height/DECIMATE) * (width/DECIMATE) ) ) )/255.0

     # generate a composite colour from these averages
     c = Color(rgb=(red, green, blue))
     #print (c)
     print("c.red:",c.red," c.green:",c.green," c.blue:",c.blue)
     #print ("time2: ",time.clock() - start)
     #print ("\naverage1  red:%s green:%s blue:%s" % (red,green,blue))
     #print ("average1   hue:%f saturation:%f luminance:%f" % (c.hue,c.saturation,c.luminance))
     #print ("average1  (hex) "+  (c.hex))
    
     #hsv = rgb_to_hsv(c.red,c.green,c.blue)
     '''
     #hsv = rgb_to_hsv(average_color[0]/255.0, average_color[1]/255.0, average_color[2]/255.0)
     hsv = rgb_to_hsv(dominant_color[0]/255.0, dominant_color[1]/255.0, dominant_color[2]/255.0)
     
     #print("hsv:",hsv)
     bulbHSBK = [hsv[0]*65535.0,hsv[1]*65535.0,hsv[2]*65535.0,3500]
     #print ("bulbHSBK:",bulbHSBK)
     #exit(0)
     try:
         if gSelectAll:
             lan.set_color_all_lights(bulbHSBK, duration=duration, rapid=True)
         elif selected_bulb:
             #print("sending color",hsv)
             selected_bulb.set_color(bulbHSBK, duration=duration, rapid=True)
         else:
             app.errorBox("Error", "Error. No bulb was selected. Please select a bulb from the pull-down menu (or tick the 'Select All' checkbox) and try again.")
             app.setCheckBox("Follow Desktop",False)
             is_follow = False
             return        
     except Exception as e:
         print ("Ignoring error:", str(e))
    
    print("Exiting loop")
    
def iswindows():
  os = java.lang.System.getProperty( "os.name" )
  return "win" in os.lower()    
    
def followDesktopPressed(name):
    global is_follow
    global r
    is_follow = app.getCheckBox("Follow Desktop")
    app.showEntry("Duration")
    if (is_follow):
        print("Pressed:",name," Follow:",is_follow)  
        app.setTransparency(0)
        app.infoBox("Select Region", "A new window entitled \"Screenshot\" will pop up. Drag a rectangle around the region of interest and press ENTER (might have to press it twice). This region's dominant color will be sent to the bulbs to match. To Cancel, press c (maybe twice).", parent=None)
        myos = system()
        image = ImageGrab.grab()
        if (myos == 'Linux') or (myos == 'Darwin'):
            print("Mac OS detected.")
            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        elif (myos == 'Windows'):
            print("Windows OS detected.")
            open_cv_image = np.array(image) 
        
        # Convert RGB to BGR 
        im = open_cv_image[:, :, ::-1].copy() 
        cv2.namedWindow("Screenshot", cv2.WINDOW_FULLSCREEN) 
        cv2.moveWindow("Screenshot", 0, 0) 
        r = cv2.selectROI("Screenshot", im, False)
        #cv2.waitKey()
        print("r is",r)
        if not any(r):
            print("No region selected. Exiting")
            cv2.destroyAllWindows()
            app.setCheckBox("Follow Desktop",False)
            is_follow = False
            app.setTransparency(1)
            return
        #cv2.waitKey(0)
        cv2.destroyAllWindows()
        app.setTransparency(1)
        app.thread(followDesktop)    


bulbList = ["-None-          "]

app = App("LIFX Controller")
#app = gui("LIFX Controller")
app.setStretch("both")
app.setResizable(True)
app.setFont(12)

app.setSticky("new")

app.startLabelFrame("", 0,0)
app.setSticky("new")
app.startLabelFrame("Find", 0,0)
app.setSticky("new")
app.setPadding(1)
app.addFlashLabel("f1", "Start here --->",0,0)
app.addButton("Find Bulbs",press,0,1)
expected_range = list(range(1,20))
app.addLabelSpinBox ( "Expected Bulbs", list(reversed(range(20))), 0,2 )
app.setSpinBox("Expected Bulbs", EXPECTED_BULBS)
gExpecteBulbs = app.getSpinBox("Expected Bulbs")
app.setSpinBoxChangeFunction("Expected Bulbs", expectedPressed)
app.setSpinBoxWidth("Expected Bulbs", 2)

app.setSpinBoxTooltip("Expected Bulbs",EXPECTED_TIP)
app.setLabelTooltip("Expected Bulbs",EXPECTED_TIP)

app.addLabel("lbl2"," ",1,0)
app.setLabelBg("lbl2","white")
app.addNamedCheckBox("Select All Bulbs","Select All",1,2)
app.setCheckBoxChangeFunction("Select All", selectAllPressed)


app.addOptionBox("LIFX Bulbs",bulbList,1,1)
app.setOptionBoxChangeFunction("LIFX Bulbs", listChanged)
app.setSticky("n")
try:
    app.addImageButton("Light", press, "bulb_off.gif",2,2)
except Exception as e:
    print ("Ignoring error:", str(e))
    #app.errorBox("Error", str(e)+"\n\nTry selecting a bulb from the list first.")
    #return

app.setButton( "Light", "Toggle Selected" )
#app.setButtonHeight ( "Light", 40 )

#app.hideButton("Light")

app.stopLabelFrame()
#-------------------------------------------------------------------------------
app.startLabelFrame("Scenes", 0,1)
app.setSticky("news")
app.addEntry("Scene 1",0,0)
app.setEntryChangeFunction("Scene 1", SceneNameChanged)
app.addNamedButton("Save","Save Scene 1",Scene,0,1)
app.addNamedButton("Restore","Restore Scene 1",Scene,0,2)
app.addEntry("Scene 2",1,0)
app.setEntryChangeFunction("Scene 2", SceneNameChanged)
app.addNamedButton("Save","Save Scene 2",Scene,1,1)
app.addNamedButton("Restore","Restore Scene 2",Scene,1,2)
app.addEntry("Scene 3",2,0)
app.setEntryChangeFunction("Scene 3", SceneNameChanged)
app.addNamedButton("Save","Save Scene 3",Scene,2,1)
app.addNamedButton("Restore","Restore Scene 3",Scene,2,2)
app.stopLabelFrame()
#-------------------------------------------------------------------------------
#app.setButtonImage("picker", "colorpicker.gif", align=None)
###
app.setSticky("ne")
app.startLabelFrame("All LAN Bulbs",0,2)
app.setSticky("new")
app.addButton("All Off", press,2,2)
app.addButton("All On",  press,3,2)
app.addButton("All White",  press,4,2)
app.addButton("All Rainbow", rainbow_press,5,2)
app.addButton("All Random", press,6,2)
#app.addButton("All Waveform", rainbow_press,6,2)
app.stopLabelFrame()

#-------------------------------------------
app.setSticky("sew")
app.startLabelFrame("HSBK Values",1,0)
app.setSticky("news")
app.setPadding(5,5)

app.addButton("Pick Color", press,3,3)
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
app.addSpinBox("kelSpin", list(reversed(range(2500,9001,1))), 3, 1)

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

app.startLabelFrame("Bulb Color",0,3,3,3)
app.setSticky("news")
app.addLabel("bulbcolor", "", 0, 3, 3,3)
app.setLabel("bulbcolor"," ")
app.setLabelHeight("bulbcolor", 5)
app.setLabelWidth("bulbcolor", 10) 
app.setLabelBg("bulbcolor", "gray")
app.stopLabelFrame()

app.stopLabelFrame()
#-------------------------------------------
app.startLabelFrame("Waveform",1,1,5,1)
#app.setFrameWidth("Waveform",20)
#app.setSticky("news")
app.setSticky("w")

app.addRadioButton("waveform", "Saw")
app.addRadioButton("waveform", "Sine")
app.addRadioButton("waveform", "HalfSine")
app.addRadioButton("waveform", "Triangle")
app.addRadioButton("waveform", "Pulse (Strobe)")

app.setSticky("e")
app.addCheckBox("Transient",0,2)
app.setCheckBox("Transient")
app.addButton("Secondary Color", press,1,1)
app.addLabel("lblwaveformcolor","     ",1,2)
app.setLabelBg("lblwaveformcolor", "#FF0000")
app.setLabelWidth("lblwaveformcolor",20)
app.addLabelEntry("Period(ms)",2,2)
app.setEntryWidth("Period(ms)",6)
app.setEntry("Period(ms)", "500")

app.addLabelEntry(CYCLES,3,2)
app.setEntryWidth(CYCLES,6)
app.setEntry(CYCLES, "5")

app.addLabelEntry("Duty Cycle",4,2)
app.setEntryWidth("Duty Cycle",6)
app.setEntry("Duty Cycle", "0")

app.setEntryTooltip("Duty Cycle",DUTY_CYCLE_TIP)
app.setLabelTooltip("Duty Cycle",DUTY_CYCLE_TIP)
app.setEntryTooltip("Cycles",CYCLES_TIP)
app.setLabelTooltip(CYCLES,CYCLES_TIP)
app.setEntryTooltip("Period(ms)",PERIOD_TIP)
app.setLabelTooltip("Period(ms)",PERIOD_TIP)
app.setCheckBoxTooltip("Transient",TRANSIENT_TIP)
app.setSticky("ew")

app.addButton("Execute", press,5,0,colspan=3)
app.setButtonBg("Execute", "cyan")





app.stopLabelFrame()
#-------------------------------------------



app.stopLabelFrame()


#app.setSticky("news")
app.startLabelFrame("Bulb Details",5,0)
app.setSticky("ew")
app.addScrolledTextArea("Result",0,0)
#app.setTextAreaWidth("Result", 45)
app.setTextAreaHeight("Result", 25)
app.setTextArea("Result", test_string)
app.stopLabelFrame()



if not os.path.exists(CONFIG):
    print("Creating .ini file")
    open(CONFIG, 'w').close()
    config = ConfigObj(CONFIG)
    config['expectedbulbs'] = 0
    config['Scene 1'] = "Scene 1"
    config['Scene 2'] = "Scene 2"
    config['Scene 3'] = "Scene 3"
    config['bulbs'] = {}
    
    config.write()
    

#print(".ini file exists")
config = ConfigObj(CONFIG)
print("config:",config)
app.setSpinBox("Expected Bulbs", config['expectedbulbs'])
app.setEntry("Scene 1", config["Scene 1"], callFunction=False)
app.setEntry("Scene 2", config["Scene 2"], callFunction=False)
app.setEntry("Scene 3", config["Scene 3"], callFunction=False)
#print("config['bulbs']:",config['bulbs'])
#print("type(config['bulbs']):",type(config['bulbs']))
if os.path.exists(PICKLE):
    bulbPickle = pkl.load(open(PICKLE , "rb"))   #this reads the pickle
    #print (bulbPickle)
    bulbList.clear()
    bulbList.append("-Select Bulb-")
    
    for i, bulb in enumerate(bulbPickle):
        #print ("mac:",bulb['mac']); 
        light = lifxlan.Light(bulb['mac'],bulb['ip'])
        light.label = bulb['label']
        bulbs.append(light)
        bulbList.append(bulb['label'])

    if len(bulbs) > 0:
        app.clearOptionBox("LIFX Bulbs", callFunction=False)
        app.changeOptionBox("LIFX Bulbs", bulbList, callFunction=False)
        app.setLabelBg("lbl2","green")
        app.hideLabel("f1")
        app.setLabel("lbl2", "Recalled "+str(len(bulbs))+" bulbs")        
        app.setCheckBox("Select All")
    
            
#light = Light("12:34:56:78:9a:bc", "192.168.1.42")
#print("bulbs:",bulbs)
lan = lifxlan.LifxLAN()


#-------------------------------------------
app.startLabelFrame("Desktop",2,0)
app.setSticky("w")
app.addCheckBox("Follow Desktop")
app.setCheckBoxChangeFunction("Follow Desktop", followDesktopPressed)
app.addLabelEntry("Duration")
app.setEntryWidth("Duration",6)
app.setEntry("Duration",DURATION_DEFAULT)
app.setEntryTooltip("Duration",DURATION_TIP)
app.setLabelTooltip("Duration",DURATION_TIP)
app.setCheckBoxTooltip("Follow Desktop",FOLLOW_DESKTOP_TIP)
app.stopLabelFrame()

#-------------------------------------------



app.go()
