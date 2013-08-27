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

## @package gear_mirrorAnimation.py
# @author Jeremie Passerin
# @version 1.0
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import re
import xml.etree.cElementTree as etree

# gear
import gear

from gear.xsi import xsi, c, XSIFactory

import gear.xmldom as xmldom
import gear.xsi.uitoolkit as uit
import gear.xsi.utils as uti
import gear.xsi.fcurve as fcv
import gear.xsi.parameter as par
import gear.xsi.animation as ani

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_mirrorAnimation"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_MirrorPose","gear_MirrorPose")
    in_reg.RegisterCommand("gear_MirrorAnimation","gear_MirrorAnimation")

    in_reg.RegisterCommand("gear_CreateMirrorTemplate","gear_CreateMirrorTemplate")

    # Properties
    in_reg.RegisterProperty("gear_Mirror")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# MIRROR POSE / ANIMATION
##########################################################
# ========================================================
def gear_MirrorPose_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    ani.mirror(xsi.Selection)

# ========================================================
def gear_MirrorAnimation_Execute(): # controlers

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return
    ## Miquel Shed added:  
    else:                
        controlers = XSIFactory.CreateActiveXObject( "XSI.Collection" )
        controlers.AddItems( xsi.Selection )
    ##end of the addition


    # Get First and Last Frame
    frames = fcv.getFirstAndLastKey(controlers)
    if not frames:
        gear.log("No Key on selection, cannot perform mirror animation", gear.sev_error)
        return

    # UI
    ui_prop = xsi.ActiveSceneRoot.AddProperty("CustomProperty", False, "Mirror Animation")
    pOffset       = ui_prop.AddParameter3("offset", c.siInt4, 0, None, None, False, False)
    pConsiderTime = ui_prop.AddParameter3("considerTime", c.siBool, False, None, None, False, False)
    pFrameIn      = ui_prop.AddParameter3("frameIn", c.siInt4, frames[0], None, None, False, False)
    pFrameOut     = ui_prop.AddParameter3("frameOut", c.siInt4, frames[1], None, None, False, False)

    layout = ui_prop.PPGLayout
    layout.AddGroup("Options")
    layout.AddItem(pOffset.ScriptName, "Offset")
    layout.AddItem(pConsiderTime.ScriptName, "Consider Time")
    layout.AddRow()
    layout.AddItem(pFrameIn.ScriptName, "Frame In")
    layout.AddItem(pFrameOut.ScriptName, "Frame Out")
    layout.EndRow()
    layout.EndGroup()

    rtn = xsi.InspectObj(ui_prop, "", "Mirror Animation", c.siModal, False)

    frame_offset = pOffset.Value
    considerTime = pConsiderTime.Value
    frame_in     = pFrameIn.Value
    frame_out    = pFrameOut.Value

    xsi.DeleteObj(ui_prop)

    if rtn:
        return

    # Mirror
    ani.mirror(controlers, True, frame_offset, considerTime, frame_in, frame_out)

    return

##########################################################
# CREATE TEMPLATES
##########################################################
# ========================================================
def gear_CreateMirrorTemplate_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    model = xsi.Selection(0).Model
    cnx_prop = ani.createMirrorCnxTemplate(model, xsi.Selection)

    xsi.InspectObj(cnx_prop)

##########################################################
# MIRROR CNX TEMPLATE
##########################################################
# ========================================================
def gear_Mirror_Define(in_ctxt):

    prop = in_ctxt.Source

    # Cnx Part
    prop.AddParameter3("Debug", c.siBool, True, None, None, False, False)

    prop.AddParameter3("Search", c.siString, "", None, None, False, False)
    prop.AddParameter3("Count", c.siInt4, 0, 0, None, False, True)

    gridHidden = prop.AddGridParameter("CnxGridHidden")
    gridDisplay = prop.AddGridParameter("CnxGridDisplay")

    gridData = gridHidden.Value
    gridData.ColumnCount = 3
    gridData.SetColumnLabel(0, "From")
    gridData.SetColumnLabel(1, "To")
    gridData.SetColumnLabel(2, "Inversed")
    gridData.SetColumnType(2, c.siColumnBool)

    gridData = gridDisplay.Value
    gridData.ColumnCount = 3
    gridData.SetColumnLabel(0, "From")
    gridData.SetColumnLabel(1, "To")
    gridData.SetColumnLabel(2, "Inversed")
    gridData.SetColumnType(2, c.siColumnBool)

    return

# ========================================================
def gear_Mirror_DefineLayout(in_ctxt):

    layout = in_ctxt.Source
    layout.Clear()

    # Connections --------------
    layout.AddTab("Connections")
    layout.AddGroup("Files")
    layout.AddRow()
    layout.AddSpacer()
    item = layout.AddButton("ImportRules", "Import")
    item = layout.AddButton("ExportRules", "Export")
    layout.EndRow()
    layout.EndGroup()

    layout.AddGroup("Rules")
    layout.AddRow()
    item = layout.AddButton("DeleteUnused", "Delete Unused Rules")
    layout.AddSpacer()
    item = layout.AddButton("AddRule", "Add")
    item = layout.AddButton("DeleteRule", "Delete")
    layout.EndRow()
    layout.AddRow()
    item = layout.AddItem("Search")
    item.SetAttribute(c.siUINoLabel, True)
    item = layout.AddButton("SearchData", "Search")
    item = layout.AddButton("SearchSelected", "Search Selected")
    layout.EndRow()
    layout.EndGroup()

    layout.AddGroup("Connections")
    item = layout.AddItem("Count", "Count")
    item = layout.AddItem("CnxGridDisplay", "", c.siControlGrid)
    item.SetAttribute(c.siUINoLabel, True)
    layout.EndGroup()

    return

# ========================================================
def gear_Mirror_ImportRules_OnClicked():

    cnx_grid = PPG.CnxGridHidden.Value

    # Parse XML file 
    path = uit.fileBrowser("Import Mirroring Templates", xsi.ActiveProject2.OriginPath, "", ["xml"], False)
    if not path:
        return

    tree = etree.parse(path)
    root = tree.getroot()

    # Create Dictionary
    connections = {}
    for xml_cnx in root.findall("mirrorCnxMap/cnx"):
        connections[xml_cnx.get("map_to")] = [xml_cnx.get("map_from"), xml_cnx.get("inv")]

    par.setDataGridFromDict(cnx_grid, connections)
    PPG.Count.Value = len(connections)

# ========================================================
def gear_Mirror_ExportRules_OnClicked():

    model = PPG.Inspected(0).Model
    cnx_grid = PPG.CnxGridHidden.Value
    connections = par.getDictFromGridData(cnx_grid)

    # Parse XML file --------------------------------
    path = uit.fileBrowser("Export Mirroring Templates", xsi.ActiveProject2.OriginPath, model.Name, ["xml"], True)
    if not path:
        return

    # Create Root structure
    xml_root = etree.Element("mirrorTemplates", version="1.0", comment="Mapping rules for gear_MirrorAnimation plugin")


    # Infos
    xml_infos = etree.SubElement(xml_root, "infos", model=model.Name, count=str(len(connections)))
    xml_cnxMap = etree.SubElement(xml_root, "mirrorCnxMap")

    # Export CnxMap
    keys = connections.keys()
    keys.sort()

    for k in keys:
        etree.SubElement(xml_cnxMap, "cnx", map_from=k, map_to=connections[k][0], inv=str(connections[k][1]))

    xmldom.indent(xml_root)
    tree = etree.ElementTree(xml_root)
    tree.write(path)

# ========================================================
def gear_Mirror_DeleteUnused_OnClicked():

    cnx_grid = PPG.CnxGridHidden.Value
    cnxGrid_display = PPG.CnxGridDisplay.Value
    connections = par.getDictFromGridData(cnx_grid)
    connections_display = par.getDictFromGridData(cnxGrid_display)

    newConnections_hidden = {}
    for k in connections:
        if connections[k][1] or k != connections[k][0]:
            newConnections_hidden[k] = connections[k]
        else:
            if k in connections_display:
                connections_display.pop(k)

    par.setDataGridFromDict(cnxGrid_display, connections_display)
    par.setDataGridFromDict(cnx_grid, newConnections_hidden)
    PPG.Count.Value = len(newConnections_hidden)

# ========================================================
def gear_Mirror_AddRule_OnClicked():

    cnxGrid_display = PPG.CnxGridDisplay.Value
    cnx_grid = PPG.CnxGridHidden.Value

    connections_display = {}
    for ctl in xsi.Selection:
        connections = ani.addMirroringRule(ctl, cnx_grid)
        connections_display.update(searchRuleInDict(ctl.Name+".", connections))

    par.setDataGridFromDict(cnxGrid_display, connections_display)
    PPG.Count.Value = len(connections)

# ========================================================
def gear_Mirror_DeleteRule_OnClicked():

    cnxGrid_display = PPG.CnxGridDisplay.Value
    cnx_grid = PPG.CnxGridHidden.Value
    connections = par.getDictFromGridData(cnx_grid)
    connections_display = par.getDictFromGridData(cnxGrid_display)
    grid_widget = cnxGrid_display.GridWidget

    for i in range(cnxGrid_display.RowCount):
        if grid_widget.IsRowSelected(i):
            sKey = cnxGrid_display.GetRowValues(i)[0]
            connections_display.pop(sKey)
            connections.pop(sKey)

    par.setDataGridFromDict(cnxGrid_display, connections_display)
    par.setDataGridFromDict(cnx_grid, connections)
    PPG.Count.Value = len(connections)

# ========================================================
def gear_Mirror_Search_OnChanged():

    cnx_grid = PPG.CnxGridHidden.Value
    connections = par.getDictFromGridData(cnx_grid)

    connections_display = searchRuleInDict(PPG.Search.Value, connections)

    cnxGrid_display = PPG.CnxGridDisplay.Value
    par.setDataGridFromDict(cnxGrid_display, connections_display)

# ========================================================
def gear_Mirror_SearchData_OnClicked():

    cnx_grid = PPG.CnxGridHidden.Value
    connections = par.getDictFromGridData(cnx_grid)

    connections_display = searchRuleInDict(PPG.Search.Value, connections)

    cnxGrid_display = PPG.CnxGridDisplay.Value
    par.setDataGridFromDict(cnxGrid_display, connections_display)

# ========================================================
def gear_Mirror_SearchSelected_OnClicked():

    cnx_grid = PPG.CnxGridHidden.Value
    connections = par.getDictFromGridData(cnx_grid)

    connections_display = {}
    for ctl in xsi.Selection:
        connections_display.update(searchRuleInDict(ctl.Name+".", connections))

    cnxGrid_display = PPG.CnxGridDisplay.Value
    par.setDataGridFromDict(cnxGrid_display, connections_display)

# ========================================================
def gear_Mirror_CnxGridDisplay_OnChanged():

    cnx_grid  = PPG.CnxGridHidden.Value
    cnxGrid_display     = PPG.CnxGridDisplay.Value
    connections         = par.getDictFromGridData(cnx_grid)
    connections_display = par.getDictFromGridData(cnxGrid_display)

    for k in connections_display:
        connections[k] = connections_display[k]

    par.setDataGridFromDict(cnx_grid, connections)

##########################################################
# MISC
##########################################################
# ========================================================
def searchRuleInDict(search_name, connections):

    if not search_name:
        return {}

    connections_display = {}
    search_name = search_name.replace("*", ".*")
    for param_name in connections.keys():
        if re.match(search_name, param_name):
            connections_display[param_name] = connections[param_name]

    return connections_display
