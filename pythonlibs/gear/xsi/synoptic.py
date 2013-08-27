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

## @package gear.xsi.synoptic
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import re

# gear
import gear
from gear.xsi import xsi, c, XSIFactory

import gear.xsi.animation as ani
import gear.xsi.display as dis

# constants
SYNOPTIC_NAME = "gear_Synoptic"
CTRL_GRP_PREFIX = "controlers_"
QUICKSEL_PARAM_PREFIX = "QuickSel_"
RESET_ACTION_NAME = "reset"
INFO_PROP_NAME = "info"
GLOBAL_CTL_NAME = "global_C0_ctl"
OGL_PARAM_NAME = "oglLevel"

##########################################################
# SELECT
##########################################################
# ========================================================
## Select object by name, according to mouse/key combo
# @param in_mousebutton Integer - 0 Left, 1 Middle, 2 Right
# @param in_keymodifier Integer - See source for information
# @param name String - object name to select
def select(in_mousebutton, in_keymodifier, name=None):

    model = getModel()

    if name is None:
        ctl = model
    else:
        ctl = model.FindChild(name)

    # Check if the object exists
    if not ctl:
        gear.log("Can't Find object : " + name, gear.sev_warning)
        return

    # Create Collection for different selection mode
    controlers = XSIFactory.CreateObject("XSI.Collection")

    # Mouse button ======================================
    # Left Clic - Simple select
    if in_mousebutton == 0:
        controlers.Add(ctl)

    # Middle Clic - Select in 'branch'
    elif in_mousebutton == 1:
        controlers.Add(ctl)

        # Get all controlers of the model
        controlers_filtered = []
        for group in getControlersGroups():
            controlers_filtered.extend(group.Members.GetAsText().split(","))

        # First Method, Try to find controlers of the same 'kind'
        # Find controler index
        has_index = False
        sIndex = re.search("[0-9]+_ctl$", ctl.Name)
        if sIndex:
            index = int(sIndex.group(0)[:-4])
            has_index = True

        # Try to find child of the same 'type'
        if has_index and controlers_filtered:
            while True:
                index += 1
                next_name = re.sub("[0-9]+_ctl$", str(index)+"_ctl", ctl.Name)

                if model.Name+"."+next_name not in controlers_filtered:
                    break

                controlers.Add(model.FindChild(next_name))

        # Second Method if no child found
        # we get all controlers children of selected one
        if controlers.Count == 1 and controlers_filtered:
            for child in ctl.FindChildren():
                if child.FullName in controlers_filtered:
                    controlers.Add(child)

    # Right Clic - Do nothing
    elif in_mousebutton == 2:
        return

    # Key pressed =======================================
    if in_keymodifier == 0 : # No Key or No Valid Key
        xsi.SelectObj(controlers)
    elif in_keymodifier == 1 : # Shift    check the object isn't already selected
        try:
            xsi.AddToSelection(controlers)
        except:
            return
    elif in_keymodifier == 2 : # Ctrl
        xsi.ToggleSelection(controlers)
    elif in_keymodifier == 3 : # Shift+Ctrl
        xsi.RemoveFromSelection (controlers)
    elif in_keymodifier == 4 : # Alt
        xsi.SelectObj(controlers, "BRANCH", True)
    elif in_keymodifier == 5 : # Alt+Shift check the object isn't already selected
        try:
            xsi.AddToSelection(controlers, "BRANCH", True)
        except:
            return
    elif in_keymodifier == 6 : # Alt+Ctrl
        xsi.ToggleSelection(controlers, "BRANCH", True)
    elif in_keymodifier == 7 : # Alt+Shift+Ctrl
        xsi.RemoveFromSelection(controlers)

# ========================================================
## Select multiple object by name
# @param in_mousebutton Integer - 0 Left, 1 Middle, 2 Right
# @param in_keymodifier Integer - See source for information
# @param object_names String - object names to select
# @param exclude String - object names to exclude from selection select
def selectMulti(in_mousebutton, in_keymodifier, object_names, exclude=[]):

    # Right click - Do nothing
    if in_mousebutton == 2:
        return

    model = getModel()

    controlers = XSIFactory.CreateObject("XSI.Collection")

    # Get objects
    for name in object_names:
        children = model.FindChildren(name)
        if children.Count:
            controlers.AddItems(children)

    # Remove objects
    # As we can yuse symbol such as '*' in the name list we might need to filter the result
    for name in exclude:
        if model.Name+"."+name in controlers.GetAsText().split(","):
            controlers.RemoveItems(model.Name+"."+name)

    if not controlers.Count:
        gear.log("Can't Find Controlers : "+",".join(object_names), gear.sev_siError)
        return

    # Key pressed =======================================
    if in_keymodifier == 0 : # No Key or No Valid Key
        xsi.SelectObj(controlers)
    elif in_keymodifier == 1 : # Shift    check the object isn't already selected
        try:
            xsi.AddToSelection(controlers)
        except:
            return
    elif in_keymodifier == 2 : # Ctrl
        xsi.ToggleSelection(controlers)
    elif in_keymodifier == 3 : # Shift+Ctrl
        xsi.RemoveFromSelection (controlers)
    elif in_keymodifier == 4 : # Alt
        xsi.SelectObj(controlers, "BRANCH", True)
    elif in_keymodifier == 5 : # Alt+Shift check the object isn't already selected
        try:
            xsi.AddToSelection(controlers, "BRANCH", True)
        except:
            return
    elif in_keymodifier == 6 : # Alt+Ctrl
        xsi.ToggleSelection(controlers, "BRANCH", True)
    elif in_keymodifier == 7 : # Alt+Shift+Ctrl
        xsi.RemoveFromSelection(controlers)

# ========================================================
## Select all controlers according to filter
# @param in_mousebutton Integer - 0 Left, 1 Middle, 2 Right
# @param in_keymodifier Integer - See source for information
def selectAll(in_mousebutton, in_keymodifier):

    controlers = getAllControlers()
    if not controlers.Count:
        gear.log("Nothing to select", gear.sev_warning)
        return

    # Left and Middle click
    if in_mousebutton in [0, 1]:
        xsi.SelectObj(controlers)

    # Right click - Do nothing
    elif in_mousebutton == 2:
        return

# ========================================================
## Call or save quick selection preset
# @param in_mousebutton Integer - 0 Left, 1 Middle, 2 Right
# @param in_keymodifier Integer - See source for information
# @param port String - Name of the port to use
def quickSel(in_mousebutton, in_keymodifier, port="A"):

    synoptic_prop = getSynoptic()
    quickSel_param = synoptic_prop.Parameters(QUICKSEL_PARAM_PREFIX+port)

    # Left click - Call selection
    if in_mousebutton == 0:
        if quickSel_param.Value == "":
            xsi.DeselectAll()
        else:
            model = getModel()

            selection = [model.FindChild(name) for name in quickSel_param.Value.split(",") if model.FindChild(name)]
            xsi.SelectObj(selection)

    # Middle click - Save selection
    elif in_mousebutton == 1:
        selection = [obj.name for obj in xsi.Selection]
        quickSel_param.Value = ",".join(selection)

    # Right click - Do nothing
    elif in_mousebutton == 2:
        return

##########################################################
# RESET
##########################################################
# ========================================================
def resetSel(in_mousebutton, in_keymodifier):

    # Left and Middle click
    if in_mousebutton in [0, 1]:
        ani.applyAction(getModel(), RESET_ACTION_NAME, xsi.Selection)

    # Right click - Do nothing
    elif in_mousebutton == 2:
        return

# ========================================================
def resetAll(in_mousebutton, in_keymodifier):

    # Left and Middle click
    if in_mousebutton in [0, 1]:
        ani.applyAction(getModel(), RESET_ACTION_NAME)

    # Right click - Do nothing
    elif in_mousebutton == 2:
        return

    import gear
    gear.log("hello")

##########################################################
# KEY
##########################################################
# ========================================================
def keySel(in_mousebutton, in_keymodifier):

    # Left and Middle click
    if in_mousebutton in [0, 1]:
        ani.setKey()

    # Right click - Do nothing
    elif in_mousebutton == 2:
        return

# ========================================================
def keyMulti(in_mousebutton, in_keymodifier, object_names, exclude=[]):

    # Right click - Do nothing
    if in_mousebutton == 2:
        return

    model = getModel()

    # Get objects
    for name in object_names:
        children = model.FindChildren(name)
        if children.Count:
            controlers.AddItems(children)

    # Remove objects
    # As we can yuse symbol such as '*' in the name list we might need to filter the result
    for name in exclude:
        if model.Name+"."+name in controlers.GetAsText().split(","):
            controlers.RemoveItems(model.Name+"."+name)

    if not controlers.Count:
        gear.log("Can't Find Controlers : "+",".join(object_names), gear.sev_siError)
        return

    ani.setKey(controlers)

# ========================================================
def keyAll(in_mousebutton, in_keymodifier):

    controlers = getAllControlers()
    if not controlers.Count:
        gear.log("Nothing to key", gear.sev_warning)
        return

    # Left and Middle click
    if in_mousebutton in [0, 1]:
        ani.setKey(controlers)

    # Right click - Do nothing
    elif in_mousebutton == 2:
        return

# ========================================================
def mirrorSel(in_mousebutton, in_keymodifier):

    # Left and Middle click
    if in_mousebutton in [0, 1]:
        ani.mirror()

    # Right click - Do nothing
    elif in_mousebutton == 2:
        return

##########################################################
# SHOW
##########################################################
# ========================================================
def toggleGroupVisibility(in_mousebutton, in_keymodifier, group_name):

    # Right click - Do nothing
    if in_mousebutton == 2:
        return

    model = getModel()
    group = model.Groups(group_name)
    if group:
        dis.toggleGroupVisibility(group)

# ========================================================
def toggleDisplayParameter(in_mousebutton, in_keymodifier, param_name):

    # Right click - Do nothing
    if in_mousebutton == 2:
        return

    dis.toggleDisplayParameter(param_name)

# ========================================================
def selectOrInspect(in_mousebutton, in_keymodifier, ctl_name, prop_name, width=None, height=None):

    # Right click - Do nothing
    if in_mousebutton == 2:
        return

    elif in_mousebutton == 0: # Left click - Select only
        select(0, in_keymodifier, ctl_name)

    elif in_mousebutton == 1: # Middle click - Select and Inspect
        select(0, in_keymodifier, ctl_name)

        prop = xsi.Selection(0).Properties(prop_name)
        if not prop:
            gear.log("Can't find property", gear.sev_error)
            return

        dis.inspect(prop, width, height, -(width+145), 75)

# ========================================================
def smooth(in_mousebutton, in_keymodifier, level=0):

    # Right click - Do nothing
    if in_mousebutton == 2:
        return

    model = getModel()
    global_ctl = model.FindChild(GLOBAL_CTL_NAME)
    if not global_ctl:
        return
    anim_prop = global_ctl.Properties("anim_prop")
    if not anim_prop:
        return

    anim_prop.Parameters(OGL_PARAM_NAME).Value = level

##########################################################
# GET
##########################################################
# ========================================================
## Return the synoptic property.
# @return Property
def getSynoptic():
    return xsi.ActiveSceneRoot.Properties(SYNOPTIC_NAME)

# ========================================================
## Return the current active model.
# @return Model
def getModel():
    model_name = getSynoptic().Parameters("Model").Value
    return xsi.ActiveSceneRoot.FindChild(model_name, c.siModelType)

# ========================================================
## return a list of controlers groups.
# @return List of Group
def getControlersGroups():
    model = getModel()
    return [group for group in model.Groups if group.Name.startswith(CTRL_GRP_PREFIX)]

# ========================================================
## Return all the controlers according to filter.
# @return XSICollection
def getAllControlers():

    synoptic_prop = getSynoptic()

    controlers = XSIFactory.CreateObject("XSI.Collection")
    for group in getControlersGroups():
        if synoptic_prop.Parameters(group.Name) and synoptic_prop.Parameters(group.Name).Value:
            controlers.AddItems(group.Members)

    return controlers