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

## @package gear.xsi.applyop
# @author Jeremie Passerin, Miquel Campos
#
# @brief library to easily apply operators
# This is not a UI to create operator within xsi but make the scripting easier.

##########################################################
# GLOBAL
##########################################################
# Built-in
import os

# gear
import gear
from gear.xsi import xsi, c, XSIFactory

import gear.xsi.parameter as par
import gear.xsi.fcurve as fcv

# Language global name
CPP = 0
JSCRIPT = 1
PYTHON = 2

# JScript operators path
JSOPPATH = os.path.join(os.path.dirname(__file__), "jsop")

##########################################################
# BUILT IN OPERATORS APPLY
##########################################################
# PathCns ================================================
## Apply a path constraint or curve constraint.
# @param obj X3DObject - Constrained object.
# @param curve Nurbcurve - Constraining Curve.
# @param cnsType Integer - 0 for Path Constraint ; 1 for Curve Constraint (Parametric).
# @param u Double - Position of the object on the curve (from 0 to 100 for path constraint, from 0 to 1 for Curve cns).
# @param tangent Boolean - Active tangent.
# @param upv X3DObject - Object that act as up vector.
# @param comp Boolean - Active constraint compensation.
# @return the newly created constraint.
def pathCns(obj, curve, cnsType=0, u=0, tangent=False, upv=None, comp=False):

    if cnsType == 0:
        cns = obj.Kinematics.AddConstraint("Path", curve, comp)
        cns.Parameters("perc").Value = u
    else:
        cns = obj.Kinematics.AddConstraint("Curve", curve, comp)
        if u > 1.0:
            u = 1.0
        cns.Parameters("posu").Value = u

    cns.Parameters("tangent").Value = tangent

    if upv:
        xsi.ApplyOp("UpVectorDefiner", cns.FullName+";"+upv.FullName, c.siUnspecified, c.siPersistentOperation, "", 0)
        cns.Parameters("upvct_active").Value = True

    return cns

# PoseCns ================================================
## Apply a pose constraint
# @param obj X3DObject - Constrained object.
# @param master X3DObject - Constraining Object.
# @param comp Boolean - Active constraint compensation.
# @param position - Boolean - Active position constraint.
# @param orientation - Boolean - Active orientation constraint.
# @param scaling - Boolean - Active scaling constraint.
# @return the newly created constraint.
def poseCns(obj, master, comp=False, position=True, orientation=True, scaling=True, affbyori=True, affbyscl=True):

    cns = obj.Kinematics.AddConstraint("Pose", master, comp)

    cns.Parameters("cnspos").Value = position
    cns.Parameters("cnsori").Value = orientation
    cns.Parameters("cnsscl").Value = scaling
    cns.Parameters("affbyori").Value = affbyori
    cns.Parameters("affbyscl").Value = affbyscl

    return cns
# PositionCns ================================================
## Apply a Position constraint
# @param obj X3DObject - Constrained object.
# @param master X3DObject - Constraining Object.
# @param comp Boolean - Active constraint compensation.

def positionCns(obj, master, comp=False):

    cns = obj.Kinematics.AddConstraint("Position", master, comp)

    return cns


# Obj2ClsCns ================================================
## Apply a Object to cluster constraint
# @param obj X3DObject - Constrained object.
# @param cls X3DObject - Constraining cluster.
# @param comp Boolean - Active constraint compensation.

def obj2ClsCns(obj, cls, comp=False):

    cns = obj.Kinematics.AddConstraint("ObjectToCluster", cls, comp)

    return cns

# symmetryCns ================================================
## Apply a Symmetry constraint
# @param obj X3DObject - Constrained object.
# @param master X3DObject - Constraining Object.
# @param comp Boolean - Active constraint compensation.
# @param position - Boolean - Active position constraint.
# @param orientation - Boolean - Active orientation constraint.
# @param scaling - Boolean - Active scaling constraint.
# @return the newly created constraint.
def symmetryCns(obj, master, comp=False , symplane = 2, position = True, orientation = True, scaling = True):

    cns = obj.Kinematics.AddConstraint("Symmetry", master, comp)

    cns.Parameters("cnspos").Value = position
    cns.Parameters("cnsori").Value = orientation
    cns.Parameters("cnsscl").Value = scaling
    cns.Parameters("SymmetryPlane").Value = symplane


    return cns
# ========================================================
## Apply a direction constraint
# @param obj X3DObject - Constrained object.
# @param master X3DObject - Constraining Object.
# @param upv X3DObject - None of you don't want to use up vector
# @param comp Boolean - Active constraint compensation.
# @param axis String - Define pointing axis and upvector axis
# @return the newly created constraint.
def dirCns(obj, master, upv=None, comp=False, axis="xy"):

    cns = obj.Kinematics.AddConstraint("Direction", master, comp)

    if upv is not None:
        xsi.ApplyOp("UpVectorDefiner", cns.FullName+";"+upv.FullName)
        cns.Parameters("upvct_active").Value = True

    if axis == "xy": a = [1,0,0,0,1,0]
    elif axis == "xz": a = [1,0,0,0,0,1]
    elif axis == "yx": a = [0,1,0,1,0,0]
    elif axis == "yz": a = [0,1,0,0,0,1]
    elif axis == "zx": a = [0,0,1,1,0,0]
    elif axis == "zy": a = [0,0,1,0,1,0]

    elif axis == "-xy": a = [-1,0,0,0,1,0]
    elif axis == "-xz": a = [-1,0,0,0,0,1]
    elif axis == "-yx": a = [0,-1,0,1,0,0]
    elif axis == "-yz": a = [0,-1,0,0,0,1]
    elif axis == "-zx": a = [0,0,-1,1,0,0]
    elif axis == "-zy": a = [0,0,-1,0,1,0]

    elif axis == "x-y": a = [1,0,0,0,-1,0]
    elif axis == "x-z": a = [1,0,0,0,0,-1]
    elif axis == "y-x": a = [0,1,0,-1,0,0]
    elif axis == "y-z": a = [0,1,0,0,0,-1]
    elif axis == "z-x": a = [0,0,1,-1,0,0]
    elif axis == "z-y": a = [0,0,1,0,-1,0]

    elif axis == "-x-y": a = [-1,0,0,0,-1,0]
    elif axis == "-x-z": a = [-1,0,0,0,0,-1]
    elif axis == "-y-x": a = [0,-1,0,-1,0,0]
    elif axis == "-y-z": a = [0,-1,0,0,0,-1]
    elif axis == "-z-x": a = [0,0,-1,-1,0,0]
    elif axis == "-z-y": a = [0,0,-1,0,-1,0]

    for i, name in enumerate(["dirx", "diry", "dirz", "upx", "upy", "upz"]):
        cns.Parameters(name).Value = a[i]

    return cns

# TwoPointCns ============================================
## Apply a pose constraint
# @param obj X3DObject - Constrained object.
# @param master0 X3DObject - First constraining Object.
# @param master1 X3DObject - Last constraining Object.
# @param comp Boolean - Active constraint compensation.
# @return the newly created constraint.
def twoPointsCns(obj, master0, master1, comp=False):

    masters = XSIFactory.CreateObject("XSI.Collection")
    masters.Add(master0)
    masters.Add(master1)

    cns = obj.Kinematics.AddConstraint("TwoPoints", masters, comp)

    return cns

# ClsCtrOp ===============================================
## Apply a cluster center operator
# @param obj Geometry - A Polymesh, NurbMesh or NurbCurve to be constrained.
# @param center X3DObject - Constraining Object.
# @param pointIndexes List of Integer - List of point index to constraint.
# @return the newly created operator.
def clsCtrOp(obj, center, pointIndexes):

    cluster = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "center_" + str(pointIndexes), pointIndexes)
    op = xsi.ApplyOp( "ClusterCenter", cluster.FullName+";"+center.FullName, 0, 0, None, 2)

    return op

# smoothOp ===============================================
def smoothOp(obj, pointIndexes):

    cluster = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "smooth_" + str(pointIndexes), pointIndexes)
    op = xsi.ApplyOp("Smooth", cluster.FullName, 3, c.siPersistentOperation, None, c.siConstructionModeAnimation)

    return op
# ========================================================
## Apply a chain upv operator
# @param chain X3DObject - Bone Chain to apply the Up vector.
# @param upv X3DObject - Upvector object.
# @return the newly created operator.
def chainUpvOp(chain, upv):

    op = xsi.ApplyOp( "SkeletonUpVector", chain.bones[0].FullName+";"+upv.FullName, 3, "siPersistentOperation", "", 0)
    return op

# CopyOp =================================================
## Apply a cluster center operator
# @param obj Geometry - A Polymesh, NurbMesh or NurbCurve to be constrained.
# @param ref Geometry - A Geometry of same type as previously.
# @return the newly created operator.
def copyOp(obj, ref):

    op = xsi.ApplyOp("CopyOp", ref.ActivePrimitive.FullName+","+obj.ActivePrimitive.FullName)

    return op

# Spine Point At ========================================
## Apply a SpinePointAt operator
# @param cns Constraint - The constraint to apply the operator on (must be a curve, path or direction constraint)
# @param startobj X3DObject - Start Reference.
# @param endobj X3DObject -End Reference.
# @param blend Double - Blend influence value from 0 to 1.
# @return the newly created operator.
def spinePointAtOp(cns, startobj, endobj, blend=.5):

    if cns.Parameters("tangent"):
        cns.Parameters("tangent").Value = True

    cns.Parameters("upvct_active").Value = True

    # Get In/Outputs
    sPointAtX = cns.Parameters("pointatx").FullName
    sPointAtY = cns.Parameters("pointaty").FullName
    sPointAtZ = cns.Parameters("pointatz").FullName

    sA_W = startobj.Kinematics.Global.Parameters("quatw").FullName
    sA_X = startobj.Kinematics.Global.Parameters("quatx").FullName
    sA_Y = startobj.Kinematics.Global.Parameters("quaty").FullName
    sA_Z = startobj.Kinematics.Global.Parameters("quatz").FullName

    sB_W = endobj.Kinematics.Global.Parameters("quatw").FullName
    sB_X = endobj.Kinematics.Global.Parameters("quatx").FullName
    sB_Y = endobj.Kinematics.Global.Parameters("quaty").FullName
    sB_Z = endobj.Kinematics.Global.Parameters("quatz").FullName

    # Apply Op
    s = "["+sPointAtX+","+sPointAtY+","+sPointAtZ+";"+\
      sA_W+","+sA_X+","+sA_Y+","+sA_Z+";"+\
      sB_W+","+sB_X+","+sB_Y+","+sB_Z+"]"

    op = xsi.ApplyOperator("SpinePointAt", s)

    op.Parameters("slider").Value = blend

    return op


# ========================================================
## Apply a sn_xfspring_op operator
# @param out X3DObject - constrained Object.
# @param mode Integer - 0 Scaling, 1 Rotation, 2 Translation, 3 SR, 4 RT, 5 ST, 6 SRT
# @return the newly created operator.
def sn_xfspring_op(out, mode=2):

    # Create Operator
    op = XSIFactory.CreateObject("sn_xfspring_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global)

    # Inputs
    op.AddInputPort(out.Parent3DObject.Kinematics.Global)

    # Set default values
    op.Parameters("mode").Value = mode

    # Connect
    op.Connect()

    par.addExpression(op.Parameters("fc"), "fc")

    return op

# ========================================================
## Apply a sn_rotspring_op operator
# @param out X3DObject -
# @return the newly created operator.
def sn_rotspring_op(out):

    # Create Operator
    op = XSIFactory.CreateObject("sn_rotspring_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global)

    # Inputs
    op.AddInputPort(out.Parent3DObject.Kinematics.Global)

    # Connect
    op.Connect()

    par.addExpression(op.Parameters("fc"), "fc")

    return op

# sn_ik2bone_op ==========================================
## Apply a sn_ik2bone_op operator
# @param out List of X3DObject - The constrained outputs order must be respected (BoneA, BoneB,  Center, CenterN, Eff), set it to None if you don't want one of the output.
# @param root X3DObject - Object that will act as the root of the chain.
# @param eff X3DObject - Object that will act as the eff controler of the chain.
# @param upv X3DObject - Object that will act as the up vector of the chain.
# @param lengthA Double - Length of first bone.
# @param lengthB Double - Length of second bone.
# @param negate Boolean - Use with negative Scale.
# @return the newly created operator.
def sn_ik2bone_op(out=[], root=None, eff=None, upv=None, lengthA=5, lengthB=3, negate=False):

    # Create Operator
    op = XSIFactory.CreateObject("sn_ik2bone_op")

    # Outputs
    for i, s in enumerate(["OutBoneA", "OutBoneB", "OutCenterN", "OutEff"]):
        if len(out) > i and out[i] is not None:
            port = op.AddOutputPort(out[i].Kinematics.Global, s)

    # Inputs
    op.AddInputPort(root.Kinematics.Global)
    op.AddInputPort(eff.Kinematics.Global)
    op.AddInputPort(upv.Kinematics.Global)

    # Set default values
    op.Parameters("negate").Value = negate
    op.Parameters("lengthA").Value = lengthA
    op.Parameters("lengthB").Value = lengthB

    # Connect
    op.Connect()

    return op

# ========================================================
## Apply a sn_ikfk2bone_op operator
# @param out List of X3DObject - The constrained outputs order must be respected (BoneA, BoneB,  Center, CenterN, Eff), set it to None if you don't want one of the output.
# @param root X3DObject - Object that will act as the root of the chain.
# @param eff X3DObject - Object that will act as the eff controler of the chain.
# @param upv X3DObject - Object that will act as the up vector of the chain.
# @param fk0 X3DObject - Object that will act as the first fk controler of the chain.
# @param fk1 X3DObject - Object that will act as the second fk controler of the chain.
# @param fk2 X3DObject - Object that will act as the fk effector controler of the chain.
# @param lengthA Double - Length of first bone.
# @param lengthB Double - Length of second bone.
# @param negate Boolean - Use with negative Scale.
# @param blend Double - Default blend value (0 for full ik, 1 for full fk).
# @return the newly created operator.
def sn_ikfk2bone_op(out=[], root=None, eff=None, upv=None, fk0=None, fk1=None, fk2=None, lengthA=5, lengthB=3, negate=False, blend=0, lang=CPP):

    # -----------------------------------------------------
    if lang == CPP:
        # Create Operator
        op = XSIFactory.CreateObject("sn_ikfk2bone_op")

        # Outputs
        for i, s in enumerate(["OutBoneA", "OutBoneB", "OutCenterN", "OutEff"]):
            if len(out) > i and out[i] is not None:
                op.AddOutputPort(out[i].Kinematics.Global, s)

        # Inputs
        op.AddInputPort(root.Kinematics.Global)
        op.AddInputPort(eff.Kinematics.Global)
        op.AddInputPort(upv.Kinematics.Global)
        op.AddInputPort(fk0.Kinematics.Global)
        op.AddInputPort(fk1.Kinematics.Global)
        op.AddInputPort(fk2.Kinematics.Global)

    # -----------------------------------------------------
    elif lang == JSCRIPT:

        paramDefs = []
        paramDefs.append(XSIFactory.CreateParamDef("lengthA", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 3, 0, None, 0, 10))
        paramDefs.append(XSIFactory.CreateParamDef("lengthB", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 5, 0, None, 0, 10))
        paramDefs.append(XSIFactory.CreateParamDef("negate", c.siBool, 0, c.siPersistable|c.siAnimatable, "", "", False))
        paramDefs.append(XSIFactory.CreateParamDef("blend", c.siDouble, 0, c.siPersistable |c.siAnimatable, "", "", 0, 0, 1, 0, 1))
        paramDefs.append(XSIFactory.CreateParamDef("roll", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, -360, 360, -360, 360))
        paramDefs.append(XSIFactory.CreateParamDef("scaleA", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 1, 0, None, 0, 2))
        paramDefs.append(XSIFactory.CreateParamDef("scaleB", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 1, 0, None, 0, 2))
        paramDefs.append(XSIFactory.CreateParamDef("maxstretch", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 1, 1, None, 1, 2))
        paramDefs.append(XSIFactory.CreateParamDef("softness", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, 0, None, 0, 1))
        paramDefs.append(XSIFactory.CreateParamDef("slide", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0.5, 0, 1, 0, 1))
        paramDefs.append(XSIFactory.CreateParamDef("reverse", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, 0, 1, 0, 1))

        outputPorts = [ (out[i].Kinematics.Global, name) for i, name in enumerate(["OutBoneA", "OutBoneB", "OutCenterN", "OutEff"]) if (len(out) > i and out[i] is not None) ]
        inputPorts = [ (obj.Kinematics.Global, "input_%s"%i) for i, obj in enumerate([root, eff, upv, fk0, fk1, fk2]) ]

        op = createJSOpFromFile("sn_ikfk2bone_op", os.path.join(JSOPPATH, "sn_ikfk2bone_op.js"), outputPorts, inputPorts, paramDefs)

    # -----------------------------------------------------
    # Set default values
    op.Parameters("negate").Value = negate
    op.Parameters("lengthA").Value = lengthA
    op.Parameters("lengthB").Value = lengthB
    op.Parameters("blend").Value = blend

    # Connect
    op.Connect()

    return op

# ========================================================
## Apply a sn_stretchChain_op operator
# @param root ChainRoot - Root of the chain to apply the operator to.
# @param ik_ctl X3DObject - Object that will act as the eff controler of the chain.
# @return the newly created operator.
def sn_stretchChain_op(root, ik_ctl):

    op = XSIFactory.CreateObject("sn_stretchChain_op")

    op.Parameters("rest0").Value = root.Bones(0).Length.Value
    op.Parameters("rest1").Value = root.Bones(1).Length.Value
    op.Parameters("prefrot").Value = root.Bones(1).Properties("Kinematic Joint").Parameters("prefrotz").Value

    op.AddOutputPort(root.Effector.Kinematics.Global)
    op.AddOutputPort(root.Bones(0).Length)
    op.AddOutputPort(root.Bones(1).Length)
    op.AddOutputPort(root.Bones(1).Properties("Kinematic Joint").Parameters("prefrotz"))
    op.AddInputPort(root.Kinematics.Global)
    op.AddInputPort(ik_ctl.Kinematics.Global)

    op.Connect()

    return op

# ========================================================
## Apply a sn_stretchChainMulti_op operator
# @param root ChainRoot - Root of the chain to apply the operator to.
# @param ik_ctl X3DObject - Object that will act as the eff controler of the chain.
# @return the newly created operator.
def sn_stretchChainMulti_op(root, ik_ctl):

    op = XSIFactory.CreateObject("sn_stretchChainMulti_op")

    for bone in root.Bones:
        op.Parameters("restlength").Value += bone.Length.Value

    op.AddOutputPort(root.Effector.Kinematics.Global)
    op.AddOutputPort(root.Bones(0).Kinematics.Local.Parameters("sclx"))
    op.AddInputPort(root.Kinematics.Global)
    op.AddInputPort(ik_ctl.Kinematics.Global)

    op.Connect()

    return op

# ========================================================
## Apply a sn_interLocalOri_op operator
# @param out X3DObject - constrained Object.
# @param refA X3DObject -
# @param refB X3DObject -
# @param blend Double -
# @return the newly created operator.
def sn_interLocalOri_op(out, refA, refB, blend=0):

    # Create Operator
    op = XSIFactory.CreateObject("sn_interLocalOri_op")

    # Outputs
    for s in ["rotx", "roty", "rotz", "nrotx", "nroty", "nrotz"]:
        op.AddOutputPort(out.Parameters(s), s)

    # Inputs
    op.AddInputPort(refA.Kinematics.Global)
    op.AddInputPort(refB.Kinematics.Global)
    op.AddInputPort(out.Parent.Kinematics.Global)
    op.AddInputPort(refA.Parameters("rotx"))
    op.AddInputPort(refB.Parameters("rotx"))

    # Set default values
    op.Parameters("blend").Value = blend

    # Connect
    op.Connect()

    return op

# sn_interpose_op ======================================
## Apply a sn_interpose_op operator
# @param out X3DObject - constrained Object.
# @param objA and objB X3DObject - Objects that will act as controler .
# @return the newly created operator.
def sn_interpose_op(out, objA, objB):


    # Create Operator
    op = XSIFactory.CreateObject("sn_interpose_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global.FullName)

    # Inputs
    op.AddInputPort(objA.Kinematics.Global.FullName)
    op.AddInputPort(objB.Kinematics.Global.FullName)

    # Connect
    op.Connect()


    return op

# sn_splinekine_op ======================================
## Apply a sn_splinekine_op operator
# @param out X3DObject - constrained Object.
# @param ctrl List of X3DObject - Objects that will act as controler of the bezier curve.
# @param u Double - Position of the object on the bezier curve (from 0 to 1).
# @return the newly created operator.
def sn_splinekine_op(out, ctrl=[], u=.5):

    # Create Operator
    op = XSIFactory.CreateObject("sn_splinekine_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global)

    # Inputs
    for obj in ctrl:
        op.AddInputPort(obj.Kinematics.Global)
    op.AddInputPort(ctrl[0].Parent.Kinematics.Global)

    # Set default values
    op.Parameters("count").Value = len(ctrl)
    op.Parameters("u").Value = u
    op.Parameters("resample").Value = True

    # Connect
    op.Connect()

    return op

# sn_rollsplinekine_op ==================================
## Apply a sn_rollsplinekine_op operator
# @param out X3DObject - constrained Object.
# @param ctrl List of X3DObject - Objects that will act as controler of the bezier curve. Objects must have a parent that will be used as an input for the operator.
# @param u Double - Position of the object on the bezier curve (from 0 to 1).
# @return the newly created operator.
def sn_rollsplinekine_op(out, ctrl=[], u=.5):

    # Create Operator
    op = XSIFactory.CreateObject("sn_rollsplinekine_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global)

    # Inputs
    for obj in ctrl:
        op.AddInputPort(obj.Parent.Kinematics.Global)
        op.AddInputPort(obj.Kinematics.Local)
    op.AddInputPort(ctrl[0].Parent.Kinematics.Global)

    # Set default values
    op.Parameters("count").Value = len(ctrl)
    op.Parameters("u").Value = u
    op.Parameters("resample").Value = True

    # Connect
    op.Connect()

    return op

# sn_curveslide_op =====================================
## Apply a sn_curveslide_op operator
# @param crv NurbeCurve - In / Out curve.
# @return the newly created operator.
def sn_curveslide_op(crv):

    length = crv.ActivePrimitive.Geometry.Length

    # Create Operator
    op = XSIFactory.CreateObject("sn_curveslide_op")

    # IO
    op.AddIOPort(crv.ActivePrimitive)

    # Set default values
    op.Parameters("length").Value = length

    # Connect
    op.Connect()

    return op

# sn_curveslide2_op =====================================
## Apply a sn_curveslide2_op operator
# @param outcrv NurbeCurve - Out Curve.
# @param incrv NurbeCurve - In Curve.
# @param position Double - Default position value (from 0 to 1).
# @param maxstretch Double - Default maxstretch value (from 1 to infinite).
# @param maxsquash Double - Default maxsquash value (from 0 to 1).
# @param softness Double - Default softness value (from 0 to 1).
# @return the newly created operator.
def sn_curveslide2_op(outcrv, incrv, position=0, maxstretch=1, maxsquash=1, softness=0, lang=CPP):

    inlength = incrv.ActivePrimitive.Geometry.Length

    # CPP -----------------------------------------------
    if lang == CPP:
        # Create Operator
        op = XSIFactory.CreateObject("sn_curveslide2_op")

        # IO
        op.AddIOPort(outcrv.ActivePrimitive)
        op.AddInputPort(incrv.ActivePrimitive)

        # Set default values
        op.Parameters("mstlength").Value = inlength
        op.Parameters("slvlength").Value = inlength
        op.Parameters("position").Value = position
        op.Parameters("maxstretch").Value = maxstretch
        op.Parameters("maxsquash").Value = maxsquash
        op.Parameters("softness").Value = softness

        # Connect
        op.Connect()

    # JSCRIPT -------------------------------------------
    elif lang == JSCRIPT:

        paramDefs = []
        paramDefs.append(XSIFactory.CreateParamDef("mstlength", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", inlength, 0, None, inlength*.5, inlength*2))
        paramDefs.append(XSIFactory.CreateParamDef("slvlength", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", inlength, 0, None, inlength*.5 , inlength*2))
        paramDefs.append(XSIFactory.CreateParamDef("position", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", position, 0, 1, 0, 1))
        paramDefs.append(XSIFactory.CreateParamDef("maxstretch", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", maxstretch, 0, None, 0, 3))
        paramDefs.append(XSIFactory.CreateParamDef("maxsquash", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", maxsquash, 0, 1, 0, 1))
        paramDefs.append(XSIFactory.CreateParamDef("softness", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", softness, 0, 1, 0, 1))

        outputPorts = [ (outcrv.ActivePrimitive, "out") ]
        inputPorts = [ (outcrv.ActivePrimitive, "in_crv"), (incrv.ActivePrimitive, "ref_crv") ]

        op = createJSOpFromFile("gear_curveslide2", os.path.join(JSOPPATH, "gear_curveslide2_op.js"), outputPorts, inputPorts, paramDefs)

        op.Connect()

        layout = op.PPGLayout
        layout.Clear()

        layout.AddGroup("Default");
        layout.AddItem("slvlength", "Slave Length");
        layout.AddItem("mstlength", "Master Length");
        layout.EndGroup();
        layout.AddGroup("Animate");
        layout.AddItem("position", "Position");
        layout.AddItem("maxstretch", "Max Stretch");
        layout.AddItem("maxsquash", "Max Squash");
        layout.AddItem("softness", "Softness");
        layout.EndGroup();

    return op

# sn_curvelength_op =====================================
## Apply a sn_curvelength_op operator
# @param out Parameter - The output of the curve length value.
# @param crv NurbeCurve - In Curve.
# @return the newly created operator.
def sn_curvelength_op(out, crv):

    # Create Operator
    op = XSIFactory.CreateObject("sn_curvelength_op")

    # Output
    op.AddOutputPort(out)

    # Input
    op.AddInputPort(crv.ActivePrimitive)

    # Connect
    op.Connect()

    return op

# sn_squashstretch_op ===================================
## Apply a sn_squashstretch_op operator
# @param out X3DObject - Constrained object.
# @param u Double - Position of the object on the S&S curve.
# @param length Double - Rest Length of the S&S.
# @return the newly created operator.
def sn_squashstretch_op(out, u=.5, length=5):

    # Create Operator
    op = XSIFactory.CreateObject("sn_squashstretch_op")

    # Output
    op.AddOutputPort(out.Kinematics.Global)

    # Input
    op.AddInputPort(out.Parent.Kinematics.Global)

    # Set default values
    op.Parameters("driver").Value = length
    op.Parameters("u").Value = u*100
    op.Parameters("sq_max").Value = length
    op.Parameters("st_min").Value = length

    # Connect
    op.Connect()

    return op

# sn_squashstretch2_op ==================================
## Apply a sn_squashstretch2_op operator
# @param out X3DObject - Constrained object.
# @param sclref X3DObject - Global scaling reference object.
# @param length Double - Rest Length of the S&S.
# @param axis String - 'x' for scale all except x axis...
# @return the newly created operator.
def sn_squashstretch2_op(out, sclref, length=5, axis="x"):

    # Create Operator
    op = XSIFactory.CreateObject("sn_squashstretch2_op")

    # Output
    op.AddOutputPort(out.Kinematics.Global)

    # Input
    op.AddInputPort(out.Kinematics.Global)
    op.AddInputPort(sclref.Kinematics.Global)

    # Set default values
    op.Parameters("driver_ctr").Value = length
    op.Parameters("driver_max").Value = length * 2
    op.Parameters("axis").Value = "xyz".index(axis)

    # Connect
    op.Connect()

    return op


# sn_null2curve_op =====================================
## Apply a sn_null2curve_op operator
# @param out X3DObject - Constrained object.
# @param driver X3DObject - Driving object.
# @param upv X3DObject - Up Vector.
# @param crv0 NurbsCurve - Curve to constraint the object on.
# @param crv1 NurbsCurve - Curve Use as reference (if None, crv0 is used).
# @return the newly created operator.
def sn_null2curve_op(out, driver, upv, crv0, crv1=None):

    if crv1 is None:
        crv1 = crv0

    # Create Operator
    op = XSIFactory.CreateObject("sn_null2curve_op")

    # Output
    op.AddOutputPort(out.Kinematics.Global)

    # Input
    op.AddInputPort(driver.Kinematics.Global)
    op.AddInputPort(upv.Kinematics.Global)
    op.AddInputPort(crv0.ActivePrimitive)
    op.AddInputPort(crv1.ActivePrimitive)

    # Connect
    op.Connect()

    return op

# sn_null2surface_op =====================================
## Apply a sn_null2surface_op operator
# @param out X3DObject - Constrained object.
# @param driver X3DObject - Driving object.
# @param upv X3DObject - Up Vector.
# @param srf0 NurbsSurface - NurbsSurface to constraint the object on.
# @param srf1 NurbsSurface - NurbsSurface Use as reference (if None, srf0 is used).
# @return the newly created operator.
def sn_null2surface_op(out, driver, upv, srf0, srf1=None):

    if srf1 is None:
        srf1 = srf0

    # Create Operator
    op = XSIFactory.CreateObject("sn_null2surface_op")

    # Output
    op.AddOutputPort(out.Kinematics.Global)

    # Input
    op.AddInputPort(driver.Kinematics.Global)
    op.AddInputPort(upv.Kinematics.Global)
    op.AddInputPort(srf0.ActivePrimitive)
    op.AddInputPort(srf1.ActivePrimitive)
    op.AddInputPort(driver.Kinematics.Local)

    # Connect
    op.Connect()

    return op

# sn_inverseRotorder_op =====================================
## Apply a sn_inverseRotorder_op operator
# @param out X3DObject - Constrained object.
# @param in X3DObject - Constrained object.
# @return the newly created operator.
def sn_inverseRotorder_op(out_obj, in_obj):

    # Create Operator
    op = XSIFactory.CreateObject("sn_inverseRotorder_op")

    # Output
    op.AddOutputPort(out_obj.Kinematics.Local.Parameters("rotorder"))

    # Input

    # Connect
    op.Connect()

    par.addExpression(op.Parameters("rotorder"), in_obj.Kinematics.Local.Parameters("rotorder").FullName)

    return op

# ========================================================
## Apply a sn_pointAt_op operator
# @param out_obj X3DObject - Constrained object.
# @param target X3DObject
# @param upv X3DObject
# @return the newly created operator.
def sn_pointAt_op(out_obj, target, upv):

    # -----------------------------------------------------
    # JSCRIPT
    paramDefs = []
    paramDefs.append(XSIFactory.CreateParamDef("offset", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, -180, 180, -90, 90))

    outputPorts = [ (out_obj.Kinematics.Global, "out") ]
    inputPorts = [ (out_obj.Kinematics.Global, "out"), (target.Kinematics.Global, "in_target"), (upv.Kinematics.Global, "in_upv") ]

    op = createJSOpFromFile("sn_pointAt_op", os.path.join(JSOPPATH, "sn_pointAt_op.js"), outputPorts, inputPorts, paramDefs)

    op.Connect()

    return op

# ========================================================
## Apply a gear_slerp operator
# @param out X3DObject
# @param crv Curve - The reference curve (if None, reference is same as target)
# @param start Double - Start Percentage (0 to 1)
# @param end Double - End Percentage (0 to 1)
# @return the newly created operator.
def gear_slerp_op(out, refA, refB, blend=.5):

    # -----------------------------------------------------
    # JSCRIPT
    paramDefs = []
    paramDefs.append(XSIFactory.CreateParamDef("blend", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", blend, 0, 1, 0, 1))

    outputPorts = [ (out.Kinematics.Global, "out") ]
    inputPorts = [ (out.Kinematics.Global, "in_obj"), (refA.Kinematics.Global, "refA"), (refB.Kinematics.Global, "refB") ]

    op = createJSOpFromFile("gear_slerp", os.path.join(JSOPPATH, "gear_slerp_op.js"), outputPorts, inputPorts, paramDefs)

    op.Connect()

    return op

# ========================================================
## Apply a gear_curveResampler operator
# @param out_crv Curve - The resampled Curve.
# @param crv Curve - The reference curve (if None, reference is same as target)
# @param start Double - Start Percentage (0 to 1)
# @param end Double - End Percentage (0 to 1)
# @return the newly created operator.
def gear_resampler_op(out_crv, crv=None, start=0, end=1, parametric=0, mode=0):

    if crv is None:
        crv = out_crv

    # -----------------------------------------------------
    # JSCRIPT
    paramDefs = []
    paramDefs.append(XSIFactory.CreateParamDef("start", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", start, 0, 1, 0, 1))
    paramDefs.append(XSIFactory.CreateParamDef("end", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", end, 0, 1, 0, 1))
    paramDefs.append(XSIFactory.CreateParamDef("parametric", c.siInt4, 0, c.siPersistable|c.siAnimatable, "", "", parametric, 0, 1, 0, 1))
    paramDefs.append(XSIFactory.CreateParamDef("mode", c.siInt4, 0, c.siPersistable|c.siAnimatable, "", "", mode, 0, 1, 0, 1))

    outputPorts = [ (out_crv.ActivePrimitive, "out") ]
    inputPorts = [ (out_crv.ActivePrimitive, "in_crv"), (out_crv.Kinematics.Global, "in_crv_kine"), (crv.ActivePrimitive, "ref_crv"), (crv.Kinematics.Global, "ref_crv_kine") ]

    op = createJSOpFromFile("gear_resampler", os.path.join(JSOPPATH, "gear_resampler_op.js"), outputPorts, inputPorts, paramDefs)

    op.Connect()

    layout = op.PPGLayout
    layout.Clear()

    layout.AddGroup("Percentage")
    layout.AddEnumControl("Parametric", ["Percentage", 0, "Parametric", 1])
    layout.AddEnumControl("Mode", ["Local", 0, "Global", 1])
    layout.AddItem("Start")
    layout.AddItem("End")
    layout.EndGroup()

    return op
# ========================================================
## Apply a gear_pointAtObjectAxis_op operator
# @param cns Constraint - Direction, Path, Curve, 2Point Constraint
# @param ref X3DObject - The object that will be use as reference
# @param axis List of Double - The vector that will be use as reference
# @return the newly created operator.
def gear_pointAtObjectAxis(cns, ref, axis=[0,1,0]):

    if cns.Parameters("tangent"):
        cns.Parameters("tangent").Value = True

    cns.Parameters("upvct_active").Value = True

    # -----------------------------------------------------
    # JSCRIPT
    paramDefs = [XSIFactory.CreateParamDef(s, c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", d, -1, 1, -1, 1) for d, s in zip(axis,"xyz")]

    outputPorts = [ (cns.Parameters("pointat%s"%s), "out_%s"%s) for s in "xyz" ]
    inputPorts = [ (ref.Kinematics.Global, "kine") ]

    op = createJSOpFromFile("gear_pointAtObjectAxis", os.path.join(JSOPPATH, "gear_pointAtObjectAxis_op.js"), outputPorts, inputPorts, paramDefs)

    # Connect
    op.Connect()

    return op

# ========================================================
def gear_dualUpVDirCns(cns, ref, target, negate=False):

    # -----------------------------------------------------
    # JSCRIPT
    paramDefs = []
    paramDefs.append(XSIFactory.CreateParamDef("negate", c.siBool, 0, c.siPersistable|c.siAnimatable, "", "", negate))

    outputPorts = [ (cns.Kinematics.Global, "out") ]
    inputPorts = [ (cns.Kinematics.Global, "kcns"),(ref.Kinematics.Global, "kref"),(target.Kinematics.Global, "ktar") ]

    op = createJSOpFromFile("gear_dualUpVDirCns", os.path.join(JSOPPATH, "gear_dualUpVDirCns_op.js"), outputPorts, inputPorts, paramDefs)

    # Connect
    op.Connect()

    return op

# ========================================================
def gear_rotationToPose(controler, reference, outputs=[], axis="x", offset=0):

    # Create Operator
    op = XSIFactory.CreateObject("gear_rotationToPose")

    # Outputs
    for i, output in enumerate(outputs):
        op.AddOutputPort(output, "out_%s"%i)

    # Inputs
    op.AddInputPort(reference.Kinematics.Global)
    op.AddInputPort(controler.Kinematics.Global)

    # Set default values
    op.Parameters("axis").Value = axis
    op.Parameters("slices").Value = len(outputs)
    op.Parameters("offset").Value = offset

    # Connect
    op.Connect()

    return op

# ========================================================
## Apply a gear_zipper operator
# @return the newly created operator.
def gear_zipper_op(crv0, crv1):

    # -----------------------------------------------------
    # JSCRIPT
    paramDefs = []
    paramDefs.append(XSIFactory.CreateParamDef("zip", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, 0, 1, 0, 1))
    paramDefs.append(XSIFactory.CreateParamDef("bias", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", .5, 0, 1, 0, 1))
    paramDefs.append(XSIFactory.CreateFCurveParamDef("start_fcv"))
    paramDefs.append(XSIFactory.CreateFCurveParamDef("speed_fcv"))

    outputPorts = [ (crv0.ActivePrimitive, "out_0"), (crv1.ActivePrimitive, "out_1") ]
    inputPorts = [ (crv0.ActivePrimitive, "crv0"), (crv1.ActivePrimitive, "crv1") ]

    op = createJSOpFromFile("gear_zipper", os.path.join(JSOPPATH, "gear_zipper_op.js"), outputPorts, inputPorts, paramDefs)

    op.Connect()

    # FCurve profile
    fcv.drawFCurve(op.Parameters("start_fcv").Value, [[0,0],[1,1]], c.siLinearKeyInterpolation)
    fcv.drawFCurve(op.Parameters("speed_fcv").Value, [[0,0],[1,1]], c.siLinearKeyInterpolation)

    # Layout
    layout = op.PPGLayout
    layout.Clear()

    layout.AddGroup("Zipper")
    layout.AddItem("Mute", "Mute")
    layout.AddItem("zip", "Zip")
    layout.AddItem("bias", "Bias")
    layout.EndGroup()

    layout.AddGroup("Profile")
    item = layout.AddFCurve("start_fcv")
    item.SetAttribute(c.siUIFCurveLabelX, "Points")
    item.SetAttribute(c.siUIFCurveLabelY, "Start")
    item.SetAttribute(c.siUIFCurveViewMinX,-.1)
    item.SetAttribute(c.siUIFCurveViewMaxX,1.1)
    item.SetAttribute(c.siUIFCurveViewMinY,-.1)
    item.SetAttribute(c.siUIFCurveViewMaxY,1.1)
    item.SetAttribute(c.siUIFCurveGridSpaceX, .1)
    item.SetAttribute(c.siUIFCurveGridSpaceY, .1)
    layout.EndGroup()

    layout.AddGroup("Speed")
    item = layout.AddFCurve("speed_fcv")
    item.SetAttribute(c.siUIFCurveLabelX, "Points")
    item.SetAttribute(c.siUIFCurveLabelY, "Speed")
    item.SetAttribute(c.siUIFCurveViewMinX,-.1)
    item.SetAttribute(c.siUIFCurveViewMaxX,2.1)
    item.SetAttribute(c.siUIFCurveViewMinY,-.1)
    item.SetAttribute(c.siUIFCurveViewMaxY,1.1)
    item.SetAttribute(c.siUIFCurveGridSpaceX, .1)
    item.SetAttribute(c.siUIFCurveGridSpaceY, .1)
    layout.EndGroup()

    return op

# ========================================================
## Apply a pathdriver operator
# @return the newly created operator.
def gear_pathdriver_op(out, max, min, perc, driver):

    # -----------------------------------------------------
    # JSCRIPT
    paramDefs = []
    paramDefs.append(XSIFactory.CreateParamDef("max", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", max, None, None, 0, 1))
    paramDefs.append(XSIFactory.CreateParamDef("min", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", min, None, None, -1, 0))
    paramDefs.append(XSIFactory.CreateParamDef("percentage", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", perc, 0, 100, 0, 100))
    paramDefs.append(XSIFactory.CreateParamDef("driver", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, None, None, -1, 1))

    outputPorts = [ (out, "out") ]
    inputPorts = []

    op = createJSOpFromFile("gear_pathdriver", os.path.join(JSOPPATH, "gear_pathdriver_op.js"), outputPorts, inputPorts, paramDefs)

    op.Connect()

    par.addExpression(op.Parameters("driver"), driver)

    return op

##########################################################
# MISC
##########################################################
# ========================================================
## Create a JScript operator from given file
# @param name String - Name of the operator
# @param path String - Path to the file that define the operator
# @param outputPorts List of Objects - Object to be connected as outputs
# @param inputPorts List of Objects - Object to be connected as inputs
# @param paramDefs List of Parameter Definition to create
# @return the newly created operator.
def createJSOpFromFile(name, path, outputPorts, inputPorts, paramDefs=[]):

    if not os.path.exists(path):
        gear.log("Can't find : "+path, gear.sev_warning)
        return False

    file = open(path)
    code = file.read()

    op = XSIFactory.CreateScriptedOp(name, code, "JScript")

    for port, name in outputPorts:
        op.AddOutputPort(port)

    for port, name in inputPorts:
        op.AddInputPort(port, name)

    for pdef in paramDefs:
        op.AddParameter(pdef)

    return op
