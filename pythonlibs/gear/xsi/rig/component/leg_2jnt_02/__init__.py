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

## @package gear.xsi.rig.component.leg_2jnt_02
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
from gear.xsi import xsi, c, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.vector as vec
import gear.xsi.transform as tra
import gear.xsi.parameter as par
import gear.xsi.primitive as pri
import gear.xsi.applyop as aop
import gear.xsi.fcurve as fcu
import gear.xsi.curve as cur

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

        self.normal = self.getNormalFromPos(self.guide.apos)

        self.length0 = vec.getDistance(self.guide.apos[0], self.guide.apos[1])
        self.length1 = vec.getDistance(self.guide.apos[1], self.guide.apos[2])
        self.length2 = vec.getDistance(self.guide.apos[2], self.guide.apos[3])

        # FK Controlers ------------------------------------
        t = tra.getTransformLookingAt(self.guide.apos[0], self.guide.apos[1], self.normal, "xz", self.negate)
        self.fk0_ctl = self.addCtl(self.root, "fk0_ctl", t, self.color_fk, "circle", w=self.size*.1, po=XSIMath.CreateVector3(.5*self.n_factor,0,0), ro=XSIMath.CreateRotation(0,0,3.1415*.5))
        xsi.SetNeutralPose(self.fk0_ctl)
        par.setKeyableParameters(self.fk0_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk0_ctl, ["posx", "posy", "posz"])

        t = tra.getTransformLookingAt(self.guide.apos[1], self.guide.apos[2], self.normal, "xz", self.negate)
        self.fk1_ctl = self.addCtl(self.fk0_ctl, "fk1_ctl", t, self.color_fk, "circle", w=self.size*.1, po=XSIMath.CreateVector3(.5*self.n_factor,0,0), ro=XSIMath.CreateRotation(0,0,3.1415*.5))
        xsi.SetNeutralPose(self.fk1_ctl, c.siST)
        par.setKeyableParameters(self.fk1_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk1_ctl, ["posx", "posy", "posz"])

        t = tra.getTransformLookingAt(self.guide.apos[2], self.guide.apos[3], self.normal, "xz", self.negate)
        self.fk2_ctl = self.addCtl(self.fk1_ctl, "fk2_ctl", t, self.color_fk, "circle", w=self.size*.1, ro=XSIMath.CreateRotation(0,0,3.1415*.5))
        xsi.SetNeutralPose(self.fk2_ctl, c.siST)
        par.setKeyableParameters(self.fk2_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk2_ctl, ["posx", "posy", "posz"])

        # IK Controlers ------------------------------------
        self.ik_cns = pri.addNullFromPos(self.root, self.getName("ik_cns"), self.guide.apos[2], self.size*.02)
        self.addToGroup(self.ik_cns, "hidden")

        self.ikcns_ctl = self.addCtl(self.ik_cns, "ikcns_ctl", self.ik_cns.Kinematics.Global.Transform, self.color_ik, "null", h=self.size*.2)
        par.setKeyableParameters(self.ikcns_ctl)
        par.addLocalParamToCollection(self.inv_params, self.ikcns_ctl, ["posx", "rotx", "rotz"])

        t = tra.getTransformLookingAt(self.guide.apos[2], self.guide.apos[3], self.x_axis, "zx", False)
        self.ik_ctl = self.addCtl(self.ikcns_ctl, "ik_ctl", t, self.color_ik, "circle", w=self.size*.2)
        self.addToCtlGroup(self.ik_ctl)
        par.setKeyableParameters(self.ik_ctl)
        par.addLocalParamToCollection(self.inv_params, self.ik_ctl, ["posx"])

        v = XSIMath.CreateVector3()
        v.Sub(self.guide.apos[2], self.guide.apos[0])
        v.Cross(self.normal, v)
        v.NormalizeInPlace()
        v.ScaleInPlace(self.size*.5)
        v.AddInPlace(self.guide.apos[1])
        self.upv_cns = pri.addNullFromPos(self.root, self.getName("upv_cns"), v, self.size*.02)
        self.addToGroup(self.upv_cns, "hidden")

        self.upv_ctl = self.addCtl(self.upv_cns, "upv_ctl", self.upv_cns.Kinematics.Global.Transform, self.color_ik, "diamond", w=self.size*.05)
        par.setKeyableParameters(self.upv_ctl, self.t_params)
        par.addLocalParamToCollection(self.inv_params, self.upv_ctl, ["posx"])

        self.ik_ref = pri.addNull(self.ik_ctl, self.getName("ik_ref"), self.ik_ctl.Kinematics.Global.Transform, self.size * .1)
        self.addToGroup(self.ik_ref, "hidden")

        # Chain --------------------------------------------
        self.chain = pri.add2DChain(self.root, self.getName(""), self.guide.apos[:-1], self.normal, self.negate, 1, False)
        self.ctrn_loc = pri.addNullFromPos(self.chain.bones[0], self.getName("ctrn_loc"), self.guide.pos["knee"], self.size*.1)
        self.addToGroup(self.chain.all, "hidden")
        self.addToGroup(self.ctrn_loc, "hidden")

        # leash
        self.leash_crv = cur.addCnsCurve(self.root, self.getName("leash_crv"), [self.chain.bones[1], self.upv_ctl], False, 1)
        self.addToGroup(self.leash_crv, "unselectable")

        # shadows
        self.settings["division0"] = 4
        self.settings["division1"] = 4

        self.div0_loc = []
        for i in range(self.settings["division0"]):
            d = min(i/(self.settings["division0"]-1.0), 1-(.5/(self.settings["division0"]-1.0)))

            t = self.chain.bones[0].Kinematics.Global.Transform
            t.SetTranslation(vec.linearlyInterpolate(self.guide.pos["root"], self.guide.pos["knee"], d))
            div_loc = pri.addNull(self.chain.bones[0], self.getName("div%s_loc"%(i)), t, self.size*.05)
            self.addShadow(div_loc, i)
            self.div0_loc.append(div_loc)

        self.addShadow(self.ctrn_loc, self.settings["division0"])

        self.div_loc = []
        for i in range(self.settings["division1"]):
            d = max(i/(self.settings["division1"]-1.0), .5/(self.settings["division1"]-1.0))

            t = self.chain.bones[1].Kinematics.Global.Transform
            t.SetTranslation(vec.linearlyInterpolate(self.guide.pos["knee"], self.guide.pos["ankle"], d))
            div_loc = pri.addNull(self.chain.bones[1], self.getName("div%s_loc"%(i+self.settings["division0"]+1)), t, self.size*.05)
            self.addShadow(div_loc, i+self.settings["division0"]+1)
            self.div_loc.append(div_loc)

        self.addToGroup(self.div0_loc, "hidden")
        self.addToGroup(self.div_loc, "hidden")

        # Hook ----------------------------------------------
        t = self.chain.bones[1].Kinematics.Global.Transform
        t.SetTranslation(self.guide.pos["ankle"])
        self.end_ref = pri.addNull(self.chain.bones[1], self.getName("end_ref"), t, self.size * .1)
        self.addToGroup(self.end_ref, "hidden")

        self.addShadow(self.end_ref, "end")

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

        if self.settings["upvrefarray"]:
            self.upvref_names = self.settings["upvrefarray"].split(",")
        else:
            self.upvref_names = []

        self.ikref_count = len(self.ikref_names)
        self.upvref_count = len(self.upvref_names)

        # Anim -------------------------------------------
        # Default parameter to get a better display in the keying panel
        self.pFullName = self.addAnimParam(self.fullName, c.siString, self.fullName, None, None, None, None, False, True, True)

        # IK/FK
        self.pBlend      = self.addAnimParam("blend", c.siDouble, self.settings["blend"], 0, 1, 0, 1)
        self.pIkRoll     = self.addAnimParam("roll", c.siDouble, 0, -180, 180, -180, 180)
        self.pIkCns      = self.addAnimParam("ikcns", c.siBool, False, None, None, None, None, False, False, True)

        # Ik/Upv References
        if self.ikref_count > 1:
            self.pIkRef      = self.addAnimParam("ikref", c.siInt4, 0, 0, self.ikref_count-1)
        if self.upvref_count > 1:
            self.pUpvRef     = self.addAnimParam("upvref", c.siInt4, 0, 0, self.upvref_count-1)

        # Squash and Stretch
        # self.pScale      = self.addAnimParam("scale", c.siDouble, 1, 0, None, 0, 2)
        # self.pMaxStretch = self.addAnimParam("maxstretch", c.siDouble, self.settings["maxstretch"], 1, None, 1, 2)
        # self.pSoftness   = self.addAnimParam("softness", c.siDouble, 0, 0, 1, 0, 1)
        # self.pSlide      = self.addAnimParam("slide", c.siDouble, .5, 0, 1, 0, 1)
        # self.pReverse    = self.addAnimParam("reverse", c.siDouble, 0, 0, 1, 0, 1)

        # Setup ------------------------------------------
        self.ankle_outputs = [self.addSetupParam("ankle_shp_%s"%s, c.siDouble, 0, 0, 1, 0, 1) for s in "abcd"]

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):

        # Items ------------------------------------------
        self.ikrefItems = []
        for i, name in enumerate(self.ikref_names):
            self.ikrefItems.append(name)
            self.ikrefItems.append(i)

        self.upvrefItems = []
        for i, name in enumerate(self.upvref_names):
            self.upvrefItems.append(name)
            self.upvrefItems.append(i)

        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        # IK/FK
        group = tab.addGroup("FK / IK")
        row = group.addRow()
        row.addItem(self.pBlend.ScriptName, "Blend")
        # row.addButton(self.getName("ikfkSwitch"), "Switch")
        group.addItem(self.pIkRoll.ScriptName, "Roll")

        group.addItem(self.pIkCns.ScriptName, "Show ik cns Controler")

        # Ik/Upv References
        if self.ikref_count > 1:
            row = group.addRow()
            row.addEnumControl(self.pIkRef.ScriptName, self.ikrefItems, "IK Ref", c.siControlCombo)
            row.addButton(self.getName("switchIkRef"), "Switch")
        if self.upvref_count > 1:
            row = group.addRow()
            row.addEnumControl(self.pUpvRef.ScriptName, self.upvrefItems, "Upv Ref", c.siControlCombo)
            row.addButton(self.getName("switchUpvRef"), "Switch")

        # Ik/Fk solver
        # group = tab.addGroup("Stretch")
        # group.addItem(self.pScale.ScriptName, "Scale")
        # group.addItem(self.pMaxStretch.ScriptName, "Max Stretch")
        # group.addItem(self.pSlide.ScriptName, "Slide")
        # group.addItem(self.pReverse.ScriptName, "Reverse")
        # group.addItem(self.pSoftness.ScriptName, "Softness")

        # Setup ------------------------------------------
        tab = self.setup_layout.addTab(self.name)
        # Shapes
        shp_group = tab.addGroup("Shapes")
        group = shp_group.addGroup("Ankle")
        for param, s in zip(self.ankle_outputs, "abcd"):
            group.addItem(param.ScriptName, "shp_%s"%s)

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
        par.addExpression(self.fk0_ctl.Properties("visibility").Parameters("viewvis"), "1 - "+self.pBlend.FullName)
        par.addExpression(self.fk1_ctl.Properties("visibility").Parameters("viewvis"), "1 - "+self.pBlend.FullName)
        par.addExpression(self.fk2_ctl.Properties("visibility").Parameters("viewvis"), "1 - "+self.pBlend.FullName)

        par.addExpression(self.upv_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)
        par.addExpression(self.leash_crv.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)
        par.addExpression(self.ikcns_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName +" * "+ self.pIkCns.FullName)
        par.addExpression(self.ik_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)

        # Twist --------------------------------------------
        for i, div_loc in enumerate(self.div0_loc):

            if i == 0:
                cns = aop.gear_dualUpVDirCns(div_loc, self.chain.root, self.chain.bones[1])
                # cns = aop.dirCns(div_loc, self.chain.bones[1], None, False, "xy")
                # aop.gear_pointAtObjectAxis(cns, self.chain.root, [0,1,0])
            elif i == self.settings["division0"]-1:
                continue
            else:
                d = i/(self.settings["division0"]-1.0)

                cns = aop.dirCns(div_loc, self.chain.bones[1], None, False, "xy")
                op = aop.spinePointAtOp(cns, self.div0_loc[0], self.chain.bones[0], d)

        for i, div_loc in enumerate(self.div_loc):
            d = i/(self.settings["division1"]-1.0)
            par.addExpression(div_loc.Parameters("rotx"), self.end_ref.Parameters("rotx").FullName+" * "+str(d))

        # IK Solver-----------------------------------------
        # cns
        self.chain.eff.Kinematics.AddConstraint("Position", self.ik_ref, False)
        aop.chainUpvOp(self.chain, self.upv_ctl)

        for bone, fk_ctl, length, div in zip(self.chain.bones, [self.fk0_ctl, self.fk1_ctl], [self.length0, self.length1], self.div_loc):
        # for bone, fk in zip(self.chain.bones, [self.fk0_ctl, self.fk1_ctl]):
            # ik/fk orientation
            cns = bone.Kinematics.AddConstraint("Orientation", fk_ctl, False)
            par.addExpression(cns.Parameters("blendweight"), "1 - "+self.pBlend.FullName)

            # stretch
            fk_st = fk_ctl.Parameters("sclx").FullName + " * (1 - "+self.pBlend.FullName+")"
            root_eff_dist = "ctr_dist(%s.kine.global, %s.kine.global)"%(self.root.FullName, self.ik_ctl.FullName)
            ik_st = "cond("+root_eff_dist+" > "+str(self.chain.length)+", "+root_eff_dist+" / "+str(self.chain.length)+", 1) * "+self.pBlend.FullName

            parent_scl = bone.Parent3DObject.Parameters("sclx").FullName
            par.addExpression(bone.Parameters("sclx"), "("+fk_st+" + "+ik_st+")/"+parent_scl)

            # par.addExpression(div.Parameters("sclx"), bone.Parameters("length").FullName+"/"+str(length))

        # blend / roll
        par.addExpression(self.chain.blend, self.pBlend)
        par.addExpression(self.chain.roll, self.pIkRoll)

        # ctr_loc
        self.ctrn_loc.Kinematics.AddConstraint("Position", self.chain.bones[1], False)
        for s in "xyz":
            par.addExpression(self.ctrn_loc.Kinematics.Local.Parameters("rot"+s), self.chain.bones[1].Kinematics.Local.Parameters("rot" + s).FullName + " * .5")

        # Stretch -----------------------------------------
        # root_eff = "ctr_dist(%s.kine.global, %s.kine.global)"%(self.chain.root, self.ik_ref)
        # st_value = "(%s/%s)"%(root_eff,self.chain.length)
        # for bone in self.chain.bones:
            # par.addExpression(bone.Parameters("length"),
                              # "cond(%s>%s,%s*%s,%s)*%s + %s*(1 - %s)"%(root_eff,
                                                                     # self.chain.length,
                                                                     # bone.Parameters("length").Value,
                                                                     # st_value, bone.Parameters("length").Value,
                                                                     # self.pBlend.FullName,
                                                                     # bone.Parameters("length").Value,
                                                                     # self.pBlend.FullName))

        # Hook
        self.end_ref.Kinematics.AddConstraint("Position", self.chain.eff)
        self.end_ref.Kinematics.AddConstraint("Scaling", self.chain.eff)
        aop.poseCns(self.end_ref, self.fk2_ctl, True, False, True, False)
        cns = aop.poseCns(self.end_ref, self.ik_ref, True, False, True, False)
        par.addExpression(cns.Parameters("blendweight"), self.pBlend.fullName)
        par.addExpression(self.end_ref.Parameters("rotx"), 0)
        par.addExpression(self.end_ref.Parameters("roty"), 0)
        par.addExpression(self.end_ref.Parameters("rotz"), 0)
        par.setRotOrder(self.end_ref, "YZX")

        # Shape Reference ---------------------------------
        # shoulder
        aop.gear_rotationToPose(self.end_ref, self.chain.bones[1], self.ankle_outputs, "x", 0)

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):
        self.relatives["root"] = self.chain.bones[0]
        self.relatives["knee"] = self.chain.bones[1]
        self.relatives["ankle"] = self.chain.eff
        self.relatives["eff"] = self.chain.eff

    ## standard connection definition.
    # @param self
    def connect_standard(self):
        self.connect_standardWithIkRef()
