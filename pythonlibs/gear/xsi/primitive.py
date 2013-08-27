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

## @package gear.xsi.primitive
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
import math

from gear.xsi import xsi, c, XSIMath, Dispatch

import gear

import gear.xsi.vector as vec
import gear.xsi.transform as tra
import gear.xsi.icon as icon
import gear.xsi.utils as uti
import gear.xsi.xmldom as xsixmldom
import gear.xsi.curve as cur
import gear.xsi.parameter as par
import gear.xsi.geometry as geo

##########################################################
#
##########################################################
# ========================================================
def generateFromXml(parent, name, xml_def, color):

    if str(type(xml_def)) != "<type 'Element'>":
        gear.log("Invalid input", gear.sev_error)
        return False

    xObject = xsixmldom.xmlToObject(xml_def)
    obj = xObject.generateObject(parent)
    obj.Name = name

    uti.setColor(obj, color)

    return obj

##########################################################
# NULL
##########################################################
## Create a null with a given transform and size.
# @param parent X3DObject - Parent object.
# @param name String - Null name.
# @param t SITransformation - Null global transform.
# @param size Double - Null display size.
# @return Null - The newly created null.
def addNull(parent, name, t=XSIMath.CreateTransform(), size=1, color=[0,0,0]):

    null = parent.AddNull(name)

    null.Parameters("Size").Value = max(size, .01)
    null.Kinematics.Global.Transform = t

    uti.setColor(null, color)

    return null

# ========================================================
## Create a null with a given position and size.
# @param parent X3DObject - Parent object.
# @param name String - Null name.
# @param position SIVector3 - Null global position.
# @param size Double - Null display size.
# @return Null - The newly created null.
def addNullFromPos(parent, name, position=XSIMath.CreateVector3(), size=1, color=[0,0,0]):

    t = XSIMath.CreateTransform()
    t.SetTranslation(position)

    null = addNull(parent, name, t, size, color)

    return null
    
    
# ========================================================
## Create a nulls with a given position list .
# @param parent X3DObject - Parent object.
# @param name String - Null name.
# @param positions List of SiVector3 - Positions of the controlers.
# @param rot_off SIRotation - Rotation offset.
# @param size Double - Null display size.
# @return Null - The newly created null.
def addNullsFromPositions(parent, name, positions, rot_offset=XSIMath.CreateRotation() , size=1, color=[0,0,0]):
    # Name
    if "#" in name:
        name = name.replace("#", "%s")
    else:
        name += "%s"
        
    nullList = []
    i = 0
    for x in positions:
        t = tra.getTransformFromPosition(x)
        t.SetRotation(rot_offset)
        #t = tra.getTransformLookingAt(x, lookat, normal, axis, negate)

        null = addNull(parent, name%i, t, size, color)
        nullList.append(null)
        i +=1
    return nullList

# ========================================================
## Set the display of a Null.
# @param null X3DObject - Null object.
# @param pri_icon Integer - Null primary icon.
# @param size Double - Null display size.
# @param shd_icon Integer - Null shadow icon.
# @param shd_offx Double - Null shadow offset position X.
# @param shd_offy Double - Null shadow offset position Y.
# @param shd_offz Double - Null shadow offset position Z.
# @param shd_sclx Double - Null shadow offset scaling X.
# @param shd_scly Double - Null shadow offset scaling Y.
# @param shd_sclz Double - Null shadow offset scaling Z.
# @param color List of Double - The RGB color of the Null (ie. [1,0,0] for red)
# @return
def setNullDisplay(null, pri_icon=None, size=None, shd_icon=None, shd_offx=None, shd_offy=None, shd_offz=None, shd_sclx=None, shd_scly=None, shd_sclz=None, color=None):

    params = ["primary_icon", "size", "shadow_icon", "shadow_offsetX", "shadow_offsetY", "shadow_offsetZ", "shadow_scaleX", "shadow_scaleY", "shadow_scaleZ"]
    values = [pri_icon, size, shd_icon, shd_offx, shd_offy, shd_offz, shd_sclx, shd_scly, shd_sclz]

    for param, value in zip(params, values):
        if value is not None:
            null.ActivePrimitive.Parameters(param).Value = value

    if color is not None:
        uti.setColor(null, color)

##########################################################
# Axis
##########################################################
# ========================================================
def drawAxis(parent=xsi.ActiveSceneRoot, size=1):

     x_crv = cur.addCurve(parent, parent.Name+"_x", [0,0,0,1,size,0,0,1], False, 1, parent.Kinematics.Global.Transform, [1,0,0])
     y_crv = cur.addCurve(parent, parent.Name+"_y", [0,0,0,1,0,size,0,1], False, 1, parent.Kinematics.Global.Transform, [0,1,0])
     z_crv = cur.addCurve(parent, parent.Name+"_z", [0,0,0,1,0,0,size,1], False, 1, parent.Kinematics.Global.Transform, [0,0,1])

     return [x_crv, y_crv, z_crv]

##########################################################
# IMPLICITE
##########################################################
# ========================================================
## Create an implicite with a given transform and size.
# @param parent X3DObject - Parent object.
# @param preset String - Implicite type (ie. Cube, Cone, Sphere...).
# @param name String - Name.
# @param t SITransformation - Global transform.
# @param size Double - Display size.
# @return Implicite - The newly created implicite.
def addImplicite(parent, preset, name, t=XSIMath.CreateTransform(), size=1):

    implicite = parent.AddPrimitive(preset, name)

    implicite.Parameters("length").Value = max(size, .01)
    implicite.Kinematics.Global.Transform = t

    return implicite

##########################################################
# BONE
##########################################################
# ========================================================
## Create a bone with a given transform and length.
# @param parent X3DObject - Parent object.
# @param name String - Name.
# @param t SITransformation - Global transform.
# @param length Double - Display size.
# @return Implicite - The newly created implicite.
def addBone(parent, name, t=XSIMath.CreateTransform(), length=1):

    bone = addImplicite(parent, "Bone", name, t, length)

    return bone

# ========================================================
## Create a bone with a given position and length.
# @param parent X3DObject - Parent object.
# @param name String - Name.
# @param position SIVector3 - Global position.
# @param length Double - Display size.
# @return Implicite - The newly created implicite.
def addBoneFromPos(parent, name, position=XSIMath.CreateVector3(), length=1):

     t = XSIMath.CreateTransform()
     t.SetTranslation(position)

     bone = addBone(parent, name, t, length)

     return bone

##########################################################
# CHAINS
##########################################################
# ========================================================
def add2DChain(parent, name, positions, normal=None, negate=False, size=1, alignRoot=False):

    if size < 0.05:
        size = 0.05

    # Compute Normal --------
    if normal is None:
        if len(positions) >= 3:
            normal = vector.computePlaneNormal(positions[0], positions[1], positions[2])
        else:
            normal = XSIMath.CreateVector3(0,0,-1)

    # Draw -------------------
    root = parent.Add2DChain(positions[0], positions[1], normal, c.si2DChainNormalRadian)
    for i in range(len(positions)-2):
        root.AddBone(positions[i+2])

    xChain = Chain(root, name)

    # Negative Scaling -------
    for bone in xChain.bones:

        bone.size.Value = size

        if negate:
            bone.axisz = 180

        #xsi.SetNeutralPose(bone)

    if negate:
        xChain.bones[0].Properties("kinematic chain").Parameters("effori_offz").Value = 180

    # Display ----------------
    xChain.root.Size = size * .25
    xChain.eff.Size = size * .125

    # !!! This can be trouble !!!
    # !!! OUT OF FOCUS BUG !!!
    # Using this command gives weird result when the focus is not on XSI
    # xsi.AlignRootToFirstBone(root)
    if alignRoot:
        alignRootToFirstBone(xChain)

    return xChain

def alignRootToFirstBone(xChain):

    t = XSIMath.CreateTransform()
    t.SetTranslation(xChain.root.Kinematics.Global.Transform.Translation)
    t.SetRotation(xChain.bones[0].Kinematics.Global.Transform.Rotation)
    xChain.root.Kinematics.Global.Transform = t

    t = XSIMath.CreateTransform()
    xChain.bones[0].Kinematics.Local.Transform = t

# ========================================================
## Create a chain of null
# Used to create chain of fk controlers.
# @param parent X3DObject - Parent object.
# @param name String - Name.
# @param positions List of SiVector3 - Positions of the controlers.
# @param normal SIVector3 - Normal vector. (Z axes)
# @param negate Boolean - Create a chain for negative side. (-X axes pointing forward)
# @param size Double - Display size.
# @return List of Null - The newly created chain.
def addNullChain(parent, name, positions, normal, negate=False, size=1):

    # Name
    if "#" in name:
        name = name.replace("#", "%s")
    else:
        name += "%s"

    # Draw
    bones = []
    for i in range(len(positions)-1):
        v0 = positions[i-1]
        v1 = positions[i]
        v2 = positions[i+1]

        # Normal Offset
        if i > 0:
            normal = vec.getTransposedVector(normal, [v0, v1], [v1, v2])

        t = tra.getTransformLookingAt(v1, v2, normal, "xy", negate)

        # Cube Offset
        d = vec.getDistance(v1, v2)
        offset = XSIMath.CreateVector3(d*.5, 0, 0)

        if negate:
            offset.NegateInPlace()

        # Draw
        bone = addNull(parent, name%i, t, size)

        bones.append(bone)
        parent = bone

    return bones

## Create a chain of fk controlers (icon.cube).
# @param parent X3DObject - Parent object.
# @param name String - Name.
# @param positions List of SIVector3 - positions of the curve points.
# @param normal SIVector3 - normal direction.
# @param negate Boolean - True to create a negative scale chain.
# @param size Float - Size of the controlers.
# @param color List of Double - The RGB color of the object (ie. [1,0,0] for red).
# @return List of NurbCurve - The newly created curve.
def addCubeChain(parent, name, positions, normal, negate=False, size=1, color=[0,0,0]):

    # Name
    if "#" in name:
        name = name.replace("#", "%s")
    else:
        name += "%s"

    # Draw
    bones = []
    for i in range(len(positions)-1):
        v0 = positions[i-1]
        v1 = positions[i]
        v2 = positions[i+1]

        # Normal Offset
        if i > 0:
            normal = vec.getTransposedVector(normal, [v0, v1], [v1, v2])

        t = tra.getTransformLookingAt(v1, v2, normal, "xy", negate)

        # Cube Offset
        d = vec.getDistance(v1, v2)
        offset = XSIMath.CreateVector3(d*.5, 0, 0)

        if negate:
            offset.NegateInPlace()

        # Draw
        bone = icon.cube(parent, name%i, d, size, size, color, t, offset)

        bones.append(bone)
        parent = bone

    return bones

# ========================================================
def addLattice(parent, name, t=XSIMath.CreateTransform(), subd=[4,4,4], size=[1,1,1]):

    lattice = parent.AddPrimitive("Lattice", name)
    
    lattice.Kinematics.Global.Transform = t
    for i, s in enumerate("xyz"):
        lattice.Parameters("subdiv%s"%s).Value = subd[i]
        lattice.Parameters("size%s"%s).Value = size[i]
        
    return lattice
    
# ========================================================
class Chain(object):

    def __init__(self, root=None, name="chain"):

        if root.type != "root":
            gear.log( "chain Init : Invalid object specified", gear.sev_warning )
            return False

        self.root = root

        self.setDisplay()
        self.setName(name)

    # Methods ---------------------------------------------
    def setName(self, name=None):

        if "#" in name:
            name = name.replace("#", "%s")
        else:
            name += "%s"

        self.root.Name = name%("_chn")
        for i, bone in enumerate(self.bones):
            bone.Name = name%("_"+str(i)+"_bone")
        self.eff.Name = name%("_eff")

    def setDisplay(self):
        self.root.Parameters("primary_icon").Value = 4
        self.eff.Parameters("primary_icon").Value = 2

        uti.setColor(self.root, [.75,1,.75])
        uti.setColor(self.eff, [.75,1,.75])

    # Properties ------------------------------------------
    def getEff(self):
        return self.root.Effector

    def getBones(self):
        return [bone for bone in self.root.Bones]

    def getAll(self):
        all = [self.root]
        all.extend(self.bones)
        all.append(self.eff)
        return all

    def getBlend(self):
        return self.bones[0].Properties("kinematic chain").Parameters("blendik")

    def getRoll(self):
        return self.bones[0].Properties("kinematic joint").Parameters("roll")

    def getLength(self):
        length = 0
        for bone in self.bones:
            length += bone.Length.Value
        return length

    eff = property(getEff)
    bones = property(getBones)
    all = property(getAll)
    blend = property(getBlend)
    roll = property(getRoll)
    length = property(getLength)

##########################################################
# CREATE OR RETURN
##########################################################
# ========================================================
## Create or return the gear_PSet property if one was found with the same name.
# @param obj X3DObject - Object hosting the property.
# @param name String - Name of the property.
# @return Property - sn_PSet property.
def createOrReturnPSet(obj, name):

    prop = obj.Properties(name)
    if not prop:
        prop = obj.AddProperty("gear_PSet", False, name)

    return Dispatch(prop)

# ========================================================
## Create or return group.
# @param model Model - Model hosting the group.
# @param name String - Name of the group.
# @return Group
def createOrReturnGroup(model, name):

    group = model.Groups(name)
    if not group:
        group = model.AddGroup(None, name)

    return group

##########################################################
# CLASS
##########################################################
def getPrimitive(ref):

    if str(type(ref)) == "<type 'Element'>":
        refType = ref.get("type")
    else:
        refType = ref.Type


    if refType == "null":
        return Null(ref)
    elif refType == "crvlist":
        return NurbsCurve(ref)
    else:
        return False

# ========================================================
class Primitive(object):

    def __init__(self, ref):

        # Parameters
        self.params = {}
        self.transform = {}
        self.obj = None

        if str(type(ref)) == "<type 'Element'>":
            self.xml = ref
            for xml_param in self.xml.findall("primitive/parameter"):
                self.params[xml_param.get("scriptName")] = xml_param.get("value")

        else:
            self.obj = ref
            for param in self.obj.ActivePrimitive.Parameters:
                self.params[param.scriptName] = param.Value

        self.transform = self.setTransform()

    def getAsXml(self):

        if self.obj is None:
            gear.log("Can't export primitive to xml", gear.sev_error)
            return

        xsixmldom.setOptions(X3DObject_children=False, X3DObject_properties=[], X3DObject_kinematics=True, Geometry_stack=False)
        return xsixmldom.getObject(self.obj).xml

    def setTransform(self):

        t = {}

        if self.obj is None:
            for xml_param in self.xml.findall("kinematics/global/parameter"):
                t[xml_param.get("scriptName")] = float(xml_param.get("value"))
        else:
            t["posx"] = self.obj.Kinematics.Global.Transform.PosX
            t["posy"] = self.obj.Kinematics.Global.Transform.PosY
            t["posz"] = self.obj.Kinematics.Global.Transform.PosZ
            t["rotx"] = self.obj.Kinematics.Global.Transform.RotX
            t["roty"] = self.obj.Kinematics.Global.Transform.RotY
            t["rotz"] = self.obj.Kinematics.Global.Transform.RotZ
            t["sclx"] = self.obj.Kinematics.Global.Transform.SclX
            t["scly"] = self.obj.Kinematics.Global.Transform.SclY
            t["sclz"] = self.obj.Kinematics.Global.Transform.SclZ

        return t

    def getTransform(self):

        t = XSIMath.CreateTransform()
        t.SetTranslationFromValues(float(self.transform["posx"]),
                                   float(self.transform["posy"]),
                                   float(self.transform["posz"]))

        t.SetRotationFromXYZAnglesValues(math.radians(float(self.transform["rotx"])),
                                         math.radians(float(self.transform["roty"])),
                                         math.radians(float(self.transform["rotz"])))

        t.SetScalingFromValues(float(self.transform["sclx"]),
                               float(self.transform["scly"]),
                               float(self.transform["sclz"]))

        return t

# ========================================================
class Null(Primitive):

    def create(self, parent, name, t=None, color=[0,0,0]):

        if t is None:
            t = self.getTransform()

        obj = addNull(parent, name, t)
        setNullDisplay(obj, self.params["primary_icon"], self.params["size"], self.params["shadow_icon"],
                            self.params["shadow_offsetX"], self.params["shadow_offsetY"], self.params["shadow_offsetZ"],
                            self.params["shadow_scaleX"], self.params["shadow_scaleY"], self.params["shadow_scaleZ"],
                            color)

        return obj

    def match(self, obj):

        setNullDisplay(obj, self.params["primary_icon"], self.params["size"], self.params["shadow_icon"],
                            self.params["shadow_offsetX"], self.params["shadow_offsetY"], self.params["shadow_offsetZ"],
                            self.params["shadow_scaleX"], self.params["shadow_scaleY"], self.params["shadow_scaleZ"])

# ========================================================
class NurbsCurve(Primitive):

    def __init__(self, ref):

        self.curves = {"cp":[], "ncp":[], "kn":[], "nkn":[], "closed":[], "degree":[]}
        self.obj = None

        if str(type(ref)) == "<type 'Element'>":
            self.xml = ref
            for xml_curve in self.xml.findall("primitive/curve"):
                self.curves["cp"].extend([float(s) for s in xml_curve.get("cp").split(",")])
                self.curves["ncp"].append(int(xml_curve.get("ncp")))
                self.curves["kn"].extend([float(s) for s in xml_curve.get("kn").split(",")])
                self.curves["nkn"].append(int(xml_curve.get("nkn")))
                self.curves["closed"].append(par.convertVariantType(xml_curve.get("closed"), c.siBool))
                self.curves["degree"].append(int(xml_curve.get("degree")))
        else:
            self.obj = ref
            for curves in self.obj.ActivePrimitive.Geometry.Curves:
                self.curves["cp"].extend([t[i] for i in range(len(curves.ControlPoints.Array[0])) for t in curves.ControlPoints.Array])
                self.curves["ncp"].append(len(curves.ControlPoints.Array[0]))
                self.curves["kn"].extend(curves.Knots.Array)
                self.curves["nkn"].append(len(curves.Knots.Array))
                self.curves["closed"].append(cur.isClosed(curves))
                self.curves["degree"].append(curves.Degree)

        self.transform = self.setTransform()

    def create(self, parent, name, t=None, color=[0,0,0]):

        if t is None:
            t = self.getTransform()

        if len(self.curves["closed"]) == 1:
            obj = cur.addCurve(parent, name, self.curves["cp"], self.curves["closed"][0], self.curves["degree"][0], t, color)
        else:
            obj = cur.addCurve2(parent, name, self.curves["cp"], self.curves["ncp"], self.curves["kn"], self.curves["nkn"], self.curves["closed"], self.curves["degree"], t, color)

        return obj

    def match(self, obj):

        if geo.isFrozen(obj):
            obj.ActivePrimitive.Geometry.ControlPoints.Array = self.curves["cp"]

