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

## @package gear.xsi.transform
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, XSIMath

import gear.xsi.vector as vec

##########################################################
# TRANSFORM
##########################################################
# getTransformLookingAt ==================================
## Get a transform that is oriented looking at another position.
# @param position SIVector3 - The position of the object.
# @param lookAtPos SIVector3 - The position that the object is looking at.
# @param upv SIVector3 - Up vector direction.
# @param negate Boolean - True to create negative side transform.
# @param axis String - First the axis point at the look at position then the axe pointing to the up vector ("xy", "xz", "yx", "yz", "zx", "zy")
# @return SITransformation - The newly created transform.
def getTransformLookingAt(position, lookat, normal, axis="xy", negate=False):

    a = XSIMath.CreateVector3()
    a.Sub(lookat, position)

    r = getRotationFromAxis(a, normal, axis, negate)

    t = XSIMath.CreateTransform()
    t.SetTranslation(position)
    t.SetRotation(r)

    return t

# ===========================================================
def getChainTransform(positions, normal, negate=False):

    # Draw
    transforms = []
    for i in range(len(positions)-1):
        v0 = positions[i-1]
        v1 = positions[i]
        v2 = positions[i+1]

        # Normal Offset
        if i > 0:
            normal = vec.getTransposedVector(normal, [v0, v1], [v1, v2])

        t = getTransformLookingAt(v1, v2, normal, "xz", negate)
        transforms.append(t)

    return transforms

# getGlobalPositionFromObjects ==============================
## Get the global translation of each object in list or collection.
# @param collection List of X3DObject or XSICollection.
# @return List of SIVector3 - The global translation.
def getGlobalPositionFromObjects(collection):

     return [obj.Kinematics.Global.Transform.Translation for obj in collection]

# getTransformFromPos ======================================
## Get a SITransformation with translation equal the given position.
# @param position SIVector3 - The position
# @return SITransformatin - The newy created transform
def getTransformFromPosition(position):

     t = XSIMath.CreateTransform()
     t.SetTranslation(position)

     return t

# getSymmetricalTransform ===================================
## Get the SITransformation.
# @param t SITransformation - The transform to symmetrize.
# @param axis SIVector3 - Mirroring axis.
# @return SITransformatin - The newy created transform
def getSymmetricalTransform(t, axis="yz"):

    if axis == "yz":
        t.PosX *= -1
        t.RotZ *= -1
        t.RotY *= -1
    elif axis == "xy":
        t.PosZ *= -1
        t.RotX *= -1
        t.RotY *= -1
    elif axis == "zx":
        t.PosY *= -1
        t.RotZ *= -1
        t.RotX *= -1

    return t

def getSymmetricalTransform2(t, axis="yz"):

    m = t.Matrix4

    if axis == "yz":
        mirror = XSIMath.CreateMatrix4(-1,0,0,0,
                                        0,1,0,0,
                                        0,0,1,0,
                                        0,0,0,1)
    elif axis == "xy":
        mirror = XSIMath.CreateMatrix4(1,0,0,0,
                                       0,1,0,0,
                                       0,0,-1,0,
                                       0,0,0,1)
    elif axis == "zx":
        mirror = XSIMath.CreateMatrix4(1,0,0,0,
                                       0,-1,0,0,
                                       0,0,1,0,
                                       0,0,0,1)

    m.MulInPlace(mirror)

    if axis == "yz":
        m.Set(m.Value(0,0), m.Value(0,1), m.Value(0,2), m.Value(0,3),
              m.Value(1,0), m.Value(1,1), m.Value(1,2), m.Value(1,3),
             -m.Value(2,0), -m.Value(2,1), -m.Value(2,2), m.Value(2,3),
              m.Value(3,0), m.Value(3,1), m.Value(3,2), m.Value(3,3))

    elif axis == "xy":
        m.Set(m.Value(0,0), m.Value(0,1), m.Value(0,2), m.Value(0,3),
             -m.Value(1,0), -m.Value(1,1), -m.Value(1,2), m.Value(1,3),
              m.Value(2,0), m.Value(2,1), m.Value(2,2), m.Value(2,3),
              m.Value(3,0), m.Value(3,1), m.Value(3,2), m.Value(3,3))

    elif axis == "zx":
        m.Set(-m.Value(0,0), -m.Value(0,1), -m.Value(0,2), m.Value(0,3),
               m.Value(1,0), m.Value(1,1), m.Value(1,2), m.Value(1,3),
               m.Value(2,0), m.Value(2,1), m.Value(2,2), m.Value(2,3),
               m.Value(3,0), m.Value(3,1), m.Value(3,2), m.Value(3,3))

    t.Matrix4 = m

    return t

# matchGlobalTransform =====================================
## Math the global transformation of target object to source.
# @param target X3DObject - Target object. The one we apply the new transform to.
# @param source X3DObject - Source object.
# @param translation Boolean - True to match translation.
# @param rotation Boolean - True to match rotation.
# @param scaling Boolean - True to match scaling.
def matchGlobalTransform(target, source, translation=True, rotation=True, scaling=True):

     t = target.Kinematics.Global.Transform
     if translation:
          t.SetTranslation(source.Kinematics.Global.Transform.Translation)
     if rotation:
          t.SetRotation(source.Kinematics.Global.Transform.Rotation)
     if scaling:
          t.SetScaling(source.Kinematics.Global.Transform.Scaling)

     target.Kinematics.Global.Transform = t

# filterTransform ==========================================
## Retrieve a transformation filtered.
# @param t SITransformation - Reference transformation.
# @param translation Boolean - True to match translation.
# @param rotation Boolean - True to match rotation.
# @param scaling Boolean - True to match scaling.
# @return SITransformation - The filtered transformation
def getFilteredTransform(t, translation=True, rotation=True, scaling=True):

    out = XSIMath.CreateTransform()

    if translation:
        out.SetTranslation(t.Translation)
    if rotation:
        out.SetRotation(t.Rotation)
    if scaling:
        out.SetScaling(t.Scaling)

    return out


def getNegatedTransform(t, axis="xy"):

    m = t.Matrix4

    if axis == "yz":
        m.Set(m.Value(0,0), m.Value(0,1), m.Value(0,2), m.Value(0,3),
             -m.Value(1,0), -m.Value(1,1), -m.Value(1,2), m.Value(1,3),
             -m.Value(2,0), -m.Value(2,1), -m.Value(2,2), m.Value(2,3),
              m.Value(3,0), m.Value(3,1), m.Value(3,2), m.Value(3,3))

    elif axis == "xy":
        m.Set(-m.Value(0,0), -m.Value(0,1), -m.Value(0,2), m.Value(0,3),
              -m.Value(1,0), -m.Value(1,1), -m.Value(1,2), m.Value(1,3),
               m.Value(2,0), m.Value(2,1), m.Value(2,2), m.Value(2,3),
               m.Value(3,0), m.Value(3,1), m.Value(3,2), m.Value(3,3))

    elif axis == "zx":
        m.Set(-m.Value(0,0), -m.Value(0,1), -m.Value(0,2), m.Value(0,3),
               m.Value(1,0), m.Value(1,1), m.Value(1,2), m.Value(1,3),
              -m.Value(2,0), -m.Value(2,1), -m.Value(2,2), m.Value(2,3),
               m.Value(3,0), m.Value(3,1), m.Value(3,2), m.Value(3,3))


    t = XSIMath.CreateTransform()

    t.Matrix4 = m

    return t

##########################################################
# KINEMATICS
##########################################################
# setRefPose =============================================
## set the reference (neutral) pose of an object. Neutral translation and scaling and neutral orientation with offset.
# @param obj X3DObject - The object.
# @param orientation List of Double - The object neutral pose orientation angles in degrees.
# @param negate Boolean - True to use with negative side.
def setRefPose(obj, orientation=[0,0,0], negate=False):

     xsi.SetNeutralPose(obj, c.siST)

     t = obj.Kinematics.Global.Transform

     if negate:
          # obj.Kinematics.Local.nrotx.Value = 90
          obj.Kinematics.Local.nrotx.Value = - orientation[0]
          obj.Kinematics.Local.nroty.Value = - orientation[1]
          obj.Kinematics.Local.nrotz.Value = - orientation[2]
     else:
          obj.Kinematics.Local.nrotx.Value = orientation[0]
          obj.Kinematics.Local.nroty.Value = orientation[1]
          obj.Kinematics.Local.nrotz.Value = orientation[2]

     obj.Kinematics.Global.Transform = t


##########################################################
# ROTATION
##########################################################
# setRefPose =============================================
def getRotationFromAxis(in_a, in_b, axis="xy", negate=False):

    a = XSIMath.CreateVector3(in_a.X, in_a.Y, in_a.Z)
    b = XSIMath.CreateVector3(in_b.X, in_b.Y, in_b.Z)
    c = XSIMath.CreateVector3()

    x = XSIMath.CreateVector3()
    y = XSIMath.CreateVector3()
    z = XSIMath.CreateVector3()

    if negate:
        a.NegateInPlace()

    a.NormalizeInPlace()
    c.Cross(a, b)
    c.NormalizeInPlace()
    b.Cross(c, a)
    b.NormalizeInPlace()

    if axis == "xy":
      x = a
      y = b
      z = c
    elif axis == "xz":
      x = a
      z = b
      y.Negate(c)
    elif axis == "yx":
      y = a
      x = b
      z.Negate(c)
    elif axis == "yz":
      y = a
      z = b
      x = c
    elif axis == "zx":
      z = a
      x = b
      y = c
    elif axis == "zy":
      z = a
      y = b
      x.Negate(c)
    else:
        gear.log("Invalid Input", gear.sev_error)
        return

    r = XSIMath.CreateRotation()
    r.SetFromXYZAxes(x,y,z)

    return r
