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

## @package gear.xsi.xmldom
# @author Jeremie Passerin, Miquel Campos
#

#######################################################################
# GLOBAL
#######################################################################
# Built-in
from xml.etree.cElementTree import ElementTree, Element, SubElement

# gear
import gear
import gear.xmldom as xmldom
import gear.encode as enc

from gear.xsi import xsi, c, XSIMath, dynDispatch, XSIFactory

# =====================================================================
# VERSION
VERSION = 1.0

# =====================================================================
# OPTIONS
OPTIONS = {}

def resetOptions():

    OPTIONS["Compression"] = False
    OPTIONS["ProgressBar"] = False

    OPTIONS["Group_members"] = True

    OPTIONS["Kinematics_local"] = True
    OPTIONS["Kinematics_global"] = True
    OPTIONS["Kinematics_constraints"] = True
    OPTIONS["Kinematics_removeScaling"] = False

    OPTIONS["Parameter_simple"] = True
    OPTIONS["Parameter_source"] = True

    OPTIONS["X3DObject_children"] = True
    OPTIONS["X3DObject_primitive"] = True
    OPTIONS["X3DObject_kinematics"] = True
    OPTIONS["X3DObject_skipBranchProp"] = True
    OPTIONS["X3DObject_properties"] = "all"

    OPTIONS["Geometry_stack"] = True
    OPTIONS["Geometry_operators"] = "all"
    OPTIONS["Geometry_addScaling"] = False

    OPTIONS["Operator_ports"] =  True

def setOptions(**kwargs):

    resetOptions()

    # Options
    for k, v in kwargs.items():
        OPTIONS[k] = v

resetOptions()

# =====================================================================
def getObject(item):

    # X3DObject
    if item.Type == "#model":
        xItem = Model(item)
    elif item.Type == "null":
        xItem = Null(item)
    elif item.Type == "polymsh":
        xItem = PolygonMesh(item)
    elif item.Type == "surfmsh":
        xItem = NurbsSurfaceMesh(item)
    elif item.Type == "crvlist":
        xItem = NurbsCurveList(item)

    # Groups
    elif item.Type == "#group":
        xItem = Group(item)

    # Properties
    elif item.Families == "Properties":
        xItem = Property(item)

    # Else
    else:
        xItem = SIObject(item)

    return xItem

def xmlToObject(item, parent=xsi.ActiveSceneRoot):

    type = item.get("type")
    # X3DObject
    if type == "#model":
        xItem = Model(item)
    elif type == "null":
        xItem = Null(item)
    elif type == "polymsh":
        xItem = PolygonMesh(item)
    elif type == "surfmsh":
        xItem = NurbsSurfaceMesh(item)
    elif type == "crvlist":
        xItem = NurbsCurveList(item)

    # Groups
    elif type == "#group":
        xItem = Group(item)

    # Properties
    elif item.Families == "Properties":
        xItem = Property(item)

    # Else
    else:
        xItem = SIObject(item)

    return xItem


#######################################################################
# XML
#######################################################################
# SIObject ============================================================
class SIObject(object):

    nodeName = "siobject"

    # ------------------------------------------------------------------
    ## Init Method.
    # @param self
    # @param ref SIObject or etree.Element
    def __init__(self, ref):

        # Set
        if str(type(ref)) == "<type 'Element'>":
            self.xml = ref
        else:
            self.xml = Element(self.nodeName)
            self.generateXml(ref)
            self.ref = ref

    # ------------------------------------------------------------------
    ## Save node to xml file
    def save(self, path, pretty_print=True):

        if pretty_print:
            xmldom.indent(self.xml)

        tree = ElementTree(self.xml)
        tree.write(path)

    def open(self, path):
        return

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("type", ref.Type)

    def generateObject(self):
        return

    # ------------------------------------------------------------------
    ## Convert a variant according to XSI siVariantType.
    # @param value String - Value as string.
    # @param variantType Int - siVariantType.
    # @return
    def convertVariantType(self, value, variantType):

        if isinstance(variantType, str):
            variantType = int(variantType)

        if variantType in [c.siInt2, c.siInt4]:
            return int(value)
        elif variantType == c.siString:
            return str(value)
        elif variantType == c.siBool:
            return value in ["true", "True", "1", 1, True]
        elif variantType == c.siDouble:
            return float(value)
        else:
            return value

# SceneItem ===========================================================
class SceneItem(SIObject):

    nodeName = "sceneitem"

    # Xml
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("model", ref.Model.Name)
        self.xml.set("fullName", ref.FullName)
        self.xml.set("type", ref.Type)
        self.xml.set("owners", ref.Owners.GetAsText())

        for prop in ref.Properties:
            xProp = Property(prop)
            self.xml.append(xProp.self.xml)

#######################################################################
# GROUPS
#######################################################################
# Group ===============================================================
class Group(SceneItem):

    nodeName = "group"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("model", ref.Model.Name)

        # Parameters
        for param in ref.Parameters:
            xParam = Parameter(param)
            self.xml.append(xParam.xml)

        # Members
        if OPTIONS["Group_members"]:
            xml_members = SubElement(self.xml, "members", count=str(ref.Members.Count))
            for member in ref.Members:
                branch = ref.IsMember(member, True)
                xml_member = SubElement(xml_members, "member", model=member.Model.Name, name=member.Name, branch=str(branch))

        # Properties & Overrides
        if ref.Properties.Count:
            for prop in ref.Properties:
                if prop.Name.startswith("VisibilityOverride"):
                    continue

                xProp = Property(prop)
                self.xml.append(xProp.xml)

    # ------------------------------------------------------------------
    def generateObject(self, model):

        name = self.xml.get("name")

        group = model.Groups(name)
        if not group:
            group = model.AddGroup(None, name)

        # Parameters
        for xml_param in self.xml.findall("parameter"):
            xParam = Parameter(xml_param)
            xParam.generateObject(group)

        # Properties
        for xml_prop in self.xml.findall("property"):
            name = xml_prop.get("name")
            if name.startswith("VisibilityOverride"):
                continue
            xProp = Property(xml_prop)
            xProp.generateObject(group)

        # Members
        if OPTIONS["Group_members"]:
            members = XSIFactory.CreateObject("XSI.Collection")
            members_branch = XSIFactory.CreateObject("XSI.Collection")

            for xml_member in self.xml.findall("members/member"):
                member_name    = xml_member.get("name")
                member_branch = self.convertVariantType(xml_member.get("branch"), c.siBool)

                member = model.FindChild(member_name)
                if not member:
                     gear.log("Unable to find member : " + member_name, gear.sev_warning)
                     continue

                if member:
                     if member_branch :
                          members_branch.Add(member)
                     else:
                          members.Add(member)

            if members.Count:
                group.AddMember(members)

            if members_branch.Count:
                group.AddMember(members_branch, True)

        return group

#######################################################################
# PROPERTIES
#######################################################################
# Property ============================================================
class Property(SIObject):

    nodeName = "property"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("id", str(ref.ObjectID))
        self.xml.set("name", ref.Name)
        self.xml.set("type", ref.Type)
        self.xml.set("branch", str(ref.Branch))

        for param in ref.Parameters:
            if param.Parent.IsEqualTo(ref):
                xParam = Parameter(param)
                self.xml.append(xParam.xml)

    # ------------------------------------------------------------------
    def generateObject(self, parent):

        d = {}
        d["display"] = "Display Property"

        name = self.xml.get("name")
        type = self.xml.get("type")
        branch = self.convertVariantType(self.xml.get("branch"), c.siBool)

        if type in d:
            type = d[type]

        prop = parent.Properties(name)
        if not prop or (prop and prop.Branch != branch):
            prop = parent.AddProperty(type, branch, name)

        for xml_param in self.xml.findall("parameter"):
            xParam = Parameter(xml_param)
            xParam.generateObject(prop)

        return prop

# Kinematics ==========================================================
class Kinematics(Property):

    nodeName = "kinematics"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        simple = OPTIONS["Parameter_simple"]
        OPTIONS["Parameter_simple"] = True

        # Local
        if OPTIONS["Kinematics_local"]:
            xml_local = SubElement(self.xml, "local")
            for param in ref.Local.Parameters:
                if param.Parent.IsEqualTo(ref.Local):
                    xParam = Parameter(param)

                    if param.ScriptName in ["sclx", "scly", "sclz"] and OPTIONS["Kinematics_removeScaling"]:
                        xParam.xml.set("value", "1")

                    xml_local.append(xParam.xml)

        # Global
        if OPTIONS["Kinematics_global"]:
            xml_global = SubElement(self.xml, "global")
            for s in ["posx", "posy", "posz", "rotx", "roty", "rotz", "sclx", "scly", "sclz"]:
                param = ref.Global.Parameters(s)
                xParam = Parameter(param)

                if s in ["sclx", "scly", "sclz"] and OPTIONS["Kinematics_removeScaling"]:
                    xParam.xml.set("value", "1")

                xml_global.append(xParam.xml)

        # Constraint
        if OPTIONS["Kinematics_constraints"]:
            xml_constraints = SubElement(self.xml, "constraints", count=str(ref.Constraints.Count))
            for cns in ref.Constraints:
                xCns = Constraint(cns)
                xml_constraints.append(xCns.xml)

        OPTIONS["Parameter_simple"] = simple

    def generateObject(self, obj):

        xml_global = self.xml.find("global")
        if xml_global:
            for xml_param in xml_global.findall("parameter"):
                xParam = Parameter(xml_param)
                param = xParam.generateObject(obj.Kinematics.Global)

        xml_local = self.xml.find("local")
        if xml_local:
            for xml_param in xml_local.findall("parameter"):
                xParam = Parameter(xml_param)
                xParam.generateObject(obj.Kinematics.Local)

        xml_constraints = self.xml.find("constraints")
        if xml_constraints:
            for xml_cns in xml_constraints.findall("constraint"):
                xCns = Constraint(xml_cns)
                xCns.generateObject(obj)

    # ------------------------------------------------------------------
    def getLocalTransform(self):
        return self.__getTransform("local")

    def getGlobalTransform(self):
        return self.__getTransform("global")

    def __getTransform(self, type="local"):

        xml_trans = self.xml.find(type)
        if not xml_trans:
            loger.warning("Can't find %s transform inside the kinematic xml"%type, True)
            return None

        d = {}
        for s in ["posx", "posy", "posz", "rotx", "roty", "rotz", "sclx", "scly", "sclz"]:
            xml_param = xmldom.findChildByAttribute(xml_trans, "parameter", "scriptName", s)
            d[s] = float(xml_param.get("value"))

        for s in "xyz":
            d["rot"+s] = XSIMath.DegreesToRadians(d["rot"+s])

        t = XSIMath.CreateTransform()
        t.SetTranslation(XSIMath.CreateVector3(d["posx"],d["posy"],d["posz"]))
        t.SetRotationFromXYZAngles(XSIMath.CreateVector3(d["rotx"],d["roty"],d["rotz"]))
        t.SetScaling(XSIMath.CreateVector3(d["sclx"],d["scly"],d["sclz"]))

        return t

    # ------------------------------------------------------------------
    def setLocalTransform(self, t):
        self.__setTransform("local", t)

    def setGlobalTransform(self, t):
        self.__setTransform("global", t)

    def __setTransform(self, type="local", t=XSIMath.CreateTransform):

        xml_trans = self.xml.find(type)
        if not xml_trans:
            gear.log("Can't find %s transform inside the kinematic xml"%type, gear.sev_warning)
            return None

        d = {"posx":t.PosX, "posy":t.PosY, "posz":t.PosZ,
              "rotx":t.RotX, "roty":t.RotY, "rotz":t.RotZ,
              "sclx":t.SclX, "scly":t.SclY, "sclz":t.SclZ}
        for s in d.keys():
            xml_param = xmldom.findChildByAttribute(xml_trans, "parameter", "scriptName", s)
            xml_param.set("value", str(d[s]))

    localTransform = property(getLocalTransform, setLocalTransform)
    globalTransform = property(getGlobalTransform, setGlobalTransform)

# Constraint ==========================================================
class Constraint(Property):

    nodeName = "constraint"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("type", ref.Type)

        # Constraining
        for obj in ref.Constraining:
            xml_constraining = SubElement(self.xml, "constraining")
            xml_constraining.set("id", str(obj.ObjectID))
            xml_constraining.set("name", obj.Name)
            xml_constraining.set("model", obj.Model.Name)

        # Parameters
        simple = OPTIONS["Parameter_simple"]
        OPTIONS["Parameter_simple"] = True

        for param in ref.Parameters:
            if param.Parent.IsEqualTo(ref):
                xParam = Parameter(param)
                self.xml.append(xParam.xml)

        OPTIONS["Parameter_simple"] = simple

    # ------------------------------------------------------------------
    def generateObject(self, parent):

        type = self.xml.get("type")
        name = self.xml.get("name")
        preset = name[:-4]

        constrainings = XSIFactory.CreateObject("XSI.Collection")
        for xml_constraining in self.xml.findall("constraining"):
          constraining_name = xml_constraining.get("name")
          constraining = parent.Model.FindChild(constraining_name)
          if not constraining:
                gear.log("Unable to retrieve Constraint : Reference is missing - "+constraining_name, gear.sev_warning)
                return False

          constrainings.Add(constraining)

        cns = parent.Kinematics.AddConstraint(preset, constrainings, False)

        for xml_param in self.xml.findall("parameter"):
            xParam = Parameter(xml_param)
            xParam.generateObject(cns)

        return cns

#######################################################################
# PARAMETERS
#######################################################################
# Parameter ===========================================================
class Parameter(SceneItem):

    nodeName = "parameter"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("scriptName", ref.ScriptName)
        self.xml.set("value", str(ref.Value))
        self.xml.set("valueType", str(ref.ValueType))

        if not OPTIONS["Parameter_simple"]:
            self.xml.set("name", ref.Name)
            self.xml.set("min", str(ref.Min))
            self.xml.set("max", str(ref.Max))
            self.xml.set("suggestedMin", str(ref.SuggestedMin))
            self.xml.set("suggestedMax", str(ref.SuggestedMax))
            self.xml.set("capabilities", str(ref.Capabilities))

        if OPTIONS["Parameter_source"]:
            if ref.IsAnimated(c.siFCurveSource):
                self.xml.set("source", "fcurve")
                xFCurve = FCurve(ref.Source)
                self.xml.append(xFCurve.xml)
            elif ref.IsAnimated(c.siExpressionSource):
                self.xml.set("source", "expression")
                xExpr = Expression(ref.Source)
                self.xml.append(xExpr.xml)
            elif ref.IsAnimated(c.siConstraintSource):
                self.xml.set("source", "constraint")
            elif ref.IsAnimated(c.siAnySource):
                self.xml.set("source", "unsupportedSource")

    # ------------------------------------------------------------------
    def generateObject(self, prop):

        d = {}

        # The string values
        for s in ["scriptName", "name", "source"]:
            d[s] = self.xml.get(s, None)

        # The unknown Values
        d["valueType"] = int(self.xml.get("valueType"))
        for s in ["value", "min", "max", "suggestedMin", "suggestedMax"]:
            if s in self.xml.attrib.keys():
                d[s] = self.convertVariantType(self.xml.get(s), d["valueType"])
            else:
                d[s] = None

        # The integer values
        d["capabilities"] = int(self.xml.get("capabilities", c.siPersistable))

        # Apply or create parameter
        param = prop.Parameters(d["scriptName"])
        if param:
            param.Value = d["value"]
        else:
            param = prop.AddParameter2(d["scriptName"], d["valueType"], d["value"], d["min"], d["max"], d["suggestedMin"], d["suggestedMax"], c.siClassifUnknown, d["capabilities"], d["name"])

        # Source
        if d["source"] == "FCurve":
            xml_fcurve = self.xml.find("fcurve")
            fcurve = FCurve(xml_fcurve)
            fcurve.generateObject(param)
        elif d["source"] == "Expression":
            xml_exp = self.xml.find("expression")
            exp = Expression(xml_exp)
            exp.generateObject(param)

        return param


# ProxyParameter ======================================================
class ProxyParameter(Parameter):

    nodeName = "proxyParameter"

    # ------------------------------------------------------------------
    def generateXml(self, ref):
        Parameter.generateXml(self, ref)

        self.xml.set("master", ref.MasterParameter.FullName)

    def generateObject(self, prop):

        master = self.xml.get("master")
        master_param = xsi.Dictionary.GetObject(master)
        if not master_param:
            gear.log("Can't find master parameter : " + master, gear.sev_warning)
            return

        scriptName = self.xml.get("scriptName", None)
        name = self.xml.get("name", None)

        proxyParam = prop.AddProxyParameter(master_parameter, scriptName, name)

        return proxyParam

# FCurve ==============================================================
class FCurve(SceneItem):

    nodeName = "fcurve"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("type", str(ref.Type))
        self.xml.set("extrapolation", str(ref.Extrapolation))
        self.xml.set("interpolation", str(ref.Interpolation))
        self.xml.set("si3dstyle", str(ref.SI3DStyle))

        xml_keys = SubElement(self.xml, "keys", count=str(ref.Keys.Count))
        for key in ref.Keys:
            xml_key = SubElement(xml_keys, "key")
            xml_key.set("index", str(key.Index))
            xml_key.set("time", str(key.Time))
            xml_key.set("value", str(key.Value))
            xml_key.set("leftTanX", str(key.LeftTanX))
            xml_key.set("leftTanY", str(key.LeftTanY))
            xml_key.set("rightTanX", str(key.RightTanY))
            xml_key.set("rightTanY", str(key.RightTanX))
            xml_key.set("interpolation", str(key.Interpolation))

    # ------------------------------------------------------------------
    def generateObject(self, param):

        type = int(self.xml.get("type"))
        interpolation = int(self.xml.get("interpolation"))
        extrapolation = int(self.xml.get("extrapolation"))
        si3Dstyle = self.convertVariantType(self.xml.get("si3dstyle"), c.siBool)

        fcurve = param.AddFCurve(type, interpolation, extrapolation)

        xml_keys = self.xml.find("keys")
        for xml_key in xml_keys.findall("key"):

            fcurve.AddKey(float(xml_key.get("time")), float(xmlKey.get("value")))
            key = fcurve.GetKey(float(xml_key.get("time")), 0)

            key.Interpolation = int(xmlKey.get("interpolation"))
            key.LeftTanX = float(xml_key.get("leftTanX"))
            key.LeftTanY = float(xml_key.get("leftTanY"))
            key.RightTanX = float(xml_key.get("rightTanX"))
            key.RightTanY = float(xml_key.get("rightTanY"))

        return fcurve

# Expression ==========================================================
class Expression(SceneItem):

    nodeName = "expression"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        # Generize definition
        definition = ref.Parameters("Definition").Value
        thisName = ref.Parent3DObject.FullName
        modelName = ref.Parent3DObject.Model.Name
        definition = definition.replace(thisName + ".", "this.")
        definition = definition.replace(modelName + ".", "this_model.")
        self.xml.set("definition", definition)

        # Parameters
        simple = OPTIONS["Parameter_simple"]
        OPTIONS["Parameter_simple"] = True

        for param in ref.Parameters:
            if param.Parent.IsEqualTo(ref):
                xParam = Parameter(param)
                self.xml.append(xParam.xml)

        OPTIONS["Parameter_simple"] = simple

    # ------------------------------------------------------------------
    def generateObject(self, param):

        definition = self.xml.get("definition")
        exp = self.__addExpression(param, definition)

        for xml_param in self.xml.findall("parameter"):
            xParam = Parameter(xml_param)
            xParam.generateObject(exp)

        return exp

    # ------------------------------------------------------------------
    ## Add an expression to given parameter. Log an error if expression is invalid.
    # @param param Parameter - The parameter to apply the expression on.
    # @param exp String - The expression.
    # @return
    def __addExpression(param, exp):

        if not param.Animatable:
            gear.log(param.FullName + " is not animatable", gear.sev_warning)
            return False

        exp = param.AddExpression(str(exp))

        if not param.IsAnimated(c.siExpressionSource):
            gear.log("Invalid Expression on " + param.FullName + ": \r\n" + str(exp), gear.sev_warning)
            return False

        return exp

#######################################################################
# X3DOBJECT
#######################################################################
# X3DObject ===========================================================
class X3DObject(SceneItem):

    nodeName = "x3dobject"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("id", str(ref.ObjectID))
        self.xml.set("name", ref.Name)
        self.xml.set("model", ref.Model.Name)
        self.xml.set("fullName", ref.FullName)
        self.xml.set("type", ref.Type)
        self.xml.set("owners", ref.Owners.GetAsText())

        # Active Primitive
        self.prim = ref.ActivePrimitive
        self.xml_prim = SubElement(self.xml, "primitive")
        if OPTIONS["X3DObject_primitive"]:

            simple = OPTIONS["Parameter_simple"]
            OPTIONS["Parameter_simple"] = True
            for param in self.prim.Parameters:
                if param.Parent.IsEqualTo(self.prim):
                    xParam = Parameter(param)
                    self.xml_prim.append(xParam.xml)

            OPTIONS["Parameter_simple"] = simple

        # Kinematics
        if OPTIONS["X3DObject_kinematics"]:
            self.xKine = Kinematics(ref.Kinematics)
            self.xml.append(self.xKine.xml)

        # Properties
        if OPTIONS["X3DObject_properties"]:
            for prop in ref.Properties:
                if prop.Type in ["kine"] or prop.Name.startswith("VisibilityOverride"):
                    continue

                if OPTIONS["X3DObject_skipBranchProp"] and prop.Branch:
                    continue

                if OPTIONS["X3DObject_properties"] == "all" or prop.Name in OPTIONS["X3DObject_properties"]:

                    xProp = Property(prop)
                    self.xml.append(xProp.xml)

        # Recursive
        if OPTIONS["X3DObject_children"]:
            for child in ref.Children:
                xSIObject = getObject(child)
                self.xml.append(xSIObject.xml)

    # ------------------------------------------------------------------
    def generateObject(self, parent=xsi.ActiveSceneRoot):

        name = self.xml.get("name")

        obj = self.generatePrimitive(parent, name)

        # Primitive
        xml_prim = self.xml.find("primitive")
        if xml_prim:
            for xml_param in xml_prim.findall("parameter"):
                xParam = Parameter(xml_param)
                xParam.generateObject(obj.ActivePrimitive)

        # Kinematics
        xml_kine = self.xml.find("kinematics")
        if xml_kine:
            xKinematics = Kinematics(xml_kine)
            xKinematics.generateObject(obj)

        # Properties
        for xml_prop in self.xml.findall("property"):
            xProp = Property(xml_prop)
            xProp.generateObject(obj)

        for xml_obj in self.xml.findall("x3dobject"):
            xObject = xmlToObject(xml_obj, obj)
            xObject.generateObject(parent)

        return obj

    # ------------------------------------------------------------------
    def getLocalTransform(self):
        return self.__getTransform("local")

    def getGlobalTransform(self):
        return self.__getTransform("global")

    def __getTransform(self, type):
        xml_kine = self.xml.find("kinematics")
        if not xml_kine:
            gear.log("There is no kinematics available on this xml definition", gear.sev_error)
            return False

        xKinematics = Kinematics(xml_kine)

        if type == "local":
            return xKinematics.localTransform
        elif type == "global":
            return xKinematics.globalTransform

    # ------------------------------------------------------------------
    def setLocalTransform(self, t):
        self.__setTransform("local", t)

    def setGlobalTransform(self, t):
        self.__setTransform("global", t)

    def __setTransform(self, type, t):
        xml_kine = self.xml.find("kinematics")
        if not xml_kine:
            gear.log("There is no kinematics available on this xml definition", gear.sev_error)
            return

        xKinematics = Kinematics(xml_kine)

        if type == "local":
            xKinematics.localTransform = t
        elif type == "global":
            xKinematics.globalTransform = t

    localTransform = property(getLocalTransform, setLocalTransform)
    globalTransform = property(getGlobalTransform, setGlobalTransform)

# Model ===============================================================
class Model(X3DObject):

    # ------------------------------------------------------------------
    def generateXml(self, ref):
        X3DObject.generateXml(self, ref)

        self.xml.set("modelkind", str(ref.ModelKind))

        for group in ref.Groups:
            xGroup = Group(group)
            self.xml.append(xGroup.xml)

    # ------------------------------------------------------------------
    def generateObject(self, parent=xsi.ActiveSceneRoot):
        model = X3DObject.generateObject(self, parent)

        for xml_group in self.xml.findall("group"):
            xGroup = Group(xml_group)
            xGroup.generateObject(model)

        return model

    # ------------------------------------------------------------------
    def generatePrimitive(self, parent, name):
        return parent.AddModel(None, name)

# Null ================================================================
class Null(X3DObject):

    # ------------------------------------------------------------------
    def generatePrimitive(self, parent, name):
        return parent.AddNull(name)

#######################################################################
# GEOMETRIES
#######################################################################
# Geometry ============================================================
class Geometry(X3DObject):

    # ------------------------------------------------------------------
    def generateXml(self, ref):
        X3DObject.generateXml(self, ref)

        self.geo = self.prim.Geometry

        # Clusters
        self.xml_clusters = SubElement(self.xml_prim, "clusters", count=str(self.geo.Clusters.Count))
        for cls in self.geo.Clusters:
            xCluster = Cluster(cls)
            self.xml_clusters.append(xCluster.xml)

        # Operator Stack
        if OPTIONS["Geometry_stack"]:
            self.xml_stack = SubElement(self.xml_prim, "stack")
            for nested in self.prim.NestedObjects:
                if nested.Type in ["cls", "parameter"]:
                    continue

                elif nested.Type.endswith("marker"):
                    SubElement(self.xml_stack, "marker", name=nested.Name)

                elif nested.IsClassOf(c.siOperatorID) and (nested.Type in OPTIONS["Geometry_operators"] or OPTIONS["Geometry_operators"] == "all"):
                    if nested.Type == "envelopop":
                        xOp = EnvelopeOp(nested)
                        self.xml_stack.append(xOp.xml)
                    elif nested.Type == "clsctr":
                        xOp = ClusterCenterOp(nested)
                        self.xml_stack.append(xOp.xml)
                    else:
                        xOp = Operator(nested)
                        self.xml_stack.append(xOp.xml)

    # ------------------------------------------------------------------
    def generateObject(self, parent=xsi.ActiveSceneRoot):
        obj = X3DObject.generateObject(self, parent)

        # Clusters
        for xml_cls in self.xml.findall("primitive/clusters/cluster"):
            xCls = Cluster(xml_cls)
            xCls.generateObject(obj)

        # Operators
        modes = ["Modeling", "Shape Modeling", "Animation", "Secondary Shape Modeling"]
        mode = 0
        for xml_child in self.xml.findall("primitive/stack/*"):

            if xml_child.tag == "marker":
                name = xml_child.get("name")
                mode = modes.index(name) + 1

            elif xml_child.tag == "operator":
                type = xml_child.get("type")
                if type == "envelopop":
                    xOp = EnvelopeOp(xml_child)
                    xOp.generateObject(obj, mode)
                elif type == "clsctr":
                    xOp = ClusterCenterOp(xml_child)
                    xOp.generateObject(obj, mode)
                else:
                    gear.log("Unsupported operator type : "+type, gear.sev_warning)

        return obj

# PolygonMesh =========================================================
class PolygonMesh(Geometry):
    pass

# NurbsSurfaceMesh ====================================================
class NurbsSurfaceMesh(Geometry):
    pass

# NurbsCurveList ======================================================
class NurbsCurveList(Geometry):

    # ------------------------------------------------------------------
    def generateXml(self, ref):
        Geometry.generateXml(self, ref)

        for crv in self.geo.Curves:

            point_count = crv.ControlPoints.Count

            if OPTIONS["Geometry_addScaling"]:
                cp = []
                a = crv.ControlPoints.Array
                scl = ref.Kinematics.Global.Transform.Scaling
                for i in range(point_count):
                    cp.append(str(a[0][i] * scl.X))
                    cp.append(str(a[1][i] * scl.Y))
                    cp.append(str(a[2][i] * scl.Z))
                    cp.append(str(1))

                cp = ",".join(cp)

            else:
                cp = ",".join([str(t[i]) for i in range(point_count) for t in crv.ControlPoints.Array])

            xml_crv = SubElement(self.xml_prim, "curve")
            xml_crv.set("index", str(crv.Index))
            xml_crv.set("cp", cp)
            xml_crv.set("ncp", str(point_count))
            xml_crv.set("kn", ",".join([str(i) for i in crv.Knots.Array]))
            xml_crv.set("nkn", str(len(crv.Knots.Array)))
            xml_crv.set("closed", str(self.__isClosed(crv)))
            xml_crv.set("degree", str(crv.Degree))
            #Getting the colors
            rR = self.geo.Parent.Parent.Properties('display').Parameters(12).GetValue2(None)
            rG = self.geo.Parent.Parent.Properties('display').Parameters(13).GetValue2(None)
            rB = self.geo.Parent.Parent.Properties('display').Parameters(14).GetValue2(None)
            xml_crv.set("rColor", str(rR))
            xml_crv.set("gColor", str(rG))
            xml_crv.set("bColor", str(rB))


    # ------------------------------------------------------------------
    def generatePrimitive(self, parent, name):

        cp = []
        ncp = []
        kn = []
        nkn = []
        closed = []
        degree = []

        xml_curves = self.xml.findall("primitive/curve")
        count = len(xml_curves)
        for xml_crv in xml_curves:
            cp.extend(float(d) for d in xml_crv.get("cp").split(","))
            ncp.append(int(xml_crv.get("ncp")))
            kn.extend(float(d) for d in xml_crv.get("kn").split(","))
            nkn.append(int(xml_crv.get("nkn")))
            closed.append(self.convertVariantType(xml_crv.get("closed"), c.siBool))
            degree.append(int(xml_crv.get("degree")))

        if count == 1:
            crv = parent.AddNurbsCurve(cp, kn, closed[0], degree[0], c.siNonUniformParameterization, c.siSINurbs, name)
        else:
            par = [c.siNonUniformParameterization] * count
            crv = parent.AddNurbsCurveList2(count, cp, ncp, kn, nkn, closed, degree, par, c.siSINurbs, name)
        return crv

    # ------------------------------------------------------------------
    def __isClosed(self, crv):
        if crv.Degree ==  3:
            return not crv.ControlPoints.Count == (len(crv.Knots.Array)-2)
        else:
            return not crv.ControlPoints.Count == len(crv.Knots.Array)

    def getPointArray(self):

        cp = []

        xml_curves = self.xml.findall("primitive/curve")
        for xml_crv in xml_curves:
            cp.extend(float(d) for d in xml_crv.get("cp").split(","))

        return cp

#######################################################################
# CLUSTERS AND CLUSTER PROPERTIES
#######################################################################
# Cluster =============================================================
class Cluster(SceneItem):

    nodeName = "cluster"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("type", ref.Type)
        self.xml.set("alwaysComplete", str(ref.IsAlwaysComplete()))

        if not ref.IsAlwaysComplete():
            self.xml.set("elements", ",".join([str(i) for i in ref.Elements.Array]))

    # ------------------------------------------------------------------
    def generateObject(self, parent):

        name = self.xml.get("name")
        type = self.xml.get("type")
        alwaysComplete = self.convertVariantType(self.xml.get("alwaysComplete"), c.siBool)

        elements = None
        if not alwaysComplete:
            elements = [int(i) for i in self.xml.get("elements").split(",")]

        cls = parent.ActivePrimitive.Geometry.AddCluster(type, name, elements)

        return cls

# ClusterProperty =====================================================
class ClusterProperty(SceneItem):

    nodeName = "clusterProperty"

# WeightMap ===========================================================
class WeightMap(ClusterProperty):

    nodeName = "weightMap"

# Projection ==========================================================
class Projection(ClusterProperty):

    nodeName = "projection"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("cluster", ref.Parent.Name)

        # Get the shape array
        uvTuple = ref.Elements.Array
        pnt_count = len(uvTuple[0])

        xml_weights = SubElement(self.xml, "weights", points=str(pnt_count))

        for index in range(pnt_count):
            xml_pnt = SubElement(xml_weights, "point")
            xml_pnt.set("id", str(index))
            xml_pnt.set("U", str(uvTuple[0][index]))
            xml_pnt.set("V", str(uvTuple[1][index]))
            xml_pnt.set("W", str(uvTuple[2][index]))

    # ------------------------------------------------------------------
    def generateObject(self, obj):

        # Get xml Infos
        name = self.xml.get("name")
        cls_name = self.xml.get("cluster")

        xml_weights = self.xml.find("weights")
        pnt_count = int(xml_weights.get("points"))

        if obj.ActivePrimitive.Geometry.Samples.Count != pnt_count:
            gear.log("Point count doesn't match", gear.sev_error)
            return

        # Find Cluster
        cls = obj.ActivePrimitive.Geometry.Clusters(cls_name)
        if not cls:
            cls = obj.ActivePrimitive.Geometry.AddCluster(c.siSampledPointCluster, cls_name)

        # Get or create shape Key
        projection = cls.Properties(name)
        if not projection:
            xsi.CreateProjection(cls, c.siTxtUV, c.siTxtDefaultPlanarXY, None, name)
            projection = cls.Properties(name)

        projection = dynDispatch(projection)

        # retrieve Weights ------------------------------------------
        uvArray = [0.0] * 3 * pnt_count

        for xml_pnt in xml_weights.findall("point"):

            point_index = int(xml_pnt.get("id"))

            uvArray[point_index*3+0] = float(xml_pnt.get("U"))
            uvArray[point_index*3+1] = float(xml_pnt.get("V"))
            uvArray[point_index*3+2] = float(xml_pnt.get("W"))

        # Finalizing ---------------------------------------------
        # Apply Projection
        projection.Elements.Array = uvArray
        xsi.FreezeObj(projection)

        return projection

# VertexColor =========================================================
class VertexColor(ClusterProperty):

    nodeName = "vertexColor"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("cluster", ref.Parent.Name)

        # Get the shape array
        vcTuple = ref.Elements.Array
        pnt_count = len(vcTuple[0])

        xml_weights = SubElement(self.xml, "weights", points=str(pnt_count))

        for index in range(pnt_count):
            xml_pnt = SubElement(xml_weights, "point")
            xml_pnt.set("id", str(index))
            xml_pnt.set("R", str(vcTuple[0][index]))
            xml_pnt.set("G", str(vcTuple[1][index]))
            xml_pnt.set("B", str(vcTuple[2][index]))
            xml_pnt.set("A", str(vcTuple[3][index]))

#######################################################################
# DEFORMERS
#######################################################################
class Operator(SceneItem):

    nodeName = "operator"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("type", ref.Type)

        # Parameters
        for param in ref.Parameters:
            if param.Parent.IsEqualTo(ref):
                xParam = Parameter(param)
                self.xml.append(xParam.xml)

        if OPTIONS["Operator_ports"]:
            # InputPorts
            for port in ref.InputPorts:
                xPort = InputPort(port)
                self.xml.append(xPort.xml)

            # OutputPorts
            for port in ref.OutputPorts:
                xPort = OutputPort(port)
                self.xml.append(xPort.xml)

    # ------------------------------------------------------------------
    def getOperatorFromStack(self, obj, opType, firstOnly=True):

        operators = XSIFactory.CreateObject("XSI.Collection")

        for nested in obj.ActivePrimitive.NestedObjects:
          if nested.IsClassOf(c.siOperatorID):
                if nested.Type == opType:
                     if firstOnly:
                          return nested
                     else:
                          operators.Add(nested)

        if operators.Count:
          return operators

        return False

# Envelope ============================================================
class ClusterCenterOp(Operator):

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        port = OPTIONS["Operator_ports"]
        OPTIONS["Operator_ports"] = False
        Operator.generateXml(self, ref)
        OPTIONS["Operator_ports"] = port

        port = ref.PortAt(3,0,0)
        cls = port.Target2

        port = ref.PortAt(0,1,0)
        target = port.Target2
        obj = target.Parent3DObject

        self.xml.set("cluster", cls.Name)
        self.xml.set("targetName", obj.Name)
        self.xml.set("targetModel", obj.Model.Name)
        self.xml.set("targetID", str(obj.ObjectID))

    # ------------------------------------------------------------------
    def generateObject(self, obj, mode=4):

        cls_name = self.xml.get("cluster")
        target = obj.Model.FindChild(self.xml.get("targetName"))
        cluster = obj.ActivePrimitive.Geometry.Clusters(cls_name)

        op = xsi.ApplyOp("ClusterCenter", cluster.FullName+";"+target.FullName, 0, 0, None, mode)

        return op

# Envelope ============================================================
class EnvelopeOp(Operator):

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        port = OPTIONS["Operator_ports"]
        OPTIONS["Operator_ports"] = False
        Operator.generateXml(self, ref)
        OPTIONS["Operator_ports"] = port

        # Deformers
        deformers = ref.Deformers
        def_count = deformers.Count
        xml_deformers = SubElement(self.xml, "deformers", count=str(def_count))

        for defIndex, deformer in enumerate(deformers):
            xml_deformer = SubElement(xml_deformers, "deformer")
            xml_deformer.set("id", str(defIndex))
            xml_deformer.set("model", deformer.Model.Name)
            xml_deformer.set("name", deformer.Name)

        # Points & Weights ----------------------
        weightsTuple = ref.Weights.Array
        pnt_count = len(weightsTuple[0])

        xml_weights = SubElement(self.xml, "weights", points=str(pnt_count), compressed=str(OPTIONS["Compression"]))

        if OPTIONS["Compression"]:
            xml_weights.text = enc.encodeData(weightsTuple)
        else:
            for pntIndex in range(pnt_count):

                pnt_weights = []
                for defIndex in range(def_count):
                    weight = weightsTuple[defIndex][pntIndex]
                    if weight > 0:
                        pnt_weights.append(str(defIndex)+"="+str(weight))

                xml_pnt = SubElement(xml_weights, "point")
                xml_pnt.set("id", str(pntIndex))
                xml_pnt.set("weights", ",".join(pnt_weights))

    # ------------------------------------------------------------------
    # @param mode Integer - ConstructionMode
    def generateObject(self, obj, pnt_selection=None, mode=2):

        xml_deformers = self.xml.find("deformers")
        def_count = int(xml_deformers.get("count"))

        xml_weights = self.xml.find("weights")
        pnt_count = int(xml_weights.get("points"))

        if obj.ActivePrimitive.Geometry.Points.Count != pnt_count:
            gear.log("Point count doesn't match", gear.sev_error)
            return

        # Get Deformers
        model = obj.Model
        deformers = [None] * def_count
        for xml_deformer in xml_deformers.findall("deformer"):

            def_index = int(xml_deformer.get("id"))
            name = xml_deformer.get("name")

            # Get Deformer
            deformer = model.FindChild(name)
            if not deformer:
                 gear.log("Deformer is missing : " + name, gear.sev_warning)
                 deformers[def_index] = None
            else:
                 deformers[def_index] = deformer

        # Apply or re-apply envelope --------------------------------
        bWasNotEnveloped = not self.getOperatorFromStack(obj, "envelopop")

        cDeformers = XSIFactory.CreateObject("XSI.Collection")
        cDeformers.AddItems(deformers)

        if not cDeformers.Count:
            gear.log("All deformers are missing. Unable to retrieve envelope", gear.sev_warning)
            return

        envelopeOp = obj.ApplyEnvelope(cDeformers)
        def_count = envelopeOp.Deformers.Count

        # Get original weights (if we have no point selection or mesh wasn't enveloped we start from an empty weights array)
        if not pnt_selection or bWasNotEnveloped:
            weights = [0] * pnt_count * envelopeOp.Deformers.Count
        else:
            weightsTuple = envelopeOp.Weights.Array
            weights = [weightsTuple[j][i] for i in range(len(weightsTuple[0])) for j in range(len(weightsTuple))]

        # Get real deformer Index -----------------------------------
        deformers_index = [None] * len(deformers)
        for i, deformer in enumerate(deformers):
            if deformer:
                 deformers_index[i] = self.__getDeformerIndex(envelopeOp, deformer)
            else:
                 deformers_index[i] = -1

        # retrieve Weights ------------------------------------------
        # Compressed datas
        if xml_weights.get("compressed")=="True":

            retrieved_weights = enc.decodeData(compressed.text)

            for point_index in range(pnt_count):

                # if we have a point selection, we only retrieve envelope on selection
                if pnt_selection and (point_index not in pnt_selection):
                    continue

                for deformer_index in range(len(retrieved_weights)):

                    deformer_realIndex = deformers_index[deformer_index]

                    # Skip missing deformer
                    if deformer_realIndex == -1 :
                        continue

                    weights[point_index * iDeformers + deformer_realIndex] = retrieved_weights[deformer_index][point_index]

        # Uncompressed
        else:
            for xml_point in xml_weights.findall("point"):

                 point_index = int(xml_point.get("id"))
                 pnt_weights = xml_point.get("weights").split(",")

                 # if we have a point selection, we only retrieve envelope on selection
                 if pnt_selection and (point_index not in pnt_selection):
                      continue

                 for weight in pnt_weights:

                      if not weight:
                            continue

                      weight_info = weight.split("=")
                      deformer_realIndex = deformers_index[int(weight_info[0])]

                      # Skip missing deformer
                      if deformer_realIndex == -1 :
                            continue

                      weights[point_index * def_count + deformer_realIndex] = float(weight_info[1])


        # Finalizing -------------------------------------------------
        # Apply Weights
        envelopeOp.Weights.Array = weights

        # Rebuilt Envelope to have the good deformers colors and warning
        envelopeOp = self.__rebuiltEnvelope(envelopeOp)

        return envelopeOp

    # ------------------------------------------------------------------
    def __getDeformerIndex(self, envelopeOp, deformer):

        deformers = envelopeOp.Deformers.GetAsText().split(",")

        try:
          index = deformers.index(deformer.FullName)
          return index
        except:
          return -1

    def __rebuiltEnvelope(self, envelopeOp):

        obj = envelopeOp.Parent3DObject
        deformers = envelopeOp.Deformers

        weights = envelopeOp.Weights.Array
        xsi.RemoveFlexEnv(obj)
        envelopeOp = obj.ApplyEnvelope(deformers)
        envelopeOp.Weights.Array = weights

        return envelopeOp

# Shape ===============================================================
class Shape(SceneItem):

    nodeName = "shape"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("name", ref.Name)
        self.xml.set("cluster", ref.Parent.Name)

        # Get the shape array
        shapeTuple = ref.Elements.Array
        pnt_count = len(shapeTuple[0])

        # Get the shape action clip to get the expression applied on the shape
        actionClips = xsi.FindObjects(None, "{12A3EFC6-E543-11D2-B352-00105A1E6CE9}")

        weight = False
        for clip in actionClips:
            clip = dynDispatch(clip)
            shapeAction = clip.NestedObjects("Mixer."+ref.Name)
            if shapeAction:
                weight = clip.NestedObjects(clip.FullName+".weight")
                break

        # dump weight of applied shapeKey
        if weight:
            xParam = Parameter(weight)
            self.xml.append(xParam.xml)

        xml_weights = SubElement(self.xml, "weights", points=str(pnt_count))

        for index in range(pnt_count):

            if shapeTuple[0][index] != 0 or shapeTuple[1][index] != 0 or shapeTuple[2][index] != 0:

                xml_pnt = SubElement(xml_weights, "point")
                xml_pnt.set("id", str(index))
                xml_pnt.set("X", str(shapeTuple[0][index]))
                xml_pnt.set("Y", str(shapeTuple[1][index]))
                xml_pnt.set("Z", str(shapeTuple[2][index]))

    # ------------------------------------------------------------------
    def generateObject(self, obj):

        # Get xml Infos
        name = self.xml.get("name")
        cls_name = self.xml.get("cluster")

        xml_weights = self.xml.find("weights")
        pnt_count = int(xml_weights.get("points"))

        if obj.ActivePrimitive.Geometry.Points.Count != pnt_count:
          gear.log("Point count doesn't match", gear.sev_error)
          return

        # Find Cluster
        cls = obj.ActivePrimitive.Geometry.Clusters(cls_name)
        if not cls:
          cls = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, cls_name)

        # Get or create shape Key
        shapeKey = cls.Properties(name)
        if not shapeKey:
          shapeKey = xsi.StoreShapeKey(cls, name)

        # retrieve Weights ------------------------------------------
        shapeArray = [0] * 3 * pnt_count

        for xml_pnt in xml_weights.findall("point"):

            point_index = int(xml_pnt.get("id"))

            shapeArray[point_index*3+0] = float(xml_pnt.get("X"))
            shapeArray[point_index*3+1] = float(xml_pnt.get("Y"))
            shapeArray[point_index*3+2] = float(xml_pnt.get("Z"))

        # Finalizing ---------------------------------------------
        # Apply Shape Key
        shapeKey.Elements.Array = shapeArray
        xsi.ApplyShapeKey(shapeKey, None, None, 100, None, None, None, 2)
        xsi.FreezeObj(shapeKey)

        return shapeKey

#######################################################################
# PORTS
#######################################################################
class Port(SceneItem):

    nodeName = "port"

    # ------------------------------------------------------------------
    def generateXml(self, ref):

        self.xml.set("index", str(ref.Index))
        self.xml.set("name", ref.Name)
        self.xml.set("isConnected", str(ref.IsConnected))
        self.xml.set("branchGroup", str(ref.BranchGroup))
        self.xml.set("groupIndex", str(ref.GroupIndex))
        self.xml.set("groupInstance", str(ref.GroupInstance))
        self.xml.set("groupName", ref.GroupName)
        if ref.Target2:
            self.xml.set("target", ref.Target2.FullName)

class InputPort(Port):

    nodeName = "inputPort"

    # ------------------------------------------------------------------
    def generateXml(self, ref):
        Port.generateXml(self, ref)

        self.xml.set("optional", str(ref.Optional))

class OutputPort(Port):

    nodeName = "outputPort"

