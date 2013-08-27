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

## @package gear.xsi.rig.component.spine_ik_01.guide
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c

from gear.xsi.rig.component.guide import ComponentGuide

# guide info
AUTHOR = "Jeremie Passerin"
URL = "http://www.jeremiepasserin.com"
EMAIL = "geerem@hotmail.com"
VERSION = [1,0,0]
TYPE = "spine_ik_01"
NAME = "spine"
DESCRIPTION = "an ik spine with an over top layer of fk controlers that follow the ik position."

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
    
    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.pick_transform = ["root", "eff"]
        self.save_transform = ["root", "eff"]
        self.save_blade = ["blade"]

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.eff = self.addLoc("eff", self.root)
        self.blade = self.addBlade("blade", self.root, self.eff)

        centers = [self.root, self.eff]
        self.dispcrv = self.addDispCurve("crv", centers)

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        # Default values
        self.pPosition = self.addParam("position", c.siDouble, 0, 0, 1, 0, 1)
        self.pMaxStretch = self.addParam("maxstretch", c.siDouble, 1.5, 1, None, 1, 3)
        self.pMaxSquash = self.addParam("maxsquash", c.siDouble, .5, 0, 1, 0, 1)
        self.pSoftness = self.addParam("softness", c.siDouble, 0.5, 0, 1, 0, 1)
        self.pLockOri = self.addParam("lock_ori", c.siDouble, 1, 0, 1, 0, 1)

        # Options
        self.pDivision = self.addParam("division", c.siInt4, 5, 3, None, 3, 10)

        # FCurves
        self.pFCurveCombo = self.addParam("fcurvecombo", c.siInt4, 0, 0, None)
        self.pSt_profile = self.addFCurveParam("st_profile", [[0,-25],[40,-100],[100,-10]])
        self.pSq_profile = self.addFCurveParam("sq_profile", [[0,10],[40,100],[100,10]])

    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):

        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        group = tab.addGroup("Stretch Default Values")
        group.addItem(self.pPosition.scriptName, "Base/Top")
        group.addItem(self.pMaxStretch.scriptName, "Max Stretch")
        group.addItem(self.pMaxSquash.scriptName, "Max Squash")
        group.addItem(self.pSoftness.scriptName, "Softness")
        group.addItem(self.pLockOri.scriptName, "Lock Orientation")

        # Divisions ---------------------------------------------
        tab = self.layout.addTab("Division")
        group = tab.addGroup("Division")
        group.addItem(self.pDivision.scriptName, "Count")

        # FCurves
        group = tab.addGroup("FCurves")
        group.addEnumControl(self.pFCurveCombo.scriptName, ["Stretch", 0, "Squash", 1], "FCurve", c.siControlCombo)

        fcv_item = group.addFCurve2(self.pSt_profile.scriptName, "Divisions", "Stretch", -10, 110, 10, -110, 5, 5)
        fcv_item.addCondition("PPG."+self.pFCurveCombo.scriptName+".Value == 0")
        fcv_item = group.addFCurve2(self.pSq_profile.scriptName, "Divisions", "Squash", -10, 110, -10, 110, 5, 5)
        fcv_item.addCondition("PPG."+self.pFCurveCombo.scriptName+".Value == 1")
    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):

        self.logic.addGlobalCode("from gear.xsi.rig.component import logic\r\nreload(logic)")

        self.logic.addOnChangedRefresh(self.pFCurveCombo.scriptName)
