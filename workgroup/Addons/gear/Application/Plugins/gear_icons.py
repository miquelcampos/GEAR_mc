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

## @package gear_icons.py
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
import gear
import gear.xsi.icon as icon
from gear.xsi import xsi, c, lm
import gear.xsi.transform as tra

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_icons"
    in_reg.Email = "geerem@hotmail.com, hello@miqueltd.com"
    in_reg.URL = "http://www.jeremiepasserin.com, http://www.miqueltd.com "
    in_reg.Major = 1
    in_reg.Minor = 0

    in_reg.RegisterCommand("gear_createIcon","gear_createIcon")

    in_reg.RegisterCommand("gear_DrawCube","gear_DrawCube")
    in_reg.RegisterCommand("gear_DrawPyramid","gear_DrawPyramid")
    in_reg.RegisterCommand("gear_DrawSquare","gear_DrawSquare")
    in_reg.RegisterCommand("gear_DrawFlower","gear_DrawFlower")
    in_reg.RegisterCommand("gear_DrawCircle","gear_DrawCircle")
    in_reg.RegisterCommand("gear_DrawCylinder","gear_DrawCylinder")
    in_reg.RegisterCommand("gear_DrawCompas","gear_DrawCompas")
    in_reg.RegisterCommand("gear_DrawFoil","gear_DrawFoil")
    in_reg.RegisterCommand("gear_DrawDiamond","gear_DrawDiamond")
    in_reg.RegisterCommand("gear_DrawLeash","gear_DrawLeash")
    in_reg.RegisterCommand("gear_DrawCubeWithPeak","gear_DrawCubeWithPeak")
    in_reg.RegisterCommand("gear_DrawSphere","gear_DrawSphere")
    in_reg.RegisterCommand("gear_DrawArrow","gear_DrawArrow")
    in_reg.RegisterCommand("gear_DrawCrossArrow","gear_DrawCrossArrow")
    in_reg.RegisterCommand("gear_DrawBendedArrow","gear_DrawBendedArrow")
    in_reg.RegisterCommand("gear_DrawBendedArrow2","gear_DrawBendedArrow2")
    in_reg.RegisterCommand("gear_DrawCross","gear_DrawCross")
    in_reg.RegisterCommand("gear_DrawGlasses","gear_DrawGlasses")
    in_reg.RegisterCommand("gear_DrawLookAt","gear_DrawLookAt")
    in_reg.RegisterCommand("gear_DrawEyeArrow","gear_DrawEyeArrow")
    in_reg.RegisterCommand("gear_DrawAngleSurvey","gear_DrawAngleSurvey")
    in_reg.RegisterCommand("gear_DrawEyeBall","gear_DrawEyeBall")
    in_reg.RegisterCommand("gear_DrawRectangleCube","gear_DrawRectangleCube")
    in_reg.RegisterCommand("gear_DrawMan","gear_DrawMan")
    in_reg.RegisterCommand("gear_DrawNull","gear_DrawNull")
    in_reg.RegisterCommand("gear_DrawBoomerang","gear_DrawBoomerang")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# FUNCTION
##########################################################

def gear_createIcon_Init(in_ctxt):
    oCmd = in_ctxt.Source
    oCmd.Description = ""
    oCmd.ReturnValue = True

    oArgs = oCmd.Arguments
    oArgs.Add("icon",c.siArgumentInput)
    return True

def gear_createIcon_Execute(iconPreset):
    reload(gear.xsi.icon)
    funcDic = {"cube":icon.cube,
                "pyramid":icon.pyramid,
                "square":icon.square,
                "flower":icon.flower,
                "circle":icon.circle,
                "cylinder":icon.cylinder,
                "compas":icon.compas,
                "foil":icon.foil,
                "diamond":icon.diamond,
                "leash":icon.leash,
                "cubewithpeak":icon.cubewithpeak,
                "sphere":icon.sphere,
                "arrow":icon.arrow,
                "crossarrow":icon.crossarrow,
                "bendedarrow":icon.bendedarrow,
                "bendedarrow2":icon.bendedarrow2,
                "cross":icon.cross,
                "glasses":icon.glasses,
                "lookat":icon.lookat,
                "eyearrow":icon.eyearrow,
                "anglesurvey":icon.anglesurvey,
                "eyeball":icon.eyeball,
                "rectanglecube":icon.rectanglecube,
                "man":icon.man,
                "null":icon.null,
                "boomerang":icon.boomerang}


    if xsi.Selection.Count:
        XSIDial  = XSIFactory.CreateObject(  "XSIDial.XSIDialog")

        items = ["Only in Place", "Make it Parent", "Make it Child"]
        out = XSIDial.Combo("Creating Controls on Selected Objects", items)
        if out == -1:
            lm("Controls creation cancelled")
            return
        for obj in xsi.Selection:
            crv = funcDic[iconPreset]()
            source_object = obj

            tra.matchGlobalTransform( crv, source_object)
            if out == 1:
                oParent = obj.Parent
                #check if 2 objects have the same parent.
                if oParent.Name != crv.Parent.Name:
                    xsi.ParentObj(oParent, crv)
                xsi.ParentObj(crv, obj)
            elif out == 2:
                xsi.ParentObj(obj, crv)
            crv.Name = obj.Name + "_" + iconPreset
    else:
        crv = funcDic[iconPreset]()
        xsi.SelectObj(crv)
    return crv

##########################################################
# EXECUTE
##########################################################

def gear_DrawCube_Execute(): xsi.gear_createIcon("cube")
def gear_DrawPyramid_Execute(): xsi.gear_createIcon("pyramid")
def gear_DrawSquare_Execute(): xsi.gear_createIcon("square")
def gear_DrawFlower_Execute(): xsi.gear_createIcon("flower")
def gear_DrawCircle_Execute(): xsi.gear_createIcon("circle")
def gear_DrawCylinder_Execute(): xsi.gear_createIcon("cylinder")
def gear_DrawCompas_Execute(): xsi.gear_createIcon("compas")
def gear_DrawFoil_Execute(): xsi.gear_createIcon("foil")
def gear_DrawDiamond_Execute(): xsi.gear_createIcon("diamond")
def gear_DrawLeash_Execute(): xsi.gear_createIcon("leash")
def gear_DrawCubeWithPeak_Execute(): xsi.gear_createIcon("cubewithpeak")
def gear_DrawSphere_Execute(): xsi.gear_createIcon("sphere")
def gear_DrawArrow_Execute(): xsi.gear_createIcon("arrow")
def gear_DrawCrossArrow_Execute(): xsi.gear_createIcon("crossarrow")
def gear_DrawBendedArrow_Execute(): xsi.gear_createIcon("bendedarrow")
def gear_DrawBendedArrow2_Execute(): xsi.gear_createIcon("bendedarrow2")
def gear_DrawCross_Execute(): xsi.gear_createIcon("cross")
def gear_DrawGlasses_Execute(): xsi.gear_createIcon("glasses")
def gear_DrawLookAt_Execute(): xsi.gear_createIcon("lookat")
def gear_DrawEyeArrow_Execute(): xsi.gear_createIcon("eyearrow")
def gear_DrawAngleSurvey_Execute(): xsi.gear_createIcon("anglesurvey")
def gear_DrawEyeBall_Execute(): xsi.gear_createIcon("eyeball")
def gear_DrawRectangleCube_Execute(): xsi.gear_createIcon("rectanglecube")
def gear_DrawMan_Execute(): xsi.gear_createIcon("man")
def gear_DrawNull_Execute(): xsi.gear_createIcon("null")
def gear_DrawBoomerang_Execute(): xsi.gear_createIcon("boomerang")
