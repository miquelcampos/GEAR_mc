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

## @package gear_synoptic.py
# @author Jeremie Passerin, Miquel Campos
# @version 1.0
#

##########################################################
# GLOBAL
##########################################################
# Built_in
import os

# gear
from gear.xsi import xsi, c
import gear.xsi.plugin as plu
import gear.xsi.display as dis

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_synoptic"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_OpenSynoptic","gear_OpenSynoptic")

    # Property
    in_reg.RegisterProperty("gear_Synoptic")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# OPEN SYNOPTIC
##########################################################
def gear_OpenSynoptic_Execute():

    if xsi.ActiveSceneRoot.Properties("gear_Synoptic"):
        prop = xsi.ActiveSceneRoot.Properties("gear_Synoptic")
    else:
        prop = xsi.ActiveSceneRoot.AddProperty("gear_Synoptic", False, "gear_Synoptic")

    dis.inspect(prop, 335, 700, 125, 75)
 
##########################################################
# PROPERTY
##########################################################
# Define =================================================
def gear_Synoptic_Define(in_ctxt):

    prop = in_ctxt.Source
    prop.AddParameter3("Model", c.siString, "", None, None, False, False)

# Define Layout ==========================================
def gear_Synoptic_DefineLayout(in_ctxt):

    layout = in_ctxt.Source

    # Logic
    path = plu.getPluginFullPath("gear_Synoptic")
    file = open(path)
    layout.Logic = file.read()

    return True

# OnInit =================================================
def gear_Synoptic_OnInit():

    # Get Property
    prop = PPG.Inspected(0)
    layout = PPG.PPGLayout
    layout.Clear()

    # Plugin Folder Path
    path = plu.getPluginPath("gear_Synoptic")

    # Get Active Model -----------------------------
    model_items = getRigModels()

    if model_items and PPG.Model.Value not in model_items:
        PPG.Model.Value = model_items[1]

    # Common Logic
    file = open(plu.getPluginFullPath("gear_Synoptic"))
    layout.Logic = file.read()

    # Default Layout
    if not PPG.Model.Value:
        layout.AddString("No valid model in the scene")
        layout.AddButton("RefreshModelList", "Refresh")
        return

    # Parse Tabs -----------------------------------
    model = xsi.ActiveSceneRoot.FindChild(PPG.Model.Value, c.siModelType)
    model_prop = model.Properties("info")

    tab_names = model_prop.Parameters("synoptic").Value
    if not tab_names:
        layout.AddTab("Default Tab")

        layout.AddGroup("Active Model")
        layout.AddRow()
        item = layout.AddEnumControl("Model", model_items, "Model", c.siControlCombo)
        item.SetAttribute(c.siUINoLabel, True)
        item = layout.AddButton("RefreshModelList", "Refresh")
        item = layout.AddButton("Highlight", "Highlight")
        layout.EndRow()
        layout.EndGroup()

        layout.AddGroup("")
        layout.AddStaticText("No tab in this model")
        layout.EndGroup()

    else:
        for tab in tab_names.split(","):

            tab_path = os.path.join(path, "tabs", tab)
            if not tab or not os.path.exists(tab_path):
                continue

            param_path  = os.path.join(tab_path, "parameters.py")
            logic_path  = os.path.join(tab_path, "logic.py")
            layout_path  = os.path.join(tab_path, "layout.py")

            # Parameters -------------
            if os.path.exists(param_path):
                xsi.ExecuteScript(param_path, "Python", "addParameters", [prop])

            # Logic ------------------
            if os.path.exists(logic_path):
                file = open(logic_path)
                layout.Logic += file.read()

            # Layout -----------------
            if os.path.exists(layout_path):
                layout.AddTab(tab[tab.find("/")+1:])

                layout.AddGroup("Active Model")
                layout.AddRow()
                item = layout.AddEnumControl("Model", model_items, "Model", c.siControlCombo)
                item.SetAttribute(c.siUINoLabel, True)
                item = layout.AddButton("RefreshModelList", "Refresh")
                item = layout.AddButton("Highlight", "Highlight")
                layout.EndRow()
                layout.EndGroup()

                layout.AddGroup("")
                xsi.ExecuteScript(layout_path, "Python", "addLayout", [layout, prop])
                layout.EndGroup()

    PPG.Refresh()

##########################################################
# EVENTS
##########################################################
def gear_Synoptic_RefreshModelList_OnClicked():
    gear_Synoptic_OnInit()

def gear_Synoptic_Model_OnChanged():
    gear_Synoptic_OnInit()

def gear_Synoptic_Highlight_OnClicked():
    model = xsi.ActiveSceneRoot.FindChild(PPG.Model.Value, c.siModelType)
    dis.highlight(model)

##########################################################
# MISC
##########################################################
def getRigModels():

    model_items = []

    models = xsi.ActiveSceneRoot.FindChildren("", c.siModelType)

    for model in models:
        info_prop = model.Properties("info")
        if info_prop and info_prop.Parameters("synoptic"):
             model_items.append(info_prop.Parameters("rig_name").Value+" ("+model.Name+")")
             model_items.append(model.FullName)

    return model_items