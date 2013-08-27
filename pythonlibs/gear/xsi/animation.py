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

## @package gear.xsi.animation
# @author Jeremie Passerin
#
# @brief xsi animation methods, keys, mirror animation, apply action...
# test

##########################################################
# GLOBAL
##########################################################

# gear
import gear

from gear.xsi import xsi, c, XSIFactory
import gear.xsi.uitoolkit as uit
import gear.xsi.utils as uti
import gear.xsi.fcurve as fcu
import gear.xsi.parameter as par
import gear.xsi.mixer as mix

# Constants
MIRROR_PROP_NAME = "mirror_cnx"

##########################################################
# KEYS
##########################################################
# ========================================================
## Return a collection of keyable parameters for input objects
# @param in_controlers XSICollection
# @return XSICollection of Parameters
def getKeyableParameters(in_controlers):

    # We make sure input is a collection (next method doesn't work with selection)
    controlers = XSIFactory.CreateObject("XSI.Collection")
    controlers.AddItems(in_controlers)
    return controlers.FindObjectsByMarkingAndCapabilities(None, 2048)

# ========================================================
## Set a key on keyable parameters for given controler at current keyable frame
# @param controlers an XSI Collection of controler, if None, current selection is used
# @return true if the controlers has been succefully keyed
def setKey(controlers=xsi.Selection):

    if not controlers.Count:
        uit.msgBox("Nothing selected", c.siMsgExclamation, "Key Selection Failed")
        return False

    keyable_params = getKeyableParameters(controlers)
    if not keyable_params.Count:
        uit.msgBox("There is no keyable parameter on selection", c.siMsgExclamation, "Key Selection Failed")
        return False

    # Save Key
    playcontrol = xsi.GetValue("PlayControl")

    # Some Keyable display parameters (id) can be in the list, we need to remove them
    # or some parameters with expression on them
    itemsToRemove = XSIFactory.CreateObject("XSI.Collection")
    for param in keyable_params:
        if not param.Animatable or param.isAnimated(c.siExpressionSource):
            itemsToRemove.Add(param)

    if itemsToRemove.Count:
        keyable_params.RemoveItems(itemsToRemove)

    xsi.SaveKey(keyable_params, playcontrol.Parameters("Key").Value)

    return True

##########################################################
# MIRROR
##########################################################
# ========================================================
## Create the mirror connection template
# @param model Model - Model to add the template to
# @param in_controlers XSICollection - Controlers to add to the template
# @return Grid
def createMirrorCnxTemplate(model, in_controlers=None):

    cnx_prop = model.Properties(MIRROR_PROP_NAME)
    if not cnx_prop:
        cnx_prop = model.AddProperty("gear_Mirror", False, MIRROR_PROP_NAME)
        cnx_grid = cnx_prop.Parameters("CnxGridHidden").Value
        connections = par.getDictFromGridData(cnx_grid)

    if in_controlers is not None:
        
        controlers = XSIFactory.CreateObject("XSI.Collection")
        controlers.AddItems(in_controlers)

        cnx_grid.BeginEdit()

        pbar = uit.progressBar(controlers.Count, 1, "Creating Mirror Template", "", False)

        # Adding selected controlers to Connection map
        for ctl in controlers:
            pbar.StatusText = ctl.Name
            connections = addMirroringRule(ctl, cnx_grid, connections)
            pbar.Increment()

        pbar.Visible = False

        par.setDataGridFromDict(cnx_grid, connections)
        cnx_prop.Parameters("Count").Value = len(connections)

        cnx_grid.EndEdit()

    return cnx_grid

# ========================================================
## Adding a mirroring rul to the connection grid for given controlers
# @param ctl X3DObject - Controler to add to the mirroring template
# @param cnx_grid Grid - The connection grid
# @param inversed_params List of String - List of the fullname of parameters to inverse
# @param delUnused Boolean - True to remove rules that mirror to themself
# @return Dictionary - Connections
def addMirroringRule(ctl, cnx_grid, inversed_params=[], delUnused=False):

    model = ctl.Model

    # I want to get all the keyable parameters for this object and the easiest way
    # is to use the FindObjectsByMarkingAndCapabilities() method
    # but it only applies on collection
    controlers = XSIFactory.CreateObject("XSI.Collection")
    controlers.Add(ctl)
    key_params = controlers.FindObjectsByMarkingAndCapabilities(None, 2048)

    # try to find the mirror object
    mirror_ctl = model.FindChild(uti.convertRLName(ctl.Name))
    
    connections = par.getDictFromGridData(cnx_grid)

    for param in key_params:

        # Skip marking set to avoid having all the params twice
        if param.Parent.Name == "MarkingSet" or param.Parent.Name.startswith("DisplayInfo"):
            continue

        fullName = param.FullName[param.FullName.find(".")+1:]

        # If the object mirror on itself, try to find R and L parameters
        if not mirror_ctl or mirror_ctl.IsEqualTo(ctl):
            mirror_param = param.Parent.Parameters(uti.convertRLName(param.Name))
            if mirror_param:
                mirror_fullName = mirror_param.FullName[mirror_param.FullName.find(".")+1:]
            else:
                mirror_fullName = fullName
        else:
            mirror_fullName = fullName.replace(ctl.Name, mirror_ctl.Name)

        if delUnused and (fullName == mirror_fullName and not param.FullName in inversed_params):
            continue
            
        connections[fullName] = [mirror_fullName, param.FullName in inversed_params]
        
    par.setDataGridFromDict(cnx_grid, connections)

    return connections

# ========================================================
## Transfer the pose/animation of givben controlers according to the rules define in the connection template
# @param controlers XSICollection - Controlers to mirror
# @param animation Boolean - True to mirror the FCurve and not only the static value
# @param frame_offset Integer - Offset original animation
# @param considerTime Boolean - True to use the in and out frame
# @param frame_in Integer - Start frame of animation to mirror
# @param frame_out Integer - End frame of animation to mirror
def mirror(controlers=xsi.Selection, animation=False, frame_offset=0, considerTime=False, frame_in=0, frame_out=0):

    if not animation:
        source_type = 1
        considerTime = False
        frame_offset = 0
    else:
        source_type = 6

    params = getKeyableParameters(controlers)

    # Avoid having the parameter and its proxy in the collection
    # Curiosly, XSI can store the fcurves of the parameter and its proxy separatly
    # We get weird result when applying the action
    key_params = XSIFactory.CreateObject("XSI.Collection")
    key_params.Unique = True
    for param in params:
        if param.Type == "ProxyParameter":
            key_params.Add(param.MasterParameter)
        else:
            key_params.Add(param)

    if not key_params.Count:
        gear.log("No Keyable Parameter on Selection", gear.sev_error)
        return

    # Get all keys if considerTime is False
    if not considerTime and animation:
        frame_in, frame_out = fcu.getFirstAndLastKey(controlers)

    # Get Connexion Map --------------------
    model = controlers(0).Model
    cnx_prop = model.Properties(MIRROR_PROP_NAME)
    if not cnx_prop:
        gear.log("There is no Mirror Cnx Template on this model", gear.sev_error)
        return

    cnx_grid = cnx_prop.Parameters("CnxGridHidden").Value
    connections = par.getDictFromGridData(cnx_grid)

    # Actions ------------------------------
    # Store the Action
    if model.Sources("Temp_MirrorAction"):
        xsi.DeleteObj(model.Sources("Temp_MirrorAction"))

    action = xsi.StoreAction(model, key_params, source_type, "Temp_MirrorAction", False, frame_in, frame_out, considerTime, False, False, False)

    # Edit the stored Action
    for item in action.SourceItems:

        # skip sourceItems if not listed in the CnxMap
        if item.Target not in connections:
            continue

        # Change the target to mirror action
        target = connections[item.Target]
        item.Target = target[0]

        # Inverse the value of fcurve if necessary
        # The string version is to keep compatibility with previous version of XSI
        # When the gridata was only returning string
        if target[1] in [True, "True"]:
            invertSource(item.Source)

    xsi.ApplyAction(action, model, True, frame_in+frame_offset, frame_out+frame_offset, False)
    xsi.DeleteObj(action)

    return

# ========================================================
## Inverse the source value
# @param source 
def invertSource(source):

    if source.Type == 20:

        for key in source.Keys:

            key.value = - key.value
            if key.Index == 0:
                key.RightTanY = - key.RightTanY
            elif key.Index == source.Keys.Count:
                key.LeftTanY = - key.LeftTanY
            else:
                key.LeftTanY = - key.LeftTanY
                if key.Constraint(c.siG1ContinuousConstraint) == False:
                    key.RightTanY = - key.RightTanY

    elif source.Type == "StaticSource":
        source.Value = - source.Value

##########################################################
# ACTION
##########################################################
## Apply action to model for given controlers
# @param model Model - model to apply the action to
# @param action_name String - Name of the action to apply
# @controlers XSICollection - Controlers to apply the action to (None, to apply to all)
def applyAction(model, action_name, controlers=None):

    mixer = mix.Mixer(model)

    if action_name not in mixer.animSources.keys():
        gear.log("Can't find action : "+action_name, gear.sev_error)

    action = mixer.animSources[action_name].value

    if controlers is not None:
        keyable_params = [param.FullName for param in getKeyableParameters(controlers)]
        import gear
        gear.log(keyable_params)

        for item in action.SourceItems:
            if model.FullName+"."+item.Target in keyable_params:
                item.Active = True
            else:
                item.Active = False
    else:
        for item in action.SourceItems:
            item.Active = True

    xsi.ApplyAction(action, model)

##########################################################
# PLAYCONTROL
##########################################################
## Class to easily access the playcontrol object inside XSI
class PlayControl(object):

    def __init__(self):

        playcontrol = xsi.GetValue("PlayControl")

        self.current   = playcontrol.Parameters("Current")
        self.globalIn  = playcontrol.Parameters("GlobalIn")
        self.localIn   = playcontrol.Parameters("In")
        self.globalOut = playcontrol.Parameters("GlobalOut")
        self.localOut  = playcontrol.Parameters("Out")
        self.key       = playcontrol.Parameters("Key")

