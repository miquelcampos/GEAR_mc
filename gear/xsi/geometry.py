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

## @package gear.xsi.geometry
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c, XSIFactory, dynDispatch, XSIMath
import gear.xsi.utils as uti

##########################################################
# SUBCOMPONENT
##########################################################
# getSymSubComponent =====================================
## get the symmetrical suncomponent indices.
# @param indexes List of Integer - List of subcomponent index to mirror.
# @param subcomponentType String - Type of subcomponent. (pntSubComponent, polySubComponent or edgeSubComponent)
# @param mesh Geometry - The owner mesh.
# @return List of Integer - The list of symmetrical indices.
def getSymSubComponent(indexes, subcomponentType, mesh):

     symmetryMap = uti.getSymmetryMap(mesh)
     if not symmetryMap:
          return False

     symmetryArray = symmetryMap.Elements.Array[0]
     symIndexes = []

     geometry = dynDispatch(mesh.ActivePrimitive.Geometry)

     # Point Cluster ---------------------------
     if subcomponentType == "pntSubComponent":
          for pointIndex in indexes:
                symIndexes.append(symmetryArray[pointIndex])

     # Polygon Cluster -------------------------
     elif subcomponentType == "polySubComponent":

          for polyIndex in indexes:

                # Get Symmetrical Polygon Points
                symPoints = []
                for vertex in geometry.Polygons(polyIndex).Vertices:
                     symPoints.append(symmetryArray[vertex.Index])

                # Get symmetrical Polygons (Get too much polygons, we filter them right after)
                aSymPolygons = []
                for pointIndex in symPoints:
                     for polygon in geometry.Vertices(pointIndex).NeighborPolygons(1):
                          if polygon.Index not in aSymPolygons:
                                aSymPolygons.append(polygon.Index)

                # Find the good one (the one which all points belongs to the symmetrical array)
                for polyIndex in aSymPolygons:
                     polygon = geometry.Polygons(polyIndex)

                     b = True
                     for vertex in polygon.Vertices:
                          if vertex.Index not in symPoints:
                                b = False
                                break

                     if b:
                          symIndexes.append(polyIndex)

     # Edge Cluster ----------------------------
     elif subcomponentType == "edgeSubComponent":

          for edgeIndex in indexes:

                # Get Edge Points
                symPoints = []
                for vertex in geometry.Edges(edgeIndex).Vertices:
                     symPoints.append(symmetryArray[vertex.Index])

                # Get symmetrical Edges (Get too much edges, we filter them right after)
                aSymEdges = []
                for pointIndex in symPoints:
                     for edge in geometry.Vertices(pointIndex).NeighborEdges(1):
                          if edge.Index not in aSymEdges:
                                aSymEdges.append(edge.Index)

                # Find the good one (the one which all points belongs to the symmetrical array)
                for edgeIndex in aSymEdges:
                     edge = geometry.Edges(edgeIndex)

                     b = True
                     for vertex in edge.Vertices:
                          if vertex.Index not in symPoints:
                                b = False
                                break

                     if b:
                          symIndexes.append(edgeIndex)

     return symIndexes

# ========================================================
## Create a symmetrical cluster
# @param cls Cluster
# @return Cluster
def mirrorCluster(cls):

    mesh = cls.Parent3DObject
    mirror_component = getSymSubComponent(cls.Elements, cls.Type+"SubComponent", mesh)

    mirror_cls = mesh.ActivePrimitive.Geometry.AddCluster(cls.Type, uti.convertRLName(cls.Name), mirror_component)

    return mirror_cls

##########################################################
# CONSTRUCTION HISTORY
##########################################################
# ========================================================
## Return True if given geometry has an empty stack of deformers
# @param Geometry
# @return Boolean
def isFrozen(obj):
    if obj.ActivePrimitive.NestedObjects.Count <= 5:
        return True
    else:
        return False

# getOperatorFromStack ===================================
## Return an operator of given type from the deformer stack of given geometry
# @param obj Geometry - The geometry to check.
# @param opType String - The type of the operator to find.
# @param firstOnly Boolean - Only return first matching operator.
# @return An operator if firstOnly is true, a collection of operator if it's false, False if there is no such operator.
def getOperatorFromStack(obj, opType, firstOnly=True):

     operators = XSIFactory.CreateObject("XSI.Collection")

     for nested in obj.ActivePrimitive.NestedObjects:
          if nested.IsClassOf(c.siOperatorID):
                if nested.Type == opType:
                     if firstOnly:
                          return nested
                     else:
                          operators.Add(nested)

     if operators.Count:
          return operators

     return False
##########################################################
# POLYMESH
##########################################################
# ========================================================
## Return the indexes of point with a certian number of edges connected to them
# @param obj Geometry
# @param count Integer - Number of edges we are looking for
# @param equalOrSuperior - True to also return point with more than the given count
# @return List of Integer
def getStars(obj, count, equalOrSuperior=False):

    stars = []

    for vertex in obj.ActivePrimitive.Geometry.Vertices:

        if equalOrSuperior:
            if vertex.NeighborEdges().Count >= count:
                stars.append(vertex.Index)
        else:
            if vertex.NeighborEdges().Count == count:
                stars.append(vertex.Index)

    return stars

# ========================================================
## Merge geometries and keep the clusters
# @param objects List of Polymesh
# @return Operator - The merge operator
def mergeWithClusters(objects):

    # Apply Merge Operator -------------------------------
    merge_op = xsi.ApplyGenOp("MeshMerge", "", objects, 3, c.siPersistentOperation, c.siKeepGenOpInputs, None)(0)
    merged_mesh = merge_op.OutputPorts(0).Target2.Parent

    # Merge Clusters -------------------------------------
    # Init subcomponent count
    point_count = 0
    face_count = 0
    edge_count = 0
    sample_count = 0

    # Loop on objects to recreate the clusters
    for i, obj in enumerate(objects):

        # Add last object subcomponent count to total
        if i > 0:
            last_geo = objects[i-1].ActivePrimitive.Geometry

            point_count += last_geo.Vertices.Count
            face_count += last_geo.Polygons.Count
            edge_count += last_geo.Edges.Count
            sample_count += last_geo.Samples.Count

        # Cycle on clusters to be recreate
        for cls in obj.ActivePrimitive.Geometry.Clusters:

            cls_type = cls.Type

            if cls_type == "poly":
                sub_count = face_count
            elif cls_type == "pnt":
                sub_count = point_count
            elif cls_type == "edge":
                sub_count = edge_count
            elif cls_type == "sample":
                sub_count = sample_count
            else:
                continue

            # Offset Cluster Elements Indexes
            cls_indexes = []
            for i in cls.Elements:
                cls_indexes.append(i+sub_count)

            # Create the cluster
            merged_mesh.ActivePrimitive.Geometry.AddCluster(cls_type, obj.Name +"_"+ cls.Name, cls_indexes)

    return merge_op

# ========================================================
## Split a geometry into sub island component
# @param obj Polymesh
# @return List of Polymesh
def splitPolygonIsland(obj):

    sub_indexes = getIslands(obj, c.siPolygonCluster)
    geometry = obj.ActivePrimitive.Geometry

    islands = []
    for i, sub in enumerate(sub_indexes):
        isle = xsi.ExtractFromComponents("ExtractPolygonsOp", obj.FullName+".poly"+str(sub), obj.Name+"_island_%s"%i, None, c.siPersistentOperation, c.siKeepGenOpInputs)(0)(0)
        islands.append(isle)

    return islands

# ========================================================
## Create an cluster of type clsType for each island
# @param obj Polymesh
# @return List of Clusters
def createIslandsClusters(obj, clsType=c.siPolygonCluster):

    sub_indexes = getIslands(obj, clsType)
    geometry = obj.ActivePrimitive.Geometry

    clusters = []
    for i, sub in enumerate(sub_indexes):
        cls = geometry.AddCluster(clsType, "Island_%s"%i, sub)
        clusters.append(cls)

# ========================================================
## Return a list of subcomponent indexes
# @param obj Polymesh
# @return List of List of Integer
def getIslands(obj, clsType=c.siPolygonCluster):

    geometry = obj.ActivePrimitive.Geometry

    # Polygon Islands
    if clsType == c.siPolygonCluster :
        indexes = range(geometry.Polygons.Count)

        islands = []
        while indexes:

            depth = 1
            old_count = 0

            while True:

                start_polygon = geometry.Polygons(indexes[0])

                neighbors = start_polygon.NeighborPolygons(depth)

                if neighbors.Count == old_count:
                    isle = [poly.Index for poly in neighbors]
                    isle.append(start_polygon.Index)
                    for i in isle:
                        indexes.remove(i)
                    break

                depth += 1
                old_count = neighbors.Count

            islands.append(isle)

        return islands

    # Vertex Islands
    elif clsType == c.siVertexCluster :
        indexes = range(geometry.Vertices.Count)

        islands = []
        while indexes:

            depth = 1
            old_count = 0

            while True:

                start_vertex = geometry.Vertices(indexes[0])

                neighbors = start_vertex.NeighborVertices(depth)

                if neighbors.Count == old_count:
                    isle = [vertex.Index for vertex in neighbors]
                    isle.append(start_vertex.Index)
                    for i in isle:
                        indexes.remove(i)
                    break

                depth += 1
                old_count = neighbors.Count

            islands.append(isle)

        return islands

    # Edge Islands
    elif clsType == c.siEdgeCluster :
        indexes = range(geometry.Edges.Count)

        islands = []
        while indexes:

            depth = 1
            old_count = 0

            while True:

                start_edge = geometry.Edges(indexes[0])

                neighbors = start_edge.NeighborEdges(depth)

                if neighbors.Count == old_count:
                    isle = [edge.Index for edge in neighbors]
                    isle.append(start_edge.Index)
                    for i in isle:
                        indexes.remove(i)
                    break

                depth += 1
                old_count = neighbors.Count

            islands.append(isle)

        return islands

# ========================================================
## Create a null for each given point of the geometry and apply a ClusterCenter op
# @param obj Geometry
# @param pnt_index List of Integer - The indexes of the points (None to work on all the points)
# @return List of Null - The newly created centers
def addClusterCenter(obj, pnt_index=[]):

    obj_geo = obj.ActivePrimitive.Geometry

    if not pnt_index:
        pnt_index = range(obj_geo.Points.Count)

    centers = []
    for i in pnt_index:
        cluster = obj_geo.AddCluster(c.siVertexCluster, "center_%s"%i, [i])

        t = XSIMath.CreateTransform()
        t.SetTranslation(obj_geo.Points(i).Position)
        center = obj.AddNull("center_%s"%i)
        center.Kinematics.Global.Transform = t

        xsi.ApplyOp( "ClusterCenter", cluster.FullName+";"+center.FullName, 0, 0, None, 2)

        centers.append(center)

    return centers

