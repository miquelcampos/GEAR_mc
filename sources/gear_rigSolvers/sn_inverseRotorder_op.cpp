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
XSIPLUGINCALLBACK CStatus sn_inverseRotorder_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_inverseRotorder_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_inverseRotorder_op_Update( CRef& in_ctxt );

///////////////////////////////////////////////////////////////
// INVERSE ROTORDER
///////////////////////////////////////////////////////////////
// Define =====================================================
CStatus sn_inverseRotorder_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();
	pdef = factory.CreateParamDef(L"rotorder",CValue::siInt4,siPersistable|siAnimatable,L"",L"",0,0,5,0,5);
	op.AddParameter(pdef,param);

	op.PutAlwaysEvaluate(false);
	op.PutDebug(0);

	return CStatus::OK;
}

// Define Layout =====================================================
XSIPLUGINCALLBACK CStatus sn_inverseRotorder_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem item;

   layout = ctxt.GetSource();
   layout.Clear();

   CValueArray orderItems(12);
   orderItems[0] = L"XYZ";
   orderItems[1] = (LONG)0l;
   orderItems[2] = L"XZY";
   orderItems[3] = (LONG)1l;
   orderItems[4] = L"YXZ";
   orderItems[5] = (LONG)2l;
   orderItems[6] = L"YZX";
   orderItems[7] = (LONG)3l;
   orderItems[8] = L"ZXY";
   orderItems[9] = (LONG)4l;
   orderItems[10] = L"ZYX";
   orderItems[11] = (LONG)5l;

   layout.AddGroup("Rotation");
   layout.AddEnumControl("rotorder", orderItems, "Order");
   layout.EndGroup();
   return CStatus::OK;
}

// Update =====================================================
CStatus sn_inverseRotorder_op_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	LONG rotorder = ctxt.GetParameterValue(L"rotorder");
	LONG out_ro = 0;

	if(rotorder == 0)
		out_ro = 5;
	else if (rotorder == 1)
		out_ro = 3;
	else if (rotorder == 2)
		out_ro = 4;
	else if (rotorder == 3)
		out_ro = 1;
	else if (rotorder == 4)
		out_ro = 2;
	else if (rotorder == 5)
		out_ro = 0;

	OutputPort Out = ctxt.GetOutputPort();
	Out.PutValue(out_ro);

	return CStatus::OK;
}
