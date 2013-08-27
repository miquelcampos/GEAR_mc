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

## @package gear_shapeTools.py
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, XSIMath, Dispatch, dynDispatch, XSIFactory

import gear.xsi.shape as sha
import gear.xsi.uitoolkit as uit

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_shapeTools"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_SelectShapePoints","gear_SelectShapePoints")
    in_reg.RegisterCommand("gear_ResetShapePoints","gear_ResetShapePoints")
    in_reg.RegisterCommand("gear_ScaleShapePoints","gear_ScaleShapePoints")
    in_reg.RegisterCommand("gear_SmoothShapePoints","gear_SmoothShapePoints")
    in_reg.RegisterCommand("gear_SymShapePoints","gear_SymShapePoints")

    in_reg.RegisterCommand("gear_DuplicateShapeKey","gear_DuplicateShapeKey")
    in_reg.RegisterCommand("gear_MoveShapeKey","gear_MoveShapeKey")

    in_reg.RegisterCommand("gear_ResetShapeKey","gear_ResetShapeKey")
    in_reg.RegisterCommand("gear_MergeShapeKey","gear_MergeShapeKey")
    in_reg.RegisterCommand("gear_SplitShapeKey","gear_SplitShapeKey")
    in_reg.RegisterCommand("gear_MirrorShapeKey","gear_MirrorShapeKey")
    in_reg.RegisterCommand("gear_MatchShapeKey","gear_MatchShapeKey")
    in_reg.RegisterCommand("gear_ReplaceShapeKey","gear_ReplaceShapeKey")

    in_reg.RegisterCommand("gear_ExtractShapeKey","gear_ExtractShapeKey")

    # Operators
    in_reg.RegisterOperator("gear_ScaleShapeOp")
    in_reg.RegisterOperator("gear_SmoothShapeOp")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    gear.log(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# SELECT SHAPE POINTS
##########################################################
# Execute ================================================
def gear_SelectShapePoints_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    shape = xsi.Selection(0)

    # Check input
    if shape.Type not in ["clskey"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    points = sha.getShapePoints(shape)

    if not points:
        gear.log("There is no point deformed by this shape", gear.sev_warning)
        return

    mesh = shape.Parent3DObject
    xsi.SelectGeometryComponents(mesh.FullName+".pnt"+str(points))

##########################################################
# RESET SHAPE POINTS
##########################################################
# Execute ================================================
def gear_ResetShapePoints_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select first the point and then the shape", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    shape = xsi.Selection(1)

    # Check  if input doesn't match
    if pntSubComp.Type not in ["pntSubComponent"] or shape.Type not in ["clskey"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    points = pntSubComp.SubComponent.ElementArray

    sha.resetShapePoints(shape, points)

##########################################################
# SCALE SHAPE POINTS
##########################################################
# Define =================================================
def gear_ScaleShapeOp_Define(ctxt):

    op = ctxt.Source
    op.AlwaysEvaluate = False
    op.Debug = 0

    pdef = XSIFactory.CreateParamDef("Scale", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",.5,-100,100,0,1)
    op.AddParameter(pdef)

    return True

# Update =================================================
def gear_ScaleShapeOp_Update(ctxt):

    # Inputs
    shape    = ctxt.GetInputValue(0, 0, 0)
    cls = ctxt.GetInputValue(1, 0, 0)

    scale = ctxt.GetParameterValue("Scale")

    # Process
    shape_tuple = shape.Elements.Array
    shape_array = [shape_tuple[j][i] for i in range(len(shape_tuple[0])) for j in range(len(shape_tuple)) ]

    points = cls.Elements.Array
    for i in points:
        shape_array[ i*3+0 ] *= scale
        shape_array[ i*3+1 ] *= scale
        shape_array[ i*3+2 ] *= scale

    # Output
    Out = ctxt.OutputTarget
    Out.Elements.Array = shape_array

# Execute ================================================
def gear_ScaleShapePoints_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select first the point and then the shape", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    shape = xsi.Selection(1)

    # Check  if input doesn't match
    if pntSubComp.Type not in ["pntSubComponent"] or shape.Type not in ["clskey"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    points = pntSubComp.SubComponent.ElementArray

    op = sha.applyScaleShapeOp(shape, points)

    xsi.InspectObj(op)

##########################################################
# SMOOTH SHAPE POINTS
##########################################################
# Define =================================================
def gear_SmoothShapeOp_Define(ctxt):

    op = ctxt.Source
    op.AlwaysEvaluate = False
    op.Debug = 0

    pdef = XSIFactory.CreateParamDef("NeighbourDepth", c.siInt4, 0, c.siPersistable|c.siAnimatable, "", "",1,1,10,1,10)
    op.AddParameter(pdef)
    pdef = XSIFactory.CreateParamDef("Blend", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",1,0,1,0,1)
    op.AddParameter(pdef)

    return True

# Update =================================================
def gear_SmoothShapeOp_Update(ctxt):

    # Inputs -----------------------------------------------
    shape = ctxt.GetInputValue(0, 0, 0)
    geo  = ctxt.GetInputValue(1, 0, 0).Geometry
    cls  = ctxt.GetInputValue(2, 0, 0)

    neighbor_depth = ctxt.GetParameterValue("NeighbourDepth")
    blend     = ctxt.GetParameterValue("Blend")

    # Process ----------------------------------------------
    shape_tuple = shape.Elements.Array
    shape_array = [shape_tuple[j][i] for i in range(len(shape_tuple[0])) for j in range(len(shape_tuple)) ]

    points = cls.Elements.Array
    vSmoothShape = XSIMath.CreateVector3()
    vOriShape     = XSIMath.CreateVector3()
    for i in points:

        vertex = geo.Vertices(i)
        cNghbVertices = vertex.NeighborVertices(neighbor_depth)

        vSmoothShape.Set(0,0,0)
        vOriShape.Set(shape_array[i*3+0], shape_array[i*3+1], shape_array[i*3+2])
        for oVtx in cNghbVertices:
            index = oVtx.Index

            vSmoothShape.X += shape_array[ index*3+0 ]
            vSmoothShape.Y += shape_array[ index*3+1 ]
            vSmoothShape.Z += shape_array[ index*3+2 ]

        vSmoothShape.ScaleInPlace(blend/cNghbVertices.Count)
        vOriShape.ScaleInPlace(1-blend)

        shape_array[ i*3+0 ] = vSmoothShape.X + vOriShape.X
        shape_array[ i*3+1 ] = vSmoothShape.Y + vOriShape.Y
        shape_array[ i*3+2 ] = vSmoothShape.Z + vOriShape.Z

    # Output -----------------------------------------------
    Out = ctxt.OutputTarget
    Out.Elements.Array = shape_array

# Execute ================================================
def gear_SmoothShapePoints_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select first the point and then the shape", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    shape = xsi.Selection(1)

    # Check  if input doesn't match
    if pntSubComp.Type not in ["pntSubComponent"] or shape.Type not in ["clskey"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    points = pntSubComp.SubComponent.ElementArray

    op = sha.applySmoothShapeOp(shape, points)

    xsi.InspectObj(op)

##########################################################
# SYMMETRIZE SHAPE POINTS
##########################################################
# Execute ================================================
def gear_SymShapePoints_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select first the point and then the shape", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    shape = xsi.Selection(1)

    # Check  if input doesn't match
    if pntSubComp.Type not in ["pntSubComponent"] or shape.Type not in ["clskey"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    points = pntSubComp.SubComponent.ElementArray

    sha.symmetrizeShapePoints(shape, points)

##########################################################
# DUPLICATE SHAPE KEY
##########################################################
# Execute ================================================
def gear_DuplicateShapeKey_Execute():

    if not xsi.Selection.Count:
        gear.log("Select shape keys", gear.sev_error)
        return

    for shape in xsi.Selection:

        if shape.Type not in ["clskey"]:
            continue

        sha.duplicateShapeKey(shape)

##########################################################
# RESET SHAPE KEY
##########################################################
# Execute ================================================
def gear_ResetShapeKey_Execute():

    if not xsi.Selection.Count:
        gear.log("Select shape keys", gear.sev_error)
        return

    for shape in xsi.Selection:

        if shape.Type not in ["clskey"]:
            continue

        sha.resetShapeKey(shape)

##########################################################
# MERGE SHAPE KEY
##########################################################
# Execute ================================================
def gear_MergeShapeKey_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select shape keys", gear.sev_error)
        return

    shapes = [shape for shape in xsi.Selection if shape.Type in ["clskey"]]
    if not shapes:
        return

    sha.mergeShapeKeys(shapes)

##########################################################
# MOVE SHAPE KEY
##########################################################
# Execute ================================================
def gear_MoveShapeKey_Execute():

    if not xsi.Selection.Count:
        gear.log("Select shape keys", gear.sev_error)
        return

    shapes = [shape for shape in xsi.Selection if shape.Type in ["clskey"]]
    if not shapes:
        return

    cls = shapes[0].Parent
    geo = cls.Parent
    clusters = geo.Clusters

    # UI
    prop = xsi.ActiveSceneRoot.AddProperty("Custom_parameter_list", False, "gear_MoveShapeKey")
    pDuplicate = prop.AddParameter3("duplicate", c.siBool, True, None, None, False, False)
    pClusters = prop.AddParameter3("clusters", c.siInt4, -1, 0, clusters.Count-1, False, False)

    clustersItems = ["New Cluster", -1]
    for i, cls in enumerate(clusters):
        clustersItems.append(cls.Name)
        clustersItems.append(i)

    layout = prop.PPGLayout
    layout.Clear()
    layout.AddTab("General")
    layout.AddGroup("Move Shape Key Option")
    item = layout.AddItem(pDuplicate.ScriptName, "Duplicate")
    item = layout.AddEnumControl(pClusters.ScriptName, clustersItems, "Move to", c.siControlCombo)
    layout.EndGroup()

    # Inspect
    rtn = xsi.InspectObj(prop, "", "Move Shape Key", c.siModal, False)

    # Return values
    duplicate = pDuplicate.Value
    cluster_index = pClusters.Value

    xsi.DeleteObj(prop)

    if rtn:
         return

    # Create or get target cluster
    if cluster_index == -1:
        target_cluster = geo.AddCluster(c.siVertexCluster, cls.Name+"_Copy", cls.Elements.Array)
    else:
        target_cluster = clusters(cluster_index)

    # Duplicate Shape key
    for shape in shapes:
        sha.duplicateShapeKey(shape, target_cluster)

    # Delete original
    if not duplicate:
        xsi.DeleteObj(shapes)

##########################################################
# SPLIT SHAPE KEY
##########################################################
# Execute ================================================
def gear_SplitShapeKey_Execute():

    if not xsi.Selection.Count:
        gear.log("Select shape keys", gear.sev_error)
        return

    shapes = [shape for shape in xsi.Selection if shape.Type in ["clskey"]]
    if not shapes:
        return

    cls = shapes[0].Parent
    mesh = cls.Parent3DObject
    geo = mesh.ActivePrimitive.Geometry
    clusters = geo.Clusters

    # UI
    prop = xsi.ActiveSceneRoot.AddProperty("Custom_parameter_list", False, "gear_SplitShapeKey")

    pLPrefix  = prop.AddParameter3("LPrefix", c.siString, "L_", None, None, False, False)
    pRPrefix  = prop.AddParameter3("RPrefix", c.siString, "R_", None, None, False, False)
    pRCluster = prop.AddParameter3("RCluster", c.siInt4, -1, -1, clusters.Count-1, False, False)
    pLCluster = prop.AddParameter3("LCluster", c.siInt4, -1, -1, clusters.Count-1, False, False)
    pCCluster = prop.AddParameter3("CCluster", c.siInt4, -1, -1, clusters.Count-1, False, False)

    clusters_items = ["Auto Detect Points", -1]
    for i, cls in enumerate(clusters):
        clusters_items.append(cls.Name)
        clusters_items.append(i)

    # Layout
    layout = prop.PPGLayout
    layout.Clear()

    layout.AddTab("General")
    layout.AddGroup("Prefix")
    layout.AddRow()
    layout.AddItem(pRPrefix.ScriptName, "Right")
    layout.AddItem(pLPrefix.ScriptName, "Left")
    layout.EndRow()
    layout.EndGroup()

    layout.AddGroup("Clusters")
    layout.AddEnumControl(pRCluster.ScriptName, clusters_items, "Right Points", c.siControlCombo)
    layout.AddEnumControl(pLCluster.ScriptName, clusters_items, "Left Points", c.siControlCombo)
    layout.AddEnumControl(pCCluster.ScriptName, clusters_items, "Center Points", c.siControlCombo)
    layout.EndGroup()

    # Inspect
    rtn = xsi.InspectObj(prop, "", "Split Shape Key", c.siModal, False)

    # Return Values
    if pRCluster.Value == -1:
        r_points = sha.getPoints(geo, "R")
    else:
        r_points = clusters(pRCluster.value-1).Elements.Array

    if pLCluster.Value == -1:
        l_points = sha.getPoints(geo, "L")
    else:
        l_points = clusters(pLCluster.value-1).Elements.Array

    if pCCluster.Value == -1:
        c_points = sha.getPoints(geo, "C")
    else:
        c_points = clusters(pCCluster.value-1).Elements.Array

    r_prefix = pRPrefix.Value
    l_prefix = pLPrefix.Value

    xsi.DeleteObj(prop)

    if rtn:
        return

    # Process
    for shape in shapes:
        sha.createHalfShape(shape, c_points, l_prefix, r_points)
        sha.createHalfShape(shape, c_points, r_prefix, l_points)

##########################################################
# MIRROR SHAPE
##########################################################
# Execute ================================================
def gear_MirrorShapeKey_Execute():

    if not xsi.Selection.Count:
        gear.log("Select shape keys", gear.sev_error)
        return

    shapes = [shape for shape in xsi.Selection if shape.Type in ["clskey"]]
    if not shapes:
        return

    for shape in shapes:
        sha.mirrorShapeKey(shape)

##########################################################
# MATCH SHAPE KEY
##########################################################
# Execute ================================================
def gear_MatchShapeKey_Execute():

    if not xsi.Selection.Count:
        gear.log("Select shape key", gear.sev_error)
        return

    target_shape = xsi.Selection(0)
    if target_shape.Type not in ["clskey"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    source_shape = uit.pickSession(c.siPropertyFilter, "Pick Source Shape", True)
    if not source_shape:
        return

    if source_shape.Type not in ["clskey"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    sha.matchShapeKey(target_shape, source_shape)
##########################################################
# MATCH SHAPE KEY
##########################################################
# Execute ================================================
def gear_ReplaceShapeKey_Execute():

    if not xsi.Selection.Count:
        gear.log("Select shape key", gear.sev_error)
        return

    shape = xsi.Selection(0)
    if shape.Type not in ["clskey"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    sha.replaceShapeKey(shape)

##########################################################
# EXTRACT SHAPE KEY
##########################################################
# Execute ================================================
def gear_ExtractShapeKey_Execute():

    if not xsi.Selection.Count:
        gear.log("Select a mesh with shape keys", gear.sev_error)
        return

    geo = xsi.Selection(0)
    if geo.Type not in ["polymsh", "surfmsh", "crvlist"]:
        gear.log("Select a mesh with shape keys", gear.sev_error)
        return

    shapes = [prop for cls in geo.ActivePrimitive.Geometry.Clusters for prop in cls.Properties if prop.Type == "clskey"]
    if len(shapes) == 0:
        gear.log("Select a mesh with shape keys", gear.sev_error)
        return

    extracted_shapes = sha.extractShapes(shapes, True)
    uti.organizeGeometries(extracted_shapes.values(), 9)
