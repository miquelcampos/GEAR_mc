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

## @package gear.xsi.icetree
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
from gear.xsi import xsi, c

##########################################################
# ICE TREE
##########################################################
# ========================================================
## Create a new weight map to given cluster.
# @param obj
# @param construction_mode Integer
# @return Operator - The newly created Ice Tree Operator
def addIceTree(obj, construction_mode=c.siConstructionModeDefault):
    
    tree = xsi.ApplyOp("ICETree", obj, c.siNode, None, None, construction_mode)
    
    return tree
    