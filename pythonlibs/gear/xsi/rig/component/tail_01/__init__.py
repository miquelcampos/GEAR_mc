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

## @package gear.xsi.rig.component.tail_01
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

        self.division = len(self.guide.apos)-1

        # FK controlers ------------------------------------
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

        xsi.SetNeutralPose(self.fk_ctl[0])

        # Chain -------------------------------------------
        parent = self.fk_ctl[0]
        self.chain = []
        for i in range(self.division):
            pos = [self.guide.apos[i], self.guide.apos[i+1]]
            chain = pri.add2DChain(parent, self.getName("spring%s"%i), pos, self.normal, self.negate, self.size*.25, True)
            self.addToGroup(chain.all, "hidden")

            eff_ref = pri.addNull(chain.root, self.getName("eff%s_ref"%i), chain.eff.Kinematics.Global.Transform, self.size*.1)
            eff_ref.AddChild(chain.eff)
            self.addToGroup(eff_ref, "hidden")

            self.addShadow(chain.bones[0], i)

            self.chain.append(chain)
            parent = chain.bones[0]

        # Plot Reference ----------------------------------
        self.ref = pri.addNullChain(self.root, self.getName("#_ref"), self.guide.apos, self.normal, self.negate, self.size * .1)
        self.addToGroup(self.ref, "hidden")
        xsi.SetNeutralPose(self.ref[0])

    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):

        # Anim -------------------------------------------
        # Default parameter to get a better display in the keying panel
        self.pFullName = self.addAnimParam(self.fullName, c.siString, self.fullName, None, None, None, None, False, True, True)

        self.pSpeed = self.addAnimParam("speed", c.siDouble, self.settings["speed"], 0, None, 0, 1)
        self.pDamping = self.addAnimParam("damping", c.siDouble, self.settings["damping"], 0, None, 0, 1)

        if self.settings["multi_blend"]:
            default = 1
        else:
            default = self.settings["blend"]
        self.pMainBlend = self.addAnimParam("main_blend", c.siDouble, default, 0, None, 0, 1)

        if self.settings["multi_blend"]:
            self.pBlend = [ self.addAnimParam("blend_%s"%i, c.siDouble, self.settings["blend"], 0, None, 0, 1) for i in range(self.division)]

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):

        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        group = tab.addGroup("Spring")
        row = group.addRow()
        row.addSpacer()
        row.addButton("plot", "Plot to Controler")
        group.addItem(self.pSpeed.ScriptName, "Speed")
        group.addItem(self.pDamping.ScriptName, "Damping")
        group.addItem(self.pMainBlend.ScriptName, "Global Blend")

        if self.settings["multi_blend"]:
            group = group.addGroup("Blend")
            for i, pBlend in enumerate(self.pBlend):
                group.addItem(pBlend.ScriptName, "Blend %s"%i)

    ## Define the logic of the anim and setup properties.
    # @param self
    def addLogic(self):

        self.anim_logic.addGlobalCode("import gear.xsi.rig.component.logic as logic\r\nreload(logic)")
        self.anim_logic.addOnClicked("plot",
                                     "logic.plotSpringToControler('"+self.fullName+"', PPG.Inspected(0))")
        return

    # =====================================================
    # OPERATORS
    # =====================================================
    ## Apply operators, constraints, expressions to the hierarchy.\n
    # In order to keep the code clean and easier to debug,
    # we shouldn't create any new object in this method.
    # @param self
    def addOperators(self):

        for i, chain in enumerate(self.chain):

            op = aop.sn_xfspring_op(chain.eff, 2)
            par.addExpression(op.Parameters("speed"), self.pSpeed.FullName)
            par.addExpression(op.Parameters("damping"), self.pDamping.FullName + "* .1")

            if self.settings["multi_blend"]:
                par.addExpression(op.Parameters("scale"), self.pMainBlend.FullName+" * "+self.pBlend[i].FullName)
            else:
                par.addExpression(op.Parameters("scale"), self.pMainBlend.FullName)

            chain.root.Kinematics.AddConstraint("Orientation", self.fk_ctl[i], False)

            self.ref[i].Kinematics.AddConstraint("Orientation", chain.bones[0])
            
        xsi.SetNeutralPose(self.ref[0])

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):

        self.relatives["root"] = self.chain[0].bones[0]
        for i in range(1, len(self.chain)):
            self.relatives["%s_loc"%i] = self.chain[i].bones[0]
        self.relatives["%s_loc"%(len(self.chain)-1)] = self.chain[-1].bones[0]
