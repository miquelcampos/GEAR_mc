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

## @package gear.xsi.weightmap
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
from gear.xsi import xsi, dynDispatch

##########################################################
# WEIGHTMAP
##########################################################
# ========================================================
## Create a new weight map to given cluster.
# @param cls Cluster
# @param name String - The name of the weightmap
# @param min_value Double - The minimum limit of the weightmap
# @param max_value Double - The maximum limit of the weightmap
# @return Property - The newly created WeightMap
def addWeightMap(cls, name="WeightMap", min_value=None, max_value=None):

    # We cannot set the min and max if we create the weightmap with this way
    # wmap = cls.AddProperty("Weight Map Property", False, name)

    wmap = xsi.CreateWeightMap("WeightMap", cls, name, "Weight Map Property", False)(0)
    setWeightMapMinMax(wmap, min_value, max_value)

    return wmap

# ========================================================
## Set the min and max value of the weightmap.
# @param wmap WeightMap
# @param min_value Double - The minimum limit of the weightmap
# @param max_value Double - The maximum limit of the weightmap
# @return Boolean - False if fails
def setWeightMapMinMax(wmap, min_value=None, max_value=None):

    if not dynDispatch(wmap.NestedObjects("Weight Map Generator")):
        return False

    min_param = dynDispatch(wmap.NestedObjects("Weight Map Generator").NestedObjects("Minimum"))
    max_param = dynDispatch(wmap.NestedObjects("Weight Map Generator").NestedObjects("Maximum"))

    if min_value is not None:
        min_param.Value = min_value

    if max_value is not None:
        max_param.Value = max_value

    return True

##########################################################
# WEIGHTMAP POINTS
##########################################################
# ========================================================
## Return all the point index affected by the weightmap.
# @param wmap WeightMap
# @param threshold Double
# @return List of Integer - The list of index
def getWeightMapPoints(wmap, threshold=1E-6):

    cls = wmap.Parent
    aWmap = wmap.Elements.Array[0]
    clsElements = cls.Elements.Array

    points = [clsElements[x] for x, v in enumerate(aWmap) if v > threshold]

    return points

# ========================================================
## Reset the value of selected point in the weightmap.
# @param wmap WeightMap
# @param points List of Integer - Indexes of point to reset.
def resetWeightMapPoints(wmap, points):

    weights = [w for w in wmap.Elements.Array[0]]

    # Process
    for i in points:
       weights[i] = 0.0

    wmap.Elements.Array = weights
