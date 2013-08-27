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

## @package gear_wireframe.py
# @author Jeremie Passerin, Miquel Campos
# @version 1.0
#

##########################################################
# GLOBAL
##########################################################
# Built_in
import os
import random

# gear
from gear.xsi import xsi, c
import gear.xsi.plugin as plu
import gear.xsi.display as dis

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_wireframe"
    in_reg.Email = "geerem@hotmail.com, hello@miqueltd.com"
    in_reg.URL = "http://www.jeremiepasserin.com, http://www.miqueltd.com "
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_OpenWireframe","gear_OpenWireframe")
    in_reg.RegisterCommand("gear_setWireColorRange","gear_setWireColorRange")


    # Property
    in_reg.RegisterProperty("gear_Wireframe")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# OPEN WIREFRAME
##########################################################
def gear_OpenWireframe_Execute():

    if xsi.ActiveSceneRoot.Properties("gear_Wireframe"):
        prop = xsi.ActiveSceneRoot.Properties("gear_Wireframe")
        xsi.DeleteObj(prop)

    prop = xsi.ActiveSceneRoot.AddProperty("gear_Wireframe", False, "gear_Wireframe")

    dis.inspect(prop, 315, 345, 125, 75)


##########################################################
# PROPERTY
##########################################################
# Define =================================================
def gear_Wireframe_Define(in_ctxt):

    prop = in_ctxt.Source
    prop.AddParameter3("colorPicker", c.siString, "", None, None, False, False)
    # Colors
    prop.AddParameter3("A_Color_r", c.siDouble, 0, 0, 1,False, False)
    prop.AddParameter3("A_Color_g", c.siDouble, 0, 0, 1, False, False)
    prop.AddParameter3("A_Color_b", c.siDouble, .75, 0, 1, False, False)

    prop.AddParameter3("B_Color_r", c.siDouble, .75, 0, 1,False, False)
    prop.AddParameter3("B_Color_g", c.siDouble, 0, 0, 1, False, False)
    prop.AddParameter3("B_Color_b", c.siDouble, 0, 0, 1, False, False)

# OnInit =================================================
def gear_Wireframe_OnInit():

    # Get Property
    prop = PPG.Inspected(0)
    layout = PPG.PPGLayout
    layout.Clear()


    # HTML Page ---------------------
    path = os.path.join(plu.getPluginPath("gear_Wireframe"), "wireSyn.htm")
    prop.Parameters("colorPicker").Value = path
    layout.AddGroup("Wireframe colors")
    layout.AddGroup("Color presets")
    item = layout.AddItem("colorPicker", "", c.siControlSynoptic)
    item.SetAttribute(c.siUINoLabel, True)
    item.SetAttribute(c.siUICX, 308)
    layout.EndGroup()

    # Other param --------------
    layout.AddGroup("Color Range")
    item = layout.addColor("A_Color_r", "")
    item.SetAttribute(c.siUINoLabel, True)

    item = layout.addColor("B_Color_r", "")
    item.SetAttribute(c.siUINoLabel, True)

    item = layout.AddButton("colorRange", "Apply Color in Range")
    item.SetAttribute(c.siUICX, 270)
    item.SetAttribute(c.siUICY, 40)
    layout.EndGroup()
    layout.AddGroup("Color utils")
    layout.AddRow()
    item = layout.AddButton("colorRandom", "Random Color")
    item.SetAttribute(c.siUICX, 135)
    item.SetAttribute(c.siUICY, 40)
    item = layout.AddButton("colorCopy", "Copy Color")
    item.SetAttribute(c.siUICX, 135)
    item.SetAttribute(c.siUICY, 40)
    layout.EndRow()
    layout.EndGroup()

    layout.EndGroup()


    PPG.Refresh()

def gear_Wireframe_colorCopy_OnClicked():
    xsi.gear_CopyWireFrameColor()

def gear_Wireframe_colorRange_OnClicked():
    prop = xsi.ActiveSceneRoot.Properties("gear_Wireframe")
    oSel = xsi.Selection
    colorTargetA = ["A_Color_r", "A_Color_g", "A_Color_b"]
    colorTargetB = ["B_Color_r", "B_Color_g", "B_Color_b"]
    inc = [0, 0, 0]
    ColorR = prop.Parameters(colorTargetA[0]).Value
    ColorG = prop.Parameters(colorTargetA[1]).Value
    ColorB = prop.Parameters(colorTargetA[2]).Value

    if oSel.Count:
        if oSel.Count > 1:
            oCount = oSel.Count
            for i in range(3):
                inc[i] =  round((prop.Parameters(colorTargetB[i]).Value - prop.Parameters(colorTargetA[i]).Value)/(oCount-1), 3)
        for obj in oSel:
            xsi.SIMakeLocal(obj.Properties("display"), "siDefaultPropagation")
            obj.Properties('display').Parameters(12).PutValue2(None,ColorR)
            obj.Properties('display').Parameters(13).PutValue2(None, ColorG)
            obj.Properties('display').Parameters(14).PutValue2(None, ColorB)
            if oSel.Count > 1:
                #Adressing precision error
                ColorR += inc[0]
                if ColorR > 1.000: ColorR = 1.000
                elif ColorR < 0: ColorR = 0
                ColorG += inc[1]
                if ColorG > 1.000: ColorG = 1.000
                elif ColorG < 0: ColorG = 0
                ColorB += inc[2]
                if ColorB > 1.000: ColorB = 1.000
                elif ColorB < 0: ColorB = 0

def gear_Wireframe_colorRandom_OnClicked():

    for obj in xsi.Selection:
        xsi.SIMakeLocal(obj.Properties("display"), "siDefaultPropagation")
        obj.Properties('display').Parameters(12).PutValue2(None,random.random())
        obj.Properties('display').Parameters(13).PutValue2(None, random.random())
        obj.Properties('display').Parameters(14).PutValue2(None, random.random())


def gear_setWireColorRange_Init(in_ctxt):
    oCmd = in_ctxt.Source
    oCmd.Description = ""
    oCmd.ReturnValue = True

    oArgs = oCmd.Arguments
    oArgs.Add("in_button",c.siArgumentInput)
    oArgs.Add("color",c.siArgumentInput)
    return True

def gear_setWireColorRange_Execute(in_button, color):

    if in_button == 1:
        colorTarget = ["A_Color_r", "A_Color_g", "A_Color_b"]
    else:
        colorTarget = ["B_Color_r", "B_Color_g", "B_Color_b"]

    prop = xsi.ActiveSceneRoot.Properties("gear_Wireframe")
    for i in range(3):
        prop.Parameters(colorTarget[i]).Value = color[i]
