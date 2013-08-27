'''

    This file is part of GEAR.

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

    Author:     Jeremie Passerin      geerem@hotmail.com
    Company:    Studio Nest (TM)
    Date:       2010 / 11 / 15

'''

## @package gear_Synoptic.biped_body.parameters
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# Built-in
import os

# sn
from gear.xsi import c
import gear.xsi.plugin as plu
import gear.xsi.parameter as par

##########################################################
# ADD PARAMETERS
##########################################################
def addParameters(prop):

    # Path Parameter for the Synoptic
    path = os.path.join(plu.getPluginPath("gear_Synoptic"), "tabs", "_common", "biped_body", "biped_body.htm")
    par.createOrReturnParameters3(prop, "biped_body_path", c.siString, path, None, None, False, False)

    # Selection control parameters
    par.createOrReturnParameters3(prop, "controlers_01_grp", c.siBool, True, None, None, False, False)
    par.createOrReturnParameters3(prop, "controlers_slider_grp", c.siBool, False, None, None, False, False)
    par.createOrReturnParameters3(prop, "controlers_facial_grp", c.siBool, False, None, None, False, False)

    par.createOrReturnParameters3(prop, "quicksel_A", c.siString, "", None, None, False, False)
    par.createOrReturnParameters3(prop, "quicksel_B", c.siString, "", None, None, False, False)
    par.createOrReturnParameters3(prop, "quicksel_C", c.siString, "", None, None, False, False)
    par.createOrReturnParameters3(prop, "quicksel_D", c.siString, "", None, None, False, False)
    par.createOrReturnParameters3(prop, "quicksel_E", c.siString, "", None, None, False, False)
    par.createOrReturnParameters3(prop, "quicksel_F", c.siString, "", None, None, False, False)
