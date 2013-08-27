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
    Company:    Studio Nest (TM)
    Date:       2010 / 11 / 15

'''

## @package gear.xsi.rig.component.neck_ik_02
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c, dynDispatch, XSIFactory, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.transform as tra
import gear.xsi.parameter as par
import gear.xsi.vector as vec
import gear.xsi.applyop as aop
import gear.xsi.primitive as pri
import gear.xsi.curve as cur
import gear.xsi.fcurve as fcu

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

        # Root ---------------------------------------------
        # For this component we need the root to be correctly oriented
        t = tra.getTransformLookingAt(self.guide.apos[0], self.guide.apos[1], self.guide.blades["blade"].z, "yx", self.negate)
        self.root = pri.addNull(self.model, self.getName("root"), t, self.size *.2)
        self.addToGroup(self.root, "hidden")

        # Shd ----------------------------------------------
        if self.options["shadowRig"]:
            self.shd_org = self.rig.shd_org.AddNull(self.getName("shd_org"))
            self.addToGroup(self.shd_org, "hidden")
            
    ## Add all the objects needed to create the component.
    # @param self
    def addObjects(self):

        # Ik Controlers ------------------------------------
        t = tra.getTransformLookingAt(self.guide.pos["tan1"], self.guide.pos["neck"], self.guide.blades["blade"].z, "yx", self.negate)
        t.SetTranslation(self.guide.pos["neck"])
        self.ik_cns = pri.addNull(self.root, self.getName("ik_cns"), t, self.size*.02)
        self.addToGroup(self.ik_cns, "hidden")

        self.ik_ctl = self.addCtl(self.ik_cns, "ik_ctl", t, self.color_ik, "compas", w=self.size*.5)
        par.setRotOrder(self.ik_ctl, "ZXY")
        par.setKeyableParameters(self.ik_ctl)
        xsi.SetNeutralPose(self.ik_ctl, c.siTrn)

        # Tangents -----------------------------------------
        t.SetTranslation(self.guide.pos["tan1"])
        self.tan1_loc = pri.addNull(self.ik_ctl, self.getName("tan1_loc"), t, self.size*.1)
        par.setKeyableParameters(self.tan1_loc, self.t_params)
        xsi.SetNeutralPose(self.tan1_loc, c.siTrn)
        self.addToGroup(self.tan1_loc, "hidden")
        
        t = tra.getTransformLookingAt(self.guide.pos["root"], self.guide.pos["tan0"], self.guide.blades["blade"].z, "yx", self.negate)
        t.SetTranslation(self.guide.pos["tan0"])
        self.tan0_loc = pri.addNull(self.root, self.getName("tan0_loc"), t, self.size*.1)
        xsi.SetNeutralPose(self.tan0_loc, c.siTrn)
        self.addToGroup(self.tan0_loc, "hidden")

        # Curves -------------------------------------------
        self.mst_crv = cur.addCnsCurve(self.root, self.getName("mst_crv"), [self.root, self.tan0_loc, self.tan1_loc, self.ik_ctl], False, 3)
        self.slv_crv = cur.addCurve(self.root, self.getName("slv_crv"), [1]*10*4, False, 3)
        self.addToGroup([self.mst_crv, self.slv_crv], "hidden")

        # Division -----------------------------------------
        # The user only define how many intermediate division he wants.
        # First and last divisions are an obligation.
        parentdiv = self.root
        parentctl = self.root
        self.div_cns = []
        self.fk_ctl = []
        for i in range(self.settings["division"]):

            # References
            div_cns = parentdiv.AddNull(self.getName("%s_cns"%i))
            pri.setNullDisplay(div_cns, 1, self.size*.05, 10, 0, 0, 0, 1, 1, 2)
            self.addToGroup(div_cns, "hidden")

            self.div_cns.append(div_cns)
            parentdiv = div_cns

            # Controlers
            if i == self.settings["division"]-1:
                fk_ctl = pri.addNull(parentctl, self.getName("fk%s_cns"%i), parentctl.Kinematics.Global.Transform, self.size*.2)
                self.addToGroup(fk_ctl, "hidden")
            else:
                fk_ctl = self.addCtl(parentctl, "fk%s_ctl"%i, parentctl.Kinematics.Global.Transform, self.color_fk, "cube", w=self.size*.5, h=self.size*.05, d=self.size*.5)

            self.fk_ctl.append(fk_ctl)
            parentctl = fk_ctl

            # Deformers (Shadow)
            self.addShadow(fk_ctl, i)

        # Head ---------------------------------------------
        t = tra.getTransformLookingAt(self.guide.pos["head"], self.guide.pos["eff"], self.guide.blades["blade"].z, "yx", self.negate)
        self.head_cns = pri.addNull(self.root, self.getName("head_cns"), t, self.size*.1)
        self.addToGroup(self.head_cns, "hidden")

        dist = vec.getDistance(self.guide.pos["head"], self.guide.pos["eff"])
        self.head_ctl = self.addCtl(self.head_cns, "head_ctl", t, self.color_fk, "cube", w=self.size*.5, h=dist, d=self.size*.5, po=XSIMath.CreateVector3(0,dist*.5,0))

        self.addShadow(self.head_ctl, "head")

    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):

        if self.settings["headrefarray"]:
            self.headref_names = self.settings["headrefarray"].split(",")
        else:
            self.headref_names = []

        if self.settings["ikrefarray"]:
            self.ikref_names = self.settings["ikrefarray"].split(",")
        else:
            self.ikref_names = []

        self.headref_count = len(self.headref_names)
        self.ikref_count = len(self.ikref_names)

        # Anim -------------------------------------------
        # Default parameter to get a better display in the keying panel
        self.pFullName = self.addAnimParam(self.fullName, c.siString, self.fullName, None, None, None, None, False, True, True)

        self.pShowIk = self.addAnimParam("showik", c.siBool, True, None, None, None, None, False, False, False)
        self.pShowFk = self.addAnimParam("showfk", c.siBool, True, None, None, None, None, False, False, False)

        # Ik/Head References
        if self.headref_count > 0:
            self.pHeadRef = self.addAnimParam("headref", c.siInt4, 0, 0, self.headref_count)
        if self.ikref_count > 1:
            self.pIkRef = self.addAnimParam("ikref", c.siInt4, 0, 0, self.ikref_count-1)

        self.pMaxStretch = self.addAnimParam("maxstretch", c.siDouble, self.settings["maxstretch"], 1, None, 1, 3)
        self.pMaxSquash = self.addAnimParam("maxsquash", c.siDouble, self.settings["maxsquash"], 0, 1, 0, 1)
        self.pSoftness = self.addAnimParam("softness", c.siDouble, self.settings["softness"], 0, 1, 0, 1)

        self.pLockOri = self.addAnimParam("lock_ori", c.siDouble, 1, 0, 1, 0, 1)
        
        self.pTan0 = self.addAnimParam("tan0", c.siDouble, 1, 0, None, 0, 4)
        self.pTan1 = self.addAnimParam("tan1", c.siDouble, 1, 0, None, 0, 4)

        # Volume
        self.pVolume = self.addAnimParam("volume", c.siDouble, 1, 0, 1, 0, 1)

        # Setup ------------------------------------------
        self.pDriver = self.addSetupParam("driver", c.siDouble, 0, 0, None, 0, 10)

        # FCurves
        self.pFCurveCombo = self.addSetupParam("fcurvecombo", c.siInt4, 0, 0, None)
        self.pSt_profile  = self.addSetupFCurveParam("st_profile", self.settings["st_profile"])
        self.pSq_profile  = self.addSetupFCurveParam("sq_profile", self.settings["sq_profile"])

        # Eval Fcurve
        self.st_value = fcu.getFCurveValues(self.pSt_profile.Value, self.settings["division"], .01)
        self.sq_value = fcu.getFCurveValues(self.pSq_profile.Value, self.settings["division"], .01)

        if self.options["mode"] == 1: # wip
            # Stretch/Squash/Roll params
            self.pEdit = self.addSetupParam("edit", c.siBool, False)
            self.pStretch = [self.addSetupParam("stretch_%s"%i, c.siDouble, self.st_value[i], -1, 1) for i in range(self.settings["division"])]
            self.pSquash  = [self.addSetupParam("squash_%s"%i, c.siDouble, self.sq_value[i], -1, 1) for i in range(self.settings["division"])]

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):

        # Items ------------------------------------------
        self.headrefItems = ["self", 0]
        for i, name in enumerate(self.headref_names):
            self.headrefItems.append(name)
            self.headrefItems.append(i+1)

        self.ikrefItems = []
        for i, name in enumerate(self.ikref_names):
            self.ikrefItems.append(name)
            self.ikrefItems.append(i)

        fcurveItems = ["Stretch", 0, "Squash", 1]

        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        # Visibilities
        group = tab.addGroup("Visibilities")
        group.addItem(self.pShowIk.ScriptName, "Show IK controlers")
        group.addItem(self.pShowFk.ScriptName, "Show FK controlers")

        # Ik/Upv References
        if self.headref_count > 0:
            row = group.addRow()
            row.addEnumControl(self.pHeadRef.ScriptName, self.headrefItems, "Head Ref", c.siControlCombo)
            row.addButton(self.getName("switchHeadRef"), "Switch")
            
        if self.ikref_count > 1:
            row = group.addRow()
            row.addEnumControl(self.pIkRef.ScriptName, self.ikrefItems, "IK Ref", c.siControlCombo)
            row.addButton(self.getName("switchIkRef"), "Switch")

        # Spine behavior
        group = tab.addGroup("Squash and Stretch")
        group.addItem(self.pMaxStretch.ScriptName, "Max Stretch")
        group.addItem(self.pMaxSquash.ScriptName, "Max Squash")
        group.addItem(self.pSoftness.ScriptName, "Softness")

        group = tab.addGroup("Orientation Lock")
        group.addItem(self.pLockOri.ScriptName, "Head")

        group = tab.addGroup("Tangent")
        group.addItem(self.pTan1.ScriptName, "Top")
        group.addItem(self.pTan0.ScriptName, "Base")

        # Volume
        group = tab.addGroup("Volume")
        group.addItem(self.pVolume.ScriptName, "Volume")

        # Setup ------------------------------------------

        # Layout
        tab = self.setup_layout.addTab(self.name)

        group = tab.addGroup("volume")
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

            for i in range(self.settings["division"]):
                stretch_group.addItem(self.pStretch[i].ScriptName, "Stretch %s"%i)
                squash_group.addItem(self.pSquash[i].ScriptName, "Squash %s"%i)

                self.setup_layout.setCodeAfter("PPG."+self.pStretch[i].ScriptName+".ReadOnly = not PPG."+self.pEdit.ScriptName+".Value")
                self.setup_layout.setCodeAfter("PPG."+self.pSquash[i].ScriptName+".ReadOnly = not PPG."+self.pEdit.ScriptName+".Value")

            self.setup_layout.setCodeAfter("from gear.xsi.rig.component import logic\r\nreload(logic)" +"\r\n" \
                                    +"prop = PPG.Inspected(0)" +"\r\n" \
                                    +"if not PPG."+self.pEdit.ScriptName+".Value:" +"\r\n" \
                                    +"    logic.setParamsValueFromFCurve(prop, '"+self.pSt_profile.ScriptName+"', "+str(self.settings["division"])+", '"+self.getName("stretch_%s")+"', -1, 1)" +"\r\n" \
                                    +"    logic.setParamsValueFromFCurve(prop, '"+self.pSq_profile.ScriptName+"', "+str(self.settings["division"])+", '"+self.getName("squash_%s")+"', -1, 1)" +"\r\n")
                                    
    ## Define the logic of the anim and setup properties.
    # @param self
    def addLogic(self):

        # Anim -------------------------------------------
        self.anim_logic.addGlobalCode("import gear.xsi.rig.component.logic as logic")
        if self.ikref_count > 1:
            self.anim_logic.addOnClicked(self.getName("switchIkRef"),
                                     "logic.switchRef(PPG.Inspected(0), '"+self.ik_ctl.Name+"', '"+self.pIkRef.ScriptName+"', "+str(self.ikref_count)+")\r\n" +
                                     "PPG.Refresh()\r\n")
        if self.headref_count > 0:
            self.anim_logic.addOnClicked(self.getName("switchHeadRef"),
                                     "logic.switchRef(PPG.Inspected(0), '"+self.head_ctl.Name+"', '"+self.pHeadRef.ScriptName+"', "+str(self.headref_count + 1)+")\r\n" +
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
        par.addExpression(self.ik_ctl.Properties("visibility").Parameters("viewvis"), self.pShowIk.FullName)
        for fk_ctl in self.fk_ctl:
            par.addExpression(fk_ctl.Properties("visibility").Parameters("viewvis"), self.pShowFk.FullName)

        # Tangent position ---------------------------------
        d = vec.getDistance(self.guide.pos["root"], self.guide.pos["neck"])

        exp = self.pTan0.FullName + " * " + str(self.tan0_loc.Parameters("nposy").Value)+" * (ctr_dist("+self.root.FullName+","+self.ik_ctl.FullName+") / "+str(d)+")"
        par.addExpression(self.tan0_loc.Parameters("nposy"), exp)

        exp = self.pTan1.FullName + " * " + str(self.tan1_loc.Parameters("nposy").Value)+" * (ctr_dist("+self.root.FullName+","+self.ik_ctl.FullName+") / "+str(d)+")"
        par.addExpression(self.tan1_loc.Parameters("nposy"), exp)

        # Curves -------------------------------------------
        op = aop.sn_curveslide2_op(self.slv_crv, self.mst_crv, 0, 1.5, .5, .5)

        par.addExpression(op.Parameters("position"), 0)
        par.addExpression(op.Parameters("maxstretch"), self.pMaxStretch.FullName)
        par.addExpression(op.Parameters("maxsquash"), self.pMaxSquash.FullName)
        par.addExpression(op.Parameters("softness"), self.pSoftness.FullName)

        # Division -----------------------------------------
        for i in range(self.settings["division"]):

            # References
            u = i / (self.settings["division"]-1.0)
            div_cns = self.div_cns[i]

            cns = aop.pathCns(div_cns, self.slv_crv, 0, u*100, True, None, False)

            cns.Parameters("dirx").Value = 0
            cns.Parameters("diry").Value = 1
            cns.Parameters("dirz").Value = 0

            cns.Parameters("upx").Value = 0
            cns.Parameters("upy").Value = 0
            cns.Parameters("upz").Value = -1

            # Roll
            aop.spinePointAtOp(cns, self.root, self.ik_ctl, u)

            # Squash n Stretch
            op = aop.sn_squashstretch2_op(div_cns, self.slv_crv, self.slv_crv.ActivePrimitive.Geometry.Curves(0).Length, "y")
            par.addExpression(op.Parameters("blend"), self.pVolume.FullName)
            par.addExpression(op.Parameters("driver"), self.pDriver.FullName)
            if self.options["mode"] == 1: # wip
                par.addExpression(op.Parameters("stretch"), self.pStretch[i])
                par.addExpression(op.Parameters("squash"), self.pSquash[i])
            else:
                import gear
                op.Parameters("stretch").Value = self.st_value[i]
                op.Parameters("squash").Value = self.sq_value[i]

            # Controlers
            fk_ctl = self.fk_ctl[i]

            for s in "xyz":
                par.addExpression(fk_ctl.Parameters("npos"+s), div_cns.Parameters("pos"+s).FullName)
                par.addExpression(fk_ctl.Parameters("nrot"+s), div_cns.Parameters("rot"+s).FullName)
                par.addExpression(fk_ctl.Kinematics.Global.Parameters("scl"+s), div_cns.Kinematics.Global.Parameters("scl"+s).FullName)

        # Orientation Lock
        cns = self.div_cns[-1].Kinematics.AddConstraint("Orientation", self.ik_ctl, False)
        par.addExpression(cns.Parameters("blendweight"), self.pLockOri.FullName)

        # Volume -------------------------------------------
        op = aop.sn_curvelength_op(self.pDriver, self.slv_crv)

        # Head ---------------------------------------------
        self.fk_ctl[-1].AddChild(self.head_cns)
        if self.headref_count > 0:
            cns = self.head_cns.Kinematics.AddConstraint("Orientation", self.fk_ctl[-1], True)
            par.addExpression(cns.Parameters("active"), self.pHeadRef.FullName+" == 0")

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):
        self.relatives["root"] = self.root
        self.relatives["tan1"] = self.root
        self.relatives["tan2"] = self.head_ctl
        self.relatives["neck"] = self.head_ctl
        self.relatives["head"] = self.head_ctl
        self.relatives["eff"] = self.head_ctl

    ## standard connection definition.
    # @param self
    def connect_standard(self):
        self.connect_standardWithIkRef()

    ## standard connection definition with ik and upv references.
    # @param self
    def connect_standardWithIkRef(self):
        self.parent.AddChild(self.root)

        cns = aop.poseCns(self.head_cns, self.fk_ctl[-1], True, True, True, False)
        
        # Set the Head Reference
        if self.settings["headrefarray"]:
            ref_names = self.settings["headrefarray"].split(",")
            for i, ref_name in enumerate(ref_names):
                ref = self.rig.findChild(ref_name)
                cns = aop.poseCns(self.head_cns, ref, True, False, True, False)
                par.addExpression(cns.Parameters("active"), self.pHeadRef.FullName+" == "+str(i+1))

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
