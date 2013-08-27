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
#include <xsi_factory.h>
#include <xsi_pluginregistrar.h>
#include <xsi_status.h>
#include <xsi_customoperator.h>
#include <xsi_customproperty.h>
#include <xsi_operatorcontext.h>
#include <xsi_ppglayout.h>
#include <xsi_ppgeventcontext.h>
#include <xsi_primitive.h>
#include <xsi_kinematics.h>
#include <xsi_kinematicstate.h>
#include <xsi_math.h>
#include <xsi_doublearray.h>
#include <xsi_nurbscurvelist.h>
#include <xsi_nurbscurve.h>
#include <xsi_nurbssurfacemesh.h>
#include <xsi_nurbssurface.h>
#include <xsi_controlpoint.h>
#include <xsi_inputport.h>
#include <xsi_outputport.h>
#include <xsi_vector3.h>
#include <vector>

#include <iostream>
#include <float.h>
#include <math.h>

using namespace XSI;
using namespace MATH;

///////////////////////////////////////////////////////////////
// DEFINE METHODS
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_slerp_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_slerp_op__DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_slerp_op_Update( CRef& in_ctxt );

///////////////////////////////////////////////////////////////
// SLERP
///////////////////////////////////////////////////////////////
// Define =====================================================
CStatus sn_slerp_op_Define( CRef& in_ctxt )
{
	Context ctxt(in_ctxt);
	CustomOperator op;
	Parameter param;
	CRef pdef;
	Factory oFactory = Application().GetFactory();
	op = ctxt.GetSource();

	op = ctxt.GetSource();
	pdef = oFactory.CreateParamDef(L"ratio",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1l,0l,1l);
	op.AddParameter(pdef,param);

	op.PutAlwaysEvaluate(false);
	op.PutDebug(0);
	return CStatus::OK;
}

// Define Layout =====================================================
XSIPLUGINCALLBACK CStatus sn_slerp_op__DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;

   layout = ctxt.GetSource();
   layout.Clear();

   layout.AddGroup("Ratio");
   layout.AddItem("ratio", "Ratio");
   layout.EndGroup();

   return CStatus::OK;
}

// Update =====================================================
CStatus sn_slerp_op_Update( CRef& in_ctxt )
{
	OperatorContext ctxt(in_ctxt);

	// Inputs
	double ratio = ctxt.GetParameterValue(L"ratio");

	KinematicState k(ctxt.GetInputValue(0));
	CTransformation t(k.GetTransform());

	KinematicState kA(ctxt.GetInputValue(1));
	CTransformation tA(kA.GetTransform());

	KinematicState kB(ctxt.GetInputValue(2));
	CTransformation tB(kB.GetTransform());

	CQuaternion qA(tA.GetRotationQuaternion());
	CQuaternion qB(tB.GetRotationQuaternion());

	qA.Normalize();
	qB.Normalize();

	// Rotation
	CQuaternion qOut;
	qOut.Slerp(qA, qB, ratio);

	// Out
	t.SetRotationFromQuaternion (qOut);

	KinematicState out(ctxt.GetOutputTarget());
	out.PutTransform(t);

	return CStatus::OK;
}
