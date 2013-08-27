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

## @package gear.xsi.io
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import datetime
import getpass
import xml.etree.cElementTree as etree

# gear
import gear
import gear.xmldom as xmldom

from gear.xsi import xsi, c, dynDispatch
import gear.xsi.xmldom as xsixmldom
import gear.xsi.operator as ope

##########################################################
# IMPORT
##########################################################
# ========================================================
## Import a skin (xml definition of deformers) on given object
# @param xml_obj XmlElement - Xml definition of the object
# @param obj X3DObject - Object to apply the deformers to 
def importSkin(xml_obj, obj):

    xml_env = xmldom.findChildByAttribute(xml_obj, "primitive/stack/operator", "type", "envelopop")
    if not xml_env:
        gear.log("No envelope definition for %s"%xml_obj.get("name"), gear.sev_warning)
        return

    xEnvelopeOp = xsixmldom.EnvelopeOp(xml_env)
    op = xEnvelopeOp.generateObject(obj)

    return op

# ========================================================
## Import an envelope from xml definition on given object
# @param xml_obj XmlElement - Xml definition of the object
# @param obj X3DObject - Object to apply the deformers to
# @param pnt_selection List of Integer - Indexes of the point to apply the envelope to
# @return Operator - The newly created envelope operator
def importEnvelope(xml_obj, obj, pnt_selection=None):

    xml_env = xmldom.findChildByAttribute(xml_obj, "primitive/stack/operator", "type", "envelopop")
    if not xml_env:
        gear.log("No envelope definition for %s"%xml_obj.get("name"), gear.sev_warning)
        return

    xEnvelopeOp = xsixmldom.EnvelopeOp(xml_env)
    op = xEnvelopeOp.generateObject(obj, pnt_selection)

    return op

##########################################################
# EXPORT
##########################################################
# ========================================================
## Export to xml the skin of an object. The skin is all the stack of deformers applied on a geometry.\n
## Only envelope are supported right now.
# @param path String - Path to a file to save the xml file.
# @param objects Collection or List of X3DObjects - objects to export.
# @param compression Boolean - True to activate compression of the datas inside the xml file.
def exportSkin(path, objects, compression=False):

    xml_doc = etree.Element("skin")
    xml_doc.set("user", getpass.getuser())
    xml_doc.set("date", str(datetime.datetime.now()))
    xml_doc.set("version", str(xsixmldom.VERSION))

    # -----------------------------------------------------
    for obj in objects:

        envelope_op = ope.getOperatorFromStack(obj, "envelopop")
        if not envelope_op:
            gear.log("%s has no envelope skipped"%obj.Name, gear.sev_warning)
            continue

        xsixmldom.setOptions(X3DObject_children=False,
                                    X3DObject_primitive=False,
                                    X3DObject_kinematics=False,
                                    X3DObject_properties=[],
                                    Geometry_operators=["envelopop"],
                                    Compression=compression)
        xObject = xsixmldom.getObject(obj)
        xml_doc.append(xObject.xml)

    # -----------------------------------------------------
    # Save to file
    xmldom.indent(xml_doc)

    tree = etree.ElementTree(xml_doc)
    tree.write(path)

    return True

# ========================================================
## Export to xml the envelope of an object.
# @param path String - Path to a file to save the xml file.
# @param objects Collection or List of X3DObjects - objects to export.
# @param compression Boolean - True to activate compression of the datas inside the xml file.
def exportEnvelope(path, objects, compression=False):

    xml_doc = etree.Element("skin")
    xml_doc.set("user", getpass.getuser())
    xml_doc.set("date", str(datetime.datetime.now()))
    xml_doc.set("version", str(xsixmldom.VERSION))

    # -----------------------------------------------------
    for obj in objects:

        envelope_op = ope.getOperatorFromStack(obj, "envelopop")
        if not envelope_op:
            gear.log("%s has no envelope skipped"%obj.Name, gear.sev_warning)
            continue

        xsixmldom.setOptions(X3DObject_children=False,
                                    X3DObject_primitive=False,
                                    X3DObject_kinematics=False,
                                    X3DObject_properties=[],
                                    Geometry_operators=["envelopop"],
                                    Compression=compression)
        xObject = xsixmldom.getObject(obj)
        xml_doc.append(xObject.xml)

    # -----------------------------------------------------
    # Save to file
    xmldom.indent(xml_doc)

    tree = etree.ElementTree(xml_doc)
    tree.write(path)

    return True

##########################################################
# MISC
##########################################################
# ========================================================
## Return 
def getObjectItems(path):

    # -----------------------------------------------------
    tree = etree.parse(path)
    xml_doc = tree.getroot()

    # -----------------------------------------------------
    items = ["-- Skip --", "0"]
    xml_objs = {}
    for xml_obj in xml_doc.findall("x3dobject"):

        name = xml_obj.get("name")
        items.append(name)
        items.append(name)

        xml_objs[name] = xml_obj

    return items, xml_objs

# ========================================================
def getObjectDefinitions(path, inputs, ui=False):

    items, xml_objs = getObjectItems(path)

    objects = []
    for obj in inputs:
        if obj.Type in ["pntSubComponent"]:
            objects.append(obj.SubComponent.Parent3DObject)
        else:
            objects.append(obj)

    # -----------------------------------------------------
    # Check if we need the UI
    defs = {}
    if ui:
        if not [False for obj in objects if obj.Name not in items]:
            ui = False
        else:
            prop = xsi.ActiveSceneRoot.AddProperty("CustomProperty", False, "ImportEnvelope")
            layout = prop.PPGLayout

            layout.AddGroup("Select Object Reference")

            params = {}
            for obj in objects:
                if obj.Name in items:
                    param = prop.AddParameter3("def_%s"%obj.Name, c.siString, obj.Name)
                else:
                    param = prop.AddParameter3("def_%s"%obj.Name, c.siString, "0")

                params[obj.name] = param

                layout.AddEnumControl(param.ScriptName, items, obj.Name, c.siControlCombo)

            layout.EndGroup()

            rtn = xsi.InspectObj(prop, "", "Import Envelope", c.siModal, False)

            for obj in objects:
                if params[obj.Name].Value != "0":
                    defs[obj.Name] = xml_objs[params[obj.Name].Value]

            xsi.DeleteObj(prop)

            if rtn:
                return False

    if not ui:
        for obj in objects:
            if obj.Name in xml_objs.keys():
                defs[obj.Name] = xml_objs[obj.Name]
            else:
                gear.log("No defintion found for %s"%obj.Name, gear.sev_warning)

    return defs
