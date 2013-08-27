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

## @package gear_Synoptic.chicken_body.layout
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

##########################################################
# ADD LAYOUT
##########################################################
def addLayout(layout, prop):

    # Buttons ----------------------
    layout.AddRow()
    item = layout.AddItem("controlers_01_grp", "", "dscontrol")
    item.SetAttribute("class", "button")
    item.SetAttribute(c.siUICaption, "Primary")
    item.SetAttribute(c.siUIStyle, 0x00001003)
    item.SetAttribute(c.siUINoLabel, True)
    item = layout.AddItem("controlers_slider_grp", "", "dscontrol")
    item.SetAttribute("class", "button")
    item.SetAttribute(c.siUICaption, "Slider")
    item.SetAttribute(c.siUIStyle, 0x00001003)
    item.SetAttribute(c.siUINoLabel, True)
    item = layout.AddItem("controlers_facial_grp", "", "dscontrol")
    item.SetAttribute("class", "button")
    item.SetAttribute(c.siUICaption, "Facial")
    item.SetAttribute(c.siUIStyle, 0x00001003)
    item.SetAttribute(c.siUINoLabel, True)
    layout.EndRow()

    # HTML Page ---------------------
    path = os.path.join(plu.getPluginPath("gear_Synoptic"), "tabs", "_common", "chicken_body", "chicken_body.htm")
    prop.Parameters("chicken_body_path").Value = path
    item = layout.AddItem("chicken_body_path", "", c.siControlSynoptic)
    item.SetAttribute(c.siUINoLabel, True)
    item.SetAttribute(c.siUICX, 308)
