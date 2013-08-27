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

## @package gear_modelingTools.py
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, XSIFactory, dynDispatch

import gear.xsi.utils as uti
import gear.xsi.geometry as geo
import gear.xsi.uitoolkit as uit

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_modelingTools"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_MatchGeometry","gear_MatchGeometry")
    in_reg.RegisterCommand("gear_SymmetrizePoints","gear_SymmetrizePoints")

    in_reg.RegisterCommand("gear_MirrorClusters","gear_MirrorClusters")
    in_reg.RegisterCommand("gear_MergeWithClusters","gear_MergeWithClusters")
    in_reg.RegisterCommand("gear_SplitPolygonIslands","gear_SplitPolygonIslands")
    in_reg.RegisterCommand("gear_AddClusterCenter","gear_AddClusterCenter")


    # Operators
    in_reg.RegisterOperator("gear_MatchGeometryOp")
    in_reg.RegisterOperator("gear_SymmetrizePointsOp")

    return True

def XSIUnloadPlugin(in_reg):
    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)
    return True

##########################################################
# MATCH GEOMETRY
##########################################################
# ========================================================
def gear_MatchGeometryOp_Define(ctxt):

    op = ctxt.Source

    pdef = XSIFactory.CreateParamDef("blend", c.siDouble, 0, c.siPersistable | c.siAnimatable, "", "",1,-100,100,0,1)
    op.AddParameter(pdef)
    pdef = XSIFactory.CreateParamDef("mode", c.siInt4, 0, c.siPersistable | c.siAnimatable, "", "",0,0,1,0,1)
    op.AddParameter(pdef)

    op.AlwaysEvaluate = False
    op.Debug = 0

    return True

# ========================================================
def gear_MatchGeometryOp_DefineLayout(ctxt):

    layout = ctxt.Source
    layout.Clear()

    mode_items = ["Local", 0, "Global", 1]

    layout.AddGroup("Options")
    layout.AddItem("Mute")
    layout.AddItem("blend", "Blend")
    layout.AddEnumControl("mode", mode_items, "", c.siControlCombo)
    layout.EndGroup()

    return True

# ========================================================
def gear_MatchGeometryOp_Update(ctxt):

    # Inputs -----------------------------------------------
    out_geo = ctxt.GetInputValue(0, 0, 0).Geometry
    in_geo = ctxt.GetInputValue(1, 0, 0).Geometry
    cls = ctxt.GetInputValue(2, 0, 0)
    mOutGeom = ctxt.GetInputValue(3, 0, 0).Transform.Matrix4
    mInGeom = ctxt.GetInputValue(4, 0, 0).Transform.Matrix4

    blend = ctxt.GetParameterValue("blend")
    mode = ctxt.GetParameterValue("mode")

    mInvOutGeom = XSIMath.CreateMatrix4()
    mInvOutGeom.Invert(mOutGeom)

    # Get Arrays --------------------------------------------
    aOutPosTuple = out_geo.Points.PositionArray
    aInPosTuple  = in_geo.Points.PositionArray

    aOutPosition = [aOutPosTuple[j][i] for i in range(len(aOutPosTuple[0])) for j in range(len(aOutPosTuple))]

    # Process -----------------------------------------------
    for point_index in cls.Elements.Array:

        vTarget = XSIMath.CreateVector3(aInPosTuple[0][point_index], aInPosTuple[1][point_index], aInPosTuple[2][point_index])
        vSource = XSIMath.CreateVector3(aOutPosTuple[0][point_index], aOutPosTuple[1][point_index], aOutPosTuple[2][point_index])

        # convert local position from target object to source object
        if mode == 1:
            vTarget.MulByMatrix4InPlace(mInGeom)
            vTarget.MulByMatrix4InPlace(mInvOutGeom)

        vResult = XSIMath.CreateVector3()
        vResult.Sub(vTarget, vSource)

        vResult.ScaleInPlace(blend)

        aOutPosition[point_index*3+0] = aOutPosTuple[0][point_index]+ vResult.X
        aOutPosition[point_index*3+1] = aOutPosTuple[1][point_index]+ vResult.Y
        aOutPosition[point_index*3+2] = aOutPosTuple[2][point_index]+ vResult.Z

    Out = ctxt.OutputTarget
    Out.Geometry.Points.PositionArray = aOutPosition

# ========================================================
def gear_MatchGeometry_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    target = xsi.Selection(0)
    if target.Type not in ["pntSubComponent", "polymsh", "surfmsh", "crvlist"]:
        gear.log("Invalid Selection, select a geometry or a point selection", gear.sev_error)
        return

    # Get reference
    source = uit.pickSession(c.siGenericObjectFilter, "Pick Source Geometry")
    if not source:
        return

    # Get cluster
    if target.Type == "pntSubComponent":
        obj = target.SubComponent.Parent3DObject
        cls = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_MatchGeometryOp_cls", target.SubComponent.ElementArray)
    else:
        obj = target
        cls = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_MatchGeometryOp_cls")

    if source.Type != obj.Type:
        gear.log("Invalid Selection", gear.sev_error)
        xsi.DeleteObj(cls)
        return

    # Apply Operator
    op = XSIFactory.CreateObject("gear_MatchGeometryOp")

    op.AddIOPort(obj.ActivePrimitive)
    op.AddInputPort(source.ActivePrimitive)
    op.AddInputPort(cls)
    op.AddInputPort(obj.Kinematics.Global)
    op.AddInputPort(source.Kinematics.Global)

    op.Connect()

    xsi.InspectObj(op)

    return op

##########################################################
# SYMMETRIZE POINTS
##########################################################
# ========================================================
def gear_SymmetrizePointsOp_Define(ctxt):

    op = ctxt.Source

    pdef = XSIFactory.CreateParamDef("axis", c.siInt4, 0, c.siPersistable|c.siAnimatable, "" , "" , 0, 0, 2, 0, 2)
    op.AddParameter(pdef)
    pdef = XSIFactory.CreateParamDef("mirror", c.siBool, 0, c.siPersistable|c.siAnimatable, "" , "" , False)
    op.AddParameter(pdef)

    op.AlwaysEvaluate = False
    op.Debug = 0

    return True

# ========================================================
def gear_SymmetrizePointsOp_DefineLayout(ctxt):

    axis_items = ["YZ", 0, "XZ", 1, "XY", 2]

    layout = ctxt.Source
    layout.Clear()

    layout.AddGroup("Options")
    layout.AddItem("Mute")
    layout.AddEnumControl("axis", axis_items, "Axis", c.siControlCombo)
    layout.AddItem("mirror", "Mirror")
    layout.EndGroup()

    return True

# ========================================================
def gear_SymmetrizePointsOp_Update(ctxt):

    # Inputs
    geometry = ctxt.GetInputValue(0, 0, 0).Geometry
    sym_map = ctxt.GetInputValue(1, 0, 0)
    cls = ctxt.GetInputValue(2, 0, 0)

    mapGenerator_op = dynDispatch(sym_map.NestedObjects("Symmetry Map Generator"))
    if mapGenerator_op:
        ctxt.SetAttribute("axis", mapGenerator_op.Parameters("axis").Value)

    axis = ctxt.GetParameterValue("axis")
    mirror = ctxt.GetParameterValue("mirror")

    # Get Arrays
    sym_array = sym_map.Elements.Array

    pos_tuple = geometry.Points.PositionArray
    positions = [pos_tuple[j][i] for i in range(len(pos_tuple[0])) for j in range(len(pos_tuple))]

    # Process
    for point_index in cls.Elements.Array:

        sym_index = int(sym_array[0][point_index])

        if axis == 0:
            positions[sym_index*3+0] = - pos_tuple[0][point_index]
            positions[sym_index*3+1] = pos_tuple[1][point_index]
            positions[sym_index*3+2] = pos_tuple[2][point_index]

            if mirror:
                positions[point_index*3+0] = - pos_tuple[0][sym_index]
                positions[point_index*3+1] = pos_tuple[1][sym_index]
                positions[point_index*3+2] = pos_tuple[2][sym_index]

        elif axis == 1:
            positions[sym_index*3+0] = pos_tuple[0][point_index]
            positions[sym_index*3+1] = - pos_tuple[1][point_index]
            positions[sym_index*3+2] = pos_tuple[2][point_index]

            if mirror:
                positions[point_index*3+0] = pos_tuple[0][sym_index]
                positions[point_index*3+1] = - pos_tuple[1][sym_index]
                positions[point_index*3+2] = pos_tuple[2][sym_index]

        elif axis == 2:
            positions[sym_index*3+0] = pos_tuple[0][point_index]
            positions[sym_index*3+1] = pos_tuple[1][point_index]
            positions[sym_index*3+2] = - pos_tuple[2][point_index]

            if mirror:
                positions[point_index*3+0] = - pos_tuple[0][sym_index]
                positions[point_index*3+1] = pos_tuple[1][sym_index]
                positions[point_index*3+2] = - pos_tuple[2][sym_index]

    Out = ctxt.OutputTarget
    Out.Geometry.Points.PositionArray = positions

# ========================================================
def gear_SymmetrizePoints_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    if pntSubComp.Type not in ["pntSubComponent"]:
        gear.log("Invalid Selection, need a pntSubComponent", gear.sev_error)
        return

    obj = pntSubComp.SubComponent.Parent3DObject

    # Get Symmetry Map -------------------
    sym_map = uti.getSymmetryMap(obj)
    if not sym_map:
        gear.log("There is no symmetry map on selected object", gear.sev_error)
        return

    cls = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_SymmetrizePointsOp_cls", pntSubComp.SubComponent.ElementArray)

    # Apply Operator ----------------------
    op = XSIFactory.CreateObject("gear_SymmetrizePointsOp")

    op.AddIOPort(obj.ActivePrimitive)
    op.AddInputPort(sym_map)
    op.AddInputPort(cls)

    op.Connect()

    xsi.InspectObj(op)

    return op


##########################################################
# MIRROR CLUSTER
##########################################################
# ========================================================
def gear_MirrorClusters_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for cls in xsi.Selection:

        if cls.Type not in ["pnt", "poly", "edge"]:
            gear.log("Invalid selection : "+cls.FullName, gear.sev_warning)
            continue

        geo.mirrorCluster(cls)

##########################################################
# MERGE WITH CLUSTERS
##########################################################
# ========================================================
def gear_MergeWithClusters_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    objects = [obj for obj in xsi.Selection if obj.Type in ["polymsh"]]
    if len(objects) < 2:
        gear.log("Not enough object to perform action. Make sure you have selected enough polymesh", gear.sev_error)
        return

    op = geo.mergeWithClusters(objects)

    xsi.InspectObj(op)

##########################################################
# SPLIT POLYGON ISLANDS
##########################################################
# ========================================================
def gear_SplitPolygonIslands_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for obj in xsi.Selection:

        if obj.Type not in ["polymsh"]:
            gear.log("Invalid input : "+ obj.FullName, gear.sev_warning)
            continue

        gear.log("Split : "+obj.FullName)

        geo.splitPolygonIsland(obj)

##########################################################
# ADD CLUSTER CENTER
##########################################################
# ========================================================
def gear_AddClusterCenter_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    sel = xsi.Selection(0)

    if sel.Type in ["polymsh", "surfmsh", "crvlist"]:
        mesh = sel
        points = range(mesh.ActivePrimitive.Geometry.Points.Count)
    elif sel.Type == "pntSubComponent":
        mesh = sel.SubComponent.Parent3DObject
        points = sel.SubComponent.ElementArray
    else:
        gear.log("Invalid selection", gear.sev_error)
        return

    geo.addClusterCenter(mesh, points)