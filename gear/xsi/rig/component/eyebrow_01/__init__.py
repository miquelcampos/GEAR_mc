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
    Date:       2011 / 12 / 5

'''

## @package gear.xsi.rig.component.eyebrow_01
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import os

import gear.lists as lis

from gear.xsi import xsi, c, dynDispatch, XSIFactory, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.ppg as ppg
import gear.xsi.parameter as par
import gear.xsi.primitive as pri
import gear.xsi.applyop as aop
import gear.xsi.transform as tra
import gear.xsi.curve as cur
import gear.xsi.vector as vec
import gear.xsi.operator as ope

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

        self.inter_shd = 1
        self.shd_count = self.inter_shd * 2 + 3
        self.inter_crv = 1
        self.crv_count = self.inter_crv * 2 + 1

        self.npo = []
        self.ctl = []

        self.crv = []
        self.upv = []
        self.ctr = []
        self.off = []
        self.cns_crv = []
        self.loc = []

        self.percentages = []

        for i, name, blade in zip(range(3), ["root", "mid_loc", "end_loc"], ["blade", "mid_blade", "end_blade"]):

            # Path ----------------------------------------
            crv = self.guide.prim["%s_crv"%i].create(self.root, self.getName("%s_crv"%i), None)
            xsi.SetNeutralPose(crv)

            self.crv.append(crv)
            self.addToGroup(crv, "hidden")

            if i == 0:
                y0 = cur.getGlobalPointPosition(0, crv).Y
                y1 = cur.getGlobalPointPosition(crv.ActivePrimitive.Geometry.Points.Count-1, crv).Y

                self.scale = (y1 - y0) * .5

            # Controlers ----------------------------------
            lookat = XSIMath.CreateVector3()
            lookat.Add(self.guide.pos[name], self.guide.blades[blade].x)
            if blade == "end_blade":
                axisPlane = "zx"
                axisNegate =  True
            else:
                axisPlane = "zx"
                axisNegate = False
            t = tra.getTransformLookingAt(self.guide.pos[name], lookat, self.guide.blades[blade].y, axisPlane, axisNegate)
            t.SetScaling(XSIMath.CreateVector3(self.scale, self.scale, self.scale))

            npo = pri.addNull(self.root, self.getName("%s_npo"%i), t, 1)
            pri.setNullDisplay(npo, 0, 1, 4, 0, 0, 0, .15, 2, 0)
            self.addToGroup(npo, "unselectable")

            ctl = self.addCtl(npo, "%s_ctl"%i, t, self.color_ik, "sphere", w=.2)
            xsi.SetNeutralPose(ctl)
            par.setKeyableParameters(ctl, ["posx", "posy", "posz", "rotx", "roty", "rotz", "rotorder", "sclx"])
            # par.addLocalParamToCollection(self.inv_params, ctl, ["posx", "roty", "rotz"]) # to be defined
            # par.setRotOrder(ctl, "XZY") # to be defined

            self.ctl.append(ctl)


            # Up Vector, Center, Offset -------------------
            v = XSIMath.CreateVector3(self.guide.blades[blade].x.X, self.guide.blades[blade].x.Y, self.guide.blades[blade].x.Z)
            v.ScaleInPlace(-self.size)
            v.AddInPlace(self.guide.pos[name])
            upv = pri.addNullFromPos(crv, self.getName("%s_upv")%i, v, self.size*.025)
            ctr = [pri.addNullFromPos(crv, self.getName("%s_%s_ctr"%(i,j)), self.guide.apos[i], self.size*.025) for j in range(3)]
            off = pri.addNullFromPos(ctr[1], self.getName("%s_off")%i, self.guide.apos[i], self.size*.05)

            self.upv.append(upv)
            self.ctr.append(ctr)
            self.off.append(off)
            self.addToGroup(upv, "hidden")
            self.addToGroup(ctr, "hidden")
            self.addToGroup(off, "hidden")

            # Collecting Percentage to evaluate the curve
            v = XSIMath.MapWorldPositionToObjectSpace(crv.Kinematics.Global.Transform, self.guide.pos[name])
            a = crv.ActivePrimitive.Geometry.GetClosestCurvePosition2(v)
            perc = crv.ActivePrimitive.Geometry.Curves(0).GetPercentageFromU(a[2])
            self.percentages.append(perc)

        # Constrained Curve -------------------------------
        self.cns_crv = []
        self.loc = []
        for i in range(self.crv_count):
            positions = []
            for crv, perc in zip(self.crv, self.percentages):

                if i < self.inter_crv:
                    perc = (i+1.0)/(self.inter_crv+1.0) * perc
                elif i > self.inter_crv:
                    perc = perc + (i-self.inter_crv)/(self.inter_crv+1.0) * perc

                pos = crv.ActivePrimitive.Geometry.Curves(0).EvaluatePositionFromPercentage(perc)[0]
                pos = XSIMath.MapObjectPositionToWorldSpace(crv.Kinematics.Global.Transform, pos)
                positions.append(pos)

            positions.insert(1, vec.linearlyInterpolate(positions[0], positions[1], .1))
            positions.insert(-1, vec.linearlyInterpolate(positions[-2], positions[-1], .9))
            cns_crv = cur.addCurveFromPos(self.root, self.getName("cns%s_crv"%i), positions, False, 3)

            self.cns_crv.append(cns_crv)
            self.addToGroup(cns_crv, "hidden")

            # Shadows
            for j in range(self.shd_count):

                if i < self.inter_crv:
                    name = "%s_low%s"%(j,i)
                elif i == self.inter_crv:
                    name = str(j)
                elif i > self.inter_crv:
                    name = "%s_upp%s"%(j,i-self.inter_crv-1)

                loc = pri.addNullFromPos(cns_crv, self.getName(name+"_loc"), XSIMath.CreateVector3(), self.size*.05)
                self.addShadow(loc, name)

                self.loc.append(loc)
                self.addToGroup(loc, "hidden")

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

        # Controlers Limits -------------------------------
        # pos_0 = self.crv[0].ActivePrimitive.Geometry.Curves(0).EvaluatePosition(0)[0]
        # pos_1 = self.crv[0].ActivePrimitive.Geometry.Curves(0).EvaluatePosition(4)[0]
        # pos_0 = XSIMath.MapObjectPositionToWorldSpace(self.crv[0].Kinematics.Global.Transform, pos_0)
        # pos_1 = XSIMath.MapObjectPositionToWorldSpace(self.crv[0].Kinematics.Global.Transform, pos_1)

        # lim_min = pos_0.Y - self.ctl[0].Kinematics.Global.Transform.Translation.Y
        # lim_max = pos_1.Y - self.ctl[0].Kinematics.Global.Transform.Translation.Y

        for ctl, crv, upv, centers, off, perc in zip(self.ctl, self.crv, self.upv, self.ctr, self.off, self.percentages):

            # crv_geo = crv.ActivePrimitive.Geometry
            # crv_0 = crv_geo.Curves(0)
            # crv_tra = crv.Kinematics.Global.Transform

            # Set Limits ----------------------------------
            par.setLimit(ctl, ["posy"], -1, 1)
            # ctl.Kinematics.Local.Parameters("posyminactive").Value = True
            # ctl.Kinematics.Local.Parameters("posymaxactive").Value = True
            # ctl.Kinematics.Local.Parameters("posyminlimit").Value = lim_min
            # ctl.Kinematics.Local.Parameters("posymaxlimit").Value = lim_max

            # Path Constraint -----------------------------
            constraints = []
            for ctr in centers:
                cns = aop.pathCns(ctr, crv, 0, perc, True, upv, False)
                ope.setConstraintTangency(cns, [0,1,0], [0,0,-1])
                constraints.append(cns)

            pos_min = "max(0,-%s)*%s"%(ctl.Kinematics.Local.Parameters("posy").FullName,perc)
            pos_max = "max(0,%s)*%s"%(ctl.Kinematics.Local.Parameters("posy").FullName,100-perc)
            par.addExpression(constraints[1].Parameters("perc"), "%s - %s + %s"%(perc,pos_min,pos_max))

            cns_perc = constraints[1].Parameters("perc").FullName
            par.addExpression(constraints[0].Parameters("perc"), cns_perc + " * .5 ")
            par.addExpression(constraints[2].Parameters("perc"), cns_perc + " + (100 - "+cns_perc+" ) * .5 ")

            # Connect Offset to Controler
            for s in "xz":
                par.addExpression(off.Kinematics.Local.Parameters("pos%s"%s), ctl.Kinematics.Local.Parameters("pos%s"%s).FullName+" * "+str(self.scale))
            for s in "yz":
                par.addExpression(off.Kinematics.Local.Parameters("rot%s"%s), ctl.Kinematics.Local.Parameters("rot%s"%s).FullName)
            for s in "x":
                par.addExpression(off.Kinematics.Local.Parameters("scl%s"%s), ctl.Kinematics.Local.Parameters("scl%s"%s).FullName)

        # Constrained Curve -------------------------------
        for i in range(self.crv_count):

            if i == self.inter_crv:
                centers = self.off
            else:
                centers = [ctr[i] for ctr in self.ctr]

            for ctr, pnts in zip(centers, [[0,1],[2],[3,4]]):
                aop.clsCtrOp(self.cns_crv[i], ctr, pnts)

        # Shadows -----------------------------------------
        constraints = []
        for i in range(self.shd_count):

            u = i/4.0
            for j in range(self.crv_count):

                if j == self.inter_crv:
                    cns = aop.pathCns(self.loc[j*self.shd_count+i], self.cns_crv[j], 1, u, True, None, False)
                    constraints.append(cns)
                else:
                    cns = aop.pathCns(self.loc[j*self.shd_count+i], self.cns_crv[j], 1, u, True, self.upv[0], False)



        # Connect Roll
        aop.gear_pointAtObjectAxis(constraints[0], self.ctl[0], [0,0,1])
        aop.spinePointAtOp(constraints[1], self.ctl[0], self.ctl[1], .5)
        aop.gear_pointAtObjectAxis(constraints[2], self.ctl[1], [0,0,1])
        aop.spinePointAtOp(constraints[3], self.ctl[1], self.ctl[2], .5)
        aop.gear_pointAtObjectAxis(constraints[4], self.ctl[2], [0,0,1])



