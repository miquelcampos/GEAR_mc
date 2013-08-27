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


# gear
from gear.xsi import xsi, c, lm


null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_groupManager"
    in_reg.Email = "geerem@hotmail.com, hello@miqueltd.com"
    in_reg.URL = "http://www.jeremiepasserin.com, http://www.miqueltd.com "
    in_reg.Major = 1
    in_reg.Minor = 0


    in_reg.RegisterCommand("gear_groupsLister", "gear_groupsLister")
    in_reg.RegisterCommand("gear_groupManagerOpen", "gear_groupManagerOpen")
    in_reg.RegisterCommand("gear_groupManagerPropSet", "gear_groupManagerPropSet")

    in_reg.RegisterProperty("gear_groupManagerProp")
    in_reg.RegisterProperty("gear_groupManager")

    return true

def XSIUnloadPlugin( in_reg ):
    strPluginName = in_reg.Name
    lm(str(strPluginName) + str(" has been unloaded."),c.siVerbose)
    return true

##############################################################################
# Groups Manager
##############################################################################
#Open Manager
def gear_groupManagerOpen_Execute():

    ppg = XSIFactory.CreateObject("gear_groupManager")
    xsi.InspectObj(ppg)

    return 1


# manager property page
def gear_groupManager_Define( in_ctxt ):
    lm("gear_groupManager_Define called",c.siVerbose)


def gear_groupManager_DefineLayout( in_ctxt ):
    lm("gear_groupManager_DefineLayout called",c.siVerbose)

def gear_groupManager_OnInit():
    prop = PPG.Inspected(0)


    #static paramenters

    #dinamic paramenters
    gList = xsi.gear_groupsLister()
    print gList
    if gList:
        for group in gList:
            if len(group.Properties):
                for p in group.Properties:
                    if p.Name.startswith("gear_groupManagerProp"):
                        inProp = p
                    else:
                        inProp = xsi.gear_groupManagerPropSet(group)
            else:
                inProp = xsi.gear_groupManagerPropSet(group)
            oName = inProp.Parameters("grpName").Value
            prop.AddProxyParameter(inProp.Parameters("grpName"), oName +"_N", oName +"_N")
            prop.AddProxyParameter(inProp.Parameters("Vis"), oName +"_V", oName +"_V" )
            # item = prop.AddParameter3( oName +"_V",c.siBool, False, None, None, True, False)
            # inProp.Parameters("Vis").AddExpression(item)
            prop.AddProxyParameter(inProp.Parameters("Ren"), oName +"_R", oName +"_R" )
            prop.AddProxyParameter(inProp.Parameters("Select"), oName +"_S", oName +"_S"  )

        oLayout = PPG.PPGLayout
        oLayout.Clear()
        oLayout.AddGroup()

        if gList:
            for group in gList:
                for p in group.Properties:
                    if p.Name.startswith("gear_groupManagerProp"):
                        inProp = p
                oLayout.AddGroup()

                oLayout.AddRow()
                oName = inProp.Parameters("grpName").Value
                item = oLayout.AddItem( oName + "_N")
                item = oLayout.AddItem( oName +"_V")
                item = oLayout.AddItem( oName +"_R")
                item = oLayout.AddItem( oName +"_S")
                oLayout.EndRow()
                oLayout.EndGroup()

        oLayout.EndGroup()
        PPG.Refresh()



##############################################################################
# help functions
##############################################################################


def gear_groupsLister_Execute():
    oSel = xsi.Selection
    gList = []
    if oSel.Count:
        if oSel(0).Type == "#Group":
            for group in oSel:
                if group.Type == "#Group":
                    gList.append(group)
        elif oSel(0).Type == "#model":
            for model in oSel:
                if model.Type == "#model":
                    groups = model.Groups
                    for group in groups:
                        gList.append(group)
    else:
        root = xsi.ActiveSceneRoot
        groups = root.Groups
        for group in groups:
            gList.append(group)

    return gList


##############################################################################
# Group Property
##############################################################################
def gear_groupManagerPropSet_Init( in_ctxt ):
    oCmd = in_ctxt.Source
    oCmd.Description = ""
    oCmd.ReturnValue = true

    oArgs = oCmd.Arguments
    oArgs.Add("obj",c.siArgumentInput)
    return true
def gear_groupManagerPropSet_Execute(obj):
    prop = obj.AddProperty("gear_groupManagerProp")
    # dis.inspect(prop)
    return prop


def gear_groupManagerProp_Define( in_ctxt ):
    oCustomProperty = in_ctxt.Source
    pV = oCustomProperty.AddParameter3("Vis",c.siBool, False, None, None, True, False)
    pR = oCustomProperty.AddParameter3("Ren",c.siBool,False, None, None, True, False)
    pS = oCustomProperty.AddParameter3("Select",c.siBool, False, None, None, True, False)
    pN = oCustomProperty.AddParameter3("grpName",c.siString, False, None, None, False, True)

    return true


def gear_groupManagerProp_DefineLayout( in_ctxt ):
    oLayout = in_ctxt.Source
    oLayout.Clear()
    oLayout.AddGroup()
    oLayout.AddRow()
    item = oLayout.AddItem("grpName")
    item.SetAttribute(c.siUINoLabel, True)
    oLayout.AddItem("Vis", "V")
    oLayout.AddItem("Ren", "R")
    oLayout.AddItem("Select", "S")
    oLayout.EndRow()
    oLayout.EndGroup()
    return true

def gear_groupManagerProp_OnInit( ):
    lm("gear_groupManager_OnInit called",c.siVerbose)
    group = PPG.grpName.Parent.Parent
    PPG.grpName.Value = group.FullName
    vVal = group.Parameters("viewvis").Value
    rVal = group.Parameters("rendvis").Value
    sVal = group.Parameters("selectability").Value

    if vVal:
        PPG.Vis.Value = True
    else:
        PPG.Vis.Value = False

    if rVal:
        PPG.Ren.Value = True
    else:
        PPG.Ren.Value = False

    if sVal:
        PPG.Select.Value = True
    else:
        PPG.Select.Value = False
    PPG.Refresh()

def gear_groupManagerProp_Vis_OnChanged( ):
    lm("gear_groupManager_Vis_OnChanged called",c.siVerbose)
    oParam = PPG.Vis
    paramVal = oParam.Value

    group = PPG.grpName.Parent.Parent

    if paramVal:
        val = 2
    else:
        val = 0
    group.Parameters("viewvis").Value = val
    xsi.DeselectAll()

    lm(str("New value: ") + str(paramVal),c.siVerbose)


def gear_groupManagerProp_Ren_OnChanged( ):
    lm("gear_groupManager_Ren_OnChanged called",c.siVerbose)
    oParam = PPG.Ren
    paramVal = oParam.Value

    group = PPG.grpName.Parent.Parent

    if paramVal:
        val = 2
    else:
        val = 0
    group.Parameters("rendvis").Value = val
    xsi.DeselectAll()

    lm(str("New value: ") + str(paramVal),c.siVerbose)

def gear_groupManagerProp_Select_OnChanged( ):
    lm("gear_groupManager_Select_OnChanged called",c.siVerbose)
    oParam = PPG.Select
    paramVal = oParam.Value

    group = PPG.grpName.Parent.Parent

    if paramVal:
        val = 2
    else:
        val = 0
    group.Parameters("selectability").Value = val
    xsi.DeselectAll()

    lm(str("New value: ") + str(paramVal),c.siVerbose)