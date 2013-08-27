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

## @package gear.xsi.rig.utils
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import gear
from gear.xsi import xsi, c, dynDispatch, XSIFactory, XSIMath

import gear.xsi.uitoolkit as uit
import gear.xsi.xmldom as xmldom

XRIG_ORG_NAME = "xrig_org"
XRIG_PROP_NAME = "infos"

##########################################################
# XTRA RIG
##########################################################
def createXtraRig(model):
    return

    xrig_org = model.FindChild(XRIG_ORG_NAME)
    if xrig_org:
        uit.msgBox("There is already a %s null on this model"%XRIG_ORG_NAME, c.siMsgExclamation, "Xtra Rig Creation Failed")
        return xtra_org

    # Create xtra rig root null
    xrig_org = model.AddNull(XRIG_ORG_NAME)
    xrig_anim_prop = xrig_org.Properties("anim_prop")
    xrig_setup_prop = xrig_org.Properties("setup_prop")

    # Add null to group
    hidden_grp = model.Group("hidden_grp")
    if hidden_grp:
        hidden.grp.AddMember(xrig_org)

    return xrig_org

##########################################################
# IMPORT
##########################################################
def importXtraRig(path, model):
    return

    # Check Input
    if not os.path.exists(path):
        gear.log("Invalid File", gear.sev_error)
        return

    # Import
    xrig_model = xsi.ImportModel(path, xsi.ActiveSceneRoot, False, None, model.Name+"_xrig")(1)
    xrig_org = xrig_model.FindChild(XRIG_ORG_NAME)
    xrig_prop = xrig_model.Properties(XRIG_PROP_NAME)
    xrig_cns = xrig_prop.Parameters("constraints").Value
    if not xrig_org or xrig_prop:
        gear.log("This is not a valid Extra Rig Model", gear.sev_error)
        xsi.DeleteObj("B:"+xrig_model.Name)
        return

    # Merging rig
    model.AddChild(xrig_org)

    # Retrieve Groups
    for xrig_group in xrig_model.Groups:
        group = model.Groups(xrig_group.Name)
        if not group:
            group = model.AddGroup(None, xrig_group.Name)
        group.AddMember(xrig_group.Members)

    xsi.DeleteObj("B:"+xrig_model.Name)

    ## TODO : IMPORT CONSTRAINT !!!
    ## TODO : IMPORT PARAMETERS AND CONNECTION !!!
    '''
    # Reconnect Controls
    oExtraControls = oExtraRig.Properties("anim_ctrl")
    oAnimCtrl = dynDispatch(oModel.Properties("anim_ctrl"))
    aSkipParameters = ["Debug", "Layout", "Logic", "LayoutLanguage"]
    for oParam in oExtraControls.Parameters:
        if oParam.Name in aSkipParameters:
            continue
        oAnimCtrl.AddProxyParameter(oParam, oParam.Name, oParam.Name)

    # Layout
    sLayout = "\r\noLayout.AddTab('ExtraRig');\r\n" + oExtraControls.Parameters("Layout").Value
    oAnimCtrl.Parameters("Layout").Value += sLayout

    # Retrive Constrains
    sXmlPath = sPath.replace(".emdl", ".xml")
    if os.path.exists(sXmlPath):
        xsi.gImportSkin(oExtraRig.Children, sXmlPath, True)
    '''

    return

##########################################################
# EXPORT
##########################################################
def exportXtraRig(path, model):
    return

    # Check Input
    if not os.path.exists(path):
        gear.log("Invalid File", gear.sev_error)
        return

    xrig_org = xrig_model.FindChild(XRIG_ORG_NAME)
    if not xrig_org or xrig_prop:
        gear.log("This is not a valid Extra Rig Model", gear.sev_error)
        xsi.DeleteObj("B:"+xrig_model.Name)
        return

    # Create New Extra Rig Model
    xrig_model = model.AddModel(xrig_org, model.Name+"_xrig")

    # Groups
    for child in xrig_model.FindChildren():
        for group in model.Groups:
            if group.IsMember(child):
                xrig_group = xrig_model.Groups(group.Name)
                if not xrig_model.Groups(group.Name):
                    xrig_group = xrig_model.AddGroup(None, group.Name)
                xrig_group.AddMember(child)

    ## TODO : EXPORT CONSTRAINT !!!

    xrig_prop = xrig_model.AddProperty("Custom Property", False, XRIG_PROP_NAME)
    pCns = xrig_prop.AddParameter3("constraints", c.siString, "")

    '''
    xmldom.setOptions("X3DObject_children":False,
                      "X3DObject_primitive":False,
                      "X3DObject_kinematics":True,
                      "X3DObject_properties":False)
    '''

    ## TODO : EXPORT PARAMETERS AND CONNECTIONS !!!

    # Export Model
    xsi.ExportModel(xrig_model, path)

    # Restore rig
    model.AddChild(xrig_org)
    xsi.DeleteObj("B:"+xrig_model.FullName)