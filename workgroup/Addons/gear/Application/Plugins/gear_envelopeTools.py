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

## @package gear_envelopeTools.py
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, XSIFactory, lm

import gear.xsi.uitoolkit as uit
import gear.xsi.operator as ope
import gear.xsi.envelope as env

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Padawan Campos"
    in_reg.Name = "gear_envelopeTools"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_SelectUnnormalizedPoints", "gear_SelectUnnormalizedPoints")
    in_reg.RegisterCommand("gear_CreateSymmetryMappingTemplate", "gear_CreateSymmetryMappingTemplate")
    in_reg.RegisterCommand("gear_MergeSymmetryMappingTemplate", "gear_MergeSymmetryMappingTemplate")

    in_reg.RegisterCommand("gear_CopyWeights", "gear_CopyWeights")
    in_reg.RegisterCommand("gear_CopyWeightsAverage", "gear_CopyWeightsAverage")
    in_reg.RegisterCommand("gear_AverageMirrorWeights","gear_AverageMirrorWeights")
    in_reg.RegisterCommand("gear_ReplaceDeformer","gear_ReplaceDeformer")


    in_reg.RegisterCommand("gear_NormalizeWeights", "gear_NormalizeWeights")
    in_reg.RegisterCommand("gear_NormalizeToDeformer","gear_NormalizeToDeformer")
    in_reg.RegisterCommand("gear_PruneWeights", "gear_PruneWeights")
    in_reg.RegisterCommand("gear_MakeIslandRigid", "gear_MakeIslandRigid")
    in_reg.RegisterCommand("gear_RebuildEnvelope", "gear_RebuildEnvelope")
    in_reg.RegisterCommand("gear_RemoveUnusedEnvCls", "gear_RemoveUnusedEnvCls")

    in_reg.RegisterCommand("gear_CopyEnvWithGator", "gear_CopyEnvWithGator")
    in_reg.RegisterCommand("gear_MirrorObjectWeights", "gear_MirrorObjectWeights")

    # Operators
    in_reg.RegisterOperator("gear_CopyWeightsOp")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# MERGE Symmetry mapping template
##########################################################
# Define =================================================
def gear_MergeSymmetryMappingTemplate_Execute():

    # Pick Session
    source_SMT = uit.pickSession(c.siGenericObjectFilter, "Pick Source Symmetry Mapping Template", True)
    if not source_SMT:
      return
    elif source_SMT.Type != "MixerProp":
        lm("The selction is not a Symmetry mapping template", 4)
        return
    target_SMT = uit.pickSession(c.siGenericObjectFilter, "Pick Target Symmetry Mapping Template", True)
    if not target_SMT:
      return
    elif target_SMT.Type != "MixerProp":
        lm("The selction is not a Symmetry mapping template", 4)
        return

    oNumRules =  xsi.GetNumMappingRules( source_SMT)


    for x in range(oNumRules):
        oFrom = xsi.GetMappingRule( source_SMT, x + 1)[1]
        oTo = xsi.GetMappingRule( source_SMT, x + 1)[3]
        xsi.AddMappingRule( target_SMT, oFrom, oTo, 0 )
##########################################################
# SELECT UNNORMALIZED POINT
##########################################################
# Execute ================================================
def gear_SelectUnnormalizedPoints_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    mesh = xsi.Selection(0)

    # Check input
    if mesh.Type not in ["polymsh", "crvlist", "surfmsh"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    # Get Envelope
    envelope_op = ope.getOperatorFromStack(mesh, "envelopop")
    if not envelope_op:
        gear.log("There's no envelope on " + mesh.Fullname, gear.sev_error)
        return

    unNormPntId = env.getUnnormalizedPoints(envelope_op)

    # Select Pnt
    if unNormPntId:
        gear.log("There is " + str(len(unNormPntId)) +" unnormalized point(s)")
        gear.log(mesh.FullName+".pnt"+str(unNormPntId))
        xsi.SelectGeometryComponents(mesh.FullName+".pnt"+str(unNormPntId))
    else:
        gear.log("There is no unnormalized point", gear.sev_warning)

##########################################################
# SELECT UNNORMALIZED POINT
##########################################################
# Execute ================================================
def gear_CreateSymmetryMappingTemplate_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    mesh = xsi.Selection(0)

    # Check input
    if mesh.Type not in ["polymsh", "crvlist", "surfmsh"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    # Get Envelope
    envelope_op = ope.getOperatorFromStack(mesh, "envelopop")
    if not envelope_op:
        gear.log("There's no envelope on " + mesh.Fullname, gear.sev_error)
        return

    env.createSymmetryMappingTemplate(envelope_op.Deformers)

##########################################################
# COPY  WEIGHTS FROM POINT TO POINT
##########################################################
# Define =================================================
def gear_CopyWeightsOp_Define(ctxt):

    op = ctxt.Source
    op.AlwaysEvaluate = False
    op.Debug = 0

    pdef = XSIFactory.CreateParamDef("Blend", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",1,0,1,0,1)
    op.AddParameter(pdef)
    pdef = XSIFactory.CreateParamDef("Index", c.siInt4, 0, c.siPersistable|c.siReadOnly, "", "")
    op.AddParameter(pdef)

    return True

# Update =================================================
def gear_CopyWeightsOp_Update(ctxt):

    # Inputs -----------------------------------------------
    env_cls = ctxt.GetInputValue(0, 0, 0)
    cls = ctxt.GetInputValue(1, 0, 0)

    weights_tuple = env_cls.Elements.Array
    weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]
    aPoints = cls.Elements.Array

    dBlend = ctxt.GetParameterValue("Blend")
    iRefIndex = ctxt.GetParameterValue("Index")

    # Use upper bound of safearray to get total num of deformers
    deformer_count = len(weights_tuple)

    # Process -----------------------------------------------
    for point_index in aPoints:
        for deformer_index in range(deformer_count):
            weights[point_index*deformer_count + deformer_index] = dBlend * weights_tuple[deformer_index][iRefIndex] + (1-dBlend) * weights_tuple[deformer_index][point_index]

    # Output -------------------------------------------------
    Out = ctxt.OutputTarget
    Out.Elements.Array = weights

# Execute ================================================
def gear_CopyWeights_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    sel = xsi.Selection(0)

    # Check input
    if sel.Type not in ["pntSubComponent"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    obj = sel.SubComponent.Parent3DObject
    envelope_op = ope.getOperatorFromStack(obj, "envelopop")
    if not envelope_op:
        gear.log("There is no envelope on selected mesh", gear.sev_error)
        return

    cls = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_CopyWeightsOp_Cls", sel.SubComponent.ElementArray)

    # Pick Session
    source_pnt = uit.pickSession(c.siPointFilter, "Pick Source Point", True)
    if not source_pnt:
      return

    points = source_pnt.SubComponent.ElementArray
    if len(points) != 1:
      gear.log("Please Select Only One Point" , gear.sev_error)
      return

    # Need to find the cluster
    for port in envelope_op.InputPorts:
      if port.Target2.Type == "envweights":
            env_cls = port.Target2

    if not env_cls:
      gear.log("Invalid Envelop, no cluster was found",  gear.sev_error)
      return

    # Apply Operator ----------------------
    op = XSIFactory.CreateObject("gear_CopyWeightsOp")

    op.AddIOPort(env_cls)
    op.AddInputPort(cls)
    op.Index = points[0]
    op.Connect()

    xsi.InspectObj(op)

    return op

##########################################################
# COPY WEIGHTS AVERAGE
##########################################################
# Execute ================================================
def gear_CopyWeightsAverage_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    sel = xsi.Selection(0)

    # Check input
    if sel.Type not in ["pntSubComponent"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    target_point = sel.SubComponent.ElementArray

    obj = sel.SubComponent.Parent3DObject
    envelope_op = ope.getOperatorFromStack(obj, "envelopop")
    if not envelope_op:
        gear.log("There is no envelope on selected mesh", gear.sev_error)
        return

    # Pick Session
    source_points = []
    while True:
        source_pnt = uit.pickSession(c.siPointFilter, "Pick Source Point", False)
        if not source_pnt:
            break

        source_points.extend(source_pnt.SubComponent.ElementArray)

    if not source_points:
        gear.log("No Points Selected", gear.sev_error)
        return

    # Get Weights
    weights_tuple = envelope_op.Weights.Array
    weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]
    deformer_count = envelope_op.Deformers.Count

    # Array of average value of weights
    avr_weights = [0] * deformer_count
    for point_index in source_points:
        for deformer_index in range(deformer_count):
            avr_weights[deformer_index] += weights_tuple[deformer_index][point_index] / len(source_points)

    # Replace Weights in Weight Array
    for point_index in target_point:
        for deformer_index in range(deformer_count):
            weights[point_index*deformer_count + deformer_index] = avr_weights[deformer_index]

    envelope_op.Weights.Array = weights

    return

##########################################################
# AVERAGE MIRROR WEIGHTS (Central points of the geommetry)
##########################################################
# Execute ================================================
def gear_AverageMirrorWeights_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    sel = xsi.Selection(0)

    # Check input
    if sel.Type not in ["pntSubComponent"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    mesh = sel.SubComponent.Parent3DObject
    envelope_op = ope.getOperatorFromStack(mesh, "envelopop")
    if not envelope_op:
        gear.log("There is no envelope on selected mesh", gear.sev_error)
        return

    points = sel.SubComponent.ElementArray

    # Process
    env.averageMirrorWeights(envelope_op, points)

##########################################################
# REPLACE DEFORMER
# This method don't replace the deformers from 1 source to 1 target deformer. Instead can replace 1 source deformer to x target deformers
# or x source deformers to 1 target deformer. For this reason the envelopes will be regenerate.
##########################################################
# Execute ================================================
def gear_ReplaceDeformer_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    sel = xsi.Selection(0)

    if sel.Type == "polymsh":
        mesh = sel
        points = range(mesh.ActivePrimitive.Geometry.Points.Count)
    elif sel.Type == "pntSubComponent":
        mesh = sel.SubComponent.Parent3DObject
        points = sel.SubComponent.ElementArray
    else:
        gear.log("Invalid selection", gear.sev_error)
        return

    # Get Envelope from object
    envelope_op = ope.getOperatorFromStack(mesh, "envelopop")
    if not envelope_op:
        gear.log("There is no envelope on selected mesh", gear.sev_error)
        return False

    # Source deformers
    source_deformers = XSIFactory.CreateObject("XSI.Collection")
    while True:
        picked = uit.pickSession(c.siGenericObjectFilter, "Pick Source Deformers", False)
        if not picked:
            break

        if picked.Type == "#Group":
            source_deformers.AddItems(picked.Members)
        else:
            source_deformers.Add(picked)

    if not source_deformers.Count:
        return False

    # Target deformers
    target_deformers = XSIFactory.CreateObject("XSI.Collection")
    while True:
        picked = uit.pickSession(c.siGenericObjectFilter, "Pick Target Deformers", False)
        if not picked:
            break

        if picked.Type == "#Group":
            target_deformers.AddItems(picked.Members)
        else:
            target_deformers.Add(picked)

    if not target_deformers.Count:
        return False

    # Some log to be sure of what we have selected
    gear.log("Geometry: " + mesh.FullName + "  \nSource(s): " + str(source_deformers) + "  \nTarget(s): " + str(target_deformers))

    env.replaceDeformerInEnvelope(envelope_op, source_deformers, target_deformers, points)

##########################################################
# PRUNE WEIGHTS
##########################################################
# Execute ================================================
def gear_PruneWeights_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    sel = xsi.Selection(0)

    if sel.Type in ["polymsh", "surfmsh", "crvlist"]:
        mesh = sel
        points = range(mesh.ActivePrimitive.Geometry.Points.Count)
#    elif sel.Type == "pntSubComponent":
#        mesh = sel.SubComponent.Parent3DObject
#        points = sel.SubComponent.ElementArray
    else:
        gear.log("Invalid selection", gear.sev_error)
        return

    # Get Envelope from object
    envelope_op = ope.getOperatorFromStack(mesh, "envelopop")
    if not envelope_op:
        gear.log("There is no envelope on selected mesh", gear.sev_error)
        return

    # PPG for Options
    prop = xsi.ActiveSceneRoot.AddProperty("CustomProperty", False, "gear_PruneWeights")
    pThreshold = prop.AddParameter3("Threshold", c.siDouble, .1, 0, None, False, False)
    pRemove    = prop.AddParameter3("RemoveDeformers", c.siBool, True, None, None, False, False)

    layout = prop.PPGLayout
    layout.AddGroup("Prune")
    layout.AddItem(pThreshold.ScriptName, "Weights Threshold")
    layout.AddItem(pRemove.ScriptName, "Remove Unused Deformers")
    layout.EndGroup()

    rtn = xsi.InspectObj(prop, "", "Prune Weights", c.siModal, False)

    threshold = pThreshold.Value
    remove = pRemove.Value

    xsi.DeleteObj(prop)

    if rtn:
        return

    # Process
    env.pruneWeights(envelope_op, points, threshold, remove, True)

##########################################################
# MAKE ISLAND RIGID
##########################################################
# Execute ================================================
def gear_MakeIslandRigid_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for sel in xsi.Selection:

        if sel.Type not in ["polymsh", "surfmsh", "crvlist"]:
            gear.log("Invalid selection : %s"%sel.Name, gear.sev_warning)
            continue

        # Process
        env.makeIslandRigid(sel)

##########################################################
# NORMALIZE WEIGHTS
##########################################################
# Execute ================================================
def gear_NormalizeWeights_Execute():

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

    # Get Envelope from object
    envelope_op = ope.getOperatorFromStack(mesh, "envelopop")
    if not envelope_op:
        gear.log("There is no envelope on selected mesh", gear.sev_error)
        return

    # Process
    points = env.getUnnormalizedPoints(envelope_op, points)
    if not env.normalizeWeights(envelope_op, points):
        return

    env.freezeEnvelope(envelope_op)
    env.rebuiltEnvelope(envelope_op)

##########################################################
# NORMALIZE TO DEFORMER
##########################################################
# Execute ================================================
def gear_NormalizeToDeformer_Execute():

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

    # Get Envelope from object
    envelope_op = ope.getOperatorFromStack(mesh, "envelopop")
    if not envelope_op:
        gear.log("There is no envelope on selected mesh", gear.sev_error)
        return

    # Get The deformers
    deformers = XSIFactory.CreateObject("XSI.Collection")
    while True:
        deformer =  uit.pickSession(c.siGenericObjectFilter, "Pick Deformer", False)
        if not deformer:
            break

        if env.isDeformer(envelope_op, deformer):
            deformers.Add(deformer)
        else:
            gear.log("Picked object is not a deformer for this envelope", c.siWarning)

    if not deformers.Count:
        return

    # Process
    env.normalizeToDeformer(envelope_op, deformers, points)
    env.freezeEnvelope(envelope_op)
    env.rebuiltEnvelope(envelope_op)

##########################################################
# REBUILD ENVELOPE
##########################################################
# Execute ================================================
def gear_RebuildEnvelope_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for mesh in xsi.Selection:

        if mesh.Type not in ["polymsh", "surfmsh", "crvlist"]:
            gear.log("Invalid selection", gear.sev_error)
            continue

        # Get Envelope from object
        envelope_op = ope.getOperatorFromStack(mesh, "envelopop")
        if not envelope_op:
            gear.log("There is no envelope on selected mesh", c.siWarning)
            continue

        env.rebuiltEnvelope(envelope_op)

##########################################################
# REMOVE UNUSED ENVELOPE CLS
##########################################################
# Execute ================================================
def gear_RemoveUnusedEnvCls_Execute():

    # This method is named based and doesn't provide a perfect result but should work in most of the case.

    # Return All the Pnt Cluster from the active scene
    point_clusters = xsi.FindObjects(None, "{E4DD8E40-1E1C-11D0-AA2E-00A0243E34C4}")

    # Search for unused EnvelopWeightCls
    delete_objs = XSIFactory.CreateObject("XSI.Collection")
    for cls in point_clusters:

        if cls.Name.startswith("EnvelopWeightCls"):
            delete = True
            for prop in cls.Properties:
                if prop.Type == "envweights":
                    delete = False

            if delete:
                delete_objs.Add(cls)

    # Delete
    if delete_objs.Count:
        xsi.DeleteObj(delete_objs)

##########################################################
# COPY ENVELOPE WITH GATOR
##########################################################
# Execute ================================================
def gear_CopyEnvWithGator_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    source_meshes = XSIFactory.CreateObject("XSI.Collection")
    while True:
        picked = uit.pickSession(c.siGeometryFilter, "Pick Source Mesh", False)
        if not picked:
            break

        if not ope.getOperatorFromStack(picked, "envelopop"):
            gear.log("No Envelope on " + picked.Name, c.siWarning)
            continue

        source_meshes.Add(picked)

    if not source_meshes:
        return

    for mesh in xsi.Selection:
        env.copyEnvelopeWithGator(mesh, source_meshes)


##########################################################
# MIRROR OBJECT WEIGHTS
##########################################################
# Execute ================================================
def gear_MirrorObjectWeights_Execute():

    xsi.DeselectAll()

    # Get Source Mesh
    source_mesh = uit.pickSession(c.siGenericObjectFilter, "Pick Enveloped Mesh", True)
    if not source_mesh:
        return

    if source_mesh.Type not in ["polymsh", "surfmsh", "crvlist"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    envelope_op = ope.getOperatorFromStack(source_mesh, "envelopop")
    if not envelope_op:
        gear.log("There is no envelope on selected mesh", gear.sev_error)
        return

    # Get Target Mesh
    target_mesh = uit.pickSession(c.siGenericObjectFilter, "Pick Target Mesh", True)
    if not target_mesh:
        return

    if target_mesh.Type not in ["polymsh", "surfmsh", "crvlist"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    # Process
    env.copyMirrorEnvelope(source_mesh, target_mesh)
