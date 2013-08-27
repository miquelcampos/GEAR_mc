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

## @package gear_curveTools.py
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, dynDispatch

import gear.xsi.primitive as pri
import gear.xsi.curve as cur
import gear.xsi.fcurve as fcv
import gear.xsi.applyop as aop

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_curveTools"
    in_reg.Email = "geerem@hotmail.com, hello@miqueltd.com"
    in_reg.URL = "http://www.jeremiepasserin.com, http://www.miqueltd.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_CurveResampler","gear_CurveResampler")
    in_reg.RegisterCommand("gear_ApplyZipperOp","gear_ApplyZipperOp")


    in_reg.RegisterCommand("gear_DrawCnsCurve_Linear","gear_DrawCnsCurve_Linear")
    in_reg.RegisterCommand("gear_DrawCnsCurve_Cubic","gear_DrawCnsCurve_Cubic")

    in_reg.RegisterCommand("gear_MergeCurves","gear_MergeCurves")
    in_reg.RegisterCommand("gear_SplitCurves","gear_SplitCurves")

    in_reg.RegisterCommand("gear_crvLenInfo","gear_crvLenInfo")

    # Operators
    in_reg.RegisterOperator("gear_CurveResamplerOp")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):
    strPluginName = in_reg.Name
    gear.log(str(strPluginName) + str(" has been unloaded."), c.siVerbose)
    return True

##########################################################
# CURVE RESAMPLER
##########################################################
# Define =================================================
def gear_CurveResamplerOp_Define(ctxt):

    op = ctxt.Source
    op.AlwaysEvaluate = False
    op.Debug = 0

    pdef = XSIFactory.CreateParamDef("Start", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",0,0,100,0,100)
    op.AddParameter(pdef)
    pdef = XSIFactory.CreateParamDef("End", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",100,0,100,0,100)
    op.AddParameter(pdef)

    return True

# Update =================================================
def gear_CurveResamplerOp_Update(ctxt):

    # Inputs
    curve_geo = ctxt.GetInputValue(0, 0, 0).Geometry
    nurbscrv = curve_geo.Curves(0)

    start = ctxt.GetParameterValue("Start")
    end = ctxt.GetParameterValue("End")

    point_count = curve_geo.Points.Count

    # Process
    positions = []

    for i in range(point_count):

        step = (end - start) / (point_count-1.0)
        perc = start + (i*step)

        pos = nurbscrv.EvaluatePositionFromPercentage(perc)[0]
        positions.append(pos.X)
        positions.append(pos.Y)
        positions.append(pos.Z)

    # Output
    Out = ctxt.OutputTarget
    Out.Geometry.Points.PositionArray = positions

# Execute ================================================
def gear_CurveResampler_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for curve in xsi.Selection:

        if curve.Type not in ["crvlist"]:
            gear.log("Invalid selection", gear.sev_warning)
            continue

        if curve.ActivePrimitive.Geometry.Curves.Count > 1:
            gear.log("Curve Resampler works only with single curve", gear.sev_warning)
            continue

        # Apply Operator
        op = cur.applyCurveResamplerOp(curve)

    xsi.InspectObj(op)

##########################################################
# DRAW CONSTRAINED CURVE LINEAR
##########################################################
# Execute ================================================
def gear_DrawCnsCurve_Linear_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select enough centers", gear.sev_error)
        return

    cur.addCnsCurve(xsi.ActiveSceneRoot, "crvCns", xsi.Selection, False, 1)

##########################################################
# DRAW CONSTRAINED CURVE CUBIC
##########################################################
# Execute ================================================
def gear_DrawCnsCurve_Cubic_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select enough centers", gear.sev_error)
        return

    cur.addCnsCurve(xsi.ActiveSceneRoot, "crvCns", xsi.Selection, False, 3)

##########################################################
# MERGE CURVES
##########################################################
# Execute ================================================
def gear_MergeCurves_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    curves = [curve for curve in xsi.Selection if curve.Type in ["crvlist"]]
    if not curves:
        gear.log("Invalid selection", gear.sev_error)
        return

    cur.mergeCurves(curves)

##########################################################
# SPLIT CURVES
##########################################################
# Execute ================================================
def gear_SplitCurves_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for curve in xsi.Selection:

        if curve.Type not in ["crvlist"]:
            gear.log("Invalid selection", gear.sev_warning)
            continue

        cur.splitCurve(curve)

################################################################################################################
# CATMULL-ROM OP
################################################################################################################
# OPERATOR =====================================================================================================
# Define ======================================================================================================
def gCubicHermiteSplineOp_Define(ctxt):

    oCustomOperator = ctxt.Source
    oCustomOperator.AlwaysEvaluate = False
    oCustomOperator.Debug = 0

    oPDef = XSIFactory.CreateParamDef("Segment", c.siInt4, 0, c.siPersistable|c.siAnimatable, "", "",4,1,None,1,20)
    oCustomOperator.AddParameter(oPDef)
    oPDef = XSIFactory.CreateParamDef("Degree", c.siInt4, 0, c.siPersistable|c.siAnimatable, "", "",1,1,3,1,3)
    oCustomOperator.AddParameter(oPDef)
    oPDef = XSIFactory.CreateParamDef("Tangents", c.siInt4, 0, c.siPersistable|c.siAnimatable, "", "",0,0,1,0,1)
    oCustomOperator.AddParameter(oPDef)
    oPDef = XSIFactory.CreateParamDef("Tension", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",0,None,None,-1,1)
    oCustomOperator.AddParameter(oPDef)
    oPDef = XSIFactory.CreateParamDef("Bias", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",0,None,None,-1,1)
    oCustomOperator.AddParameter(oPDef)
    oPDef = XSIFactory.CreateParamDef("Continuity", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",0,None,None,-1,1)
    oCustomOperator.AddParameter(oPDef)

    return True

# Layout =======================================================================================================
def gCubicHermiteSplineOp_OnInit():

    aDegreeItems = ["Linear", 1, "Cubic", 3]
    aTangentsItems = ["Catmull-Rom", 0, "Kochanek-Bartels", 1]

    oLayout = PPG.PPGLayout
    oLayout.Clear()

    oLayout.AddGroup("Options")
    oLayout.AddItem("Segment", "Segment")
    oLayout.AddEnumControl("Degree", aDegreeItems, "Degree", c.siControlCombo)
    oLayout.AddEnumControl("Tangents", aTangentsItems, "Tangents", c.siControlCombo)
    oLayout.EndGroup()

    oLayout.AddGroup("Options")
    oLayout.AddItem("Tension", "Tension")
    oLayout.AddItem("Bias", "Bias")
    oLayout.AddItem("Continuity", "Continuity")
    oLayout.EndGroup()

    PPG.Tension.Enable(PPG.Tangents.Value == 1)
    PPG.Bias.Enable(PPG.Tangents.Value == 1)
    PPG.Continuity.Enable(PPG.Tangents.Value == 1)

    PPG.Refresh()

    return True

def gCubicHermiteSplineOp_Tangents_OnChanged():
    gCubicHermiteSplineOp_OnInit()

# Update =======================================================================================================
def gCubicHermiteSplineOp_Update(ctxt):

    # Inputs -----------------------------------------------
    tCurve = ctxt.GetInputValue(0, 0, 0).Transform
    tStart = ctxt.GetInputValue(1, 0, 0).Transform
    tEnd   = ctxt.GetInputValue(2, 0, 0).Transform

    mCurve = tCurve.Matrix4
    vStart = tStart.Translation
    vEnd   = tEnd.Translation

    mCurve.InvertInPlace()
    vStart.MulByMatrix4InPlace(mCurve)
    vEnd.MulByMatrix4InPlace(mCurve)

    iSegment = ctxt.GetParameterValue("Segment")
    iDegree = ctxt.GetParameterValue("Degree")

    iTangents = ctxt.GetParameterValue("Tangents")

    dTension = ctxt.GetParameterValue("Tension")
    dBias = ctxt.GetParameterValue("Bias")
    dContinuity = ctxt.GetParameterValue("Continuity")

    # --------------------------------------------------------
    aV = [vStart]
    for i in range(ctxt.Source.GetNumInstancesInGroup(1)):
        vPos = ctxt.GetInputValue(0,1,i).Transform.Translation
        vPos.MulByMatrix4InPlace(mCurve)
        aV.append(vPos)

    aV.append(vEnd)

    # Process -----------------------------------------------
    aPos = []
    for i in range(len(aV)-3):

        v1 = aV[i+0]
        v2 = aV[i+1]
        v3 = aV[i+2]
        v4 = aV[i+3]

        for j in range(iSegment-1):

            t = j/(iSegment-1.0)

            if iTangents == 0:
                p = catmullRomSplines(t, v1, v2, v3, v4)
            else:
                p = kochanekBartelsSplines(t, v1, v2, v3, v4, dTension, dBias, dContinuity)

            aPos.append(p.X)
            aPos.append(p.Y)
            aPos.append(p.Z)
            aPos.append(1)

    aPos.append(aV[-2].X)
    aPos.append(aV[-2].Y)
    aPos.append(aV[-2].Z)
    aPos.append(1)

    # Output ------------------------------------------------

    Out = ctxt.OutputTarget
    Out.Geometry.Set(1, aPos, None, None, None, None, (iDegree,), (1,))

# Simple CatmullRom ================================================================
def catmullRomSplines(t, p0, p1, p2, p3):

    pX = catmullRomEq(t, p0.X, p1.X, p2.X, p3.X)
    pY = catmullRomEq(t, p0.Y, p1.Y, p2.Y, p3.Y)
    pZ = catmullRomEq(t, p0.Z, p1.Z, p2.Z, p3.Z)

    p = XSIMath.CreateVector3(pX, pY, pZ)

    return p

def catmullRomEq(t, p1, p2, p3, p4):

    q = 0.5 * ((-p1 + 3*p2 -3*p3 + p4)*t*t*t
           + (2*p1 -5*p2 + 4*p3 - p4)*t*t
           + (-p1+p3)*t
           + 2*p2)

    return q

# KochanekBartels ====================================================================
def kochanekBartelsSplines(t, p0, p1, p2, p3, dTension, dBias, dContinuity):

    m1 = starttgnt(p0, p1, p2, dTension, dBias, dContinuity)
    m2 = endtgnt(p1, p2, p3, dTension, dBias, dContinuity)

    h00 = (1+2*t)*(1-t)*(1-t)
    h10 = t*(1-t)*(1-t)
    h01 = t*t*(3-2*t)
    h11 = t*t*(t-1)

    pX = h00 * p1.X + h10 * m1.X + h01 * p2.X + h11 * m2.X
    pY = h00 * p1.Y + h10 * m1.Y + h01 * p2.Y + h11 * m2.Y
    pZ = h00 * p1.Z + h10 * m1.Z + h01 * p2.Z + h11 * m2.Z

    p = XSIMath.CreateVector3(pX, pY, pZ)

    return p

def starttgnt(pk0, pk1, pk2, dTension, dBias, dContinuity):
    x = startKochanek(pk0.X, pk1.X, pk2.X, dTension, dBias, dContinuity)
    y = startKochanek(pk0.Y, pk1.Y, pk2.Y, dTension, dBias, dContinuity)
    z = startKochanek(pk0.Z, pk1.Z, pk2.Z, dTension, dBias, dContinuity)

    v = XSIMath.CreateVector3(x, y, z)
    return v

def endtgnt(pk0, pk1, pk2, dTension, dBias, dContinuity):
    x = endKochanek(pk0.X, pk1.X, pk2.X, dTension, dBias, dContinuity)
    y = endKochanek(pk0.Y, pk1.Y, pk2.Y, dTension, dBias, dContinuity)
    z = endKochanek(pk0.Z, pk1.Z, pk2.Z, dTension, dBias, dContinuity)

    v = XSIMath.CreateVector3(x, y, z)
    return v

def startKochanek(k0, k1, k2, t, b, c):
    return ((1-t)*(1+b)*(1+c)*.5)*(k1-k0)+((1-t)*(1-b)*(1-c)*.5)*(k2-k1)

def endKochanek(k0, k1, k2, t, b, c):
    return ((1-t)*(1+b)*(1-c)*.5)*(k1-k0)+((1-t)*(1-b)*(1+c)*.5)*(k2-k1)


# EXECUTE ======================================================================================================
def drawCubicHermiteSpline(cInputs, bCreateTangentCtrl = True):

    # Create Curve and tangent controler ----------------------------
    oCurve = xsi.ActiveSceneRoot.AddNurbsCurve()
    oCurve.Name = "CatmullRom_crv"

    if bCreateTangentCtrl:
        oStartTangent = prm.addNull(oCurve, "StartTangent", cInputs(0).Kinematics.Global.Transform, 1)
        oEndTangent = prm.addNull(oCurve, "EndTangent", cInputs(cInputs.Count-1).Kinematics.Global.Transform, 1)
    else:
        oStartTangent = cInputs(0)
        oEndTangent = cInputs(cInputs.Count-1)

    # Apply Operator ------------------------------------------------
    oOp = XSIFactory.CreateObject("gCubicHermiteSplineOp")

    # Output
    oOp.AddOutputPort(oCurve.ActivePrimitive)
    oOp.AddInputPort(oCurve.Kinematics.Global)
    oOp.AddInputPort(oStartTangent.Kinematics.Global)
    oOp.AddInputPort(oEndTangent.Kinematics.Global)

    # PortGroup
    oInputGroup = oOp.AddPortGroup("InputGroup", 0, 1000)

    # PortGroup class ID
    oOp.AddInputPortByClassID(c.siKinematicsID, "InputKine", oInputGroup.Index)

    for oInput in cInputs:
        oOp.ConnectToGroup(oInputGroup.Index,oInput.Kinematics.Global)

    oOp.Connect()

    xsi.InspectObj(oOp)

    return oOp

# Init =========================================================================================================
def gDrawCubicHermiteSplineWithTangentCtrl_Init(in_ctxt):

    oCmd = in_ctxt.Source
    oCmd.Description = ""
    oCmd.ReturnValue = True

    oArgs = oCmd.Arguments
    oArgs.AddWithHandler("cInputs", c.siArgHandlerCollection)

    return

# Execute ======================================================================================================
def gDrawCubicHermiteSplineWithTangentCtrl_Execute(cInputs):
    drawCubicHermiteSpline(cInputs)

# Init =========================================================================================================
def gDrawCubicHermiteSpline_Init(in_ctxt):

    oCmd = in_ctxt.Source
    oCmd.Description = ""
    oCmd.ReturnValue = True

    oArgs = oCmd.Arguments
    oArgs.AddWithHandler("cInputs", c.siArgHandlerCollection)

    return

# Execute ======================================================================================================
def gDrawCubicHermiteSpline_Execute(cInputs):
    drawCubicHermiteSpline(cInputs, False)

##########################################################
# Curve Length info
##########################################################
# ========================================================
def gear_crvLenInfo_Execute():

    if not xsi.Selection.Count and xsi.Selection(0).Type == "crvlist":
        gear.log("No selection or first selected object not a crvlist",
        gear.sev_error)
        return

    crv = xsi.Selection(0)
    prop = xsi.gear_PSet_Apply(crv, "Length_Info", False, False )
    pLength = prop.AddParameter3( "Length", c.siDouble, 0, -1000000, 1000000 )
    pOriginalLength = prop.AddParameter3( "Original_Length", c.siDouble, 0, -1000000, 1000000, False, True )
    pLengthRatio = prop.AddParameter3( "Length Ratio", c.siDouble, 0, -1000000, 1000000 )

    layout = r"""layout.AddTab('Length_Info');\
        layout.AddGroup('Default Layout');\
        item = layout.AddItem('Length', 'Length', None);\
        item = layout.AddItem('Original_Length', 'Original_Length', None);\
        item = layout.AddItem('Length_Ratio', 'Length_Ratio', None);\
        layout.EndGroup()"""

    prop.Parameters("layout").Value = layout
    aop.sn_curvelength_op(pLength.FullName, crv)
    pOriginalLength.Value = pLength.Value
    pLengthRatio.AddExpression( pLength.FullName +  "/" + pOriginalLength.FullName)
    xsi.InspectObj(prop)

##########################################################
# APPLY ZIPPER
##########################################################
# ========================================================
def gear_ApplyZipperOp_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select 2 curve", gear.sev_error)
        return

    crv_A = xsi.Selection(0)
    crv_B = xsi.Selection(1)

    if crv_A.Type not in ["crvlist"] or crv_B.Type not in ["crvlist"]:
        gear.log("Select 2 curve", gear.sev_error)
        return
    else:
        op =  aop.gear_zipper_op( crv_A, crv_B)

    xsi.InspectObj(op)