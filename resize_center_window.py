#!/usr/bin/python3

import os
import os.path
import sys
import subprocess

import logging
logging.basicConfig( level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"  )

LOGGING_FILE_FORMAT = "%(asctime)s - %(levelname)-8s - %(name)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
hf = logging.FileHandler( "/tmp/resize.log", "a" )
hf.setFormatter( logging.Formatter(LOGGING_FILE_FORMAT) )
hf.setLevel( logging.DEBUG )

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#log.addHandler(hf)

#import resize_save_config as cfg

def read_coords( coordsfile ):
    try:
        with open(coordsfile) as cf:
            l = cf.readline().strip()
            return l.split(" ")
    except Exception as e:
        log.info("Error: {} for file '{}'".format(e, coordsfile))
        return (1000,500)

#log.info(sys.argv)

COORDSFILE="{}/.config/resize_center_window.txt".format(os.environ["HOME"])
log.debug("Coordsfile is '{}'".format(COORDSFILE))

if 'COORDSFILE' in os.environ:
    sizex,sizey = read_coords(os.environ['COORDSFILE'])
else:
    sizex,sizey = read_coords(COORDSFILE)

# mouse location
# xdotool getmouselocation
# x:3029 y:560 screen:0 window:58720297
ret = subprocess.run("xdotool getmouselocation | awk '{print $1\" \"$2}' | tr -d xy: ", shell=True, check=True, stdout=subprocess.PIPE)
mousex, mousey = str(ret.stdout, "utf-8").strip().split(" ")
log.debug("mouse x,y: '{},{}'".format(mousex, mousey))

# if monitor is connected but disabled in options, there is following ouput after 'grep connected':
# eDP-1 connected (normal left inverted right x axis y axis)
# DP-1-2 connected primary 1920x1200+0+0 (normal left inverted right x axis y axis) 518mm x 324mm
ret = subprocess.run("xrandr | grep ' connected ' | sed 's/primary //' | awk '{print $3}' | tr x+ \ \  | grep '^[0-9]'", shell=True, check=True, stdout=subprocess.PIPE)
lns = [ l.split(" ") for l in str(ret.stdout,"utf-8").strip().split("\n") ]
"""
lns indexes:
0 ... width of display
1 ... height of display
2 ... x offset of display in workspace
2 ... y offset of display in workspace
"""

wins = {"x": {}, "y": {}}
for l in lns:
    wins['x'][ l[2] ] = l
    wins['y'][ l[3] ] = l

def get_display_spec(wins):
    # prereq
    #   - we have horizontal positioning of monitors
    #   - we have 2 monitors
    oldx = -1
    display_x = None

    xorder = sorted(list(wins['x'].keys()))
    log.debug("xorder: '{}'".format(xorder))
    for n in range(len(xorder)):
        log.debug("Iter: mousex, oldx, n: {}, {}, {}".format(mousex, oldx, n))
        if int(mousex) >= int(oldx) and int(mousex) < int(xorder[n]):
            display_x = xorder[n - 1]
            break
        oldx = xorder[n]

    if display_x is None:
        display_x = xorder[-1]

    log.info("x / wins: '{}/{}'".format(display_x, wins))

    return wins['x'][display_x]


display_spec = get_display_spec(wins)
log.debug("display_spec: '{}'".format(display_spec))

# calculate new pos of window
# x = (display_width - window_width) / 2 + display_x_offset
# y = (display_height - window_height) / 2 + display_y_offset

newx = int( (int(display_spec[0]) - int(sizex)) / 2 + int(display_spec[2]) )
newy = int( (int(display_spec[1]) - int(sizey)) / 2 + int(display_spec[3]) )

if len(sys.argv) > 1:
    win_id = int(sys.argv[1])
else:
    ret = subprocess.run("xdotool selectwindow", shell=True, check=True, stdout=subprocess.PIPE)
    win_id = int(ret.stdout)

log.debug("size: x,y: {}.{}".format(sizex,sizey))
log.debug("offs: x,y: {}.{}".format(newx,newy))

ret = subprocess.run("xdotool windowsize {} {} {}".format(win_id, sizex, sizey), shell=True, check=True, stdout=subprocess.PIPE)
ret = subprocess.run("xdotool windowmove {} {} {}".format(win_id, newx, newy), shell=True, check=True, stdout=subprocess.PIPE)
