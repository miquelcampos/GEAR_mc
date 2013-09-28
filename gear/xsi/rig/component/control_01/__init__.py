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

## @package gear.xsi.rig.component.control_01
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c, dynDispatch, XSIFactory

from gear.xsi.rig.component import MainComponent

import gear.xsi.ppg as ppg
import gear.xsi.parameter as par
import gear.xsi.primitive as pri

##########################################################
# COMPONENT
##########################################################
## The main component class.
class Component(MainComponent):

    # =====================================================
    # OBJECTS
    # =====================================================
    ## Build the initial hierarchy of the component.\n
    # Add the root and if needed the shadow root
    # @param self
    def initialHierarchy(self):

        # Get color
        if self.settings["color"] == 0:
            color = self.color_ik
        elif self.settings["color"] == 1:
            color = self.color_fk
        else:
            color = [self.settings["color_r"], self.settings["color_g"], self.settings["color_b"]]

        # Copy controler from given icon
        self.root = self.guide.prim["icon"].create(self.model, self.getName("ctl"), self.guide.tra["icon"], color)
        self.addToCtlGroup(self.root)

        # Shd --------------------------------
        if self.options["shadowRig"] and self.settings["shadow"]:
            self.shd_org = self.rig.shd_org.AddNull(self.getName("shd_org"))
            self.addToGroup(self.shd_org, "hidden")

    ## Add all the objects needed to create the component.
    # @param self
    def addObjects(self):
        if self.settings["shadow"]:
            self.addShadow(self.root, 0)

        if self.settings["rotorder"]:
            self.root.Kinematics.Local.Parameters("rotorder").Value = self.settings["default_rotorder"]

    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):
        
        if self.settings["ikrefarray"]:
            self.ikref_names = self.settings["ikrefarray"].split(",")
        else:
            self.ikref_names = []

        self.ikref_count = len(self.ikref_names)

        # Anim -------------------------------------------
        # Default parameter to get a better display in the keying panel
        self.pFullName = self.addAnimParam(self.fullName, c.siString, self.fullName, None, None, None, None, False, True, True)

        # Ik References
        if self.ikref_count > 1:
            self.pIkRef      = self.addAnimParam("ikref", c.siInt4, 0, 0, self.ikref_count-1)

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):
        
        # Items ------------------------------------------
        self.ikrefItems = []
        for i, name in enumerate(self.ikref_names):
            self.ikrefItems.append(name)
            self.ikrefItems.append(i)

        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        # IK/FK
        group = tab.addGroup("FK / IK")

        # Ik/Upv References
        if self.ikref_count > 1:
            row = group.addRow()
            row.addEnumControl(self.pIkRef.ScriptName, self.ikrefItems, "IK Ref", c.siControlCombo)
            row.addButton(self.getName("switchIkRef"), "Switch")

    ## Define the logic of the anim and setup properties.
    # @param self
    def addLogic(self):
        
        # Anim -------------------------------------------
        self.anim_logic.addGlobalCode("import gear.xsi.rig.component.logic as logic")

        if self.ikref_count > 1:
            self.anim_logic.addOnClicked(self.getName("switchIkRef"),
                                     "logic.switchRef(PPG.Inspected(0), '"+self.ik_ctl.Name+"', '"+self.pIkRef.ScriptName+"', "+str(self.ikref_count)+")\r\n" +
                                     "PPG.Refresh()\r\n")

    # =====================================================
    # OPERATORS
    # =====================================================
    ## Apply operators, constraints, expressions to the hierarchy.\n
    # In order to keep the code clean and easier to debug,
    # we shouldn't create any new object in this method.
    # @param self
    def addOperators(self):
        return

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Post connection action
    # @param self
    def postConnect(self):

        # As the root is the main controler, we need to set the neutral pose and lock the parameters after the connection.
        xsi.SetNeutralPose(self.root)
        keyables = [name for name in self.local_params if self.settings[name]]
        par.setKeyableParameters(self.root, keyables)

