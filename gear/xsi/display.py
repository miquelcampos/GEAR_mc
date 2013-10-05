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

## @package gear.xsi.display
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import time

# gear
import gear
import gear.screen as scr
from gear.xsi import xsi, c, XSIFactory, dynDispatch

##########################################################
# INSPECT
##########################################################
# ========================================================
## Open a property inside XSI using the Create View, Property Panel
## Allows you to define size and position on the screen
# @param prop Property - Property to display
# @param width Integer - Width of the created window
# @param height Integer - Height of the created window
# @param posx Integer - Position X of the created window (use negative value to position from the right side of the screen)
# @param posy Integer - Position Y of the created window (use negative value to position from the bottom of the screen)
def inspect(prop, width=None, height=None, posx=None, posy=None):

    # If no size define we just do a simple inspect obj
    if width is None or height is None:
        xsi.InspectObj(prop)
        return

    # Get the screen resolution to position the window
    screen_width, screen_height = scr.getResolution()

    if posx is None:
        posx = int((screen_width / 2.0) - (width / 2.0))
    elif posx < 0:
        posx = int(screen_width + posx)

    if posy is None:
        posy = int((screen_height / 2.0) - (height / 2.0))
    elif posy < 0:
        posy = int(screen_height + posy)


    view = xsi.Desktop.ActiveLayout.CreateView("Property Panel", prop.Name)

    view.BeginEdit()

    view.Move(posx, posy)
    view.Resize(width, height)
    view.SetAttributeValue("targetcontent", prop.FullName)

    view.EndEdit()

##########################################################
# HIGHLIGHT
##########################################################
# ========================================================
## Highlight an object inside the 3D view byu turning it's color to bright green for just a second
# @param obj X3DObject - Object to highlight
# @param branch Boolean - True to highlight all the children of given object
def highlight(obj, branch=True):

    # save selection in order to retrieve it at the end
    selection = XSIFactory.CreateObject("XSI.Collection")
    selection.AddItems(xsi.Selection)

    pref = xsi.Dictionary.GetObject("Preferences")
    scene_color = dynDispatch(pref.NestedObjects("Scene Colors"))
    sel_color = scene_color.Parameters("selcol")
    inh_color = scene_color.Parameters("inhcol")

    selColor_value = sel_color.Value
    inhColor_value = inh_color.Value
    sel_color.Value = 16712703
    inh_color.Value = 16712703

    if branch:
        mode = "BRANCH"
    else:
        mode = "ASITIS"

    xsi.SelectObj(obj, mode)
    xsi.Refresh()
    time.sleep(.2)
    sel_color.Value = selColor_value
    inh_color.Value = inhColor_value

    # Retrieve selection
    xsi.SelectObj(selection)

##########################################################
# VISIBILITY
##########################################################
# ========================================================
## Toggle the visibility parameter value of a group
# @param group Group - Group to toggle
def toggleGroupVisibility(group):

    prop = group.Properties("Visibility")

    if prop:
        param = prop.Parameters("viewvis")
        group.Parameters("viewvis").Value = 2
        param.Value = not param.Value

    else:
        if group.Parameters("viewvis").Value == 0:
            group.Parameters("viewvis").Value = 2
        else :
            group.Parameters("viewvis").Value = 0

    xsi.Refresh()

# ========================================================
## Toggle the Display parameter value for active camera
# @param param_name String - Name of the parameter to toggle
def toggleDisplayParameter(param_name):

    # The Toogle is made on the view that got the focus
    cam_name = getActiveCamera()
    if not cam_name:
        XSIUIToolkit.Msgbox("There is no 'View Manager' in current layout.", c.siMsgExclamation, "Failed")
        return

    xsi.ToggleValue("camdisp."+param_name, cam_name)
    xsi.SetValue(cam_name+".camvis.custominfoproxynames", True, None)

##########################################################
# COLORS
##########################################################
# ========================================================
## Create a Display Property on the object and set the wirecolor.
# @param obj X3DObject - Object.
# @param color List of Double - The RGB color of the object wireframe (ie. [1,0,0] for red).
# @return Property - The newly created display property.
def setColor(obj, color=[0,0,0]):

    disp_prop = obj.AddProperty("Display Property")
    disp_prop.wirecolorr.Value = color[0]
    disp_prop.wirecolorg.Value = color[1]
    disp_prop.wirecolorb.Value = color[2]

    return disp_prop

# ========================================================
## Return the wireframecolor of the object.
# @param obj X3DObject - Object.
# @return List of Double - The RGB color of the object wireframe (ie. [1,0,0] for red).
def getColor(obj):

    color = [0] * 3   
    disp_prop = obj.Properties("display")
    color[0] = disp_prop.Parameters("wirecolorr").Value
    color[1] = disp_prop.Parameters("wirecolorg").Value
    color[2] = disp_prop.Parameters("wirecolorb").Value
    
    return color    
    
##########################################################
# CAMERA
##########################################################
# ========================================================
## Return the active camera inside the 3DView
# @return String - Camera name
def getActiveCamera():

    vm = False
    for view in xsi.Desktop.ActiveLayout.Views:
        if view.type == "View Manager":
            vm = view

    if not vm:
        return False

    focus = vm.GetAttributeValue("focusedviewport")
    camera = vm.GetAttributeValue("activecamera:" + focus)

    if camera == "Front" or camera == "Right" or camera == "Top" or camera == "User":
        cam_name = "Views.View"+focus+"."+camera+"Camera"
    else:
        cam_name = camera

    return cam_name
