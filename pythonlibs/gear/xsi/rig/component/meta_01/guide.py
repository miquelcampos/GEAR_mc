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
    Url:        http://gear.jeremiepasserin.com
    Date:       2010 / 11 / 15

'''

## @package gear.xsi.rig.component.meta_01.guide
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c

from gear.xsi.rig.component.guide import ComponentGuide

# guide info
AUTHOR = "Jeremie Passerin"
URL = "http://www.jeremiepasserin.com"
EMAIL = "geerem@hotmail.com"
VERSION = [1,0,3]
TYPE = "meta_01"
NAME = "meta"
DESCRIPTION = "Metacarpe rig for the hand"

##########################################################
# CLASS
##########################################################
class Guide(ComponentGuide):

    compType = TYPE
    compName = NAME
    description = DESCRIPTION

    author = AUTHOR
    url = URL
    email = EMAIL
    version = VERSION

    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.pick_transform = ["root", "#_loc"]
        self.save_transform = ["root", "#_loc"]
        self.addMinMax("#_loc", 1, -1)

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.locs = self.addLocMulti("#_loc", self.root)

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        self.pStartCtl = self.addParam("startctl", c.siBool, False)
        self.pInterCtl = self.addParam("interctl", c.siBool, False)

    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):

        # --------------------------------------------------
        # Layout
        tab = self.layout.addTab("Options")

        # IK / FK
        group = tab.addGroup("Controlers")
        group.addItem(self.pStartCtl.scriptName, "Create start controler")
        group.addItem(self.pInterCtl.scriptName, "Create inter controlers")

    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):
        return

