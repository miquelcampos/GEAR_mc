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

## @package gear.xmldom
# @author Jeremie Passerin
#
# @brief xml management methods. Work with the cElementTree module

##########################################################
# GLOBAL
##########################################################
# built-in



##########################################################
# METHODS
##########################################################
# ========================================================
## Get the child node with given attribute value.\n
## In cElementTree 1.3 we can use directly the path [@attr='value']\n
## but this is not the version available in Python 2.6.
# @param elem etree.Element
# @param tag String - Child element path.
# @param attr String - Attribute name.
# @param value String - Attribute value.
def findChildByAttribute(elem, tag, attr, value):
    for xml_child in elem.findall(tag):
        if xml_child.get(attr, None) == value:
            return xml_child

    return None

## Get all children nodes with given attribute value.\n
## In cElementTree 1.3 we can use directly the path [@attr='value']\n
## but this is not the version available in Python 2.6.
# @param elem etree.Element
# @param tag String - Child element path.
# @param attr String - Attribute name.
# @param value String - Attribute value.
def findAllChildByAttribute(elem, tag, attr, value):
    xml_children = []
    for xml_child in elem.findall(tag):
        if xml_child.get(attr, None) == value:
            xml_children.append(xml_child)
    return xml_children

# ========================================================
## Pretty print for the cElementTree module.
# @param elem etree.Element - Element to get with nice indentation.
# @param level int - level of indentation.
def indent(elem, level=0):
    i = "\n" + level*" "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + " "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
