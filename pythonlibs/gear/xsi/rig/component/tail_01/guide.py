'''

    This file is part of GEAR.

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

    Author:     Jeremie Passerin      geerem@hotmail.com
    Url:        http://gear.jeremiepasserin.com
    Date:       2010 / 11 / 15

'''

## @package gear.xsi.rig.component.tail_01.guide
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import c

from gear.xsi.rig.component.guide import ComponentGuide

# guide info
AUTHOR = "Jeremie Passerin"
URL = "http://www.jeremiepasserin.com"
EMAIL = "geerem@hotmail.com"
VERSION = [1,0,1]
TYPE = "tail_01"
NAME = "tail"
DESCRIPTION = "chain component with spring operator"

##########################################################
# CLASS
##########################################################
class Guide(ComponentGuide):

    compType = TYPE
    compName = NAME
    description = DESCRIPTION

    author = AUTHOR
    url = URL
    email = EMAIL
    version = VERSION

    compatible = ["chain_01", "chain_cns_01"]

    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.pick_transform = ["root", "#_loc"]
        self.save_transform = ["root", "#_loc"]
        self.save_blade = ["blade"]
        self.addMinMax("#_loc", 1, -1)

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.locs = self.addLocMulti("#_loc", self.root)
        self.blade = self.addBlade("blade", self.root, self.locs[0])

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        self.pSpeed = self.addParam("speed", c.siDouble, .5, 0, None, 0, 1)
        self.pDamping = self.addParam("damping", c.siDouble, .7, 0, None, 0, 1)
        self.pBlend = self.addParam("blend", c.siDouble, .7, 0, None, 0, 1)

        self.pMultiBlend = self.addParam("multi_blend", c.siBool, True)

    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):

        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        group = tab.addGroup("Spring")
        group.addItem(self.pSpeed.scriptName, "Speed")
        group.addItem(self.pDamping.scriptName, "Damping")
        group.addItem(self.pBlend.scriptName, "Blend")

        group.addItem(self.pMultiBlend.scriptName, "Multi Blend")

    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):
        return