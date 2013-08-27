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

## @package gear_io.py
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
import gear

from gear.xsi import xsi, c, dynDispatch

import gear.xsi.uitoolkit as uit
import gear.xsi.io as io
import gear.xsi.xmldom as xsixmldom

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_io"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    in_reg.RegisterCommand("gear_ImportEnvelope","gear_ImportEnvelope")
    in_reg.RegisterCommand("gear_ImportSkin","gear_ImportSkin")

    in_reg.RegisterCommand("gear_ExportSkin","gear_ExportSkin")
    in_reg.RegisterCommand("gear_ExportEnvelope","gear_ExportEnvelope")
    in_reg.RegisterCommand("gear_ExportObject","gear_ExportObject")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# IMPORT
##########################################################
# ========================================================
## Import Envelope
def gear_ImportSkin_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    # -----------------------------------------------------
    # Getting the file path
    path = uit.fileBrowser("Import Skin", xsi.ActiveProject2.OriginPath, "", ["xml"], False)
    if not path:
        return

    # -----------------------------------------------------
    xml_objs = io.getObjectDefinitions(path, xsi.Selection, True)
    if not xml_objs:
        return

    # -----------------------------------------------------
    for obj in xsi.Selection:

        if obj.Name not in xml_objs.keys():
            continue

        io.importSkin(xml_objs[obj.Name], obj)

# ========================================================
## Import Envelope
def gear_ImportEnvelope_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    # -----------------------------------------------------
    # Getting the file path
    path = uit.fileBrowser("Import Envelope", xsi.ActiveProject2.OriginPath, "", ["xml"], False)
    if not path:
        return

    # -----------------------------------------------------
    xml_objs = io.getObjectDefinitions(path, xsi.Selection, True)
    if not xml_objs:
        return

    # -----------------------------------------------------
    for sel in xsi.Selection:

        if sel.Type in ["pntSubComponent"]:
            obj = sel.SubComponent.Parent3DObject
            pnt_selection = sel.SubComponent.ElementArray
        else:
            obj = sel
            pnt_selection = None

        if obj.Name not in xml_objs.keys():
            continue

        io.importEnvelope(xml_objs[obj.Name], obj, pnt_selection)

##########################################################
# EXPORT
##########################################################
# ========================================================
## Export Skin
def gear_ExportSkin_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    # -----------------------------------------------------
    # Getting the file path
    path = uit.fileBrowser("Export Skin", xsi.ActiveProject2.OriginPath, xsi.Selection(0).Model.Name+"_skin.xml", ["xml"], True)
    if not path:
        return

    io.exportSkin(path, xsi.Selection, False)

# ========================================================
## Export Envelope
def gear_ExportEnvelope_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    # -----------------------------------------------------
    # Getting the file path
    path = uit.fileBrowser("Export Envelope", xsi.ActiveProject2.OriginPath, xsi.Selection(0).Model.Name+"_skin.xml", ["xml"], True)
    if not path:
        return

    io.exportEnvelope(path, xsi.Selection, False)

# ========================================================
## Export Object
def gear_ExportObject_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    # -----------------------------------------------------
    # Getting the file path
    path = uit.fileBrowser("Export Object", xsi.ActiveProject2.OriginPath, xsi.Selection(0).Name+"_skin.xml", ["xml"], True)
    if not path:
        return

    xsixmldom.resetOptions()
    xObject = xsixmldom.getObject(xsi.Selection(0))
    xObject.save(path)




