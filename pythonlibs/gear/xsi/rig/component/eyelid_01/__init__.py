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

## @package gear.xsi.rig.component.eyelid_01
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
        self.normal = self.guide.blades["blade"].z
        t = tra.getTransformLookingAt(self.guide.apos[0], self.guide.apos[2], self.normal, "zx", False)
        offsetRotation = XSIMath.CreateRotation()
        t.GetRotation(offsetRotation)
        self.tracking_lvl = pri.addNullFromPos(self.root, self.getName("tracking_lvl"), self.guide.apos[0 ],   self.size*.15)
        self.addToGroup(self.tracking_lvl, "hidden")
        self.loc = pri.addNullsFromPositions(self.tracking_lvl, self.getName("#_loc"), self.guide.apos[3:],  offsetRotation, self.size*.15)
        self.addToGroup(self.loc, "hidden")
        i = 0
        self.oDirDriverList = []
        self.oDirDrivenList = []
        self.oPointerLvlList = []
        self.oCornersList = []
        self.oUpDownList = []
        self.oSidesList = []
       
        for x in self.loc:
            t = x.Kinematics.Global.Transform
            self.coners_lvl = pri.addNull(x, self.getName("coners%s_lvl"%i), t, self.size*.15)
            self.upDown_lvl = pri.addNull(self.coners_lvl, self.getName("upDown%s_lvl"%i), t, self.size*.15)
            self.sides_lvl = pri.addNull(self.upDown_lvl, self.getName("sides%s_lvl"%i), t, self.size*.15)
            self.tweak_lvl = pri.addNull(self.sides_lvl, self.getName("tweak%s_lvl"%i), t, self.size*.15)
            t2 = tra.getTransformLookingAt(self.guide.apos[0], x.Kinematics.Global.Transform.Translation, self.normal, "xy", False)
            self.oPointer= pri.addNull(self.root, self.getName("pointer%s_loc"%i), t2, self.size*.15)
            self.oPointerLvl= pri.addNull(self.root, self.getName("pointer%s_lvl"%i), t, self.size*.15)
            self.shadow = self.addShadow(self.oPointerLvl, "%s"%i)
            self.oHiddenList = [self.coners_lvl,  self.upDown_lvl, self.sides_lvl, self.oPointer, self.oPointerLvl, self.tweak_lvl ]
            self.addToGroup(self.oHiddenList, "hidden")
            self.oDirDriverList.append(self.tweak_lvl)
            self.oDirDrivenList.append(self.oPointer)
            self.oPointerLvlList.append(self.oPointerLvl)
            self.oCornersList.append(self.coners_lvl)
            self.oUpDownList.append(self.upDown_lvl)
            self.oSidesList.append(self.sides_lvl)

            i +=1
            
        self.cornerA_lvl = pri.addNullFromPos(self.root, self.getName("cornerA_lvl"), self.guide.apos[3],   self.size*.15)
        self.cornerA = pri.addNullFromPos(self.cornerA_lvl, self.getName("cornerA"), self.guide.apos[3],  self.size*.15)
        self.addToGroup(self.cornerA_lvl, "hidden")
        self.addToGroup(self.cornerA, "hidden")

        self.cornerB_lvl = pri.addNullFromPos(self.root, self.getName("cornerB_lvl"), self.guide.apos[-1],   self.size*.15)
        self.cornerB = pri.addNullFromPos(self.cornerB_lvl, self.getName("cornerB"), self.guide.apos[-1],   self.size*.15)
        self.addToGroup(self.cornerB_lvl, "hidden")
        self.addToGroup(self.cornerB, "hidden")
        
        self.upVec = pri.addNullFromPos(self.root, self.getName("upVec_loc"), self.guide.apos[1], self.size*.15)
        self.addToGroup(self.upVec, "hidden")

        self.mediumPosition = self.guide.apos[((len(self.guide.apos) -3 )//2) + 3]
        self.oTempPosY =  XSIMath.CreateVector3()
        self.oTempPosY.X =  self.mediumPosition.X
        self.oTempPosY.Y =  self.mediumPosition.Y + 3
        self.oTempPosY.Z =  self.mediumPosition.Z
        
        self.oTempPosZ = XSIMath.CreateVector3()
        self.oTempPosZ.X =  self.mediumPosition.X
        self.oTempPosZ.Y =  self.mediumPosition.Y
        self.oTempPosZ.Z =  self.mediumPosition.Z +3

        
        t = tra.getTransformLookingAt( self.mediumPosition, self.oTempPosZ, self.oTempPosY, "zy", self.negate)
        t.RotZ = 0.0

        self.control_lvl = pri.addNull(self.root, self.getName("eyelidCtl_lvl"), t, self.size*.15)
        self.addToGroup(self.control_lvl, "hidden")
        self.control = self.addCtl(self.control_lvl, "eyelid_ctl", t, self.color_ik,  "square", w=self.size*.2)
         
         
        
        
    # =====================================================
    # PROPERTY
    # =====================================================
    ## Add parameters to the anim and setup properties to control the component.
    # @param self
    def addParameters(self):
       
        i=0
        self.blockList = []
        for edLoop in self.oDirDriverList:
            
            # controls block
            self.blockName = "block_%s" %str(i)
           
            self.plusXcornerA_upDown = self.addSetupParam("plusX", c.siDouble, 0, None, None, -2, 2)
            self.minusXcornerA_upDown = self.addSetupParam("minusX", c.siDouble, 0, None, None, -2, 2)
            self.plusYcornerA_upDown = self.addSetupParam("plusY", c.siDouble, 0, None, None, -2, 2)
            self.minusYcornerA_upDown = self.addSetupParam("minusY", c.siDouble, 0, None, None, -2, 2)

            self.plusXcornerA_sides = self.addSetupParam("plusX", c.siDouble, 0, None, None, -2, 2)
            self.minusXcornerA_sides = self.addSetupParam("minusX", c.siDouble, 0, None, None, -2, 2)
            self.plusYcornerA_sides = self.addSetupParam("plusY", c.siDouble, 0, None, None, -2, 2)
            self.minusYcornerA_sides = self.addSetupParam("minusY", c.siDouble, 0, None, None, -2, 2)

            self.plusXcornerB_upDown = self.addSetupParam("plusX", c.siDouble, 0, None, None, -2, 2)
            self.minusXcornerB_upDown = self.addSetupParam("minusX", c.siDouble, 0, None, None, -2, 2)
            self.plusYcornerB_upDown = self.addSetupParam("plusY", c.siDouble, 0, None, None, -2, 2)
            self.minusYcornerB_upDown = self.addSetupParam("minusY", c.siDouble, 0, None, None, -2, 2)

            self.plusXcornerB_sides = self.addSetupParam("plusX", c.siDouble, 0, None, None, -2, 2)
            self.minusXcornerB_sides = self.addSetupParam("minusX", c.siDouble, 0, None, None, -2, 2)
            self.plusYcornerB_sides = self.addSetupParam("plusY", c.siDouble, 0, None, None, -2, 2)
            self.minusYcornerB_sides = self.addSetupParam("minusY", c.siDouble, 0, None, None, -2, 2)

            self.plusXupDown = self.addSetupParam("plusX", c.siDouble, 0, None, None, -2, 2)
            self.minusXupDown = self.addSetupParam("minusX", c.siDouble, 0, None, None, -2, 2)
            self.plusYupDown = self.addSetupParam("plusY", c.siDouble, 0, None, None, -2, 2)
            self.minusYupDown = self.addSetupParam("minusY", c.siDouble, 0, None, None, -2, 2)

            self.plusXSides = self.addSetupParam("plusX", c.siDouble, 0, None, None, -2, 2)
            self.minusXSides = self.addSetupParam("minusX", c.siDouble, 0, None, None, -2, 2)
            self.plusYSides = self.addSetupParam("plusY", c.siDouble, 0, None, None, -2, 2)
            self.minusYSides = self.addSetupParam("minusY", c.siDouble, 0, None, None, -2, 2)

            i+=1

            self.blockList.append([self.blockName, self.plusXcornerA_upDown, self.minusXcornerA_upDown, self.plusYcornerA_upDown, self.minusYcornerA_upDown, \
                                                    self.plusXcornerA_sides, self.minusXcornerA_sides, self.plusYcornerA_sides, self.minusYcornerA_sides, \
                                                    self.plusXcornerB_upDown,  self.minusXcornerB_upDown, self.plusYcornerB_upDown, self.minusYcornerB_upDown, \
                                                    self.plusXcornerB_sides,  self.minusXcornerB_sides, self.plusYcornerB_sides, self.minusYcornerB_sides, \
                                                    self.plusXupDown, self.minusXupDown, self.plusYupDown, self.minusYupDown, \
                                                    self.plusXSides, self.minusXSides,  self.plusYSides, self.minusYSides])

        
    
        if self.settings["cornerARefArray"]:
            self.cornerARef_names = self.settings["cornerARefArray"].split(",")
        else:
            self.cornerARef_names = []
            
        self.cornerARef_count = len(self.cornerARef_names)

        if self.cornerARef_count > 0:
            self.pCornerARef = self.addAnimParam("cornerARef", c.siInt4, 0, 0, self.cornerARef_count)
        
        if self.settings["cornerBRefArray"]:
            self.cornerBRef_names = self.settings["cornerBRefArray"].split(",")
        else:
            self.cornerBRef_names = []
            
        self.cornerBRef_count = len(self.cornerBRef_names)

        if self.cornerBRef_count > 0:
            self.pCornerBRef = self.addAnimParam("cornerBRef", c.siInt4, 0, 0, self.cornerBRef_count)

    ## Define the layout of the anim and setup properties.
    # @param self
    def addLayout(self):
        
        # setup -------------------------------------------

        tab = self.setup_layout.addTab(self.name)

        
        i =0
        for oBlock in self.blockList:
            oTempName = self.blockList[i][0]
            group = tab.addGroup(oTempName)
            row = group.addRow()
            subGroup = row.addGroup("Corner A Up Down")
            subGroup.addItem(self.blockList[i][1].ScriptName, "+X")
            subGroup.addItem(self.blockList[i][2].ScriptName, "-X")
            subGroup.addItem(self.blockList[i][3].ScriptName, "+Y")
            subGroup.addItem(self.blockList[i][4].ScriptName, "-Y")
            subGroup = row.addGroup("Corner A Sides")
            subGroup.addItem(self.blockList[i][5].ScriptName, "+X")
            subGroup.addItem(self.blockList[i][6].ScriptName, "-X")
            subGroup.addItem(self.blockList[i][7].ScriptName, "+Y")
            subGroup.addItem(self.blockList[i][8].ScriptName, "-Y")
            subGroup = row.addGroup("Corner B Up Down")
            subGroup.addItem(self.blockList[i][9].ScriptName, "+X")
            subGroup.addItem(self.blockList[i][10].ScriptName, "-X")
            subGroup.addItem(self.blockList[i][11].ScriptName, "+Y")
            subGroup.addItem(self.blockList[i][12].ScriptName, "-Y")
            subGroup = row.addGroup("Corner B Sides")
            subGroup.addItem(self.blockList[i][13].ScriptName, "+X")
            subGroup.addItem(self.blockList[i][14].ScriptName, "-X")
            subGroup.addItem(self.blockList[i][15].ScriptName, "+Y")
            subGroup.addItem(self.blockList[i][16].ScriptName, "-Y")
            subGroup = row.addGroup("Up Down")
            subGroup.addItem(self.blockList[i][17].ScriptName, "+X")
            subGroup.addItem(self.blockList[i][18].ScriptName, "-X")
            subGroup.addItem(self.blockList[i][19].ScriptName, "+Y")
            subGroup.addItem(self.blockList[i][20].ScriptName, "-Y")
            subGroup = row.addGroup("Sides")
            subGroup.addItem(self.blockList[i][21].ScriptName, "+X")
            subGroup.addItem(self.blockList[i][22].ScriptName, "-X")
            subGroup.addItem(self.blockList[i][23].ScriptName, "+Y")
            subGroup.addItem(self.blockList[i][24].ScriptName, "-Y")

            i+=1

        
        self.cornerARef_Items = ["self", 0]
        for i, name in enumerate(self.cornerARef_names):
            self.cornerARef_Items.append(name)
            self.cornerARef_Items.append(i+1)

        self.cornerBRef_Items = ["self", 0]
        for i, name in enumerate(self.cornerBRef_names):
            self.cornerBRef_Items.append(name)
            self.cornerBRef_Items.append(i+1)
            
        # Anim -------------------------------------------
        tab = self.anim_layout.addTab(self.name)
        group = tab.addGroup("space")
        if self.cornerARef_count > 0:
            row = group.addRow()
            row.addEnumControl(self.pCornerARef.ScriptName, self.cornerARef_Items, "Corner A Ref", c.siControlCombo)
            row.addButton(self.getName("switchCornerARef"), "Switch")
        if self.cornerBRef_count > 0:
            row = group.addRow()
            row.addEnumControl(self.pCornerBRef.ScriptName, self.cornerBRef_Items, "Corner A Ref", c.siControlCombo)
            row.addButton(self.getName("switchCornerBRef"), "Switch")
        
        


        
        
    # @param self
    def addLogic(self):
        
        # Anim -------------------------------------------
        self.anim_logic.addGlobalCode("import gear.xsi.rig.component.logic as logic")
        if self.cornerARef_count > 0:
            self.anim_logic.addOnClicked(self.getName("switchCornerARef"),
                                     "logic.switchRef(PPG.Inspected(0), '"+self.cornerA.Name+"', '"+self.pCornerARef.ScriptName+"', "+str(self.cornerARef_count + 1)+")\r\n" +
                                     "PPG.Refresh()\r\n")
        if self.cornerBRef_count > 0:
            self.anim_logic.addOnClicked(self.getName("switchCornerBRef"),
                                     "logic.switchRef(PPG.Inspected(0), '"+self.cornerB.Name+"', '"+self.pCornerBRef.ScriptName+"', "+str(self.cornerBRef_count + 1)+")\r\n" +
                                     "PPG.Refresh()\r\n")

    # =====================================================
    # OPERATORS
    # =====================================================
    ## Apply operators, constraints, expressions to the hierarchy.\n
    # In order to keep the code clean and easier to debug,
    # we shouldn't create any new object in this method.
    # @param self
    def addOperators(self):
        #return
        i = 0
        for x  in self.oDirDrivenList:            
            oTmpOp = aop.dirCns(x, self.oDirDriverList[i], self.upVec, False, "xz")
            xsi.ParentObj(x, self.oPointerLvlList[i])
            i +=1


        i =0
        for oBlock in self.blockList:


            # Corners
            par.addExpression(self.oCornersList[i].Kinematics.Local.Parameters("posy"), \
                "(cond(" + self.cornerA.Kinematics.Local.Parameters("posy").FullName + " > 0," + \
                self.cornerA.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][3].FullName + "," + \
                self.cornerA.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][4].FullName + ") +" + \
                "cond(" + self.cornerB.Kinematics.Local.Parameters("posy").FullName + " > 0," + \
                self.cornerB.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][11].FullName + "," + \
                self.cornerB.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][12].FullName + "))" + \
                "+ (cond(" + self.cornerA.Kinematics.Local.Parameters("posx").FullName + " > 0," + \
                self.cornerA.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][7].FullName + "," + \
                self.cornerA.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][8].FullName + ") +" + \
                "cond(" + self.cornerB.Kinematics.Local.Parameters("posx").FullName + " > 0," + \
                self.cornerB.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][15].FullName + "," + \
                self.cornerB.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][16].FullName + "))")
                

            par.addExpression(self.oCornersList[i].Kinematics.Local.Parameters("posx"), \
                "cond(" + self.cornerA.Kinematics.Local.Parameters("posy").FullName + " > 0," + \
                self.cornerA.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][1].FullName + "," + \
                self.cornerA.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][2].FullName + ") +" + \
                "cond(" + self.cornerB.Kinematics.Local.Parameters("posy").FullName + " > 0," + \
                self.cornerB.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][9].FullName + "," + \
                self.cornerB.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][10].FullName + ")" + \
                "+ (cond(" + self.cornerA.Kinematics.Local.Parameters("posx").FullName + " > 0," + \
                self.cornerA.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][5].FullName + "," + \
                self.cornerA.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][6].FullName + ") +" + \
                "cond(" + self.cornerB.Kinematics.Local.Parameters("posx").FullName + " > 0," + \
                self.cornerB.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][13].FullName + "," + \
                self.cornerB.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][14].FullName + "))")


            #Control up down
            par.addExpression(self.oUpDownList[i].Kinematics.Local.Parameters("posy"), \
                "cond(" + self.control.Kinematics.Local.Parameters("posy").FullName + " > 0," + \
                self.control.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][19].FullName + "," + \
                self.control.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][20].FullName + ")")
            par.addExpression(self.oUpDownList[i].Kinematics.Local.Parameters("posx"), \
                "cond(" + self.control.Kinematics.Local.Parameters("posy").FullName + " > 0," + \
                self.control.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][17].FullName + "," + \
                self.control.Kinematics.Local.Parameters("posy").FullName + " * " + self.blockList[i][18].FullName + ")")

            #Control sides
            par.addExpression(self.oSidesList[i].Kinematics.Local.Parameters("posy"), \
                "cond(" + self.control.Kinematics.Local.Parameters("posx").FullName + " > 0," + \
                self.control.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][23].FullName + "," + \
                self.control.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][24].FullName + ")")
            par.addExpression(self.oSidesList[i].Kinematics.Local.Parameters("posx"), \
                "cond(" + self.control.Kinematics.Local.Parameters("posx").FullName + " > 0," + \
                self.control.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][21].FullName + "," + \
                self.control.Kinematics.Local.Parameters("posx").FullName + " * " + self.blockList[i][22].FullName + ")")
                

            i+=1
        

     
    # =====================================================
    # CONNECTOR
    # =====================================================
    
    

    ## standard connection definition.
    # @param self
    def connect_standard(self):
        self.connect_standardWithIkRef()

    ## standard connection definition with ik and upv references.
    # @param self
    def connect_standardWithIkRef(self):
        
        self.parent.AddChild(self.root)
        
        if self.settings["cornerARefArray"]:
            ref_names = self.settings["cornerARefArray"].split(",")
            for i, ref_name in enumerate(ref_names):
                ref = self.rig.findChild(ref_name)
                cns = aop.poseCns(self.cornerA, ref, True, True, True, False)
               
                par.addExpression(cns.Parameters("active"), self.pCornerARef.FullName+" == "+str(i+1))

        if self.settings["cornerBRefArray"]:
            ref_names = self.settings["cornerBRefArray"].split(",")
            for i, ref_name in enumerate(ref_names):
                ref = self.rig.findChild(ref_name)
                cns = aop.poseCns(self.cornerB, ref, True, True, True, False)
         
                par.addExpression(cns.Parameters("active"), self.pCornerBRef.FullName+" == "+str(i+1))
                    