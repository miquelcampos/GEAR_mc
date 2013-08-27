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

## @package gear.xsi.wireframes
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################

# gear

from gear.xsi import xsi

##########################################################
# SET WIREFRAME COLOR
##########################################################
# ========================================================
## Sets wireframe color in selected objects, according to mouse/key combo
# @param in_mousebutton Integer - 0 Left, 1 Middle, 2 Right
# @param in_keymodifier Integer - See source for information
# @param name String - object name to select
def setWireColor(in_mousebutton=0, color=0):

    colors = [[0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.25098039215686274, 0.25098039215686274, 0.25098039215686274],
        [0.5019607843137255, 0.5019607843137255, 0.5019607843137255],
        [0.6078431372549019, 0.0, 0.1568627450980392],
        [0.0, 0.011764705882352941, 0.37254901960784315],
        [0.0, 0.0, 0.9921568627450981],
        [0.00392156862745098, 0.27450980392156865, 0.10196078431372549],
        [0.15294117647058825, 0.0, 0.2627450980392157],
        [0.7843137254901961, 0.0, 0.7803921568627451],
        [0.5372549019607843, 0.2784313725490196, 0.19215686274509802],
        [0.24313725490196078, 0.13333333333333333, 0.12156862745098039],
        [0.6039215686274509, 0.14509803921568626, 0.00392156862745098],
        [0.9921568627450981, 0.0, 0.0],
        [0.0, 1.0, 0.00392156862745098],
        [0.0, 0.2588235294117647, 0.6],
        [1.0, 1.0, 1.0],
        [1.0, 1.0, 0.00392156862745098],
        [0.38823529411764707, 0.8627450980392157, 1.0],
        [0.2588235294117647, 1.0, 0.6352941176470588],
        [1.0, 0.6862745098039216, 0.6901960784313725],
        [0.8901960784313725, 0.6745098039215687, 0.4745098039215686],
        [1.0, 1.0, 0.38431372549019605],
        [0.0, 0.6, 0.32156862745098036],
        [0.6274509803921569, 0.4117647058823529, 0.1843137254901961],
        [0.6235294117647059, 0.6313725490196078, 0.18823529411764706],
        [0.40784313725490196, 0.6274509803921569, 0.1843137254901961],
        [0.1843137254901961, 0.6313725490196078, 0.36470588235294116],
        [0.1843137254901961, 0.6235294117647059, 0.6274509803921569],
        [0.1843137254901961, 0.4, 0.6313725490196078],
        [0.43529411764705883, 0.1843137254901961, 0.6313725490196078],
        [0.6274509803921569, 0.1843137254901961, 0.40784313725490196]]

    if in_mousebutton:
            xsi.gear_setWireColorRange(in_mousebutton, colors[color])
    else:
        for obj in xsi.Selection:
            if obj.Properties("display") != None:
                if color:
                    xsi.SIMakeLocal(obj.Properties("display"), "siDefaultPropagation")
                else:
                    xsi.DeleteObj(obj.Properties("display"))

                obj.Properties('display').Parameters(12).PutValue2(None, colors[color][0])
                obj.Properties('display').Parameters(13).PutValue2(None, colors[color][1])
                obj.Properties('display').Parameters(14).PutValue2(None, colors[color][2])

