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

## @package gear.xsi.rig.component.chain_01.guide
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
TYPE = "chain_01"
NAME = "chain"
DESCRIPTION = "Simple ik/fk chain"

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

    compatible = ["tail_01", "chain_cns_01"]

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

        self.pType = self.addParam("type", c.siInt4, 0, 0, None)
        self.pBlend = self.addParam("blend", c.siInt4, 0, 0, 1)
        
        self.pNeutralPose = self.addParam("neutralpose", c.siBool, False)

    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):

        # --------------------------------------------------
        # Items
        typeItems = ["fk only", 0,
                     "ik only", 1,
                     "ik / fk", 2]

        blendItems = ["fk", 0,
                      "ik", 1]

        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        group = tab.addGroup("Kinematic")
        group.addEnumControl(self.pType.scriptName, typeItems, "Type", c.siControlCombo)
        item = group.addItem(self.pNeutralPose.scriptName, "Set Neutral Pose on FK Controlers")   
        item.addCondition("PPG."+self.pType.scriptName+".Value != 1")  
        item = group.addEnumControl(self.pBlend.scriptName, blendItems, "Default blend", c.siControlCombo)
        item.addCondition("PPG."+self.pType.scriptName+".Value == 2")   

    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):

        self.logic.addOnChangedRefresh(self.pType.scriptName)

