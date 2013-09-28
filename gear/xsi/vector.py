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

## @package gear.xsi.vector
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import math

# SN
from gear.xsi import xsi, c, XSIMath
import gear.xsi.log as log

import gear.xsi.xmldom as xsixmldom

##########################################################
# VECTORS
##########################################################
# getDistance ============================================
## Get the distance between two positions.
# @param v0 SIVector3 - First position.
# @param v1 SIVector3 - Second position.
# @return Double - The distance.
def getDistance(v0, v1):

    distance = XSIMath.CreateVector3()
    distance.Sub(v0, v1)

    return distance.Length()

# getDistance2 ===========================================
## Get the distance between two objects.
# @param obj0 X3DObject - First object.
# @param obj1 X3DObject - Second object.
# @return Double - The distance.
def getDistance2(obj0, obj1):

    v0 = obj0.Kinematics.Global.Transform.Translation
    v1 = obj1.Kinematics.Global.Transform.Translation

    return getDistance(v0, v1)

# Triangle ===============================================
def trigo_opp(hypotenuse, a):
    return math.cos(a) * hypotenuse

def trigo_adj(hypotenuse, a):
    return math.sin(a) * hypotenuse

def getDistanceToAxe(pos, axe_pos0, axe_pos1):

    axe = XSIMath.CreateVector3()
    axe.Sub(axe_pos1, axe_pos0)

    hyp = XSIMath.CreateVector3()
    hyp.Sub(pos, axe_pos0)

    a = axe.Angle(hyp)

    distance = trigo_adj(hyp.Length(), a)

    return distance

def getOrthocentre(v0, v1, v2):

    axe = XSIMath.CreateVector3()
    axe.Sub(v2, v0)

    hyp = XSIMath.CreateVector3()
    hyp.Sub(v1, v0)

    a = axe.Angle(hyp)

    distance = trigo_opp(hyp.Length(), a)

    axe.NormalizeInPlace()
    axe.ScaleInPlace(distance)
    axe.AddInPlace(v0)

    return axe

def getOrthocentreDistances(v0, v1, v2):

    axe = XSIMath.CreateVector3()
    axe.Sub(v2, v0)

    hyp = XSIMath.CreateVector3()
    hyp.Sub(v1, v0)

    a = axe.Angle(hyp)

    distanceA = trigo_opp(hyp.Length(), a)
    distanceB = axe.Length() - distanceA

    return distanceA, distanceB

# linearlyInterpolate ====================================
## Get a vector that is the interpolation of the two input vector.\n
# This method is not limitied to a 0-1
# @param v0 SIVector3 - First position.
# @param v1 SIVector3 - Second position.
# @param blend Double - Blend between the two vectors. (0 return the first vector, 1 return the second vector)
# @return SIVector3 - The interpolated vector.
def linearlyInterpolate(v0, v1, blend=.5):

    vector = XSIMath.CreateVector3()
    vector.Sub(v1, v0)
    vector.ScaleInPlace(blend)
    vector.AddInPlace(v0)

    return vector

# rotateVectorAlongAxis ==================================
## Get a vector that is the rotation of first vector along an axis. Angle must be in radians.
# @param v SIVector3 - Vector to transform.
# @param axis SIVector3 - Vector use as axes.
# @param a Double - Angle in radians.
# @return SIVector3 - The newly created vector.
def rotateVectorAlongAxis(v, axis, a=0):
    # Angle as to be in radians

    sa = math.sin(a / 2.0)
    ca = math.cos(a / 2.0)

    q1 = XSIMath.CreateQuaternion(0, v.X, v.Y, v.Z)
    q2 = XSIMath.CreateQuaternion(ca, axis.X * sa, axis.Y * sa, axis.Z * sa)
    q2n = XSIMath.CreateQuaternion(ca, -axis.X * sa, -axis.Y * sa, -axis.Z * sa)

    q = XSIMath.CreateQuaternion()
    q.Mul(q2, q1)
    q.MulInPlace(q2n)

    vector = XSIMath.CreateVector3(q.X, q.Y, q.Z)

    return vector

# getPlaneNormal ===================================
## Get the normal vector of a plane (Defined by 3 positions).
# @param v0 SIVector3 - First position on the plane.
# @param v1 SIVector3 - Second position on the plane.
# @param v2 SIVector3 - Third position on the plane.
# @return SIVector3 - The normal.
def getPlaneNormal(v0, v1, v2):

    vector0 = XSIMath.CreateVector3()
    vector1 = XSIMath.CreateVector3()

    vector0.Sub(v1, v0)
    vector1.Sub(v2, v0)

    vector0.NormalizeInPlace()
    vector1.NormalizeInPlace()

    normal = XSIMath.CreateVector3()

    normal.Cross(vector1, vector0)
    normal.NormalizeInPlace()

    return normal

# getPlaneBiNormal =================================
## Get the binormal vector of a plane (Defined by 3 positions).
# @param v0 SIVector3 - First position on the plane.
# @param v1 SIVector3 - Second position on the plane.
# @param v2 SIVector3 - Third position on the plane.
# @return SIVector3 - The binormal.
def getPlaneBiNormal(v0, v1, v2):

    normal = getPlaneNormal(v0, v1, v2)

    vector0 = XSIMath.CreateVector3()
    vector0.Sub(v1, v0)

    biNormal = XSIMath.CreateVector3()

    biNormal.Cross(normal, vector0)
    biNormal.NormalizeInPlace()

    return biNormal

# getBladeNormal ===================================
## Get the normal vector of a blade. A Blade is a 3 points curve that define a plane.
# @param blade NurbCurve.
# @return SIVector3 - The normal.
def getBladeNormal(blade):

    geometry = blade.ActivePrimitive.Geometry
    t = blade.Kinematics.Global.Transform

    points = [XSIMath.MapObjectPositionToWorldSpace(t, geometry.Points(i).Position) for i in range(3)]

    normal = getPlaneNormal(points[0], points[1], points[2])

    return normal

def getBladeNormalFromXml(xml_def):

    xNurbsCurveList = xsixmldom.NurbsCurveList(xml_def)
    t = xNurbsCurveList.globalTransform
    p = xNurbsCurveList.getPointArray()

    points = []

    for i in range(3):
        v = XSIMath.CreateVector3(p[i*3+0], p[i*3+1], p[i*3+2])
        points.append(XSIMath.MapObjectPositionToWorldSpace(t, v) )

    normal = getPlaneNormal(points[0], points[1], points[2])

    return normal

# getBladeBiNormal ================================
## Get the binormal vector of a blade. A Blade is a 3 points curve that define a plane.
# @param blade NurbCurve.
# @return SIVector3 - The binormal.
def getBladeBiNormal(blade):

    geometry = blade.ActivePrimitive.Geometry
    t = blade.Kinematics.Global.Transform

    points = []

    for i in range(3):
        points.append(XSIMath.MapObjectPositionToWorldSpace(t, geometry.Points(i).Position) )

    biNormal = getPlaneBiNormal(points[0], points[1], points[2])

    return biNormal

def getBladeBiNormalFromXml(xml_def):

    xNurbsCurveList = xsixmldom.NurbsCurveList(xml_def)
    t = xNurbsCurveList.globalTransform
    p = xNurbsCurveList.getPointArray()

    points = []

    for i in range(3):
        v = XSIMath.CreateVector3(p[i*3+0], p[i*3+1], p[i*3+2])
        points.append(XSIMath.MapObjectPositionToWorldSpace(t, v) )

    normal = getPlaneBiNormal(points[0], points[1], points[2])

    return normal

# getTransposedVector ==============================
## Get the transposed vector.
# @param v SIVector - vector to transpose.
# @param position0 SIVector - original position.
# @param position1 SIVector - new position.
# @param inverse Boolean - True to inverse the orientation.
# @return SIVector3 - The transposed vector.
def getTransposedVector(v, position0, position1, inverse=False):

    v0 = XSIMath.CreateVector3()
    v0.Sub(position0[1], position0[0])
    v0.NormalizeInPlace()

    v1 = XSIMath.CreateVector3()
    v1.Sub(position1[1], position1[0])
    v1.NormalizeInPlace()

    ra = v0.Angle(v1)

    if inverse:
        ra = -ra

    axis = XSIMath.CreateVector3()
    #axis.Cross(v, v0)
    axis.Cross(v0, v1)

    r = XSIMath.CreateRotation()
    r.SetFromAxisAngle(axis, ra)

    vector = XSIMath.CreateVector3()
    vector.MulByRotation(v, r)

    # Check if the rotation has been set in the right order
    ra2 = (math.pi *.5 ) - v1.Angle(vector)
    r.SetFromAxisAngle(axis, -ra2)
    vector.MulByRotationInPlace(r)

    return vector

# getDegreeAngleFromPlane ==============================
## Get the transposed vector.
# @param positions0 List of SIVector - first plane position.
# @param positions1 List of SIVector - second plane position.
# @return Double - Angle In Degree.
def getDegreeAngleFromPlane(positions0, positions1):

    normal0 = getPlaneNormal(positions0[0], positions0[1], positions0[2])
    normal1 = getPlaneNormal(positions1[0], positions1[1], positions1[2])

    angle_radians = normal0.Angle(normal1)
    angle_degrees = math.degrees(angleInRadian)

    # Is it sure enough ?
    if normal0.Z < normal1.Z:
        angle_degrees *= -1

    return angle_degrees

# drawVector ===========================================
## Help method to draw a curve that represent a vector.
# @param vector SIVector - vector to draw.
# @param name String - name of the vector.
# @param parent XSI3DObject - parent object. (Used to move a vector at the position of an object).
# @return NUrbCurve - The curve that represent the vector.
def drawVector(vector, name="vector", parent=xsi.ActiveSceneRoot):

    points = [0,0,0,1,vector.X, vector.Y, vector.Z, 1]

    curve = xsi.ActiveSceneRoot.AddNurbsCurve(points, None, False, 1, c.siNonUniformParameterization, c.siSINurbs, name)
    log.logVector(vector, "draw "+curve.Name+" : ")

    t = XSIMath.CreateTransform()
    t.SetTranslation(parent.Kinematics.Global.Transform.Translation)
    curve.Kinematics.Global.Transform = t

    return curve

class Blade(object):

    def __init__(self, ref):

        if str(type(ref)) == "<type 'Element'>":
            self.normal = getBladeNormalFromXml(ref)
            self.binormal = getBladeBiNormalFromXml(ref)
        else:
            self.normal = getBladeNormal(ref)
            self.binormal = getBladeBiNormal(ref)



##########################################################
# CLASS
##########################################################
# ========================================================
class Blade(object):

    def __init__(self, t=XSIMath.CreateTransform()):

        self.transform = t

        self.x = XSIMath.CreateVector3(1,0,0)
        self.y = XSIMath.CreateVector3(0,1,0)
        self.z = XSIMath.CreateVector3(0,0,1)

        self.x.MulByRotationInPlace(t.Rotation)
        self.y.MulByRotationInPlace(t.Rotation)
        self.z.MulByRotationInPlace(t.Rotation)
