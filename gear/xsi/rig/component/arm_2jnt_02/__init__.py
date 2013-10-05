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

## @package gear.xsi.rig.component.arm_2jnt_02
# @author Jeremie Passerin, Miquel Campos

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c, dynDispatch, XSIFactory, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.vector as vec
import gear.xsi.transform as tra
import gear.xsi.parameter as par
import gear.xsi.primitive as pri
import gear.xsi.applyop as aop
import gear.xsi.fcurve as fcu

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
        self.fk0_ctl = self.addCtl(self.root, "fk0_ctl", t, self.color_fk, "cube", h=self.size*.1, w=1, d=self.size*.1, po=XSIMath.CreateVector3(.5*self.n_factor,0,0))
        self.fk0_ctl.Parameters("SclX").Value = self.length0
        par.setRotOrder(self.fk0_ctl, "XZY")
        tra.setRefPose(self.fk0_ctl, [-90,0,0], self.negate)
        xsi.SetNeutralPose(self.fk0_ctl, c.siST)
        par.setKeyableParameters(self.fk0_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk0_ctl, ["posx", "posy", "posz"])

        t = tra.getTransformLookingAt(self.guide.apos[1], self.guide.apos[2], self.normal, "xz", self.negate)
        self.fk1_ctl = self.addCtl(self.fk0_ctl, "fk1_ctl", t, self.color_fk, "cube", h=self.size*.1, w=1, d=self.size*.1, po=XSIMath.CreateVector3(.5*self.n_factor,0,0))
        self.fk1_ctl.Parameters("SclX").Value = self.length1/self.length0
        xsi.SetNeutralPose(self.fk1_ctl, c.siST)
        par.setKeyableParameters(self.fk1_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk1_ctl, ["posx", "posy", "posz"])

        t = tra.getTransformLookingAt(self.guide.apos[2], self.guide.apos[3], self.normal, "xz", self.negate)
        self.fk2_ctl = self.addCtl(self.fk1_ctl, "fk2_ctl", t, self.color_fk, "cube", h=self.size*.1, w=self.length2, d=self.size*.1, po=XSIMath.CreateVector3(self.length2*.5*self.n_factor,0,0))
        par.setRotOrder(self.fk2_ctl, "XZY")
        xsi.SetNeutralPose(self.fk2_ctl, c.siST)
        par.setKeyableParameters(self.fk2_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk2_ctl, ["posx", "posy", "posz"])

        # IK Controlers ------------------------------------
        self.ik_cns = pri.addNullFromPos(self.root, self.getName("ik_cns"), self.guide.apos[2], self.size*.02)
        self.addToGroup(self.ik_cns, "hidden")

        self.ikcns_ctl = self.addCtl(self.ik_cns, "ikcns_ctl", self.ik_cns.Kinematics.Global.Transform, self.color_ik, "null", h=self.size*.2)
        par.setKeyableParameters(self.ikcns_ctl)
        par.addLocalParamToCollection(self.inv_params, self.ikcns_ctl, ["posx", "rotx", "rotz"])

        t = tra.getTransformLookingAt(self.guide.apos[2], self.guide.apos[3], self.normal, "xz", self.negate)
        self.ik_ctl = self.addCtl(self.ikcns_ctl, "ik_ctl", t, self.color_ik, "cube", h=self.size*.12, w=self.length2, d=self.size*.12, po=XSIMath.CreateVector3(self.length2*.5*self.n_factor,0,0))
        tra.setRefPose(self.ik_ctl, [-90,0,0], self.negate)
        par.setRotOrder(self.ik_ctl, "XZY")
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

        self.upv_ctl = self.addCtl(self.upv_cns, "upv_ctl", self.upv_cns.Kinematics.Global.Transform, self.color_ik, "leash", h=self.size*.05, ap=self.guide.apos[1])
        par.setKeyableParameters(self.upv_ctl, self.t_params)
        par.addLocalParamToCollection(self.inv_params, self.upv_ctl, ["posx"])

        # Chain --------------------------------------------
        self.bone0 = pri.addNull(self.root, self.getName("0_jnt"), self.fk0_ctl.Kinematics.Global.Transform)
        pri.setNullDisplay(self.bone0, 0, 1, 4, self.n_factor*.5, 0, 0, 1, self.size*.01, self.size*.01)
        self.bone0.Kinematics.Global.Parameters("sclx").Value = self.length0
        self.bone1 = pri.addNull(self.bone0, self.getName("1_jnt"), self.fk1_ctl.Kinematics.Global.Transform)
        pri.setNullDisplay(self.bone1, 0, 1, 4, self.n_factor*.5, 0, 0, 1, self.size*.01, self.size*.01)
        self.bone1.Kinematics.Global.Parameters("sclx").Value = self.length1

        self.ctrn_loc = pri.addNullFromPos(self.bone0, self.getName("ctrn_loc"), self.guide.apos[1], self.size*.05)
        self.eff_loc  = pri.addNullFromPos(self.root, self.getName("eff_loc"), self.guide.apos[2], self.size*.05)

        self.addToGroup([self.bone0, self.bone1, self.ctrn_loc, self.eff_loc], "hidden")

        # wrist Tangent ________________________Miquel modification

        self.wristCtl = self.addCtl(self.eff_loc, "wristTang_ctl", self.eff_loc.Kinematics.Global.Transform, self.color_ik, "circle", w=self.size*.2)
        self.addShadow(self.wristCtl, "end")






        # Mid Controler ------------------------------------
        self.mid_ctl = self.addCtl(self.ctrn_loc, "mid_ctl", self.ctrn_loc.Kinematics.Global.Transform, self.color_ik, "sphere", h=self.size*.2)
        par.addLocalParamToCollection(self.inv_params, self.mid_ctl, ["posx", "posy", "posz"])


        # Twist references ---------------------------------
        t = tra.getFilteredTransform(self.fk0_ctl.Kinematics.Global.Transform, True, True, False)
        self.tws0_loc = pri.addNull(self.root, self.getName("tws0_loc"), t, self.size*.05)

        # shoulder Tangent ________________________Miquel modification

        self.shoulderCtl = self.addCtl(self.tws0_loc, "shoulderTang_ctl", self.tws0_loc.Kinematics.Global.Transform, self.color_ik, "circle", w=self.size*.2)

        self.tws0_rot = pri.addNull(self.shoulderCtl, self.getName("tws0_rot"), t)
        pri.setNullDisplay(self.tws0_rot, 0, self.size*.05, 2, 0, 0, 0, self.size*.01)

        self.tws1_loc = pri.addNull(self.ctrn_loc, self.getName("tws1_loc"), self.ctrn_loc.Kinematics.Global.Transform, self.size*.05)
        self.tws1_rot = pri.addNull(self.tws1_loc, self.getName("tws1_rot"), self.ctrn_loc.Kinematics.Global.Transform)
        pri.setNullDisplay(self.tws1_rot, 0, self.size*.05, 2, 0, 0, 0, self.size*.01)

        t = tra.getFilteredTransform(self.bone1.Kinematics.Global.Transform, True, True, False)
        t.SetTranslation(self.guide.apos[2])
        self.tws2_loc = pri.addNull(self.bone1, self.getName("tws2_loc"), t, self.size*.05)
        self.tws2_rot = pri.addNull(self.tws2_loc, self.getName("tws2_rot"),t)
        self.tws2_rot.Kinematics.Global.Parameters("SclX").Value = .001
        pri.setNullDisplay(self.tws2_rot, 0, self.size*.05, 2, 0, 0, 0, self.size*.01)

        self.addToGroup([self.tws0_loc, self.tws0_rot, self.tws1_loc, self.tws1_rot, self.tws2_loc, self.tws2_rot], "hidden")

        # End reference ------------------------------------
        t = tra.getFilteredTransform(self.tws2_rot.Kinematics.Global.Transform, True, True, False)
        self.end_ref = pri.addNull(self.tws2_rot, self.getName("end_ref"), t, self.size*.2)
        self.addToGroup(self.end_ref, "hidden")


        # Divisions ----------------------------------------
        # We have at least one division at the start, the end and one for the elbow.
        self.divisions = self.settings["div0"] + self.settings["div1"] + 3

        self.div_cns = []
        for i in range(self.divisions):

            div_cns = pri.addNull(self.tws0_loc, self.getName("div%s_loc"%i), XSIMath.CreateTransform())
            pri.setNullDisplay(div_cns, 1, self.size*.02, 10, 0, 0, 0, 1, 1, 2)
            self.addToGroup(div_cns, "hidden")

            self.div_cns.append(div_cns)

            self.lastShadow = self.addShadow(div_cns, i)

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
        self.pScale      = self.addAnimParam("scale", c.siDouble, 1, 0, None, 0, 2)
        self.pMaxStretch = self.addAnimParam("maxstretch", c.siDouble, self.settings["maxstretch"], 1, None, 1, 2)
        self.pSoftness   = self.addAnimParam("softness", c.siDouble, 0, 0, 1, 0, 1)
        self.pSlide      = self.addAnimParam("slide", c.siDouble, .5, 0, 1, 0, 1)
        self.pReverse    = self.addAnimParam("reverse", c.siDouble, 0, 0, 1, 0, 1)

        # Roundness
        self.pRoundness  = self.addAnimParam("roundness", c.siDouble, 0, 0, 1, 0, 1)

        # Volume
        self.pVolume  = self.addAnimParam("volume", c.siDouble, 1, 0, 1, 0, 1)

        # Tangents
        self.tWrist = self.addAnimParam("tWrist", c.siDouble, .001, 0.001, 2, 0.001, 2)
        self.tShoulder = self.addAnimParam("tShoulder", c.siDouble, .001, 0.001, 2, 0.001, 2)

        # Setup ------------------------------------------
        self.pDriver = self.addSetupParam("driver", c.siDouble, 0, 0, None, 0, 10, True)

        # FCurves
        self.pFCurveCombo = self.addSetupParam("fcurvecombo", c.siInt4, 0, 0, None)
        self.pSt_profile  = self.addSetupFCurveParam("st_profile", self.settings["st_profile"])
        self.pSq_profile  = self.addSetupFCurveParam("sq_profile", self.settings["sq_profile"])

        # Eval Fcurve
        self.st_value = fcu.getFCurveValues(self.pSt_profile.Value, self.divisions, .01)
        self.sq_value = fcu.getFCurveValues(self.pSq_profile.Value, self.divisions, .01)

        if self.options["mode"] == 1: # wip
            # Stretch/Squash/Roll params
            self.pEdit = self.addSetupParam("edit", c.siBool, False)
            self.pStretch = [self.addSetupParam("stretch_%s"%i, c.siDouble, self.st_value[i], -1, 1) for i in range(self.divisions)]
            self.pSquash  = [self.addSetupParam("squash_%s"%i, c.siDouble, self.sq_value[i], -1, 1) for i in range(self.divisions)]

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

        fcurveItems = ["Stretch", 0, "Squash", 1]

        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        # IK/FK
        group = tab.addGroup("FK / IK")
        row = group.addRow()
        row.addItem(self.pBlend.ScriptName, "Blend")
        row.addButton(self.getName("ikfkSwitch"), "Switch")
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
        group = tab.addGroup("Stretch")
        group.addItem(self.pScale.ScriptName, "Scale")
        group.addItem(self.pMaxStretch.ScriptName, "Max Stretch")
        group.addItem(self.pSlide.ScriptName, "Slide")
        group.addItem(self.pReverse.ScriptName, "Reverse")
        group.addItem(self.pSoftness.ScriptName, "Softness")

        # Divisions
        group = tab.addGroup("Volume")
        group.addItem(self.pVolume.ScriptName, "Volume")

        # Roundness
        group = tab.addGroup("Roundness")
        group.addItem(self.pRoundness.ScriptName, "Roundness")

         # Tangets
        group = tab.addGroup("Tangents")
        group.addItem(self.tWrist.ScriptName, "Tangent Wrist")
        group.addItem(self.tShoulder.ScriptName, "Tangent Shoulder")

        # Setup ------------------------------------------
        tab = self.setup_layout.addTab(self.name)

        group = tab.addGroup("Volume")
        group.addItem(self.pDriver.ScriptName, "Driver")

        if self.options["mode"] == 1: # wip
            # FCurves
            group = tab.addGroup("FCurves")
            group.addEnumControl(self.pFCurveCombo.ScriptName, fcurveItems, "FCurve", c.siControlCombo)

            fcv_item = group.addFCurve2(self.pSt_profile.ScriptName, "Divisions", "Stretch", -10, 110, 10, -110, 5, 5)
            fcv_item.addCondition("PPG."+self.pFCurveCombo.ScriptName+".Value == 0")
            fcv_item = group.addFCurve2(self.pSq_profile.ScriptName, "Divisions", "Squash", -10, 110, -10, 110, 5, 5)
            fcv_item.addCondition("PPG."+self.pFCurveCombo.ScriptName+".Value == 1")

            # Stretch / Squash / Roll params
            stretch_group = tab.addGroup("Values")
            stretch_group.addItem(self.pEdit.ScriptName, "Edit Values")
            stretch_group.addCondition("PPG."+self.pFCurveCombo.ScriptName+".Value == 0")
            squash_group = tab.addGroup("Values")
            squash_group.addItem(self.pEdit.ScriptName, "Edit Values")
            squash_group.addCondition("PPG."+self.pFCurveCombo.ScriptName+".Value == 1")

            for i in range(self.divisions):
                stretch_group.addItem(self.pStretch[i].ScriptName, "Stretch %s"%i)
                squash_group.addItem(self.pSquash[i].ScriptName, "Squash %s"%i)

                self.setup_layout.setCodeAfter("PPG."+self.pStretch[i].ScriptName+".ReadOnly = not PPG."+self.pEdit.ScriptName+".Value")
                self.setup_layout.setCodeAfter("PPG."+self.pSquash[i].ScriptName+".ReadOnly = not PPG."+self.pEdit.ScriptName+".Value")

            self.setup_layout.setCodeAfter("from gear.xsi.rig.component import logic\r\nreload(logic)" +"\r\n" \
                                    +"prop = PPG.Inspected(0)" +"\r\n" \
                                    +"if not PPG."+self.pEdit.ScriptName+".Value:" +"\r\n" \
                                    +"    logic.setParamsValueFromFCurve(prop, '"+self.pSt_profile.ScriptName+"', "+str(self.divisions)+", '"+self.getName("stretch_%s")+"', -1, 1)" +"\r\n" \
                                    +"    logic.setParamsValueFromFCurve(prop, '"+self.pSq_profile.ScriptName+"', "+str(self.divisions)+", '"+self.getName("squash_%s")+"', -1, 1)" +"\r\n")

    ## Define the logic of the anim and setup properties.
    # @param self
    def addLogic(self):

        # Anim -------------------------------------------
        self.anim_logic.addGlobalCode("import gear.xsi.rig.component.logic as logic")


        self.anim_logic.addOnClicked(self.getName("ikfkSwitch"),
                              "prop = PPG.Inspected(0)\r\n" +
                              "switcher = logic.IKFKSwitcher(prop.Model, prop.Parent3DObject, '"+self.getName()+"')\r\n" +
                              "switcher.switch()\r\n" +
                              "PPG.Refresh()\r\n")

        if self.ikref_count > 1:
            self.anim_logic.addOnClicked(self.getName("switchIkRef"),
                                     "logic.switchRef(PPG.Inspected(0), '"+self.ik_ctl.Name+"', '"+self.pIkRef.ScriptName+"', "+str(self.ikref_count)+")\r\n" +
                                     "PPG.Refresh()\r\n")
        if self.upvref_count > 1:
            self.anim_logic.addOnClicked(self.getName("switchUpvRef"),
                                     "logic.switchRef(PPG.Inspected(0), '"+self.upv_ctl.Name+"', '"+self.pUpvRef.ScriptName+"', "+str(self.upvref_count)+")\r\n" +
                                     "PPG.Refresh()\r\n")

        # Setup ------------------------------------------
        if self.options["mode"] == 1: # wip
            self.setup_logic.addOnChangedRefresh(self.pFCurveCombo.ScriptName)
            self.setup_logic.addOnChangedRefresh(self.pSt_profile.ScriptName)
            self.setup_logic.addOnChangedRefresh(self.pSq_profile.ScriptName)
            self.setup_logic.addOnChangedRefresh(self.pEdit.ScriptName)



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
        par.addExpression(self.ikcns_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName +" * "+ self.pIkCns.FullName)
        par.addExpression(self.ik_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)

        # Leash --------------------------------------------
        aop.clsCtrOp(self.upv_ctl, self.mid_ctl, [0])

        # IK Solver-----------------------------------------
        out = [self.bone0, self.bone1, None, self.eff_loc]
        op = aop.sn_ikfk2bone_op(out, self.root, self.ik_ctl, self.upv_ctl, self.fk0_ctl, self.fk1_ctl, self.fk2_ctl, self.length0, self.length1, self.negate)

        par.addExpression(op.Parameters("blend"), self.pBlend.FullName)
        par.addExpression(op.Parameters("roll"), self.pIkRoll.FullName)
        par.addExpression(op.Parameters("scaleA"), self.pScale.FullName)
        par.addExpression(op.Parameters("scaleB"), self.pScale.FullName)
        par.addExpression(op.Parameters("maxstretch"), self.pMaxStretch.FullName)
        par.addExpression(op.Parameters("softness"), self.pSoftness.FullName)
        par.addExpression(op.Parameters("slide"), self.pSlide.FullName)
        par.addExpression(op.Parameters("reverse"), self.pReverse.FullName)

        # I'm not using the output of the solver to get the ctrn because it only has a +/-180 degree
        # With this simple expression I have a much better result
        # Also remove scaling from ctrn
        for s in "xyz":
            par.addExpression(self.ctrn_loc.Kinematics.Local.Parameters("rot"+s), self.bone1.Kinematics.Local.Parameters("rot"+s).FullName + " * .5")
            par.addExpression(self.ctrn_loc.Kinematics.Global.Parameters("scl"+s), self.root.Kinematics.Global.Parameters("scl"+s).FullName)

        # Twist references ---------------------------------
        par.addExpression(self.pDriver, "(ctr_dist(%s, %s) + ctr_dist(%s, %s)) / %s"
                                        %(self.tws0_loc.Kinematics.Global.FullName, self.tws1_loc.Kinematics.Global.FullName,
                                          self.tws1_loc.Kinematics.Global.FullName, self.tws2_loc.Kinematics.Global.FullName,
                                          self.root.Kinematics.Global.Parameters("sclx").FullName))

        self.tws0_loc.Kinematics.AddConstraint("Pose", self.root, True)
        aop.dirCns(self.tws0_loc, self.mid_ctl, None, False, self.n_sign+"xy")

        self.tws1_loc.Kinematics.AddConstraint("Position", self.mid_ctl)
        self.tws1_loc.Kinematics.AddConstraint("Scaling", self.mid_ctl)
        self.tws1_rot.Kinematics.AddConstraint("Orientation", self.mid_ctl)
        par.addExpression(self.tws1_rot.Parameters("rotx"), 0)
        par.addExpression(self.tws1_rot.Parameters("roty"), 0)
        par.addExpression(self.tws1_rot.Parameters("rotz"), 0)

        self.tws2_loc.Kinematics.AddConstraint("Position", self.eff_loc)
        self.tws2_loc.Kinematics.AddConstraint("Scaling", self.eff_loc)
        self.cnsPoseWrist = aop.poseCns(self.tws2_rot, self.wristCtl, False, False, True, False)
        # The next 2 lines is for force the update on position. I dont know way but is not getting it  --Miquel
        self.cnsPoseWrist.Parameters("cnspos").Value = False
        self.cnsPoseWrist.Parameters("cnspos").Value = True
        #
        par.addExpression(self.tws2_rot.Parameters("rotx"), 0)
        par.addExpression(self.tws2_rot.Parameters("roty"), 0)
        par.addExpression(self.tws2_rot.Parameters("rotz"), 0)
        par.setRotOrder(self.tws2_rot, "YZX")


        par.addExpression(self.tws0_rot.SclX, self.tShoulder.FullName )
        #self.tws0_rot.SclX = .001
        par.addExpression(self.tws1_rot.SclX, self.pRoundness.FullName + " + .001")
        par.addExpression(self.tws2_rot.SclX, self.tWrist.FullName )
        #self.tws2_rot.SclX = .001

        par.setRotOrder(self.tws2_rot, "XYZ")

        # Divisions ----------------------------------------
        # at 0 or 1 the division will follow exactly the rotation of the controler.. and we wont have this nice tangent + roll
        for i, div_cns in enumerate(self.div_cns):

            if i < (self.settings["div0"]+1):
                perc = i*.5 / (self.settings["div0"]+1.0)
            else:
                perc = .5 + (i-self.settings["div0"]-1.0)*.5 / (self.settings["div1"]+1.0)

            perc = max(.001, min(.999, perc))

            # Roll
            if self.negate:
                op = aop.sn_rollsplinekine_op(div_cns, [self.tws2_rot, self.tws1_rot, self.tws0_rot], 1-perc)
            else:
                op = aop.sn_rollsplinekine_op(div_cns, [self.tws0_rot, self.tws1_rot, self.tws2_rot], perc)

            # Squash n Stretch
            op = aop.sn_squashstretch2_op(div_cns, self.root, self.pDriver.Value, "x")
            par.addExpression(op.Parameters("blend"), self.pVolume.FullName)
            par.addExpression(op.Parameters("driver"), self.pDriver.FullName)
            if self.options["mode"] == 1: # wip
                par.addExpression(op.Parameters("stretch"), self.pStretch[i])
                par.addExpression(op.Parameters("squash"), self.pSquash[i])
            else:
                op.Parameters("stretch").Value = self.st_value[i]
                op.Parameters("squash").Value = self.sq_value[i]

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):
        self.relatives["root"] = self.bone0
        self.relatives["elbow"] = self.bone1
        self.relatives["wrist"] = self.wristCtl
        self.relatives["eff"] = self.wristCtl
        self.relatives["wristRoll"] = self.lastShadow

    ## standard connection definition.
    # @param self
    def connect_standard(self):
        self.connect_standardWithIkRef()
