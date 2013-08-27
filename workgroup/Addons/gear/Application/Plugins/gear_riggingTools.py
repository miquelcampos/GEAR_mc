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

## @package gear_riggingTools.py
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, XSIMath, Dispatch, dynDispatch, XSIFactory, lm

import gear.xsi.primitive as pri
import gear.xsi.applyop as aop
import gear.xsi.vector as vec
import gear.xsi.uitoolkit as uit
import gear.xsi.display as dis

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_riggingTools"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_GetDistance", "gear_GetDistance")
    in_reg.RegisterCommand("gear_DrawAxis", "gear_DrawAxis")
    in_reg.RegisterCommand("gear_AddNullParent", "gear_AddNullParent")
    in_reg.RegisterCommand("gear_AddNullChild", "gear_AddNullChild")
    in_reg.RegisterCommand("gear_CopyWireFrameColor", "gear_CopyWireFrameColor")

    in_reg.RegisterCommand("gear_CreateSplineKine", "gear_CreateSplineKine")
    in_reg.RegisterCommand("gear_CreateRollSplineKine", "gear_CreateRollSplineKine")
    in_reg.RegisterCommand("gear_CurveSlide2Op", "gear_CurveSlide2Op")
    in_reg.RegisterCommand("gear_InterLocalOri", "gear_InterLocalOri")
    in_reg.RegisterCommand("gear_Interpose", "gear_Interpose")
    in_reg.RegisterCommand("gear_XformSpring", "gear_XformSpring")

    in_reg.RegisterCommand("gear_ApplySpinePointAtOp", "gear_ApplySpinePointAtOp")

    in_reg.RegisterCommand("gear_InspectSolvers", "gear_InspectSolvers")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# GET DISTANCE
##########################################################
# ========================================================
## Log the distance between selected objects.
def gear_GetDistance_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    objects = [obj for obj in xsi.Selection if obj.IsClassOf(c.siX3DObjectID)]

    if len(objects) < 2:
        gear.log("Not enough object selected", gear.sev_error)
        return

    total = 0
    for i in range(len(objects)-1):
        a = objects[i]
        b = objects[i+1]

        distance = vec.getDistance2(a,b)
        gear.log("Distance : %s (%s to %s)"%(distance, a.Name, b.Name))

        total += distance

    gear.log("Total : %s"%total)

##########################################################
# DRAW AXIS
##########################################################
# ========================================================
## Draw the axis of selection.
def gear_DrawAxis_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for sel in xsi.Selection:
        pri.drawAxis(sel, 1)

##########################################################
# ADD NULL
##########################################################
# ========================================================
## Add a null parent of selection at the same position.
def gear_AddNullParent_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for sel in xsi.Selection:
        null = pri.addNull(sel.Parent3DObject, sel.Name+"_parent", sel.Kinematics.Global.Transform)
        null.AddChild(sel)

# ========================================================
## Add a null child of selection at the same position.
def gear_AddNullChild_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for sel in xsi.Selection:
        pri.addNull(sel, sel.Name+"_child", sel.Kinematics.Global.Transform)

##########################################################
# COPY WIREFRAME COLOR
##########################################################
# ========================================================
## .
def gear_CopyWireFrameColor_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    ref = uit.pickSession(c.siGenericObjectFilter, "Pick Reference", True)
    if not ref:
        return

    color = dis.getColor(ref)

    for sel in xsi.Selection:
        dis.setColor(sel, color)

##########################################################
# CREATE SPLINE KINE
##########################################################
# ========================================================
## Create null connected to selection using the gear_splinekine_op.
def gear_CreateSplineKine_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select at least two objects", gear.sev_error)
        return

    controlers = [obj for obj in xsi.Selection]

    # -----------------------------------------------------
    # UI
    prop = xsi.ActiveSceneRoot.AddProperty("CustomProperty", False, "SplineKineOptions")
    pDivision = prop.AddParameter3("division", c.siInt4, 10, 1, None, False, False)

    rtn = xsi.InspectObj(prop, "", "Spline Kine Options", c.siModal, False)

    div_count = pDivision.Value

    xsi.DeleteObj(prop)

    if rtn:
        return

    # -----------------------------------------------------
    # Create Parent property to connect the multiple operators parameters
    prop = controlers[0].Properties("gear_splinekine_options")
    if not prop:
        prop = controlers[0].AddProperty("CustomProperty", False, "gear_splinekine_options")
        prop.AddParameter3("resample", c.siBool, True, None, None, True, False)
        prop.AddParameter3("subdiv", c.siInt4, 10, 3, 50, True, False)
        prop.AddParameter3("absolute", c.siBool, False, None, None, True, False)

    # -----------------------------------------------------
    for i in range(div_count):

        div = controlers[0].AddNull("div_%s"%i)
        pri.setNullDisplay(div, 4, .5)
        op = aop.sn_splinekine_op(div, controlers, i/(div_count-1.0))

        for s in ["resample", "subdiv", "absolute"]:
            op.Parameters(s).AddExpression(prop.Parameters(s))

    xsi.InspectObj(prop)

##########################################################
# CREATE ROLL SPLINE KINE
##########################################################
# ========================================================
## Create null connected to selection using the gear_rollsplinekine_op.
def gear_CreateRollSplineKine_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select at least two objects", gear.sev_error)
        return

    controlers = [pri.addNull(obj, obj.Name+"_rot", obj.Kinematics.Global.Transform) for obj in xsi.Selection]
    for ctl in controlers:
        pri.setNullDisplay(ctl, 2)

    # -----------------------------------------------------
    # UI
    prop = xsi.ActiveSceneRoot.AddProperty("CustomProperty", False, "SplineKineOptions")
    pDivision = prop.AddParameter3("division", c.siInt4, 10, 1, None, False, False)

    rtn = xsi.InspectObj(prop, "", "Spline Kine Options", c.siModal, False)

    div_count = pDivision.Value

    xsi.DeleteObj(prop)

    if rtn:
        return

    # -----------------------------------------------------
    # Create Parent property to connect the multiple operators parameters
    prop = controlers[0].Properties("gear_splinekine_options")
    if not prop:
        prop = controlers[0].AddProperty("CustomProperty", False, "gear_splinekine_options")
        prop.AddParameter3("resample", c.siBool, True, None, None, True, False)
        prop.AddParameter3("subdiv", c.siInt4, 10, 3, 50, True, False)
        prop.AddParameter3("absolute", c.siBool, False, None, None, True, False)

    # -----------------------------------------------------
    for i in range(div_count):

        div = controlers[0].AddNull("div_%s"%i)
        pri.setNullDisplay(div, 4, .5)
        op = aop.sn_rollsplinekine_op(div, controlers, i/(div_count-1.0))

        for s in ["resample", "subdiv", "absolute"]:
            op.Parameters(s).AddExpression(prop.Parameters(s))

    xsi.InspectObj(prop)

##########################################################
# APPLY CURVE SLIDE 2 OP
##########################################################
# ========================================================
def gear_CurveSlide2Op_Execute():

    if not xsi.Selection.Count or xsi.Selection(0).Type not in ["crvlist"]:
        gear.log("No selection or invalid Selection", gear.sev_error)
        return

    out_crv = xsi.Selection(0)

    if out_crv.ActivePrimitive.Geometry.Curves.Count > 1:
        gear.log("Curve Resampler works only with single curve", gear.sev_error)
        return

    in_crv = uit.pickSession(c.siCurveFilter, "Pick Reference Curve", True)
    if not in_crv:
        return

    op = aop.sn_curveslide2_op(out_crv, in_crv)

    xsi.InspectObj(op)

##########################################################
# APPLY INTER LOCAL ORI OP
##########################################################
# ========================================================
def gear_InterLocalOri_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    out = xsi.Selection(0)

    ref_A = uit.pickSession(c.siGenericObjectFilter, "Pick Reference A", True)
    if not ref_A:
        return

    ref_B = uit.pickSession(c.siGenericObjectFilter, "Pick Reference B", True)
    if not ref_B:
        return

    op = aop.sn_interLocalOri_op(out, ref_A, ref_B, .5)

    xsi.InspectObj(op)

##########################################################
# APPLY SPINE POINT AT OP
##########################################################
# ========================================================
def gear_ApplySpinePointAtOp_Execute():

    start_obj = uit.pickSession(c.siGenericObjectFilter, "Pick Start Reference", True)
    if not start_obj:
        return

    end_obj = uit.pickSession(c.siGenericObjectFilter, "Pick End Reference", True)
    if not end_obj:
        return

    count = xsi.Selection.Count+0.0
    operators = []
    for i, sel in enumerate(Application.Selection):

        path_cns = False
        for cns in sel.Kinematics.Constraints:
            if cns.Type in ["crvcns", "pathcns", "dircns"]:
                path_cns = cns
                break

        if not path_cns:
            gear.log("There is no path ,curve or direction constraint on this object : %s"%sel.Name, gear.sev_warning)
            continue

        blend = i/count
        op = aop.spinePointAtOp(cns, start_obj, end_obj, blend)
        operators.append(op)

    xsi.InspectObj(operators)

##########################################################
# APPLY INTERPOSE
##########################################################
# ========================================================
def gear_Interpose_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    out = xsi.Selection(0)

    ref_A = uit.pickSession(c.siGenericObjectFilter, "Pick Reference A", True)
    if not ref_A:
        return

    ref_B = uit.pickSession(c.siGenericObjectFilter, "Pick Reference B", True)
    if not ref_B:
        return

    op = aop.sn_interpose_op(out, ref_A, ref_B)

    xsi.InspectObj(op)

##########################################################
# APPLY XFORM SPRING
##########################################################
# ========================================================
def gear_XformSpring_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    out = xsi.Selection(0)

    op = aop.sn_xfspring_op(out, mode=2)

    xsi.InspectObj(op)



##########################################################
# INSPECT SOLVERS
##########################################################
# ========================================================

def gear_InspectSolvers_Execute( ):

    if xsi.Selection.Count:
        try:
            xsi.InspectObj(".Kine.Global.sn_*")
        except:
            lm("Any of the selected objects have GEAR,s 'sn_solver' solvers", 2)