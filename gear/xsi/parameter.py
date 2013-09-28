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

## @package gear.xsi.parameter
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import xml.etree.cElementTree as etree

# SN
from gear.xsi import xsi, c

import gear.xsi.fcurve as fcu

##########################################################
# PARAMETER
##########################################################
# ========================================================
## Set the local limit of given object to min and max
# @param obj X3DObject - The object to set limit on.
# @param params List of String - List of local parameter name to limit. (only rotation and position)\n
# if None, ["rotx", "roty", "rotz", "posx", "posy", "posz"] is used
# @param minimum Double - The minimum value.
# @param maximum Double - The maximum value.
# @return
def setLimit(obj, params=None, minimum=0, maximum=0):

    if params is None:
        params=["rotx", "roty", "rotz", "posx", "posy", "posz"]

    for s in params:
        obj.Kinematics.Local.Parameters(s+"minactive").Value = True
        obj.Kinematics.Local.Parameters(s+"maxactive").Value = True
        obj.Kinematics.Local.Parameters(s+"minlimit").Value = minimum
        obj.Kinematics.Local.Parameters(s+"maxlimit").Value = maximum

# ========================================================
## Set an expression on local parameter of target object equal to source parameter
# @param target X3DObject - The object to apply the expression on.
# @param source X3DObject - The object reference for the expression.
# @param params List of String - List of local parameter name.\n
# if None, ["posx", "posy", "posz", "rotorder", "rotx", "roty", "rotz", "sclx", "scly", "sclz"] is used
# @param addPivot Boolean - True to add the pivot local parameter in the expression.
# @return
def linkLocalParams(target, source, params=None, addPivot=False):

    if params is None:
        params=["posx", "posy", "posz", "rotorder", "rotx", "roty", "rotz", "sclx", "scly", "sclz"]

    for s in params:

        if addPivot and s != "rotorder":
            exp = source.Kinematics.Local.Parameters(s).FullName +" + "+  source.Kinematics.Local.Parameters("pc"+s).FullName
        else:
            exp = source.Kinematics.Local.Parameters(s).FullName

        target.Kinematics.Local.Parameters(s).AddExpression(exp)

# ========================================================
## Set Capabilities of given local parameters to keyable or nonKeyable
# @param obj X3DObject - The object to set.
# @param params List of String - The local parameter to set as keyable. params not in the list will be locked (expression + readonly)\n
# if None, ["posx", "posy", "posz", "rotorder", "rotx", "roty", "rotz", "sclx", "scly", "sclz"] is used
# @return
def setKeyableParameters(objects, params=None):

    if params is None:
        params=["posx", "posy", "posz", "rotorder", "rotx", "roty", "rotz", "sclx", "scly", "sclz"]

     # oMS = FindOrCreateProperty(obj, "MarkingSet")
    localParams = ["posx", "posy", "posz", "rotorder", "rotx", "roty", "rotz", "sclx", "scly", "sclz"]


    if not isinstance(objects, list):
        objects = [objects]

    for s in localParams:

        for obj in objects:
            param = obj.Kinematics.Local.Parameters(s)

            if s in params:
                param.Keyable = True
                # oMS.AddProxyParameter(param, s, s)
            else:
                param.AddExpression("")
                param.Keyable = False
                # param.Animatable = False
                param.ReadOnly = True
                # param.SetLock(c.siLockLevelAll)

# ========================================================
## Add the local parameter of given object to collection
# @param collection XSICollection - The collection to fill up.
# @param obj X3DObject - The object to get the local parameter from.
# @param params List of String - List of local parameter name.\n
# if None, ["posx", "posy", "posz", "rotorder", "rotx", "roty", "rotz", "sclx", "scly", "sclz"] is used
# @return
def addLocalParamToCollection(collection, obj, params=None):

    if params is None:
        params=["posx", "posy", "posz", "rotorder", "rotx", "roty", "rotz", "sclx", "scly", "sclz"]

    for s in params:
        if obj.Kinematics.Local.Parameters(s):
            collection.Add(obj.Kinematics.Local.Parameters(s))

# ========================================================
## Set the rotorder of the object
# @param obj X3DObject - The object to set the rot order on
# @param s String - Value of the rotorder. Possible values : ("XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX")
# @return
def setRotOrder(obj, s="XYZ"):

    a = ["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"]

    if s not in a:
        xsi.LogMessage("Invalid Rotorder : "+s, c.siError)
        return False

    obj.Kinematics.Local.Parameters("rotorder").Value = a.index(s)

# ========================================================
## Create or return the parameter if it already exists
# @param prop Property - The property to add the parameter to.
# @param scriptName String - The scripting name of parameter.
# @param valueType Integer - Parameter Type (siString, siBool, siDouble, siInt4...).
# @param defaultValue Variant - Default value of parameter.
# @param minimum Variant - Minimum value of parameter.
# @param maximum Variant - Maximum value of parameter.
# @param animatable Boolean - Parameter is animatable.
# @param readonly Boolean - Parameter is readonly.
# @return
def createOrReturnParameters3(prop, scriptName, valueType, defaultValue, minimum, maximum, animatable=True, readonly=False):

    if prop.Parameters(scriptName):
        param = prop.Parameters(scriptName)
    else:
        param = prop.AddParameter3(scriptName, valueType, defaultValue, minimum, maximum, animatable, readonly)

    return param


# ========================================================
## Add an expression to given parameter. Log an error if expression is invalid.
# @param param Parameter - The parameter to apply the expression on.
# @param exp String - The expression.
# @return
def addExpression(param, definition):

    if not param.Animatable:
        xsi.LogMessage(param.FullName + " is not animatable", c.siWarning)
        return False

    definition = str(definition)
    exp = param.AddExpression(definition)

    if not param.IsAnimated(c.siExpressionSource):
        xsi.LogMessage("Invalid Expression on " + param.FullName + ": \r\n" + definition, c.siWarning)
        return False
    else:
        param.SetLock(c.siLockLevelAll)

    return exp

# ========================================================
## Convert a variant according to XSI siVariantType.
# @param value String - Value as string.
# @param variantType Int - siVariantType.
# @return
def convertVariantType(value, variantType):

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

##########################################################
# DATA GRID
##########################################################
# ========================================================
## Return a grid data as a dictionary
# @param grid_data GridData
# #return Dictionary
def getDictFromGridData(grid_data):

    data_tuple = grid_data.Data
    if not data_tuple:
        return {}

    datas = {}
    for iRowIndex in range(len(data_tuple[0])):
        datas[data_tuple[0][iRowIndex]] = [data_tuple[1][iRowIndex], data_tuple[2][iRowIndex]]

    return datas

# ========================================================
# Set grid data from given dictionary
# @param grid_data GridData
# @param datas Dictionary
def setDataGridFromDict(grid_data, datas):

    grid_data.BeginEdit()
    grid_data.RowCount = 0

    data_keys = datas.keys()
    data_keys.sort()

    for k in data_keys:
        grid_data.RowCount += 1
        d = [k]
        d.extend(datas[k])
        grid_data.SetRowValues(grid_data.RowCount-1, d)
        grid_data.SetRowLabel(grid_data.RowCount-1, grid_data.RowCount-1)

    grid_data.EndEdit()

##########################################################
# PARAMETER DEFINITION
##########################################################
# ========================================================
class ParamDef(object):

    ## Init Method.
    # @param self
    # @param scriptName String - Parameter scriptname
    # @return ParamDef - The stored parameter definition
    def __init__(self, scriptName):

        self.scriptName = scriptName
        self.value = None
        self.valueType = None

    ## Add a parameter to property using the parameter definition.
    # @param self
    # @param prop Property - The property to add the parameter to.
    def create(self, prop):
        param = prop.AddParameter2(self.scriptName, self.valueType, self.value, self.minimum, self.maximum, self.sugMinimum, self.sugMaximum, self.classification, self.capabilities)

        return param

    ## Return the xml definition of the parameterDef.
    # @param self
    # @param simple Boolean - Treu to only export name, value and valuetype.
    def getAsXml(self, simple=False):

        xml_param = etree.Element("parameter")
        xml_param.set("scriptName", self.scriptName)
        xml_param.set("value", str(self.value))
        xml_param.set("valueType", str(self.valueType))

        if not simple:
            xml_param.set("minimum", self.minimum)
            xml_param.set("maximum", str(self.maximum))
            xml_param.set("sugMinimum", str(self.sugMinimum))
            xml_param.set("sugMaximum", str(self.sugMaximum))
            xml_param.set("classification", str(self.classification))
            xml_param.set("capabilities", str(self.capabilities))

        return xml_param

    def setFromXml(self, xml_param):

        self.scriptName = xml_param.get("scriptName")
        self.valueType = int(xml_param.get("valueType"))
        self.value = convertVariantType(xml_param.get("value"), self.valueType)

        self.minimum = convertVariantType(xml_param.get("minimum", None))
        self.maximum = convertVariantType(xml_param.get("maximum", None))
        self.sugMinimum = convertVariantType(xml_param.get("sugMinimum", None))
        self.sugMaximum = convertVariantType(xml_param.get("sugMaximum", None))

        self.classification = int(xml_param.get("classification", c.siClassifUnknown))
        self.capabilities = int(xml_param.get("capabilities", c.siPersistable))

## Create a parameter definition using the AddParameter2 mapping.\n
# I didn't implement the simple ParamDef class (only ParamDef2 and ParamDef3) beacuase this is some kind of obsolete method in Softimage SDK.
class ParamDef2(ParamDef):

    ## Init Method.
    # @param self
    # @param scriptName String - Parameter scriptname
    # @param valueType Integer - siVariantType
    # @param value Variant - Default parameter value
    # @param minimum Variant - mininum value
    # @param maximum Variant - maximum value
    # @param sugMinimum Variant - suggested mininum value
    # @param sugMaximum Variant - suggested maximum value
    # @param classification Integer - parameter classification
    # @param capabilities Integer - parameter capabilities
    # @return ParamDef - The stored parameter definition
    def __init__(self, scriptName, valueType, value, minimum=None, maximum=None, sugMinimum=None, sugMaximum=None, classification=c.siClassifUnknown, capabilities=c.siPersistable):

        self.scriptName = scriptName
        self.valueType = valueType
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.sugMinimum = sugMinimum
        self.sugMaximum = sugMaximum
        self.classification = classification
        self.capabilities = capabilities

## Create a parameter definition using the AddParameter3 mapping.
class ParamDef3(ParamDef):

    ## Init Method.
    # @param self
    # @param scriptName String - Parameter scriptname
    # @param valueType Integer - siVariantType
    # @param value Variant - Default parameter value
    # @param minimum Variant - mininum value
    # @param maximum Variant - maximum value
    # @param animatable Boolean - parameter is animatable
    # @param readOnly Boolean - parameter is readonly
    # @return ParamDef - The stored parameter definition
    def __init__(self, scriptName, valueType, value, minimum=None, maximum=None, animatable=True, readOnly=False):

        self.scriptName = scriptName
        self.valueType = valueType
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.sugMinimum = minimum
        self.sugMaximum = maximum
        self.classification = c.siClassifUnknown
        self.capabilities = (1 * animatable + 2 * readOnly)

## Create an Fcurve parameter definition.\n
class FCurveParamDef(ParamDef):

    ## Init Method.
    # @param self
    # @param scriptName String - Parameter scriptname
    # @return ParamDef - The stored parameter definition
    def __init__(self, scriptName, keys=None, interpolation=c.siCubicInterpolation, extrapolation=c.siConstantExtrapolation):

        self.scriptName = scriptName
        self.keys = keys
        self.interpolation = interpolation
        self.extrapolation = extrapolation
        self.value = None
        self.valueType = None

    ## Add a parameter to property using the parameter definition.
    # @param self
    # @param prop Property - The property to add the parameter to.
    def create(self, prop):

        param = prop.AddFCurveParameter(self.scriptName)

        if self.keys is not None:
            fcu.drawFCurve(param.Value, self.keys, self.interpolation, self.extrapolation)
        else:
            param.Value.Interpolation = self.interpolation
            param.Value.Interpolation = self.extrapolation

        self.value = param.Value

        return param

    ## Return the xml definition of the parameterDef.
    # @param self
    # @param simple Boolean - Unused, for compatibility only
    def getAsXml(self, simple=False):

        xml_param = etree.Element("fcurveparameter")
        xml_param.set("scriptName", self.scriptName)
        xml_param.set("interpolation", str(self.interpolation))
        xml_param.set("extrapolation", str(self.extrapolation))

        keys = []
        for k in self.keys:
            keys.append( ",".join([str(i) for i in k]) )

        xml_param.set("keys", ";".join(keys))

        return xml_param

    def setFromFCurve(self, fcv):

        self.keys = fcu.getFCurveKeys(fcv)
        self.interpolation = fcv.Interpolation
        self.extrapolation = fcv.Extrapolation

    def setFromXml(self, xml_param):

        self.interpolation = int(xml_param.get("interpolation"))
        self.extrapolation = int(xml_param.get("extrapolation"))
        self.keys = [[float(d) for d in k.split(",")] for k in xml_param.get("keys").split(";")]
            

