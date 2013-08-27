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

## @package gear.xsi.rig.component.meta_01
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c, dynDispatch, XSIFactory

from gear.xsi.rig.component import MainComponent

import gear.xsi.icon as icon
import gear.xsi.parameter as par
import gear.xsi.primitive as pri
import gear.xsi.transform as tra
import gear.xsi.applyop as aop

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

        if self.negate:
            transforms = [tra.getNegatedTransform(tra.getFilteredTransform(t, True, True, False)) for t in self.guide.atra]
        else:
            transforms = [tra.getFilteredTransform(t, True, True, False) for t in self.guide.atra]

        # Controlers ---------------------------------------
        self.end_ctl = self.addCtl(self.root, "end_ctl", transforms[-1], self.color_ik, "cube", w=self.size*.2, h=self.size*.2, d=self.size*.2)
        par.setKeyableParameters(self.end_ctl, ["posx", "posy", "posz", "rotx", "roty", "rotz", "rotorder"])
        xsi.SetNeutralPose(self.end_ctl)

        if self.settings["startctl"]:
            self.start_ctl = self.addCtl(self.root, "0_ctl", transforms[0], self.color_ik, "cube", w=self.size*.2, h=self.size*.2, d=self.size*.2)
            par.setKeyableParameters(self.start_ctl, ["posx", "posy", "posz", "rotx", "roty", "rotz", "rotorder"])
            xsi.SetNeutralPose(self.end_ctl)
        else:
            self.start_ctl = pri.addNull(self.root, self.getName("0_loc"), transforms[0], self.size*.2)
            self.addToGroup(self.start_ctl, "hidden")

        # Locations ----------------------------------------
        self.loc = []
        for i, t in enumerate(transforms[1:-1]):
            loc = pri.addNull(self.root, self.getName("%s_loc"%(i+1)), t, self.size*.2)
            self.addToGroup(loc, "hidden")
            self.loc.append(loc)

        # Intermediate controlers --------------------------
        if self.settings["interctl"]:
            self.inter_ctl = []
            for i, loc in enumerate(self.loc):
                ctl = self.addCtl(loc, "%s_ctl"%(i+1), loc.Kinematics.Global.Transform, self.color_fk, "cube", w=self.size*.2, h=self.size*.2, d=self.size*.2)
                par.setKeyableParameters(ctl, ["posx", "posy", "posz", "rotx", "roty", "rotz", "rotorder"])
                xsi.SetNeutralPose(ctl)
                self.inter_ctl.append(ctl)

        # Deformers (Shadow) -------------------------------
        self.addShadow(self.start_ctl, 0)

        if self.settings["interctl"]:
            for i, ctl in enumerate(self.inter_ctl):
                self.addShadow(ctl, i+1)
        else:
            for i, loc in enumerate(self.loc):
                self.addShadow(loc, i+1)

        self.addShadow(self.end_ctl, "end")

    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):
        return

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):
        return

    ## Define the logic of the anim and setup properties.
    # @param self
    def addLogic(self):
        return

    # =====================================================
    # OPERATORS
    # =====================================================
    ## Apply operators, constraints, expressions to the hierarchy.\n
    # In order to keep the code clean and easier to debug,
    # we shouldn't create any new object in this method.
    # @param self
    def addOperators(self):

        # Intermediate position ---------------------------
        for i, loc in enumerate(self.loc):

            u = (i+1.0) / (len(self.loc)+1.0)

            cnsA = aop.poseCns(loc, self.start_ctl, True, True, True, True)
            cnsB = aop.poseCns(loc, self.end_ctl, True, True, True, True)
            cnsB.Parameters("blendweight").Value = u

            cnsA.Parameters("affbyori").Value = False
            cnsA.Parameters("affbyscl").Value = False
            cnsB.Parameters("affbyori").Value = False
            cnsB.Parameters("affbyscl").Value = False

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):
        self.relatives["root"] = self.start_ctl

        if self.settings["interctl"]:
            for i, ctl in enumerate(self.inter_ctl):
                self.relatives["%s_loc"%i] = ctl
        else:
            for i, loc in enumerate(self.loc):
                self.relatives["%s_loc"%i] = loc

        self.relatives["%s_loc"%len(self.loc)] = self.end_ctl

