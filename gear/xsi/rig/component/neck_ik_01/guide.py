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

## @package gear.xsi.rig.component.neck_ik_01.guide
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c

from gear.xsi.rig.component.guide import ComponentGuide
import gear.xsi.vector as vec

# guide info
AUTHOR = "Jeremie Passerin"
URL = "http://www.jeremiepasserin.com"
EMAIL = "geerem@hotmail.com"
VERSION = [1,0,0]
TYPE = "neck_ik_01"
NAME = "neck"
DESCRIPTION = "pretty similar to the ik spine with an over top layer of fk controlers that follow the ik position."

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
        self.pick_transform = ["root", "neck", "head", "eff"]
        self.save_transform = ["root", "tan0", "tan1", "neck", "head", "eff"]
        self.save_blade = ["blade"]

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.neck = self.addLoc("neck", self.root)
        self.head = self.addLoc("head", self.neck)
        self.eff = self.addLoc("eff", self.head)

        v0 = vec.linearlyInterpolate(self.root.Kinematics.Global.Transform.Translation, self.neck.Kinematics.Global.Transform.Translation, .333)
        self.tan0 = self.addLoc("tan0", self.root, v0)
        v1 = vec.linearlyInterpolate(self.root.Kinematics.Global.Transform.Translation, self.neck.Kinematics.Global.Transform.Translation, .666)
        self.tan1 = self.addLoc("tan1", self.neck, v1)

        self.blade = self.addBlade("blade", self.root, self.tan0)

        centers = [self.root, self.tan0, self.tan1, self.neck]
        self.dispcrv = self.addDispCurve("neck_crv", centers, 3)

        centers = [self.neck, self.head, self.eff]
        self.dispcrv = self.addDispCurve("head_crv", centers, 1)

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        # Ik
        self.pHeadRef      = self.addParam("headref", c.siInt4, None, 0, None)
        self.pHeadRefArray = self.addParam("headrefarray", c.siString, "", )
        self.pIkRef        = self.addParam("ikref", c.siInt4, None, 0, None)
        self.pIkRefArray   = self.addParam("ikrefarray", c.siString, "")

        # Default values
        self.pMaxStretch = self.addParam("maxstretch", c.siDouble, 1.5, 1, None, 1, 3)
        self.pMaxSquash = self.addParam("maxsquash", c.siDouble, .5, 0, 1, 0, 1)
        self.pSoftness = self.addParam("softness", c.siDouble, 0.5, 0, 1, 0, 1)

        # Options
        self.pDivision = self.addParam("division", c.siInt4, 3, 3, None, 3, 10)

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
        headItemsCode = "headrefItems = []" +"\r\n"+\
                      "if PPG."+self.pHeadRefArray.scriptName+".Value:" +"\r\n"+\
                      "    a = PPG."+self.pHeadRefArray.scriptName+".Value.split(',')" +"\r\n"+\
                      "    for i, v in enumerate(a):" +"\r\n"+\
                      "        headrefItems.append(a[i])" +"\r\n"+\
                      "        headrefItems.append(i)" +"\r\n"+\
                      "item.UIItems = headrefItems" +"\r\n"

        ikItemsCode = "ikrefItems = []" +"\r\n"+\
                      "if PPG."+self.pIkRefArray.scriptName+".Value:" +"\r\n"+\
                      "    a = PPG."+self.pIkRefArray.scriptName+".Value.split(',')" +"\r\n"+\
                      "    for i, v in enumerate(a):" +"\r\n"+\
                      "        ikrefItems.append(a[i])" +"\r\n"+\
                      "        ikrefItems.append(i)" +"\r\n"+\
                      "item.UIItems = ikrefItems" +"\r\n"

        fcurveItems = ["Stretch", 0, "Squash", 1]

        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        # IK/Upv References
        group = tab.addGroup("IK References")

        row = group.addRow()
        item = row.addEnumControl(self.pHeadRef.scriptName, [], "Head Ref", c.siControlCombo)
        item.setCodeAfter(headItemsCode)
        row.addButton("PickHeadRef", "Pick New")
        row.addButton("DeleteHeadRef", "Delete")
        # item = group.addItem(self.pHeadRefArray.scriptName, "")
        # item.setAttribute(c.siUINoLabel, True)

        row = group.addRow()
        item = row.addEnumControl(self.pIkRef.scriptName, [], "IK", c.siControlCombo)
        item.setCodeAfter(ikItemsCode)
        row.addButton("PickIkRef", "Pick New")
        row.addButton("DeleteIkRef", "Delete")
#        item = group.addItem(self.pIkRefArray.scriptName, "")
#        item.setAttribute(c.siUINoLabel, True)

        group = tab.addGroup("Stretch Default Values")
        group.addItem(self.pMaxStretch.scriptName, "Max Stretch")
        group.addItem(self.pMaxSquash.scriptName, "Max Squash")
        group.addItem(self.pSoftness.scriptName, "Softness")

        # Divisions ---------------------------------------------
        tab = self.layout.addTab("Division")
        group = tab.addGroup("Division")
        group.addItem(self.pDivision.scriptName, "Count")

        # FCurves
        group = tab.addGroup("FCurves")
        group.addEnumControl(self.pFCurveCombo.scriptName, fcurveItems, "FCurve", c.siControlCombo)

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

        self.logic.addOnClicked("PickHeadRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.pickReferences(prop, '"+self.pHeadRefArray.scriptName+"', '"+self.pHeadRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("DeleteHeadRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.deleteReference(prop, '"+self.pHeadRefArray.scriptName+"', '"+self.pHeadRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("PickIkRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.pickReferences(prop, '"+self.pIkRefArray.scriptName+"', '"+self.pIkRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("DeleteIkRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.deleteReference(prop, '"+self.pIkRefArray.scriptName+"', '"+self.pIkRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")