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

## @package gear_renamer.py
# @author Jeremie Passerin
# @version 1.0
#

##########################################################
# GLOBAL
##########################################################
# Built_in
import re

# gear
from gear.xsi import xsi, c, XSIFactory
import gear.string as string
import gear.xsi.display as dis

# Constants
LOWER_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
UPPER_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_renamer"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    in_reg.RegisterCommand("gear_OpenRenamer","gear_OpenRenamer")
    in_reg.RegisterProperty("gear_Renamer")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)
    
    return True

##########################################################
# OPEN RENAMER
##########################################################
# ========================================================
def gear_OpenRenamer_Execute():

    if xsi.ActiveSceneRoot.Properties("gear_Renamer"):
        xsi.DeleteObj(xsi.ActiveSceneRoot.Properties("gear_Renamer"))

    prop = xsi.ActiveSceneRoot.AddProperty("gear_Renamer", False, "gear_Renamer")

    dis.inspect(prop, 550, 450)

##########################################################
# RENAMER PROPERTY
##########################################################
# ========================================================
def gear_Renamer_Define(in_ctxt):

    prop = in_ctxt.Source

    prop.AddParameter3("UseSearchReplace", c.siBool, 1, None, None, False, False)

    prop.AddParameter3("EditMode", c.siInt4, 0, 0, None, False, False)

    prop.AddParameter3("Search", c.siString, "", None, None, False, False)
    prop.AddParameter3("Replace", c.siString, "", None, None, False, False)

    prop.AddParameter3("RespectCase", c.siBool, 1, None, None, False, False)

    prop.AddParameter3("AddPrefix", c.siBool, 0, None, None, False, False)
    prop.AddParameter3("Prefix", c.siString, "", None, None, False, False)
    prop.AddParameter3("AddSuffix", c.siBool, 0, None, None, False, False)
    prop.AddParameter3("Suffix", c.siString, "", None, None, False, False)

    prop.AddParameter3("UseLetters", c.siBool, False, None, None, False, False)
    prop.AddParameter3("UpperCase", c.siBool, False, None, None, False, False)

    prop.AddParameter3("start", c.siInt4, 0, 0, None, False, False)
    prop.AddParameter3("step", c.siInt4, 1, 1, None, False, False)

    prop.AddParameter3("rootSuffix", c.siString, "chn", None, None, False, False)
    prop.AddParameter3("boneSuffix", c.siString, "jnt_#", None, None, False, False)
    prop.AddParameter3("effSuffix", c.siString, "eff", None, None, False, False)

    prop.AddParameter3("rootIcon", c.siInt4, 4, 0, 10, False, False)
    prop.AddParameter3("effIcon", c.siInt4, 2, 0, 10, False, False)
    prop.AddParameter3("size", c.siDouble, .1, 0, None, False, False)

    grid = prop.AddGridParameter("PreviewGrid")

    grid_data = grid.Value
    grid_data.ColumnCount = 3
    grid_data.SetColumnLabel(0, "Model")
    grid_data.SetColumnLabel(1, "Name")
    grid_data.SetColumnLabel(2, "New Name")

# ========================================================
def gear_Renamer_OnInit():

    # Items ----------------------------------------------
    mode_items = ["Simple", 0, "Regular Expression", 1, "Serialize", 2, "Chain", 3]
    icons_items = ["None", 0, "Null", 1, "Rings", 2, "Arrow Rings", 3, "Box", 4, "Circle", 5, "Square", 6, "Diamond", 7, "Pyramid", 8, "Pointed Box", 9, "Arrow", 10]

    alphabet_items = []
    if PPG.UpperCase.Value:
        for i, s in enumerate(UPPER_ALPHABET):
            alphabet_items.append(s)
            alphabet_items.append(i)
    else:
        for i, s in enumerate(LOWER_ALPHABET):
            alphabet_items.append(s)
            alphabet_items.append(i)

    # Layout ---------------------------------------------
    layout = PPG.PPGLayout
    layout.Clear()

    layout.AddTab("Main")

    # Edit Mode
    layout.AddGroup("Edit Mode")
    layout.AddEnumControl("EditMode", mode_items, "Edit Mode", c.siControlCombo)
    layout.EndGroup()

    # Chain
    if PPG.EditMode.Value == 3:
        layout.AddGroup("Name")
        layout.AddItem("Replace", "Chain Name")
        layout.EndGroup()
        layout.AddGroup("Suffixes")
        layout.AddItem("rootSuffix", "Root")
        layout.AddItem("boneSuffix", "Bone")
        layout.AddItem("effSuffix", "Eff")
        layout.EndGroup()
        layout.AddGroup("Display")
        layout.AddEnumControl("rootIcon", icons_items, "Root Icon", c.siControlCombo)
        layout.AddEnumControl("effIcon", icons_items, "Eff Icon", c.siControlCombo)
        layout.AddItem("size", "Size")
        layout.EndGroup()

    # Serialize
    elif PPG.EditMode.Value == 2:
        layout.AddGroup("Serialize")
        layout.AddItem("Replace", "Name")
        layout.AddRow()
        layout.AddItem("UseLetters", "Use Letter")
        layout.AddItem("UpperCase", "UpperCase")
        layout.EndRow()
        if PPG.UseLetters.Value:
            layout.AddEnumControl("start", alphabet_items, "Start", c.siControlCombo)
        else:
            layout.AddItem("start", "Start")
        layout.AddItem("step", "Step")
        layout.EndGroup()

    # Search / Replace
    else:

        layout.AddGroup("Search / Replace")

        layout.AddItem("UseSearchReplace", "Search & Replace")
        # layout.AddItem("RespectCase", "Match Case")

        layout.AddItem("Search", "Search")
        layout.AddItem("Replace", "Replace")

        layout.EndGroup()

        # Prefix / Suffix
        layout.AddGroup("Prefix / Suffix")
        layout.AddRow()
        layout.AddItem("AddPrefix", "Prefix")
        item = layout.AddItem("Prefix")
        item.SetAttribute(c.siUINoLabel, True)
        item.SetAttribute(c.siUIWidthPercentage, 90)
        layout.EndRow()
        layout.AddRow()
        layout.AddItem("AddSuffix", "Suffix")
        item = layout.AddItem("Suffix")
        item.SetAttribute(c.siUINoLabel, True)
        item.SetAttribute(c.siUIWidthPercentage, 90)
        layout.EndRow()
        layout.EndGroup()

    # Result
    layout.AddGroup("Result")

    item = layout.AddItem("PreviewGrid", "", c.siControlGrid)
    item.SetAttribute(c.siUINoLabel, True)

    layout.AddRow()
    if PPG.EditMode.Value == 3:
        item = layout.AddButton("PreviewChain", "PREVIEW")
    else:
        item = layout.AddButton("Preview", "PREVIEW")
    item.SetAttribute(c.siUICX, 100)
    item.SetAttribute(c.siUICY, 40)
    layout.AddSpacer()
    item = layout.AddButton("Apply", "APPLY")
    item.SetAttribute(c.siUICX, 100)
    item.SetAttribute(c.siUICY, 40)
    layout.EndRow()

    layout.EndGroup()

    # Logic
    PPG.Search.Enable(PPG.UseSearchReplace.Value)
    PPG.Replace.Enable(PPG.UseSearchReplace.Value)
    PPG.RespectCase.Enable(PPG.UseSearchReplace.Value)
    PPG.EditMode.Enable(PPG.UseSearchReplace.Value)
    PPG.Prefix.Enable(PPG.AddPrefix.Value)
    PPG.Suffix.Enable(PPG.AddSuffix.Value)
    PPG.UpperCase.Enable(PPG.UseLetters.Value)

    PPG.Refresh()

##########################################################
# EVENTS
##########################################################
# ========================================================
def gear_Renamer_EditMode_OnChanged():
    gear_Renamer_OnInit()
def gear_Renamer_UseSearchReplace_OnChanged():
    gear_Renamer_OnInit()
def gear_Renamer_AddPrefix_OnChanged():
    gear_Renamer_OnInit()
def gear_Renamer_AddSuffix_OnChanged():
    gear_Renamer_OnInit()
def gear_Renamer_UseLetters_OnChanged():
    gear_Renamer_OnInit()
def gear_Renamer_UpperCase_OnChanged():
    gear_Renamer_OnInit()

# ========================================================
def gear_Renamer_PreviewGrid_OnChanged():

    grid_data = PPG.PreviewGrid.Value
    for i in range(grid_data.RowCount):

        row_values = grid_data.GetRowValues(i)

        # Check if new entered name is not empty
        if row_values[2] == "":
            grid_data.SetRowValues(i, [row_values[0], row_values[1], row_values[1]])

        # Get a valid name
        row_values = grid_data.GetRowValues(i)
        grid_data.SetRowValues(i, [row_values[0], row_values[1], string.normalize(row_values[2])])

        setRowColor(grid_data, i)

    PPG.Refresh()

# ========================================================
def gear_Renamer_Preview_OnClicked():

    grid_data = PPG.PreviewGrid.Value
    grid_data.RowCount = xsi.Selection.Count

    for i in range(grid_data.RowCount):

        sel = xsi.Selection(i)
        new_name = rename(PPG, sel.Name, i)

        grid_data.SetRowLabel(i, "  "+str(i)+"  ")
        grid_data.SetRowValues(i, [sel.Model.FullName, sel.FullName[sel.FullName.find(".")+1:], new_name])

        setRowColor(grid_data, i)

    PPG.Refresh()

# ========================================================
def gear_Renamer_PreviewChain_OnClicked():

    chain_objects = XSIFactory.CreateObject("XSI.Collection")
    chain_objects.Unique = True

    for sel in xsi.Selection:
        if sel.Type in ["root", "bone", "eff"]:
            if sel.Type == "root":
                chain_objects.Add(sel)
                chain_objects.AddItems(sel.Bones)
                chain_objects.Add(sel.Effector)
            else:
                chain_objects.Add(sel.Root)
                chain_objects.AddItems(sel.Root.Bones)
                chain_objects.Add(sel.Root.Effector)

    grid_data = PPG.PreviewGrid.Value
    grid_data.RowCount = chain_objects.Count

    for i in range(grid_data.RowCount):

        obj = chain_objects(i)
        new_name = renameChain(PPG, obj)

        grid_data.SetRowLabel(i, "  "+str(i)+"  ")
        grid_data.SetRowValues(i, [obj.Model.FullName, obj.FullName[obj.FullName.find(".")+1:], new_name])

        setRowColor(grid_data, i)

    PPG.Refresh()

# ========================================================
def gear_Renamer_Apply_OnClicked():

    grid_data = PPG.PreviewGrid.Value

    if grid_data.RowCount:
        for i in range(grid_data.RowCount):

            row_values = grid_data.GetRowValues(i)

            obj = xsi.Dictionary.GetObject(row_values[0]+"."+row_values[1])
            obj.Name = row_values[2]

            if PPG.EditMode.Value == 3:
                if obj.Type == "root":
                    obj.primary_icon.Value = PPG.rootIcon.Value
                if obj.Type == "eff":
                    obj.primary_icon.Value = PPG.effIcon.Value

                obj.size.Value = PPG.size.Value

    else:
        for i in range(xsi.Selection.Count):

            sel = xsi.Selection(i)
            sel.Name = rename(PPG, sel.Name,i)

    grid_data.RowCount = 0

    PPG.Refresh()

##########################################################
# MISC
##########################################################
# ========================================================
def rename(PPG, name, i):

    if PPG.UseSearchReplace.Value:

        # Simple Mode ------------------------------------------------------
        if PPG.EditMode.Value == 0 and PPG.Search.Value != "":
            name = name.replace(PPG.Search.Value, PPG.Replace.Value)

        # Regular Expression ----------------------------------------------
        elif PPG.EditMode.Value == 1 and PPG.Search.Value != "":
            name = re.sub(PPG.Search.Value, PPG.Replace.Value, name)

        # Serialize --------------------------------------------------------
        elif PPG.EditMode.Value == 2:

            index = (i * PPG.step.Value) + PPG.start.Value

            # Use Letter
            if PPG.UseLetters.Value:

                if PPG.UpperCase.Value:
                    alphabet = UPPER_ALPHABET
                else:
                    alphabet = LOWER_ALPHABET

                if (index/26) > 0:
                    letter = alphabet[index/26]+alphabet[index%26]
                else:
                    letter = alphabet[index%26]

                while len(letter) < PPG.Replace.Value.count("#"):
                    letter = alphabet[0]+letter

                name = re.sub("#+", letter, PPG.Replace.Value)

            # Use Digit
            else:
                digit = str(index)
                while len(digit) < PPG.Replace.Value.count("#"):
                    digit = "0"+digit
                name = re.sub("#+", digit, PPG.Replace.Value)

    if PPG.AddPrefix.Value:
        name = PPG.Prefix.Value + name

    if PPG.AddSuffix.Value:
        name += PPG.Suffix.Value

    return string.normalize(name)

# ========================================================
def renameChain(PPG, obj):

    prop = PPG.Inspected(0)

    suffix = prop.Parameters(obj.Type+"Suffix").Value

    name = PPG.replace.Value+"_"+suffix

    if obj.Type == "bone":

        padding = len(str(obj.Root.Bones.Count-1))

        for i, bone in enumerate(obj.Root.Bones):
            if bone.IsEqualTo(obj):
                index = i

        name = re.sub("#", "%0"+str(padding)+"i", name)
        name = name%index

    return string.normalize(name)

# ========================================================
def setRowColor(grid_data, i):

    color_grey  = [170,170,170,0] # unchanged
    color_green = [100,225,150,0] # valid
    color_red   = [200,50,50,0]   # invalid (object already exist in the scene)

    row_values = grid_data.GetRowValues(i)

    if row_values[1] == row_values[2]:
        color = setColor(grid_data.GetRowBackgroundColor(i), color_grey)
    else:
        if xsi.Dictionary.GetObject(row_values[0]+"."+row_values[2], False):
            color = setColor(grid_data.GetRowBackgroundColor(i), color_red)
        else:
            isvalid = True
            for j in range(grid_data.RowCount):
                if j == i:
                    continue
                elif row_values[2] == grid_data.GetRowValues(j)[2]:
                    isvalid = False
                    break

            if isvalid:
                color = setColor(grid_data.GetRowBackgroundColor(i), color_green)
            else:
                color = setColor(grid_data.GetRowBackgroundColor(i), color_red)

    grid_data.SetRowBackgroundColor(i, color)

# ========================================================
def setColor(color, color_array):

    color.Red   = color_array[0]
    color.Green = color_array[1]
    color.Blue  = color_array[2]
    color.Alpha = color_array[3]

    return color




