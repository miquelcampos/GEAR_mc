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

## @package gear.xsi.rig.component.eye_01.guide
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
TYPE = "eye_01"
NAME = "eye"
DESCRIPTION = "Simple eye rig"

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
        self.pick_transform = ["root", "lookat"]
        self.save_transform = ["root", "lookat"]
        self.save_primitive = []

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.lookat = self.addLoc("lookat", self.root)
        
        self.dispcrv = self.addDispCurve("crv", [self.root, self.lookat])

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):
        
        self.pIkRef      = self.addParam("ikref", c.siInt4, None, 0, None)
        self.pIkRefArray = self.addParam("ikrefarray", c.siString, "")
        
    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):
        
        # --------------------------------------------------
        # Items
        ikItemsCode = "ikrefItems = []" +"\r\n"+\
                      "if PPG."+self.pIkRefArray.scriptName+".Value:" +"\r\n"+\
                      "    a = PPG."+self.pIkRefArray.scriptName+".Value.split(',')" +"\r\n"+\
                      "    for i, v in enumerate(a):" +"\r\n"+\
                      "        ikrefItems.append(a[i])" +"\r\n"+\
                      "        ikrefItems.append(i)" +"\r\n"+\
                      "item.UIItems = ikrefItems" +"\r\n"

        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        # IK/Upv References
        group = tab.addGroup("IK Reference")

        row = group.addRow()
        item = row.addEnumControl(self.pIkRef.scriptName, [], "IK", c.siControlCombo)
        item.setCodeAfter(ikItemsCode)
        row.addButton("PickIkRef", "Pick New")
        row.addButton("DeleteIkRef", "Delete")
#        item = group.addItem(self.pIkRefArray.scriptName, "")
#        item.setAttribute(c.siUINoLabel, True)

    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):
        
        self.logic.addGlobalCode("from gear.xsi.rig.component import logic\r\nreload(logic)")

        self.logic.addOnClicked("PickIkRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.pickReferences(prop, '"+self.pIkRefArray.scriptName+"', '"+self.pIkRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("DeleteIkRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.deleteReference(prop, '"+self.pIkRefArray.scriptName+"', '"+self.pIkRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")


