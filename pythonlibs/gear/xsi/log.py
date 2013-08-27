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

## @package gear.xsi.log
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, XSIMath

##########################################################
# Change Log
##########################################################
# setMsgLog ==============================================
## Set the message log to given value
# @param b Boolean - Value to set the message log.
# @return the original value of the parameter.
def setMsgLog(b):

    bLog = xsi.Preferences.Categories("Scripting").Parameters("msglog").Value
    xsi.Preferences.Categories("Scripting").Parameters("msglog").Value = b

    return bLog

# setCmdLog ==============================================
## Set the command log to given value
# @param b Boolean - Value to set the message log.
# @return the original value of the parameter.
def setCmdLog(b):

    bLog = xsi.Preferences.Categories("Scripting").Parameters("cmdlog").Value
    xsi.Preferences.Categories("Scripting").Parameters("cmdlog").Value = b

    return bLog

##########################################################
# LOG
##########################################################
# Log Vector =============================================
## Log vector values and length
# @param v SIVector3 - Vector to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logVector(v, msg="v"):

    gear.log(msg + "[ x : " + str(v.X) + " | y : " + str(v.Y) + " | z : " + str(v.Z) +" ] - Length : "+str(v.Length()))

# Log Matrix 4 ===========================================
## Log matrix 4 values
# @param m Matrix4 - Matrix 4 to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logMatrix4(m, msg="matrix4"):

    s = msg + " : \n"\
	+"| %s , %s , %s , %s |\n"%(m.Value(0,0), m.Value(0,1), m.Value(0,2), m.Value(0,3))\
	+"| %s , %s , %s , %s |\n"%(m.Value(1,0), m.Value(1,1), m.Value(1,2), m.Value(1,3))\
	+"| %s , %s , %s , %s |\n"%(m.Value(2,0), m.Value(2,1), m.Value(2,2), m.Value(2,3))\
	+"| %s , %s , %s , %s |"%(m.Value(3,0), m.Value(3,1), m.Value(3,2), m.Value(3,3))

    gear.log(s)

# Log Matrix 4 ===========================================
## Log matrix 4 values as Scaling, Rotation, Translation values.
# @param m Matrix4 - Matrix 4 to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logMatrix4AsSRT(m, msg="matrix4"):

    t = XSIMath.CreateTransform()
    t.SetMatrix4(m)

    vScl = t.Scaling
    vRot = t.Rotation.XYZAngles
    vRot.Set(XSIMath.RadiansToDegrees(vRot.X), XSIMath.RadiansToDegrees(vRot.Y), XSIMath.RadiansToDegrees(vRot.Z))
    vPos = t.Translation

    logVector(vScl, msg + " S")
    logVector(vRot, msg + " R")
    logVector(vPos, msg + " T")

# Log Matrix 3 ===========================================
## Log matrix 3 values
# @param m Matrix3 - Matrix 3 to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logMatrix3(m, msg="matrix3"):

    s = msg + " : \n"\
	+"| %s , %s , %s |\n"%(m.Value(0,0), m.Value(0,1), m.Value(0,2))\
	+"| %s , %s , %s |\n"%(m.Value(1,0), m.Value(1,1), m.Value(1,2))\
	+"| %s , %s , %s |"%(m.Value(2,0), m.Value(2,1), m.Value(2,2))

    gear.log(s)

# Log Matrix 3 ===========================================
## Log matrix 3 values as XYZ angles
# @param m Matrix3 - Matrix 3 to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logMatrix3AsAngles(m, msg="matrix3"):

    r = XSIMath.CreateRotation()
    r.SetFromMatrix3(m)
    v = r.XYZAngles

    logVector(v, msg)

# Log Rotation as Matrix 3 ===============================
## Log rotation as matrix 3
# @param r SIRotation - Rotation to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logRotationAsMatrix3(r, msg="rotation"):

    m = XSIMath.CreateMatrix3()
    r.GetMatrix3(m)

    logMatrix3(m, msg)

# Log Rotation as Angles ===============================
## Log rotation as XYZ Angles
# @param r SIRotation - Rotation to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logRotationAsAngles(r, msg="rotation"):

    m = XSIMath.CreateMatrix3()
    r.GetMatrix3(m)

    logMatrix3AsAngle(m, msg)

# Log Rotation as Quaternion =========================
## Log rotation as Quaternion
# @param r SIRotation - Rotation to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logRotationAsQuaternion(r, msg="rotation"):

    logQuaternion(r.Quaternion, msg)

# Log  Quaternion ===================================
## Log quaternion values
# @param q SIQuaternion - Quaternion to log.
# @param msg String - Message to add to the log to identify it.
# @return
def logQuaternion(q, msg="quaternion"):

    gear.log(msg + "[ w : " + str(q.W) +" | x : " + str(q.X) + " | y : " + str(q.Y) + " | z : " + str(q.Z) + " ]")
