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

## @package gear.xsi.rig.component.arm_2jnt_02.guide
# @author Jeremie Passerin
# @modify by Miquel Campos

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c

from gear.xsi.rig.component.guide import ComponentGuide

# guide info
AUTHOR = "Jeremie Passerin, Miquel Campos"
URL = "http://www.jeremiepasserin.com, http://www.miqueltd.com"
EMAIL = "geerem@hotmail.com"
VERSION = [1,0,1]
TYPE = "arm_2jnt_02"
NAME = "arm"
DESCRIPTION = "Arm with stretch, roundess, ik/fk.... . This modification of the version 01 and expose the tangency control in the arms. "

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

    compatible = ["arm_2jnt_01"]

    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.pick_transform = ["root", "elbow", "wrist", "eff"]
        self.save_transform = ["root", "elbow", "wrist", "eff"]

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.elbow = self.addLoc("elbow", self.root)
        self.wrist = self.addLoc("wrist", self.elbow)
        self.eff = self.addLoc("eff", self.wrist)

        self.dispcrv = self.addDispCurve("crv", [self.root, self.elbow, self.wrist, self.eff])

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        # Default Values
        self.pBlend         = self.addParam("blend", c.siInt4, 0, 0, 1)
        self.pIkRef         = self.addParam("ikref", c.siInt4, None, 0, None)
        self.pIkRefArray  = self.addParam("ikrefarray", c.siString, "")
        self.pUpvRef        = self.addParam("upvref", c.siInt4, None, 0, None)
        self.pUpvRefArray = self.addParam("upvrefarray", c.siString, "")
        self.pMaxStretch  = self.addParam("maxstretch", c.siDouble, 1.5 , 1, None, 1, 3)

        # Divisions
        self.pDiv0 = self.addParam("div0", c.siInt4, 2, 1, None, 1, 10)
        self.pDiv1 = self.addParam("div1", c.siInt4, 2, 1, None, 1, 10)

        # FCurves
        self.pFCurveCombo = self.addParam("fcurvecombo", c.siInt4, 0, 0, None)
        self.pSt_profile = self.addFCurveParam("st_profile", [[0,-25],[40,-100],[100,-10]])
        self.pSq_profile = self.addFCurveParam("sq_profile", [[0,10],[40,100],[100,10]])

    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):

        # --------------------------------------------------
        # Items
        blendItems = ["fk", 0, "ik", 1]

        ikItemsCode = "ikrefItems = []" +"\r\n"+\
                      "if PPG."+self.pIkRefArray.scriptName+".Value:" +"\r\n"+\
                      "    a = PPG."+self.pIkRefArray.scriptName+".Value.split(',')" +"\r\n"+\
                      "    for i, v in enumerate(a):" +"\r\n"+\
                      "        ikrefItems.append(a[i])" +"\r\n"+\
                      "        ikrefItems.append(i)" +"\r\n"+\
                      "item.UIItems = ikrefItems" +"\r\n"

        upvItemsCode = "upvrefItems = []" +"\r\n"+\
                      "if PPG."+self.pUpvRefArray.scriptName+".Value:" +"\r\n"+\
                      "    a = PPG."+self.pUpvRefArray.scriptName+".Value.split(',')" +"\r\n"+\
                      "    for i, v in enumerate(a):" +"\r\n"+\
                      "        upvrefItems.append(a[i])" +"\r\n"+\
                      "        upvrefItems.append(i)" +"\r\n"+\
                      "item.UIItems = upvrefItems" +"\r\n"

        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        # IK / FK
        group = tab.addGroup("IK / FK")
        item = group.addEnumControl(self.pBlend.scriptName, blendItems, "Default blend", c.siControlCombo)

        # IK/Upv References
        group = tab.addGroup("IK Reference")

        row = group.addRow()
        item = row.addEnumControl(self.pIkRef.scriptName, [], "IK", c.siControlCombo)
        item.setCodeAfter(ikItemsCode)
        row.addButton("PickIkRef", "Pick New")
        row.addButton("DeleteIkRef", "Delete")
#        item = group.addItem(self.pIkRefArray.scriptName, "")
#        item.setAttribute(c.siUINoLabel, True)

        row = group.addRow()
        item = row.addEnumControl(self.pUpvRef.scriptName, [], "Up Vector", c.siControlCombo)
        item.setCodeAfter(upvItemsCode)
        row.addButton("PickUpvRef", "Pick New")
        row.addButton("DeleteUpvRef", "Delete")
#        item = group.addItem(self.pUpvRefArray.scriptName, "")
#        item.setAttribute(c.siUINoLabel, True)

        # Stretch
        group = tab.addGroup("Stretch Default Values")
        group.addItem(self.pMaxStretch.scriptName, "Max Stretch")

        # Divisions ---------------------------------------------
        tab = self.layout.addTab("Divisions")
        group = tab.addGroup("Divisions")
        row = group.addRow()
        row.addItem(self.pDiv0.scriptName, "Bone 0")
        row.addItem(self.pDiv1.scriptName, "Bone 1")

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

        self.logic.addOnClicked("PickIkRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.pickReferences(prop, '"+self.pIkRefArray.scriptName+"', '"+self.pIkRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("DeleteIkRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.deleteReference(prop, '"+self.pIkRefArray.scriptName+"', '"+self.pIkRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("PickUpvRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.pickReferences(prop, '"+self.pUpvRefArray.scriptName+"', '"+self.pUpvRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("DeleteUpvRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.deleteReference(prop, '"+self.pUpvRefArray.scriptName+"', '"+self.pUpvRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")
