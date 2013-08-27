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

## @package gear.xsi.rig.component
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
# built-in
import os

# gear
import gear
from gear.xsi import xsi, c, XSIFactory, XSIMath

import gear.xsi.primitive as pri
import gear.xsi.ppg as ppg
import gear.xsi.vector as vec
import gear.xsi.parameter as par
import gear.xsi.fcurve as fcu
import gear.xsi.icon as ico

##########################################################
# BUILDER
##########################################################
class MainComponent(object):

    steps = ["Objects", "Properties", "Operators", "Connect", "Finalize"]

    local_params = ("posx", "posy", "posz", "rotx", "roty", "rotz", "rotorder", "sclx", "scly", "sclz")
    t_params = ("posx", "posy", "posz")
    r_params = ("rotx", "roty", "rotz", "rotorder")
    s_params = ("sclx", "scly", "sclz")
    tr_params = ("posx", "posy", "posz", "rotx", "roty", "rotz", "rotorder")
    rs_params = ("rotx", "roty", "rotz", "rotorder", "sclx", "scly", "sclz")
    x_axis = XSIMath.CreateVector3(1,0,0)
    y_axis = XSIMath.CreateVector3(0,1,0)
    z_axis = XSIMath.CreateVector3(0,0,1)

    # =====================================================
    ## Init Method.
    # @param self
    # @param rig Rig - The parent Rig of this component.
    # @param guide ComponentGuide - The guide for this component.
    def __init__(self, rig, guide):

        # --------------------------------------------------
        # Main Objects
        self.rig = rig
        self.guide = guide

        self.options = self.rig.options
        self.model = self.rig.model
        self.settings = self.guide.values

        self.name = self.settings["comp_name"]
        self.side = self.settings["comp_side"]
        self.index = self.settings["comp_index"]

        # --------------------------------------------------
        # Shortcut to useful settings
        self.size = self.guide.size

        self.color_fk = self.options[self.side + "_color_fk"]
        self.color_ik = self.options[self.side + "_color_ik"]

        self.negate = self.side == "R"
        if self.negate:
            self.n_sign = "-"
            self.n_factor = -1
        else:
            self.n_sign = ""
            self.n_factor = 1

        # --------------------------------------------------
        # Builder init
        self.groups = {} ## Dictionary of groups
        self.controlers = [] ## List of all the controlers of the component
        self.inv_params = XSIFactory.CreateObject("XSI.Collection")

        if not self.settings["set_ctl_grp"] or (self.settings["set_ctl_grp"] and self.settings["ctl_grp"] == ""):
            self.settings["ctl_grp"] = "01"

        # --------------------------------------------------
        # Property init
        self.anim_layout = ppg.PPGLayout()
        self.anim_logic = ppg.PPGLogic()
        self.setup_layout = ppg.PPGLayout()
        self.setup_logic = ppg.PPGLogic()

        self.ui = None

        # --------------------------------------------------
        # Connector init
        self.connections = {}
        self.connections["standard"]  = self.connect_standard

        self.relatives = {}

        # --------------------------------------------------
        # Step
        self.stepMethods = [eval("self.step_0%s"%i) for i in range(len(self.steps))]

    # =====================================================
    # BUILDING STEP
    # =====================================================
    ## Step 00. Initial Hierarchy, create objects and set the connection relation.
    # @param self
    def step_00(self):
        self.initialHierarchy()
        self.addObjects()
        self.setRelation()
        return

    ## Step 01. Get the properties host, create parameters and set layout and logic.
    # @param self
    def step_01(self):
        self.getHost()
        self.addParameters()
        self.addLayout()
        self.addLogic()
        self.setUI()
        return

    ## Step 02. Apply all the operators.
    # @param self
    def step_02(self):
        self.addOperators()
        return

    ## Step 03. Connect the component to the rest of the rig.
    # @param self
    def step_03(self):
        self.initConnector()
        self.addConnection()
        self.connect()
        self.postConnect()
        return

    ## Step 04. Finalize the component.
    # @param self
    def step_04(self):
        self.finalize()
        return

    ## NOT YET AVAILABLE
    def step_05(self):
        self.addPostSkin()
        return

    # =====================================================
    # OBJECTS
    # =====================================================
    ## Build the initial hierarchy of the component.\n
    # Add the root and if needed the shadow root
    # @param self
    def initialHierarchy(self):

        # Root -------------------------------
        self.root = pri.addNullFromPos(self.model, self.getName("root"), self.guide.pos["root"], self.options["size"]*.1)
        self.addToGroup(self.root, "hidden")

        # Shd --------------------------------
        if self.options["shadowRig"]:
            self.shd_org = self.rig.shd_org.AddNull(self.getName("shd_org"))
            self.addToGroup(self.shd_org, "hidden")

    ## Add all the objects needed to create the component.\n
    # REIMPLEMENT. This method should be reimplemented in each component.\n
    # Try not to apply any constraint, operator, or expression in here. Just X3DObjects.
    # @param self
    def addObjects(self):
        return

    ## Add the object in a collection for later group creation
    # @param self
    # @param objs Single or List of X3DObject - object to put in group
    # @param names Single or List of String - names of the groups to create
    def addToGroup(self, objects, names=["hidden"]):

        if not isinstance(names, list):
            names = [names]

        if not isinstance(objects, list):
            objects = [objects]

        for name in names:
            if name not in self.groups.keys():
                self.groups[name] = []

            self.groups[name].extend(objects)

    def addToCtlGroup(self, objects, names=None):

        if names is None:
            names = [self.settings["ctl_grp"]]
        elif not isinstance(names, list):
            names = [names]

        if not isinstance(objects, list):
            objects = [objects]

        for name in names:
            name = "controlers_"+name
            if name not in self.groups.keys():
                self.groups[name] = []

            self.groups[name].extend(objects)
            self.controlers.extend(objects)

    def addShadow(self, obj, name):

        if self.options["shadowRig"]:
            shd = pri.addImplicite(self.shd_org, "Cube", self.getName(str(name)+"_shd"), obj.Kinematics.Global.Transform, self.options["size"]*.15 )
            shd.Kinematics.AddConstraint("Pose", obj, False)
        else:
            shd = pri.addImplicite(obj, "Cube", self.getName(str(name)+"_shd"), obj.Kinematics.Global.Transform, self.options["size"]*.15)

        self.addToGroup(shd, "deformers")

        return shd

    def getNormalFromPos(self, pos):
        if len(pos) < 3:
            gear.log("%s : Not enough references to define normal"%self.fullName, gear.sev_error)

        return vec.getPlaneNormal(pos[0], pos[1], pos[2])


    def getBiNormalFromPos(self, pos):
        if len(pos) < 3:
            gear.log("%s : Not enough references to define binormal"%self.fullName, gear.sev_error)

        return vec.getPlaneBiNormal(pos[0], pos[1], pos[2])

    # =====================================================
    def addCtl(self, parent, name, t, color, icon, **kwargs):

        prim = None
        if self.getName(name) in self.rig.guide.controlers.keys():
            prim = self.rig.guide.controlers[self.getName(name)]
            #Get color from rig
            rR = prim.obj.Properties('display').Parameters(12).GetValue2(None)
            rG = prim.obj.Properties('display').Parameters(13).GetValue2(None)
            rB = prim.obj.Properties('display').Parameters(14).GetValue2(None)
            color = [rR, rG,rB]

        ctl = ico.primOrIcon(prim, parent, self.getName(name), t, color, icon, kwargs=kwargs)
        self.addToCtlGroup(ctl)
        return ctl

    # =====================================================
    # PROPERTY
    # =====================================================
    ## Get the host for the properties.
    # @param self
    def getHost(self):

        self.uihost = self.rig.findUIHost(self.settings["uiHost"])
        self.anim_prop = self.uihost.anim_prop
        self.setup_prop = self.uihost.setup_prop

    ## Add parameters to the anim and setup properties to control the component.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def addParameters(self):
        return

    ## Define the layout of the anim and setup properties.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def addLayout(self):
        return

    ## Define the logic of the anim and setup properties.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def addLogic(self):
        return

    def setUI(self):

        # Layout
        for source_layout, target_layout in ((self.anim_layout, self.uihost.anim_layout),(self.setup_layout, self.uihost.setup_layout)):

            target_layout.beforeCode.extend(source_layout.beforeCode)
            target_layout.afterCode.extend(source_layout.afterCode)

            for name, tab in source_layout.tabs.items():
                newtab = target_layout.addTab(name)
                if not newtab.items:
                    row = newtab.addRow()
                    r_group = row.addGroup("Right")
                    c_group = row.addGroup("")
                    l_group = row.addGroup("Left")
                else:
                    row = newtab.items[0]
                    r_group = row.items[0]
                    c_group = row.items[1]
                    l_group = row.items[2]

                if self.side == "R":
                    group = r_group
                elif self.side == "C":
                    group = c_group
                elif self.side == "L":
                    group = l_group

                group.items.extend(tab.items)

        # Logic
        self.uihost.anim_logic.addGlobalCode(self.anim_logic.getValue())
        self.uihost.setup_logic.addGlobalCode(self.setup_logic.getValue())

    ## Add a parameter to the animation property.\n
    # Note that animatable and keyable are True per default.
    # @param self
    # @param scriptName String - Parameter scriptname.
    # @param valueType Integer - siVariantType.
    # @param value Variant - Default parameter value.
    # @param minimum Variant - mininum value.
    # @param maximum Variant - maximum value.
    # @param sugMinimum Variant - suggested mininum value.
    # @param sugMaximum Variant - suggested maximum value.
    # @param animatable Boolean - True to make parameter animatable.
    # @param readOnly Boolean - True to make parameter readOnly.
    # @param keyable Boolean - True to make parameter keyable.
    # @return Parameter - The newly created parameter.
    def addAnimParam(self, scriptName, valueType, value, minimum=None, maximum=None, sugMinimum=None, sugMaximum=None, animatable=True, readOnly=False, keyable=True):

        capabilities = 1*animatable + 2*readOnly + 4 + 2048*keyable
        param = self.anim_prop.AddParameter2(self.getName(scriptName), valueType, value, minimum, maximum, sugMinimum, sugMaximum, c.siClassifUnknown, capabilities, scriptName)

        return param

    ## Add a parameter to the setup property.\n
    # Note that animatable and keyable are false per default.
    # @param self
    # @param scriptName String - Parameter scriptname.
    # @param valueType Integer - siVariantType.
    # @param value Variant - Default parameter value.
    # @param minimum Variant - mininum value.
    # @param maximum Variant - maximum value.
    # @param sugMinimum Variant - suggested mininum value.
    # @param sugMaximum Variant - suggested maximum value.
    # @param animatable Boolean - True to make parameter animatable.
    # @param readOnly Boolean - True to make parameter readOnly.
    # @param keyable Boolean - True to make parameter keyable.
    # @return Parameter - The newly created parameter.
    def addSetupParam(self, scriptName, valueType, value, minimum=None, maximum=None, sugMinimum=None, sugMaximum=None, animatable=False, readOnly=False, keyable=False):

        capabilities = 1*animatable + 2*readOnly + 4 + 2048*keyable
        param = self.setup_prop.AddParameter2(self.getName(scriptName), valueType, value, minimum, maximum, sugMinimum, sugMaximum, c.siClassifUnknown, capabilities, scriptName)

        return param

    ## Add a parameter to the setup property.\n
    # Note that animatable and keyable are false per default.
    # @param self
    # @param scriptName String - Parameter scriptname.
    # @param valueType Integer - siVariantType.
    # @param value Variant - Default parameter value.
    # @param minimum Variant - mininum value.
    # @param maximum Variant - maximum value.
    # @param sugMinimum Variant - suggested mininum value.
    # @param sugMaximum Variant - suggested maximum value.
    # @param animatable Boolean - True to make parameter animatable.
    # @param readOnly Boolean - True to make parameter readOnly.
    # @param keyable Boolean - True to make parameter keyable.
    # @return Parameter - The newly created parameter.
    def addSetupFCurveParam(self, scriptName, ref_fcv):

        ref_fcv.scriptName = self.getName(scriptName)
        param = ref_fcv.create(self.setup_prop)

        return param

    # =====================================================
    # OPERATORS
    # =====================================================
    ## Apply operators, constraint, expressions to the hierarchy.\n
    # REIMPLEMENT. This method should be reimplemented in each component.\n
    # We shouldn't create any new object in this method.
    # @param self
    def addOperators(self):
        return

    # =====================================================
    # CONNECTOR
    # =====================================================
    ## Add more connection definition to the set.\n
    # REIMPLEMENT. This method should be reimplemented in each component.\n
    # Only if you need to use an new connection (not the standard).
    # @param self
    def addConnection(self):
        return

    ## Set the relation beetween object from guide to rig.\n
    # REIMPLEMENT. This method should be reimplemented in each component.
    # @param self
    def setRelation(self):
        for name in self.guide.objectNames:
            self.relatives[name] = self.root

    ## Return the relational object from guide to rig.
    # @param self
    # @param local name of the guide object.
    def getRelation(self, name):
        if name not in self.relatives.keys():
            gear.log("Can't find reference for object : " + self.fullName + "." + name, gear.sev_error)
            return False

        return self.relatives[name]

    def initConnector(self):

        parent_name = "none"
        if self.guide.parentComponent is not None:
            parent_name = self.guide.parentComponent.getName(self.guide.parentLocalName)

        self.parent = self.rig.findChild(parent_name)
        self.parent_comp = self.rig.findComponent(parent_name)

    ## Connect the component to the rest of the rig using the defined connection.
    # @param
    def connect(self):

        if self.settings["connector"] not in self.connections.keys():
            gear.log("Unable to connect object", gear.sev_error)
            return False

        self.connections[self.settings["connector"]]()

        return True

    ## standard connection definition. This is a simple parenting of the root.
    # @param self
    def connect_standard(self):
        self.parent.AddChild(self.root)

    ## standard connection definition with ik and upv references.
    # @param self
    def connect_standardWithIkRef(self):
        self.parent.AddChild(self.root)

        # Set the Ik Reference
        if self.settings["ikrefarray"]:
            ref_names = self.settings["ikrefarray"].split(",")
            if len(ref_names) == 1:
                ref = self.rig.findChild(ref_names[0])
                ref.AddChild(self.ik_cns)
            else:
                for i, ref_name in enumerate(ref_names):
                    ref = self.rig.findChild(ref_name)
                    cns = self.ik_cns.Kinematics.AddConstraint("Pose", ref, True)
                    par.addExpression(cns.Parameters("active"), self.pIkRef.FullName+" == "+str(i))

        # Set the Upv Reference
        if self.settings["upvrefarray"]:
            ref_names = self.settings["upvrefarray"].split(",")
            if len(ref_names) == 1:
                ref = self.rig.findChild(ref_names[0])
                ref.AddChild(self.upv_cns)
            else:
                for i, ref_name in enumerate(ref_names):
                    ref = self.rig.findChild(ref_name)
                    cns = self.upv_cns.Kinematics.AddConstraint("Pose", ref, True)
                    par.addExpression(cns.Parameters("active"), self.pUpvRef.FullName+" == "+str(i))

    ## Post connection actions.
    # REIMPLEMENT. This method should be reimplemented in each component.\n
    # @param self
    def postConnect(self):
        return

    # =====================================================
    # FINALIZE
    # =====================================================
    def finalize(self):

        # Set the layout and logic in the ppg
        if self.ui is not None:
            self.ui.fillLayoutAndLogic()

    # =====================================================
    # MISC
    # =====================================================
    ## Return the name for component element
    # @param self
    # @param name String - Name.
    def getName(self, name="", side=None):

        if side is None:
            side = self.side

        name = str(name)

        if name:
            return self.name + "_" + side + str(self.index) + "_" + name
        else:
            return self.fullName

    # =====================================================
    # PROPERTIES
    # =====================================================
    ## return the fullname of the component
    # @param self
    def getFullName(self):
        return self.guide.fullName

    ## return the type of the component
    # @param self
    def getType(self):
        return self.guide.type

    fullName = property(getFullName)
    type = property(getType)
