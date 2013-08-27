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

## @package gear.xsi.rig.guide
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import os
import datetime
import getpass
import xml.etree.cElementTree as etree

# gear
import gear
import gear.xmldom as xmldom
from gear.xsi import xsi, c, XSIFactory, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.utils as uti
import gear.xsi.uitoolkit as uit
import gear.xsi.parameter as par
import gear.xsi.ppg as ppg
import gear.xsi.xmldom as xsixmldom
import gear.xsi.vector as vec
import gear.xsi.primitive as pri

COMPONENT_PATH = os.path.join(os.path.dirname(__file__), "component")
TEMPLATE_PATH = os.path.join(COMPONENT_PATH, "templates")
VERSION = 1.0

##########################################################
# GUIDE
##########################################################
## The main guide class.\n
# Provide the methods to add parameters, set parameter values, create property...
class MainGuide(object):

    def __init__(self):

        # Parameters names, definition and values.
        self.paramNames = [] ## List of parameter name cause it's actually important to keep them sorted.
        self.paramDefs = {} ## Dictionary of parameter definition.
        self.values = {} ## Dictionary of options values.

        # Property layout and logic
        self.layout = ppg.PPGLayout() ## PPGLayout object.
        self.logic = ppg.PPGLogic() ## PPGLogic object.

        # We will check a few things and make sure the guide we are loading is up to date.
        # If parameters or object are missing a warning message will be display and the guide should be updated.
        self.valid = True

    # ====================================================
    # GUIDE PROPERTY, LAYOUT AND LOGIC

    ## Add more parameter to the parameter definition list.
    # REIMPLEMENT. This method should be reimplemented in each guide.
    # @param self
    def addParameters(self):
        return

    ## Add layout for new parameters.
    # REIMPLEMENT. This method should be reimplemented in each guide.
    # @param self
    def addLayout(self):
        return

    ## Add logic for new layout.
    # REIMPLEMENT. This method should be reimplemented in each guide.
    # @param self
    def addLogic(self):
        return

    # ====================================================
    # PROPERTY AND PARAMETERS

    ## Add a property (sn_PSet) with all the parameters from the parameter definition list.
    # @param self
    # @param parent X3DObject - The parent of the property.
    # @param name String - Name of the new property.
    # @ return Property - The newly created property.
    def addProperty(self, parent, name):

        prop = parent.AddProperty("gear_PSet", False, name)

        # Creating the parameter in the right order is actually very important to display Color widget :(
        for scriptName in self.paramNames:
            paramDef = self.paramDefs[scriptName]
            paramDef.create(prop)

        prop.Parameters("layout").Value = self.layout.getValue()
        prop.Parameters("logic").Value = self.logic.getValue()

        return prop

    def getParametersAsXml(self, name, prop=None):

        xml_prop = etree.Element(name)
        for scriptName, paramDef in self.paramDefs.items():
            xml_prop.append(paramDef.getAsXml(True))

        # Adding unregistered parameters
        if prop:
            for param in prop.Parameters:
                if param.ScriptName not in self.values.keys() and param.ScriptName not in ["layout, logic, debug"]:
                    xParam = xsixmldom.Parameters(param)
                    xml_prop.append(xParam.xml)

        return xml_prop

    # ----------------------------------------------------
    # Set Parameters values

    ## Set the value of parameter with matching scriptname.
    # @param self
    # @param scriptName String - Scriptname of the parameter to edit.
    # @param value Variant - New value.
    # @return Boolean - False if the parameter wasn't found.
    def setParamDefValue(self, scriptName, value):

        if not scriptName in self.paramDefs.keys():
            gear.log("Can't find parameter definition for : " + scriptName, gear.sev_warning)
            return False

        self.paramDefs[scriptName].value = value
        self.values[scriptName] = value

        return True

    ## Set the parameter values from given property.
    # @param self
    # @param prop Property - The property to parse.
    def setParamDefValuesFromProperty(self, prop):

        for scriptName, paramDef in self.paramDefs.items():
            param = prop.Parameters(scriptName)
            if not param:
                gear.log("Can't find parameter '%s' in %s"%(scriptName, prop.FullName), gear.sev_warning)
                self.valid = False
            else:
                if str(param.Value) == "FCurve":
                    paramDef.setFromFCurve(param.Value)
                    self.values[scriptName] = paramDef
                else:
                    paramDef.value = param.Value
                    self.values[scriptName] = param.Value

        # Adding unregistered parameters
#        for param in prop.Parameters:
#            if param.ScriptName not in self.values.keys() and param.ScriptName not in ["layout, logic, debug"]:
#                self.values[param.ScriptName] = param.Value

    ## Set the parameter values from given xml defintion.
    # @param self
    # @param xml_root xml_node - The xml definition to parse.
    def setParamDefValuesFromXml(self, xml_prop):

        for scriptName, paramDef in self.paramDefs.items():
            xml_param = xmldom.findChildByAttribute(xml_prop, "parameter", "scriptName", scriptName)
            if xml_param is not None:
                paramDef.value = par.convertVariantType(xml_param.get("value"), xml_param.get("valueType"))
                self.values[scriptName] = paramDef.value
            else:
                xml_param = xmldom.findChildByAttribute(xml_prop, "fcurveparameter", "scriptName", scriptName)
                if xml_param is not None:
                    paramDef.setFromXml(xml_param)
                    self.values[scriptName] = paramDef

        # Adding unregistered parameters
#        for xml_param in xml_prop.findall("parameters"):
#            scriptName = xml_param.get("ScriptName")
#            if scriptName not in self.values.keys() and scriptName not in ["layout, logic, debug"]:
#                self.values[scriptName] = par.convertVariantType(xml_param.get("value"), xml_param.get("valueType"))

    # ----------------------------------------------------
    # Add Parameters

    ## Add a paramDef to the list.\n
    # Note that animatable and keyable are false per default.
    # @param self
    # @param scriptName String - Parameter scriptname.
    # @param valueType Integer - siVariantType.
    # @param value Variant - Default parameter value.
    # @param minimum Variant - mininum value.
    # @param maximum Variant - maximum value.
    # @param sugMinimum Variant - suggested mininum value.
    # @param sugMaximum Variant - suggested maximum value.
    # @param animatable Boolean - True to make parameter animatable.
    # @param readOnly Boolean - True to make parameter readOnly.
    # @param keyable Boolean - True to make parameter keyable.
    # @return ParamDef - The newly created parameter definition.
    def addParam(self, scriptName, valueType, value, minimum=None, maximum=None, sugMinimum=None, sugMaximum=None, animatable=False, readOnly=False, keyable=False):

        capabilities = 1 * animatable + 2 * readOnly + 4 + 2048 * keyable
        paramDef = par.ParamDef2(scriptName, valueType, value, minimum, maximum, sugMinimum, sugMaximum, c.siClassifUnknown, capabilities)
        self.paramDefs[scriptName] = paramDef
        self.values[scriptName] = value
        self.paramNames.append(scriptName)

        return paramDef

    ## Add a paramDef to the list.\n
    # Note that animatable and keyable are false per default.
    # @param self
    # @param scriptName String - Parameter scriptname.
    # @return FCurveParamDef - The newly created parameter definition.
    def addFCurveParam(self, scriptName, keys, interpolation=c.siCubicInterpolation):

        paramDef = par.FCurveParamDef(scriptName, keys, interpolation)
        self.paramDefs[scriptName] = paramDef
        self.values[scriptName] = paramDef
        self.paramNames.append(scriptName)

        return paramDef

    ## Add the object to a group
    # @param self
    # @param objs Single or List of X3DObject - object to put in group
    # @param names Single or List of String - names of the groups to create
    def addToGroup(self, objects, names=["hidden"]):

        if objects is None or names is None:
            return

        if not isinstance(names, list):
            names = [names]

        if not isinstance(objects, list):
            objects = [objects]

        model = objects[0].Model

        for name in names:
            group = model.Groups(name+"_grp")
            if not group:
                group = model,AddGroup(None, name+"_grp")

            c = XSIFactory.CreateObject("XSI.Collection")
            c.AddItems(objects)
            group.AddMember(c)

##########################################################
# RIG GUIDE
##########################################################
## Rig guide class.\n
# This is the class for complete rig guide definition.\n
# It contains the component guide in correct hierarchy order and the options to generate the rig.\n
# Provide the methods to add more component, import/export guide.
class RigGuide(MainGuide):

    def __init__(self):

        # Parameters names, definition and values.
        self.paramNames = [] ## List of parameter name cause it's actually important to keep them sorted.
        self.paramDefs = {} ## Dictionary of parameter definition.
        self.values = {} ## Dictionary of options values.

        # Property layout and logic
        self.layout = ppg.PPGLayout() ## PPGLayout object.
        self.logic = ppg.PPGLogic() ## PPGLogic object.

        # We will check a few things and make sure the guide we are loading is up to date.
        # If parameters or object are missing a warning message will be display and the guide should be updated.
        self.valid = True

        self.controlers = {} ## Dictionary of controlers
        # Keys are the component fullname (ie. 'arm_L0')
        self.components = {} ## Dictionary of component
        self.componentsIndex = [] ## List of component name sorted by order creation (hierarchy order)
        self.parents = [] ## List of the parent of each component, in same order as self.components

        self.addParameters()
        self.addLayout()
        self.addLogic()

        self.plog = uit.ProgressLog(False, True)

    # =====================================================
    # PARAMETERS, LAYOUT AND LOGIC FOR RIG OPTIONS

    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        # --------------------------------------------------
        # Main Tab
        self.pRigName = self.addParam("rigName", c.siString, "rig")

        self.pMode = self.addParam("mode", c.siInt4, 0)

        self.pIsolateResult = self.addParam("isolateResult", c.siBool, False)
        self.pPopUp = self.addParam("popUpControls", c.siBool, False)
        self.pStep = self.addParam("step", c.siInt4, -1, -1, None)

        self.pSetHidden = self.addParam("setHidden", c.siBool, True)
        self.pSetDeformers = self.addParam("setDeformers", c.siBool, True)
        self.pSetUnselect = self.addParam("setUnselectable", c.siBool, True)
        self.pSetGeometries = self.addParam("setGeometries", c.siBool, True)

        # --------------------------------------------------
        # Colors
        self.pRColorfkr = self.addParam("R_color_fk_r", c.siDouble, 0, 0, 1)
        self.addParam("R_color_fk_g", c.siDouble, 0, 0, 1)
        self.addParam("R_color_fk_b", c.siDouble, .75, 0, 1)

        self.pRColorikr = self.addParam("R_color_ik_r", c.siDouble, 0, 0, 1)
        self.addParam("R_color_ik_g", c.siDouble, 0.5, 0, 1)
        self.addParam("R_color_ik_b", c.siDouble, .75, 0, 1)

        self.pCColorfkr = self.addParam("C_color_fk_r", c.siDouble, 0.5, 0, 1)
        self.addParam("C_color_fk_g", c.siDouble, 0, 0, 1)
        self.addParam("C_color_fk_b", c.siDouble, 0.5, 0, 1)

        self.pCColorikr = self.addParam("C_color_ik_r", c.siDouble, 0.75, 0, 1)
        self.addParam("C_color_ik_g", c.siDouble, 0.25, 0, 1)
        self.addParam("C_color_ik_b", c.siDouble, 0.75, 0, 1)

        self.pLColorfkr = self.addParam("L_color_fk_r", c.siDouble, .75, 0, 1)
        self.addParam("L_color_fk_g", c.siDouble, 0, 0, 1)
        self.addParam("L_color_fk_b", c.siDouble, 0, 0, 1)

        self.pLColorikr = self.addParam("L_color_ik_r", c.siDouble, .75, 0, 1)
        self.addParam("L_color_ik_g", c.siDouble, 0.5, 0, 1)
        self.addParam("L_color_ik_b", c.siDouble, 0, 0, 1)

        # --------------------------------------------------
        # Settings
        self.pInspectSettings = self.addParam("inspectSettings", c.siString, "")
        self.pShadowRig = self.addParam("shadowRig", c.siBool, False)
        self.pNegate = self.addParam("negate", c.siInt4, 0, 0, 2)

        # External
        self.pAddGeo    = self.addParam("addGeometry", c.siBool, False)
        self.pGeoPath  = self.addParam("geo_path", c.siString, "")
        self.pSkinPath = self.addParam("skin_path", c.siString, "")

        self.pAddXRig    = self.addParam("addXRig", c.siBool, False)
        self.pXRigPath = self.addParam("xrig_path", c.siString, "")

        # Synoptic
        self.pProdName = self.addParam("prod_name", c.siString, "_common")
        self.pSynopticList = self.addParam("synoptic_list", c.siString, "")
        self.pSynopticSelect = self.addParam("synoptic_select", c.siString, "")
        self.pSynoptic = self.addParam("synoptic", c.siString, "")

        # --------------------------------------------------
        # Comments
        self.pComments = self.addParam("comments", c.siString, "")

    ## Add layout for new parameters.
    # @param self
    def addLayout(self):

        # --------------------------------------------------
        # Items
        modeItems = ["Final", 0, "Wip", 1]
        stepItems = ["Run All", -1]
        for i, name in enumerate(MainComponent.steps):
            stepItems.append(name)
            stepItems.append(i)

        self.layout.setCodeBefore("import os" + "\r\n" \
                                 +"import gear.xsi.plugin as plu" + "\r\n" \
                                 +"import gear.xsi.rig.logic as logic")

        # Inspect component settings
        self.layout.setCodeAfter("inspect_items = logic.getInspectItems(PPG.Inspected(0).Model)" + "\r\n" \
                                +"layout.Item('" + self.pInspectSettings.scriptName + "').UIItems = inspect_items" + "\r\n" \
                                +"if not PPG." + self.pInspectSettings.scriptName + ".Value:" + "\r\n" \
                                +"    PPG." + self.pInspectSettings.scriptName + ".Value = inspect_items[1]")

        # Synoptic production names
        self.layout.setCodeAfter("prod_items = logic.getSynProdItems()" + "\r\n" \
                                +"layout.Item('" + self.pProdName.scriptName + "').UIItems = prod_items" + "\r\n" \
                                +"if not PPG." + self.pProdName.scriptName + ".Value:" + "\r\n" \
                                +"    PPG." + self.pProdName.scriptName + ".Value = prod_items[1]")

        # Available tabs
        self.layout.setCodeAfter("tab_items = logic.getSynTabItems(PPG." + self.pProdName.scriptName + ".Value)" + "\r\n" \
                                +"layout.Item('" + self.pSynopticList.scriptName + "').UIItems = tab_items" + "\r\n" \
                                +"if not PPG." + self.pSynopticList.scriptName + ".Value:" + "\r\n" \
                                +"    PPG." + self.pSynopticList.scriptName + ".Value = tab_items[1]")

        # Selected tabs
        self.layout.setCodeAfter("sel_items = logic.getSynSelItems(PPG."+self.pSynoptic.scriptName+".Value)" + "\r\n" \
                                +"layout.Item('" + self.pSynopticSelect.scriptName + "').UIItems = sel_items" + "\r\n" \
                                +"if not PPG." + self.pSynopticSelect.scriptName + ".Value and sel_items:" + "\r\n" \
                                +"    PPG." + self.pSynopticSelect.scriptName + ".Value = sel_items[1]")

        # --------------------------------------------------
        # Main Tab
        tab = self.layout.addTab("Main")

        group = tab.addGroup("Naming Convention")
        row = group.addRow()
        item = row.addItem(self.pRigName.scriptName, "Name")

        group = tab.addGroup("Build Mode")
        item = group.addEnumControl(self.pMode.scriptName, modeItems, "Mode", c.siControlCombo)

        group = tab.addGroup("Debug")
        group.addCondition("PPG."+self.pMode.scriptName+".Value != 0")
        item = group.addItem(self.pIsolateResult.scriptName, "Isolate Result")
        item = group.addItem(self.pPopUp.scriptName, "Pop Up Controls")
        item = group.addEnumControl(self.pStep.scriptName, stepItems, "Stop after step", c.siControlCombo)

        group = tab.addGroup("Set Group Values")
        group.addCondition("PPG."+self.pMode.scriptName+".Value != 0")
        item = group.addItem(self.pSetHidden.scriptName, "Hidden")
        item = group.addItem(self.pSetUnselect.scriptName, "Unselectable")
        item = group.addItem(self.pSetDeformers.scriptName, "Deformers")
        item = group.addItem(self.pSetGeometries.scriptName, "Geometries")

        # Colors ---------------------------------------------
        tab = self.layout.addTab("Colors")

        group = tab.addGroup("Right")
        item = group.addColor(self.pRColorfkr.scriptName, "FK")
        item = group.addColor(self.pRColorikr.scriptName, "IK")
        group = tab.addGroup("Center")
        item = group.addColor(self.pCColorfkr.scriptName, "FK")
        item = group.addColor(self.pCColorikr.scriptName, "IK")
        group = tab.addGroup("Left")
        item = group.addColor(self.pLColorfkr.scriptName, "FK")
        item = group.addColor(self.pLColorikr.scriptName, "IK")

        # Settings --------------------------------------------
        tab = self.layout.addTab("Settings")

        group = tab.addGroup("Rig Part Settings")
        row = group.addRow()
        item = row.addEnumControl(self.pInspectSettings.scriptName, [], "", c.siControlCombo)
        item.setAttribute(c.siUINoLabel, True)
        row.addButton("inspect", "Inspect")
        row.addButton("selectRoots", "Select Roots")

        group = tab.addGroup("Shadow")
        item = group.addItem(self.pShadowRig.scriptName, "Enable")

        # External
        group = tab.addGroup("Geometry")
        item = group.addItem(self.pAddGeo.scriptName, "Add Geometry")

        row = group.addRow()
        item = row.addEnumControl(self.pGeoPath.scriptName, [], "Geometry Path", c.siControlFilePath)
        item.addCondition("PPG."+self.pAddGeo.scriptName+".Value")
        item.setAttribute(c.siUIOpenFile, True)
        item.setAttribute(c.siUIFileMustExist, True)
        item.setAttribute(c.siUIInitialDir, xsi.ActiveProject2.OriginPath)
        item.setAttribute(c.siUIFileFilter, "Emdl files (*.emdl)|*.emdl|All Files (*.*)|*.*||")
        item = row.addButton("importGeo", "Import")
        item.addCondition("PPG."+self.pAddGeo.scriptName+".Value")
        item = group.addEnumControl(self.pSkinPath.scriptName, [], "Skin Path", c.siControlFilePath)
        item.addCondition("PPG."+self.pAddGeo.scriptName+".Value")
        item.setAttribute(c.siUIOpenFile, True)
        item.setAttribute(c.siUIFileMustExist, True)
        item.setAttribute(c.siUIInitialDir, xsi.ActiveProject2.OriginPath)
        item.setAttribute(c.siUIFileFilter, "Skin files (*.xml)|*.xml|All Files (*.*)|*.*||")

        '''
        group = tab.addGroup("Extra Rig")
        item = group.addItem(self.pAddGeo.scriptName, "Add Extra Rig")

        row = group.addRow()
        item = row.addEnumControl(self.pXRigPath.scriptName, [], "Extra Rig Path", c.siControlFilePath)
        item.addCondition("PPG."+self.pAddXRig.scriptName+".Value")
        item.setAttribute(c.siUIOpenFile, True)
        item.setAttribute(c.siUIFileMustExist, True)
        item.setAttribute(c.siUIInitialDir, xsi.ActiveProject2.OriginPath)
        item.setAttribute(c.siUIFileFilter, "Emdl files (*.emdl)|*.emdl|All Files (*.*)|*.*||")
        '''

        # Synoptic
        synoptic_group = tab.addGroup("Synoptic")
        item = synoptic_group.addEnumControl(self.pProdName.scriptName, [], "Production", c.siControlCombo)

        row = synoptic_group.addRow()
        item = row.addEnumControl(self.pSynopticList.scriptName, [], "Tabs", c.siControlListBox)
        item.setAttribute(c.siUINoLabel, True)
        item.setAttribute(c.siUIWidthPercentage, 60)

        group = row.addGroup("")
        group.addButton("addTab", ">>")
        group.addButton("remTab", "<<")
        group.addSpacer()
        group.addButton("moveTabUp", "Up")

        item = row.addEnumControl(self.pSynopticSelect.scriptName, [], "Tabs", c.siControlListBox)
        item.setAttribute(c.siUINoLabel, True)
        item.setAttribute(c.siUIWidthPercentage, 60)

#        item = synoptic_group.addItem(self.pSynoptic.scriptName, "Tabs")
#        item.setAttribute(c.siUINoLabel, True)

        # Comments  -----------------------------------------
        tab = self.layout.addTab("Comments")

        group = tab.addGroup("Comments")
        item = group.addString(self.pComments.scriptName, "", True, 300)
        item.setAttribute(c.siUINoLabel, True)

    ## Add logic for new layout.
    # @param self
    def addLogic(self):

        self.logic.addGlobalCode("import gear.xsi.rig.logic as logic")

        self.logic.addOnChangedRefresh(self.pMode.scriptName)
        self.logic.addOnChangedRefresh(self.pAddGeo.scriptName)

        self.logic.addOnClicked("inspect", "Application.InspectObj(PPG."+self.pInspectSettings.scriptName+".Value)")

        self.logic.addOnClicked("importGeo", "return")

        self.logic.addOnClicked("selectRoots", "logic.selectRoots(PPG.Inspected(0).Model)")

        self.logic.addOnChangedRefresh(self.pProdName.scriptName)

        self.logic.addOnClicked("addTab", "PPG."+self.pSynoptic.scriptName+".Value = logic.synAddTab(PPG."+self.pSynopticList.scriptName+".Value, PPG."+self.pSynoptic.scriptName+".Value)" + "\r\n" \
                                         +self.logic.refresh_method)

        self.logic.addOnClicked("remTab", "PPG."+self.pSynoptic.scriptName+".Value = logic.synRemTab(PPG."+self.pSynopticSelect.scriptName+".Value, PPG."+self.pSynoptic.scriptName+".Value)" + "\r\n" \
                                         +self.logic.refresh_method)

        self.logic.addOnClicked("moveTabUp", "PPG."+self.pSynoptic.scriptName+".Value = logic.synMoveTabUp(PPG."+self.pSynopticSelect.scriptName+".Value, PPG."+self.pSynoptic.scriptName+".Value)" + "\r\n" \
                                         +self.logic.refresh_method)

    # =====================================================
    # SET

    ## set the guide hierarchy from selection.
    # @param self
    def setFromSelection(self):

        if not xsi.Selection.Count:
            gear.log("Select one or more guide root or a guide model", gear.sev_error)
            self.valid = False
            return False

        for item in xsi.Selection:
            branch = item.IsSelected(True) or item.Type == "#model"
            self.setFromHierarchy(item, branch)

        return True

    ## set the guide from given hierarchy.
    # @param self
    # @param root X3DObject - The root of the hierarchy to parse.
    # @param branch Boolean - True to parse children components
    def setFromHierarchy(self, root, branch=True):

        if not root.IsClassOf(c.siX3DObjectID):
            root = root.Parent3DObject

        # Start
        self.plog.start("Checking guide")

        if root.Type == "#model":
            self.model = root
        else:
            self.model = root.Model
            while True:
                if root.Properties("settings") or root.IsEqualTo(self.model):
                    break
                root = root.Parent3DObject

        # ---------------------------------------------------
        # First check and set the options
        self.plog.log(None, "Get options")
        self.options = self.model.Properties("options")
        if not self.options:
            gear.log("Can't find the 'options' property. %s is not a proper rig guide."%self.model.Name, gear.sev_error)
            self.valid = False
            return

        self.setParamDefValuesFromProperty(self.options)

        # ---------------------------------------------------
        # Get the controlers
        self.plog.log(None, "Get controlers")
        self.controlers_org = self.model.FindChild("controlers_org")
        if self.controlers_org:
            for child in self.controlers_org.Children:
                if child.Type in ["null", "crvlist"]:
                    self.controlers[child.Name] = pri.getPrimitive(child)
                else:
                    gear.log("Invalid controler type : " + child.Name + " - " + child.Type, gear.sev_warning)

        # ---------------------------------------------------
        # Components
        self.plog.log(None, "Get components")
        self.findComponentRecursive(root, branch)

        # Parenting
        self.plog.log(None, "Get parenting")
        for name  in self.componentsIndex:
            compChild = self.components[name]
            for name in self.componentsIndex:
                compParent = self.components[name]
                for name, element in compParent.getObjects(self.model).items():
                    if element is not None and element.IsEqualTo(compChild.root.Parent):
                        compChild.parentComponent = compParent
                        compChild.parentLocalName = name
                        break

        # More option values
        self.addOptionsValues()

        # End
        if not self.valid:
            gear.log("The guide doesn't seem to be up to date. Check logged messages and update the guide.", gear.sev_warning)

        gear.log("Guide loaded from hierarchy in [ " + self.plog.getTime() + " ]")
        self.plog.hideBar()

    def findComponentRecursive(self, obj, branch=True):

        settings = obj.Properties("settings")
        if settings:
            comp_type = settings.Parameters("comp_type").Value
            comp_guide = self.getComponentGuide(comp_type)

            if comp_guide:
                comp_guide.setFromHierarchy(obj)
                self.plog.log(None, comp_guide.fullName+" ("+comp_type+")")
                if not comp_guide.valid:
                    self.valid = False

                self.componentsIndex.append(comp_guide.fullName)
                self.components[comp_guide.fullName] = comp_guide

        if branch:
            for child in obj.Children:
                self.findComponentRecursive(child)

    # @param self
    # @param path String - Path to an xml definition.
    def setFromFile(self, path):

        if not os.path.exists(path):
            gear.log("Can't find file : "+ path, gear.sev_error)
            self.valid = False
            return False

        tree = etree.parse(path)
        xml_guide = tree.getroot()
        if xml_guide is None or xml_guide.tag != "guide":
            gear.log("Error opening File", gear.sev_error)
            self.valid = False
            return False

        self.setFromXml(xml_guide)

        return True

    ## set the guide hierarchy from given xml definition.
    # @param self
    # @param xml_doc xml_node - Xml definition of the guide.
    def setFromXml(self, xml_guide):

        # Options
        xml_options = xml_guide.find("options")
        if not xml_options:
            self.valid = False
        else:
            self.setParamDefValuesFromXml(xml_options)

        # Controlers
        xml_controlers = xml_guide.find("controlers")
        if xml_controlers:
            for xml_obj in xml_controlers.findall("x3dobject"):
                name = xml_obj.get("name")
                type = xml_obj.get("type")
                if type in ["null", "crvlist"]:
                    self.controlers[name] = pri.getPrimitive(xml_obj)
                else:
                    gear.log("Invalid controler type : " + name + " - " + type, gear.sev_warning)

        # Component Guide
        for xml_comp in xml_guide.findall("component"):
            comp_name = xml_comp.get("name")
            comp_type = xml_comp.get("type")
            comp_guide = self.getComponentGuide(comp_type)

            if not comp_guide:
                continue

            comp_guide.setFromXml(xml_comp)

            self.componentsIndex.append(comp_name)
            self.components[comp_name] = comp_guide

        # Parenting
        for xml_comp in xml_guide.findall("component"):
            name = xml_comp.get("name")
            parent = xml_comp.get("parent")

            if parent is None:
                continue

            parent = parent.split(".")

            if parent[0] != "None":
                self.components[name].parentComponent = self.components[parent[0]]
                self.components[name].parentLocalName = parent[1]

        # More option values
        self.addOptionsValues()

    ## Gather or change some options values according to some others.
    # @param self
    def addOptionsValues(self):

        # Convert color sliders to list
        for s in ["R_", "L_", "C_"]:
            self.values[s+"color_fk"] = [self.values[s+"color_fk_r"], self.values[s+"color_fk_g"], self.values[s+"color_fk_b"]]
            self.values[s+"color_ik"] = [self.values[s+"color_ik_r"], self.values[s+"color_ik_g"], self.values[s+"color_ik_b"]]

        # When not wip, some options are forced
        if self.values["mode"] == 0:
            self.values["setHidden"] = True
            self.values["setUnselectable"] = True
            self.values["setDeformers"] = True
            self.values["setGeometries"] = True
            self.values["popUpControls"] = False
            self.values["isolateResult"] = False

        # Get rig size to adapt size of object to the scale of the character
        maximum = 1
        v = XSIMath.CreateVector3()
        for comp in self.components.values():
            for pos in comp.apos:
                d = vec.getDistance(v, pos)
                maximum = max(d, maximum)

        self.values["size"] = max(maximum * .05, .1)

    # =====================================================
    # XML IMPORT EXPORT

    ## Import guide from xml.
    # @param self
    # @param path String.
    def importFromXml(self, path):

        if not self.setFromFile(path):
            return

        if not self.valid:
            uit.msgBox("Imported guide is not up to date, Check log for missing element")

        self.draw()

        self.model.Name = os.path.basename(path).split(".")[0]

        xsi.SelectObj(self.model)

        return self.model

    ## Export a guide to xml.
    # @param self
    # @param model Model - Model of the guide to export.
    # @param path String.
    def exportToXml(self, model, path):

        self.model = model

        self.setFromHierarchy(self.model, True)

        # root
        xml_guide = etree.Element("guide")
        xml_guide.set("name", model.Name)
        xml_guide.set("user", getpass.getuser())
        xml_guide.set("date", str(datetime.datetime.now()))
        xml_guide.set("version", str(xsixmldom.VERSION))
        xml_guide.set("description", str(self.values["comments"]))

        # options
        xml_options = self.getParametersAsXml("options")
        xml_guide.append(xml_options)

        # controlers
        xml_controlers = etree.SubElement(xml_guide, "controlers")
        for name, ctl in self.controlers.items():
            xml_ctl = ctl.getAsXml()
            xml_controlers.append(xml_ctl)

        # components
        for name in self.componentsIndex:
            comp_guide = self.components[name]
            xml_comp = comp_guide.getAsXml()
            xml_guide.append(xml_comp)

        xmldom.indent(xml_guide)

        tree = etree.ElementTree(xml_guide)
        tree.write(path)

    # =====================================================
    # DRAW

    ## Create the initial rig gudie hierarchy (model, options...)
    # @param self
    def initialHierarchy(self):

        # Model
        self.model = xsi.ActiveSceneRoot.AddModel(None, "guide")
        self.model.Properties("Visibility").Parameters("viewvis").Value = False

        # Options
        self.options = self.addProperty(self.model, "options")

        # Groups
        self.hidden_grp = self.model.AddGroup(None, "hidden_grp")
        self.unselectable_grp = self.model.AddGroup(None, "unselectable_grp")
        self.controlers_grp = self.model.AddGroup(None, "controlers_grp")

        self.hidden_grp.Parameters("viewvis").Value = False
        self.hidden_grp.Parameters("rendvis").Value = False
        self.unselectable_grp.Parameters("selectability").Value = False
        self.controlers_grp.Parameters("viewvis").Value = False
        self.controlers_grp.Parameters("rendvis").Value = False

        # The basic org nulls
        self.controlers_org = self.model.AddNull("controlers_org")
        self.hidden_grp.AddMember(self.controlers_org)


    ## Add a new component to the guide.
    # @param self
    # @param parent X3DObject - Parent of this new component guide.
    # @param compType String - Type of component to add.
    def drawNewComponent(self, parent, comp_type):

        comp_guide = self.getComponentGuide(comp_type)

        if not comp_guide:
            return

        if parent is None:
            self.initialHierarchy()
            parent = self.model

        elif not parent.IsClassOf(c.siX3DObjectID):
            gear.log("Invalid Parent Selected", gear.sev_error)
            return

        else:
            parent_root = parent
            while True:
                if parent_root.Type == "#model":
                    break

                # Setting some default value according to the parent (side, connector and uihost)
                if parent_root.Properties("settings"):
                    parent_type = parent_root.Properties("settings").Parameters("comp_type").Value
                    parent_side = parent_root.Properties("settings").Parameters("comp_side").Value
                    parent_uihost = parent_root.Properties("settings").Parameters("uiHost").Value

                    if parent_type in comp_guide.connectors:
                        comp_guide.setParamDefValue("connector", parent_type)

                    comp_guide.setParamDefValue("comp_side", parent_side)
                    comp_guide.setParamDefValue("uiHost", parent_uihost)

                    break

                parent_root = parent_root.Parent3DObject

            if not self.isValidModel(parent.Model):
                return

        if comp_guide.drawFromUI(parent):
            xsi.SelectObj(comp_guide.root)
            xsi.InspectObj(comp_guide.settings)

    def draw(self, parent=None):

        # Initial hierarchy
        if parent is None:
            self.initialHierarchy()
            parent = self.model

        # Controlers
        for name, controler in self.controlers.items():
            if controler.xml.find("primitive").find("curve") != None:
                rC = controler.xml.find("primitive").find("curve").get("rColor")
                gC = controler.xml.find("primitive").find("curve").get("gColor")
                bC = controler.xml.find("primitive").find("curve").get("bColor")
                ctlColor = [rC, gC, bC]
            else:
                ctlColor = [.25,.35,.25]

            obj = controler.create(self.controlers_org, name, XSIMath.CreateTransform(), ctlColor )
            self.controlers_grp.AddMember(obj)

        # Components
        for name in self.componentsIndex:
            comp_guide = self.components[name]

            if comp_guide.parentComponent is None:
                parent = self.model
            else:
                parent = self.model.FindChild(comp_guide.parentComponent.getName(comp_guide.parentLocalName))
                if not parent:
                    gear.log("Unable to find parent (%s.%s) for guide %s"%(comp_guide.parentComponent .getFullName, comp_guide.parentLocalName, comp_guide.getFullName ))
                    parent = self.model

            comp_guide.drawFromXml(parent)

    def update(self, sel):

        if sel.Type == "#model":
            self.model = sel
        else:
            self.model = sel.Model

        name = self.model.Name

        self.setFromHierarchy(self.model, True)
        if self.valid:
            rtn = uit.msgBox("No error detected. \n Do you really want to update it ?", c.siMsgYesNo, "Guide Update")
            if rtn == c.siMsgNo:
                return

        self.model.Name = name+"_old"
        self.draw()
        self.model.Name = name

    ## Duplicate the guide hierarchy.
    # @param self
    # @param root X3DObject
    # @param symmetrize Boolean
    # @return X3DObject - The root of the newly created hierarchy.
    def duplicate(self, root, symmetrize=False):

        if not root or (root.Type != "#model" and not root.Properties("settings")):
            gear.log("Select a root to duplicate", gear.sev_error)
            return

        self.setFromHierarchy(root)
        for name in self.componentsIndex:
            comp_guide = self.components[name]
            if symmetrize:
                if not comp_guide.symmetrize():
                    return

        # Draw
        if root.Type == "#model":
            self.draw()
        else:

            for name in self.componentsIndex:
                comp_guide = self.components[name]

                if comp_guide.parentComponent is None:
                    if symmetrize:
                        parent = self.model.FindChild(uti.convertRLName(comp_guide.root.Name))
                        if parent is None:
                            parent = comp_guide.root.Parent
                    else:
                        parent = comp_guide.root.Parent

                else:
                    parent = self.model.FindChild(comp_guide.parentComponent.getName(comp_guide.parentLocalName))
                    if not parent:
                        gear.log("Unable to find parent (%s.%s) for guide %s"%(comp_guide.parentComponent.getFullName, comp_guide.parentLocalName, comp_guide.getFullName ))
                        parent = self.model

                comp_guide.root = None # Reset the root so we force the draw to duplicate
                comp_guide.setIndex(self.model)

                comp_guide.draw(parent)

        xsi.SelectObj(self.components[self.componentsIndex[0]].root)

    # =====================================================
    # MISC

    ## Check if given model is a guide model.
    # @param self
    # @param model Model - Model to check.
    # @return Boolean - True if the model is valid.
    def isValidModel(self, model):

        self.model = model
        self.options = self.model.Properties("options")
        if not self.options:
            gear.log("Invalid parent selected", gear.sev_error)
            return False

        return True

    def getComponentGuide(self, comp_type):

        # Check component type
        path = os.path.join(COMPONENT_PATH, comp_type, "guide.py")
        if not os.path.exists(path):
            gear.log("Can't find guide definition for : " + comp_type + ".\n"+ path, gear.sev_error)
            return False

        # Import module and get class
        module_name = "gear.xsi.rig.component."+comp_type+".guide"
        module = __import__(module_name, globals(), locals(), ["*"], -1)
        ComponentGuide = getattr(module , "Guide")

        return ComponentGuide()
