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
    Date:       2011 / 12 / 5

'''

## @package gear.xsi.rig.component.eyebrow_01.guide
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c, XSIMath

from gear.xsi.rig.component.guide import ComponentGuide

# guide info
AUTHOR = "Jeremie Passerin"
URL = "http://www.jeremiepasserin.com"
EMAIL = "geerem@hotmail.com"
VERSION = [1,0,0]
TYPE = "eyebrow_01"
NAME = "eyebrow"
DESCRIPTION = "Simple eyebrow rig"

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
        self.pick_transform = ["root", "mid_loc", "end_loc"]
        self.save_transform = ["root", "mid_loc", "end_loc"]
        self.save_primitive = ["0_crv", "1_crv", "2_crv"]
        self.save_blade = ["blade", "mid_blade", "end_blade"]

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.mid_loc = self.addLoc("mid_loc", self.root)
        self.end_loc = self.addLoc("end_loc", self.mid_loc)

        self.blade = self.addBlade("blade", self.root, self.mid_loc)
        self.mid_blade = self.addBlade("mid_blade", self.mid_loc, self.end_loc)
        self.end_blade = self.addBlade("end_blade", self.end_loc, self.mid_loc)

        # Disp Curve
        centers = [self.root, self.mid_loc, self.end_loc]
        self.dispcrv = self.addDispCurve("crv", centers)

        # Tangent Curves
        points = [0,-1,0,1,
                  0,-.5,0,1,
                  0,0,0,1,
                  0,.5,0,1,
                  0,1,0,1]
        self.crv = []
        for i, loc in enumerate([self.root, self.mid_loc, self.end_loc]):
            crv = self.addCurve2("%s_crv"%i, loc, points, False, 3, loc.Kinematics.Global.Transform.Translation)
            self.crv.append(crv)

    # =====================================================
    ## Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):
        return

    # =====================================================
    ## Add layout for new parameters.
    # @param self
    def addLayout(self):
        return

    # =====================================================
    ## Add logic for new layout.
    # @param self
    def addLogic(self):
        return


