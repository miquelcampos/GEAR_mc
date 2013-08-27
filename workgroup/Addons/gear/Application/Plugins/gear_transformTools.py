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

## @package gear_transformTools.py
# @author Jeremie Passerin
# @version 1.0
#

##########################################################
# GLOBAL
##########################################################
# Built_in
from gear.xsi import xsi, c

import gear.xsi.uitoolkit as uit
import gear.xsi.transform as tra

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_transformTools"
    in_reg.Email = "geerem@hotmail.com, hello@miqueltd.com"
    in_reg.URL = "http://www.jeremiepasserin.com, http://www.miqueltd.com "
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_MatchSRT","gear_MatchSRT")

    in_reg.RegisterCommand("gear_MatchT","gear_MatchT")
    in_reg.RegisterCommand("gear_MatchR","gear_MatchR")
    in_reg.RegisterCommand("gear_MatchS","gear_MatchS")

    in_reg.RegisterCommand("gear_MatchRT","gear_MatchRT")
    in_reg.RegisterCommand("gear_MatchSR","gear_MatchSR")
    in_reg.RegisterCommand("gear_MatchST","gear_MatchST")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    xsi.LogMessage(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True

##########################################################
# MATCH TRANSFORM
##########################################################
# ========================================================
def gear_MatchSRT_Execute():

    if not xsi.Selection.Count:
        gear.log("No Selection", gear.sev_error)
        return

    source_object = xsi.Selection(0)
    target_object = uit.pickSession()
    if not target_object:
        return

    tra.matchGlobalTransform(source_object, target_object)

# ========================================================
def gear_MatchT_Execute():

    if not xsi.Selection.Count:
        gear.log("No Selection", gear.sev_error)
        return

    source_object = xsi.Selection(0)
    target_object = uit.pickSession()
    if not target_object:
        return

    tra.matchGlobalTransform(source_object, target_object, True, False, False)

# ========================================================
def gear_MatchR_Execute():

    if not xsi.Selection.Count:
        gear.log("No Selection", gear.sev_error)
        return

    source_object = xsi.Selection(0)
    target_object = uit.pickSession()
    if not target_object:
        return

    tra.matchGlobalTransform(source_object, target_object, False, True, False)

# ========================================================
def gear_MatchS_Execute():

    if not xsi.Selection.Count:
        gear.log("No Selection", gear.sev_error)
        return

    source_object = xsi.Selection(0)
    target_object = uit.pickSession()
    if not target_object:
        return

    tra.matchGlobalTransform(source_object, target_object, False, False, True)

# ========================================================
def gear_MatchRT_Execute():

    if not xsi.Selection.Count:
        gear.log("No Selection", gear.sev_error)
        return

    source_object = xsi.Selection(0)
    target_object = uit.pickSession()
    if not target_object:
        return

    tra.matchGlobalTransform(source_object, target_object, True, True, False)

# ========================================================
def gear_MatchSR_Execute():

    source_object = xsi.Selection(0)
    target_object = uit.pickSession()
    if not target_object:
        return

    tra.matchGlobalTransform(source_object, target_object, False, True, True)

# ========================================================
def gear_MatchST_Execute():

    if not xsi.Selection.Count:
        gear.log("No Selection", gear.sev_error)
        return

    source_object = xsi.Selection(0)
    target_object = uit.pickSession()
    if not target_object:
        return

    tra.matchGlobalTransform(source_object, target_object, True, False, True)