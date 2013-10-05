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

## @package gear.xsi.rig.component.chain_cns_01
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
import gear.xsi.transform as tra
import gear.xsi.icon as icon
import gear.xsi.vector as vec
import gear.xsi.applyop as aop

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

        self.normal = self.guide.blades["blade"].z

        # Root ---------------------------------------------
        # For this component we need the root to be correctly oriented
        t = tra.getTransformLookingAt(self.guide.apos[0], self.guide.apos[1], self.normal, "xy", self.negate)
        self.root = pri.addNull(self.model, self.getName("root"), t, self.size *.2)
        self.addToGroup(self.root, "hidden")

        # Shd ----------------------------------------------
        if self.options["shadowRig"]:
            self.shd_org = self.rig.shd_org.AddNull(self.getName("shd_org"))
            self.addToGroup(self.shd_org, "hidden")

    ## Add all the objects needed to create the component.
    # @param self
    def addObjects(self):

        self.div_count = len(self.guide.apos) - 1

        #
        
        # FK controlers ------------------------------------
        self.fk_ctl = []
        self.fk_ref = []
        self.dir_ref = []
        fk_ctl_parent = self.root
        fk_ref_parent = self.root
        dir_ref_parent = self.root
        for i, t in enumerate(tra.getChainTransform(self.guide.apos, self.normal, self.negate)):

            # ctl
            dist = vec.getDistance(self.guide.apos[i], self.guide.apos[i+1])
            fk_ctl = self.addCtl(fk_ctl_parent, "fk%s_ctl"%i, t, self.color_fk, "cube", w=dist, h=self.size*.25, d=self.size*.25, po=XSIMath.CreateVector3(dist*.5*self.n_factor,0,0))
            xsi.SetNeutralPose(fk_ctl)
            par.setKeyableParameters(fk_ctl)
            fk_ctl_parent = fk_ctl

            self.fk_ctl.append(fk_ctl)

            self.addShadow(fk_ctl, i)

            # ref
            fk_ref = pri.addNull(fk_ref_parent, self.getName("fk%s_ref"%i), t, self.size*.1)
            fk_ref_parent = fk_ref

            self.fk_ref.append(fk_ref)

            dir_ref = pri.addNull(dir_ref_parent, self.getName("dir%s_ref"%i), t, self.size*.1)
            dir_ref_parent = dir_ref

            self.dir_ref.append(dir_ref)

        end_ref = pri.addNullFromPos(self.dir_ref[-1], self.getName("dir%s_ref"%(i+1)), self.guide.apos[-1], self.size*.1)
        self.dir_ref.append(end_ref)

        self.addToGroup(self.fk_ref, "hidden")
        self.addToGroup(self.dir_ref, "hidden")

        parent = self.root
        self.ref_chn = []
        for i in range(self.div_count):
            pos = [self.guide.apos[i], self.guide.apos[i+1]]
            ref_chn =  pri.add2DChain(parent, self.getName("ref%s"%i), pos, self.normal, self.negate, self.size*.1, True)
            self.addToGroup(ref_chn.all, "hidden")

            parent = ref_chn.eff
            
            self.ref_chn.append(ref_chn)

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

        for i, ref_chn in enumerate(self.ref_chn):
            ref_chn.eff.Kinematics.AddConstraint("Position", self.dir_ref[i+1], False)

            self.fk_ref[i].Kinematics.AddConstraint("Pose", ref_chn.bones[0], False)

        for fk_ref, fk_ctl in zip(self.fk_ref, self.fk_ctl):

            for s in "xyz":
                par.addExpression(fk_ctl.Kinematics.Local.Parameters("nrot"+s), fk_ref.Kinematics.Local.Parameters("rot"+s))
                par.addExpression(fk_ctl.Kinematics.Local.Parameters("npos"+s), fk_ref.Kinematics.Local.Parameters("pos"+s))

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):

        self.relatives["root"] = self.fk_ctl[0]

        for i in range(self.div_count):
            self.relatives["%s_loc"%i] = self.fk_ctl[i]

        if self.div_count > 0:
            self.relatives["%s_loc"%self.div_count] = self.fk_ctl[-1]
            
    ## Add more connection definition to the set.
    # @param self
    def addConnection(self):
        self.connections["leg_2jnt_01"] = self.connect_leg_2jnt_01
        self.connections["leg_3jnt_01"] = self.connect_leg_3jnt_01

    ## leg connection definition.
    # @param self
    def connect_leg_2jnt_01(self):
        # If the parent component hasn't been generated we skip the connection
        if self.parent_comp is None:
            return

        self.parent_comp.fk2_ctl.addChild(self.root)
        self.root.Kinematics.AddConstraint("Pose", self.parent_comp.fk2_ctl, True)
        cns = self.root.Kinematics.AddConstraint("Pose", self.parent_comp.ik_ctl, True)
        par.addExpression(cns.Parameters("blendweight"), self.parent_comp.pBlend.FullName)

        self.parent_comp.tws2_rot.addChild(self.ref_chn[0].root)

        return

    ## leg connection definition.
    # @param self
    def connect_leg_3jnt_01(self):
        # If the parent component hasn't been generated we skip the connection
        if self.parent_comp is None:
            return

        self.parent_comp.fk3_ctl.addChild(self.root)
        self.root.Kinematics.AddConstraint("Pose", self.parent_comp.fk3_ctl, True)
        cns = self.root.Kinematics.AddConstraint("Pose", self.parent_comp.ik_ctl, True)
        par.addExpression(cns.Parameters("blendweight"), self.parent_comp.pBlend.FullName)
        
        self.parent_comp.tws3_rot.addChild(self.ref_chn[0].root)
