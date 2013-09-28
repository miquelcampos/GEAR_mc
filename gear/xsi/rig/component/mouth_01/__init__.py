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

## @package gear.xsi.rig.component.mouth_01
# @author Miquel Campos 
#

##########################################################
# GLOBAL
##########################################################
import os

from gear.xsi import xsi, c, dynDispatch, XSIFactory, XSIMath

from gear.xsi.rig.component import MainComponent

import gear.xsi.vector as vec
import gear.xsi.transform as tra
import gear.xsi.icon as icon
import gear.xsi.parameter as par
import gear.xsi.primitive as pri
import gear.xsi.applyop as aop
import gear.xsi.fcurve as fcu
import gear.xsi.curve as cur

##########################################################
# COMPONENT
##########################################################
## The main component class.
class Component(MainComponent):

    # =====================================================
    # OBJECTS
    # =====================================================
    
    ## Add all the objects needed to create the component.
    # @param self
    def addObjects(self):
    
        # Jaw objects
        self.jawRotCenter = pri.addNullFromPos(self.root, self.getName("jaw_rot_center"), self.guide.apos[2], self.size*.02)
        self.jawTrans = pri.addNullFromPos(self.jawRotCenter, self.getName("jaw_translation"), self.guide.apos[0], self.size*.02)
        self.jawRotBase = pri.addNullFromPos(self.jawTrans, self.getName("jaw_rot_base"), self.guide.apos[0], self.size*.02)
        
        self.addToGroup(self.jawRotCenter, "hidden")
        self.addToGroup(self.jawTrans, "hidden")
        self.addToGroup(self.jawRotBase, "hidden")
        
        self.addShadow(self.jawRotBase, "jaw")
        
        plane = [self.guide.apos[0], self.guide.apos[1], self.guide.apos[2]]
        self.normal = self.getNormalFromPos(plane)
        
        
        
        self.jawContLvl = pri.addNullFromPos(self.root, self.getName("jaw_ctl_Level"), self.guide.apos[1], self.size*.02)
        t = self.jawContLvl.Kinematics.Global.Transform
        self.oAngle = XSIMath.DegreesToRadians( 90)
        self.tmpRot = XSIMath.CreateRotation(self.oAngle, 0.0, 0.0)    
        self.jawControl = self.addCtl(self.jawContLvl, "jaw_ctl", t, self.color_fk,  "circle", w=self.size*.5, ro = self.tmpRot)
        
        self.addToGroup(self.jawContLvl, "hidden")
        
        #Neutral posing
        
        xsi.SetNeutralPose(self.jawRotCenter, c.siSRT)
        xsi.SetNeutralPose(self.jawTrans, c.siSRT)
        
        
        #teeth Objects
        
        plane = [self.guide.pos["root"], self.guide.pos["lip01"], self.guide.pos["tongueB"]]
        self.normal = self.getNormalFromPos(plane)
        self.binormal = self.getBiNormalFromPos(plane)
        
        
        t = tra.getTransformLookingAt(self.guide.pos["teethT"], self.guide.pos["teethB"], self.normal, "zx", 1)        
        self.teeth_lvl = pri.addNull(self.root, self.getName("teeth_lvl"), t)
        self.teeth_lvl.Parameters("primary_icon").Value = 1
        self.teethHead = pri.addNull(self.root, self.getName("teethHead"), t)
        self.teethJaw = pri.addNull(self.jawRotBase, self.getName("teethJaw"), t)
        self.upTeethControl = self.addCtl(self.teeth_lvl, "upTeeth_ctl", t, self.color_fk,  "circle", w=self.size*.2)
        self.downTeethControl = self.addCtl(self.teethJaw, "downTeeth_ctl", t, self.color_fk,  "circle", w=self.size*.2)
        
        self.addToGroup(self.teeth_lvl, "hidden")
        self.addToGroup(self.teethHead, "hidden")
        self.addToGroup(self.teethJaw, "hidden")
        self.addShadow(self.upTeethControl, "upTeeth")
        self.addShadow(self.downTeethControl, "lowTeeth")
        
        
        
        #Lips Objects
        t = tra.getTransformLookingAt(self.guide.pos["teethT"], self.guide.pos["teethB"], self.normal, "zx", 1)        
        self.upLips_lvl = pri.addNull(self.root, self.getName("upLips_lvl"), t)
        self.upLips_lvl.Parameters("primary_icon").Value = 4
        self.upLips_loc = pri.addNull(self.upLips_lvl, self.getName("upLips_loc"), t)
        self.upLipsHead = pri.addNull(self.root, self.getName("upLipsHead"), t)
        self.upLipsJaw = pri.addNull(self.jawRotBase, self.getName("upLipsJaw"), t)
        self.lowLipsJaw_lvl = pri.addNull(self.jawRotBase, self.getName("lowLipsJaw_lvl"), t)
        self.lowLipsJaw = pri.addNull(self.lowLipsJaw_lvl, self.getName("lowLipsJaw"), t)
        
        self.addToGroup(self.upLips_lvl, "hidden")
        self.addToGroup(self.upLipsHead, "hidden")
        self.addToGroup(self.upLipsJaw, "hidden")
        self.addToGroup(self.lowLipsJaw_lvl, "hidden")
        self.addToGroup(self.lowLipsJaw, "hidden")
        self.addToGroup(self.upLips_loc, "hidden")
        
        
        #upper lips
        t = tra.getTransformFromPosition(self.guide.pos["lip01"])
        self.uLip01Upper_ref = pri.addNull(self.upLips_loc, self.getName("uLip01Upper_loc"), t, self.size * .01)
        self.uLip01Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("uLip01Lower_loc"), t, self.size * .01)
        self.uLip01_lvl = pri.addNull(self.root, self.getName("uLip01_lvl"), t, self.size * .01)
        self.uLip01_ctl = self.addCtl(self.uLip01_lvl, "uLip01_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.uLip01_lvl, "hidden")
        self.addToGroup(self.uLip01Upper_ref, "hidden")
        self.addToGroup(self.uLip01Lower_ref, "hidden")
        self.addShadow(self.uLip01_ctl, "uLip01")
        
        
        t = tra.getTransformFromPosition(self.guide.pos["lip02"])
        self.uLip02Upper_ref = pri.addNull(self.upLips_loc, self.getName("uLip02Upper_loc"), t, self.size * .01)
        self.uLip02Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("uLip02Lower_loc"), t, self.size * .01)
        self.uLip02_lvl = pri.addNull(self.root, self.getName("uLip02_lvl"), t, self.size * .01)
        self.uLip02_ctl = self.addCtl(self.uLip02_lvl, "uLip02_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.uLip02_lvl, "hidden")
        self.addToGroup(self.uLip02Upper_ref, "hidden")
        self.addToGroup(self.uLip02Lower_ref, "hidden")
        self.addShadow(self.uLip02_ctl, "uLip02")
        
        t = tra.getTransformFromPosition(self.guide.pos["lip03"])
        self.uLip03Upper_ref = pri.addNull(self.upLips_loc, self.getName("uLip03Upper_loc"), t, self.size * .01)
        self.uLip03Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("uLip03Lower_loc"), t, self.size * .01)
        self.uLip03_lvl = pri.addNull(self.root, self.getName("uLip03_lvl"), t, self.size * .01)
        self.uLip03_ctl = self.addCtl(self.uLip03_lvl, "uLip03_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.uLip03_lvl, "hidden")
        self.addToGroup(self.uLip03Upper_ref, "hidden")
        self.addToGroup(self.uLip03Lower_ref, "hidden")
        self.addShadow(self.uLip03_ctl, "uLip03")
        
        t = tra.getTransformFromPosition(self.guide.pos["lip11"])
        self.uLip11Upper_ref = pri.addNull(self.upLips_loc, self.getName("uLip11Upper_loc"), t, self.size * .01)
        self.uLip11Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("uLip11Lower_loc"), t, self.size * .01)
        self.uLip11_lvl = pri.addNull(self.root, self.getName("uLip11_lvl"), t, self.size * .01)
        self.uLip11_ctl = self.addCtl(self.uLip11_lvl, "uLip11_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.uLip11_lvl, "hidden")
        self.addToGroup(self.uLip11Upper_ref, "hidden")
        self.addToGroup(self.uLip11Lower_ref, "hidden")
        self.addShadow(self.uLip11_ctl, "uLip11")
        
        t = tra.getTransformFromPosition(self.guide.pos["lip12"])
        self.uLip12Upper_ref = pri.addNull(self.upLips_loc, self.getName("uLip12Upper_loc"), t, self.size * .01)
        self.uLip12Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("uLip12Lower_loc"), t, self.size * .01)
        self.uLip12_lvl = pri.addNull(self.root, self.getName("uLip12_lvl"), t, self.size * .01)
        self.uLip12_ctl = self.addCtl(self.uLip12_lvl, "uLip12_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.uLip12_lvl, "hidden")
        self.addToGroup(self.uLip12Upper_ref, "hidden")
        self.addToGroup(self.uLip12Lower_ref, "hidden")
        self.addShadow(self.uLip12_ctl, "uLip12")
        
        
        
        
        #lower Lips
        
        t = tra.getTransformFromPosition(self.guide.pos["lip05"])
        self.lLip05Upper_ref = pri.addNull(self.upLips_loc, self.getName("lLip05Upper_loc"), t, self.size * .01)
        self.lLip05Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("lLip05Lower_loc"), t, self.size * .01)
        self.lLip05_lvl = pri.addNull(self.root, self.getName("lLip05_lvl"), t, self.size * .01)
        self.lLip05_ctl = self.addCtl(self.lLip05_lvl, "lLip05_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.lLip05_lvl, "hidden")
        self.addToGroup(self.lLip05Upper_ref, "hidden")
        self.addToGroup(self.lLip05Lower_ref, "hidden")
        self.addShadow(self.lLip05_ctl, "lLip05")
        
        t = tra.getTransformFromPosition(self.guide.pos["lip06"])
        self.lLip06Upper_ref = pri.addNull(self.upLips_loc, self.getName("lLip06Upper_loc"), t, self.size * .01)
        self.lLip06Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("lLip06Lower_loc"), t, self.size * .01)
        self.lLip06_lvl = pri.addNull(self.root, self.getName("lLip06_lvl"), t, self.size * .01)
        self.lLip06_ctl = self.addCtl(self.lLip06_lvl, "lLip06_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.lLip06_lvl, "hidden")
        self.addToGroup(self.lLip06Upper_ref, "hidden")
        self.addToGroup(self.lLip06Lower_ref, "hidden")
        self.addShadow(self.lLip06_ctl, "lLip06")
        
        t = tra.getTransformFromPosition(self.guide.pos["lip07"])
        self.lLip07Upper_ref = pri.addNull(self.upLips_loc, self.getName("lLip07Upper_loc"), t, self.size * .01)
        self.lLip07Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("lLip07Lower_loc"), t, self.size * .01)
        self.lLip07_lvl = pri.addNull(self.root, self.getName("lLip07_lvl"), t, self.size * .01)
        self.lLip07_ctl = self.addCtl(self.lLip07_lvl, "lLip07_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.lLip07_lvl, "hidden")
        self.addToGroup(self.lLip07Upper_ref, "hidden")
        self.addToGroup(self.lLip07Lower_ref, "hidden")
        self.addShadow(self.lLip07_ctl, "lLip07")
        
        t = tra.getTransformFromPosition(self.guide.pos["lip08"])
        self.lLip08Upper_ref = pri.addNull(self.upLips_loc, self.getName("lLip08Upper_loc"), t, self.size * .01)
        self.lLip08Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("lLip08Lower_loc"), t, self.size * .01)
        self.lLip08_lvl = pri.addNull(self.root, self.getName("lLip08_lvl"), t, self.size * .01)
        self.lLip08_ctl = self.addCtl(self.lLip08_lvl, "lLip08_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.lLip08_lvl, "hidden")
        self.addToGroup(self.lLip08Upper_ref, "hidden")
        self.addToGroup(self.lLip08Lower_ref, "hidden")
        self.addShadow(self.lLip08_ctl, "lLip08")
        
        t = tra.getTransformFromPosition(self.guide.pos["lip09"])
        self.lLip09Upper_ref = pri.addNull(self.upLips_loc, self.getName("lLip09Upper_loc"), t, self.size * .01)
        self.lLip09Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("lLip09Lower_loc"), t, self.size * .01)
        self.lLip09_lvl = pri.addNull(self.root, self.getName("lLip09_lvl"), t, self.size * .01)
        self.lLip09_ctl = self.addCtl(self.lLip09_lvl, "lLip09_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.lLip09_lvl, "hidden")
        self.addToGroup(self.lLip09Upper_ref, "hidden")
        self.addToGroup(self.lLip09Lower_ref, "hidden")
        self.addShadow(self.lLip09_ctl, "lLip09")
       
        
        
        #Corner lips
        
        t = tra.getTransformLookingAt(self.guide.pos["lip04"], self.guide.pos["lipL"], self.normal, "zx", 1)
        self.lLip04Upper_ref = pri.addNull(self.upLips_loc, self.getName("LLip04Upper_loc"), t, self.size * .01)
        self.lLip04Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("LLip04Lower_loc"), t, self.size * .01)
        self.cLip04_lvl = pri.addNull(self.root, self.getName("cLip04_lvl"), t, self.size * .05)
        self.cLip04_ctl = self.addCtl(self.cLip04_lvl, "LLip04_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.cLip04_lvl, "hidden")
        self.addToGroup(self.lLip04Upper_ref, "hidden")
        self.addToGroup(self.lLip04Lower_ref, "hidden")
        self.addShadow(self.cLip04_ctl, "cLip04")
        
        
        t = tra.getTransformLookingAt(self.guide.pos["lip10"], self.guide.pos["lipR"], self.normal, "zx", 1) 
        self.lLip10Upper_ref = pri.addNull(self.upLips_loc, self.getName("RLip10Upper_loc"), t, self.size * .01)
        self.lLip10Lower_ref = pri.addNull(self.lowLipsJaw, self.getName("RLip10Lower_loc"), t, self.size * .01)
        self.cLip10_lvl = pri.addNull(self.root, self.getName("cLip10_lvl"), t, self.size * .05)
        self.cLip10_ctl = self.addCtl(self.cLip10_lvl, "RLip10_ctl", t, self.color_fk,  "cube", w=self.size*.02, h = self.size*.02, d = self.size*.02 )
        self.addToGroup(self.cLip10_lvl, "hidden")
        self.addToGroup(self.lLip10Upper_ref, "hidden")
        self.addToGroup(self.lLip10Lower_ref, "hidden")
        self.addShadow(self.cLip10_ctl, "cLip10")
        
        
        #Tongue
        
        self.oAngle = XSIMath.DegreesToRadians( 90)
        self.tmpRot = XSIMath.CreateRotation(0.0, 0.0, self.oAngle)    
        
        t = tra.getTransformLookingAt(self.guide.pos["tongueB"], self.guide.pos["tongueBM"], self.normal, "zx", 0) 
        self.tongue01_ctl = self.addCtl(self.teethJaw, "tongue01_ctl", t, self.color_fk,  "square", w=self.size*.1, d=self.size*.01, ro=self.tmpRot)
        self.tongue01 = pri.addNull(self.tongue01_ctl, self.getName("tongue01"), t, self.size * .05) 
        self.addShadow(self.tongue01_ctl, "tongue01")
        xsi.SetNeutralPose(self.tongue01_ctl, c.siSRT)
        self.addToGroup(self.tongue01, "hidden")
          
        t = tra.getTransformLookingAt(self.guide.pos["tongueBM"], self.guide.pos["tongueC"], self.normal, "zx", 0)
        self.tongue02_ctl = self.addCtl(self.tongue01, "tongue02_ctl", t, self.color_fk,  "square", w=self.size*.1, d=self.size*.01, ro=self.tmpRot)        
        self.tongue02 = pri.addNull(self.tongue02_ctl, self.getName("tongue02"), t, self.size * .05)
        self.addShadow(self.tongue02_ctl, "tongue02")
        xsi.SetNeutralPose(self.tongue02_ctl, c.siSRT)
        self.addToGroup(self.tongue02, "hidden")
        
        t = tra.getTransformLookingAt(self.guide.pos["tongueC"], self.guide.pos["tongueTM"], self.normal, "zx", 0)
        self.tongue03_ctl = self.addCtl(self.tongue02, "tongue03_ctl", t, self.color_fk,  "square", w=self.size*.1, d=self.size*.01, ro=self.tmpRot)
        self.tongue03 = pri.addNull(self.tongue03_ctl, self.getName("tongue03"), t, self.size * .05)
        self.addShadow(self.tongue03_ctl, "tongue03")
        xsi.SetNeutralPose(self.tongue03_ctl, c.siSRT)
        self.addToGroup(self.tongue03, "hidden")
        
        t = tra.getTransformLookingAt(self.guide.pos["tongueTM"], self.guide.pos["tongueT"], self.normal, "zx", 0) 
        self.tongue04_ctl = self.addCtl(self.tongue03, "tongue04_ctl", t, self.color_fk,  "square", w=self.size*.1, d=self.size*.01, ro=self.tmpRot)
        self.tongue04 = pri.addNull(self.tongue04_ctl, self.getName("tongue04"), t, self.size * .05)
        self.addShadow(self.tongue04_ctl, "tongue04")
        xsi.SetNeutralPose(self.tongue04_ctl, c.siSRT)
        self.addToGroup(self.tongue04, "hidden")
        
        t = tra.getTransformLookingAt(self.guide.pos["tongueT"], self.guide.pos["tongueTM"], self.normal, "zx", 1) 
        self.tongue05_ctl = self.addCtl(self.tongue04, "tongue05_ctl", t, self.color_fk,  "square", w=self.size*.1, d=self.size*.01, ro=self.tmpRot)
        self.tongue05 = pri.addNull(self.tongue05_ctl, self.getName("tongue05"), t, self.size * .05)
        self.addShadow(self.tongue05_ctl, "tongue05")
        xsi.SetNeutralPose(self.tongue05_ctl, c.siSRT)
        self.addToGroup(self.tongue05, "hidden")
        
        
        # # ICE shapes Controlers
        # t = tra.getTransformLookingAt(self.guide.pos["teethT"], self.guide.pos["teethB"], self.normal, "zx", 1)  
        
        
        
        # self.mouthICE_lvl = pri.addNull(self.root, self.getName("mouthICE_lvl"), t)
        # vTrans = XSIMath.CreateVector3()
        # vTrans.Set(0, 0, self.size*.1)
        # t.AddLocalTranslation(vTrans)
        # self.mouthICE_off = pri.addNull(self.mouthICE_lvl, self.getName("mouthICE_off"), t) 
        # self.oAngle = XSIMath.DegreesToRadians( 90)
        # self.tmpRot = XSIMath.CreateRotation(self.oAngle, 0.0, 0.0)            
        # self.mouthICE_ctl = self.addCtl(self.mouthICE_off, "mouthICE_ctl", t, self.color_fk,   "circle", w=self.size*.2, ro = self.tmpRot)
        
        # t = tra.getTransformLookingAt(self.guide.pos["lip04"], self.guide.pos["lipL"], self.normal, "xz", 0) 
        # self.mouthICE_L_off = pri.addNull(self.mouthICE_ctl, self.getName("mouthICE_L_off"), t, self.size * .05) 
        
        # self.mouthICE_L_ctl = self.addCtl(self.mouthICE_L_off, "mouthICE_L_ctl", t, self.color_fk,  "pointer", w=self.size*.1, d=self.size*.1)
        
        # t = tra.getTransformLookingAt(self.guide.pos["lip10"], self.guide.pos["lipR"], self.normal, "xz", 0) 
        # self.mouthICE_R_off = pri.addNull(self.mouthICE_ctl, self.getName("mouthICE_R_off"), t, self.size * .05) 
        
        # self.mouthICE_R_ctl = self.addCtl(self.mouthICE_R_off, "mouthICE_R_ctl", t, self.color_fk,  "pointer", w=self.size*.1, d=self.size*.1)
        
        # self.addToGroup(self.mouthICE_lvl, "hidden")
        # self.addToGroup(self.mouthICE_off, "hidden")
        # self.addToGroup(self.mouthICE_L_off, "hidden")
        # self.addToGroup(self.mouthICE_R_off, "hidden")
        
        
        
        # #upper lip
        # t = tra.getTransformLookingAt(self.guide.pos["teethT"], self.guide.pos["teethB"], self.normal, "zx", 1) 
        # vTrans = XSIMath.CreateVector3()
        # vTrans.Set(0, self.size*.05, self.size*.1)
        # t.AddLocalTranslation(vTrans) 
        # self.upLipICE_off = pri.addNull(self.teeth_lvl, self.getName("upLipICE_off"), t)   
        # self.upLipICE_ctl = self.addCtl(self.upLipICE_off, "upLipICE_ctl", t, self.color_fk,   "boomerang", w=self.size*.1, d=self.size*.1)
        
        # self.addToGroup(self.upLipICE_off, "hidden")
        
        # #upper lips corners
        # self.oAngle = XSIMath.DegreesToRadians( 90)
        # self.tmpRot = XSIMath.CreateRotation(self.oAngle, 0.0, 0.0)   
        # vTrans.Set(self.size*.1, 0, 0)
        # t.AddLocalTranslation(vTrans)
        # self.upLipICE_L_off = pri.addNull(self.upLipICE_ctl, self.getName("upLipICE_L_off"), t)
        # self.upLipICE_L_ctl= self.addCtl(self.upLipICE_L_off, "upLipICE_L_ctl", t, self.color_fk,   "circle", w=self.size*.02, ro = self.tmpRot )
        # vTrans.Set(self.size*-0.2, 0, 0)
        # t.AddLocalTranslation(vTrans)
        # self.upLipICE_R_off = pri.addNull(self.upLipICE_ctl, self.getName("upLipICE_R_off"), t)
        # self.upLipICE_R_ctl= self.addCtl(self.upLipICE_R_off, "upLipICE_R_ctl", t, self.color_fk,   "circle", w=self.size*.02, ro = self.tmpRot)
        
        # self.addToGroup(self.upLipICE_L_off, "hidden")
        # self.addToGroup(self.upLipICE_R_off, "hidden")
        
        # #lower lip
        # t = tra.getTransformLookingAt(self.guide.pos["teethT"], self.guide.pos["teethB"], self.normal, "zx", 1) 
        # vTrans = XSIMath.CreateVector3()
        # vTrans.Set(0, self.size* -0.05, self.size*.1)
        # t.AddLocalTranslation(vTrans) 
        # self.downLipICE_off = pri.addNull(self.teethJaw, self.getName("downLipICE_off"), t)  
        # self.oAngle = XSIMath.DegreesToRadians( 180)
        # self.tmpRot = XSIMath.CreateRotation(self.oAngle, 0.0, 0.0)          
        # self.downLipICE_ctl = self.addCtl(self.downLipICE_off, "downLipICE_ctl", t, self.color_fk,    "boomerang", w=self.size*.1, d=self.size*.1, ro = self.tmpRot)
        
        # self.addToGroup(self.downLipICE_off, "hidden")
        
        # #lower lips corners
        # self.oAngle = XSIMath.DegreesToRadians( 90)
        # self.tmpRot = XSIMath.CreateRotation(self.oAngle, 0.0, 0.0)   
        # vTrans.Set(self.size*.1, 0, 0)
        # t.AddLocalTranslation(vTrans)
        # self.downLipICE_L_off = pri.addNull(self.downLipICE_ctl, self.getName("downLipICE_L_off"), t)
        # self.downLipICE_L_ctl= self.addCtl(self.downLipICE_L_off, "downLipICE_L_ctl", t, self.color_fk,   "circle", w=self.size*.02, ro = self.tmpRot)
        # vTrans.Set(self.size*-0.2, 0, 0)
        # t.AddLocalTranslation(vTrans)
        # self.downLipICE_R_off = pri.addNull(self.downLipICE_ctl, self.getName("downLipICE_R_off"), t)
        # self.downLipICE_R_ctl= self.addCtl(self.downLipICE_R_off, "downLipICE_R_ctl", t, self.color_fk,   "circle", w=self.size*.02, ro = self.tmpRot)    
        
        # self.addToGroup(self.downLipICE_L_off, "hidden")
        # self.addToGroup(self.downLipICE_R_off, "hidden")
        
       
        
       
        
    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):
        
        
    
    
        # Anim -------------------------------------------
        # Default parameter to get a better display in the keying panel
        self.pFullName = self.addAnimParam(self.fullName, c.siString, self.fullName, None, None, None, None, False, True, True)
        
        #lips
        self.sticky_Lips = self.addAnimParam("sticky_Lips", c.siDouble, 0, 0, 1, 0, 1)
        self.lips_compression = self.addAnimParam("lips_compression", c.siDouble, 0.2, 0, 1, 0, 1)
        self.lips_upperTranslation = self.addAnimParam("lips_upperTranslation", c.siDouble, 0, -1, 1, -10, 10)
        self.lips_lowerTranslation = self.addAnimParam("lips_lowerTranslation", c.siDouble, 0, -1, 1, -10, 10)
        self.lips_upperOffset = self.addAnimParam("lips_upperOffset", c.siDouble, 0, -1, 1, -10, 10)
        self.lips_lowerOffset = self.addAnimParam("lips_lowerOffset", c.siDouble, 0, -1, 1, -10, 10)
        
        
      
        #Setup -------------------------------------------
        #Jaw parameters
        self.mult_jaw_trans_Z = self.addSetupParam("mult_jaw_trans_Z", c.siDouble, 2, 0, None, 0, 20)
        self.mult_jaw_rot_X = self.addSetupParam("mult_jaw_rot_X", c.siDouble, 30, 0, None, 0, 50)
        self.mult_jaw_rot_Y = self.addSetupParam("mult_jaw_rot_Y", c.siDouble, 15, 0, None, 0, 50)
        self.mult_jaw_rot_Z = self.addSetupParam("mult_jaw_rot_Z", c.siDouble, 30, 0, None, 0, 50)
        
        
        #teeth parameters
        self.teeth_jaw_head = self.addSetupParam("follow_head_jaw", c.siDouble, 0,0, None, 0, 1)
        self.teeth_jaw_head_multi = self.addSetupParam("follow_head_jaw_multi", c.siDouble, 4,0, None, 0, 8)
        
        #lips parameters
        self.upLips_jaw_head = self.addSetupParam("follow_head_jaw", c.siDouble, 0.2,0, None, 0, 1)
        self.upLips_jaw_head_multi = self.addSetupParam("follow_head_jaw_multi", c.siDouble, 4,0, None, 0, 8)
        
        #lips profile
        self.lip_01 = self.addSetupParam("lip_01", c.siDouble, 1, 0, 1, 0, 1)
        self.lip_02 = self.addSetupParam("lip_02", c.siDouble, 0.95, 0, 1, 0, 1)
        self.lip_03 = self.addSetupParam("lip_03", c.siDouble, 0.8, 0, 1, 0, 1)
        self.lip_04 = self.addSetupParam("lip_04", c.siDouble, 0.5, 0, 1, 0, 1)
        self.lip_05 = self.addSetupParam("lip_05", c.siDouble, 0.2, 0, 1, 0, 1)
        self.lip_06 = self.addSetupParam("lip_06", c.siDouble, 0.05, 0, 1, 0, 1)
        self.lip_07 = self.addSetupParam("lip_07", c.siDouble, 0, 0, 1, 0, 1)
        self.lip_08 = self.addSetupParam("lip_08", c.siDouble, 0.05, 0, 1, 0, 1)
        self.lip_09 = self.addSetupParam("lip_09", c.siDouble, 0.2, 0, 1, 0, 1)
        self.lip_10 = self.addSetupParam("lip_10", c.siDouble, 0.5, 0, 1, 0, 1)
        self.lip_11 = self.addSetupParam("lip_11", c.siDouble, 0.8, 0, 1, 0, 1)
        self.lip_12 = self.addSetupParam("lip_12", c.siDouble, 0.95, 0, 1, 0, 1)
        

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):
        
        
        
        
        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)

        # Lips
        group = tab.addGroup("Lips")
        group.addItem(self.sticky_Lips.ScriptName, "Quick Sticky Lips")
        group.addItem(self.lips_compression.ScriptName, "Compression")
        group.addItem(self.lips_upperTranslation.ScriptName, "Upper Auto Translation")
        group.addItem(self.lips_lowerTranslation.ScriptName, "Lower Auto Translation")
        group.addItem(self.lips_upperOffset.ScriptName, "Upper Offset")
        group.addItem(self.lips_lowerOffset.ScriptName, "Lower Offset")
        
        # Setup ------------------------------------------
        # Jaw 
        tab = self.setup_layout.addTab(self.name)
        group = tab.addGroup("Jaw")
        group.addItem(self.mult_jaw_trans_Z.ScriptName, "mult_jaw_trans_Z")
        group.addItem(self.mult_jaw_rot_X.ScriptName, "mult_jaw_rot_X")
        group.addItem(self.mult_jaw_rot_Y.ScriptName, "mult_jaw_rot_Y")
        group.addItem(self.mult_jaw_rot_Z.ScriptName, "mult_jaw_rot_Z")
        
        #Teeth
        group = tab.addGroup("Teeth")
        group.addItem(self.teeth_jaw_head.ScriptName, "follow_jaw_head")
        group.addItem(self.teeth_jaw_head_multi.ScriptName, "follow_jaw_head_multi")
        
        #Lips
        group = tab.addGroup("Lips")
        group.addItem(self.upLips_jaw_head.ScriptName, "follow_jaw_head")
        group.addItem(self.upLips_jaw_head_multi.ScriptName, "follow_jaw_head_multi")
        
        #Lips profile
        group = tab.addGroup("Lips profile")
        group.addItem(self.lip_01.ScriptName, "Lip 01")
        group.addItem(self.lip_02.ScriptName, "Lip 02")
        group.addItem(self.lip_03.ScriptName, "Lip 03")
        group.addItem(self.lip_04.ScriptName, "Lip 04")
        group.addItem(self.lip_05.ScriptName, "Lip 05")
        group.addItem(self.lip_06.ScriptName, "Lip 06")
        group.addItem(self.lip_07.ScriptName, "Lip 07")
        group.addItem(self.lip_08.ScriptName, "Lip 08")
        group.addItem(self.lip_09.ScriptName, "Lip 09")
        group.addItem(self.lip_10.ScriptName, "Lip 10")
        group.addItem(self.lip_11.ScriptName, "Lip 11")
        group.addItem(self.lip_12.ScriptName, "Lip 12")


    ## Define the logic of the anim and setup properties.
    # @param self
    def addLogic(self):
        return

    # =====================================================
    # OPERATORS
    # =====================================================
    ## Apply operators, constraints, expressions to the hierarchy.\n
    # In order to keep the code clean and easier to debug,
    # we shouldn't create any new object in this method.
    # @param self
    def addOperators(self):
        
        
    
        #Jaw Operators
        par.addExpression(self.jawRotCenter.Kinematics.Local.Parameters("rotz"), self.jawControl.Kinematics.Local.Parameters("rotz").FullName  )
        par.addExpression(self.jawTrans.Kinematics.Local.Parameters("posz"), self.jawControl.Kinematics.Local.Parameters("posz").FullName + " *" + self.mult_jaw_trans_Z.FullName )
        par.addExpression(self.jawRotBase.Kinematics.Local.Parameters("rotx"), "(" + self.jawControl.Kinematics.Local.Parameters("posy").FullName + " *" + self.mult_jaw_rot_X.FullName + ") * -1")
        par.addExpression(self.jawRotBase.Kinematics.Local.Parameters("roty"),  self.jawControl.Kinematics.Local.Parameters("posx").FullName + " *" + self.mult_jaw_rot_Y.FullName )
        par.addExpression(self.jawRotBase.Kinematics.Local.Parameters("rotz"),  self.jawControl.Kinematics.Local.Parameters("posx").FullName + " *" + self.mult_jaw_rot_Z.FullName )
         
        oAxis = [ "posx", "posy", "posz"]
         
        par.setLimit( self.jawControl, oAxis, -1, 1)
         
         
        #teeth
        self.intePose01 = aop.sn_interpose_op(self.teeth_lvl, self.teethHead, self.teethJaw )
        
        par.addExpression(self.intePose01.Parameters("blend_pos"), "MIN( MAX((" + self.jawControl.Kinematics.Local.Parameters("posy").FullName + "*" + self.upLips_jaw_head_multi.FullName + ")+"  + self.sticky_Lips.FullName + "+" + self.upLips_jaw_head.FullName + "+ abs(" + self.jawControl.Kinematics.Local.Parameters("posx").FullName + " ) , 0 + " + self.upLips_jaw_head.FullName + " + "  + self.sticky_Lips.FullName  + "), 1 )"  )
        par.addExpression(self.intePose01.Parameters("blend_dir"), "MIN( MAX((" + self.jawControl.Kinematics.Local.Parameters("posy").FullName + "*" + self.upLips_jaw_head_multi.FullName + ")+"   + self.sticky_Lips.FullName + "+" + self.upLips_jaw_head.FullName + "+ abs(" + self.jawControl.Kinematics.Local.Parameters("posx").FullName + " ), abs(" + self.jawControl.Kinematics.Local.Parameters("posx").FullName +  ")+" + self.upLips_jaw_head.FullName + "+ "  + self.sticky_Lips.FullName  +" ), 1 )"  )
        par.addExpression(self.intePose01.Parameters("blend_upv"), "MIN( MAX((" + self.jawControl.Kinematics.Local.Parameters("posy").FullName + "*" + self.upLips_jaw_head_multi.FullName + ")+"  + self.sticky_Lips.FullName + "+" + self.upLips_jaw_head.FullName + "+ abs(" + self.jawControl.Kinematics.Local.Parameters("posx").FullName + " ) , 0 + " + self.upLips_jaw_head.FullName + " + "  + self.sticky_Lips.FullName  + "), 1 )"  )
        
        
        
        #lips
                
        self.intePose02 = aop.sn_interpose_op(self.upLips_lvl, self.upLipsHead, self.upLipsJaw )
        
        par.addExpression(self.intePose02.Parameters("blend_pos"), "MIN( MAX((" + self.jawControl.Kinematics.Local.Parameters("posy").FullName + "*" + self.upLips_jaw_head_multi.FullName + ")+"  + self.sticky_Lips.FullName + "+" + self.upLips_jaw_head.FullName + "+ abs(" + self.jawControl.Kinematics.Local.Parameters("posx").FullName + " ) , 0 + " + self.upLips_jaw_head.FullName + " + "  + self.sticky_Lips.FullName  + "), 1 )"  )
        par.addExpression(self.intePose02.Parameters("blend_dir"), "MIN( MAX((" + self.jawControl.Kinematics.Local.Parameters("posy").FullName + "*" + self.upLips_jaw_head_multi.FullName + ")+"   + self.sticky_Lips.FullName + "+" + self.upLips_jaw_head.FullName + "+ abs(" + self.jawControl.Kinematics.Local.Parameters("posx").FullName + " ), abs(" + self.jawControl.Kinematics.Local.Parameters("posx").FullName +  ")+" + self.upLips_jaw_head.FullName + "+ "  + self.sticky_Lips.FullName  +" ), 1 )"  )
        par.addExpression(self.intePose02.Parameters("blend_upv"), "MIN( MAX((" + self.jawControl.Kinematics.Local.Parameters("posy").FullName + "*" + self.upLips_jaw_head_multi.FullName + ")+"  + self.sticky_Lips.FullName + "+" + self.upLips_jaw_head.FullName + "+ abs(" + self.jawControl.Kinematics.Local.Parameters("posx").FullName + " ) , 0 + " + self.upLips_jaw_head.FullName + " + "  + self.sticky_Lips.FullName  + "), 1 )"  )
        
        
        #Lips profile contrains
        self.cnsLower01 = aop.poseCns(self.uLip01_lvl, self.uLip01Lower_ref, True)
        self.cnsUpper01 = aop.poseCns(self.uLip01_lvl, self.uLip01Upper_ref, True)        
        par.addExpression(self.cnsUpper01.Parameters("blendweight"),  self.lip_01.FullName   )
        self.cnsLower01.Parameters("cnsscl").Value = False
        self.cnsUpper01.Parameters("cnsscl").Value = False
        
        self.cnsLower02 = aop.poseCns(self.uLip02_lvl, self.uLip02Lower_ref, True)
        self.cnsUpper02 = aop.poseCns(self.uLip02_lvl, self.uLip02Upper_ref, True)        
        par.addExpression(self.cnsUpper02.Parameters("blendweight"),  self.lip_02.FullName    )
        self.cnsLower02.Parameters("cnsscl").Value = False
        self.cnsUpper02.Parameters("cnsscl").Value = False
        
        self.cnsLower03 = aop.poseCns(self.uLip03_lvl, self.uLip03Lower_ref, True)
        self.cnsUpper03 = aop.poseCns(self.uLip03_lvl, self.uLip03Upper_ref, True)        
        par.addExpression(self.cnsUpper03.Parameters("blendweight"),  self.lip_03.FullName  )
        self.cnsLower03.Parameters("cnsscl").Value = False
        self.cnsUpper03.Parameters("cnsscl").Value = False
        
        self.cnsLower04 = aop.poseCns(self.cLip04_lvl, self.lLip04Lower_ref, True)
        self.cnsUpper04 = aop.poseCns(self.cLip04_lvl, self.lLip04Upper_ref, True)        
        par.addExpression(self.cnsUpper04.Parameters("blendweight"),  self.lip_04.FullName    )
        self.cnsLower04.Parameters("cnsscl").Value = False
        self.cnsUpper04.Parameters("cnsscl").Value = False
        
        self.cnsLower05 = aop.poseCns(self.lLip05_lvl, self.lLip05Lower_ref, True)
        self.cnsUpper05 = aop.poseCns(self.lLip05_lvl, self.lLip05Upper_ref, True)        
        par.addExpression(self.cnsUpper05.Parameters("blendweight"),  self.lip_05.FullName    )
        self.cnsLower05.Parameters("cnsscl").Value = False
        self.cnsUpper05.Parameters("cnsscl").Value = False
        
        self.cnsLower06 = aop.poseCns(self.lLip06_lvl, self.lLip06Lower_ref, True)
        self.cnsUpper06 = aop.poseCns(self.lLip06_lvl, self.lLip06Upper_ref, True)        
        par.addExpression(self.cnsUpper06.Parameters("blendweight"),  self.lip_06.FullName    )
        self.cnsLower06.Parameters("cnsscl").Value = False
        self.cnsUpper06.Parameters("cnsscl").Value = False
        
        self.cnsLower07 = aop.poseCns(self.lLip07_lvl, self.lLip07Lower_ref, True)
        self.cnsUpper07 = aop.poseCns(self.lLip07_lvl, self.lLip07Upper_ref, True)        
        par.addExpression(self.cnsUpper07.Parameters("blendweight"),  self.lip_07.FullName    )
        self.cnsLower07.Parameters("cnsscl").Value = False
        self.cnsUpper07.Parameters("cnsscl").Value = False
        
        self.cnsLower08 = aop.poseCns(self.lLip08_lvl, self.lLip08Lower_ref, True)
        self.cnsUpper08= aop.poseCns(self.lLip08_lvl, self.lLip08Upper_ref, True)        
        par.addExpression(self.cnsUpper08.Parameters("blendweight"),  self.lip_08.FullName    )
        self.cnsLower08.Parameters("cnsscl").Value = False
        self.cnsUpper08.Parameters("cnsscl").Value = False
        
        self.cnsLower09 = aop.poseCns(self.lLip09_lvl, self.lLip09Lower_ref, True)
        self.cnsUpper09 = aop.poseCns(self.lLip09_lvl, self.lLip09Upper_ref, True)        
        par.addExpression(self.cnsUpper09.Parameters("blendweight"),  self.lip_09.FullName    )
        self.cnsLower09.Parameters("cnsscl").Value = False
        self.cnsUpper09.Parameters("cnsscl").Value = False
        
        self.cnsLower10 = aop.poseCns(self.cLip10_lvl, self.lLip10Lower_ref, True)
        self.cnsUpper10 = aop.poseCns(self.cLip10_lvl, self.lLip10Upper_ref, True)        
        par.addExpression(self.cnsUpper10.Parameters("blendweight"),  self.lip_10.FullName    )
        self.cnsLower10.Parameters("cnsscl").Value = False
        self.cnsUpper10.Parameters("cnsscl").Value = False
        
        self.cnsLower11 = aop.poseCns(self.uLip11_lvl, self.uLip11Lower_ref, True)
        self.cnsUpper11 = aop.poseCns(self.uLip11_lvl, self.uLip11Upper_ref, True)        
        par.addExpression(self.cnsUpper11.Parameters("blendweight"),  self.lip_11.FullName    )
        self.cnsLower11.Parameters("cnsscl").Value = False
        self.cnsUpper11.Parameters("cnsscl").Value = False
        
        self.cnsLower12 = aop.poseCns(self.uLip12_lvl, self.uLip12Lower_ref, True)
        self.cnsUpper12 = aop.poseCns(self.uLip12_lvl, self.uLip12Upper_ref, True)        
        par.addExpression(self.cnsUpper12.Parameters("blendweight"),  self.lip_12.FullName    )
        self.cnsLower12.Parameters("cnsscl").Value = False
        self.cnsUpper12.Parameters("cnsscl").Value = False
        
        #mouth compression
        par.addExpression(self.upLips_loc.Kinematics.Local.Parameters("sclx"),  "1-((" + \
            self.jawControl.Kinematics.Local.Parameters("posy").FullName + \
            "*-1)*"+  self.lips_compression.FullName + ")")
            
        par.addExpression(self.lowLipsJaw.Kinematics.Local.Parameters("sclx"),  "1-((" + \
            self.jawControl.Kinematics.Local.Parameters("posy").FullName +"*-1)*"+ \
            self.lips_compression.FullName+ ")")
        
        par.addExpression(self.upLips_loc.Kinematics.Local.Parameters("posz"),  "((MAX("+ \
            self.jawControl.Kinematics.Local.Parameters("posy").FullName + "*-1,0))*" +  \
            self.lips_upperTranslation.FullName + ")+" + self.lips_upperOffset.FullName )
            
        par.addExpression(self.lowLipsJaw.Kinematics.Local.Parameters("posz"),  "((MAX("+ \
            self.jawControl.Kinematics.Local.Parameters("posy").FullName + "*-1,0))*" + \
            self.lips_lowerTranslation.FullName + ") +" + self.lips_lowerOffset.FullName )
         
         
        # # ICE Shapes Controls
        # self.intePose03 = aop.sn_interpose_op(self.mouthICE_lvl, self.upLipsHead, self.upLipsJaw )
        
        
        

        
         