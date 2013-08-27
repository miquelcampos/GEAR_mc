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

## @package gear.xsi.rig.component.eyelid_01.guide
# @author Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c, XSIMath

from gear.xsi.rig.component.guide import ComponentGuide
import gear.xsi.applyop as aop

# guide info
AUTHOR = "Miquel Campos "
URL = "http://www.miqueltd.com"
EMAIL = "hello@miqueltd.com"
VERSION = [1,0,0]
TYPE = "eyelid_01"
NAME = "eyelid"
DESCRIPTION = "eyelids rig"

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
        self.pick_transform = ["root", "#_loc"]
        self.save_transform = ["root", "upVector", "direction", "#_loc"]
        self.save_blade = ["blade"]
        self.addMinMax("#_loc", 1, -1)
        
        
        

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):
        self.root = self.addRoot()
        self.locs = self.addLocMulti("#_loc", self.root, False)
        
        
        vTemp = XSIMath.CreateVector3(self.root.Kinematics.Global.PosX.Value  , self.root.Kinematics.Global.PosY.Value +2, self.root.Kinematics.Global.PosZ.Value )
        self.upVector = self.addLoc("upVector", self.root, vTemp )
        
        vTemp = XSIMath.CreateVector3(self.root.Kinematics.Global.PosX.Value  , self.root.Kinematics.Global.PosY.Value , self.root.Kinematics.Global.PosZ.Value +2 )
        self.direction = self.addLoc("direction", self.root, vTemp )
        
        centers = [self.direction, self.root, self.upVector]
        self.dispcrv = self.addDispCurve("crvUp", centers)
        
        self.blade = self.addBlade("blade", self.root, self.upVector)
        
        centers = []
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)
        
    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):
        
        # eye corners controlers
        self.pCornerA       = self.addParam("cornerARef", c.siInt4, None, 0, None)
        self.pCornerAArray  = self.addParam("cornerARefArray", c.siString, "")
        self.pCornerB      = self.addParam("cornerBRef", c.siInt4, None, 0, None)
        self.pCornerBArray = self.addParam("cornerBRefArray", c.siString, "")
        
    
    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):
        # --------------------------------------------------
        # Items

        cornerAItemsCode = "cornerARefItems = []" +"\r\n"+\
                      "if PPG."+self.pCornerAArray.scriptName+".Value:" +"\r\n"+\
                      "    a = PPG."+self.pCornerAArray.scriptName+".Value.split(',')" +"\r\n"+\
                      "    for i, v in enumerate(a):" +"\r\n"+\
                      "        cornerARefItems.append(a[i])" +"\r\n"+\
                      "        cornerARefItems.append(i)" +"\r\n"+\
                      "item.UIItems = cornerARefItems" +"\r\n"

        cornerBItemsCode = "cornerBRefItems = []" +"\r\n"+\
                      "if PPG."+self.pCornerBArray.scriptName+".Value:" +"\r\n"+\
                      "    a = PPG."+self.pCornerBArray.scriptName+".Value.split(',')" +"\r\n"+\
                      "    for i, v in enumerate(a):" +"\r\n"+\
                      "        cornerBRefItems.append(a[i])" +"\r\n"+\
                      "        cornerBRefItems.append(i)" +"\r\n"+\
                      "item.UIItems = cornerBRefItems" +"\r\n"

       
        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        # IK/Upv References
        group = tab.addGroup("Eyelids controls")

        row = group.addRow()
        item = row.addEnumControl(self.pCornerA.scriptName, [], "Corner control A", c.siControlCombo)
        item.setCodeAfter(cornerAItemsCode)
        row.addButton("PickCornerARef", "Pick New")
        row.addButton("DeleteCornerARef", "Delete")
        
        row = group.addRow()
        item = row.addEnumControl(self.pCornerB.scriptName, [], "Corner control B", c.siControlCombo)
        item.setCodeAfter(cornerBItemsCode)
        row.addButton("PickCornerBRef", "Pick New")
        row.addButton("DeleteCornerBRef", "Delete")
    
    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):
        

        self.logic.addGlobalCode("from gear.xsi.rig.component import logic\r\nreload(logic)")

        

        self.logic.addOnClicked("PickCornerARef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.pickReferences(prop, '"+self.pCornerAArray.scriptName+"', '"+self.pCornerA.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")
                                      
        self.logic.addOnClicked("DeleteCornerARef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.deleteReference(prop, '"+self.pCornerAArray.scriptName+"', '"+self.pCornerA.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("PickCornerBRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.pickReferences(prop, '"+self.pCornerBArray.scriptName+"', '"+self.pCornerB.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")
                                      
        self.logic.addOnClicked("DeleteCornerBRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.deleteReference(prop, '"+self.pCornerBArray.scriptName+"', '"+self.pCornerB.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

    
    