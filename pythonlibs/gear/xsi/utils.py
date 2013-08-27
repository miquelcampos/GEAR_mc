'''

    This file is part of GEAR_mc.
    GEAR_mc is a fork of Jeremie Passerin's GEAR project.

    GEAR is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

    Author:     Jeremie Passerin    geerem@hotmail.com  www.jeremiepasserin.com
    Fork Author:  Miquel Campos       hello@miqueltd.com  www.miqueltd.com
    Date:       2013 / 08 / 16

'''

## @package gear.xsi.utils
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import re

# gear
from gear.xsi import xsi, c

##########################################################
# UTILS
##########################################################
# ========================================================
## Convert a string with _L_, _L0_, L_, _L to R. And vice and versa.
# @param name String - string to convert
# @return Tuple of Integer - screen width and height.
def convertRLName(name):

    if name == "L":
        return "R"
    elif name == "R":
        return "L"

    rePattern = re.compile("_[RL][0-9]+_|^[RL][0-9]+_|_[RL][0-9]+$|_[RL]_|^[RL]_|_[RL]$")

    reMatch = re.search(rePattern, name)
    if reMatch:
      instance = reMatch.group(0)
      if instance.find("R") != -1:
            rep = instance.replace("R", "L")
      else:
            rep = instance.replace("L", "R")

      name = re.sub(rePattern, rep, name)

    return name

# ========================================================
## Get the symmetry map of an object.
# @param obj Geometry.
# @param logWarning Boolean - Log a warning if there is no symmetry map on selection.
# @return Map - The object symmetry map. False if there is none.
def getSymmetryMap(obj, logWarning=True):

     allSymmetryMaps = xsi.FindObjects(None, "{2EBA6DE4-B7EA-4877-80FE-FC768F32729F}")

     for map in allSymmetryMaps:
          if map.Parent3DObject.IsEqualTo(obj):
                return map

     if logWarning:
          xsi.LogMessage("No Symmetry Map for " + obj.FullName, c.siWarning)

     return False

# ========================================================
## Create a Display Property on the object and set the wirecolor.
# @param obj X3DObject - Object.
# @param color List of Double - The RGB color of the object (ie. [1,0,0] for red).
# @return Property - The newly created display property.
def setColor(obj, color=[0,0,0]):

    disp_prop = obj.AddProperty("Display Property")
    disp_prop.wirecolorr.Value = color[0]
    disp_prop.wirecolorg.Value = color[1]
    disp_prop.wirecolorb.Value = color[2]

    return disp_prop
