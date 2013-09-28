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

## @package gear.xsi.envelope
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
import gear

from gear.xsi import xsi, c, XSIFactory, XSIUtils

import gear.xsi.uitoolkit as uit
import gear.xsi.utils as uti
import gear.xsi.operator as ope
import gear.xsi.geometry as geo

##########################################################
# ENVELOPE
##########################################################
# createEnvelope =========================================
## Apply envelope
# @param obj to apply the envelope.
# @param deformers: List of  deformers
# @return
def createEnvelope(obj, deformers):

    oListStr = ""
        
    for i in range(len(deformers)):
        if i ==0:
            oListStr = oListStr + deformers[i].Fullname
        else:
            oListStr = oListStr + ", " + deformers[i].Fullname

    envOp = xsi.ApplyFlexEnv(obj.FullName + ";" + oListStr ,"",2)
    return envOp
# FreezeEnvelope =========================================
## Freeze the operator stack of given envelope
# @param envelope_op Envelope Operator - the envelope operator to freeze.
# @return
def freezeEnvelope(envelope_op):

     # Get Envelope Weights
     for port in envelope_op.InputPorts:
          if port.Target2.Type == "envweights":
                envWeights = port.Target2
                break

     xsi.FreezeObj(envWeights, None, None)

# Rebuilt Envelope ======================================
## Rebuilt given envelope
# @param envelope_op Envelope Operator - the envelope operator.
# @return Operator - the newly created envelope operator.
def rebuiltEnvelope(envelope_op):

     geo = envelope_op.Parent3DObject
     deformers = envelope_op.Deformers

     weights = envelope_op.Weights.Array
     xsi.RemoveFlexEnv(geo)
     envelope_op = geo.ApplyEnvelope(deformers)
     envelope_op.Weights.Array = weights

     return envelope_op

# Copy Envelope With Gator ==============================
## Allows to copy envelope
# @param mesh Polymsh.
# @param source_meshes - XSICollection of Polymsh.
def copyEnvelopeWithGator(mesh, source_meshes):

    # Set the log display to False because Gator Op display a lot of messages
    b = xsi.Preferences.Categories("scripting").Parameters("msglog").Value
    xsi.Preferences.Categories("scripting").Parameters("msglog").Value = False

    if mesh.Type not in ["polymsh"]:
        gear.log("Invalid selection", gear.sev_error)
        return

    # Apply a Gator Op
    gator_op = xsi.ApplyGenOp("Gator", "", mesh.FullName+";"+source_meshes.GetAsText(), 3, c.siPersistentOperation, c.siKeepGenOpInputs, None)
    xsi.CopyAnimationAcrossGenerator(gator_op, 2, 1)
    # I wasn't able to use the FullName Property for gator_op
    xsi.SetValue(str(gator_op) + ".inputreadregion", 0, None)

    xsi.FreezeModeling(mesh)

    # Set the log back to its original value
    xsi.Preferences.Categories("scripting").Parameters("msglog").Value = b

# Copy Mirror Envelope ==================================
## Copy the envelope to a mirror object.
# @param source_mesh Polymsh.
# @param target_mesh Polymsh.
def copyMirrorEnvelope(source_mesh, target_mesh):

    sourceEnv_op = ope.getOperatorFromStack(source_mesh, "envelopop")
    if not sourceEnv_op:
        gear.log("There is no envelope on source mesh", gear.sev_error)
        return

    target_deformers = XSIFactory.CreateObject("XSI.Collection")
    for deformer in sourceEnv_op.Deformers:

        model = deformer.Model
        target_deformer = model.FindChild(uti.convertRLName(deformer.Name))
        if not target_deformer:
            gear.log("Deformer missing : " +uti.convertRLName(deformer.Name), c.siWarning)
            target_deformer = deformer

        target_deformers.Add(target_deformer)

    targetEnv_op = target_mesh.ApplyEnvelope(target_deformers)

    # Apply Weights
    targetEnv_op.Weights.Array = sourceEnv_op.Weights.Array

# AddStaticKineState =====================================
## Add a static kine state property to objects
# @param objs List or Collection of X3DObject - Objects to create a StaticKineState property on.
# @return List of Property - the newly created properties.
def addStaticKineState(objs):

     props = [obj.AddProperty("Static Kinematic State Property") for obj in objs]
     return  props

##########################################################
# DEFORMERS
##########################################################
# Is Deformer ===========================================
## Check if the object is a deformer of given envelope
# @param envelope_op Envelope Operator - the envelope operator.
# @param obj X3DObject - Object to check.
# @return true if the object is used as a deformer for the given envelope.
def isDeformer(envelope_op, obj):

     deformers = envelope_op.Deformers.GetAsText().split(",")

     try:
          index = deformers.index(obj.FullName)
          return True
     except:
          return False

     # for deformer in envelope_op.Deformers:
          # if deformer.IsEqualTo(obj):
                # return True

     # return False

# Get Deformer Index ======================================
## Get the deformer index
# @param envelope_op Envelope Operator - the envelope operator.
# @param obj X3DObject - Object to check.
# @return the index of the deformer in the envelope (-1 if it's not found).
def getDeformerIndex(envelope_op, obj):

     deformers = envelope_op.Deformers.GetAsText().split(",")

     try:
          index = deformers.index(obj.FullName)
          return index
     except:
          return -1

     # for i, deformer in enumerate(envelope_op.Deformers):
          # if deformer.IsEqualTo(obj):
                # return i

     # return -1

# replacedeformerInEnvelope =============================
## Replace a collection of deformer with another one in the envelope.\n
## This method don't replace the deformers from 1 source to 1 target deformer. Instead can replace 1 source deformer to x target deformers\n
## or x source deformers to 1 target deformer. For this reason the envelopes will be regenerate.
# @param envelope_op Envelope Operator - the envelope operator.
# @param source_deformers XSICollection - Deformers we want to remove.
# @param target_deformers XSICollection - Deformers we want to add.
def replaceDeformerInEnvelope(envelope_op, source_deformers, target_deformers, points=None):


    # Check source deformers
    source_index = []
    for obj in source_deformers:
        deformer_index = getDeformerIndex(envelope_op, obj)
        if deformer_index != -1:
            source_index.append(deformer_index)

    if not source_index:
        gear.log("None of the source deformers belongs to the envelope", gear.sev_warning)
        return False

    # Add Target Deformer to envelope if missing
    mesh = envelope_op.Parent3DObject
    for obj in target_deformers:
        if not isDeformer(envelope_op, obj):
            envelope_op = mesh.ApplyEnvelope(obj)

    # Get the target deformers index
    target_index = []
    for obj in target_deformers:
        deformer_index = getDeformerIndex(envelope_op, obj)
        target_index.append(deformer_index)

    # Get Weights
    mesh = envelope_op.Parent3DObject
    point_count = mesh.ActivePrimitive.Geometry.Points.Count
    deformer_count = envelope_op.Deformers.Count
    weights_tuple = envelope_op.Weights.Array
    weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]

    # Process
    if points is None:
        points = range(point_count)

    for point_index in points:

        point_weight = 0
        for deformer_index in source_index:
            point_weight += weights_tuple[deformer_index][point_index]
            weights[point_index * deformer_count + deformer_index] = 0

        if point_weight == 0:
            continue

        for deformer_index in target_index:
            weights[point_index * deformer_count + deformer_index] += point_weight / len(target_index)

    envelope_op.Weights.Array = weights

    freezeEnvelope(envelope_op)

    # Remove old deformers from the envelope
    for source_deformer in source_deformers:
        delete = True

        for target_deformer in target_deformers:
            if source_deformer.FullName == target_deformer.FullName:
                delete = False

        gear.log(mesh.FullName + "     " + source_deformer.FullName + "    " + str(delete))

        if delete:
            rtn = removeEnvDeformer(envelope_op, source_deformer)
            if not rtn:
                gear.log("Deformer " + source_deformer.FullName + " could not be removed !", gear.sev_warning)

    return True

# RemoveEnvDeformer =====================================
## Remove a Deformer from given envelope
# @param envelope_op Envelope Operator - the envelope operator.
# @param deformer X3DObject - the deformer to remove from envelope.
# @return Envelope Operator - The newly created envelope operator
def removeEnvDeformer(envelope_op, obj):

    mesh = envelope_op.Parent3DObject
    points = mesh.ActivePrimitive.Geometry.Points
    point_count = points.Count
    deformers = envelope_op.Deformers
    deformer_count = deformers.Count
    index = 0
    weights_tuple = envelope_op.Weights.Array
    weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]
    new_deformers = XSIFactory.CreateObject("XSI.Collection")

    # Process
    for deformer_index, deformer in enumerate(deformers):
        if obj.FullName == deformer.FullName:
            index = deformer_index
        else:
            new_deformers.add(deformer)

    newWeight = []
    for point_index in range(point_count):
        newWeight.extend(weights[point_index*deformer_count : point_index*deformer_count+index])
        newWeight.extend(weights[point_index*deformer_count+index+1 : point_index* deformer_count + deformer_count])

    # Delete the old Envelope and add the new one with the new Deformers
    xsi.RemoveFlexEnv(mesh)
    envelope_op = mesh.ApplyEnvelope(new_deformers)
    envelope_op.Weights.Array = newWeight

    return envelope_op

##########################################################
# WEIGHTS
##########################################################
# GetUnnormalizedPoints =================================
## Return the indexes of unormalized points of the envelope.
# @param envelope_op Envelope Operator - the envelope operator.
# @param threshold Float - the threshold.
# @return List of Integer - the list of unnormalized point index .
def getUnnormalizedPoints(envelope_op, points=None, threshold=1E-6):

    mesh = envelope_op.Parent3DObject
    deformer_count = envelope_op.Deformers.Count
    point_count = mesh.ActivePrimitive.Geometry.Points.Count
    weights_tuple = envelope_op.Weights.Array

    unNormPntId = []

    if points is None:
        points = range(point_count)

    for point_index in points:

        total_weight = 0
        for deformer_index in range(deformer_count):
            total_weight += weights_tuple[deformer_index][point_index]

        if total_weight < (100 - threshold) or total_weight > (100 + threshold):
            unNormPntId.append(point_index)

    return unNormPntId

# normalizeWeights ======================================
## Normalize the weight array to 100 for given point of given envelope op
# @param envelope_op Operator - Envelope operator to normalize
# @param points List of Integer - Index of vertices to normalize
def normalizeWeights(envelope_op, points):

    mesh = envelope_op.Parent3DObject
    deformer_count = envelope_op.Deformers.Count
    point_count = mesh.ActivePrimitive.Geometry.Points.Count
    weights_tuple = envelope_op.Weights.Array
    weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]

    for point_index in points:

        point_weights = weights[point_index*deformer_count:(point_index+1)*deformer_count]
        total_weight = sum(point_weights)

        if total_weight > 0:
            point_weights = normalizeArray(point_weights)
        else:
            point_weights = normalizeToClosestPoint(envelope_op, weights, point_index)

        if not point_weights:
            gear.log("Unable to normalize " + envelope_op.FullName, gear.sev_warning)
            return False

        # rebuilt weights array
        for deformer_index in range(deformer_count):
            weights[point_index*deformer_count + deformer_index] = point_weights[deformer_index]

    envelope_op.Weights.Array = weights

    return True

# normalizeToClosestPoint ===============================
## Normalize the point according to surronding values. Useful when a point weight is 0.
# @param envelope_op Envelope Operator - the envelope operator.
# @param weights List of float - The weights of the envelope. We pass it as an argument for speed purpose.
# @param point_index Integer - Index of the point to normalize.
# @return List of Float - The weight of the point.
def normalizeToClosestPoint(envelope_op, weights, point_index):

    mesh = envelope_op.Parent3DObject
    deformer_count = envelope_op.Deformers.Count
    point_count = mesh.ActivePrimitive.Geometry.Points.Count

    vertex = mesh.ActivePrimitive.Geometry.Points(point_index)

    point_weights = [0] * deformer_count

    distance = 1
    neighbor_count = vertex.NeighborVertices(1).Count

    while neighbor_count < point_count - 1:

        neighbor_vertices = vertex.NeighborVertices(distance)
        neighbor_count = neighbor_vertices.Count

        for neighbor_vertex in neighbor_vertices:
             neighbor_index = neighbor_vertex.Index
             for deformer_index in range(deformer_count):
                point_weights[deformer_index] += (weights[ neighbor_index*deformer_count + deformer_index ]) / neighbor_vertices.Count

        if sum(point_weights) != 0:
            point_weights = normalizeArray(point_weights)
            return point_weights

        distance += 1

    gear.log("Normalize to Closest Point aborded at distance "+ str(distance), c.siWarning)
    return False

# NormalizeTdeformer ===================================
## Add the missing weight of a point to given deformer
# @param envelope_op Operator - Envelope operator to normalize
# @param deformers XSICollection - Collection of deformers
# @param points List of Integer - Index of vertices to normalize
# @param threshold Float
def normalizeToDeformer(envelope_op, deformers, points=None, threshold=1E-6):

    mesh = envelope_op.Parent3DObject
    deformer_count = envelope_op.Deformers.Count
    point_count = mesh.ActivePrimitive.Geometry.Points.Count
    weights_tuple = envelope_op.Weights.Array
    weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]

    # Get Deformers Index
    deformers_index = [getDeformerIndex(envelope_op, obj) for obj in deformers if isDeformer(envelope_op, obj)]
    if not deformers_index:
        gear.log("No deformers to add weights", gear.sev_error)
        return False

    if points is None:
        points = range(point_count)

    for point_index in points:

        total_weights = 0
        for deformer_index, deformer in enumerate(envelope_op.Deformers):
            total_weights += weights[point_index*deformer_count + deformer_index]

        if total_weights < (100 - threshold):
            for deformer_index in deformers_index:
                weights[point_index*deformer_count + deformer_index] += (100 - total_weights) / len(deformers_index)

    # Apply new Weights
    envelope_op.Weights.Array = weights

    return True

# NormalizeArray ========================================
## Normalize given array so the sum of the array is equal to 100.
# @param a List of Float - the array to normalize.
# @return List of Float - the normalized array.
def normalizeArray(a):

    total = sum(a)
    if total == 0:
        return False

    return [(d*100) / total for d in a]

# PruneWeigths ==========================================
## Remove the influence of deformers that are smaller than threshold.\n
# @param envelope_op Envelope Operator - the envelope operator.
# @param threshold Float - Minimum influence a deformer can have.
# @param remove Boolean - Remove the unsued deformers.
# @param showPBar Boolean - Display a progress bar.
# @return Envelope Operator
def pruneWeights(envelope_op, points=None, threshold=.1, remove=False, showPBar=False):

    # Get weights array
    mesh = envelope_op.Parent3DObject
    point_count = mesh.ActivePrimitive.Geometry.Points.Count
    weights_tuple = envelope_op.Weights.Array
    weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]

    deformer_count = envelope_op.Deformers.Count
    used_deformers = XSIFactory.CreateObject("XSI.Collection")
    used_deformers.Unique = True

    if points is None:
        points = range(point_count)

    if showPBar:
        pbar = uit.progressBar(len(points), 1, str(len(points)) + " points to prune on : "+mesh.Name, "0", False)

    # Prune Weights
    pointsToNormalize = []
    for point_index in points:

        if showPBar:
            pbar.StatusText = point_index

        for deformer_index, deformer in enumerate(envelope_op.Deformers):

            if weights[point_index*deformer_count + deformer_index] <= threshold:
                weights[point_index*deformer_count + deformer_index] = 0
                if not point_index in pointsToNormalize:
                    pointsToNormalize.append(point_index)
            else:
                used_deformers.Add(deformer)

        if showPBar:
            pbar.Increment()

    if showPBar:
        pbar.Visible = False

    # Normalize points
    envelope_op.Weights.Array = weights
    normalizeWeights(envelope_op, pointsToNormalize)
    freezeEnvelope(envelope_op)

    # Rebuilt Envelope ------------------------------------------------
    # If True, we rebuilt the envelope a first time without the unused deformers
    if remove:

        gear.log("There is "+str(envelope_op.Deformers.Count - used_deformers.Count) + " deformers that will be removed")

        path = XSIUtils.ResolvePath("Temp")
        preset_name = mesh.Name +"_Weights"

        env_prop = envelope_op.PortAt(4, 0, 0).Target2
        xsi.SavePreset(env_prop, preset_name, path, None, 1, None, None)
        xsi.RemoveFlexEnv(mesh)

        envelope_op = mesh.ApplyEnvelope(used_deformers)
        env_prop = envelope_op.PortAt(4, 0, 0).Target2

        xsi.LoadPreset(path +"/"+ preset_name, env_prop)

    # Rebuilt the envelope to get the correct colors and normalisation warning
    envelope_op = rebuiltEnvelope(envelope_op)

    return envelope_op

# Average Mirror Weights ================================
## This is for the central line of the mesh, it setthe weight properly splitted between right and left side.
# @param envelope_op Envelope Operator - the envelope operator.
# @param points List of Integer - list of point index to mirror.
def averageMirrorWeights(envelope_op, points):

    weights_tuple = envelope_op.Weights.Array
    weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]
    deformers = envelope_op.Deformers
    deformer_count = deformers.Count

    # Get Mirror Deformer Index
    mirror_deformers = [0] * deformer_count
    for deformer_index, deformer in enumerate(deformers):

        mirror_deformer = deformer.Model.FindChild(uti.convertRLName(deformer.Name))
        if mirror_deformer and isDeformer(envelope_op, mirror_deformer):
            mirror_deformers[deformer_index] = getDeformerIndex(envelope_op, mirror_deformer)
        else:
            mirror_deformers[deformer_index] = deformer_index

  # Replace weights in weight array
    for point_index in points:
        for deformer_index in range(deformer_count):
            weights[point_index*deformer_count + deformer_index] = (weights_tuple[deformer_index][point_index] + weights_tuple[mirror_deformers[deformer_index]][point_index]) * .5

    envelope_op.Weights.Array = weights


# Make Island Rigid =====================================
##
# @param envelope_op Envelope Operator - the envelope operator.
# @param points List of Integer - list of point index to mirror.
def makeIslandRigid(mesh):

	envelope_op = geo.getOperatorFromStack(mesh, "envelopop")

	point_count = mesh.ActivePrimitive.Geometry.Points.Count
	deformer_count = envelope_op.Deformers.Count
	weights_tuple = envelope_op.Weights.Array
	weights = [weights_tuple[j][i] for i in range(len(weights_tuple[0])) for j in range(len(weights_tuple))]
	
	islands = geo.getIslands(mesh, c.siVertexCluster)
	
	for isle in islands:
		
		a = [0] * deformer_count
		for pnt_index in isle:
			for def_index in range(deformer_count):
				a[def_index] +=  weights_tuple[def_index][pnt_index]

		for pnt_index in isle:
			for def_index in range(deformer_count):
				weights[pnt_index*deformer_count + def_index]  = a[def_index]/len(isle)
			
	envelope_op.Weights.Array = weights
	
# =======================================================
## Create a symmetry mapping template for given deformers using the naming convention for right and left objects
# @param in_deformers XSICollection
# @return Property - Mapping Template
def createSymmetryMappingTemplate(in_deformers):

    deformers = XSIFactory.CreateObject("XSI.Collection")
    deformers.AddItems(in_deformers)

    temp_mesh = deformers(0).Model.AddGeometry("Sphere", "MeshSurface", "TempMesh")
    temp_mesh.ApplyEnvelope(deformers, False, False)

    # Create Mapping Template
    mapTemplate = xsi.CreateSymmetryMappingTemplate(temp_mesh, False, 0, False)

    for deformer in deformers:

        # Skip effectors
        if deformer.Type == "eff":
            continue

        sym_deformers = deformer.Model.FindChild(uti.convertRLName(deformer.Name))
        if not sym_deformers or sym_deformers.IsEqualTo(deformer):
            continue

        xsi.AddMappingRule(mapTemplate, deformer.Name, sym_deformers.Name, xsi.GetNumMappingRules(mapTemplate))

    xsi.DeleteObj(temp_mesh)

    return mapTemplate
