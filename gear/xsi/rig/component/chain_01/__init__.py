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

## @package gear.xsi.rig.component.chain_01
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
    ## Add all the objects needed to create the component.
    # @param self
    def addObjects(self):

        self.normal = self.guide.blades["blade"].z
        self.binormal = self.guide.blades["blade"].x

        self.isFk = self.settings["type"] != 1
        self.isIk = self.settings["type"] != 0
        self.isFkIk = self.settings["type"] == 2

        # FK controlers ------------------------------------
        if self.isFk:
            self.fk_ctl = []
            parent = self.root
            for i, t in enumerate(tra.getChainTransform(self.guide.apos, self.normal, self.negate)):
                dist = vec.getDistance(self.guide.apos[i], self.guide.apos[i+1])
                fk_ctl = self.addCtl(parent, "fk%s_ctl"%i, t, self.color_fk, "cube", w=dist, h=self.size*.25, d=self.size*.25, po=XSIMath.CreateVector3(dist*.5*self.n_factor,0,0))
                xsi.SetNeutralPose(fk_ctl, c.siTrn)
                par.setKeyableParameters(fk_ctl)
                par.addLocalParamToCollection(self.inv_params, fk_ctl, ["posx", "posy", "posz"])

                parent = fk_ctl
                self.fk_ctl.append(fk_ctl)

            if self.settings["neutralpose"]:
                xsi.SetNeutralPose(self.fk_ctl)
            else:
                xsi.SetNeutralPose(self.fk_ctl[0])

        # IK controlers ------------------------------------
        if self.isIk:

            normal = vec.getTransposedVector(self.normal, [self.guide.apos[0], self.guide.apos[1]], [self.guide.apos[-2], self.guide.apos[-1]])
            t = tra.getTransformLookingAt(self.guide.apos[-2], self.guide.apos[-1], normal, "xy", self.negate)
            t.SetTranslation(self.guide.apos[-1])

            self.ik_cns = pri.addNull(self.root, self.getName("ik_cns"), t, self.size*.2)
            self.addToGroup(self.ik_cns, "hidden")

            self.ikcns_ctl = self.addCtl(self.ik_cns, "ikcns_ctl", t, self.color_ik, "null", h=self.size)
            par.setKeyableParameters(self.ikcns_ctl)

            self.ik_ctl = self.addCtl(self.ikcns_ctl, "ik_ctl", t, self.color_ik, "cube", h=self.size*.3, w=self.size*.3, d=self.size*.3)
            xsi.SetNeutralPose(self.ik_ctl)
            par.setKeyableParameters(self.ik_ctl, self.tr_params)

            v = XSIMath.CreateVector3()
            v.Sub(self.guide.apos[-1], self.guide.apos[0])
            v.Cross(self.normal, v)
            v.NormalizeInPlace()
            v.ScaleInPlace(self.size * 4)
            v.AddInPlace(self.guide.apos[1])
            self.upv_cns = pri.addNullFromPos(self.root, self.getName("upv_cns"), v, self.size*.1)
            self.addToGroup(self.upv_cns, "hidden")

            self.upv_ctl = self.addCtl(self.upv_cns, "upv_ctl", self.upv_cns.Kinematics.Global.Transform, self.color_ik, "leash", h=self.size*.2, ap=self.guide.apos[1])
            par.setKeyableParameters(self.upv_ctl, self.t_params)

            # Chain
            self.chain = pri.add2DChain(self.root, self.getName("chain"), self.guide.apos, self.normal, self.negate, self.size*.5, True)
            self.addToGroup(self.chain.all, "hidden")

        # Chain of deformers -------------------------------
        self.loc = pri.addNullChain(self.root, self.getName("#_loc"), self.guide.apos, self.normal, self.negate, self.size*.25)
        xsi.SetNeutralPose(self.loc, c.siTrn)
        self.addToGroup(self.loc, "hidden")

        for i, loc in enumerate(self.loc):
            self.addShadow(loc, i)

    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):

        # Anim -------------------------------------------
        # Default parameter to get a better display in the keying panel
        if self.isIk:
            self.pFullName = self.addAnimParam(self.fullName, c.siString, self.fullName, None, None, None, None, False, True, True)

        if self.isFkIk:
            self.pBlend = self.addAnimParam("blend", c.siDouble, self.settings["blend"], 0, 1, 0, 1)

        if self.isIk:
            self.pRoll  = self.addAnimParam("roll", c.siDouble, 0, -360, 360, -180, 180)
            self.pIkCns = self.addAnimParam("ikcns", c.siBool, False, None, None, None, None, False, False, True)

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):

        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        group = tab.addGroup("FK / IK")

        if self.isFkIk:
            group.addItem(self.pBlend.ScriptName, "Blend")

        if self.isIk:
            group.addItem(self.pRoll.ScriptName, "Roll")
            group.addItem(self.pIkCns.ScriptName, "Show ik cns Controler")

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

        # Visibilities -------------------------------------
        if self.isFkIk:
            for fk_ctl in self.fk_ctl:
                par.addExpression(fk_ctl.Properties("visibility").Parameters("viewvis"), "1 - "+self.pBlend.FullName)

            par.addExpression(self.upv_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)
            par.addExpression(self.ikcns_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName +" * "+ self.pIkCns.FullName)
            par.addExpression(self.ik_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)

        # IK Chain -----------------------------------------
        if self.isIk:
            # Leash
            aop.clsCtrOp(self.upv_ctl, self.chain.bones[0], [0])

            # Constraint and up vector
            self.chain.eff.Kinematics.AddConstraint("Position", self.ik_ctl, False)
            xsi.ApplyOp("SkeletonUpVector", self.chain.bones[0].FullName+";"+self.upv_ctl.FullName, 3, "siPersistentOperation", "", 0)

            par.addExpression(self.chain.roll, self.pRoll.FullName)

        # Chain of deformers -------------------------------
        for i, loc in enumerate(self.loc):

            if self.settings["type"] == 0: # fk only
                loc.Kinematics.addConstraint("Pose", self.fk_ctl[i])

            elif self.settings["type"] == 1: # ik only
                loc.Kinematics.addConstraint("Pose", self.chain.bones[i])

            elif self.settings["type"] == 2: # fk/ik
                # orientation
                cns = loc.Kinematics.AddConstraint("Orientation", self.fk_ctl[i])
                cns = loc.Kinematics.AddConstraint("Orientation", self.chain.bones[i])
                par.addExpression(cns.Parameters("blendweight"), self.pBlend.FullName)

                # position / scaling
                for s in "xyz":
                    par.addExpression(loc.Kinematics.Local.Parameters("pos%s"%s), self.fk_ctl[i].Kinematics.Local.Parameters("pos%s"%s).FullName+" * (1 - "+self.pBlend.FullName+") + "+self.chain.bones[i].Kinematics.Local.Parameters("pos%s"%s).FullName +" * "+self.pBlend.FullName)
                    par.addExpression(loc.Kinematics.Local.Parameters("scl%s"%s), self.fk_ctl[i].Kinematics.Local.Parameters("scl%s"%s).FullName+" * (1 - "+self.pBlend.FullName+") + "+self.chain.bones[i].Kinematics.Local.Parameters("scl%s"%s).FullName +" * "+self.pBlend.FullName)

        # Default Values -----------------------------------
        if self.isFkIk:
            self.pBlend.Value = self.settings["blend"]

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):

        self.relatives["root"] = self.loc[0]
        for i in range(1, len(self.loc)):
            self.relatives["%s_loc"%i] = self.loc[i]
        self.relatives["%s_loc"%(len(self.loc)-1)] = self.loc[-1]
