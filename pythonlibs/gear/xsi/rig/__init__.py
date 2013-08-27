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

## @package gear.xsi.rig
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
import sys
import re
import os
import datetime
import getpass

import gear
from gear.xsi import xsi, c, dynDispatch, XSIFactory, XSIMath
from gear.xsi.rig.guide import RigGuide

from gear.xsi.rig.component import MainComponent

import gear.xsi.uitoolkit as uit
import gear.xsi.ppg as ppg
import gear.xsi.primitive as pri
import gear.xsi.parameter as par
import gear.xsi.icon as icon
import gear.xsi.io as io
import gear.xsi.geometry as geo
import gear.xsi.envelope as env
import gear.xsi.animation as ani

##########################################################
# RIG
##########################################################
## The main rig class.
class Rig(object):

    # =====================================================
    ## Init Method
    # @param self
    def __init__(self):

        self.guide = RigGuide()

        ## Dictionary of component.\n
        # Keys are the component fullname (ie. 'arm_L0')
        self.components = {}
        self.componentsIndex = []

        ## Dictionary of Groups.
        self.groups = {}
        self.addToGroup(None, ["hidden", "unselectable", "deformers", "geometries"])

        self.plog = uit.ProgressLog(True, False)

    # =====================================================
    ## Build the rig from selected guides.
    # @param self
    def buildFromSelection(self):

        # Cet the option first otherwise the change wight might do won't be taken
        sel = xsi.Selection(0)
        if sel.Type == "#model":
            guide_model = sel
        else:
            guide_model = sel.Model
        guide_options = guide_model.Properties("options")
        if not guide_options:
            gear.log("Can't generate rig, invalid model selected", gear.sev_error)
            return

        rtn = xsi.InspectObj(guide_options, "", "Options", c.siModal, False)
        if rtn:
            return False

        # Check guide is valid
        self.guide.setFromSelection()
        if not self.guide.valid:
            return

        # Build
        self.build()

    ## Build the rig from xml definition file.
    # @param self
    # @param path String - Path to an xml definition.
    def buildFromFile(self, path=None):

        self.guide.setFromFile(path)
        if not self.guide.valid:
            return

        self.build()

    # =====================================================
    # @param self
    def build(self):

        self.options = self.guide.values
        self.guides = self.guide.components

        gear.log("= GEAR RIG SYSTEM ==============================================")
        self.plog.start("Gear Rig Sytem started")

        # Set Preferences
        xsi.SetUserPref("SI3D_NODETRANSFORM_CHILD_COMPENSATE", False)
        xsi.SetUserPref("SI3D_CONSTRAINT_COMPENSATION_MODE", False)

        self.initialHierarchy()
        self.processComponents()
        self.finalize()

        gear.log("= GEAR BUILD RIG DONE ================ [ " + self.plog.getTime() + " ] ======")
        self.plog.hideBar()

        return self.model

    # =====================================================
    ## Build the initial hierarchy of the rig
    # Create the rig model, the main properties, and a couple of base organisation nulls
    # Get the global size of the rig
    # @param self
    def initialHierarchy(self):

        self.plog.log("Build initial hierarchy")

        # --------------------------------------------------
        # Model
        self.model = xsi.ActiveSceneRoot.AddModel(None, self.options["rigName"])
        self.model.Properties("visibility").Parameters("viewvis").Value = False

        # --------------------------------------------------
        # Global Ctl
        if "global_C0_ctl" in self.guide.controlers.keys():
            self.global_ctl = self.guide.controlers["global_C0_ctl"].create(self.model, "global_C0_ctl", XSIMath.CreateTransform(), self.options["C_color_fk"])
        else:
            self.global_ctl = icon.crossarrow(self.model, "global_C0_ctl", 10, self.options["C_color_fk"])

        par.setKeyableParameters(self.global_ctl, ["posx", "posy", "posz", "rotx", "roty", "rotz", "rotorder"])
        self.addToGroup(self.global_ctl, "controlers_01")

        # --------------------------------------------------
        # INFOS
        self.info_prop = self.model.AddProperty("gear_PSet", False, "info")

        pRigName     = self.info_prop.AddParameter3("rig_name", c.siString, self.options["rigName"], None, None, False, True)
        pUser        = self.info_prop.AddParameter3("user", c.siString, getpass.getuser(), None, None, False, True)
        pIsWip       = self.info_prop.AddParameter3("isWip", c.siBool, self.options["mode"] != 0, None, None, False, True)
        pDate        = self.info_prop.AddParameter3("date", c.siString, datetime.datetime.now(), None, None, False, True)
        pXSIVersion  = self.info_prop.AddParameter3("xsi_version", c.siString, xsi.Version(), None, None, False, True)
        pGEARVersion = self.info_prop.AddParameter3("gear_version", c.siString, gear.getVersion(), None, None, False, True)
        pSynoptic    = self.info_prop.AddParameter3("synoptic", c.siString, self.options["synoptic"], None, None, False, False)
        pComments    = self.info_prop.AddParameter3("comments", c.siString, self.options["comments"], None, None, False, True)
        pComponentsGrid = self.info_prop.AddGridParameter("componentsGrid")


        self.components_grid = pComponentsGrid.Value
        self.components_grid.ColumnCount = 4
        self.components_grid.SetColumnLabel(0, "Name")
        self.components_grid.SetColumnLabel(1, "Type")
        self.components_grid.SetColumnLabel(2, "Version")
        self.components_grid.SetColumnLabel(3, "Author")

        self.info_layout = ppg.PPGLayout()
        self.info_mainTab = self.info_layout.addTab("Main")

        group = self.info_mainTab.addGroup("Main")
        group.addItem(pRigName.ScriptName, "Name")
        group.addItem(pUser.ScriptName, "User")
        group.addItem(pIsWip.ScriptName, "Is Wip")
        group.addItem(pDate.ScriptName, "Date")
        group.addItem(pXSIVersion.ScriptName, "XSI Version")
        group.addItem(pGEARVersion.ScriptName, "GEAR Version")
        group = self.info_mainTab.addGroup("Synoptic")
        item = group.addItem(pSynoptic.ScriptName, "Synoptic")
        item.setAttribute(c.siUINoLabel, True)
        group = self.info_mainTab.addGroup("Comments")
        item = group.addString(pComments.ScriptName, "", True, 120)
        item.setAttribute(c.siUINoLabel, True)

        self.info_componentTab = self.info_layout.addTab("Components")
        group = self.info_componentTab.addGroup("GEAR")
        group.addItem(pGEARVersion.ScriptName, "Version")
        group = self.info_componentTab.addGroup("Components")
        item = group.addItem(pComponentsGrid.ScriptName, "", c.siControlGrid)
        item.setAttribute(c.siUINoLabel, True)

        self.info_prop.Parameters("layout").Value = self.info_layout.getValue()

        # --------------------------------------------------
        # UI SETUP AND ANIM
        self.ui = UIHost(self.global_ctl)

        # Setup_Ctrl
        self.setup_mainTab = self.ui.setup_layout.addTab("Main")

        # Anim_Ctrl
        self.anim_mainTab = self.ui.anim_layout.addTab("Main")
        self.pRigScale    = self.ui.anim_prop.AddParameter2("rigScale", c.siDouble, 1, 0.001, None, .001, 3, c.siClassifUnknown, c.siAnimatable|c.siKeyable)
        self.pOGLLevel    = self.ui.anim_prop.AddParameter3("oglLevel", c.siInt4, 0, 0, 2, False, False)
        self.pResolutions = self.ui.anim_prop.AddParameter3("resolutions", c.siInt4, 0, 0, None, False, False)

        group = self.anim_mainTab.addGroup("Animate")
        group.addItem(self.pRigScale.ScriptName, "Global Scale")

        group = self.anim_mainTab.addGroup("Performance")
        #group.addEnumControl(self.pResolutions.ScriptName, ["default", 0], "Resolutions", c.siControlCombo)
        group.addItem(self.pOGLLevel.ScriptName, "OGL Level")

        # scale expression
        for s in "xyz":
            par.addExpression(self.global_ctl.Kinematics.Local.Parameters("scl"+s), self.pRigScale)

        # --------------------------------------------------
        # Basic set of null
        if self.options["shadowRig"]:
            self.shd_org = self.model.AddNull("shd_org")
            self.addToGroup(self.shd_org, "hidden")

    # =====================================================
    def processComponents(self):

        import gear.xsi.rig.component as comp

        self.plog.reset(len(self.guides), 1)

        # Init
        self.components_infos = {}
        for guide in self.guides.values():
            self.plog.log("Init", guide.fullName + " ("+guide.type+")", True)

            module_name = "gear.xsi.rig.component."+guide.type
            module = __import__(module_name, globals(), locals(), ["*"], -1)
            Component = getattr(module , "Component")

            component = Component(self, guide)
            if component.fullName not in self.componentsIndex:
                self.components[component.fullName] = component
                self.componentsIndex.append(component.fullName)

                self.components_infos[component.fullName] = [guide.compType, guide.getVersion(), guide.author]

        par.setDataGridFromDict(self.components_grid, self.components_infos)

        # Creation steps
        self.steps = MainComponent.steps

        self.plog.reset(len(self.guides) * self.options["step"]+1, 1)

        for i, name in enumerate(self.steps):
            for count, compName in enumerate(self.componentsIndex):
                component = self.components[compName]
                self.plog.log(name, component.fullName + " ("+component.type+")", True)
                component.stepMethods[i]()
                xsi.Refresh()

            if self.options["step"] >= 0 and i >= self.options["step"]:
                break

    # =====================================================
    ## Build the initial hierarchy of the rig
    # @param self
    def finalize(self):

        # Properties --------------------------------------
        self.plog.log("Filling layout and logic")
        self.ui.fillLayoutAndLogic()

        # Groups ------------------------------------------
        self.plog.log("Creating groups")
        # Retrieve group content from components
        for name in self.componentsIndex:
            component = self.components[name]
            for name, objects in component.groups.items():
                self.addToGroup(objects, name)

        # Creating all groups
        for name, objects in self.groups.items():
            collection = XSIFactory.CreateObject("XSI.Collection")
            collection.AddItems(objects)
            self.groups[name] = self.model.AddGroup(collection, name + "_grp")

        # Hidden
        if self.options["setHidden"]:
            self.groups["hidden"].Parameters("viewvis").Value = 0
            self.groups["hidden"].Parameters("rendvis").Value = 0

        # Unselectable
        if self.options["setUnselectable"]:
            self.groups["unselectable"].Parameters("selectability").Value = 0

        # Deformers
        if self.options["setDeformers"]:
            self.groups["deformers"].Parameters("viewvis").Value = 0
            self.groups["deformers"].Parameters("rendvis").Value = 0

        # Geometries
        if self.options["setGeometries"]:
            self.groups["geometries"].Parameters("selectability").Value = 0
            prop = self.groups["geometries"].AddProperty("GeomApprox")
            par.addExpression(prop.Parameters("gapproxmosl"), self.pOGLLevel)

        # Skin --------------------------------------------
        if self.options["addGeometry"]:
            self.plog.log("Applying skin")

            # Import geometry
            if self.options["geo_path"] and os.path.exists(self.options["geo_path"]):
                geo_model = xsi.ImportModel(self.options["geo_path"], xsi.ActiveSceneRoot, False, None)(1)

                geo_objects = geo_model.FindChildren()

                self.model.AddChild(geo_model.children)
                for group in geo_model.Groups:
                    target_group = pri.createOrReturnGroup(self.model, group.Name)
                    target_group.AddMember(group.Members)
                xsi.DeleteObj(geo_model)

                # Apply skin
                if self.options["skin_path"] and os.path.exists(self.options["skin_path"]):
                    xml_objs = io.getObjectDefinitions(self.options["skin_path"], geo_objects, False)

                    for obj in geo_objects:

                        if obj.Name not in xml_objs.keys():
                            continue

                        io.importSkin(xml_objs[obj.Name], obj)

        # Symmetry Mapping Template -----------------------
        if self.options["mode"] == 1:

            env.createSymmetryMappingTemplate(self.groups["deformers"].Members)

            for geo in self.groups["geometries"].Members:
                if geo.Type == "polymsh":
                    xsi.CreateSymmetryMap("SymmetryMap", geo, "Symmetry Map")

        # Mirror Animation Template -----------------------
        if self.options["mode"] == 0:
            cnx_prop = ani.createMirrorCnxTemplate(self.model)
            for count, compName in enumerate(self.componentsIndex):
                component = self.components[compName]
                inversed_params = component.inv_params.GetAsText().split(",")
                for ctl in component.controlers:
                    ani.addMirroringRule(ctl, cnx_prop, inversed_params, True)

        # Reset Pose --------------------------------------
        self.plog.log("Creating rest pose")
        controlers = XSIFactory.CreateObject("XSI.Collection")
        for group in self.model.Groups:
            if group.Name.startswith("controlers"):
                controlers.AddItems(group.Members)

        keyableParams = controlers.FindObjectsByMarkingAndCapabilities(None, c.siKeyable)
        xsi.StoreAction(self.model, keyableParams, 1, "reset", False)

        # Isolate and popup -------------------------------
        if self.options["isolateResult"]:
            xsi.SelectObj(self.model, "BRANCH")
            xsi.IsolateSelected(False, -1)
            xsi.DeselectAll()

        if self.options["popUpControls"]:
            xsi.InspectObj(self.ui.anim_prop)
            
    # =====================================================
    ## Add the object in a collection for later group creation.
    # @param self
    # @param objs Single or List of X3DObject - object to put in group.
    # @param names Single or List of String - names of the groups to create.
    def addToGroup(self, objects, names=["hidden"]):

        if not isinstance(names, list):
            names = [names]

        if not isinstance(objects, list):
            objects = [objects]

        # objects = [obj for obj in objects if obj is not None]

        for name in names:
            if name not in self.groups.keys():
                self.groups[name] = []

            self.groups[name].extend(objects)

    ## Return the object in the rig matching the guide object.
    # @param self
    # @param guideName String - Name of the guide object
    def findChild(self, guideName):

        if guideName is None:
            return self.global_ctl

        comp_name = "_".join(guideName.split("_")[:2])
        child_name = "_".join(guideName.split("_")[2:])

        if comp_name not in self.components.keys():
            return self.global_ctl

        return self.components[comp_name].getRelation(child_name)

    def findComponent(self, guideName):

        if guideName is None:
            return None

        comp_name = "_".join(guideName.split("_")[:2])
        child_name = "_".join(guideName.split("_")[2:])

        if comp_name not in self.components.keys():
            return None

        return self.components[comp_name]

    def findUIHost(self, guideName):

        if guideName is None:
            return self.ui

        comp_name = "_".join(guideName.split("_")[:2])
        child_name = "_".join(guideName.split("_")[2:])

        if comp_name not in self.components.keys():
            return self.ui

        if self.components[comp_name].ui is None:
            self.components[comp_name].ui = UIHost(self.components[comp_name].root)

        return self.components[comp_name].ui


##########################################################
# UI HOST
##########################################################
class UIHost(object):

    def __init__(self, parent):

        self.anim_prop = pri.createOrReturnPSet(parent, "anim_prop")
        self.setup_prop = pri.createOrReturnPSet(parent, "setup_prop")

        self.anim_prop.PPGLayout.SetAttribute(c.siUIShowChildren, False)
        self.setup_prop.PPGLayout.SetAttribute(c.siUIShowChildren, False)

        self.anim_layout = ppg.PPGLayout()
        self.anim_logic = ppg.PPGLogic()
        self.setup_layout = ppg.PPGLayout()
        self.setup_logic = ppg.PPGLogic()

    def fillLayoutAndLogic(self):

        self.anim_prop.Parameters("layout").Value = self.anim_layout.getValue()
        self.anim_prop.Parameters("logic").Value = self.anim_logic.getValue()

        self.setup_prop.Parameters("layout").Value = self.setup_layout.getValue()
        self.setup_prop.Parameters("logic").Value = self.setup_logic.getValue()
