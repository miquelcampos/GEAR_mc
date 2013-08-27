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

## @package gear_Synoptic.human_face.layout
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
    item = layout.AddItem("controlers_slidersFace_grp", "", "dscontrol")
    item.SetAttribute("class", "button")
    item.SetAttribute(c.siUICaption, "Sliders")
    item.SetAttribute(c.siUIStyle, 0x00001003)
    item.SetAttribute(c.siUINoLabel, True)
    item = layout.AddItem("controlers_upperFace_grp", "", "dscontrol")
    item.SetAttribute("class", "button")
    item.SetAttribute(c.siUICaption, "Upper Face")
    item.SetAttribute(c.siUIStyle, 0x00001003)
    item.SetAttribute(c.siUINoLabel, True)
    item = layout.AddItem("controlers_lowerFace_grp", "", "dscontrol")
    item.SetAttribute("class", "button")
    item.SetAttribute(c.siUICaption, "Lower Face")
    item.SetAttribute(c.siUIStyle, 0x00001003)
    item.SetAttribute(c.siUINoLabel, True)
    layout.EndRow()

    # HTML Page ---------------------
    path = os.path.join(plu.getPluginPath("gear_Synoptic"), "tabs", "_common", "human_face", "human_face.htm")
    prop.Parameters("human_face_path").Value = path
    item = layout.AddItem("human_face_path", "", c.siControlSynoptic)
    item.SetAttribute(c.siUINoLabel, True)
    item.SetAttribute(c.siUICX, 308)
