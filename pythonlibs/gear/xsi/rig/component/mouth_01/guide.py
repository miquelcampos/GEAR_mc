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

## @package gear.xsi.rig.component.mouth_01.guide
# @author Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
# gear
from gear.xsi import xsi, c, XSIMath

from gear.xsi.rig.component.guide import ComponentGuide
import gear.xsi.applyop as aop

# guide info
AUTHOR = "Miquel Campos "
URL = "http://www.miqueltd.com"
EMAIL = "hello@miqueltd.com"
VERSION = [1,0,0]
TYPE = "mouth_01"
NAME = "mouth"
DESCRIPTION = "mouth with tongue and lips controls "

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
    
    compatible = ["mouth_01" ]

    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.pick_transform = ["root","jawT", "tongueB", "tongueC", "tongueT", "teethB", "teethT"]
        self.save_transform = ["root", "jawT", "jawC", "tongueB", "tongueC", "tongueT", "tongueBM", "tongueTM", \
        "lip01","lip02", "lip03", "lip04", "lip05", "lip06", "lip07", "lip08", "lip09", "lip10", "lip11", "lip12",\
         "lipR", "lipL", \
         "teethB", "teethT"]
        

    # =====================================================
    ## Add more object to the object definition list.
    # @param self
    def addObjects(self):
        
        #jaw guide
        self.root = self.addRoot()
        self.jawT = self.addLoc("jawT", self.root )
        
        vJawC = XSIMath.CreateVector3((self.root.Kinematics.Global.PosX.Value + self.jawT.Kinematics.Global.PosX.Value) / 2,  \
        (self.root.Kinematics.Global.PosY.Value + self.jawT.Kinematics.Global.PosY.Value) / 2 , \
        (self.root.Kinematics.Global.PosZ.Value + self.jawT.Kinematics.Global.PosZ.Value) / 2)
        
        self.jawC = self.addLoc("jawC", self.root, vJawC)
        
        centers = [self.root, self.jawC, self.jawT]
        self.dispcrv = self.addDispCurve("crv", centers)
        
        #tongue guide, the position are: tongue Base, Center, Tip, Base-Medium, Tip-Medium
        self.tongueB = self.addLoc("tongueB", self.jawT )
        self.tongueC = self.addLoc("tongueC", self.jawT )
        self.tongueT = self.addLoc("tongueT", self.jawT )
        
        vTongueBM = XSIMath.CreateVector3((self.tongueB.Kinematics.Global.PosX.Value + self.tongueC.Kinematics.Global.PosX.Value) / 2,  \
        (self.tongueB.Kinematics.Global.PosY.Value + self.tongueC.Kinematics.Global.PosY.Value) / 2 , \
        (self.tongueB.Kinematics.Global.PosZ.Value + self.tongueC.Kinematics.Global.PosZ.Value) / 2)
        
        vTongueTM = XSIMath.CreateVector3((self.tongueT.Kinematics.Global.PosX.Value + self.tongueC.Kinematics.Global.PosX.Value) / 2,  \
        (self.tongueT.Kinematics.Global.PosY.Value + self.tongueC.Kinematics.Global.PosY.Value) / 2 , \
        (self.tongueT.Kinematics.Global.PosZ.Value + self.tongueC.Kinematics.Global.PosZ.Value) / 2)
        
        self.tongueBM = self.addLoc("tongueBM", self.jawT, vTongueBM )
        self.tongueTM = self.addLoc("tongueTM", self.jawT, vTongueTM )
        
        centers = [self.tongueB, self.tongueBM, self.tongueC, self.tongueTM, self.tongueT]
        self.dispcrv = self.addDispCurve("crv", centers)
        
        #Lips Guide
        def lipVector(X, Y, Z, vectorMultiply):
            x = X * vectorMultiply
            y = Y * vectorMultiply
            z = Z * vectorMultiply
            vLip = XSIMath.CreateVector3(self.tongueT.Kinematics.Global.PosX.Value + x, self.tongueT.Kinematics.Global.PosY.Value + y, self.tongueT.Kinematics.Global.PosZ.Value + z )
            return vLip
        
        #This multiplication value is for by default mouth  size fine tunning. 
        vectorMultiply = 1
        
        #lip position 01
        vLip01 = lipVector(0 , 1 , 1, vectorMultiply) 
        self.lip01 = self.addLoc("lip01", self.jawT, vLip01 )
                
        #lip position 02
        vLip02 = lipVector(1 , 1 , 1, vectorMultiply) 
        self.lip02 = self.addLoc("lip02", self.jawT, vLip02 )
        
        #lip position 03
        vLip03 = lipVector(2 , 1 , 1, vectorMultiply) 
        self.lip03 = self.addLoc("lip03", self.jawT, vLip03 )
        
        #lip position 04
        vLip04 = lipVector(3 , 0 , 1, vectorMultiply) 
        self.lip04 = self.addLoc("lip04", self.jawT, vLip04 )
        vLipL = lipVector(5, 0, 1, vectorMultiply)
        self.lipL = self.addLoc("lipL", self.jawT, vLipL )
        
        centers = [self.lip04, self.lipL]
        self.dispcrv = self.addDispCurve("crv", centers)
        
        #lip position 05
        vLip05 = lipVector(2 , -1 , 1, vectorMultiply) 
        self.lip05 = self.addLoc("lip05", self.jawT, vLip05 )
        
        #lip position 06
        vLip06 = lipVector(1 , -1 , 1, vectorMultiply) 
        self.lip06 = self.addLoc("lip06", self.jawT, vLip06 )
        
        #lip position 07
        vLip07 = lipVector(0 , -1 , 1, vectorMultiply) 
        self.lip07 = self.addLoc("lip07", self.jawT, vLip07 )

        #lip position 08
        vLip08 = lipVector(-1 , -1 , 1, vectorMultiply) 
        self.lip08 = self.addLoc("lip08", self.jawT, vLip08 )
        
        #lip position 09
        vLip09 = lipVector(-2 , -1 , 1, vectorMultiply) 
        self.lip09 = self.addLoc("lip09", self.jawT, vLip09 )
        
        #lip position 10
        vLip10 = lipVector(-3 , 0 , 1, vectorMultiply) 
        self.lip10 = self.addLoc("lip10", self.jawT, vLip10 )
        vLipR = lipVector(-5, 0, 1, vectorMultiply)
        self.lipR = self.addLoc("lipR", self.jawT, vLipR )
        
        centers = [self.lip10, self.lipR]
        self.dispcrv = self.addDispCurve("crv", centers)
        
        #lip position 11
        vLip11 = lipVector(-2 , 1 , 1, vectorMultiply) 
        self.lip11 = self.addLoc("lip11", self.jawT, vLip11 )
        
        #lip position 12
        vLip12 = lipVector(-1 , 1 , 1, vectorMultiply) 
        self.lip12 = self.addLoc("lip12", self.jawT, vLip12 )
        centers = [self.lip01, self.lip02, self.lip03, self.lip04, self.lip05, self.lip06, self.lip07, self.lip08, self.lip09, self.lip10, self.lip11, self.lip12, self.lip01 ]
        self.dispcrv = self.addDispCurve("crv", centers)
        
        
        #teeth guide
        
        self.teethB = self.addLoc("teethB", self.jawT )
        self.teethT = self.addLoc("teethT", self.jawT )
        
        centers = [self.teethB, self.teethT]
        self.dispcrv = self.addDispCurve("crv", centers)
        

        
        