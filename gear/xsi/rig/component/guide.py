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

## @package gear.xsi.rig.component.guide
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
# Built in
import xml.etree.cElementTree as etree

# gear
import gear

import gear.xsi.xmldom as xsixmldom
import gear.string as string

from gear.xsi import xsi, c

from gear.xsi.rig.guide import MainGuide

import gear.xsi.ppg as ppg
import gear.xsi.utils as uti
import gear.xsi.uitoolkit as uit
import gear.xsi.primitive as pri
import gear.xsi.transform as tra
import gear.xsi.parameter as par
import gear.xsi.vector as vec
import gear.xsi.curve as cur

# Guide global variable
GUIDE_ROOT_COLOR = [1,0,0]
GUIDE_LOC_COLOR = [1,.75,0]
GUIDE_BLADE_COLOR = [.75, .75, 0]

##########################################################
# COMPONENT GUIDE
##########################################################
## Main class for component guide creation.\n
# This class handles all the parameters and objectDefs creation.\n
# It also now how to parse its own hierachy of object to retrieve position and transform.\n
# Finally it also now how to export itself as xml_node.
class ComponentGuide(MainGuide):

    compType = "component"  ## Component type
    compName = "component"  ## Component default name
    compSide = "C"
    compIndex = 0 ## Component default index

    description = "" ## Description of the component

    connectors = []
    compatible = []
    ctl_grp = ""

    # ====================================================
    ## Init method.
    # @param self
    # @param ref an xml definition or a SI3DObject
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

        self.root = None
        self.id = None

        # parent component identification
        self.parentComponent = None
        self.parentLocalName = None

        # List and dictionary used during the creation of the component
        self.tra = {} ## dictionary of global transform
        self.atra = [] ## list of global transform
        self.pos = {} ## dictionary of global postion
        self.apos = [] ## list of global position
        self.prim = {} ## List of primitive
        self.blades = {}
        self.size = .1
        self.root_size = None

        # List and dictionary used to define data of the guide that should be saved
        self.pick_transform = [] ## User will have to pick the position of this object name
        self.save_transform = [] ## Transform of object name in this list will be saved
        self.save_primitive = [] ## Primitive of object name in this list will be saved
        self.save_blade = [] ## Normal and BiNormal of object will be saved
        self.minmax = {} ## Define the min and max object for multi location objects

        # Init the guide
        self.postInit()
        self.initialHierarchy()
        self.addParameters()
        self.addLayout()
        self.addLogic()

    ## Define the objects name and categories.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def postInit(self):
        self.save_transform = ["root"]
        return

    # ====================================================
    # OBJECTS AND PARAMETERS
    ## Initial hierachy. It's no more than the basic set of parameters and layout needed for the setting property.
    # @param self
    def initialHierarchy(self):

        # Parameters --------------------------------------
        # This are the necessary parameter for conponent guide definition
        self.pCompType = self.addParam("comp_type", c.siString, self.compType)
        self.pCompName = self.addParam("comp_name", c.siString, self.compName)
        self.pCompSide = self.addParam("comp_side", c.siString, self.compSide)
        self.pCompIndex = self.addParam("comp_index", c.siInt4, self.compIndex, 0)
        self.pConnector = self.addParam("connector", c.siString, "standard")
        self.pUIHost = self.addParam("uiHost", c.siString, "")
        self.pSetGrp = self.addParam("set_ctl_grp", c.siBool, self.ctl_grp != "")
        self.pCtlGrp = self.addParam("ctl_grp", c.siString, self.ctl_grp)

        # Items -------------------------------------------
        typeItems = [self.compType, self.compType]
        for type in self.compatible:
            typeItems.append(type)
            typeItems.append(type)

        connectorItems = ["standard", "standard"]
        for item in self.connectors:
            connectorItems.append(item)
            connectorItems.append(item)

        # Layout ------------------------------------------
        tab = self.layout.addTab("Main")

        group = tab.addGroup("Component")
        item = group.addEnumControl(self.pCompType.scriptName, typeItems, "Type", c.siControlCombo)

        group = tab.addGroup("Naming")
        row = group.addRow()
        item = row.addItem(self.pCompName.scriptName, "Name")
        item.setAttribute(c.siUIWidthPercentage, 55)
        item = row.addEnumControl(self.pCompSide.scriptName, ["Center", "C", "Right", "R", "Left", "L"], "Side", c.siControlCombo)
        item.setAttribute(c.siUINoLabel, True)
        item.setAttribute(c.siUIWidthPercentage, 25)
        item = row.addItem(self.pCompIndex.scriptName, "Index")
        item.setAttribute(c.siUINoLabel, True)
        item.setAttribute(c.siUIWidthPercentage, 20)
        item.setAttribute(c.siUINoSlider, True)

        group = tab.addGroup("Connector")
        group.addEnumControl(self.pConnector.scriptName, connectorItems, "Type", c.siControlCombo)
        row = group.addRow()
        row.addItem(self.pUIHost.scriptName, "UI Host")
        row.addButton("pick_uihost", "Pick")

        group = tab.addGroup("Controlers")
        item = group.addItem(self.pSetGrp.scriptName, "Use Custom Group Name for Controlers")
        item = group.addItem(self.pCtlGrp.scriptName, "Group Name")
        item.addCondition("PPG."+self.pSetGrp.scriptName+".Value")

        # Logic -------------------------------------------
        self.logic.addGlobalCode("import gear.xsi.uitoolkit as uit")
        self.logic.addGlobalCode("from gear.xsi.rig.component."+self.values["comp_type"]+".guide import Guide")
        code = "g = Guide()\r\ng.rename(PPG.Inspected(0))"

        self.logic.addOnChanged(self.pCompName.scriptName, code)
        self.logic.addOnChanged(self.pCompSide.scriptName, code)
        self.logic.addOnChanged(self.pCompIndex.scriptName, code)

        self.logic.addOnChangedRefresh(self.pSetGrp.scriptName)

        self.logic.addOnClicked("pick_uihost", "rtn = uit.pickSession(c.siGenericObjectFilter, 'Pick UI Host', False)"+"\r\n"+\
                                                            "if not rtn:"+"\r\n"+\
                                                            "    return"+"\r\n"+\
                                                            "PPG."+self.pUIHost.scriptName+".Value = rtn.Name")

    ## Create the objects of the guide.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def addObjects(self):
        self.root = self.addRoot()

    ## Create the parameter definitions of the guide.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def addParameters(self):
        return

    ## Define the layout attached to the parameters.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def addLayout(self):
        return

    ## Define the logic attached to the ppg.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def addLogic(self):
        return

    # ====================================================
    # SET / GET
    def setFromHierarchy(self, root):

        self.root = root
        self.model = self.root.Model

        # ---------------------------------------------------
        # First check and set the settings
        self.settings = self.root.Properties("settings")
        if not self.settings:
            gear.log("Can't find the 'setting' property. %s is not a proper guide."%self.root.Name, gear.sev_error)
            self.valid = False
            return

        self.setParamDefValuesFromProperty(self.settings)

        # ---------------------------------------------------
        # Then get the objects
        for name in self.save_transform:
            if "#" in name:
                i = 0
                while not self.minmax[name].max > 0 or i < self.minmax[name].max:
                    localName = string.replaceSharpWithPadding(name, i)

                    obj = self.model.FindChild(self.getName(localName))
                    if not obj:
                        break

                    self.tra[localName] = obj.Kinematics.Global.Transform
                    self.atra.append(obj.Kinematics.Global.Transform)
                    self.pos[localName] = obj.Kinematics.Global.Transform.Translation
                    self.apos.append(obj.Kinematics.Global.Transform.Translation)

                    i += 1

                if i < self.minmax[name].min:
                    gear.log("Minimum of object requiered for "+name+" hasn't been reached", gear.sev_warning)
                    self.valid = False
                    continue

            else:
                obj = self.model.FindChild(self.getName(name))
                if not obj:
                    gear.log("Object missing : %s"%name, gear.sev_warning)
                    self.valid = False
                    continue

                self.tra[name] = obj.Kinematics.Global.Transform
                self.atra.append(obj.Kinematics.Global.Transform)
                self.pos[name] = obj.Kinematics.Global.Transform.Translation
                self.apos.append(obj.Kinematics.Global.Transform.Translation)

        for name in self.save_primitive:
            obj = self.model.FindChild(self.getName(name))
            if not obj:
                gear.log("Object missing : %s"%name, gear.sev_warning)
                self.valid = False
                continue

            self.prim[name] = pri.getPrimitive(obj)

        for name in self.save_blade:
            obj = self.model.FindChild(self.getName(name))
            if not obj:
                gear.log("Object missing : %s"%name, gear.sev_warning)
                self.valid = False
                continue

            self.blades[name] = vec.Blade(obj.Kinematics.Global.Transform)

        self.size = self.getSize()
        self.root_size = self.root.size.Value

    def setFromXml(self, xml_comp):

        # ---------------------------------------------------
        # Settings
        xml_settings = xml_comp.find("settings")
        self.setParamDefValuesFromXml(xml_settings)

        # ---------------------------------------------------
        # First get all the object available in the xml (it's faster that way)
        xml_objects = xml_comp.find("objects")
        for xml_obj in xml_objects.findall("x3dobject"):
            localName = xml_obj.get("localName")
            xObj = xsixmldom.xmlToObject(xml_obj)

            xml_kine = xml_obj.find("kinematics")
            if xml_kine and len(xml_kine):
                t = xObj.getGlobalTransform()
                self.tra[localName] = t
                self.pos[localName] = t.Translation

            xml_prim = xml_obj.find("primitive")
            if xml_prim  and len(xml_prim):
                self.prim[localName] = pri.getPrimitive(xml_obj)

            if localName in self.save_blade:
                self.blades[localName] = vec.Blade(self.tra[localName])

        # ---------------------------------------------------
        # Then check what is missing
        for name in self.save_transform:
            if "#" in name:
                i = 0
                while not self.minmax[name].max > 0 or i < self.minmax[name].max:
                    localName = string.replaceSharpWithPadding(name, i)

                    if localName not in self.tra.keys():
                        break

                    self.atra.append(self.tra[localName])
                    self.apos.append(self.pos[localName])

                    i += 1

                if i < self.minmax[name].min:
                    gear.log("Minimum of object requiered for "+name+" hasn't been reached", gear.sev_warning)
                    self.valid = False
                    continue
            else:
                if name not in self.tra.keys():
                    gear.log("Object missing : %s"%name, gear.sev_warning)
                    self.valid = False
                    continue

                self.atra.append(self.tra[name])
                self.apos.append(self.pos[name])

        for name in self.save_primitive:
            if name not in self.prim.keys():
                gear.log("Object missing : %s"%name, gear.sev_warning)
                self.valid = False
                continue

        for name in self.save_blade:
            if name not in self.blades.keys():
                gear.log("Object missing : %s"%name, gear.sev_warning)
                self.valid = False
                continue

        self.size = self.getSize()
        self.root_size = float(xml_comp.get("root_size"))

    ## Return the guide as an xml definition.
    # param self
    def getAsXml(self):

        xml_comp = etree.Element("component")
        xml_comp.set("name", self.fullName)
        xml_comp.set("type", self.type)
        if self.parentComponent is None:
            xml_comp.set("parent", "None")
        else:
            xml_comp.set("parent", self.parentComponent.fullName+"."+self.parentLocalName)
        xml_comp.set("root_size", str(self.root.size.Value))

        # Settings and parameters
        xml_settings = self.getParametersAsXml("settings")
        xml_comp.append(xml_settings)

        # Objects
        xml_objects = etree.SubElement(xml_comp, "objects")
        for name in self.objectNames:
            if "#" in name:
                i = 0
                while not self.minmax[name].max > 0 or i < self.minmax[name].max:
                    localName = string.replaceSharpWithPadding(name, i)

                    xsixmldom.setOptions(X3DObject_children=False,
                                             X3DObject_primitive=(name in self.save_primitive),
                                             X3DObject_kinematics=(name in self.save_transform or name in self.save_blade),
                                             X3DObject_properties=[],
                                             Kinematics_local=False,
                                             Kinematics_constraints=False,
                                             Kinematics_removeScaling=True,
                                             Geometry_addScaling=True,
                                             Geometry_stack=False)

                    obj = self.model.FindChild(self.getName(localName))
                    if not obj:
                        break
                    xml_def = xsixmldom.getObject(obj).xml
                    xml_def.set("localName", localName)
                    xml_objects.append(xml_def)

                    i += 1

                if i < self.minmax[name].min:
                    gear.log("Minimum of object requiered for "+name+" hasn't been reached", gear.sev_warning)
                    self.valid = False
                    continue

            else:
                xsixmldom.setOptions(X3DObject_children=False,
                                         X3DObject_primitive=(name in self.save_primitive),
                                         X3DObject_kinematics=(name in self.save_transform or name in self.save_blade),
                                         X3DObject_properties=[],
                                         Kinematics_local=False,
                                         Kinematics_constraints=False,
                                         Kinematics_removeScaling=True,
                                         Geometry_addScaling=True,
                                         Geometry_stack=False)

                obj = self.model.FindChild(self.getName(name))
                if not obj:
                    gear.log("Object missing : %s"%name, gear.sev_warning)
                    continue
                xml_def = xsixmldom.getObject(obj).xml
                xml_def.set("localName", name)
                xml_objects.append(xml_def)

        return xml_comp

    # ====================================================
    # DRAW

    ## Draw the guide in the scene.
    # param self
    # param parent X3DObject - Parent object.
    def draw(self, parent):
        self.parent = parent
        self.addObjects()

        # Set the size of the root
        self.root.size = self.root_size

    ## Launch a pick session to get the position of the guide, then draw the guide in the scene.
    # param self
    # param parent X3DObject - Parent object.
    def drawFromUI(self, parent):

        if not self.pickPositions():
            gear.log("aborded", gear.sev_warning)
            return

        self.parent = parent
        self.setIndex(self.parent.Model)
        self.addObjects()

        # Set the size of the controlers
        if self.root_size is None:
            self.root_size = 1
            if self.type != "control_01":
                for child in self.root.FindChildren():
                    self.root_size = max(self.root_size, vec.getDistance2(self.root, child))
                self.root_size = min(1, max(.1, self.root_size*.15))

        self.root.size = self.root_size

        xsi.InspectObj(self.settings)

    def drawFromXml(self, parent):

        self.parent = parent
        self.setIndex(self.parent.Model)
        self.addObjects()

        # Set the size of the root
        self.root.size = self.root_size

    ## Launch a pick session to get the position of the guide.
    # param self
    # return Boolean - False if pick session was aborded at anytime.
    def pickPositions(self):

        refs = []

        for name in self.pick_transform:

            if "#" in name:
                i = 0
                while not self.minmax[name].max > 0 or i < self.minmax[name].max:
                    localName = string.replaceSharpWithPadding(name, i)

                    position = uit.pickPosition("Pick %s position"%localName, False)
                    if not position:
                        break
                    self.tra[localName] = tra.getTransformFromPosition(position)
                    refs.append(self.drawRef(self.tra[localName]))

                    i += 1

                if i < self.minmax[name].min:
                    gear.log("Minimum of object requiered for "+name+" hasn't been reached", gear.sev_warning)
                    xsi.DeleteObj(refs)
                    return False
            else:
                position = uit.pickPosition("Pick %s position"%name, True)
                if not position:
                    xsi.DeleteObj(refs)
                    return False

                self.tra[name] = tra.getTransformFromPosition(position)
                refs.append(self.drawRef(self.tra[name]))

        xsi.DeleteObj(refs)

        return True

    ## Create a temporary null to display the picked position.
    # param self
    # param t SITransformation - The transformation of the reference object.
    # return Null - The newly created reference null.
    def drawRef(self, t):
        ref = pri.addNull(xsi.ActiveSceneRoot, self.getName("ref"), t, .3)
        pri.setNullDisplay(ref, 1, .3, 2, 0, 0, 0, .5, .5, .5, [.5,.875,.5])
        return ref

    # ====================================================
    # UPDATE

    ## Update the component index to get the next valid one.
    # @param self
    # @param parent X3DObject - The parent object of the guide.
    def setIndex(self, model):

        self.model = model

        # Find next index available
#        self.values["comp_index"] = 0
        while True:
            obj = self.model.FindChild(self.getName("root"))
            if not obj or (self.root and obj.IsEqualTo(self.root)):
                break

            self.setParamDefValue("comp_index", self.values["comp_index"] + 1)

        if self.root:
            self.settings = self.root.Properties("settings")
            self.settings.Parameters("comp_index").Value = self.values["comp_index"]

    ## Inverse the transform of each element of the guide.
    # @param self
    def symmetrize(self):

        if self.values["comp_side"] not in ["R", "L"]:
            gear.log("Can't symmetrize central component", gear.sev_error)
            return False

        #self.setParamDefValue("comp_side", uti.convertRLName(self.values["comp_side"]))

        for name, paramDef in self.paramDefs.items():
            if paramDef.valueType == c.siString:
                self.setParamDefValue(name, uti.convertRLName(self.values[name]))

        for name, t in self.tra.items():
            self.tra[name] = tra.getSymmetricalTransform2(t)

        for name, blade in self.blades.items():
            self.blades[name] = vec.Blade(tra.getSymmetricalTransform2(blade.transform))

        return True

    ## Rename the component. Rename use the value of the setting property.
    # @param
    # @param prop Property - The setting property of the component to remame.
    def rename(self, prop):

        self.settings = prop
        self.root = prop.Parent3DObject
        self.model = self.root.Model

        new_name = self.settings.Parameters("comp_name").Value
        new_side = self.settings.Parameters("comp_side").Value
        new_index = self.settings.Parameters("comp_index").Value

        a = self.root.Name.split("_")
        self.settings.Parameters("comp_name").Value = a[0]
        self.settings.Parameters("comp_side").Value = a[1][0]
        self.settings.Parameters("comp_index").Value = int(a[1][1:])

        self.setFromHierarchy(self.root)
        oldName = self.fullName

        self.values["comp_name"] = new_name
        self.values["comp_side"] = new_side
        self.values["comp_index"] = new_index
        self.settings.Parameters("comp_name").Value = new_name
        self.settings.Parameters("comp_side").Value = new_side
        self.settings.Parameters("comp_index").Value = new_index

        self.setIndex(self.model)

        for obj in self.model.FindChildren(oldName+"_*"):
            localName = obj.Name.replace(oldName+"_", "")
            obj.Name = self.getName(localName)

    # ====================================================
    # ELEMENTS

    ## Add a root object to the guide.\n
    ## This mehod can initialize the object or draw it.\n
    ## Root object is a simple null with a specific display and a setting property.
    # @param self
    # return X3DObject - The created root null.
    def addRoot(self):

        self.root = pri.addNull(self.parent, self.getName("root"), self.tra["root"])
        pri.setNullDisplay(self.root, 1, 1, 4, 0, 0, 0, .75, .75, .75, GUIDE_ROOT_COLOR)

        # Settings
        self.settings = self.addProperty(self.root, "settings")

        return self.root

    ## Add a loc object to the guide.\n
    ## This mehod can initialize the object or draw it.\n
    ## Loc object is a simple null to define a position or a tranformation in the guide.
    # @param self
    # @param name String - Local name of the element.
    # @param parent X3DObject - The parent of the element.
    # @param position SIVector3 - The default position of the element. Pick sesssion is launch if none.
    # return X3DObject - The created loc null.
    def addLoc(self, name, parent, position=None):

        if name not in self.tra.keys():
            self.tra[name] = tra.getTransformFromPosition(position)

        if name in self.prim.keys():
            loc = self.prim[name].create(parent, self.getName(name), self.tra[name], GUIDE_LOC_COLOR)
        else:
            loc = pri.addNull(parent, self.getName(name), self.tra[name])
            pri.setNullDisplay(loc, 1, .5, 2, 0, 0, 0, .5, .5, .5, GUIDE_LOC_COLOR)

        if loc.Type == "null":
            par.addExpression(loc.size, self.root.size.FullName+" * .5")

        return loc

    ## Add multiple loc objects to the guide.\n
    ## This mehod can initialize the object or draw it.\n
    ## Loc object is a simple null to define a position or a tranformation in the guide.
    # @param self
    # @param name String - Local name of the element.
    # @param parent X3DObject - The parent of the element.
    # @param minimum Int - The minimum number of loc.
    # @param maximum Int - The maximum number of loc.
    # @param updateParent - update the parent reference or keep the same for all loc
    # return List of X3DObject - The created loc nulls in a list.
    def addLocMulti(self, name, parent, updateParent = True):

        if "#" not in name:
            gear.log("You need to put a '#' in the name of multiple location.", gear.sev_error)
            return False

        locs = []

        i = 0
        while True:
            localName = string.replaceSharpWithPadding(name, i)
            if localName not in self.tra.keys():
                break

            loc = pri.addNull(parent, self.getName(localName), self.tra[localName])
            pri.setNullDisplay(loc, 1, .5, 2, 0, 0, 0, .5, .5, .5, GUIDE_LOC_COLOR)
            par.addExpression(loc.size, self.root.size.FullName+" * .5")
            locs.append(loc)
            if updateParent:
                parent = loc

            i += 1

        return locs

    ## Add a curve object to the guide.\n
    ## This mehod can initialize the object or draw it.\n
    ## Curve object is a curve that can be use in the final rig.
    # @param self
    # @param name String - Local name of the element.
    # @param parent X3DObject - parent guide object.
    # @param points List of Double - list of point position.
    # @param degree Int4 - Curve degree.
    # @param position SIVector3 - The default position of the element. Pick sesssion is launch if none.
    # return X3DObject - The created curve.
    def addCurve(self, name, parent, points=[], close=False, degree=1, position=None):

        if name not in self.tra.keys():
            self.tra[name] = tra.getTransformFromPosition(position)

        if name in self.prim.keys():
            crv = self.prim[name].create(parent, self.getName(name), self.tra[name], GUIDE_LOC_COLOR)
        else:
            crv = cur.addCurveFromPos(parent, name, points, close, degree, c.siNonUniformParameterization, self.tra[name], GUIDE_LOC_COLOR)

        return crv

    ## Add a curve object to the guide.\n
    ## This mehod can initialize the object or draw it.\n
    ## Curve object is a curve that can be use in the final rig.
    # @param self
    # @param name String - Local name of the element.
    # @param parent X3DObject - parent guide object.
    # @param points List of Double - list of point position.
    # @param degree Int4 - Curve degree.
    # @param position SIVector3 - The default position of the element. Pick sesssion is launch if none.
    # return X3DObject - The created curve.
    def addCurve2(self, name, parent, points=[], close=False, degree=1, position=None):

        if name not in self.tra.keys():
            self.tra[name] = tra.getTransformFromPosition(position)

        if name in self.prim.keys():
            crv = self.prim[name].create(parent, self.getName(name), self.tra[name], GUIDE_LOC_COLOR)
        else:
            crv = cur.addCurve(parent, self.getName(name), points, close, degree, self.tra[name], GUIDE_LOC_COLOR)

        return crv
    ## Add a blade object to the guide.\n
    ## This mehod can initialize the object or draw it.\n
    ## Blade object is a 3points curve to define a plan in the guide.
    # @param self
    # @param name String - Local name of the element.
    # @param parentPos X3DObject - The parent of the element.
    # @param parentDir X3DObject - The direction constraint of the element.
    # return X3DObject - The created blade curve.
    def addBlade(self, name, parentPos, parentDir, negate = False):

        # Draw from UI
        dist = vec.getDistance2(parentPos, parentDir)

#        points = [0,0,0,1,0,dist*.5,0,1,dist*.25,0,0,1]
#        blade = cur.addCurve(parentPos, self.getName(name), points, True, 1, parentPos.Kinematics.Global.Transform, [.75, .75, 0])
        blade = pri.addNull(parentPos, self.getName(name), parentPos.Kinematics.Global.transform, dist * .5)
        pri.setNullDisplay(blade, 0, dist*.5, 9, .25, 0, 0, .5, 1, 0, GUIDE_BLADE_COLOR)
        for s in ["primary_icon", "shadow_icon", "shadow_offsetX", "shadow_offsetY", "shadow_offsetZ", "shadow_scaleX", "shadow_scaleY", "shadow_scaleZ"]:
            blade.ActivePrimitive.Parameters(s).AddExpression(blade.ActivePrimitive.Parameters(s).Value)
            blade.ActivePrimitive.Parameters(s).ReadOnly = True

        blade.Kinematics.Local.Parameters("rotorder").Value = 2

        if negate:
            blade.Kinematics.Local.Parameters("roty").Value = -90
        else:
            blade.Kinematics.Local.Parameters("roty").Value = 90



        blade.Kinematics.AddConstraint("Position", parentPos, False)
        cns = blade.Kinematics.AddConstraint("Direction", parentDir, False)
        cns.Parameters("dirx").Value = 0
        cns.Parameters("diry").Value = 1
        cns.Parameters("dirz").Value = 0

        if name in self.blades.keys():
            blade.Kinematics.Global.Transform = self.blades[name].transform

        return blade

    ## Add a display curve object to the guide.\n
    ## This mehod can initialize the object or draw it.\n
    ## Display curve object is a simple curve to show the connection between different guide element.
    # @param self
    # @param name String - Local name of the element.
    # @param centers List of X3DObject - List of parent of the curve.
    # @param degree Int4 - Curve degree.
    # return X3DObject - The created display curve.
    def addDispCurve(self, name, centers=[], degree=1):

        crv = cur.addCnsCurve(centers[0], self.getName(name), centers, False, degree)
        self.addToGroup(crv, "unselectable")

        return crv

    # ====================================================
    # MISC
    ##
    # @param self
    # @paran model
    # @return Dictionary of X3DObject
    def getObjects(self, model):
        objects = {}
        for child in model.FindChildren(self.fullName+"_*"):
            objects[child.Name.replace(self.fullName+"_", "")] = child
        return objects

    ##
    # @param self
    def addMinMax(self, name, minimum=1, maximum=-1):
        if "#" not in name:
            gear.log("Invalid definition for min/max. You should have a '#' in the name", gear.sev_error)
        self.minmax[name] = MinMax(minimum, maximum)

    ##
    # @param self
    # @return Double
    def getSize(self):

        # size
        size = .01
        for pos in self.apos:
            d = vec.getDistance(self.pos["root"], pos)
            size = max(size, d)
        size = max(size, .01)

        return size

    ## Return the fullname of given element of the component.
    # @param self
    # @param name String - Localname of the element.
    def getName(self, name):
        return self.fullName + "_" + name

    ## Return the fullname of the component.
    # @param self
    def getFullName(self):
        return self.values["comp_name"] + "_" + self.values["comp_side"] + str(self.values["comp_index"])

    ## Return the type of the component.
    # @param self
    def getType(self):
        return self.compType

    ##
    # @param self
    def getObjectNames(self):

        names = set()
        names.update(self.save_transform)
        names.update(self.save_primitive)
        names.update(self.save_blade)

        return names

    def getVersion(self):
        return ".".join([str(i) for i in self.version])

    fullName = property(getFullName)
    type = property(getType)
    objectNames = property(getObjectNames)

##########################################################
# OTHER CLASSES
##########################################################
class MinMax(object):

    def __init__(self, minimum=1, maximum=-1):
        self.min = minimum
        self.max = maximum
