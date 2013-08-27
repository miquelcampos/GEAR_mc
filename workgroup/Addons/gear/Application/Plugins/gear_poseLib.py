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


## @package gear_poseLib.py
# @author Jeremie Passerin, Miquel Campos
# @version 1.0
#

##########################################################
# GLOBAL
##########################################################
from win32com.client import constants as c
from time import  strftime
import os
import xml.etree.cElementTree as xml
import shutil

import gear.xsi.display as ds
from gear.xsi import xsi, lm

SEP = os.sep


##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin, Miquel Campos"
    in_reg.Name = "gear_poseLib"
    in_reg.Email = "geerem@hotmail.com, hello@miqueltd.com"
    in_reg.URL = "http://www.jeremiepasserin.com, http://www.miqueltd.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    in_reg.RegisterCommand("gear_poseLib","gear_poseLib")
    in_reg.RegisterCommand("gear_prefPoseLib","gear_prefPoseLib")
    in_reg.RegisterCommand("gear_newPose","gear_newPose")

    in_reg.RegisterProperty("gear_poseLibManager")
    in_reg.RegisterProperty("gear_prefPoseLibProp")
    in_reg.RegisterProperty("gear_newPoseProp")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):

    strPluginName = in_reg.Name
    lm(str(strPluginName) + str(" has been unloaded."), c.siVerbose)

    return True


##########################################################
# Pose library manager
##########################################################

def gear_poseLib_Execute():

    if xsi.ActiveSceneRoot.Properties("gear_poseLibManager"):
        xsi.DeleteObj(xsi.ActiveSceneRoot.Properties("gear_poseLibManager"))

    prop = xsi.ActiveSceneRoot.AddProperty("gear_poseLibManager", False, "gear_poseLibManager")

    if xsi.Preferences.Categories("gear_prefPoseLib"):
        listSize = xsi.GetValue("preferences.gear_prefPoseLib.list_Size")
    else:
        listSize = 500

    ds.inspect(prop, 300, 365 + listSize)


def gear_poseLibManager_Define(in_ctxt):

    prop = in_ctxt.Source

    #combo
    prop.AddParameter3("parRepo", c.siString, 0, 0, None, False, False)
    prop.AddParameter3("parUser", c.siString, 0, 0, None, False, False)
    prop.AddParameter3("parModel", c.siString, 0, 0, None, False, False)

    #List
    prop.AddParameter3("parPoseList", c.siString, 0, 0, None, False, False)

    #Integer
    prop.AddParameter3("parRowsNum", c.siInt4, 4, 1, None, False, False)


def gear_poseLibManager_OnInit(repo = "Current_DB", user = "Self", model = "All", pose_items = [] ):
    #retriving Preferences
    if xsi.Preferences.Categories("gear_prefPoseLib"):
        listSize = xsi.GetValue("preferences.gear_prefPoseLib.list_Size")
    else:
        listSize = 500

    # Dropbox menus populating
    repo_items = ["Current_DB", "Current_DB", "Global", "Global", "Both", "Both"]
    user_items = ["Self", "Self", "All", "All"]
    model_items = ["All", "All", "Selected", "Selected", "In_Scene", "In_Scene"]

    #Users List populating
    currentProject = xsi.ActiveProject2.Path
    currentRepoPath = os.path.join(currentProject, "PoseLib")
    #local
    if not os.path.isdir(currentRepoPath):
        os.makedirs(currentRepoPath)
    oUserFolders = [d for d in os.listdir(currentRepoPath)]
    for oFolder in oUserFolders:
        for x in range(2):
            user_items.append(oFolder)

    #global
    if xsi.Preferences.Categories("gear_prefPoseLib"):
        globlaRepoPath = xsi.GetValue("preferences.gear_prefPoseLib.global_Repo")
        oUserFolders = [d for d in os.listdir(globlaRepoPath)]
        for oFolder in oUserFolders:
            for x in range(2):
                user_items.append(oFolder)

    #Layout ------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------

    layout = PPG.PPGLayout
    layout.Clear()

    layout.AddTab("Main")
    layout.AddGroup("Search filters")
    layout.AddEnumControl("parRepo", repo_items, "Repository", c.siControlCombo)
    PPG.parRepo.Value = repo
    layout.AddEnumControl("parUser", user_items, "User", c.siControlCombo)
    PPG.parUser.Value = user
    layout.AddEnumControl("parModel", model_items, "Model", c.siControlCombo)
    PPG.parModel.Value = model
    layout.EndGroup()

    oButton = layout.AddButton("refreshList", "Refresh List")
    oButton.SetAttribute(c.siUICX, 280)
    oButton.SetAttribute(c.siUICY, 30)

    layout.AddGroup("Pose List")
    oListBox = layout.AddItem( "parPoseList", "", c.siControlListBox )
    oListBox.SetAttribute(c.siUINoLabel,True)
    oListBox.SetAttribute( c.siUICY, listSize )
    oListBox.SetAttribute( c.siUIMultiSelectionListBox, True )

    oListBox.UIItems = pose_items
    #PPG.pModelList.Value = defaultValue
    layout.EndGroup()

    oButton = layout.AddButton("createPoseSet", "Create Pose Set")
    oButton.SetAttribute(c.siUICX, 280)
    oButton.SetAttribute(c.siUICY, 40)
    layout.AddRow()
    oButton = layout.AddButton("removePose", "<< Remove")
    oButton.SetAttribute(c.siUICX, 115)
    oButton.SetAttribute(c.siUICY, 20)
    oButton = layout.AddButton("syncPose", "Sync")
    oButton.SetAttribute(c.siUICX, 50)
    oButton.SetAttribute(c.siUICY, 20)
    oButton = layout.AddButton("addPose", "Add >>")
    oButton.SetAttribute(c.siUICX, 115)
    oButton.SetAttribute(c.siUICY, 20)
    layout.EndRow()
    layout.AddGroup("Set Columns Number")
    tmpItem = layout.AddItem("parRowsNum", "Set columns Number", c.siControlNumber )
    tmpItem.SetAttribute(c.siUINoLabel,True)
    layout.EndGroup()

    layout.AddGroup("STORE")
    oButton = layout.AddButton("newPose", "New Pose")
    oButton.SetAttribute(c.siUICX, 270)
    oButton.SetAttribute(c.siUICY, 40)
    layout.AddRow()
    oButton = layout.AddButton("delPose", "Del")
    oButton.SetAttribute(c.siUICX, 40)
    oButton.SetAttribute(c.siUICY, 20)
    oButton = layout.AddButton("preferences", "Preferences")
    oButton.SetAttribute(c.siUICX, 230)
    oButton.SetAttribute(c.siUICY, 20)
    layout.EndRow()
    layout.EndGroup()

    PPG.Refresh()

##########################################################
# Envents
##########################################################
def gear_poseLibManager_delPose_OnClicked():
    userName = os.environ.get( "USERNAME" )
    oReturn = XSIUIToolkit.MsgBox( "ATTENTION!!, You CAN'T UNDO this operation!!!", c.siMsgYesNo )
    if oReturn == 6:
        for pose2Delete in PPG.parPoseList.Value.split(";"):
            if pose2Delete.split(SEP)[-2] == userName:
                shutil.rmtree(pose2Delete)
            else:
                notUser = XSIUIToolkit.MsgBox( "You are not the user for: " + pose2Delete + ". Do you want to delete it?" , c.siMsgYesNo )
                if notUser == 6:
                    shutil.rmtree(pose2Delete)
    gear_poseLibManager_refreshList_OnClicked()

def gear_poseLibManager_createPoseSet_OnClicked(currPose = False, setName = False, remPose = False ):
    root = xsi.ActiveSceneRoot
    if currPose and setName and not remPose:
        for newPose2add in PPG.parPoseList.Value.split(";"):
            if newPose2add not in currPose:
                currPose.append(newPose2add)
        pose2add = currPose
        pEditList = ";".join(currPose)
    elif currPose and setName and remPose:
        for newPose2remove in PPG.parPoseList.Value.split(";"):
            if newPose2remove  in currPose:
                currPose.remove(newPose2remove)
        pose2add = currPose
        pEditList = ";".join(currPose)
    else:
        pose2add = PPG.parPoseList.Value.split(";")
        setName = xsi.XSIInputBox ("Pose Set Name", "Name", "poseSet")
        pEditList = PPG.parPoseList.Value


    oPSet = root.AddCustomProperty(setName, False )
    oPSet.AddParameter3("percentage", c.siInt4, 25, 1, 100, False, False)
    oLayout = oPSet.PPGLayout
    oLayout.AddItem("percentage", "Pose %", c.siControlNumber )


    oPSet.AddParameter3( "poseEditList", c.siString)
    oPSet.Parameters("poseEditList").Value = pEditList

    rowNumber = PPG.parRowsNum.Value
    rowConter = 0
    rowAdd = 0
    lines = 1
    for posePath in pose2add:

        iPoseName = posePath.split(SEP)[-1]
        iPath = os.path.join(posePath, posePath.split("_")[-1] + ".htm" )
        oPSet.AddParameter3( iPoseName, c.siString)
        oPSet.Parameters(iPoseName).Value = iPath
        if  rowAdd == rowConter:
            oLayout.AddRow()
            rowConter = rowConter + rowNumber
        oItem = oLayout.AddItem(iPoseName, ".", c.siControlSynoptic)
        oItem.SetAttribute(c.siUINoLabel,True)

        if  rowAdd == rowConter -1:
             oLayout.EndRow()
             lines += 1
        rowAdd +=1

    # just testing
    ds.inspect( oPSet, (75*rowNumber)+ 25, (75*lines) + 65 )

def gear_poseLibManager_addPose_OnClicked():
    oSel = xsi.Selection(0)
    if oSel and oSel.Type == "customparamset":
        oParam = oSel.Parameters("poseEditList")
        if oParam:
            currPose = oSel.Parameters("poseEditList").Value.split(";")
            setName = oSel.Name
            xsi.DeleteObj(oSel)
            gear_poseLibManager_createPoseSet_OnClicked(currPose , setName)

        else:
            lm("The custom paramenter set selected is not a Pose Set", 4)
    else:
        lm("Select a custom paramenter set", 4)

def gear_poseLibManager_removePose_OnClicked():
    oSel = xsi.Selection(0)
    if oSel and oSel.Type == "customparamset":
        oParam = oSel.Parameters("poseEditList")
        if oParam:
            currPose = oSel.Parameters("poseEditList").Value.split(";")
            setName = oSel.Name
            xsi.DeleteObj(oSel)
            gear_poseLibManager_createPoseSet_OnClicked(currPose , setName, True)

        else:
            lm("The custom paramenter set selected is not a Pose Set", 4)
    else:
        lm("Select a custom paramenter set", 4)




def gear_poseLibManager_syncPose_OnClicked():
    oSel = xsi.Selection(0)
    if oSel and oSel.Type == "customparamset":
        oParam = oSel.Parameters("poseEditList")
        if oParam:
            pose_items = []
            rawList = oSel.Parameters("poseEditList").Value.split(";")
            for posePath in rawList:
                pose_items.append(posePath.split(SEP)[-1])
                pose_items.append(posePath)
                gear_poseLibManager_refreshList_OnClicked(pose_items)
        else:
            lm("The custom paramenter set selected is not a Pose Set", 4)
    else:
        lm("Select a custom paramenter set", 4)

def gear_poseLibManager_refreshList_OnClicked(Sync = False):
    repo = PPG.parRepo.Value
    user = PPG.parUser.Value
    model = PPG.parModel.Value

    currentProject = xsi.ActiveProject2.Path
    currentRepoPath = os.path.join(currentProject, "PoseLib")


    if xsi.Preferences.Categories("gear_prefPoseLib"):
        globlaRepoPath = xsi.GetValue("preferences.gear_prefPoseLib.global_Repo")
    else:
        globlaRepoPath = False

    oSel = xsi.Selection

    #Populating List
    if Sync:
        pose_items = Sync
    else:
        pose_items = []

        if repo in ["Current_DB", "Both"]:
                if user == "All":
                    oUserFolders = [d for d in os.listdir(currentRepoPath)]
                    for oFolder in oUserFolders:
                        oPoseFolders = [d for d in os.listdir(os.path.join(currentRepoPath, oFolder))]
                        if model == "All":
                            for iPose in oPoseFolders:
                                pose_items.append(oFolder+" : "+iPose)
                                pose_items.append(os.path.join(currentRepoPath, oFolder, iPose))
                        elif model == "Selected":
                            oModelCheck = []
                            for iSel in oSel:
                                if iSel.Type == "#model":
                                    oModelCheck.append(iSel.Name.split("_")[0])
                                else:
                                    oModelCheck.append(iSel.Model.Name.split("_")[0])
                            for iPose in oPoseFolders:
                                if iPose.split("_")[0] in oModelCheck:
                                    pose_items.append(oFolder+" : "+iPose)
                                    pose_items.append(os.path.join(currentRepoPath, oFolder, iPose))
                        elif model == "In_Scene":
                            oRoot = xsi.ActiveSceneRoot
                            oModelCheck = []
                            for iModel in oRoot.FindChildren2():
                                if iModel.Type == "#model":
                                    oModelCheck.append(iModel.Name.split("_")[0])
                            for iPose in oPoseFolders:
                                if iPose.split("_")[0] in oModelCheck:
                                    pose_items.append(oFolder+" : "+iPose)
                                    pose_items.append(os.path.join(currentRepoPath, oFolder, iPose))

                else:
                    if user == "Self":
                        userName = os.environ.get( "USERNAME" )
                    else:
                        userName = user
                    if os.path.isdir(os.path.join(currentRepoPath, userName)):
                        oPoseFolders = [d for d in os.listdir(os.path.join(currentRepoPath, userName))]
                        if model == "All":
                            for iPose in oPoseFolders:
                                pose_items.append(iPose)
                                pose_items.append(os.path.join(currentRepoPath, userName, iPose))
                        elif model == "Selected":
                            oModelCheck = []
                            for iSel in oSel:
                                if iSel.Type == "#model":
                                    oModelCheck.append(iSel.Name.split("_")[0])
                                else:
                                    oModelCheck.append(iSel.Model.Name.split("_")[0])
                            for iPose in oPoseFolders:
                                if iPose.split("_")[0] in oModelCheck:
                                    pose_items.append(iPose)
                                    pose_items.append(os.path.join(currentRepoPath, userName, iPose))
                        elif model == "In_Scene":
                            oRoot = xsi.ActiveSceneRoot
                            oModelCheck = []
                            for iModel in oRoot.FindChildren2():
                                if iModel.Type == "#model":
                                    oModelCheck.append(iModel.Name.split("_")[0])
                            for iPose in oPoseFolders:
                                if iPose.split("_")[0] in oModelCheck:
                                    pose_items.append(iPose)
                                    pose_items.append(os.path.join(currentRepoPath, userName, iPose))
                    else:
                         lm("No poses found for: " + userName, 4)


        if repo in ["Global", "Both"]:
            if globlaRepoPath :
                if user == "All":
                    oUserFolders = [d for d in os.listdir(globlaRepoPath)]
                    for oFolder in oUserFolders:
                        oPoseFolders = [d for d in os.listdir(os.path.join(globlaRepoPath, oFolder))]
                        if model == "All":
                            for iPose in oPoseFolders:
                                pose_items.append("Global: "+oFolder+" : "+iPose)
                                pose_items.append(os.path.join(globlaRepoPath, oFolder, iPose))
                        elif model == "Selected":
                            oModelCheck = []
                            for iSel in oSel:
                                if iSel.Type == "#model":
                                    oModelCheck.append(iSel.Name.split("_")[0])
                                else:
                                    oModelCheck.append(iSel.Model.Name.split("_")[0])
                            for iPose in oPoseFolders:
                                if iPose.split("_")[0] in oModelCheck:
                                    pose_items.append("Global: "+oFolder+" : "+iPose)
                                    pose_items.append(os.path.join(globlaRepoPath, oFolder, iPose))
                        elif model == "In_Scene":
                            oRoot = xsi.ActiveSceneRoot
                            oModelCheck = []
                            for iModel in oRoot.FindChildren2():
                                if iModel.Type == "#model":
                                    oModelCheck.append(iModel.Name.split("_")[0])
                            for iPose in oPoseFolders:
                                if iPose.split("_")[0] in oModelCheck:
                                    pose_items.append("Global: "+oFolder+" : "+iPose)
                                    pose_items.append(os.path.join(globlaRepoPath, oFolder, iPose))

                else:
                    if user == "Self":
                        userName = os.environ.get( "USERNAME" )
                    else:
                        userName = user
                    if os.path.isdir(os.path.join(globlaRepoPath, userName)):
                        oPoseFolders = [d for d in os.listdir(os.path.join(globlaRepoPath, userName))]
                        if model == "All":
                            for iPose in oPoseFolders:
                                pose_items.append("Global: "+iPose)
                                pose_items.append(os.path.join(globlaRepoPath, userName, iPose))
                        elif model == "Selected":
                            oModelCheck = []
                            for iSel in oSel:
                                if iSel.Type == "#model":
                                    oModelCheck.append(iSel.Name.split("_")[0])
                                else:
                                    oModelCheck.append(iSel.Model.Name.split("_")[0])
                            for iPose in oPoseFolders:
                                if iPose.split("_")[0] in oModelCheck:
                                    pose_items.append("Global: "+iPose)
                                    pose_items.append(os.path.join(globlaRepoPath, userName, iPose))
                        elif model == "In_Scene":
                            oRoot = xsi.ActiveSceneRoot
                            oModelCheck = []
                            for iModel in oRoot.FindChildren2():
                                if iModel.Type == "#model":
                                    oModelCheck.append(iModel.Name.split("_")[0])
                            for iPose in oPoseFolders:
                                if iPose.split("_")[0] in oModelCheck:
                                    pose_items.append("Global: "+iPose)
                                    pose_items.append(os.path.join(globlaRepoPath, userName, iPose))
            else:
                lm("No poses found", 4)




    gear_poseLibManager_OnInit(repo , user, model, pose_items)

def gear_poseLibManager_newPose_OnClicked():
    xsi.gear_newPose()


def gear_poseLibManager_preferences_OnClicked():
    xsi.gear_prefPoseLib()


##########################################################
# New Pose command
##########################################################
def gear_newPose_Execute():
    if xsi.ActiveSceneRoot.Properties("gear_newPoseProp"):
        xsi.DeleteObj(xsi.ActiveSceneRoot.Properties("gear_newPoseProp"))

    prop = xsi.ActiveSceneRoot.AddProperty("gear_newPoseProp", False, "gear_newPoseProp")


    ds.inspect(prop, 350, 150)

def gear_newPoseProp_Define(in_ctxt):

    prop = in_ctxt.Source


    prop.AddParameter3("parPoseName", c.siString, "New Pose Name?", None, None, False, False)
    prop.AddParameter3("parRepo", c.siString, 0, 0, None, False, False)

def gear_newPoseProp_OnInit():
    repo_items = ["Current_DB", "Current_DB", "Global", "Global"]


    #Layout____________________________________

    layout = PPG.PPGLayout
    layout.Clear()

    layout.AddTab("Main")
    layout.AddGroup("NEW POSE")
    layout.AddItem("parPoseName", "Pose Name")
    layout.AddEnumControl("parRepo", repo_items, "Target Repository", c.siControlCombo)
    PPG.parRepo.Value = repo_items[1]
    layout.EndGroup()



    #layout.AddSpacer()

    item = layout.AddButton("saveNewPose", "Save New Pose")
    item.SetAttribute(c.siUICX, 330)
    item.SetAttribute(c.siUICY, 40)

    PPG.Refresh()
def gear_newPoseProp_saveNewPose_OnClicked():


    #Check if the name is valid
    oName = PPG.parPoseName.Value
    if not  oName.isalnum():
        lm("The name is not valid, use alphanumeric characters only ", 2)
    else:
        #Check is something is selected
        oSel = xsi.Selection
        if oSel.Count:
            #Construt the path
            userName = os.environ.get( "USERNAME" )
            #Global Path
            if PPG.parRepo.Value == "Global":
                if xsi.Preferences.Categories("gear_prefPoseLib"):
                    globalPath = Application.GetValue("preferences.gear_prefPoseLib.global_Repo")
                else:
                    globalPath = "Ops! you forget to set the preferences"
                    userPath = False

                if  os.path.isdir(globalPath):
                    userPath = os.path.join(globalPath, userName)
                    if not os.path.isdir(userPath):
                        os.makedirs(userPath)

                else:
                    lm("Global Path preferences are not set correctly. Looks like the folder: " + globalPath +" Doesn't exist.", 4 )

            #Current DB user path
            else:
                currentProject = xsi.ActiveProject2.Path
                currentPosePath = os.path.join(currentProject, "PoseLib")
                if not os.path.isdir(currentPosePath):
                    os.makedirs(currentPosePath)
                    lm("New folder for poses in the current datebase (DB) was created: " + currentPosePath )

                userPath = os.path.join(currentPosePath, userName)
                if not os.path.isdir(userPath):
                    os.makedirs(userPath)

            if userPath:
                oModel = oSel(0).Model
                modName = oModel.Name.split("_")[0]
                #Check if the pose exist and ask for overwrite
                oReturn = 6 # is the return value fo "yes" in the msgBox. We use it as default.
                if os.path.isdir(os.path.join(userPath, modName + "_" + oName)):
                   oReturn = XSIUIToolkit.MsgBox( "The pose exist!!. Do you want to overwrite it?", c.siMsgYesNo )
                else:
                    #Create folders if doesn't exist
                    os.makedirs(os.path.join(userPath, modName + "_" + oName))
                if oReturn == 6:
                    #Create xml pose
                    oModel = oSel(0).Model
                    root = xml.Element(oModel.Name)

                    # Function indentation ===============================
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
                    # ===========================================


                    for oItem in oSel:
                        collection = XSIFactory.CreateActiveXObject( "XSI.Collection" )

                        collection.AddItems( oItem )

                        oKeyable = collection.FindObjectsByMarkingAndCapabilities( None, c.siKeyable )

                        child = xml.Element(oItem.Name)
                        root.append(child)

                        for oParam in oKeyable:
                            childParam = xml.Element(".".join(oParam.FullName.split(".")[2:]))
                            childParam.attrib["Value"] = str(oParam.Value)
                            #childParam.attrib["scriptName"] = str(oParam.ScriptName)
                            child.append(childParam)

                    indent(root)
                    posePath = os.path.join(userPath, modName +  "_" + oName, oName + ".xml")
                    file = open(posePath, "w")

                    xml.ElementTree(root).write(file)

                    file.close()

                    #Capture the image
                    currFrame = xsi.ActiveProject.Properties("Play Control").Parameters("Current").Value

                    oViewportCapture = xsi.Dictionary.GetObject("ViewportCapture")


                    xsi.SetValue("Views.view*.*Camera.camvis.gridaxisvis", False, "")
                    xsi.SetValue("Views.view*.*Camera.camvis.constructionlevel", False, "")
                    xsi.SetValue("*Camera.camvis.gridaxisvis", False, "")
                    xsi.SetValue("*Camera.camvis.constructionlevel", False, "")

                    oViewportCapture.NestedObjects[0].PutValue2(None, os.path.join(userPath, modName + "_" + oName, oName + ".jpg"))  # path FileName
                    oViewportCapture.NestedObjects[1].PutValue2(None, "(fn)(ext)")  # frame Padding
                    oViewportCapture.NestedObjects[2].PutValue2(None, "75")  # Width
                    oViewportCapture.NestedObjects[3].PutValue2(None, "75")  # Height
                    oViewportCapture.NestedObjects[4].PutValue2(None, "1")  # Scale Factor
                    oViewportCapture.NestedObjects[5].PutValue2(None, "True")  # user pixel ratio
                    oViewportCapture.NestedObjects[6].PutValue2(None, "1.0")  # pixel ratio
                    oViewportCapture.NestedObjects[10].PutValue2(None, currFrame) # Start Frame
                    oViewportCapture.NestedObjects[11].PutValue2(None, currFrame) # End Frame
                    oViewportCapture.NestedObjects[12].PutValue2(None, "False")  # Launch Flipbook

                    xsi.CaptureViewport( -1, False )

                    xsi.SetValue("Views.view*.*Camera.camvis.gridaxisvis", True, "")
                    xsi.SetValue("Views.view*.*Camera.camvis.constructionlevel", True, "")
                    xsi.SetValue("*Camera.camvis.gridaxisvis", True, "")
                    xsi.SetValue("*Camera.camvis.constructionlevel", True, "")

                    #Create the miniSynoptic
                    imageName = oName +".jpg"
                    oDate =  strftime("%a, %d %b %Y %H:%M:%S")
                    synCretor(posePath, imageName,  oName, userName, oDate, oModel.Name)
                else:
                    lm("Creation cancelled", 2)
            else:
                lm("Set preferences before save poses in the global repo", 2)
        else:
            lm("Nothing selected, Pose can not be stored", 2)

    PPG.Close()
    if xsi.ActiveSceneRoot.Properties("gear_newPoseProp"):
        xsi.DeleteObj(xsi.ActiveSceneRoot.Properties("gear_newPoseProp"))

def synCretor(posePath, imageName,  poseName, userName, oDate, originalModel):
    if xsi.Preferences.Categories("gear_prefPoseLib"):
        controlGoups = xsi.GetValue("preferences.gear_prefPoseLib.control_groups_list")
    else:
        controlGoups =  '''"controlers_01_grp", "controlers_facial_grp", "controlers_slider_grp"'''

    filePath = SEP.join(posePath.split(SEP)[:-1])
    posePath = "/".join(posePath.split(SEP)) # we need to use "/" for html compatibility
    synCode = '''
<html>
<body version="2">
<script language="Python">
##########################################################
# Globals
##########################################################
import xml.etree.cElementTree as xml
from win32com.client import constants as c
xsi = Application
lm = xsi.LogMessage
##########################################################
# Functions
##########################################################
def applyPose(pose, oSel=False, onlySel = False, percent = False):
    tree = xml.parse(pose)
    Log = True
    if onlySel:
        if oSel:
            for control in oSel:
                collection = XSIFactory.CreateActiveXObject( "XSI.Collection" )
                collection.AddItems( control )
                oKeyable = collection.FindObjectsByMarkingAndCapabilities( None, c.siKeyable )
                node =tree.find(control.Name)
                if node != None:
                    Log = False
                    if percent:
                        for oParam in oKeyable:
                            if oParam.ScriptName in ["rotx", "roty", "rotz", "posx", "posy", "posz", "sclx", "scly", "sclz"]:
                                oParamTag = ".".join(oParam.FullName.split(".")[2:])
                                oElem = node.find(oParamTag)
                                currVal = oParam.GetValue2()
                                val =  float(oElem.get("Value"))
                                if currVal >= 0 or currVal <= 0:
                                    valDif = currVal - val
                                    increment = valDif * (percent / 100.0)
                                    newVal = currVal + (increment * -1)
                                    if val < 0 and currVal > val:
                                        oParam.PutValue2(None,  newVal)
                                    elif val > 0 and currVal < val:
                                        oParam.PutValue2(None,  newVal)
                                    else:
                                        oParam.PutValue2(None,  newVal)
                    else:
                        for oParam in oKeyable:
                            oParamTag = ".".join(oParam.FullName.split(".")[2:])
                            oElem = node.find(oParamTag)
                            val =  oElem.get("Value")
                            oParam.PutValue2(None,  val)
            if Log:
                lm("No values for the selected objects found in the pose", 4)
        else:
            lm("Please Select something before apply only to selection", 4)
    else:
        eRoot = tree.getroot()
        oModelName = str(eRoot).split("'")[1].split("_")[0]
        oRoot = Application.ActiveSceneRoot
        oModel = False
        if oSel and oSel.Count:
            if oSel(0).Type == "#model":
                oModel = oSel(0)
            else:
                oModel = oSel(0).Model
        else:
            # Guess Model from models in the scene
            for iModel in oRoot.FindChildren2():
                if iModel.Type == "#model" and iModel.Name.split("_")[0] == oModelName and iModel.Groups:
                    oModel = iModel
        if oModel:
            for iGroup in oModel.Groups:
                if iGroup.Name in [''' + controlGoups + ''']:
                    for control in iGroup.Members:
                        collection = XSIFactory.CreateActiveXObject( "XSI.Collection" )
                        collection.AddItems( control )
                        oKeyable = collection.FindObjectsByMarkingAndCapabilities( None, c.siKeyable )
                        node =tree.find(control.Name)
                        if node != None:
                            if percent:
                                for oParam in oKeyable:
                                    if oParam.ScriptName in ["rotx", "roty", "rotz", "posx", "posy", "posz", "sclx", "scly", "sclz"]:
                                        oParamTag = ".".join(oParam.FullName.split(".")[2:])
                                        oElem = node.find(oParamTag)
                                        currVal = oParam.GetValue2()
                                        val =  float(oElem.get("Value"))
                                        if currVal >= 0 or currVal <= 0:
                                            valDif = currVal - val
                                            increment = valDif * (percent / 100.0)
                                            newVal = currVal + (increment * -1)
                                            if val < 0 and currVal > val:
                                                oParam.PutValue2(None,  newVal)
                                            elif val > 0 and currVal < val:
                                                oParam.PutValue2(None,  newVal)
                                            else:
                                                oParam.PutValue2(None,  newVal)
                            else:
                                for oParam in oKeyable:
                                    oParamTag = ".".join(oParam.FullName.split(".")[2:])
                                    oElem = node.find(oParamTag)
                                    val =  oElem.get("Value")
                                    oParam.PutValue2(None,  val)
        else:
            lm("Nothing selected found. And guess model functionality didn't match any model suitable for: " + oModelName , 4)
##########################################################
# Logic
##########################################################
def pose(in_obj, in_mousebutton, in_keymodifier):
    oSel = xsi.Selection
    perc = Application.GetValue(in_obj +  ".percentage")
    pose ="'''+ posePath + '''"
    #Apply complete pose
    if in_mousebutton == 0 and in_keymodifier == 0:
        applyPose(pose, oSel, False, False)
    #Apply complete pose in percentage
    if in_mousebutton == 0 and in_keymodifier == 4:
        applyPose(pose, oSel, False, perc)
    #Apply pose to selection
    if in_mousebutton == 1 and in_keymodifier == 0:
        applyPose(pose, oSel, True, False)
    #Apply pose to selection in percentage
    if in_mousebutton == 1 and in_keymodifier == 4:
        applyPose(pose, oSel, True, perc)
    #Show pose info
    if in_mousebutton == 0 and in_keymodifier == 2:
        Message = """
        Pose Name = '''+ poseName + '''
        File Path = '''+ filePath + '''
        Original Model = '''+ originalModel + '''
        Date = '''+ oDate + '''
        User = '''+ userName + '''
        """
        XSIUIToolkit.MsgBox( Message, 64, "Pose information" )
</SCRIPT>
<map name="SynopticMap">
<area shape="rect" coords="0,0,75,75" title='''+ poseName + ''' NOHREF onClick="pose">
</map>
<img src='''+ imageName + ''' usemap="#SynopticMap">
</body>
</html>
'''
    f = open( os.path.join(filePath, poseName + ".htm"), 'w')
    f.write(synCode)



##########################################################
# Pose Lib Preferences command
##########################################################


def gear_prefPoseLib_Execute():

    if xsi.ActiveSceneRoot.Properties("gear_prefPoseLibProp"):
        xsi.DeleteObj(xsi.ActiveSceneRoot.Properties("gear_prefPoseLibProp"))

    prop = xsi.ActiveSceneRoot.AddProperty("gear_prefPoseLibProp", False, "gear_prefPoseLibProp")


    ds.inspect(prop, 550, 200)

def gear_prefPoseLibProp_Define(in_ctxt):

    prop = in_ctxt.Source

    prop.AddParameter3("global_Repo", c.siString, 0, 0, None, False, False)
    prop.AddParameter3("list_Size", c.siInt4, 500, 1, None, False, False)
    prop.AddParameter3("control_groups_list", c.siString, 0, 0, None, False, False)


def gear_prefPoseLibProp_OnInit():



    #Layout____________________________________

    layout = PPG.PPGLayout
    layout.Clear()

    layout.AddTab("Main")
    layout.AddGroup("PoseLib preferences")

    layout.AddItem( "global_Repo", "Global repo path", c.siControlFolder)
    layout.AddItem("list_Size", "List size in pixels", c.siControlNumber )
    layout.AddItem( "control_groups_list", "Control Group List", c.siControlString)
    if xsi.Preferences.Categories("gear_prefPoseLib"):
        PPG.global_Repo.Value = xsi.GetValue("preferences.gear_prefPoseLib.global_Repo")
        PPG.list_Size.Value = xsi.GetValue("preferences.gear_prefPoseLib.list_Size")
        PPG.control_groups_list.Value = xsi.GetValue("preferences.gear_prefPoseLib.control_groups_list")
    else:
        PPG.global_Repo.Value = "Select global repo path"
        PPG.list_Size.Value = 500
        PPG.control_groups_list.Value = '''"controlers_01_grp","controlers_facial_grp", "controlers_slider_grp"'''

    layout.EndGroup()

    layout.AddSpacer()

    item = layout.AddButton("setPreferences", "Set Preferences")
    item.SetAttribute(c.siUICX, 530)
    item.SetAttribute(c.siUICY, 40)

    PPG.Refresh()


def gear_prefPoseLibProp_setPreferences_OnClicked():

    if xsi.Preferences.Categories("gear_prefPoseLib"):
        xsi.SetValue("preferences.gear_prefPoseLib.global_Repo", PPG.global_Repo.Value, "")
        xsi.SetValue("preferences.gear_prefPoseLib.list_Size", PPG.list_Size.Value, "")
        xsi.SetValue("preferences.gear_prefPoseLib.control_groups_list", PPG.control_groups_list.Value, "")

    else:

        prop = xsi.ActiveSceneRoot.AddProperty("CustomProperty", False, "gear_prefPoseLib")
        prop.AddParameter3("global_Repo", c.siString, 0, 0, None, False, False)
        prop.AddParameter3("list_Size", c.siInt4, 500, 1, None, False, False)
        prop.AddParameter3("control_groups_list", c.siString, 0, 0, None, False, False)

        prop.global_Repo.Value = PPG.global_Repo.Value
        prop.list_Size.Value = PPG.list_Size.Value
        prop.control_groups_list.Value = PPG.control_groups_list.Value

        xsi.InstallCustomPreferences (prop, "gear_prefPoseLib")


    PPG.Close()
    if xsi.ActiveSceneRoot.Properties("gear_prefPoseLibProp"):
        xsi.DeleteObj(xsi.ActiveSceneRoot.Properties("gear_prefPoseLibProp"))


##########################################################
# menu register
##########################################################

def gear_poseLib_Menu_Init( in_ctxt ):
    oMenu = in_ctxt.Source
    oMenu.AddCommandItem("gear poseLib ","gear_poseLib")
    return True