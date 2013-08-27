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

## @package gear.xsi.rig.component.foot_bk_01.guide
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c, XSIMath

from gear.xsi.rig.component.guide import ComponentGuide

# guide info
AUTHOR = "Jeremie Passerin"
URL = "http://www.jeremiepasserin.com"
EMAIL = "geerem@hotmail.com"
VERSION = [1,0,0]
TYPE = "foot_bk_01"
NAME = "foot"
DESCRIPTION = "Foot with reversed controlers to control foot roll."

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

    connectors = ["leg_2jnt_01", "leg_2jnt_02", "leg_3jnt_01"]

    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.pick_transform = ["root", "#_loc"]
        self.save_transform = ["root", "#_loc", "heel", "outpivot", "inpivot"]
        self.addMinMax("#_loc", 1, -1)

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.locs = self.addLocMulti("#_loc", self.root)

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)

        # Heel and pivots
        vHeel = XSIMath.CreateVector3(self.root.Kinematics.Global.PosX.Value, 0, self.root.Kinematics.Global.PosZ.Value)
        vLeftPivot = XSIMath.CreateVector3(self.root.Kinematics.Global.PosX.Value + .3, 0, self.root.Kinematics.Global.PosZ.Value)
        vRightPivot = XSIMath.CreateVector3(self.root.Kinematics.Global.PosX.Value - .3, 0, self.root.Kinematics.Global.PosZ.Value)

        self.heel = self.addLoc("heel", self.root, vHeel)
        self.outpivot = self.addLoc("outpivot", self.root, vLeftPivot)
        self.inpivot = self.addLoc("inpivot", self.root, vRightPivot)

        self.dispcrv = self.addDispCurve("1", [self.root, self.heel, self.outpivot, self.heel, self.inpivot])

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        self.pRoll = self.addParam("roll", c.siInt4, 0, 0, 1)

    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):

        # --------------------------------------------------
        # Items
        rollItems = ["Controler", 0, "Slider", 1]

        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        # Roll
        group = tab.addGroup("Roll")
        item = group.addEnumControl(self.pRoll.scriptName, rollItems, "Roll with", c.siControlCombo)

    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):
        return
