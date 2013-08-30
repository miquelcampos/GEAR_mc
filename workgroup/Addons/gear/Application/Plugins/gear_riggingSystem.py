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

## @package gear_riggingSystem.py
# @author Jeremie Passerin, Miquel Campos
# @version 1.0
#

##########################################################
# GLOBAL
##########################################################
# built-in
import os
import xml.etree.cElementTree as etree

# gear
import gear

from gear.xsi import xsi, c, lm

from gear.xsi.rig import Rig
from gear.xsi.rig.guide import RigGuide
import gear.xsi.rig.component as comp

import gear.xsi.uitoolkit as uit
import gear.xsi.utils as uti
import gear.xsi.display as dis

COMPONENT_PATH = comp.__path__[0]
TEMPLATE_PATH = os.path.join(comp.__path__[0], "_templates")

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_riggingSystem"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_BuildFromSelection","gear_BuildFromSelection")
    in_reg.RegisterCommand("gear_BuildFromFile","gear_BuildFromFile")

    in_reg.RegisterCommand("gear_GuideTools","gear_GuideTools")
    in_reg.RegisterCommand("gear_UpdateGuide","gear_UpdateGuide")

    in_reg.RegisterCommand("gear_ImportGuide","gear_ImportGuide")
    in_reg.RegisterCommand("gear_ExportGuide","gear_ExportGuide")

    in_reg.RegisterCommand("gear_InspectGuideSettings","gear_InspectGuideSettings")

    # Property
    in_reg.RegisterProperty("gear_GuideToolsUI")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# BUILD
##########################################################
# ========================================================
## Build From Selection
def gear_BuildFromSelection_Execute():

    # Build
    rig = Rig()
    rig.buildFromSelection()

    return

# ========================================================
## Build From File
def gear_BuildFromFile_Execute():

    path = uit.fileBrowser("Build From File", TEMPLATE_PATH, "", ["xml"], False)
    if not path:
        return

    # Build
    rig = Rig()
    rig.buildFromFile(path)

    return

##########################################################
# GUIDE TOOLS
##########################################################
# ========================================================
## Draw Guide
def gear_GuideTools_Execute():

    prop = xsi.ActiveSceneRoot.Properties("Guide_Tools")
    if not prop:
        prop = xsi.ActiveSceneRoot.AddProperty("gear_GuideToolsUI", False, "Guide_Tools")

    dis.inspect(prop, 340, 700, 125, 200)

# ========================================================
## Duplicate Symmetry Guide
def gear_UpdateGuide_Execute():

    rg = RigGuide()
    rg.update(xsi.Selection(0))

##########################################################
# GUIDE TOOLS UI
##########################################################
# Define =================================================
def gear_GuideToolsUI_Define(in_ctxt):

    prop = in_ctxt.Source

    # Main Tab --------------------------------------------
    prop.AddParameter3("componentList", c.siString, "", None, None, False, False)
    prop.AddParameter3("componentInfos", c.siString, "", None, None, False, True)
    prop.AddParameter3("templateList", c.siString, "", None, None, False, False)
    prop.AddParameter3("templateInfos", c.siString, "", None, None, False, True)

# Define Layout ==========================================
def gear_GuideToolsUI_OnInit():

    layout = PPG.PPGLayout
    layout.Clear()

    # Component tab ---------------------------------------
    layout.AddTab("Component")
    # Get list of component available
    component_items = []
    for item in os.listdir(COMPONENT_PATH):
        if os.path.exists(os.path.join(COMPONENT_PATH, item, "guide.py")):
            component_items.append(item)
            component_items.append(item)
    component_items.sort()

    # layout
    layout.AddGroup(" Components ")

    layout.AddRow()

    item = layout.AddEnumControl("componentList", component_items, "", c.siControlListBox)
    item.SetAttribute(c.siUINoLabel, True)
    item.SetAttribute(c.siUICY , 400)
    item.SetAttribute(c.siUIWidthPercentage , 80)

    layout.AddGroup()
    item = layout.AddButton("draw", "Draw")
    item.SetAttribute(c.siUICX , 90)
    item = layout.AddButton("duplicate", "Duplicate")
    item.SetAttribute(c.siUICX , 90)
    item = layout.AddButton("duplicateSym", "Dupl. Symmetry")
    item.SetAttribute(c.siUICX , 90)
    item = layout.AddButton("extractCtrl", "Extr. Controlers")
    item.SetAttribute(c.siUICX , 90)

    layout.EndGroup()

    layout.EndRow()

    item = layout.AddString("componentInfos", "", True, 210)
    item.SetAttribute(c.siUINoLabel, True)


    layout.EndGroup()

    if PPG.componentList.Value == "" and component_items:
        PPG.componentList.Value = component_items[1]

    gear_GuideToolsUI_componentList_OnChanged()

    # Template tab ----------------------------------------
    layout.AddTab("Template")
    # Get list of component available
    template_items = []
    items = os.listdir(TEMPLATE_PATH)
    items.sort()
    for item in items:
        if item.endswith(".xml"):
            template_items.append(item[:-4])
            template_items.append(os.path.join(TEMPLATE_PATH, item))

    # layout
    layout.AddGroup(" Templates ")

    layout.AddRow()

    item = layout.AddEnumControl("templateList", template_items, "", c.siControlListBox)
    item.SetAttribute(c.siUINoLabel, True)
    item.SetAttribute(c.siUICY , 400)
    item.SetAttribute(c.siUIWidthPercentage , 80)

    layout.AddGroup()
    item = layout.AddButton("import", "Import")
    item.SetAttribute(c.siUICX , 90)
    layout.AddSpacer()
    layout.AddSpacer()
    item = layout.AddButton("export", "Export")
    item.SetAttribute(c.siUICX , 90)

    layout.EndGroup()

    layout.EndRow()

    item = layout.AddString("templateInfos", "", True, 210)
    item.SetAttribute(c.siUINoLabel, True)

    layout.EndGroup()

    if PPG.templateList.Value == "" and template_items:
        PPG.templateList.Value = template_items[1]

    gear_GuideToolsUI_templateList_OnChanged()

    PPG.Refresh()

# ========================================================
# LOGIC
def gear_GuideToolsUI_componentList_OnChanged():

    item = PPG.componentList.Value

    module_name = "gear.xsi.rig.component."+item+".guide"
    module = __import__(module_name, globals(), locals(), ["*"], -1)

    description = "\r\n" \
                 +" Type : " + module.TYPE + " [ "+".".join([str(i) for i in module.VERSION])+" ]" + "\r\n" \
                 +" Author : " +module.AUTHOR + "\r\n" \
                 +" Url : " +module.URL + "\r\n" \
                 +" Email : " +module.EMAIL + "\r\n" \
                 +"\r\n" \
                 +" " + module.DESCRIPTION

    PPG.componentInfos.Value = description

def gear_GuideToolsUI_templateList_OnChanged():

    tree = etree.parse(PPG.templateList.Value)
    root = tree.getroot()

    name = root.get("name", "")
    user = root.get("user", "")
    date = root.get("date", "")
    description = root.get("description", "")


    description = "\r\n" \
                 +" Name : " + name + "\r\n" \
                 +" Author : " +user + "\r\n" \
                 +"\r\n" \
                 +" " + description

    PPG.templateInfos.Value = description

# ========================================================
# BUTTONS
def gear_GuideToolsUI_draw_OnClicked():

    if not PPG.componentList.Value:
        gear.log("There is no component selected in the list", gear.sev_error)
        return

    compType = PPG.componentList.Value

    rg = RigGuide()
    g = rg.drawNewComponent(xsi.Selection(0), compType)

## Duplicate Guide
def gear_GuideToolsUI_duplicate_OnClicked():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    selection = XSIFactory.CreateObject("XSI.Collection")
    selection.AddItems(xsi.Selection)

    rtn = XSIFactory.CreateObject("XSI.Collection")

    for sel in selection:
        if sel.IsClassOf(c.siX3DObjectID) and sel.Properties("settings"):
            rg = RigGuide()
            root = rg.duplicate(sel)
            if root:
                rtn.Add(root)
        else:
            gear.log("This object was skipped : "+sel.FullName, gear.sev_warning)

    if rtn.Count:
        xsi.SelectObj(rtn)

    return

## Duplicate Symmetry Guide
def gear_GuideToolsUI_duplicateSym_OnClicked():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    selection = XSIFactory.CreateObject("XSI.Collection")
    selection.AddItems(xsi.Selection)

    rtn = XSIFactory.CreateObject("XSI.Collection")

    for sel in selection:
        if sel.IsClassOf(c.siX3DObjectID) and sel.Properties("settings"):
            rg = RigGuide()
            root = rg.duplicate(sel, True)
            if root:
                rtn.Add(root)
        else:
            gear.log("This object was skipped : "+sel.FullName, gear.sev_warning)

    if rtn.Count:
        xsi.SelectObj(rtn)

    return

## Extract Controlers
def gear_GuideToolsUI_extractCtrl_OnClicked():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    # Get guide target
    guide_model = uit.pickSession(c.siModelFilter, "Pick Guide Model", False)
    if not guide_model:
      return

    if not guide_model.Properties("options"):
      gear.log("Invalid model", gear.sev_error)
      return

    guidectrl_org = guide_model.FindChild("controlers_org")
    guidectrl_grp = guide_model.Groups("controlers_grp")

    # Recreate Controlers -----------------------------
    for rig_ctl in xsi.Selection:

        if guide_model.FindChild(rig_ctl.Name):
            xsi.DeleteObj(guide_model.FindChild(rig_ctl.Name))

        guide_ctl = xsi.Duplicate(rig_ctl, 1,
                                          c.siCurrentHistory,
                                          c.siNoParent,
                                          c.siNoGrouping,
                                          c.siNoProperties,
                                          c.siNoAnimation,
                                          c.siNoConstraints,
                                          c.siNoSelection,
                                          c.siGlobalXForm)(0)

        #Get color from rig
        rR = rig_ctl.Properties('display').Parameters(12).GetValue2(None)
        rG = rig_ctl.Properties('display').Parameters(13).GetValue2(None)
        rB = rig_ctl.Properties('display').Parameters(14).GetValue2(None)
        uti.setColor(guide_ctl, [rR, rG,rB])
        guidectrl_org.AddChild(guide_ctl)
        guidectrl_grp.AddMember(guide_ctl)

        guide_ctl.Name = rig_ctl.Name

# ========================================================
## Import template
def gear_GuideToolsUI_import_OnClicked():

    if not os.path.exists(PPG.templateList.Value):
        return

    parent = xsi.Selection(0)
    if parent is not None and not parent.IsClassOf(c.siX3DObjectID):
        gear.log("Invalid Parent Selected", gear.sev_error)
        return

    if parent is not None:
        if parent.Type == "#model":
            target_model = parent
        else:
            target_model = parent.Model

        if not target_model.Properties("options"):
            gear.log("Invalid Parent Selected", gear.sev_error)
            return

    # import guide
    rg = RigGuide()
    model = rg.importFromXml(PPG.templateList.Value)

    if parent is not None:
        for child in model.children:
            if child.Name not in ["controlers_org"]:
                parent.AddChild(child)

        for group in model.Groups:
            if target_model.Groups(group.Name):
                target_model.Groups(group.Name).AddMember(group.Members)

        xsi.DeleteObj(model)

## Export template
def gear_GuideToolsUI_export_OnClicked():

    if not xsi.Selection.Count:
        xsi.LogMessage("Select an object from the guide to export", c.siError)
        return

    if xsi.Selection(0).Type == "#model":
        model = xsi.Selection(0)
    else:
        model = xsi.Selection(0).Model

    options = model.Properties("options")
    if not options:
        gear.log("Invalid selection", gear.sev_error)
        return

    path = uit.fileBrowser("Export Guide", TEMPLATE_PATH, model.Name, ["xml"], True)
    if not path:
        return

    rg = RigGuide()
    rg.exportToXml(xsi.Selection(0), path)

    gear_GuideToolsUI_OnInit()

##########################################################
# IMPORT/EXPORT GUIDE
##########################################################
# ========================================================
## Import Guide
def gear_ImportGuide_Execute():

    path = uit.fileBrowser("Import Guide", xsi.ActiveProject2.OriginPath, "", ["xml"], False)
    if not path:
        return

    rg = RigGuide()
    rg.importFromXml(path)

# ========================================================
## Export Guide
def gear_ExportGuide_Execute():

    if not xsi.Selection.Count:
        xsi.LogMessage("Select an object from the guide to export", c.siError)
        return

    if xsi.Selection(0).Type == "#model":
        model = xsi.Selection(0)
    else:
        model = xsi.Selection(0).Model

    options = model.Properties("options")
    if not options:
        gear.log("Invalid selection", gear.sev_error)
        return

    path = uit.fileBrowser("Export Guide", xsi.ActiveProject2.OriginPath, model.Name, ["xml"], True)
    if not path:
        return

    rg = RigGuide()
    rg.exportToXml(xsi.Selection(0), path)

##########################################################
# INSPECT GUIDE SETTINGS
##########################################################
# ========================================================
## Import Guide
def gear_InspectGuideSettings_Execute():
    if xsi.Selection.Count:
        oSel = xsi.Selection(0)
        settings = False
        while not settings :
            if oSel.Properties("settings"):
                settings = oSel.Properties("settings")
                xsi.InspectObj(settings)
            else:
                oSel = oSel.Parent
                if oSel.Type == "#model":
                    settings = True
                    lm("The selected object is not part of a guide, or the guide do not have settings", 4)
    else:
        lm("Nothing selected. Please select an object from a GEAR guide", 4)
