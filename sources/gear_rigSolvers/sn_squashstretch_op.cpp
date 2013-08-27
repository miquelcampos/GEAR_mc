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
// STRUCT
///////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////
// DEFINE METHODS
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_squashstretch_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_squashstretch_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_squashstretch_op_Update( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_squashstretch_prop_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_squashstretch_prop_DefineLayout( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_squashstretch2_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_squashstretch2_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_squashstretch2_op_Update( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_curvelength_op_Update( CRef& in_ctxt );

double max(double a,double b);
double clamp(double v,double a,double b);
double smoothstep(double v);
CTransformation InterpolateTransform(CTransformation xf1, CTransformation xf2, double blend);

///////////////////////////////////////////////////////////////
// SQUASH STRETCH
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_squashstretch_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"driver",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-100000,100000,0,24);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",50,0,100,0,100);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"sq_min",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"sq_max",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"sq_y",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"sq_z",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"st_min",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"st_max",CValue::siDouble,siPersistable | siAnimatable,L"",L"",10,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"st_y",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,-100000,100000,1,5);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"st_z",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,-100000,100000,1,5);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ==============================================
XSIPLUGINCALLBACK CStatus sn_squashstretch_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;

   oLayout = ctxt.GetSource();
   oLayout.Clear();

   oLayout.AddItem(L"blend",L"Blend");
   oLayout.AddItem(L"driver",L"Driver");
   oLayout.AddItem(L"u",L"U Value");

   oLayout.AddGroup("Squash");
   oLayout.AddRow();
   oLayout.AddItem(L"sq_min",L"Min");
   oLayout.AddItem(L"sq_max",L"Max");
   oLayout.EndRow();
   oLayout.AddRow();
   oLayout.AddItem(L"sq_y",L"Y");
   oLayout.AddItem(L"sq_z",L"Z");
   oLayout.EndRow();
   oLayout.EndGroup();

   oLayout.AddGroup("Stretch");
   oLayout.AddRow();
   oLayout.AddItem(L"st_min",L"Min");
   oLayout.AddItem(L"st_max",L"Max");
   oLayout.EndRow();
   oLayout.AddRow();
   oLayout.AddItem(L"st_y",L"Y");
   oLayout.AddItem(L"st_z",L"Z");
   oLayout.EndRow();
   oLayout.EndGroup();

   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_squashstretch_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   KinematicState parentKine = (CRef)ctxt.GetInputValue(0);
   CTransformation parentXF = parentKine.GetTransform();
   CVector3 parentScl = parentXF.GetScaling();

   double blend = ctxt.GetParameterValue(L"blend");
   double driver = ctxt.GetParameterValue(L"driver");
   double sq_min = ctxt.GetParameterValue(L"sq_min");
   double sq_max = ctxt.GetParameterValue(L"sq_max");
   double st_min = ctxt.GetParameterValue(L"st_min");
   double st_max = ctxt.GetParameterValue(L"st_max");
   double sq_y = ctxt.GetParameterValue(L"sq_y");
   double sq_z = ctxt.GetParameterValue(L"sq_z");
   double st_y = ctxt.GetParameterValue(L"st_y");
   double st_z = ctxt.GetParameterValue(L"st_z");
   double sq_ratio = smoothstep(clamp(max(sq_max - driver,0) / max(sq_max - sq_min,0.0001),0,1));
   double st_ratio = smoothstep(1.0 - clamp(max(st_max - driver,0) / max(st_max - st_min,0.0001),0,1));
   sq_y *= sq_ratio;
   sq_z *= sq_ratio;
   st_y *= st_ratio;
   st_z *= st_ratio;

   parentScl.PutY(parentScl.GetY() * max( 0, 1.0 + sq_y + st_y ));
   parentScl.PutZ(parentScl.GetZ() * max( 0, 1.0 + sq_z + st_z ));

   parentScl.LinearlyInterpolate(parentXF.GetScaling(),parentScl,blend);

   parentXF.SetScaling(parentScl);

   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(parentXF);
   return CStatus::OK;
}

// Property Define ============================================
XSIPLUGINCALLBACK CStatus sn_squashstretch_prop_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomProperty oCustomProperty;
   Parameter oParam;
   oCustomProperty = ctxt.GetSource();

   oCustomProperty.AddParameter(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1,0,1,oParam);
   oCustomProperty.AddParameter(L"sq_min",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-100000,100000,0,1,oParam);
   oCustomProperty.AddParameter(L"sq_max",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,-100000,100000,0,1,oParam);
   oCustomProperty.AddParameter(L"sq_y",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1,oParam);
   oCustomProperty.AddParameter(L"sq_z",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1,oParam);
   oCustomProperty.AddParameter(L"st_min",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,-100000,100000,0,1,oParam);
   oCustomProperty.AddParameter(L"st_max",CValue::siDouble,siPersistable | siAnimatable,L"",L"",10,-100000,100000,0,1,oParam);
   oCustomProperty.AddParameter(L"st_y",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,-100000,100000,1,5,oParam);
   oCustomProperty.AddParameter(L"st_z",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,-100000,100000,1,5,oParam);

   oCustomProperty.AddParameter(L"sq_y_profile",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,-100000,100000,1,5,oParam);
   oCustomProperty.AddParameter(L"sq_z_profile",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,-100000,100000,1,5,oParam);
   oCustomProperty.AddParameter(L"st_y_profile",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,-100000,100000,1,5,oParam);
   oCustomProperty.AddParameter(L"st_z_profile",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,-100000,100000,1,5,oParam);

   return CStatus::OK;
}

// Property DefineLayout ======================================
XSIPLUGINCALLBACK CStatus sn_squashstretch_prop_DefineLayout( CRef& in_ctxt )
{
   return sn_squashstretch_op_DefineLayout(in_ctxt);
}


///////////////////////////////////////////////////////////////
// SQUASH STRETCH 2
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_squashstretch2_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();

   oPDef = oFactory.CreateParamDef(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"driver",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-100000,100000,0,24);
   oCustomOperator.AddParameter(oPDef,oParam);

   oPDef = oFactory.CreateParamDef(L"driver_min",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"driver_ctr",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"driver_max",CValue::siDouble,siPersistable | siAnimatable,L"",L"",10,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oPDef = oFactory.CreateParamDef(L"axis",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,2,0,2);
   oCustomOperator.AddParameter(oPDef,oParam);

   oPDef = oFactory.CreateParamDef(L"squash",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-1,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"stretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-1,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ==============================================
XSIPLUGINCALLBACK CStatus sn_squashstretch2_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;

   oLayout = ctxt.GetSource();
   oLayout.Clear();

   oLayout.AddItem(L"blend",L"Blend");

   oLayout.AddGroup("Driver");
   oLayout.AddItem(L"driver",L"Driver");
   oLayout.AddRow();
   oLayout.AddItem(L"driver_min",L"Min");
   oLayout.AddItem(L"driver_ctr",L"Center");
   oLayout.AddItem(L"driver_max",L"Max");
   oLayout.EndRow();
   oLayout.EndGroup();

   oLayout.AddGroup("Axis");
   CValueArray modeItems(6);
   modeItems[0] = L"X";
   modeItems[1] = (LONG)0l;
   modeItems[2] = L"Y";
   modeItems[3] = (LONG)1l;
   modeItems[4] = L"Z";
   modeItems[5] = (LONG)2l;
   oLayout.AddEnumControl(L"axis",modeItems,L"Pointing Axis");
   oLayout.EndGroup();

   oLayout.AddGroup("Stretch / Squash");
   oLayout.AddItem(L"squash",L"Squash");
   oLayout.AddItem(L"stretch",L"Stretch");
   oLayout.EndGroup();

   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_squashstretch2_op_Update( CRef& in_ctxt )
{
   // Inputs -------------------------
   OperatorContext ctxt( in_ctxt );
   KinematicState k = (CRef)ctxt.GetInputValue(0);
   CTransformation t = k.GetTransform();

   KinematicState parent_kine = (CRef)ctxt.GetInputValue(1);
   CTransformation parent_trans = parent_kine.GetTransform();
   CVector3 parent_scl = parent_trans.GetScaling();

   double blend = ctxt.GetParameterValue(L"blend");
   double driver = ctxt.GetParameterValue(L"driver");

   double driver_min = ctxt.GetParameterValue(L"driver_min");
   double driver_ctr = ctxt.GetParameterValue(L"driver_ctr");
   double driver_max = ctxt.GetParameterValue(L"driver_max");

   double axis = ctxt.GetParameterValue(L"axis");

   double stretch = ctxt.GetParameterValue(L"stretch");
   double squash = ctxt.GetParameterValue(L"squash");

   // Ratio ---------------------------
   double st_ratio = clamp(max(driver - driver_ctr, 0) / max(driver_max - driver_ctr, 0.0001), 0,1);
   double sq_ratio = clamp(max(driver_ctr - driver, 0) / max(driver_ctr - driver_min, 0.0001), 0,1);

   squash *= sq_ratio;
   stretch *= st_ratio;

   CVector3 scl;
   scl.Set(parent_scl.GetX(), parent_scl.GetY(), parent_scl.GetZ());

   if (axis != 0)
      scl.PutX(parent_scl.GetX() * max( 0, 1.0 + squash + stretch ));

   if (axis != 1)
      scl.PutY(parent_scl.GetY() * max( 0, 1.0 + squash + stretch ));

   if (axis != 2)
      scl.PutZ(parent_scl.GetZ() * max( 0, 1.0 + squash + stretch ));

   scl.LinearlyInterpolate(parent_scl, scl, blend);

   t.SetScaling(scl);

   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(t);

   return CStatus::OK;
}

///////////////////////////////////////////////////////////////
// CURVE LENGTH
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_curvelength_op_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs -----------------------------------------
	Primitive crvprim(ctxt.GetInputValue(0));
	NurbsCurveList crvlist(crvprim.GetGeometry());
	NurbsCurve crv(crvlist.GetCurves().GetItem(0));

//	KinematicState kCurve(ctxt.GetInputValue(2));
//	CTransformation tCurve(kCurve.GetTransform());

	// ------------------------------------------------
	//CVector3 vScale(tCurve.GetScaling());

	double length;
	crv.GetLength(length);

	OutputPort outPort = ctxt.GetOutputPort();
	outPort.PutValue(length);

	return CStatus::OK;
}

