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

## @package gear.xsi.ppg
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import types

from gear.xsi import xsi, c

##########################################################
# PPG LAYOUT
##########################################################
## Dynamic PPG Layout class\n
# Allows the creation of dynamic layout for PPG and still add items to already created tabs, groups or row.\n
# Usefull to generate layout code for the sn_PSet property. Code is in Python !
class PPGLayout(object):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    def __init__(self):

        ## Dictionary of Tab
        self.tabs = {}
        ## List of tab name to be able to get tab in creation order
        self.tabIndex = []

        ## Code list
        self.beforeCode = []
        self.afterCode = []

        ## real PPGLayout value
        self.value = ""

        return

    # -----------------------------------------------------
    ## Add an new tab to layout.
    # @param self
    # @param name String - Tab name.
    # @return Tab - return the newly created Tab. If the name already exists return the existing Tab.
    def addTab(self, name):

        if name in self.tabs:
            tab = self.tabs[name]
        else:
            tab = Tab(name)
            self.tabIndex.append(name)
            self.tabs[name] = tab

        return tab

    # -----------------------------------------------------
    ## Add code to the PPGLayout before the layout itself.
    def setCodeBefore(self, code):
        self.beforeCode.append(code)

    def setCodeAfter(self, code):
        self.afterCode.append(code)

    # -----------------------------------------------------
    ## Get Tab from given index.
    # @param self
    # @param index Integer - Tab index.
    # @return Tab - return the Tab. Return False if it doesn't exists.
    def getTab(self, index=0):
        if index > (len(self.tabIndex) - 1):
            return False
        else:
            return self.tabs[self.tabIndex[index]]

    # -----------------------------------------------------
    ## Get Tab from given name.
    # @param self
    # @param name String - Tab name.
    # @return Tab - return the Tab. Return False if it doesn't exists.
    def getTabByName(self, name):
        if name not in self.tabIndex:
            return False
        else:
            return self.tabs[name]

    # -----------------------------------------------------
    ## Get items from given Tab index.
    # @param self
    # @param index Integer - Tab Index.
    # @return List of LayoutComponent - return the items of Tab. Return False if it doesn't exists.
    def getTabItems(self, index=0):
        tab = self.getTab(index)
        if not tab:
            return []
        else:
            return tab.getItems()

    # -----------------------------------------------------
    ## Get items from given Tab name.
    # @param self
    # @param name String - Tab name.
    # @return List of LayoutComponent - return the items of Tab. Return False if it doesn't exists.
    def getTabItemsByName(self, name):
        tab = self.getTabByName(name)
        if not tab:
            return []
        else:
            return tab.getItems()

    # -----------------------------------------------------
    ## Return the layout code as a string. Code is in Python.
    # @param self
    # @return String - The layout.
    def getValue(self):

        # Before code
        for code in self.beforeCode:
            self.value += code + "\r\n"

        self.value += "\r\n"

        # Layout
        for index in self.tabIndex:
            tab = self.tabs[index]
            self.value += tab.getValue()

        self.value += "\r\n"

        # After code
        for code in self.afterCode:
            self.value += code + "\r\n"


        return self.value

##########################################################
# LAYOUT COMPOUNDS
##########################################################
# ========================================================
## Base class for all layout items
class LayoutComponent(object):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    def __init__(self):

        self.codeBefore = None    ## code to place before the item
        self.codeAfter = None ## code to place after the item
        self.condition = None  ## simple condition to place before the item

        self.args = []

    # -----------------------------------------------------
    ## Add custom code before the item. Code must be in Python.
    # @param self
    # @param code String - code to place before the item.
    def setCodeBefore(self, code):
        self.codeBefore = code + "\r\n"

    # -----------------------------------------------------
    ## Add custom code after the item. Code must be in Python.
    # @param self
    # @param code String - code to place before the item.
    def setCodeAfter(self, code):
        self.codeAfter = code + "\r\n"

    # -----------------------------------------------------
    ## Simple condition to place before the item. Condition must be in Python, the 'If' statement is not needed.
    # @param self
    # @param condition String - code to place before the item.
    def addCondition(self, condition):
        self.condition = condition

    # -----------------------------------------------------
    ## Make sure that all string in the list are in ascii and not unicode.
    # @param self
    # @param items List - list to check
    # @return List - Cleaned list.
    def convertToAscii(self, items):

        new_items = []
        for item in items:
            if isinstance(item, types.UnicodeType):
                new_items.append(item.encode("ascii"))
            elif isinstance(item, list):
                new_items.append(self.convertToAscii(item))
            elif isinstance(item, tuple):
                new_items.append(self.convertToAscii(item))
            else:
                new_items.append(item)

        return new_items

    # -----------------------------------------------------
    ## Add quotemark to string and return the list as a string.
    # @param self
    # @param items List - list to convert
    # @return String
    def getAsString(self, items):

        new_items = []
        for item in items:
            if isinstance(item, str):
                new_items.append("'"+item+"'")
            else:
                new_items.append(str(item))

        return ", ".join(new_items)

# ========================================================
## Base class for all LayoutComponent that can contains some others (like Tab, Group and Row)
class LayoutCompound(LayoutComponent):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    def __init__(self):

        LayoutComponent.__init__(self)

        ## List of all the items included in this LayoutCompound.
        self.items = []

        self.prefixMethod = ""
        self.suffixMethod = ""

    # -----------------------------------------------------
    ## Get the list of items of this LayoutCompound.
    # @param self
    # @return List of Layout Component.
    def getItems(self):
        return self.items

    # -----------------------------------------------------
    ## Append items to the item list of this LayoutCompound.
    # @param self
    # @param items List of LayoutComponent.
    def appendItems(self, items):
        self.items.extend(items)

    # -----------------------------------------------------
    ## Remove a LayoutItem from the item list of this LayoutCompound.
    # @param self
    # @param itemToPop LayoutItem to remove.
    def popItem(self, itemToPop):

        index = None
        for i, item in enumerate(self.items):
            if item == itemToPop:
                index = i
                break

        if index is None:
            xsi.LogMessage("item doesn't belong to LayouCompound", c.siWarning)
            return

        self.items.pop[index]

    # -----------------------------------------------------
    ## Add a Group to this LayoutCompound.
    # @param self
    # @param name String - Group Name.
    # @return Group - The newly created Group.
    def addGroup(self, name):

        group = Group(name)
        self.items.append(group)

        return group

    # -----------------------------------------------------
    ## Add a Row to this LayoutCompound.
    # @param self
    # @return Row - The newly created Row.
    def addRow(self):

        row = Row()
        self.items.append(row)

        return row

    # -----------------------------------------------------
    ## Add an Item to this LayoutCompound.
    # @param self
    # @param scriptName String - the parameter scriptname.
    # @param name String - the parameter display name.
    # @return Item - the newly created Item.
    def addItem(self, scriptName, name=None, uitype=None):

        item = Item(scriptName, name, uitype)
        self.items.append(item)

        return item

    # -----------------------------------------------------
    ## Add an EnumControl to this LayoutCompound.
    # @param self
    # @param scriptName String - the parameter scriptname.
    # @param items List - The item list of the enumcontrol.
    # @param name String - the parameter display name.
    # @param siPPGControlType String - The control type of this EnumControl.
    # @return Item - the newly created EnumControl item.
    def addEnumControl(self, scriptName, items, name=None, siPPGControlType=c.siControlCombo):

        enumControl = EnumControl(scriptName, items, name, siPPGControlType)
        self.items.append(enumControl)

        return enumControl

    # -----------------------------------------------------
    ## Add a FCurve to this LayoutCompound.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param height Integer - The height to display the fcurve.
    # @return Item - the newly created FCurve item.
    def addFCurve(self, scriptName, height=300):

        fcv = FCurve(scriptName, height)
        self.items.append(fcv)

        return fcv

    # -----------------------------------------------------
    ## Add a FCurve to this LayoutCompound. With more option to avoid the use of setAttribute method.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param labelX String - The label at the bottom of the fcurve item.
    # @param labelY String - The label at the left of the fcurve item.
    # @param minX Double - The minimum X value to display the fcurve.
    # @param maxX Double - The maximum X value to display the fcurve.
    # @param minY Double - The minimum Y value to display the fcurve.
    # @param maxY Double - The maximum Y value to display the fcurve.
    # @param gridSpaceX Double - The gridSpace in X value to display the fcurve.
    # @param gridSpaceY Double - The gridSpace in Y value to display the fcurve.
    # @return Item - the newly created FCurve item.
    def addFCurve2(self, scriptName, labelX, labelY, minX, maxX, minY, maxY, gridSpaceX, gridSpaceY):

        fcv = FCurve(scriptName, 300)
        fcv.setAttribute(c.siUIFCurveLabelX, labelX)
        fcv.setAttribute(c.siUIFCurveLabelY, labelY)
        fcv.setAttribute(c.siUIFCurveViewMinX,minX)
        fcv.setAttribute(c.siUIFCurveViewMaxX,maxX)
        fcv.setAttribute(c.siUIFCurveViewMinY,minY)
        fcv.setAttribute(c.siUIFCurveViewMaxY,maxY)
        fcv.setAttribute(c.siUIFCurveGridSpaceX, gridSpaceX)
        fcv.setAttribute(c.siUIFCurveGridSpaceY, gridSpaceY)

        self.items.append(fcv)

        return fcv

    # -----------------------------------------------------
    ## Add a Button to this LayoutCompound.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param name String - The display name of the button.
    # @return Item - the newly created Button item.
    def addButton(self, scriptName, name=None):

        button = Button(scriptName, name)
        self.items.append(button)

        return button

    # -----------------------------------------------------
    ## Add a Color to this LayoutCompound.
    # @param self
    # @param redParamName String - The red parameter scriptname.
    # @param name String - The display name of the color.
    # @param alpha Boolean - True to display a Alpha Channel.
    # @return Item - the newly created Color item.
    def addColor(self, redParamName, name=None, alpha=False):

        color = Color(redParamName, name, alpha)
        self.items.append(color)

        return color

    # -----------------------------------------------------
    ## Add a Spacer to this LayoutCompound.
    # @param self
    # @return Item - the newly created Spacer item.
    def addSpacer(self):

        spacer = Spacer()
        self.items.append(spacer)

        return spacer

    # -----------------------------------------------------
    ## Add a String to this LayoutCompound.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param name String - The parameter display name.
    # @param multiline Boolean - True to display multiline.
    # @param height Integer - height of the widget.
    # @return Item - the newly created String item.
    def addString(self, scriptName, name=None, multiline=False, height=120):

        string = String(scriptName, name, multiline, height)
        self.items.append(string)

        return string

    # -----------------------------------------------------
    ## Return the layout code as a string. Code is in Python.
    # @param self
    # @return String - The layout.
    def getValue(self):

        if not self.items:
            return ""
        else:

            value = ""
            if self.codeBefore is not None:
                value += self.codeBefore

            tabulation = ""
            if self.condition is not None:
                value += "if "+self.condition+":\r\n"
                tabulation = "    "

            self.args = self.convertToAscii(self.args)
            args = self.getAsString(self.args)
            value += tabulation + "layout." + self.prefixMethod + "(" + args + ")\r\n"

            for item in self.items:
                value += tabulation + item.getValue()

            if self.suffixMethod:
                value += tabulation + "layout." + self.suffixMethod + "()\r\n"

            if self.codeAfter is not None:
                value += self.codeAfter

            return value

# ========================================================
## Tab class
class Tab(LayoutCompound):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param name String - Tab name.
    def __init__(self, name):

        LayoutCompound.__init__(self)

        self.name = str(name)
        self.args = [name]

        self.prefixMethod = "AddTab"

# ========================================================
## Group class
class Group(LayoutCompound):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param name String - Group name.
    def __init__(self, name):

        LayoutCompound.__init__(self)

        self.args = [name]

        self.prefixMethod = "AddGroup"
        self.suffixMethod = "EndGroup"

# ========================================================
## Row class
class Row(LayoutCompound):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    def __init__(self):

        LayoutCompound.__init__(self)

        self.prefixMethod = "AddRow"
        self.suffixMethod = "EndRow"

##########################################################
# LAYOUT ITEMS
##########################################################
# ========================================================
## Base class for all LayoutItem (Item, EnumControl, FCurve, Button, Color, Spacer)
class LayoutItem(LayoutComponent):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    def __init__(self):

        LayoutComponent.__init__(self)

        self.attributes = []

        self.methodName = ""

    # -----------------------------------------------------
    ## Set the attribute of an item widget.
    # @param self
    # @param siPPGItemAttribute String - Attribute.
    # @param variant Variant - Value.
    # @return String - The layout.
    def setAttribute(self, siPPGItemAttribute, variant):

        self.attributes.append([siPPGItemAttribute, variant])

    # -----------------------------------------------------
    ## Return the layout code as a string. Code is in Python.
    # @param self
    # @return String - The layout.
    def getValue(self):

        value = ""
        if self.codeBefore is not None:
            value += self.codeBefore

        tabulation = ""

        if self.condition is not None:
            value += "if "+self.condition+":\r\n"
            tabulation = "    "

        self.args = self.convertToAscii(self.args)
        args = self.getAsString(self.args)
        value += tabulation + "item = layout." + self.methodName + "(" + args + ")\r\n"

        for attribute in self.attributes:
            att = self.convertToAscii(attribute)
            att = self.getAsString(att)
            value += tabulation + "item.SetAttribute(" + att + ")\r\n"

        if self.codeAfter is not None:
            value += self.codeAfter

        return value

# ========================================================
## Item class
class Item(LayoutItem):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param name String - The parameter display name.
    def __init__(self, scriptName, name=None, uitype=None):

        LayoutItem.__init__(self)

        if not name:
            name = str(scriptName)

        self.methodName = "AddItem"
        self.args = [scriptName, name, uitype]

# ========================================================
## EnumControl item class
class EnumControl(LayoutItem):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param items List - List of items to display in the enumcontrol.
    # @param name String - The parameter display name.
    # @param siPPGControlType String - widget type.
    def __init__(self, scriptName, items=[], name=None, siPPGControlType=c.siControlCombo):

        LayoutItem.__init__(self)

        if not name:
            name = str(scriptName)

        if isinstance(items, list):
            items = self.convertToAscii(items)
        else:
            items = str(items)


        self.methodName = "AddEnumControl"
        self.args = [scriptName, items, name, str(siPPGControlType)]

# ========================================================
## FCurve item class
class FCurve(LayoutItem):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param height Integer - Height of the fcurve widget.
    def __init__(self, scriptName, height=300):

        LayoutItem.__init__(self)

        self.methodName = "AddFCurve"
        self.args = [scriptName, height]

# ========================================================
## Button item class
class Button(LayoutItem):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param name String - The parameter display name.
    def __init__(self, scriptName, name=None):

        LayoutItem.__init__(self)

        if not name:
            name = str(scriptName)

        self.methodName = "AddButton"
        self.args = [scriptName, name]

# ========================================================
## Spacer item class
class Spacer(LayoutItem):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    def __init__(self):

        LayoutItem.__init__(self)

        self.methodName = "AddSpacer"

# ========================================================
## String item class
class String(LayoutItem):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param scriptName String - The parameter scriptname.
    # @param name String - The parameter display name.
    # @param multiline Boolean - True to display multiline.
    # @param height Integer - height of the widget.
    def __init__(self, scriptName, name=None, multiline=False, height=120):

        LayoutItem.__init__(self)

        self.methodName = "AddString"
        self.args = [scriptName, name, multiline, height]

# ========================================================
## Color item class
class Color(LayoutItem):

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param redParamName String - The red parameter scriptname.
    # @param name String - The parameter display name.
    # @param alpha Boolean - True to display a alpha channel.
    def __init__(self, redParamName, name=None, alpha=False):

        LayoutItem.__init__(self)

        if not name:
            name = str(redParamName)

        self.methodName = "AddColor"
        self.args = [redParamName, name, alpha]

##########################################################
# LOGIC
##########################################################
## Generate PPGLogic code
class PPGLogic:

    # -----------------------------------------------------
    ## Init method.
    # @param self
    # @param propType String - Type of the property. This should always be sn_PSet, no need to set it.
    def __init__(self, propType="gear_PSet"):

        self.propType = propType
        self.globalCode = []
        self.methods = []
        self.value = ""

        self.refresh_method = self.propType+"_OnInit()"

    # -----------------------------------------------------
    ## Add Global code to the logic. For example to import modules. Code must be in Python.
    # @param self
    # @param code String.
    def addGlobalCode(self, code):
        self.globalCode.append(code)

    # -----------------------------------------------------
    ## Add a method to the logic. Code must be in Python.
    # @param self
    # @param name String - method name.
    # @param code String.
    def addMethod(self, name, code):
        self.methods.append([name, code])

    # -----------------------------------------------------
    ## Add onchanged event to the logic. Code must be in Python.
    # @param self
    # @param paramName String - Parameter name.
    # @param code String.
    def addOnChanged(self, paramName, code):
        self.methods.append([paramName+"_OnChanged", code])

    # -----------------------------------------------------
    ## Add onClicked event to the logic. Code must be in Python.
    # @param self
    # @param buttonName String - Button name.
    # @param code String.
    def addOnClicked(self, buttonName, code):
        self.methods.append([buttonName+"_OnClicked", code])

    # -----------------------------------------------------
    ## Add onchanged event that refresh the PPG.
    # @param self
    # @param paramName String - Parameter name.
    def addOnChangedRefresh(self, paramName):
        self.methods.append([paramName+"_OnChanged", self.propType+"_OnInit()"])

    # -----------------------------------------------------
    ## Return the logic code as a string. Code is in Python.
    # @param self
    # @return String - The logic.
    def getValue(self):

        for code in self.globalCode:
            self.value += code+"\r\n\r\n"

        for method in self.methods:
            code = method[1].replace("\n", "\n    ")
            self.value += "def "+self.propType+"_"+method[0]+"():\r\n    "+method[1].replace("\r\n", "\r\n    ")+"\r\n\r\n"

        return self.value
