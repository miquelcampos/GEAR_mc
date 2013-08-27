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

## @package gear.xsi.rig.component.leg_3jnt_01
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c, dynDispatch, XSIFactory, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.vector as vec
import gear.xsi.transform as tra
import gear.xsi.icon as icon
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

        self.normal = self.getNormalFromPos(self.guide.apos[1:])

        self.length0 = vec.getDistance(self.guide.apos[0], self.guide.apos[1])
        self.length1 = vec.getDistance(self.guide.apos[1], self.guide.apos[2])
        self.length2 = vec.getDistance(self.guide.apos[2], self.guide.apos[3])
        self.length3 = vec.getDistance(self.guide.apos[3], self.guide.apos[4])

        # FK Controlers ------------------------------------
        t = tra.getTransformLookingAt(self.guide.apos[0], self.guide.apos[1], self.normal, "xz", self.negate)
        self.fk0_ctl = self.addCtl(self.root, "fk0_ctl", t, self.color_fk, "cube", w=1, h=self.size*.1, d=self.size*.1, po=XSIMath.CreateVector3(.5*self.n_factor,0,0))
        self.fk0_ctl.Kinematics.Global.Parameters("SclX").Value = self.length0
        xsi.SetNeutralPose(self.fk0_ctl)
        par.setKeyableParameters(self.fk0_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk0_ctl, ["posx", "posy", "posz"])

        t = tra.getTransformLookingAt(self.guide.apos[1], self.guide.apos[2], self.normal, "xz", self.negate)
        self.fk1_ctl = self.addCtl(self.fk0_ctl, "fk1_ctl", t, self.color_fk, "cube", w=1, h=self.size*.1, d=self.size*.1, po=XSIMath.CreateVector3(.5*self.n_factor,0,0))
        self.fk1_ctl.Kinematics.Global.Parameters("SclX").Value = self.length1
        xsi.SetNeutralPose(self.fk1_ctl, c.siST)
        par.setKeyableParameters(self.fk1_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk1_ctl, ["posx", "posy", "posz"])

        t = tra.getTransformLookingAt(self.guide.apos[2], self.guide.apos[3], self.normal, "xz", self.negate)
        self.fk2_ctl = self.addCtl(self.fk1_ctl, "fk2_ctl", t, self.color_fk, "cube", w=1, h=self.size*.1, d=self.size*.1, po=XSIMath.CreateVector3(.5*self.n_factor,0,0))
        self.fk2_ctl.Kinematics.Global.Parameters("SclX").Value = self.length2
        xsi.SetNeutralPose(self.fk2_ctl, c.siST)
        par.setKeyableParameters(self.fk2_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk2_ctl, ["posx", "posy", "posz"])

        t = tra.getTransformLookingAt(self.guide.apos[3], self.guide.apos[4], self.normal, "xz", self.negate)
        self.fk3_ctl = self.addCtl(self.fk2_ctl, "fk3_ctl", t, self.color_fk, "cube", w=self.length3, h=self.size*.1, d=self.size*.1, po=XSIMath.CreateVector3(self.length3*.5*self.n_factor,0,0))
        xsi.SetNeutralPose(self.fk3_ctl, c.siST)
        par.setKeyableParameters(self.fk3_ctl)
        par.addLocalParamToCollection(self.inv_params, self.fk3_ctl, ["posx", "posy", "posz"])

        # IK Controlers ------------------------------------
        self.ik_cns = pri.addNullFromPos(self.root, self.getName("ik_cns"), self.guide.apos[3], self.size * .02)
        self.addToGroup(self.ik_cns, "hidden")

        self.ikcns_ctl = self.addCtl(self.ik_cns, "ikcns_ctl", self.ik_cns.Kinematics.Global.Transform, self.color_ik, "null", h=self.size*.2)
        self.addToCtlGroup(self.ikcns_ctl)
        par.setKeyableParameters(self.ikcns_ctl)
        par.addLocalParamToCollection(self.inv_params, self.ikcns_ctl, ["posx", "rotx", "rotz"])

        t = tra.getTransformLookingAt(self.guide.apos[3], self.guide.apos[4], self.x_axis, "zx", False)
        self.ik_ctl = self.addCtl(self.ikcns_ctl, "ik_ctl", t, self.color_ik, "cube", h=self.size*.12, w=self.size*.12, d=self.length2, po=XSIMath.CreateVector3(0,0,self.length2*.5))
        par.setKeyableParameters(self.ik_ctl)
        par.addLocalParamToCollection(self.inv_params, self.ik_ctl, ["posx"])

        # Upv
        v = XSIMath.CreateVector3()
        v.Sub(self.guide.apos[2], self.guide.apos[0])
        v.Cross(self.normal, v)
        v.NormalizeInPlace()
        v.ScaleInPlace(self.size * -.5)
        v.AddInPlace(self.guide.apos[1])
        self.upv_cns = pri.addNullFromPos(self.root, self.getName("upv_cns"), v, self.size*.02)
        self.addToGroup(self.upv_cns, "hidden")

        self.upv_ctl = self.addCtl(self.upv_cns, "upv_ctl", self.upv_cns.Kinematics.Global.Transform, self.color_ik, "leash", h=self.size*.05, ap=self.guide.apos[1])
        par.setKeyableParameters(self.upv_ctl, self.t_params)
        par.addLocalParamToCollection(self.inv_params, self.upv_ctl, ["posx"])

        # References ---------------------------------------
        x = XSIMath.CreateVector3(0,-1,0)
        x.MulByRotationInPlace(self.ik_ctl.Kinematics.Global.Transform.Rotation)
        z = XSIMath.CreateVector3(1,0,0)
        z.MulByRotationInPlace(self.ik_ctl.Kinematics.Global.Transform.Rotation)

        r = tra.getRotationFromAxis(x, z, "xz", self.negate)
        t = self.ik_ctl.Kinematics.Global.Transform
        t.SetRotation(r)

        # Ik ref
        self.ik_ref = pri.addNull(self.ik_ctl, self.getName("ik_ref"), t, self.size * .1)
        self.addToGroup(self.ik_ref, "hidden")

        # Fk ref
        self.fk_ref = pri.addNull(self.fk3_ctl, self.getName("fk_ref"), t, self.size * .1)
        self.addToGroup(self.fk_ref, "hidden")

        # Roll Controler -----------------------------------
        if self.settings["roll"] == 0: # Roll with a controler
            self.roll_ctl = self.addCtl(self.root, "roll_ctl", self.ik_ctl.Kinematics.Global.Transform, self.color_ik, "bendedarrow2", w=self.length2*.5*self.n_factor, po=XSIMath.CreateVector3(0,self.length2*.5*self.n_factor,0))
            if self.negate:
                self.roll_ctl.Kinematics.Local.Parameters("rotx").Value = 180
                xsi.SetNeutralPose(self.roll_ctl)
            par.setKeyableParameters(self.roll_ctl, self.r_params)

        # Chain --------------------------------------------
        self.ref_chn = pri.add2DChain(self.root, self.getName("ref"), self.guide.apos[:3], self.normal, self.negate, self.size*.1, True)
        self.addToGroup(self.ref_chn.all, "hidden")

        self.end_chn = pri.add2DChain(self.ref_chn.bones[-1], self.getName("end"), self.guide.apos[2:4], self.normal, self.negate, self.size*.1, True)
        self.addToGroup(self.end_chn.all, "hidden")

        # Reference Nulls ---------------------------------
        self.ref_loc = []
        parent = self.root
        for i, ref in enumerate([self.fk0_ctl, self.fk1_ctl, self.fk2_ctl, self.fk_ref]):
            t = tra.getFilteredTransform(ref.Kinematics.Global.Transform, True, True, False)
            ref_loc = pri.addNull(parent, self.getName("ref%s_loc"%i), t, self.size*.1)
            self.addToGroup(ref_loc, "hidden")
            self.ref_loc.append(ref_loc)

            parent = ref_loc

        # Mid Controler ------------------------------------
        self.ctrn0_loc = pri.addNullFromPos(self.ref_loc[0], self.getName("ctrn0_loc"), self.guide.apos[1], self.size*.05)
        self.ctrn1_loc = pri.addNullFromPos(self.ref_loc[1], self.getName("ctrn1_loc"), self.guide.apos[2], self.size*.05)

        self.addToGroup([self.ctrn0_loc, self.ctrn1_loc], "hidden")

        self.mid0_ctl = self.addCtl(self.ctrn0_loc, "mid0_ctl", self.ctrn0_loc.Kinematics.Global.Transform, self.color_ik, "sphere", h=self.size*.1)
        par.addLocalParamToCollection(self.inv_params, self.mid0_ctl, ["posx", "posy", "posz"])
        self.mid1_ctl = self.addCtl(self.ctrn1_loc, "mid1_ctl", self.ctrn1_loc.Kinematics.Global.Transform, self.color_ik, "sphere", h=self.size*.1)
        par.addLocalParamToCollection(self.inv_params, self.mid1_ctl, ["posx", "posy", "posz"])

        # Twist references ---------------------------------
        t = tra.getTransformLookingAt(self.guide.apos[0], self.guide.apos[1], self.normal, "xz", self.negate)
        self.tws0_loc = pri.addNull(self.root, self.getName("tws0_loc"), t, self.size*.05)
        self.tws0_rot = pri.addNull(self.tws0_loc, self.getName("tws0_rot"), t)
        pri.setNullDisplay(self.tws0_rot, 0, self.size*.05, 2, 0, 0, 0, self.size*.01)

        self.tws1_loc = pri.addNull(self.ctrn0_loc, self.getName("tws1_loc"), self.ctrn0_loc.Kinematics.Global.Transform, self.size*.05)
        self.tws1_rot = pri.addNull(self.tws1_loc, self.getName("tws1_rot"), self.ctrn0_loc.Kinematics.Global.Transform)
        pri.setNullDisplay(self.tws1_rot, 0, self.size*.05, 2, 0, 0, 0, self.size*.01)

        self.tws2_loc = pri.addNull(self.ctrn1_loc, self.getName("tws2_loc"), self.ctrn1_loc.Kinematics.Global.Transform, self.size*.05)
        self.tws2_rot = pri.addNull(self.tws2_loc, self.getName("tws2_rot"), self.ctrn1_loc.Kinematics.Global.Transform)
        pri.setNullDisplay(self.tws2_rot, 0, self.size*.05, 2, 0, 0, 0, self.size*.01)

        t = tra.getFilteredTransform(self.ref_loc[-2].Kinematics.Global.Transform, True, True, False)
        t.SetTranslation(self.guide.apos[3])
        self.tws3_loc = pri.addNull(self.ref_loc[-2], self.getName("tws3_loc"), t, self.size*.05)
        self.tws3_rot = pri.addNull(self.tws3_loc, self.getName("tws3_rot"),t)
        self.tws3_rot.Kinematics.Global.Parameters("SclX").Value = .001
        pri.setNullDisplay(self.tws3_rot, 0, self.size*.05, 2, 0, 0, 0, self.size*.01)

        self.addToGroup([self.tws0_loc, self.tws0_rot, self.tws1_loc, self.tws1_rot, self.tws2_loc, self.tws2_rot, self.tws3_loc, self.tws3_rot], "hidden")

        # End reference ------------------------------------
        t = tra.getFilteredTransform(self.tws3_rot.Kinematics.Global.Transform, True, True, False)
        self.end_ref = pri.addNull(self.tws3_rot, self.getName("end_ref"), t, self.size*.2)
        self.addToGroup(self.end_ref, "hidden")
        self.addShadow(self.end_ref, "end")

        # Divisions ----------------------------------------
        # We have at least one division at the start, the end and one for the elbow.
        self.divisions = self.settings["div0"] + self.settings["div1"] + self.settings["div2"] + 4

        self.div_cns = []
        for i in range(self.divisions):

            div_cns = pri.addNull(self.tws0_loc, self.getName("div%s_loc"%i), XSIMath.CreateTransform())
            pri.setNullDisplay(div_cns, 1, self.size*.02, 10, 0, 0, 0, 1, 1, 2)
            self.addToGroup(div_cns, "hidden")

            self.div_cns.append(div_cns)

            self.addShadow(div_cns, i)

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
        self.pBlend  = self.addAnimParam("blend", c.siDouble, self.settings["blend"], 0, 1, 0, 1)
        self.pIkRoll = self.addAnimParam("roll", c.siDouble, 0, -180, 180, -180, 180)
        self.pIkCns  = self.addAnimParam("ikcns", c.siBool, False, None, None, None, None, False, False, True)

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
        self.pRoundness = self.addAnimParam("roundness", c.siDouble, 0, 0, 1, 0, 1)

        # Volume
        self.pVolume = self.addAnimParam("volume", c.siDouble, 1, 0, 1, 0, 1)

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
#        row.addButton(self.getName("ikfkSwitch"), "Switch")
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
#        group = tab.addGroup("Stretch")
#        group.addItem(self.pScale.ScriptName, "Scale")
#        group.addItem(self.pMaxStretch.ScriptName, "Max Stretch")
#        group.addItem(self.pSlide.ScriptName, "Slide")
#        group.addItem(self.pReverse.ScriptName, "Reverse")
#        group.addItem(self.pSoftness.ScriptName, "Softness")

        # Divisions
        group = tab.addGroup("Volume")
        group.addItem(self.pVolume.ScriptName, "Volume")

        # Roundness
        group = tab.addGroup("Roundness")
        group.addItem(self.pRoundness.ScriptName, "Roundness")

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
            stretch_group.addCondition("PPG."+self.pFCurveCombo.ScriptName+".Value == 0")
            row = stretch_group.addRow()
            row.addItem(self.pEdit.ScriptName, "Edit Values")
            #row.addButton("Bake", "Bake To FCurve")
            squash_group = tab.addGroup("Values")
            squash_group.addCondition("PPG."+self.pFCurveCombo.ScriptName+".Value == 1")
            row = squash_group.addRow()
            row.addItem(self.pEdit.ScriptName, "Edit Values")
            #row.addButton("Bake", "Bake To FCurve")

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

            self.setup_logic.addOnClicked("Bake", "Application.LogMessage('hey')")

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
        par.addExpression(self.fk3_ctl.Properties("visibility").Parameters("viewvis"), "1 - "+self.pBlend.FullName)

        par.addExpression(self.upv_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)
        par.addExpression(self.ikcns_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName +" * "+ self.pIkCns.FullName)
        par.addExpression(self.ik_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)

        if self.settings["roll"] == 0:
            par.addExpression(self.roll_ctl.Properties("visibility").Parameters("viewvis"), self.pBlend.FullName)

        # Leash --------------------------------------------
        aop.clsCtrOp(self.upv_ctl, self.mid0_ctl, [0])

        # IK Solver-----------------------------------------
        self.roll_ctl.Kinematics.AddConstraint("Position", self.ik_ref, False)

        self.ref_chn.eff.Kinematics.AddConstraint("Pose", self.roll_ctl, True)
        self.end_chn.eff.Kinematics.AddConstraint("Pose", self.roll_ctl, True)

        op = xsi.ApplyOp("SkeletonUpVector", self.ref_chn.bones[0].FullName+";"+self.upv_ctl.FullName)[0]
        par.addExpression(self.ref_chn.roll, self.pIkRoll.FullName + " + 180")
        op = xsi.ApplyOp("SkeletonUpVector", self.end_chn.bones[0].FullName+";"+self.upv_ctl.FullName)[0]
        par.addExpression(self.end_chn.roll, self.pIkRoll.FullName + " + 180")

        # ctrn
        for s in "xyz":
            par.addExpression(self.ctrn0_loc.Kinematics.Local.Parameters("rot" + s), self.ref_loc[1].Kinematics.Local.Parameters("rot" + s).FullName + " * .5")
            par.addExpression(self.ctrn0_loc.Kinematics.Global.Parameters("scl" + s), self.root.Kinematics.Global.Parameters("scl" + s).FullName)
            par.addExpression(self.ctrn1_loc.Kinematics.Local.Parameters("rot" + s), self.ref_loc[2].Kinematics.Local.Parameters("rot" + s).FullName + " * .5")
            par.addExpression(self.ctrn1_loc.Kinematics.Global.Parameters("scl" + s), self.root.Kinematics.Global.Parameters("scl" + s).FullName)

        self.ctrn0_loc.Kinematics.AddConstraint("Position", self.ref_loc[1], False)
        self.ctrn1_loc.Kinematics.AddConstraint("Position", self.ref_loc[2], False)

        # References Nulls ---------------------------------
        fk_ref = [self.fk0_ctl, self.fk1_ctl, self.fk2_ctl, self.fk_ref]
        ik_ref = [self.ref_chn.bones[0], self.ref_chn.bones[1], self.end_chn.bones[0], self.ik_ref]
        for i, ref_loc in enumerate(self.ref_loc):

            # fk
            cns = ref_loc.Kinematics.AddConstraint("Orientation", fk_ref[i], False)
            if i != len(self.ref_loc)-1:
                cns = aop.dirCns(ref_loc, fk_ref[i+1], None, False, self.n_sign+"xz")
                par.addExpression(cns.Parameters("blendweight"), "1 - " + self.pBlend.FullName)

            #ik
            cns = ref_loc.Kinematics.AddConstraint("Orientation", ik_ref[i], False)
            par.addExpression(cns.Parameters("blendweight"), self.pBlend.FullName)

            for s in "xyz":
                par.addExpression(ref_loc.Kinematics.Local.Parameters("rot"+s), 0)

        par.addExpression(self.ref_loc[1].Kinematics.Local.Parameters("posx"), self.n_sign+" (ctr_dist(%s.kine.global, %s.kine.global) * (1 - %s) + ctr_dist(%s.kine.global, %s.kine.global) * %s)"%(self.fk0_ctl.FullName, self.fk1_ctl.FullName, self.pBlend.FullName, self.ref_chn.bones[0].FullName, self.ref_chn.bones[1].FullName, self.pBlend.FullName))
        par.addExpression(self.ref_loc[2].Kinematics.Local.Parameters("posx"), self.n_sign+" (ctr_dist(%s.kine.global, %s.kine.global) * (1 - %s) + ctr_dist(%s.kine.global, %s.kine.global) * %s)"%(self.fk1_ctl.FullName, self.fk2_ctl.FullName, self.pBlend.FullName, self.ref_chn.bones[1].FullName, self.end_chn.bones[0], self.pBlend.FullName))
        par.addExpression(self.ref_loc[3].Kinematics.Local.Parameters("posx"), self.n_sign+" (ctr_dist(%s.kine.global, %s.kine.global) * (1 - %s) + ctr_dist(%s.kine.global, %s.kine.global) * %s)"%(self.fk2_ctl.FullName, self.fk3_ctl.FullName, self.pBlend.FullName, self.end_chn.bones[0].FullName, self.end_chn.eff, self.pBlend.FullName))

        # Global Scale
        for s in "xyz":   
            par.addExpression(self.ref_loc[0].Kinematics.Global.Parameters("scl%s"%s), 1)     
            par.addExpression(self.end_ref.Kinematics.Global.Parameters("scl%s"%s), self.root.Kinematics.Global.Parameters("scl%s"%s))

        # Twist references ---------------------------------
        par.addExpression(self.pDriver, "(ctr_dist(%s, %s) + ctr_dist(%s, %s) + ctr_dist(%s, %s)) / %s"
                                        %(self.tws0_loc.Kinematics.Global.FullName, self.tws1_loc.Kinematics.Global.FullName,
                                          self.tws1_loc.Kinematics.Global.FullName, self.tws2_loc.Kinematics.Global.FullName,
                                          self.tws2_loc.Kinematics.Global.FullName, self.tws3_loc.Kinematics.Global.FullName,
                                          self.root.Kinematics.Global.Parameters("sclx").FullName))

        self.tws0_loc.Kinematics.AddConstraint("Pose", self.root, True)
        aop.dirCns(self.tws0_loc, self.mid0_ctl, None, False, self.n_sign+"xy")
        
        self.tws1_loc.Kinematics.AddConstraint("Position", self.mid0_ctl)
        self.tws1_loc.Kinematics.AddConstraint("Scaling", self.mid0_ctl)
        self.tws1_rot.Kinematics.AddConstraint("Orientation", self.mid0_ctl)
        par.addExpression(self.tws1_rot.Parameters("rotx"), 0)
        par.addExpression(self.tws1_rot.Parameters("roty"), 0)
        par.addExpression(self.tws1_rot.Parameters("rotz"), 0)

        self.tws2_loc.Kinematics.AddConstraint("Position", self.mid1_ctl)
        self.tws2_loc.Kinematics.AddConstraint("Scaling", self.mid1_ctl)
        self.tws2_rot.Kinematics.AddConstraint("Orientation", self.mid1_ctl)
        par.addExpression(self.tws2_rot.Parameters("rotx"), 0)
        par.addExpression(self.tws2_rot.Parameters("roty"), 0)
        par.addExpression(self.tws2_rot.Parameters("rotz"), 0)

        self.tws3_loc.Kinematics.AddConstraint("Position", self.ref_loc[-1])
        #self.tws3_loc.Kinematics.AddConstraint("Scaling", self.eff_loc)
        aop.poseCns(self.tws3_rot, self.fk_ref, False, False, True, False)
        cns = aop.poseCns(self.tws3_rot, self.ik_ref, True, False, True, False)
        par.addExpression(cns.Parameters("blendweight"), self.pBlend.FullName)
        par.addExpression(self.tws3_rot.Parameters("rotx"), 0)
        par.addExpression(self.tws3_rot.Parameters("roty"), 0)
        par.addExpression(self.tws3_rot.Parameters("rotz"), 0)
        par.setRotOrder(self.tws3_rot, "YZX")

        self.tws0_rot.SclX = .001
        par.addExpression(self.tws1_rot.SclX, self.pRoundness.FullName + " + .001")
        par.addExpression(self.tws2_rot.SclX, self.pRoundness.FullName + " + .001")
        self.tws3_rot.SclX = .001

        # Divisions ----------------------------------------
        # at 0 or 1 the division will follow exactly the rotation of the controler.. and we wont have this nice tangent + roll
        for i, div_cns in enumerate(self.div_cns):

            if i < (self.settings["div0"]+1):
                perc = i / ((self.settings["div0"]+1.0)*3)
            elif i < (self.settings["div0"]+self.settings["div1"]+2):
                perc = (1/3.0) + ((i-self.settings["div0"]-1.0) / ((self.settings["div1"]+1.0)*3))
            else:
                perc = (2/3.0) + ((i-self.settings["div0"]-self.settings["div1"]-2.0) / ((self.settings["div2"]+1.0)*3))

            perc = max(.001, min(.999, perc))

            if self.negate:
                op = aop.sn_rollsplinekine_op(div_cns, [self.tws3_rot, self.tws2_rot, self.tws1_rot, self.tws0_rot], 1-perc)
            else:
                op = aop.sn_rollsplinekine_op(div_cns, [self.tws0_rot, self.tws1_rot, self.tws2_rot, self.tws3_rot], perc)

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

#        # Foot --------------------------------------------
#        aop.poseCns(self.foot_ref, self.tws2_rot, True, True, True, False)
        
    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):

        self.relatives["root"] = self.ref_loc[0]
        self.relatives["knee"] = self.ref_loc[1]
        self.relatives["ankle"] = self.ref_loc[2]
        self.relatives["meta"] = self.ref_loc[3]
        self.relatives["eff"] = self.ref_loc[3]


    ## standard connection definition.
    # @param self
    def connect_standard(self):
        self.connect_standardWithIkRef()
