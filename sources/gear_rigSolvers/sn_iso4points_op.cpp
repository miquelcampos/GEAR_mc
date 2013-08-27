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
XSIPLUGINCALLBACK CStatus sn_iso4point_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_iso4point_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_iso4point_op_Update( CRef& in_ctxt );

CVector3Array bezier4point(CVector3 a, CVector3 tan_a, CVector3 d, CVector3 tan_d, double u);

///////////////////////////////////////////////////////////////
// ISO 4 POINT
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_iso4point_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();
   pdef = factory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"v",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"y_scaling",CValue::siBool,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ==============================================
XSIPLUGINCALLBACK CStatus sn_iso4point_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;
   layout = ctxt.GetSource();
   layout.Clear();
   layout.AddItem(L"u",L"U Value");
   layout.AddItem(L"v",L"V Value");
   layout.AddItem(L"y_scaling",L"Y for Scaling");
   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_iso4point_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   double u = ctxt.GetParameterValue(L"u");
   double v = ctxt.GetParameterValue(L"v");
   bool yscl = ctxt.GetParameterValue(L"y_scaling");

   CTransformation result;
   CTransformation xf[4];
   CMatrix3 mtx[4];
   CVector3 pos[4];
   CVector3 tanx[4];
   CVector3 tanz[4];

   for(long i=0;i<4;i++)
   {
      xf[i] = KinematicState(ctxt.GetInputValue(i)).GetTransform();
      mtx[i] = xf[i].GetRotationMatrix3();
      pos[i] = xf[i].GetTranslation();
      tanx[i].MulByMatrix3(CVector3(xf[i].GetSclX()*2.5,0,0),mtx[i]);
      tanz[i].MulByMatrix3(CVector3(0,0,xf[i].GetSclZ()*2.5),mtx[i]);
   }

   CVector3Array res1,res2,res3;

   res1 = bezier4point(pos[0],tanx[0],pos[1],tanx[1],u);
   res2 = bezier4point(pos[2],tanx[2],pos[3],tanx[3],u);
   CVector3 tanu, tanv1, tanv2, tanv, tany;
   tanv1.LinearlyInterpolate(tanz[0],tanz[1],u);
   tanv1.NormalizeInPlace();
   tanv1.ScaleInPlace(tanz[0].GetLength()*(1.0-u) + tanz[1].GetLength()*u);
   tanv2.LinearlyInterpolate(tanz[2],tanz[3],u);
   tanv2.NormalizeInPlace();
   tanv2.ScaleInPlace(tanz[2].GetLength()*(1.0-u) + tanz[3].GetLength()*u);
   res3 = bezier4point(res1[0],tanv1,res2[0],tanv2,v);
   tanu.LinearlyInterpolate(res1[1],res2[1],v);
   tanu.NormalizeInPlace();
   tanu.ScaleInPlace(res1[1].GetLength()*(1.0-v) + res2[1].GetLength()*v);
   tanv = res3[1];

   CVector3 scl1,scl2,scl3;
   scl1.LinearlyInterpolate(xf[0].GetScaling(),xf[1].GetScaling(),u);
   scl2.LinearlyInterpolate(xf[2].GetScaling(),xf[3].GetScaling(),u);
   scl3.LinearlyInterpolate(scl1,scl2,v);

   if(yscl)
   {
      scl3.PutX(scl3.GetY());
      scl3.PutZ(scl3.GetY());
   }
   result.SetScaling(scl3);
   tanu.NegateInPlace();
   tany.Cross(tanu,tanv);
   tanv.Cross(tanu,tany);
   tanu.NormalizeInPlace();
   tany.NormalizeInPlace();
   tanv.NormalizeInPlace();

   result.SetRotationFromXYZAxes(tanu,tany,tanv);
   result.SetTranslation(res3[0]);

   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(result);

   //bezier4point

   return CStatus::OK;
}
