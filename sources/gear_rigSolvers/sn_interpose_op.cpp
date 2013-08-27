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
XSIPLUGINCALLBACK CStatus sn_interpose_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_interpose_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_interpose_op_Update( CRef& in_ctxt );

///////////////////////////////////////////////////////////////
// ISO 4 POINT
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_interpose_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();
   pdef = factory.CreateParamDef(L"blend_pos",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"blend_dir",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"blend_upv",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"blend_scl",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0,1,0,1);
   op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ==============================================
XSIPLUGINCALLBACK CStatus sn_interpose_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;
   layout = ctxt.GetSource();
   layout.Clear();
   layout.AddItem(L"blend_pos",L"Blend Position");
   layout.AddItem(L"blend_dir",L"Blend Direction");
   layout.AddItem(L"blend_upv",L"Blend Upvector");
   layout.AddItem(L"blend_scl",L"Blend Scaling");
   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_interpose_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   KinematicState kineA = (CRef)ctxt.GetInputValue(0);
   KinematicState kineB = (CRef)ctxt.GetInputValue(1);
   CTransformation xfA = kineA.GetTransform();
   CTransformation xfB = kineB.GetTransform();

   double blend_pos = ctxt.GetParameterValue(L"blend_pos");
   double blend_dir = ctxt.GetParameterValue(L"blend_dir");
   double blend_upv = ctxt.GetParameterValue(L"blend_upv");
   double blend_scl = ctxt.GetParameterValue(L"blend_scl");

   // first linearly interpolate position and scaling, as they are simple!
   CVector3 pos,scl,dirA,dirB,upvA,upvB,xAxis,yAxis,zAxis;
   pos.LinearlyInterpolate(xfA.GetTranslation(),xfB.GetTranslation(),blend_pos);
   scl.LinearlyInterpolate(xfA.GetScaling(),xfB.GetScaling(),blend_scl);

   // access direction and upvector (X and Z) for both transforms
   CMatrix3 rotA,rotB;
   rotA = xfA.GetRotationMatrix3();
   rotB = xfB.GetRotationMatrix3();
   dirA.MulByMatrix3(CVector3(1,0,0),rotA);
   dirB.MulByMatrix3(CVector3(1,0,0),rotB);
   upvA.MulByMatrix3(CVector3(0,1,0),rotA);
   upvB.MulByMatrix3(CVector3(0,1,0),rotB);

   // now interpolate the axis!
   xAxis.LinearlyInterpolate(dirA,dirB,blend_dir);
   yAxis.LinearlyInterpolate(upvA,upvB,blend_upv);
   zAxis.Cross(xAxis,yAxis);
   yAxis.Cross(zAxis,xAxis);
   xAxis.NormalizeInPlace();
   yAxis.NormalizeInPlace();
   zAxis.NormalizeInPlace();

   // construct the resulting transform
   CTransformation result;
   result.SetScaling(scl);
   result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
   result.SetTranslation(pos);

   // and output!
   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(result);

   return CStatus::OK;
}
