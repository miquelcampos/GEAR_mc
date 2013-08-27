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

## @package gear.xsi.rig.component.eye_01
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c, dynDispatch, XSIFactory, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.ppg as ppg
import gear.xsi.parameter as par
import gear.xsi.primitive as pri
import gear.xsi.applyop as aop
import gear.xsi.transform as tra 

##########################################################
# COMPONENT
##########################################################
## The main component class.
class Component(MainComponent):

    # =====================================================
    # OBJECTS
    # =====================================================
    ## Add all the objects needed to create the component.
    # @param self
    def addObjects(self):

        t = tra.getTransformLookingAt(self.guide.pos["root"], self.guide.pos["lookat"], self.y_axis, "zy")

        # Direction cns 
        self.dir_cns = pri.addNull(self.root, self.getName("dir_cns"), t, self.size*.1)
        self.addToGroup(self.dir_cns, "hidden")
        
        upv_pos = XSIMath.CreateVector3(0,1,0)
        upv_pos.MulByTransformationInPlace(t)
        self.upv_cns = pri.addNullFromPos(self.root, self.getName("upv_cns"), upv_pos, self.size*.1)
        self.addToGroup(self.upv_cns, "hidden")

        # IK Controler
        self.ik_cns = pri.addNull(self.root, "ik_cns", tra.getTransformFromPosition(self.guide.pos["lookat"]), self.size*.1)
        self.addToGroup(self.ik_cns, "hidden")
        self.ik_ctl = self.addCtl(self.ik_cns, "ik_ctl", tra.getTransformFromPosition(self.guide.pos["lookat"]), self.color_ik, "cross", h=self.size*.5)
        par.setKeyableParameters(self.ik_ctl, self.t_params)
        
        # FK Controler
        self.fk_ctl = self.addCtl(self.dir_cns, "fk_ctl", t, self.color_fk, "arrow", h=self.size*.5)
        xsi.SetNeutralPose(self.fk_ctl, c.siTrn)
        par.setKeyableParameters(self.fk_ctl, self.r_params)
        # par.addLocalParamToCollection(self.inv_params, self.fk_ctl, ["posx", "posy", "posz"])

        self.addShadow(self.fk_ctl, 0)        
           
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

        # Ik/Upv References
        if self.ikref_count > 1:
            self.pIkRef = self.addAnimParam("ikref", c.siInt4, 0, 0, self.ikref_count-1)

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

        cns = aop.dirCns(self.dir_cns, self.ik_ctl, self.upv_cns, False, "zy")

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## standard connection definition with ik and upv references.
    # @param self
    def connect(self):
        self.parent.AddChild(self.root)

        # Set the Ik Reference
        if self.settings["ikrefarray"]:
            ref_names = self.settings["ikrefarray"].split(",")
            if len(ref_names) == 1:
                ref = self.rig.findChild(ref_names[0])
                ref.AddChild(self.ik_cns)
            else:
                for i, ref_name in enumerate(ref_names):
                    ref = self.rig.findChild(ref_name)
                    cns = self.ik_cns.Kinematics.AddConstraint("Pose", ref, True)
                    par.addExpression(cns.Parameters("active"), self.pIkRef.FullName+" == "+str(i))
