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

## @package gear.xsi.shape
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################

import gear

from gear.xsi import xsi, c, XSIFactory

import gear.xsi.utils as uti

##########################################################
# SHAPE
##########################################################
# ========================================================
## Return all the point index deformed by the shape.
# @param shape ShapeKey
# @param threshold Double
# @return List of Integer - The list of index
def getShapePoints(shape, threshold=1E-6):

    mesh = shape.Parent3DObject
    shape_tuple = shape.Elements.Array
    point_count = len(shape_tuple[0])

    return [i for i in range(point_count) if abs(shape_tuple[0][i] + shape_tuple[1][i] + shape_tuple[2][i]) > threshold]

# ========================================================
## Reset the value of selected point in the shape.
# @param shape ShapeKey
# @param points List of Integer - Indexes of point to reset.
def resetShapePoints(shape, points):

    shape_tuple = shape.Elements.Array
    shape_array = [shape_tuple[j][i] for i in range(len(shape_tuple[0])) for j in range(len(shape_tuple)) ]

    # Process
    for i in points:
        shape_array[i*3+0] = 0
        shape_array[i*3+1] = 0
        shape_array[i*3+2] = 0

    shape.Elements.Array = shape_array

# ========================================================
def symmetrizeShapePoints(shape, points):

    # Get Symmetry Map
    mesh = shape.Parent3DObject
    symmetry_map = uti.getSymmetryMap(mesh)
    if not symmetry_map:
        return

    shape_tuple = shape.Elements.Array
    shape_array = [shape_tuple[j][i] for i in range(len(shape_tuple[0])) for j in range(len(shape_tuple)) ]
    symmetry_array = symmetry_map.Elements.Array

    # Process
    for i in points:
        j = int(symmetry_array[0][i])
        shape_array[j*3+0] = - shape_tuple[0][i]
        shape_array[j*3+1] = shape_tuple[1][i]
        shape_array[j*3+2] = shape_tuple[2][i]

    shape.Elements.Array = shape_array

##########################################################
# OPERATOR
##########################################################
# ========================================================
def applyScaleShapeOp(shape, points):

    mesh = shape.Parent3DObject
    cls = mesh.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_ScaleShapeOp_Cls", points)

    # Apply Operator
    op = XSIFactory.CreateObject("gear_ScaleShapeOp")

    op.AddIOPort(shape)
    op.AddInputPort(cls)

    op.Connect(None, c.siConstructionModeModeling)

    return op

# ========================================================
def applySmoothShapeOp(shape, points):

    mesh = shape.Parent3DObject
    cls = mesh.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "gear_SmoothShapeOp_Cls", points)

    # Apply Operator
    op = XSIFactory.CreateObject("gear_SmoothShapeOp")

    op.AddIOPort(shape)
    op.AddInputPort(mesh.ActivePrimitive)
    op.AddInputPort(cls)

    op.Connect(None, c.siConstructionModeModeling)

    return op

##########################################################
# SHAPEKEY
##########################################################
# ========================================================
def duplicateShapeKey(shape, cluster=None):

    if cluster is None:
        cluster = shape.Parent

    shape_array = shape.Elements.Array

    duplicate_shape = xsi.StoreShapeKey(cluster, shape.Name+"_Copy", c.siShapeObjectReferenceMode, 1, None, None, c.siShapeContentSecondaryShape, True)
    duplicate_shape.Elements.Array = shape_array
    xsi.ApplyShapeKey(duplicate_shape, None, None, 100, None, None, None, 2)
    xsi.FreezeObj(duplicate_shape)

    return duplicate_shape

# ========================================================
def resetShapeKey(shape):

    mesh = shape.Parent3DObject

    shape_array = [0] * 3 * mesh.ActivePrimitive.Geometry.Points.Count
    shape.Elements.Array = shape_array

# ========================================================
def mergeShapeKeys(shapes):

    cls = shapes[0].Parent

    merged_array = [0] * 3 * cls.Parent3DObject.ActivePrimitive.Geometry.Points.Count
    for shape in shapes:
        shape_tuple = shape.Elements.Array

        for i in range(len(shape_tuple[0])):
            merged_array[i*3+0] += shape_tuple[0][i]
            merged_array[i*3+1] += shape_tuple[1][i]
            merged_array[i*3+2] += shape_tuple[2][i]

    cls = shapes[0].Parent

    merged_shape = xsi.StoreShapeKey(cls, "shapeKey_merged", c.siShapeObjectReferenceMode, 1, None, None, c.siShapeContentSecondaryShape, True)
    merged_shape.Elements.Array = merged_array

    xsi.ApplyShapeKey(merged_shape, None, None, 100, None, None, None, 2)
    xsi.FreezeObj(merged_shape)

    return merged_shape

# ========================================================
def mirrorShapeKey(shape):

    # Get Symmetry Map
    mesh = shape.Parent3DObject
    symmetry_map = uti.getSymmetryMap(mesh)
    if not symmetry_map:
        gear.log("There is no symmetry map available on this mesh", gear.sev_warning)
        return

    cls = shape.Parent
    shape_tuple = shape.Elements.Array
    symmetry_array = symmetry_map.Elements.Array

    shape_array = [0] * len(shape_tuple[0])*3

    # Process
    for iPntIndex in cls.Elements:

        iSymIndex = int(symmetry_array[0][iPntIndex])

        shape_array[iSymIndex*3+0] = - shape_tuple[0][iPntIndex]
        shape_array[iSymIndex*3+1] = shape_tuple[1][iPntIndex]
        shape_array[iSymIndex*3+2] = shape_tuple[2][iPntIndex]

    duplicate_shape = xsi.StoreShapeKey(cls, shape.Name+"_Mirror", c.siShapeObjectReferenceMode, 1, None, None, c.siShapeContentSecondaryShape, True)
    duplicate_shape.Elements.Array = shape_array
    xsi.ApplyShapeKey(duplicate_shape, None, None, 100, None, None, None, 2)
    xsi.FreezeObj(duplicate_shape)

    return duplicate_shape

# ========================================================
def matchShapeKey(target_shape, source_shape):
    target_shape.Elements.Array = source_shape.Elements.Array

# ========================================================
def createHalfShape(shape, c_points, prefix, opp_points):

    new_shape = xsi.StoreShapeKey(shape.Parent, prefix + shape.Name, c.siShapeObjectReferenceMode)
    shape_tuple = shape.Elements.Array
    shape_array = [shape_tuple[j][i] for i in range(len(shape_tuple[0])) for j in range(len(shape_tuple))]

    for i in opp_points:
        shape_array[i*3+0] = 0
        shape_array[i*3+1] = 0
        shape_array[i*3+2] = 0

    for i in c_points:
        shape_array[i*3+0] *= 0.5
        shape_array[i*3+1] *= 0.5
        shape_array[i*3+2] *= 0.5

    new_shape.Elements.Array = shape_array

    xsi.ApplyShapeKey(new_shape, None, None, 100, None, None, None, 2)
    xsi.FreezeObj(new_shape)

    return new_shape

##########################################################
# MISC
##########################################################
# getPoints ==============================================
def getPoints(geo, side, threshold=1E-6):

    points = []
    for point in geo.Points:

        if point.Position.X > threshold and side == "L":
            points.append(point.Index)

        elif point.Position.X < -threshold and side == "R":
            points.append(point.Index)

        elif point.Position.X <= threshold and point.Position.X >= -threshold and side == "C":
            points.append(point.Index)

    return points
