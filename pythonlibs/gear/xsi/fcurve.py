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

## @package gear.xsi.fcurve
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
from gear.xsi import xsi, c

##########################################################
# FCURVE
##########################################################
# Get FCurve Values ======================================
## Get X values evently spaced on the FCurve.
# @param fcv FCurve - The FCurve to evaluate.
# @param division Integer - The number of division you want to evaluate on the FCurve.
# @return List of Double - The values.
def getFCurveValues(fcv, division, factor=1):
    incr = 100 / (division-1.0)
    return [round(fcv.Eval(i*incr),2)*factor for i in range(division)]

# Draw FCurve ============================================
## Set FCurve Keys
# @param fcv FCurve - The FCurve to edit.
# @param keys List of Tuple (Time, Value) - The tuple (Key, Value) you want to add on the curve.
# @param siInterpolation String - Interpolation of the curve.
# @return the fcurve.
def drawFCurve(fcv, keys, interpolation=c.siCubicInterpolation, extrapolation=c.siConstantExtrapolation):

    fcv.BeginEdit()
    fcv.RemoveKeys()

    for k in keys:
        fcv.AddKey(k[0], k[1])
        key = fcv.GetKey(k[0], 0)

        if len(k) > 2 and k[2] is not None: key.LeftTanX = float(k[2])
        if len(k) > 3 and k[3] is not None: key.LeftTanY = float(k[3])
        if len(k) > 4 and k[4] is not None: key.RightTanX = float(k[4])
        if len(k) > 5 and k[5] is not None: key.RightTanY = float(k[5])

        if len(k) > 6 and k[6] is not None: key.Interpolation = int(k[6])

    fcv.Interpolation = interpolation
    fcv.Extrapolation = extrapolation

    fcv.EndEdit()

    return fcv

# ========================================================
## Return the keys of the fcurve as an 2 dimensional array
# @param fcv FCurve
# @return list
def getFCurveKeys(fcv):

    return [ [key.Time, key.Value, key.LeftTanX, key.LeftTanY, key.RightTanX, key.RightTanY, key.Interpolation] for key in fcv.Keys ]
   
# Copy FCurve ============================================
## Copy the keys of source fcurve on target fcurve
# @param target FCurve - The target FCurve (the one we write on).
# @param source FCurve - The source FCurve.
# @return
def copyFCurve(target, source):

    drawFCurve(target, getFCurveKeys(source), source.Interpolation, source.Extrapolation)

# GetFirstAndLastKey ====================================
## Get First and Last Key for given controlers
# @param controlers Collection of X3DObject - Collection of controler.
# @return a tuple (first Key, last key), False if there is no key on selection.
def getFirstAndLastKey(controlers):

    playcontrol = xsi.GetValue("PlayControl")
    currentFrame = playcontrol.Parameters("Current").Value

    keyableParams = controlers.FindObjectsByMarkingAndCapabilities(None, 2048)
    firstKey = xsi.FirstKey(keyableParams)
    lastKey = xsi.LastKey(keyableParams)

    playcontrol.Parameters("Current").Value = currentFrame

    if lastKey < firstKey:
        return False

    return (firstKey, lastKey)
