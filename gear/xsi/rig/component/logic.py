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

## @package gear.xsi.rig.component.logic
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, XSIMath

import gear.xsi.uitoolkit as uit
import gear.xsi.fcurve as fcu
import gear.xsi.animation as ani
import gear.xsi.transform as tra

##########################################################
# GUIDE LOGIC
##########################################################
# ========================================================
## Run a pick session to pick the reference for the ik or upv controler
def pickReferences(prop, list_name, item_name, onlyOne=False):

    # Get reference using pick session
    references = []
    while True:
        ref = uit.pickSession(c.siGenericObjectFilter, "Pick References", False)
        if not ref:
            break
        references.append(ref)

        if onlyOne:
            break

    # Get current reference array
    if not prop.Parameters(list_name).Value:
        a = []
    else:
        a = prop.Parameters(list_name).Value.split(",")

    # Check picked references
    for ref in references:
        if not ref.Model.IsEqualTo(prop.Model):
            gear.log("Reference doesnt belong to the guide model",gear.sev_warning)
            continue

        elif ref.Name in a:
            gear.log("Reference already in the list",gear.sev_warning)
            continue
        a.append(ref.Name)

    if not a:
        return

    # build combobox items array
    items = []
    for i, name in enumerate(a):
        items.append(name)
        items.append(i)

    layout = prop.PPGLayout
    item = layout.Item(item_name)
    item.UIItems = items

    prop.Parameters(list_name).Value = ",".join(a)
    prop.Parameters(item_name).Value = items[-1]

# ========================================================
## Remove one of the reference from the list
def deleteReference(prop, list_name, item_name):

    if not prop.Parameters(list_name).Value:
        return

    a = prop.Parameters(list_name).Value.split(",")

    if uit.msgBox("Are you sure you want to delete this reference" , c.siMsgExclamation|c.siMsgYesNo, "Confirm") == c.siMsgNo:
        return

    a.pop(prop.Parameters(item_name).Value)

    # build combobox items array
    items = []
    for i, name in enumerate(a):
        items.append(name)
        items.append(i)

    layout = prop.PPGLayout
    item = layout.Item(item_name)
    item.UIItems = items

    if items:
        prop.Parameters(list_name).Value = ",".join(a)
        prop.Parameters(item_name).Value = items[-1]
    else:
        prop.Parameters(list_name).Value = ""
        prop.Parameters(item_name).Value = 0

# ========================================================
## Eval the FCurve and set the parameters values
def setParamsValueFromFCurve(prop, fcv_name, divisions, param_name, minimum=None, maximum=None):
    values = fcu.getFCurveValues(prop.Parameters(fcv_name).Value, divisions)
    for i in range(divisions):
        value = values[i]*.01
        if minimum is not None:
            value = max(minimum, value)
        if maximum is not None:
            value = min(maximum, value)
        prop.Parameters(param_name%i).Value = value

##########################################################
# COMPONENT LOGIC
##########################################################
# ========================================================
##
def plotSpringToControler(comp_name, prop):

    # Get objects
    model = prop.Model
    refs = []
    ctls = []
    i = 0
    while True:
        ctl = model.FindChild(comp_name+"_fk%s_ctl"%i)
        ref = model.FindChild(comp_name+"_%s_ref"%i)

        if not ctl or not ref:
            break
            
        ctls.append(ctl)
        refs.append(ref)

        i += 1

    # UI
    pc = ani.PlayControl()
    ui_prop = xsi.ActiveSceneRoot.AddProperty("CustomProperty", False, "Plot")
    pStartFrame = ui_prop.AddParameter3("start_frame", c.siInt4, pc.localIn.Value, None, None)
    pEndFrame = ui_prop.AddParameter3("end_frame", c.siInt4, pc.localOut.Value, None, None)

    rtn = xsi.InspectObj(ui_prop, "", "Plot", c.siModal, False)

    start_frame = pStartFrame.Value
    end_frame = pEndFrame.Value

    xsi.DeleteObj(ui_prop)

    if rtn:
        return

    # Plot
    params = [ref.Kinematics.Local.Parameters("rot"+s).FullName for ref in refs for s in "xyz"]
    action = xsi.PlotAndApplyActions(",".join(params), "plot", start_frame, end_frame, 1, 20, 3, False, .01, True, False, False, False )(0)

    # Edit the stored Action
    for item in action.SourceItems:

        item.Target = item.Target.replace(comp_name+"_", comp_name+"_fk")
        item.Target = item.Target.replace("_ref", "_ctl")


    prop.Parameters(comp_name+"_main_blend").Value = 0
    xsi.ApplyAction(action)
    xsi.DeleteObj(action)

# ========================================================
def switchRef(prop, ctl_name, param_name, item_count):

    model = prop.Model
    ctl = model.FindChild(ctl_name)
    if not ctl:
        gear.log("Can't Find : "+ ctl_name, gear.sev_error)
        return
    prop.Parameters(param_name).Value = (prop.Parameters(param_name).Value + 1) % item_count
    t = ctl.Kinematics.Global.GetTransform2(None)
    ctl.Kinematics.Global.PutTransform2(None, t)
###############################################################################################################
# IK FK SWITCH
###############################################################################################################
# Class
class IKFKSwitcher(object):

    def __init__(self, model, uihost, name, isleg=False, negate=False):

        self.model = model
        self.anim_prop = uihost.Properties("anim_prop")
        self.setup_prop = uihost.Properties("setup_prop")
        self.name = name

        self.fk0 = self.model.FindChild(self.name + "_fk0_ctl")
        self.fk1 = self.model.FindChild(self.name + "_fk1_ctl")
        self.fk2 = self.model.FindChild(self.name + "_fk2_ctl")
        self.ik = self.model.FindChild(self.name + "_ik_ctl")
        self.upv = self.model.FindChild(self.name + "_upv_ctl")
        self.jnt0 = self.model.FindChild(self.name + "_0_jnt")
        self.jnt1 = self.model.FindChild(self.name + "_1_jnt")
        self.chn = self.model.FindChild(self.name + "_root")
        #self.eff = self.jnt0.Effector

        self.blend = self.anim_prop.Parameters(self.name + "_blend")
        self.roll = self.anim_prop.Parameters(self.name + "_roll")
        self.scale = self.anim_prop.Parameters(self.name + "_scale")
        self.maxstretch = self.anim_prop.Parameters(self.name + "_maxstretch")
        self.softik = self.anim_prop.Parameters(self.name + "_softness")

        self.op = self.jnt0.Kinematics.Global.NestedObjects("sn_ikfk2bone_op")
        self.rest = self.op.Parameters("lengthA").Value + self.op.Parameters("lengthB").Value

        self.length0 = self.jnt0.Kinematics.Global.Parameters("sclx").Value
        self.length1 = self.jnt1.Kinematics.Global.Parameters("sclx").Value

        self.isleg = isleg
        self.negate = negate
        

        # Miquel Temp Fix for globla scaling math FK - IK
        self.globalCtl = self.model.FindChild("global_C0_ctl")
        self.globalCtlProp = self.globalCtl.Properties("anim_prop")
        self.rigScale = self.globalCtlProp.Parameters("rigScale").Value

    def switch(self):

        if self.blend.Value == 0:
            self.switchToIk()
        elif self.blend.Value == 1:
            self.switchToFk()
        else:
            uitoolkit.msgBox("The Blend IK need to be set to '0' or '1'", c.siMsgExclamation, "Switch IK/FK Failed")

    # Switch To Ik --------------------------------------------
    def switchToIk(self):

        # Get the distance between Root and effector and compare it to bones total length to define if the chain is bend or not
        vRootEff = XSIMath.CreateVector3()
        vRootEff.Sub(self.jnt0.kinematics.Global.Transform.Translation, self.ik.kinematics.Global.Transform.Translation)

        # We get an approximation of the length otherwise it's sometimes tricky to compare distance
        r = 100000
        dRootEffLength = round((vRootEff.Length()*r)) / r
        dBonesLength = round(((self.length0 + self.length1)*r)) / r

        # xsi.MatchTransform(self.ik, self.eff, c.siRT, None)
        # tra.matchGlobalTransform(self.eff, self.ik, True, True, False)
        tra.matchGlobalTransform(self.ik, self.fk2, True, True, True)
        self.blend.Value = 1
        # tra.matchGlobalTransform(self.fk2, self.ik, False, True, False)

        # Compute Roll
        if dRootEffLength < dBonesLength:
            # Get Vectors to built the plane
            vFKChain0 = XSIMath.CreateVector3()
            vIKChain0 = XSIMath.CreateVector3()
            vRootEff = XSIMath.CreateVector3()

            vFKChain0.Sub(self.fk0.kinematics.Global.Transform.Translation, self.fk1.kinematics.Global.Transform.Translation)
            vIKChain0.Sub(self.jnt0.kinematics.Global.Transform.Translation , self.jnt1.kinematics.Global.Transform.Translation)
            vRootEff.Sub(self.jnt0.kinematics.Global.Transform.Translation, self.ik.kinematics.Global.Transform.Translation)

            # vFKChain0.NormalizeInPlace()
            # vIKChain0.NormalizeInPlace()
            # vRootEff.NormalizeInPlace()

            # Get Plane's Normal
            vNormFKPlane = XSIMath.CreateVector3()
            vNormIKPlane = XSIMath.CreateVector3()

            vNormFKPlane.Cross(vFKChain0, vRootEff)
            vNormIKPlane.Cross(vIKChain0, vRootEff)

            # vNormFKPlane.NormalizeInPlace() 
            # vNormIKPlane.NormalizeInPlace()

            # Get the Angle between the two planess
            dAngle = XSIMath.RadiansToDegrees(vNormFKPlane.Angle(vNormIKPlane))

            # Check if we have to remove or add the angle
            vCrossPlane = XSIMath.CreateVector3()
            vCrossPlane.Cross(vNormFKPlane, vNormIKPlane)
            # vCrossPlane.NormalizeInPlace()

            dDirectionDot = vCrossPlane.Dot(vRootEff)

            # Set the new roll Value
            a = self.roll.Value + (dDirectionDot/abs(dDirectionDot)) * dAngle

            # Set the angle in a -180 / 180 range
            if abs(a) > 180:
                a = a%((-a /abs(a))*360)

            # [OLD WAY ]Set the new roll Value --

            # Check if the bone is negated or not
            ## dNegate = self.jnt1.kinematics.Local.posx.Value + self.jnt1.kinematics.Local.nposx.Value
            #dNegate = 1
            # oldAngle = self.roll.Value

            # if (dDirectionDot * dNegate) <  0:
                # newAngle = oldAngle - dAngle
            # else:
                # newAngle = oldAngle + dAngle

            # if newAngle > 180:
                # newAngle -= 360
            # elif newAngle < -180:
                # newAngle += 360
            # [END OLD WAY ] -------------------

            self.roll.Value = a

        # Match Scale Value
        # We remove Soft distances
        self.softik.Value = 0

        if dRootEffLength > dBonesLength:
            if self.scale.Value > self.maxstretch.Value:
                self.maxstretch.Value = self.scale.Value
                self.scale.Value = 1

        if self.isleg:
            z = XSIMath.CreateVector3(1,0,0)
            y = XSIMath.CreateVector3(0,1,0)

            if self.negate:
                z.NegateInPlace()
                y.NegateInPlace()

            z.MulByRotationInPlace(self.fk2.Kinematics.Global.Transform.Rotation)
            y.MulByRotationInPlace(self.fk2.Kinematics.Global.Transform.Rotation)

            t = self.fk2.Kinematics.Global.Transform
            t.SetRotation(tra.getRotationFromAxis(z, y, "zy"))

            self.ik.Kinematics.Global.Transform = t
        else:
            tra.matchGlobalTransform(self.ik, self.fk2, False, True, True)

            
    # Switch To Fk --------------------------------------------
    def switchToFk(self):

        # Match Rotation
        tra.matchGlobalTransform(self.fk0, self.jnt0, False, True, True)
        tra.matchGlobalTransform(self.fk1, self.jnt1, False, True, True)

        # Scale
        #print self.globalCtl
        #print str(self.rigScale)
        self.scale.Value = ((self.length0 + self.length1) /  self.rest) / self.rigScale

        # Switch to FK
        self.blend.Value = 0


        if self.isleg:
            x = XSIMath.CreateVector3(0,0,1)
            y = XSIMath.CreateVector3(0,1,0)

            if self.negate:
                x.NegateInPlace()
                y.NegateInPlace()

            x.MulByRotationInPlace(self.ik.Kinematics.Global.Transform.Rotation)
            y.MulByRotationInPlace(self.ik.Kinematics.Global.Transform.Rotation)

            t = self.ik.Kinematics.Global.Transform
            t.SetRotation(tra.getRotationFromAxis(x, y, "xy"))

            self.fk2.Kinematics.Global.Transform = t
        else:
            tra.matchGlobalTransform(self.fk2, self.ik, False, True, True)
