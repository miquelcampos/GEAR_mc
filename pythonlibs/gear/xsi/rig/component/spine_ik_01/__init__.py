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

## @package gear.xsi.rig.component.spine_ik_01
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c, dynDispatch, XSIFactory

from gear.xsi.rig.component import MainComponent

import gear.xsi.icon as icon
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
    ## Add all the objects needed to create the component.
    # @param self
    def addObjects(self):

        # Ik Controlers ------------------------------------
        t = tra.getTransformLookingAt(self.guide.apos[0], self.guide.apos[1], self.guide.blades["blade"].z, "yx", self.negate)
        self.ik0_ctl = self.addCtl(self.root, "ik0_ctl", t, self.color_ik, "compas", w=self.size)
        par.setKeyableParameters(self.ik0_ctl)
        xsi.SetNeutralPose(self.ik0_ctl)
        par.addLocalParamToCollection(self.inv_params, self.ik0_ctl, ["posx", "roty", "rotz"])
        par.setRotOrder(self.ik0_ctl, "XZY")

        t.SetTranslation(self.guide.apos[1])
        self.ik1_ctl = self.addCtl(self.root, "ik1_ctl", t, self.color_ik, "compas", w=self.size)
        par.setKeyableParameters(self.ik1_ctl)
        xsi.SetNeutralPose(self.ik1_ctl)
        par.addLocalParamToCollection(self.inv_params, self.ik1_ctl, ["posx", "roty", "rotz"])
        par.setRotOrder(self.ik1_ctl, "XZY")

        # Tangent controlers -------------------------------
        t.SetTranslation(vec.linearlyInterpolate(self.guide.apos[0], self.guide.apos[1], .33))
        self.tan0_ctl = self.addCtl(self.ik0_ctl, "tan0_ctl", t, self.color_ik, "sphere", w=self.size*.2)
        par.setKeyableParameters(self.tan0_ctl, self.t_params)
        xsi.SetNeutralPose(self.tan0_ctl, c.siTrn)
        par.addLocalParamToCollection(self.inv_params, self.ik1_ctl, ["posx"])

        t.SetTranslation(vec.linearlyInterpolate(self.guide.apos[0], self.guide.apos[1], .66))
        self.tan1_ctl = self.addCtl(self.ik1_ctl, "tan1_ctl", t, self.color_ik, "sphere", w=self.size*.2)
        par.setKeyableParameters(self.tan1_ctl, self.t_params)
        xsi.SetNeutralPose(self.tan1_ctl, c.siTrn)
        par.addLocalParamToCollection(self.inv_params, self.ik1_ctl, ["posx"])

        # Curves -------------------------------------------
        self.mst_crv = cur.addCnsCurve(self.root, self.getName("mst_crv"), [self.ik0_ctl, self.tan0_ctl, self.tan1_ctl, self.ik1_ctl], False, 3)
        self.slv_crv = cur.addCurve(self.root, self.getName("slv_crv"), [1]*10*4, False, 3)
        self.addToGroup([self.mst_crv, self.slv_crv], "hidden")

        # Division -----------------------------------------
        # The user only define how many intermediate division he wants.
        # First and last divisions are an obligation.
        parentdiv = self.ik0_ctl
        parentctl = self.ik0_ctl
        self.div_cns = []
        self.fk_ctl = []
        for i in range(self.settings["division"]):

            # References
            div_cns = parentdiv.AddNull(self.getName("%s_cns"%i))
            pri.setNullDisplay(div_cns, 1, self.size*.05, 10, 0, 0, 0, 1, 1, 2)
            self.addToGroup(div_cns, "hidden")

            self.div_cns.append(div_cns)
            parentdiv = div_cns

            # Controlers (First and last one are fake)
            if i in [0, self.settings["division"] - 1]:
                fk_ctl = pri.addNull(parentctl, self.getName("%s_loc"%i), parentctl.Kinematics.Global.Transform, self.size*.05)
                self.addToGroup(fk_ctl, "hidden")
            else:
                fk_ctl = self.addCtl(parentctl, "fk%s_ctl"%(i-1), parentctl.Kinematics.Global.Transform, self.color_fk, "cube", w=self.size*1, h=self.size*.05, d=self.size*1)
                self.addToGroup(fk_ctl, "controlers_01")
                par.addLocalParamToCollection(self.inv_params, fk_ctl, ["posx", "roty", "rotz"])
                par.setRotOrder(fk_ctl, "XZY")

            self.fk_ctl.append(fk_ctl)
            parentctl = fk_ctl

            # Deformers (Shadow)
            self.addShadow(fk_ctl, (i))

        # Connections (Hooks) ------------------------------
        self.cnx0 = pri.addNull(self.root, self.getName("0_cnx"), self.root.Kinematics.Global.Transform, self.size*.2)
        self.cnx1 = pri.addNull(self.root, self.getName("1_cnx"), self.root.Kinematics.Global.Transform, self.size*.2)
        self.addToGroup([self.cnx0, self.cnx1], "hidden")

    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):

        # Anim -------------------------------------------
        # Default parameter to get a better display in the keying panel
        self.pFullName = self.addAnimParam(self.fullName, c.siString, self.fullName, None, None, None, None, False, True, True)

        self.pShowIk = self.addAnimParam("showik", c.siBool, True, None, None, None, None, False, False, False)
        self.pShowFk = self.addAnimParam("showfk", c.siBool, True, None, None, None, None, False, False, False)

        self.pPosition = self.addAnimParam("position", c.siDouble, self.settings["position"], 0, 1, 0, 1)
        self.pMaxStretch = self.addAnimParam("maxstretch", c.siDouble, self.settings["maxstretch"], 1, None, 1, 3)
        self.pMaxSquash = self.addAnimParam("maxsquash", c.siDouble, self.settings["maxsquash"], 0, 1, 0, 1)
        self.pSoftness = self.addAnimParam("softness", c.siDouble, self.settings["softness"], 0, 1, 0, 1)

        self.pLockOri0 = self.addAnimParam("lock_ori0", c.siDouble, self.settings["lock_ori"], 0, 1, 0, 1)
        self.pLockOri1 = self.addAnimParam("lock_ori1", c.siDouble, self.settings["lock_ori"], 0, 1, 0, 1)

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
        fcurveItems = ["Stretch", 0, "Squash", 1]
        
        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        # Visibilities
        group = tab.addGroup("Visibilities")
        group.addItem(self.pShowIk.ScriptName, "Show IK controlers")
        group.addItem(self.pShowFk.ScriptName, "Show FK controlers")

        # Spine behavior
        group = tab.addGroup("Squash and Stretch")
        group.addItem(self.pPosition.ScriptName, "Base / Top")
        group.addItem(self.pMaxStretch.ScriptName, "Max Stretch")
        group.addItem(self.pMaxSquash.ScriptName, "Max Squash")
        group.addItem(self.pSoftness.ScriptName, "Softness")

        group = tab.addGroup("Orientation Lock")
        group.addItem(self.pLockOri1.ScriptName, "Top")
        group.addItem(self.pLockOri0.ScriptName, "Base")

        group = tab.addGroup("Tangent")
        group.addItem(self.pTan1.ScriptName, "Top")
        group.addItem(self.pTan0.ScriptName, "Base")

        # Volume
        group = tab.addGroup("Volume")
        group.addItem(self.pVolume.ScriptName, "Volume")

        # Setup ------------------------------------------
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
            stretch_group.addItem(self.pEdit.ScriptName, "Edit Values")
            stretch_group.addCondition("PPG."+self.pFCurveCombo.ScriptName+".Value == 0")
            squash_group = tab.addGroup("Values")
            squash_group.addItem(self.pEdit.ScriptName, "Edit Values")
            squash_group.addCondition("PPG."+self.pFCurveCombo.ScriptName+".Value == 1")

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
        par.addExpression(self.ik0_ctl.Properties("visibility").Parameters("viewvis"), self.pShowIk.FullName)
        par.addExpression(self.ik1_ctl.Properties("visibility").Parameters("viewvis"), self.pShowIk.FullName)
        par.addExpression(self.tan0_ctl.Properties("visibility").Parameters("viewvis"), self.pShowIk.FullName)
        par.addExpression(self.tan1_ctl.Properties("visibility").Parameters("viewvis"), self.pShowIk.FullName)
        for fk_ctl in self.fk_ctl[1:-1]:
            par.addExpression(fk_ctl.Properties("visibility").Parameters("viewvis"), self.pShowFk.FullName)

        # Tangent position ---------------------------------
        d = vec.getDistance(self.guide.apos[0], self.guide.apos[1])

        exp = self.pTan0.FullName + " * " + str(self.tan0_ctl.Parameters("nposy").Value)+" * (ctr_dist("+self.ik0_ctl.FullName+","+self.ik1_ctl.FullName+") / "+str(d)+")"
        par.addExpression(self.tan0_ctl.Parameters("nposy"), exp)

        exp = self.pTan1.FullName + " * " + str(self.tan1_ctl.Parameters("nposy").Value)+" * (ctr_dist("+self.ik0_ctl.FullName+","+self.ik1_ctl.FullName+") / "+str(d)+")"
        par.addExpression(self.tan1_ctl.Parameters("nposy"), exp)

        # Curves -------------------------------------------
        op = aop.sn_curveslide2_op(self.slv_crv, self.mst_crv, 0, 1.5, .5, .5)

        par.addExpression(op.Parameters("position"), self.pPosition.FullName)
        par.addExpression(op.Parameters("maxstretch"), self.pMaxStretch.FullName)
        par.addExpression(op.Parameters("maxsquash"), self.pMaxSquash.FullName)
        par.addExpression(op.Parameters("softness"), self.pSoftness.FullName)

        # Division -----------------------------------------
        for i in range(self.settings["division"]):

            # References
            u = i / (self.settings["division"] - 1.0)
            div_cns = self.div_cns[i]

            cns = aop.pathCns(div_cns, self.slv_crv, 0, u*100, True, None, False)

            cns.Parameters("dirx").Value = 0
            cns.Parameters("diry").Value = 1
            cns.Parameters("dirz").Value = 0

            cns.Parameters("upx").Value = 0
            cns.Parameters("upy").Value = 0
            cns.Parameters("upz").Value = -1

            # Roll
            aop.spinePointAtOp(cns, self.ik0_ctl, self.ik1_ctl, u)

            # Squash n Stretch
            op = aop.sn_squashstretch2_op(div_cns, self.slv_crv, self.slv_crv.ActivePrimitive.Geometry.Curves(0).Length, "y")
            par.addExpression(op.Parameters("blend"), self.pVolume.FullName)
            par.addExpression(op.Parameters("driver"), self.pDriver.FullName)
            if self.options["mode"] == 1: # wip
                par.addExpression(op.Parameters("stretch"), self.pStretch[i])
                par.addExpression(op.Parameters("squash"), self.pSquash[i])
            else:
                op.Parameters("stretch").Value = self.st_value[i]
                op.Parameters("squash").Value = self.sq_value[i]

            # Controlers
            fk_ctl = self.fk_ctl[i]

            for s in "xyz":
                par.addExpression(fk_ctl.Parameters("npos"+s), div_cns.Parameters("pos"+s).FullName)
                par.addExpression(fk_ctl.Parameters("nrot"+s), div_cns.Parameters("rot"+s).FullName)
                par.addExpression(fk_ctl.Kinematics.Global.Parameters("scl"+s), div_cns.Kinematics.Global.Parameters("scl"+s).FullName)

        # Orientation Lock
        cns = self.div_cns[0].Kinematics.AddConstraint("Orientation", self.ik0_ctl, False)
        par.addExpression(cns.Parameters("blendweight"), self.pLockOri0.FullName)
        cns = self.div_cns[-1].Kinematics.AddConstraint("Orientation", self.ik1_ctl, False)
        par.addExpression(cns.Parameters("blendweight"), self.pLockOri1.FullName)

        # Volume -------------------------------------------
        op = aop.sn_curvelength_op(self.pDriver, self.slv_crv)

        # Connections (Hooks) ------------------------------
        self.cnx0.Kinematics.AddConstraint("Position", self.div_cns[0], False)
        self.cnx0.Kinematics.AddConstraint("Orientation", self.div_cns[0], False)
        self.cnx1.Kinematics.AddConstraint("Position", self.fk_ctl[-1], False)
        self.cnx1.Kinematics.AddConstraint("Orientation", self.fk_ctl[-1], False)

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Set the relation beetween object from guide to rig.\n
    # @param self
    def setRelation(self):
        self.relatives["root"] = self.cnx0
        self.relatives["eff"] = self.cnx1
