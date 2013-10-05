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

## @package gear.xsi.rig.component.foot_bk_01
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################

from gear.xsi import xsi, c, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.icon as icon
import gear.xsi.transform as tra
import gear.xsi.parameter as par
import gear.xsi.primitive as pri
import gear.xsi.applyop as aop
import gear.xsi.vector as vec

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

        self.div_count = len(self.guide.apos) - 5

        plane = [self.guide.apos[0], self.guide.apos[-4], self.guide.apos[-3]]
        self.normal = self.getNormalFromPos(plane)
        self.binormal = self.getBiNormalFromPos(plane)

        # Heel ---------------------------------------------
        t = tra.getTransformLookingAt(self.guide.pos["heel"], self.guide.apos[-4], self.normal, "xz", self.negate)

        self.heel_loc = pri.addNull(self.root, self.getName("heel_loc"), t, self.size*.15)
        xsi.SetNeutralPose(self.heel_loc)
        self.addToGroup(self.heel_loc, "hidden")

        self.heel_ctl = self.addCtl(self.heel_loc, "heel_ctl", t, self.color_ik, "sphere", w=self.size*.1)
        xsi.SetNeutralPose(self.heel_ctl)
        par.setKeyableParameters(self.heel_ctl, self.r_params)

        # Tip ----------------------------------------------
        v = XSIMath.CreateVector3(self.guide.apos[-5].X,self.guide.apos[-1].Y,self.guide.apos[-5].Z)
        t.SetTranslation(v)
        self.tip_ctl = self.addCtl(self.heel_ctl, "tip_ctl", t, self.color_ik, "circle", w=self.size*.5)
        xsi.SetNeutralPose(self.tip_ctl)
        par.setKeyableParameters(self.heel_ctl, self.r_params)

        # Roll ---------------------------------------------
        if self.settings["roll"] == 0:
            t = tra.getTransformFromPosition(self.guide.pos["root"])
            t.SetRotation(tra.getRotationFromAxis(self.y_axis, self.normal, "yz", self.negate))
            self.roll_ctl = self.addCtl(self.root, "roll_ctl", t, self.color_ik, "cylinder", w=self.size*.5, h=self.size*.5, ro=XSIMath.CreateRotation(3.1415*.5,0,0))
            xsi.SetNeutralPose(self.roll_ctl)
            par.setKeyableParameters(self.roll_ctl, ["rotx", "rotz"])

        # Backward Controlers ------------------------------
        bk_pos = self.guide.apos[1:-3]
        bk_pos.reverse()
        parent = self.tip_ctl
        self.bk_ctl = []
        for i, pos in enumerate(bk_pos):

            if i == 0:
                t = self.heel_loc.Kinematics.Global.Transform
                t.SetTranslation(pos)
            else:
                dir = bk_pos[i-1]
                t = tra.getTransformLookingAt(pos, dir, self.normal, "xz", self.negate)

            bk_ctl = self.addCtl(parent, "bk%s_ctl"%i, t, self.color_ik, "sphere", w=self.size*.15)
            xsi.SetNeutralPose(bk_ctl)
            par.setKeyableParameters(bk_ctl, self.r_params)

            self.bk_ctl.append(bk_ctl)
            parent = bk_ctl

        # Forward Controlers ------------------------------
        self.fk_ref = pri.addNullFromPos(self.bk_ctl[-1], self.getName("fk_ref"), self.guide.apos[0], self.size*.5)
        self.addToGroup(self.fk_ref, "hidden")

        self.fk_ctl = []
        parent = self.fk_ref
        for i, bk_ctl in enumerate(reversed(self.bk_ctl[1:])):
            t = bk_ctl.Kinematics.Global.Transform
            dist = vec.getDistance(self.guide.apos[i+1], self.guide.apos[i+2])
            fk_ctl = self.addCtl(parent, "fk%s_ctl"%i, t, self.color_fk, "cube", w=dist, h=self.size*.5, d=self.size*.5, po=XSIMath.CreateVector3(dist*.5*self.n_factor,0,0))
            xsi.SetNeutralPose(fk_ctl)
            par.setKeyableParameters(fk_ctl)
            self.addShadow(fk_ctl, i)

            parent = fk_ctl
            self.fk_ctl.append(fk_ctl)

    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):

        # Anim -------------------------------------------
        # Default parameter to get a better display in the keying panel
        self.pFullName = self.addAnimParam(self.fullName, c.siString, self.fullName, None, None, None, None, False, True, True)

        # Show Controlers
        self.pShowForward = self.addAnimParam("showForward", c.siBool, True, None, None, None, None, False)
        self.pShowBackward = self.addAnimParam("showBackward", c.siBool, True, None, None, None, None, False)

        # Roll Angles
        if self.settings["roll"] == 1:
            self.pRoll = self.addAnimParam("roll", c.siDouble, 0, -90, 90)
            self.pBank = self.addAnimParam("bank", c.siDouble, 0, -180, 180, -90, 90)

        self.pStartAngle = [ self.addAnimParam("angle_%s"%i, c.siDouble, 20, 0, None, 0, 90) for i in range(self.div_count) ]

        # Setup ------------------------------------------
        self.pBlend = self.addSetupParam("blend", c.siDouble, 1, 0, 1, 0, 1, True, False)

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):

        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        group = tab.addGroup("Roll")
        group.addItem(self.pShowForward.ScriptName, "Show Forward Controler")
        group.addItem(self.pShowBackward.ScriptName, "Show Backward Controler")
        if self.settings["roll"] == 1:
            group.addItem(self.pRoll.ScriptName, "Roll")
            group.addItem(self.pBank.ScriptName, "Bank")

        for i, pStartAngle in enumerate(self.pStartAngle):
            group.addItem(pStartAngle.ScriptName, "Roll Angle %s"%i)

        # Setup ------------------------------------------
        tab = self.setup_layout.addTab(self.name)

        group = tab.addGroup("FK/IK")
        group.addItem(self.pBlend.ScriptName, "FK/IK")


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
        for ctl in self.bk_ctl:
            par.addExpression(ctl.Properties("Visibility").Parameters("viewvis"), self.pShowBackward.FullName+" * "+self.pBlend.FullName)
        for ctl in self.fk_ctl:
            par.addExpression(ctl.Properties("Visibility").Parameters("viewvis"), self.pShowForward.FullName)

        if self.settings["roll"] == 0: # Using the controler
            par.addExpression(self.roll_ctl.Properties("Visibility").Parameters("viewvis"), self.pBlend.FullName)

        par.addExpression(self.tip_ctl.Properties("Visibility").Parameters("viewvis"), self.pBlend.FullName)
        par.addExpression(self.heel_ctl.Properties("Visibility").Parameters("viewvis"), self.pBlend.FullName)

        # Roll / Bank --------------------------------------
        if self.settings["roll"] == 0: # Using the controler
            self.pRoll = self.roll_ctl.Kinematics.Local.Parameters("rotz")
            self.pBank = self.roll_ctl.Kinematics.Local.Parameters("rotx")

        par.addExpression(self.heel_loc.Parameters("rotz"), "cond(%s>0, %s, 0)"%(self.pRoll.FullName, self.pRoll.FullName))
        par.addExpression(self.heel_loc.Parameters("rotx"), self.pBank.FullName)

        # Bank pivot compensation
        self.heel_loc.Kinematics.Local.pivotcompactive.Value = False

        outside = vec.getDistanceToAxe(self.guide.pos["outpivot"], self.guide.pos["heel"], self.guide.apos[-4])
        inside = vec.getDistanceToAxe(self.guide.pos["inpivot"], self.guide.pos["heel"], self.guide.apos[-4])

        if self.negate:
            par.addExpression(self.heel_loc.Parameters("pposz"), "cond(%s>0, %s, %s)"%(self.pBank.FullName, -inside, outside))
        else:
            par.addExpression(self.heel_loc.Parameters("pposz"), "cond(%s>0, %s, %s)"%(self.pBank.FullName, outside, -inside))

        # Reverse Controler offset -------------------------
        angle = "0"
        for i, ctl in enumerate(reversed(self.bk_ctl)):

            if i < len(self.pStartAngle):
                pStartAngle = self.pStartAngle[i]
                par.addExpression(ctl.Kinematics.Local.Parameters("pcrotz"), "MIN(0,MAX("+self.pRoll.FullName+" + ("+angle+"), -"+pStartAngle.FullName+"))")
                angle += " + " + pStartAngle.FullName
            else:
                 par.addExpression(ctl.Kinematics.Local.Parameters("pcrotz"), "MIN(0,"+self.pRoll.FullName+" + ("+angle+"))")

        # Reverse compensation -----------------------------
        for i, ctl in enumerate(self.fk_ctl):
            bk_ctl = self.bk_ctl[-i-1]

            for s in "xyz":
                par.addExpression(ctl.Kinematics.Local.Parameters("pcrot"+s),
                    "- ("+bk_ctl.Kinematics.Local.Parameters("rot"+s).FullName+" + "+bk_ctl.Kinematics.Local.Parameters("pcrot"+s).FullName+") * "+self.pBlend.FullName)

            aop.sn_inverseRotorder_op(ctl, bk_ctl)

        # Global Scale
        for s in "xyz":
            par.addExpression(self.fk_ref.Kinematics.Global.Parameters("scl%s"%s), self.root.Kinematics.Global.Parameters("scl%s"%s))

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):
        self.relatives["root"] = self.root
        self.relatives["heel"] = self.root
        self.relatives["inpivot"] = self.root
        self.relatives["outpivot"] = self.root

        for i in range(self.div_count):
            self.relatives["%s_loc"%i] = self.fk_ctl[i]

        if self.div_count > 0:
            self.relatives["%s_loc"%self.div_count] = self.fk_ctl[-1]

    ## Add more connection definition to the set.
    # @param self
    def addConnection(self):
        self.connections["leg_2jnt_01"] = self.connect_leg_2jnt_01
        self.connections["leg_2jnt_02"] = self.connect_leg_2jnt_02
        self.connections["leg_3jnt_01"] = self.connect_leg_3jnt_01

    ## leg connection definition.
    # @param self
    def connect_leg_2jnt_01(self):
        # If the parent component hasn't been generated we skip the connection
        if self.parent_comp is None:
            return

        self.parent_comp.ik_ctl.AddChild(self.root)
        self.bk_ctl[-1].AddChild(self.parent_comp.ik_ref)
        self.parent_comp.tws2_rot.AddChild(self.fk_ref)
        par.addExpression(self.pBlend, self.parent_comp.pBlend.FullName)
    ## leg connection definition.
    # @param self
    def connect_leg_2jnt_02(self):
        # If the parent component hasn't been generated we skip the connection
        if self.parent_comp is None:
            return

        self.parent_comp.ik_ctl.AddChild(self.root)
        self.bk_ctl[-1].AddChild(self.parent_comp.ik_ref)
        self.parent_comp.end_ref.AddChild(self.fk_ref)
        par.addExpression(self.pBlend, self.parent_comp.pBlend.FullName)

    ## leg connection definition.
    # @param self
    def connect_leg_3jnt_01(self):
        # If the parent component hasn't been generated we skip the connection
        if self.parent_comp is None:
            return

        self.parent_comp.ik_ctl.AddChild(self.root)
        self.bk_ctl[-1].AddChild(self.parent_comp.ik_ref)
        self.parent_comp.tws3_rot.AddChild(self.fk_ref)
        par.addExpression(self.pBlend, self.parent_comp.pBlend.FullName)

