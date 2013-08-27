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

## @package gear.xsi.rig.logic
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c
import gear.xsi.plugin as plu


SYNOPTIC_TABS_PATH = os.path.join(plu.getPluginPath("gear_synoptic"), "tabs")

##########################################################
# GET ITEMS
##########################################################
# ========================================================
## Get all components settings of the guide model
def getInspectItems(model):
    
    inspect_items = []
    children = {}
    for child in model.FindChildren():
        if child.Properties("settings"):
            children[child.Name[:-5]] = child.Properties("settings").FullName

    for name in sorted(children.keys()):
        inspect_items.append(name)
        inspect_items.append(children[name])

    return inspect_items

# ========================================================
## Synoptic : Get production names
def getSynProdItems():
    return sorted([s for s in os.listdir(SYNOPTIC_TABS_PATH) if "." not in s]*2)

## Synoptic : Get tabs available fors this production
def getSynTabItems(prod_name):
    path = os.path.join(SYNOPTIC_TABS_PATH, prod_name)
    tab_items = []
    for tab in [s for s in os.listdir(path) if '.' not in s]:
        tab_items.append(tab)
        tab_items.append(prod_name+'/'+tab)
    return tab_items

# Synoptic : Get selected tabs
def getSynSelItems(synoptic):
    sel_items = []
    if synoptic:
        for tab in synoptic.split(','):
            sel_items.append(tab)
            sel_items.append(tab)
    return sel_items

##########################################################
# BUTTONS ON CLICKED
##########################################################
# ========================================================
def selectRoots(model):
    roots = model.FindChildren("*_root")
    if roots.Count:
        xsi.SelectObj(roots)

# ========================================================
def synAddTab(tab, synoptic):
    if not tab:
        return synoptic
    
    tabs = []
    if synoptic:
        tabs = synoptic.split(",")

    if tab not in tabs:
        tabs.append(tab)

    return ",".join(tabs)

def synRemTab(tab, synoptic):
    
    if not tab or not synoptic or tab not in synoptic.split(","):
        return synoptic

    tabs = synoptic.split(",")
    tabs.pop(tabs.index(tab))

    return ",".join(tabs)

def synMoveTabUp(tab, synoptic):

    if not tab or not synoptic or tab not in synoptic.split(","):
        return synoptic
    
    tabs = synoptic.split(",")
    i = tabs.index(tab)
    if i == 0:
        return synoptic

    tabs.pop(i)
    tabs.insert(i-1, tab)

    return ",".join(tabs)