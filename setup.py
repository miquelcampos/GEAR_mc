# -*- coding: utf-8 -*-
#!/usr/bin/env python

from distutils.core import setup

config = {
    "name": "gear",
    "description": "GEAR is a complete and production quality toolset for rigging and animation inside Autodesk Softimage.",
    "author": "Jeremie Passerin",
    "author_email": "geerem@hotmail.com",
    "url": "http://gear.jeremiepasserin.com",
    "version": "1.1.0",
    "packages": ["gear",
                 "gear.xsi",
                 "gear.xsi.rig",
                 "gear.xsi.rig.component",
                 "gear.xsi.rig.component.arm_2jnt_01",
                 "gear.xsi.rig.component.arm_2jnt_02",
                 "gear.xsi.rig.component.chain_01",
                 "gear.xsi.rig.component.chain_cns_01",
                 "gear.xsi.rig.component.control_01",
                 "gear.xsi.rig.component.control_02",
                 "gear.xsi.rig.component.eyebrow_01",
                 "gear.xsi.rig.component.eyelid_01",
                 "gear.xsi.rig.component.eye_01",
                 "gear.xsi.rig.component.foot_bk_01",
                 "gear.xsi.rig.component.head_ik_01",
                 "gear.xsi.rig.component.leg_2jnt_01",
                 "gear.xsi.rig.component.leg_2jnt_02",
                 "gear.xsi.rig.component.leg_3jnt_01",
                 "gear.xsi.rig.component.leg_3jnt_02",
                 "gear.xsi.rig.component.meta_01",
                 "gear.xsi.rig.component.mouth_01",
                 "gear.xsi.rig.component.neck_ik_01",
                 "gear.xsi.rig.component.neck_ik_02",
                 "gear.xsi.rig.component.spine_ik_01",
                 "gear.xsi.rig.component.tail_01",
                 "gear.xsi.rig.component.wing_01"],
    "package_data": {"gear": ["xsi/jsop/*.js",
                              "xsi/rig/component/_templates/*.xml"]},
    "scripts": []}

setup(**config)
