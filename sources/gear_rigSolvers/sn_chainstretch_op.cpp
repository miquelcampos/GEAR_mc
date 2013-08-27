/*

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

    Author:     Helge Mathee, Jeremie Passerin      helge.mathee@gmx.net, geerem@hotmail.com
    BetaTester: Miquel Campos
    Company:    Studio Nest (TM)
    Date:       2010 / 11 / 15

*/

#include <xsi_application.h>
#include <xsi_context.h>
#include <xsi_pluginregistrar.h>
#include <xsi_status.h>
#include <xsi_customoperator.h>
#include <xsi_operatorcontext.h>
#include <xsi_ppglayout.h>
#include <xsi_ppgeventcontext.h>
#include <xsi_selection.h>
#include <xsi_command.h>
#include <xsi_factory.h>
#include <xsi_primitive.h>
#include <xsi_kinematics.h>
#include <xsi_outputport.h>
#include <xsi_x3dobject.h>
#include <xsi_chaineffector.h>
#include <xsi_chainroot.h>
#include <xsi_chainbone.h>
#include <xsi_ref.h>
#include <xsi_transformation.h>
#include <xsi_vector3.h>
#include <xsi_comapihandler.h>
#include <xsi_argument.h>

using namespace XSI;
using namespace XSI::MATH;

///////////////////////////////////////////////////////////////
// STRUCT
///////////////////////////////////////////////////////////////
struct OpUserData
{

	double index;
	CTransformation t;
	double length0;
	double length1;
	double pref_rot;

	OpUserData()
			{
	}
} ;
///////////////////////////////////////////////////////////////
// DEFINE METHODS
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_stretchChain_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_stretchChain_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_stretchChain_op_Update( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_stretchChainMulti_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_stretchChainMulti_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_stretchChainMulti_op_Update( CRef& in_ctxt );

///////////////////////////////////////////////////////////////
// CHAIN STRETCH
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_stretchChain_op_Define( CRef& in_ctxt )
{
    Context ctxt( in_ctxt );
    CustomOperator op;
    Parameter param;
    CRef pdef;
    Factory oFactory = Application().GetFactory();
    op = ctxt.GetSource();

    // Initial Settings (Read Only)
    pdef = oFactory.CreateParamDef(L"rest0",CValue::siDouble,siPersistable | siReadOnly,L"",L"",0.0,0,1000.0,0,10.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"rest1",CValue::siDouble,siPersistable | siReadOnly,L"",L"",0.0,0,1000.0,0,10.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"prefrot",CValue::siDouble,siPersistable | siReadOnly,L"",L"",0,-9999,9999,-90,90);
    op.AddParameter(pdef,param);

    // Animatable Parameters
    pdef = oFactory.CreateParamDef(L"scale0",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,0,1000.0,0,2.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"scale1",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,0,1000.0,0,2.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"maxstretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,1.0,1000.0,1.0,2.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"soft",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0.0,4.0,0.0,1.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"slide",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0.0,1.0,0.0,1.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"reverse",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0.0,1.0,0.0,1.0);
    op.AddParameter(pdef,param);

    op.PutAlwaysEvaluate(false);
    op.PutDebug(0);

    return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sn_stretchChain_op_DefineLayout( CRef& in_ctxt )
{
    Context ctxt( in_ctxt );
    PPGLayout layout;
    PPGItem item;
    layout = ctxt.GetSource();
    layout.Clear();

    layout.AddGroup(L"Init");
    layout.AddItem(L"rest0", L"Bone 0 Length");
    layout.AddItem(L"rest1", L"Bone 1 Length");
    layout.AddItem(L"prefrot", L"Bone 1 Rot");
    layout.EndGroup();

    layout.AddGroup(L"Animate");
    item = layout.AddItem(L"scale0", L"Bone 0 Scale");
    item = layout.AddItem(L"scale1", L"Bone 1 Scale");
    item = layout.AddItem(L"maxstretch", L"Max Stretch");
    item = layout.AddItem(L"soft", L"Softness");
    item = layout.AddItem(L"slide", L"Slide");
    item = layout.AddItem(L"reverse", L"Reverse");
    layout.EndGroup();

	return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sn_stretchChain_op_Update( CRef& in_ctxt )
{
    OperatorContext ctxt( in_ctxt );

    // User Datas ------------------------------------
    CValue::siPtrType pUserData = ctxt.GetUserData();
    OpUserData* pOpState = (OpUserData*)pUserData;

    if ( pOpState == NULL || pOpState->index >= 4)
    {
        // First time called
        pOpState = new OpUserData();
        ctxt.PutUserData( (CValue::siPtrType)pOpState );

        // Inputs ---------------------------------------
        KinematicState root_kine(ctxt.GetInputValue(0));
        KinematicState ctrl_kine(ctxt.GetInputValue(1));
        CTransformation root_tra(root_kine.GetTransform());
        CTransformation ctrl_tra(ctrl_kine.GetTransform());
        CVector3 root_pos = root_tra.GetTranslation();
        CVector3 ctrl_pos = ctrl_tra.GetTranslation();
        CMatrix4 root_mat = root_tra.GetMatrix4();
        CMatrix4 root_matNeg;
        root_matNeg.Invert(root_mat);

        double rest0       = ctxt.GetParameterValue(L"rest0");
        double rest1       = ctxt.GetParameterValue(L"rest1");
        double pref_rot    = ctxt.GetParameterValue(L"prefrot");
        double scale0      = ctxt.GetParameterValue(L"scale0");
        double scale1      = ctxt.GetParameterValue(L"scale1");
        double softness    = ctxt.GetParameterValue(L"soft");
        double max_stretch = ctxt.GetParameterValue(L"maxstretch");
        double slide       = ctxt.GetParameterValue(L"slide");
        double reverse     = ctxt.GetParameterValue(L"reverse");

        // Distance with MaxStretch ---------------------
        double rest_length = rest0 * scale0 + rest1 * scale1;
        CVector3 vDistance;
        vDistance.MulByMatrix4(ctrl_pos, root_matNeg);
        double distance = vDistance.GetLength();
        double distance2 = distance;
        if (distance > (rest_length * max_stretch))
        {
            vDistance.NormalizeInPlace();
            vDistance.ScaleInPlace(rest_length * max_stretch);
            distance = rest_length * max_stretch;
        }

        // Adapt Softness value to chain length --------
        softness *= rest_length*.1;

        // Stretch and softness ------------------------
        /// We use the real distance from root to controler to calculate the softness
        /// This way we have softness working even when there is no stretch
        double stretch = distance/rest_length;
        if (stretch < 1)
            stretch = 1;
        double da = rest_length - softness;
        if (softness > 0 && distance2 > da)
        {
            double newlen = softness*(1.0 - exp(-(distance2 -da)/softness)) + da;
            stretch = distance / newlen;
        }

        double length0 = rest0 * stretch * scale0;
        double length1 = rest1 * stretch * scale1;

        // Reverse -------------------------------------
        double d = distance/(length0 + length1);

        double scale;
        if (reverse < 0.5)
            scale = 1-(reverse*2 * (1-d));
        else
            scale = 1-((1-reverse)*2 * (1-d));

        length0 *= scale;
        length1 *= scale;

        pref_rot = -(reverse-0.5) * 2 * pref_rot;

        // Slide ---------------------------------------
        double add;
        if (slide < .5)
            add = (length0 * (slide*2)) - (length0);
        else
            add = (length1 * (slide*2)) - (length1);

        length0 += add;
        length1 -= add;

        // Effector Position ----------------------------
        CTransformation t;
        vDistance.MulByMatrix4(vDistance, root_mat);
        t.SetTranslation(vDistance);

        pOpState->index = 0;
        pOpState->t = t;
        pOpState->length0 = length0;
        pOpState->length1 = length1;
        pOpState->pref_rot = pref_rot;
    }

    // Outputs -------------------------------------
    CRef outputPortRef=ctxt.GetOutputPort();
    OutputPort OutPort(outputPortRef);

    // Effector Transform
    if (OutPort.GetIndex() == 2)
    {
        KinematicState kOut = ctxt.GetOutputTarget();
        kOut.PutTransform(pOpState->t);
    }
    // Bone 0 Length
    else if (OutPort.GetIndex() == 3)
    {
        OutPort.PutValue(pOpState->length0);
    }
    // Bone 1 Length
    else if (OutPort.GetIndex() == 4)
    {
        OutPort.PutValue(pOpState->length1);
    }
    // Bone 1 PrefRot
    else if (OutPort.GetIndex() == 5)
    {
        OutPort.PutValue(pOpState->pref_rot);
    }

    pOpState->index += 1;

    return CStatus::OK;
}

///////////////////////////////////////////////////////////////
// CHAIN STRETCH MULTI
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_stretchChainMulti_op_Define( CRef& in_ctxt )
{
    Context ctxt( in_ctxt );
    CustomOperator op;
    Parameter param;
    CRef pdef;
    Factory oFactory = Application().GetFactory();
    op = ctxt.GetSource();

    // Initial Settings (Read Only)
    pdef = oFactory.CreateParamDef(L"restlength",CValue::siDouble,siPersistable | siReadOnly,L"",L"",0.0,0,1000.0,0,10.0);
    op.AddParameter(pdef,param);

    // Animatable Parameters
    pdef = oFactory.CreateParamDef(L"scale",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,0,1000.0,0,2.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"maxstretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,1.0,1000.0,1.0,2.0);
    op.AddParameter(pdef,param);
    pdef = oFactory.CreateParamDef(L"soft",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0.0,4.0,0.0,1.0);
    op.AddParameter(pdef,param);

    op.PutAlwaysEvaluate(false);
    op.PutDebug(0);

    return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sn_stretchChainMulti_op_DefineLayout( CRef& in_ctxt )
{
    Context ctxt( in_ctxt );
    PPGLayout layout;
    PPGItem item;
    layout = ctxt.GetSource();
    layout.Clear();

    layout.AddGroup(L"Init");
    layout.AddItem(L"restlength", L"Rest Length");
    layout.EndGroup();

    layout.AddGroup(L"Animate");
    item = layout.AddItem(L"scale", L"Scale");
    item = layout.AddItem(L"maxstretch", L"Max Stretch");
    item = layout.AddItem(L"soft", L"Softness");
    layout.EndGroup();

    return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sn_stretchChainMulti_op_Update( CRef& in_ctxt )
{

    OperatorContext ctxt( in_ctxt );

    // User Datas ------------------------------------
    CValue::siPtrType pUserData = ctxt.GetUserData();
    OpUserData* pOpState = (OpUserData*)pUserData;

    if ( pOpState == NULL || pOpState->index >= 2)
    {
        // First time called
        pOpState = new OpUserData();
        ctxt.PutUserData( (CValue::siPtrType)pOpState );

        // Inputs ---------------------------------------
        KinematicState root_kine(ctxt.GetInputValue(0));
        KinematicState ctrl_kine(ctxt.GetInputValue(1));
        CTransformation root_tra(root_kine.GetTransform());
        CTransformation ctrl_tra(ctrl_kine.GetTransform());
        CVector3 root_pos = root_tra.GetTranslation();
        CVector3 ctrl_pos = ctrl_tra.GetTranslation();
        CMatrix4 root_mat = root_tra.GetMatrix4();
        CMatrix4 root_matNeg;
        root_matNeg.Invert(root_mat);

        double rest_length = ctxt.GetParameterValue(L"restlength");
        double scale      = ctxt.GetParameterValue(L"scale");
        double softness   = ctxt.GetParameterValue(L"soft");
        double max_stretch = ctxt.GetParameterValue(L"maxstretch");

        // Distance with MaxStretch ---------------------
        rest_length = rest_length * scale - .00001;
        CVector3 vDistance;
        vDistance.MulByMatrix4(ctrl_pos, root_matNeg);
        double distance = vDistance.GetLength();
        double distance2 = distance;
        if (distance > (rest_length * max_stretch))
        {
                vDistance.NormalizeInPlace();
                vDistance.ScaleInPlace(rest_length * max_stretch);
                distance = rest_length * max_stretch;
        }

        // Adapt Softness value to chain length --------
        softness = softness * rest_length *.1;

        // Stretch and softness ------------------------
        /// We use the real distance from root to controler to calculate the softness
        /// This way we have softness working even when there is no stretch
        double stretch = distance/rest_length;
        if (stretch < 1)
            stretch = 1;
        double da = rest_length - softness;
        if (softness > 0 && distance2 > da)
        {
            double newlen = softness*(1.0 - exp(-(distance2 -da)/softness)) + da;
            stretch = distance / newlen;
        }

        double dScaleX = stretch * scale;

        // Effector Position ----------------------------
        CTransformation t;
        vDistance.MulByMatrix4(vDistance, root_mat);
        t.SetTranslation(vDistance);

        pOpState->index = 0;
        pOpState->t = t;
        pOpState->length0 = dScaleX;
    }

    // Outputs -------------------------------------
    CRef outputPortRef=ctxt.GetOutputPort();
    OutputPort OutPort(outputPortRef);

    // Effector Transform
    if (OutPort.GetIndex() == 2)
    {
        KinematicState kOut = ctxt.GetOutputTarget();
        kOut.PutTransform(pOpState->t);
    }
    // Bone 0 Length
    else if (OutPort.GetIndex() == 3)
    {
        OutPort.PutValue(pOpState->length0);
    }

    pOpState->index += 1;

    return CStatus::OK;
}
