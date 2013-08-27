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

## @package gear_PSet.py
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################

import gear

from gear.xsi import xsi, c, dynDispatch, XSIFactory

import gear.xsi.plugin as plu
import gear.xsi.ppg as ppg

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_PSet"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    in_reg.RegisterProperty("gear_PSet")
    in_reg.RegisterCommand("gear_PSet_Apply","gear_PSet_Apply")
    in_reg.RegisterCommand("gear_PSet_Debug","gear_PSet_Debug")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    gear.log(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# PROPERTY
##########################################################
# Define =================================================
def gear_PSet_Define(in_ctxt):

    prop = in_ctxt.Source

    # Debug Tab --------------------------------------------
    prop.AddParameter3("layout", c.siString, "", None, None, False, False)
    prop.AddParameter3("logic", c.siString, "", None, None, False, False)
    prop.AddParameter3("debug", c.siBool, False, None, None, False, False)

# Define Layout ==========================================
def gear_PSet_DefineLayout(in_ctxt):

    layout = in_ctxt.Source

    path = plu.getPluginFullPath("gear_PSet")
    f = open(path)
    layout.Logic = f.read()

    return True

# OnInit =================================================
def gear_PSet_OnInit():

    prop = PPG.Inspected(0)
    layout = PPG.PPGLayout

    # Define the Logic -----------------------------------------------
    path = plu.getPluginFullPath("gear_PSet")
    f = open(path)

    layout.Logic = f.read()
    layout.Logic += PPG.Logic.Value

    # Define Layout --------------------------------------------------
    layout.Clear()

    baseParameters = ["layout", "logic", "debug"]

    # If there is no parameters and debug mode is False
    if not PPG.debug.Value and prop.Parameters.Count == len(baseParameters):
        layout.AddStaticText("No Parameter to display")

    # If Debug Mode is True or no layout has been define
    elif PPG.debug.Value or PPG.layout.Value == "":

        layout.AddTab("DEBUG LAYOUT")

        layout.AddGroup()
        layout.AddRow()
        layout.AddButton("refresh", "Refresh")
        layout.AddSpacer()
        layout.AddButton("hide", "Hide Me")
        layout.AddButton("generateLayout", "Generate Layout")
        layout.EndRow()
        layout.EndGroup()

        layout.AddGroup("Layout")
        item = layout.AddString("layout", "", True, 300)
        item.SetAttribute(c.siUINoLabel, True)
        layout.EndGroup()

        layout.AddTab("DEBUG LOGIC")

        layout.AddGroup()
        layout.AddRow()
        layout.AddButton("refresh", "Refresh")
        layout.AddSpacer()
        layout.AddButton("hide", "Hide Me")
        layout.AddButton("generateLayout", "Generate Layout")
        layout.EndRow()
        layout.EndGroup()

        layout.AddGroup("Logic")
        item = layout.AddString("logic", "", True, 300)
        item.SetAttribute(c.siUINoLabel, True)
        layout.EndGroup()

        # If there is no layout define we still display the parameter with a default layout
        if PPG.layout.Value == "":
            drawDefaultLayout(prop, baseParameters)

    # Add custom Layout -----------------------------------------
    layoutcode = PPG.layout.Value.replace("\r\n", "\r\n    ")
    code = "def readLayout(layout, PPG):\r\n    "+layoutcode+"\r\n    return\r\n"

    try:
        xsi.ExecuteScriptCode(code, "Python", "readLayout", [layout, PPG])
    except Exception, e:

        gear.log("INVALID LAYOUT DETECTED ========================", gear.sev_error)
        for arg in e.args:
            gear.log(arg, gear.sev_error)

        gear.log("LAYOUT CODE ====================================", gear.sev_error)
        gear.log("\r\n"+code, gear.sev_error)
        gear.log("END OF LAYOUT CODE =============================", gear.sev_error)

        drawDefaultLayout(prop, baseParameters)

    PPG.Refresh()

##########################################################
# EVENTS
##########################################################
# ========================================================
def drawDefaultLayout(prop, baseParameters):

    layout = prop.PPGLayout

    layout.AddTab(prop.Name)

    layout.AddGroup("Default Layout")
    for param in prop.Parameters:
        if param.ScriptName not in baseParameters:
            layout.AddItem(param.ScriptName)
    layout.EndGroup()

# ========================================================
def gear_PSet_refresh_OnClicked():
    gear_PSet_OnInit()

# ========================================================
def gear_PSet_hide_OnClicked():
    PPG.debug.Value = False
    gear_PSet_OnInit()

# ========================================================
def gear_PSet_generateLayout_OnClicked():

    prop = PPG.Inspected(0)

    ppglayout = ppg.PPGLayout()

    tab = ppglayout.addTab(prop.Name)
    group = tab.addGroup("Default Layout")
    for param in prop.Parameters:
        if param.ScriptName not in ["layout", "logic", "debug"]:
            group.addItem(param.ScriptName)

    PPG.layout.Value = ppglayout.getValue()

    PPG.Refresh()

##########################################################
# EXECUTE
##########################################################
# Init ===================================================
def gear_PSet_Apply_Init(in_ctxt):

    cmd = in_ctxt.Source
    cmd.Description = ""
    cmd.ReturnValue = True

    args = cmd.Arguments
    args.Add("parent")
    args.Add("sname", c.siArgumentInput, "gear_PSet")
    args.Add("branch", c.siArgumentInput, False)
    args.Add("debug", c.siArgumentInput, False)

    return

# Execute ================================================
def gear_PSet_Apply_Execute(parent, sname, branch, debug):

    if not parent:
        if xsi.Selection.Count:
            parent = xsi.Selection(0)
        else:
            gear.log("Select an object to create the gear_PSet on", gear.sev_error)
            return

    prop = parent.AddProperty("gear_PSet", branch, sname)

    # Set the debug mode
    prop.Parameters("debug").Value = debug

    return prop

##########################################################
# TOGGLE DEBUG MODE
##########################################################
# Execute ================================================
def gear_PSet_Debug_Execute():

    prop = xsi.Selection(0)

    if not prop or not prop.Parameters("debug"):
        gear.log("Select a gear_PSet", gear.sev_error)
        return

    # Set the debug mode
    prop.Parameters("debug").Value = True

