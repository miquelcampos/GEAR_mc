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

## @package gear.xsi
# @author Jeremie Passerin, Miquel Campos
#
# @brief main xsi module, xsi constants, preferences mangement

##########################################################
# GLOBAL
##########################################################
# Built-in
import win32com.client

from win32com.client import Dispatch
from win32com.client.dynamic import Dispatch as dynDispatch

from win32com.client import constants
from win32com.client import constants as c

# Constants
Application = Dispatch("XSI.Application").Application
xsi = Dispatch("XSI.Application").Application

XSIFactory = Dispatch("XSI.Factory")
XSIUIToolkit = Dispatch("XSI.UIToolkit")
XSIMath = Dispatch("XSI.Math")
XSIUtils = Dispatch("XSI.Utils")

lm = xsi.LogMessage

# Combo Items
comboItems_rotorder = ["XYZ", 0, "XZY", 1, "YXZ", 2, "YZX", 3, "ZXY", 4, "ZYX", 5]

##########################################################
# PREFERENCES
##########################################################
## XSI Preferences wraper.
class XSIPreferences(object):

    ## Init Method
    # @param self
    def __init__(self):

        self.root = xsi.Preferences
        self.categories = {}
        for categories in self.root.Categories:
            self.categories[categories.Name] = categories.Parameters

    # =====================================================
    ## Set the preference value and return the original value.
    # @param self
    # @param category String - category of preference.
    # @param parameter String - parameter of category.
    # @param value Variant - new value of the parameter.
    # @return Variant - The original value of the parameter.
    def setPrefValue(self, category, parameter, value):
        if category not in self.categories.keys():
            xsi.LogMessage("This category ("+str(category)+")doesn't exist")
            return None

        if not self.categories[category].Parameters(parameter):
            xsi.LogMessage("This parameter ("+str(parameter)+")doesn't exist in this category ("+category+")")
            return None

        oldValue = self.categories[category].Parameter.Value
        self.categories[category].Parameter.Value = value

        return value

    # =====================================================
    ## List user preferences.
    # @param self
    def listUserPref(self):
        prefs = [c.siAutoInspect, c.siCompensationFlag, c.siCustomCommandLibCache,
                    c.siCustomOperatorLibCache, c.siDisplayCallbackLibCache,
                    c.siDisplayLibCache, c.siDisplayPassLibCache, c.siEventLibCache,
                    c.siFilterLibCache, c.siMenuLibCache, c.siPropertyLibCache,
                    c.siRTShaderLibCache, c.siScrCommandLogEnabled, c.siScrCommandLogFileName,
                    c.siScrCommandLogMaxSize, c.siScrCommandLogToFile, c.siScrCommandLogUnlimitedSize,
                    c.siScrLanguage, c.siScrMessageLogEnabled, c.siScrRealTimeMessagingEnabled,
                    c.siTimeDisplayFormatDisplayAsFrames, c.siTimeDisplayFormatDisplayUserFormat,
                    c.siTimeDisplayFormatUserFormat, c.siTimeFormatDefaultFrameFormat,
                    c.siTimeFormatDefaultFrameRate, c.siTransformAxisMode, c.siTransformRefMode,
                    c.siUILayoutDefault]
        for pref in prefs:
            xsi.LogMessage(pref)

    ## List all the categories of preference.
    # @param self
    def listCategories(self):
        for k in self.categories.keys():
            xsi.LogMessage(k)

    ## List all the parameter of given category.
    # @param self
    # @param category String - category to list.
    def listParameters(self, category):
        if category not in self.categories.keys():
            xsi.LogMessage("This category ("+str(category)+")doesn't exist" )
            return False

        for param in self.categories[category]:
            xsi.LogMessage(param.FullName + " : " + str(param.Value))
