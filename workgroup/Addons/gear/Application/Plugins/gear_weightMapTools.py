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

## @package gear_weightMapTools.py
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
# Built in
import math

# Gear
import gear
from gear.xsi import xsi, c, XSIMath, Dispatch, dynDispatch

import gear.xsi.utils as uti
import gear.xsi.weightmap as wei

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_weightMapTools"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_SelectWeightMapPoints", "gear_SelectWeightMapPoints")
    in_reg.RegisterCommand("gear_ResetWeightMapPoints", "gear_ResetWeightMapPoints")
    in_reg.RegisterCommand("gear_SetWeightMapPoints", "gear_SetWeightMapPoints")
    in_reg.RegisterCommand("gear_ScaleWeightMapPoints", "gear_ScaleWeightMapPoints")
    in_reg.RegisterCommand("gear_SmoothWeightMapPoints", "gear_SmoothWeightMapPoints")
    in_reg.RegisterCommand("gear_SymWeightMapPoints", "gear_SymWeightMapPoints")

    # Operators
    in_reg.RegisterOperator("gear_SetWeightMapPointsOp")
    in_reg.RegisterOperator("gear_ScaleWeightMapPointsOp")
    in_reg.RegisterOperator("gear_SmoothWeightMapPointsOp")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# SELECT WEIGHT MAP POINTS
##########################################################
# ========================================================
def gear_SelectWeightMapPoints_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    wmap = xsi.Selection(0)
    if wmap.Type not in ["wtmap"]:
        gear.log("Select a Weight Map", gear.sev_error)
        return

    obj = wmap.Parent3DObject
    points = wei.getWeightMapPoints(wmap)

    if points:
        xsi.SelectGeometryComponents(obj.FullName + ".pnt" + str(points))
    else:
        gear.log("There is no points in the Weght map", gear.sev_warning)

##########################################################
# RESET WEIGHT MAP POINTS
##########################################################
# ========================================================
def gear_ResetWeightMapPoints_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select some points and a weight map", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    wmap = xsi.Selection(1)

    # Check  if input doesn't match
    if pntSubComp.Type not in ["pntSubComponent"] or wmap.Type not in ["wtmap"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    wei.resetWeightMapPoints(wmap, pntSubComp.SubComponent.ElementArray)

##########################################################
# SET WEIGHTMAP POINTS
##########################################################
# ========================================================
def gear_SetWeightMapPointsOp_Define(ctxt):

    op = ctxt.Source
    op.AlwaysEvaluate = False
    op.Debug = 0

    pdef = XSIFactory.CreateParamDef("Value", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",1,-100,100,0,1)
    op.AddParameter(pdef)

    return True

# ========================================================
def gear_SetWeightMapPointsOp_Update(ctxt):

    # Inputs
    wmap = ctxt.GetInputValue(0, 0, 0)
    cls = ctxt.GetInputValue(1, 0, 0)

    value = ctxt.GetParameterValue("Value")

    # Process
    weights = [w for w in wmap.Elements.Array[0]]

    for i in cls.Elements.Array:
        weights[i] = value

    # Output
    Out = ctxt.OutputTarget
    Out.Elements.Array = weights

# ========================================================
def gear_SetWeightMapPoints_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select some points and a weight map", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    wmap = xsi.Selection(1)

    # Check  if input doesn't match
    if pntSubComp.Type not in ["pntSubComponent"] or wmap.Type not in ["wtmap"]:
        gear.log("Invalid selection", gear.sev_error)
        return
    
    # Get Arrays
    clsElements = wmap.Parent.Elements
    points = [clsElements.FindIndex(i) for i in pntSubComp.SubComponent.ElementArray if clsElements.FindIndex(i) != -1]

    obj = pntSubComp.SubComponent.Parent3DObject
    cls = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_SetWeightMapPointsOp_Cls", points )

    # Apply Operator
    op = XSIFactory.CreateObject("gear_SetWeightMapPointsOp")

    op.AddIOPort(wmap)
    op.AddInputPort(cls)

    op.Connect(None, c.siConstructionModeModeling)

    xsi.InspectObj(op)

##########################################################
# SCALE WEIGHTMAP POINTS
##########################################################
# ========================================================
def gear_ScaleWeightMapPointsOp_Define(ctxt):

    op = ctxt.Source
    op.AlwaysEvaluate = False
    op.Debug = 0

    pdef = XSIFactory.CreateParamDef("Scale", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",1,-100,100,0,1)
    op.AddParameter(pdef)

    return True

# ========================================================
def gear_ScaleWeightMapPointsOp_Update(ctxt):

    # Inputs
    wmap = ctxt.GetInputValue(0, 0, 0)
    cls = ctxt.GetInputValue(1, 0, 0)

    scale = ctxt.GetParameterValue("Scale")

    # Process
    weights = [w for w in wmap.Elements.Array[0]]

    for i in cls.Elements.Array:
       weights[i] *= scale

    # Output
    Out = ctxt.OutputTarget
    Out.Elements.Array = weights

# ========================================================
def gear_ScaleWeightMapPoints_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select some points and a weight map", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    wmap = xsi.Selection(1)

    # Check  if input doesn't match
    if pntSubComp.Type not in ["pntSubComponent"] or wmap.Type not in ["wtmap"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    # Get Arrays
    clsElements = wmap.Parent.Elements
    points = [clsElements.FindIndex(i) for i in pntSubComp.SubComponent.ElementArray if clsElements.FindIndex(i) != -1]

    obj = pntSubComp.SubComponent.Parent3DObject
    cls = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_ScaleWeightMapPointsOp_Cls", points )

    # Apply Operator
    op = XSIFactory.CreateObject("gear_ScaleWeightMapPointsOp")

    op.AddIOPort(wmap)
    op.AddInputPort(cls)

    op.Connect(None, c.siConstructionModeModeling)

    xsi.InspectObj(op)

##########################################################
# SMOOTH WEIGHTMAP POINTS
##########################################################
# miquel: this operator only work with complete clusters
# ========================================================
def gear_SmoothWeightMapPointsOp_Define(ctxt):

    op = ctxt.Source
    op.AlwaysEvaluate = False
    op.Debug = 0

    pdef = XSIFactory.CreateParamDef("Depth", c.siInt4, 0, c.siPersistable|c.siAnimatable, "", "",1,1,10,1,10)
    op.AddParameter(pdef)
    pdef = XSIFactory.CreateParamDef("Blend", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",1,0,1,0,1)
    op.AddParameter(pdef)
    # miquel: WIP feature for partial clusters
    # pdef = XSIFactory.CreateParamDef("aPointCls", c.siString, 0, c.siPersistable|c.siReadOnly)
    # op.AddParameter(pdef)

    return True

# ========================================================
def gear_SmoothWeightMapPointsOp_Update(ctxt):

    # Inputs
    wmap   = ctxt.GetInputValue(0, 0, 0)
    geometry = ctxt.GetInputValue(1, 0, 0).Geometry
    cls  = ctxt.GetInputValue(2, 0, 0)

    depth = ctxt.GetParameterValue("Depth")
    blend     = ctxt.GetParameterValue("Blend")
    # miquel: WIP feature for partial clusters
    # outSel     = ctxt.GetParameterValue("aPointCls").split(',')

    # Process
    weights = [w for w in wmap.Elements.Array[0]]
    # miquel: WIP feature for partial clusters
    # weights = outSel

    points = cls.Elements.Array
    for i in points:

        vertex = geometry.Vertices(i)
        neighbors = vertex.NeighborVertices(depth)

        smooth_weight = 0
        for vtx in neighbors:
            index = vtx.Index

            smooth_weight += weights[index]

        smooth_weight = ((smooth_weight + 0.0) / neighbors.Count) * blend
        original_weight = weights[i] * (1-blend)

        weights[i] = smooth_weight + original_weight

    # Output
    Out = ctxt.OutputTarget
    Out.Elements.Array = weights

# ========================================================
def gear_SmoothWeightMapPoints_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select some points and a weight map", gear.sev_error)
        return

    pntSubComp = xsi.Selection(0)
    wmap = xsi.Selection(1)

    # Check  if input doesn't match
    if pntSubComp.Type not in ["pntSubComponent"] or wmap.Type not in ["wtmap"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    # Get Arrays
    clsElements = wmap.Parent.Elements
    points = [clsElements.FindIndex(i) for i in pntSubComp.SubComponent.ElementArray if clsElements.FindIndex(i) != -1]

    obj = pntSubComp.SubComponent.Parent3DObject
    cls = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_SmoothWeightMapPointsOp_Cls", points )

    # Apply Operator
    op = XSIFactory.CreateObject("gear_SmoothWeightMapPointsOp")

    op.AddIOPort(wmap)
    op.AddInputPort(wmap.Parent3DObject.ActivePrimitive)
    op.AddInputPort(cls)

    op.Connect(None, c.siConstructionModeModeling)

    xsi.InspectObj(op)

##########################################################
# SYMMETRIZE WEIGHT MAP POINTS
##########################################################
# ========================================================
def gear_SymWeightMapPoints_Execute():

  if xsi.Selection.Count < 2:
      gear.log("Select some points and a weight map", gear.sev_error)
      return

  pntSubComp = xsi.Selection(0)
  wmap = xsi.Selection(1)

  # Check  if input doesn't match
  if pntSubComp.Type not in ["pntSubComponent"] or wmap.Type not in ["wtmap"]:
      gear.log("Invalid selection", gear.sev_error)
      return

  # Get Symmetry Map
  symMap = uti.getSymmetryMap(wmap.Parent3DObject)
  if not symMap:
      return

  # Get Arrays
  points = pntSubComp.SubComponent.ElementArray
  weights = [w for w in wmap.Elements.Array[0]]
  sym_array = symMap.Elements.Array

  # Process
  for i in points:
      weights[int(sym_array[0][i])] = weights[i]

  wmap.Elements.Array = weights
