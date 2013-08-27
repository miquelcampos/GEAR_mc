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

## @package gear.xsi.rig.component.control_01.guide
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c, comboItems_rotorder

from gear.xsi.rig.component.guide import ComponentGuide

# guide info
AUTHOR = "Jeremie Passerin"
URL = "http://www.jeremiepasserin.com"
EMAIL = "geerem@hotmail.com"
VERSION = [1,0,1]
TYPE = "control_01"
NAME = "control"
DESCRIPTION = "Simple controler"

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
        self.pick_transform = ["root"]
        self.save_transform = ["root", "icon"]
        self.save_primitive = ["icon"]

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.icon = self.addLoc("icon", self.root, self.root.Kinematics.Global.Transform.Translation)

        self.addToGroup(self.root, "hidden")

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        self.pIkRef      = self.addParam("ikref", c.siInt4, None, 0, None)
        self.pIkRefArray = self.addParam("ikrefarray", c.siString, "")
        
        self.pIcon = self.addParam("icon", c.siString, "null", None, None)

        self.pColor = self.addParam("color", c.siInt4, 0, 0, 2)
        self.pColor_r = self.addParam("color_r", c.siDouble, 0.5, 0, 1)
        self.pColor_g = self.addParam("color_g", c.siDouble, 0.5, 0, 1)
        self.pColor_b = self.addParam("color_b", c.siDouble, 0.5, 0, 1)

        self.pShadow = self.addParam("shadow", c.siBool, False)

        self.pSclX = self.addParam("sclx", c.siBool, True)
        self.pSclY = self.addParam("scly", c.siBool, True)
        self.pSclZ = self.addParam("sclz", c.siBool, True)
        self.pRotX = self.addParam("rotx", c.siBool, True)
        self.pRotY = self.addParam("roty", c.siBool, True)
        self.pRotZ = self.addParam("rotz", c.siBool, True)
        self.pRotOrder = self.addParam("rotorder", c.siBool, True)
        self.pPosX = self.addParam("posx", c.siBool, True)
        self.pPosY = self.addParam("posy", c.siBool, True)
        self.pPosZ = self.addParam("posz", c.siBool, True)
        
        self.pDefault_RotOrder = self.addParam("default_rotorder", c.siInt4, 0)

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
        # Items
        iconItems = ["null", "null",
                         "curve : cube", "cube",
                         "curve : pyramid", "pyramid",
                         "curve : square", "square",
                         "curve : flower", "flower",
                         "curve : circle", "circle",
                         "curve : compas", "compas",
                         "curve : foil", "foil",
                         "curve : diamond", "diamond",
                         "curve : cube with peak", "cubewithpeak",
                         "curve : sphere", "sphere",
                         "curve : arrow", "arrow",
                         "curve : cross arrow", "crossarrow",
                         "curve : bended arrow", "bendedarrow",
                         "curve : cross", "cross",
                         "curve : glasses", "glasses",
                         "curve : look at", "lookat",
                         "curve : eye arrow", "eyearrow",
                         "curve : eye ball", "eyeball"]

        colorItems = ["Use IK color", 0, "Use FK Color", 1, "Custom", 2]

        rotorderItems = comboItems_rotorder

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
        
        group = tab.addGroup("Display")
        row = group.addRow()
        row.addEnumControl(self.pIcon.scriptName, iconItems, "Icon", c.siControlCombo)
        row.addButton("pickIcon", "Pick")
        group.addEnumControl(self.pColor.scriptName, colorItems, "Color", c.siControlCombo)
        item = group.addColor(self.pColor_r.scriptName, "Custom Color")
        item.addCondition("PPG."+self.pColor.scriptName+".Value == 2")

        group = tab.addGroup("Shadow")
        item = group.addItem(self.pShadow.scriptName, "Add Shadow")

        tab = self.layout.addTab("Keyable")
        keyablegroup = tab.addGroup("Keyable")
        row = keyablegroup.addRow()
        row.addSpacer()
        row.addButton("all", "All")
        row.addButton("none", "None")

        group = keyablegroup.addGroup("Scaling")
        item = group.addItem(self.pSclX.scriptName, "Scl X")
        item = group.addItem(self.pSclY.scriptName, "Scl Y")
        item = group.addItem(self.pSclZ.scriptName, "Scl Z")

        group = keyablegroup.addGroup("Rotation")
        item = group.addItem(self.pRotX.scriptName, "Rot X")
        item = group.addItem(self.pRotY.scriptName, "Rot Y")
        item = group.addItem(self.pRotZ.scriptName, "Rot Z")
        item = group.addItem(self.pRotOrder.scriptName, "Rot Order")
        item = group.addEnumControl(self.pDefault_RotOrder.scriptName, rotorderItems, "Default", c.siControlCombo)
        item.addCondition("PPG."+self.pRotOrder.scriptName+".Value")

        group = keyablegroup.addGroup("Position")
        item = group.addItem(self.pPosX.scriptName, "Pos X")
        item = group.addItem(self.pPosY.scriptName, "Pos Y")
        item = group.addItem(self.pPosZ.scriptName, "Pos Z")

    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):

        self.logic.addGlobalCode("from gear.xsi.rig.component import logic\r\nreload(logic)")
        self.logic.addGlobalCode("from gear.xsi import xsi, c\r\n" + \
                                         "import gear.xsi.icon as icon\r\n" + \
                                         "import gear.xsi.primitive as pri\r\n" + \
                                         "import gear.xsi.utils as uti\r\n" + \
                                         "import gear.xsi.uitoolkit as uit\r\n")

        self.logic.addOnChangedRefresh(self.pColor.scriptName)
        self.logic.addOnChangedRefresh(self.pRotOrder.scriptName)

        self.logic.addOnClicked("PickIkRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.pickReferences(prop, '"+self.pIkRefArray.scriptName+"', '"+self.pIkRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("DeleteIkRef",
                                      "prop = PPG.Inspected(0)\r\n" +
                                      "logic.deleteReference(prop, '"+self.pIkRefArray.scriptName+"', '"+self.pIkRef.scriptName+"')\r\n" +
                                      "PPG.Refresh() \r\n")

        self.logic.addOnClicked("all",
                                        "prop = PPG.Inspected(0)\r\n" +
                                        "for s in ['posx', 'posy', 'posz', 'rotx', 'roty', 'rotz', 'rotorder', 'sclx', 'scly', 'sclz']:" + "\r\n" + \
                                        "    prop.Parameters(s).Value = True" + "\r\n" + \
                                        "PPG.Refresh()")

        self.logic.addOnClicked("none",
                                        "prop = PPG.Inspected(0)\r\n" +
                                        "for s in ['posx', 'posy', 'posz', 'rotx', 'roty', 'rotz', 'rotorder', 'sclx', 'scly', 'sclz']:" + "\r\n" + \
                                        "    prop.Parameters(s).Value = False" + "\r\n" + \
                                        "PPG.Refresh()")


        self.logic.addOnChanged("icon",
                                      "root = PPG.Inspected(0).Parent3DObject\r\n" +
                                      "name = PPG.comp_name.Value+'_'+PPG.comp_side.Value+str(PPG.comp_index.Value)+'_icon'\r\n" +
                                      "ctl = root.FindChild(name)\r\n" +
                                      "t = ctl.Kinematics.Global.Transform\r\n" +
                                      "children  = ctl.children\r\n" +
                                      "if children.Count:\r\n" +
                                      "    root.addChild(children)\r\n" +
                                      "color = [.875,.75,.25]\r\n" +
                                      "xsi.DeleteObj(ctl)\r\n" +
                                      "if PPG.icon.Value == 'null' : ctl = pri.addNull(root, name, t, 1, color)\r\n" +
                                      "elif PPG.icon.Value == 'cube': ctl = icon.cube(root, name, 1, 1, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'pyramid': ctl = icon.pyramid(root, name, 1, 1, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'square': ctl = icon.square(root, name, 1, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'flower': ctl = icon.flower(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'circle': ctl = icon.circle(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'compas': ctl = icon.compas(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'foil': ctl = icon.foil(root, name, 1, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'diamond': ctl = icon.diamond(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'cubewithpeak': ctl = icon.cubewithpeak(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'sphere': ctl = icon.sphere(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'arrow': ctl = icon.arrow(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'crossarrow': ctl = icon.crossarrow(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'bendedarrow': ctl = icon.bendedarrow(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'cross': ctl = icon.cross(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'glasses': ctl = icon.glasses(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'lookat': ctl = icon.lookat(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'eyearrow': ctl = icon.eyearrow(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'anglesurvey': ctl = icon.anglesurvey(root, name, 1, color, t)\r\n" +
                                      "elif PPG.icon.Value == 'eyeball': ctl = icon.eyeball(root, name, 1, color, t)\r\n" +
                                      "if children.Count:\r\n" +
                                      "    ctl.AddChild(children)\r\n" )

        self.logic.addOnClicked("pickIcon",
                                        "new_ctl = uit.pickSession(c.siGenericObjectFilter, 'Pick icon reference', False)\r\n" +
                                        "if not new_ctl or new_ctl.Type not in ['null', 'crvlist']:\r\n" +
                                        "    xsi.LogMessage('PickSession aborded or invalid object selected (Only curve or null is supported)', c.siWarning)\r\n" +
                                        "    return\r\n" +
                                        "root = PPG.Inspected(0).Parent3DObject\r\n" +
                                        "name = PPG.comp_name.Value+'_'+PPG.comp_side.Value+str(PPG.comp_index.Value)+'_icon'\r\n" +
                                        "ctl = root.FindChild(name)\r\n" +
                                        "children  = ctl.children\r\n" +
                                        "if children.Count:\r\n" +
                                        "    root.addChild(children)\r\n" +
                                        "xsi.DeleteObj(ctl)\r\n" +
                                        "ctl = xsi.Duplicate(new_ctl, 1, 0, 0, 0, 2, 1, 2, 1, 0)(0)\r\n" +
                                        "root.AddChild(ctl)\r\n" +
                                        "if children.Count:\r\n" +
                                        "    ctl.AddChild(children)\r\n" +
                                        "ctl.Name = name\r\n" +
                                        "uti.setColor(ctl, [.875,.75,.25])\r\n")


