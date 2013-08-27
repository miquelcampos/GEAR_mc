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

## @package gear_selectionTools.py
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, lm, XSIMath, XSIFactory

import gear.xsi.geometry as geo
import gear.xsi.display as dis

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_selectionTools"
    in_reg.Email = "geerem@hotmail.com, hello@miqueltd.com"
    in_reg.URL = "http://www.jeremiepasserin.com, http://www.miqueltd.com "
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_SymmetrizeSelection","gear_SymmetrizeSelection")
    in_reg.RegisterCommand("gear_MirrorSelection","gear_MirrorSelection")

    in_reg.RegisterCommand("gear_Select5BranchesStars", "gear_Select5BranchesStars")
    in_reg.RegisterCommand("gear_Select6MoreBranchesStars", "gear_Select6MoreBranchesStars")

    in_reg.RegisterCommand("gear_selectionSetsCmd","gear_selectionSetsCmd")

    in_reg.RegisterProperty("gear_selectionSets")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# SYMMETRIZE SELECTION
##########################################################
# ========================================================
def gear_SymmetrizeSelection_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    subComp = xsi.Selection(0)
    if subComp.Type not in ["pntSubComponent", "edgeSubComponent", "polySubComponent"]:
        gear.log("Invalid Selection", gear.sev_error)
        return

    elements = subComp.SubComponent.ElementArray
    mesh = subComp.SubComponent.Parent3DObject

    mirror_elements = geo.getSymSubComponent(elements, subComp.Type, mesh)
    if not mirror_elements:
      return

    points = []
    points.extend(elements)
    points.extend(mirror_elements)

    sub_type = subComp.Type.replace("SubComponent", "")
    xsi.SelectGeometryComponents(mesh.FullName+"."+sub_type+str(points))

##########################################################
# MIRROR SELECTION
##########################################################
# ========================================================
def gear_MirrorSelection_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    subComp = xsi.Selection(0)
    if subComp.Type not in ["pntSubComponent", "edgeSubComponent", "polySubComponent"]:
        gear.log("Invalid Selection", gear.sev_error)
        return

    elements = subComp.SubComponent.ElementArray
    mesh = subComp.SubComponent.Parent3DObject

    mirror_elements = geo.getSymSubComponent(elements, subComp.Type, mesh)
    if not mirror_elements:
      return

    sub_type = subComp.Type.replace("SubComponent", "")
    xsi.SelectGeometryComponents(mesh.FullName+"."+sub_type+str(mirror_elements))

###########################################################
# SELECT STARS
###########################################################
# ========================================================
def gear_Select5BranchesStars_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    objects = [obj for obj in xsi.Selection if obj.Type in ["polymsh"]]

    if not objects:
        gear.log("Invalid Selection", gear.sev_error)
        return

    xsi.DeselectAll()

    for obj in objects:

        stars = geo.getStars(obj, 5, False)

        if stars:
            gear.log("There is "+str(len(stars))+" stars with 5 branches on "+obj.FullName)
            xsi.AddToSelection(obj.FullName+".pnt"+str(stars), "", True)
        else:
            gear.log("There is no stars with 5 branches on "+obj.FullName)

# ========================================================
def gear_Select6MoreBranchesStars_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    objects = [obj for obj in xsi.Selection if obj.Type in ["polymsh"]]

    if not objects:
        gear.log("Invalid Selection", gear.sev_error)
        return

    xsi.DeselectAll()

    for obj in objects:

        stars = geo.getStars(obj, 6, True)

        if stars:
            gear.log("There is "+str(len(stars))+" stars with 6 branches or more on "+obj.FullName)
            xsi.AddToSelection(obj.FullName+".pnt"+str(stars), "", True)
        else:
            gear.log("There is no stars with 6 branches or more on "+obj.FullName)


##########################################################
# Selection sets
##########################################################
# ========================================================

def gear_selectionSetsCmd_Init(in_ctxt):
    oCmd = in_ctxt.Source
    oCmd.ScriptingName = "gear_selectionSetsCmd"
    #oCmd.Language = "Python"
    oCmd.ReturnValue = True



def gear_selectionSetsCmd_Execute():
    if xsi.ActiveSceneRoot.Properties("gear_selectionSets"):
        xsi.DeleteObj(xsi.ActiveSceneRoot.Properties("gear_selectionSets"))


    oScene = xsi.ActiveProject.ActiveScene

    prop = xsi.ActiveSceneRoot.AddProperty("gear_selectionSets", False, "gear_selectionSets")

    dis.inspect(prop, 410, 525)


def gear_selectionSets_Define(in_ctxt):
    prop = in_ctxt.Source
    #List
    prop.AddParameter3("pSetsList", c.siString, 0, 0, None, False, False)


def gear_selectionSets_OnInit(varModel = "ALL", varSets = False):
    #Note: Model list option removed for simplify the tool
    sets_items =[]

    oRoot = xsi.ActiveSceneRoot
    for iGroup in oRoot.Groups:
        if len(iGroup.Name.split("_")) > 3 and iGroup.Name.split("_")[0] == "selSet":
            sets_items.append("_".join(iGroup.Name.split("_")[3:]) + ": " + "_".join(iGroup.Name.split("_")[:2]))
            sets_items.append(iGroup.FullName)
        elif len(iGroup.Name.split("_")) == 3 and iGroup.Name.split("_")[0] == "selSet":
                        sets_items.append(iGroup.Model.Name + ": " + iGroup.Name)
                        sets_items.append(iGroup.FullName)


    for iModel in oRoot.FindChildren2():
        if iModel.Type == "#model":

            if iModel.Groups:

                for iGroup in iModel.Groups:
                    if len(iGroup.Name.split("_")) == 3 and iGroup.Name.split("_")[0] == "selSet":
                        sets_items.append(iGroup.Model.Name + ": " + iGroup.Name)
                        sets_items.append(iGroup.FullName)


    # Layout -------------------------------------------------------------------------------------
    layout = PPG.PPGLayout
    layout.Clear()

    layout.AddTab("Main")
    layout.AddGroup()
    bSel = layout.AddButton("selectMembers", "Select")
    bSel.SetAttribute(c.siUICX, 380)
    bSel.SetAttribute(c.siUICY, 40)
    layout.EndGroup()

    layout.AddGroup("Selection Sets")

    oListBox = layout.AddItem( "pSetsList", "Sets", c.siControlListBox )
    oListBox.SetAttribute( c.siUICY, 320 )
    oListBox.SetAttribute( c.siUIMultiSelectionListBox, True )

    oListBox.UIItems = sets_items
    layout.EndGroup()

    layout.AddGroup("Sets Edition")
    layout.AddRow()
    bRefresh = layout.AddButton("inObject", "IN >>")
    bRefresh.SetAttribute(c.siUICX, 190)
    bRefresh.SetAttribute(c.siUICY, 30)
    bCreate = layout.AddButton("outObject", "<< OUT")
    bCreate.SetAttribute(c.siUICX, 190)
    bCreate.SetAttribute(c.siUICY, 30)
    layout.EndRow()

    layout.AddRow()
    bRefresh = layout.AddButton("refreshList", "Refresh")
    bRefresh.SetAttribute(c.siUICX, 190)
    bRefresh.SetAttribute(c.siUICY, 30)
    bCreate = layout.AddButton("createSet", "Create")
    bCreate.SetAttribute(c.siUICX, 155)
    bCreate.SetAttribute(c.siUICY, 30)
    bCreate = layout.AddButton("deleteSet", "DEL")
    bCreate.SetAttribute(c.siUICX, 30)
    bCreate.SetAttribute(c.siUICY, 30)
    layout.EndRow()
    layout.EndGroup()

    PPG.Refresh()


def gear_selectionSets_refreshList_OnClicked():

    gear_selectionSets_OnInit()

def gear_selectionSets_selectMembers_OnClicked():
    oList = PPG.pSetsList.Value.split(";")[0]
    for x in PPG.pSetsList.Value.split(";")[1:]:
        oList = oList + "," + x
    if len(oList) <= 1:
        xsi.LogMessage("Select a Set before selet items", 4)
    else:

        xsi.SelectMembers(oList, "", "")

def gear_selectionSets_createSet_OnClicked():
    
    oSel = xsi.Selection
    oRoot = xsi.ActiveSceneRoot
    oModel = oSel[0].Model

    oDescription = xsi.XSIInputBox ("Group Description", "Description", "NoDescription")
    if oDescription.isalnum():
        if oModel.ModelKind:
            oRoot.AddGroup(oSel, "selSet_" + oDescription + "_grp_" + oModel.Name )
        else:
            oModel.AddGroup(oSel, "selSet_" + oDescription + "_grp" )
        gear_selectionSets_OnInit()
    else:
        xsi.LogMessage("Description not valid. Creation aborted!!!!", 4)

def gear_selectionSets_deleteSet_OnClicked():
    from win32com.client import constants as c



    oList = PPG.pSetsList.Value.split(";")[0]
    for x in PPG.pSetsList.Value.split(";")[1:]:
        oList = oList + "," + x
    if len(oList) <= 1:
        xsi.LogMessage("Select a Set before Delete it", 4)
    else:
        oReturn = XSIUIToolkit.MsgBox( "Are you sure? Want to delete selected sets?", c.siMsgYesNo )
        if oReturn:
            xsi.DeleteObj(oList)
            gear_selectionSets_OnInit()
        else:
            lm("You cancel the delete operation.")

def gear_selectionSets_inObject_OnClicked():
    from win32com.client import constants as c
    oList = PPG.pSetsList.Value.split(";")[0]

    if len(oList) <= 1:
        xsi.LogMessage("Select one Set before add objects to it, and Only one set at the time", 4)
    else:
        oReturn = XSIUIToolkit.MsgBox( "ADD Selected objects to first selected Set?, Remember if you have more than one set, only the first one will be used. ", c.siMsgYesNo )
        if oReturn:
            xsi.SIAddToGroup(oList)

        else:
            lm("You cancel the adding operation.", 4)

def gear_selectionSets_outObject_OnClicked():
    from win32com.client import constants as c
    oList = PPG.pSetsList.Value.split(";")[0]

    if len(oList) <= 1:
        xsi.LogMessage("Select one Set before remove objects to it, and Only one set at the time", 4)
    else:
        oReturn = XSIUIToolkit.MsgBox( "REMOVE Selected objects to first selected Set?, Remember if you have more than one set, only the first one will be used. ", c.siMsgYesNo )
        if oReturn:
            xsi.RemoveFromGroup(oList)

        else:
            lm("You cancel the adding operation.", 4)
