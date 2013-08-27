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

using namespace XSI;
using namespace MATH;

///////////////////////////////////////////////////////////////
// STRUCT
///////////////////////////////////////////////////////////////
class sixXFSpringUserData
{
public:
   CVector3 s;
   CVector3 sv;
   CQuaternion r;
   CQuaternion rv;
   CVector3 t;
   CVector3 tv;
};

class sixRotSpringUserData
{
public:
   CVector3 pos;
   CVector3 vel;
};

///////////////////////////////////////////////////////////////
// DEFINE METHODS
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_xfspring_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_xfspring_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_xfspring_op_Update( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_rotspring_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_rotspring_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_rotspring_op_Update( CRef& in_ctxt );

///////////////////////////////////////////////////////////////
// XF SPRING OP
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_xfspring_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();
   pdef = factory.CreateParamDef(L"fr",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"fc",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"speed",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.25,0,100,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"damping",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.01,0,1,0,.1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"scale",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1000,0,2);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",2,0,1000,0,2);
   op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout =============================================
XSIPLUGINCALLBACK CStatus sn_xfspring_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;

   layout = ctxt.GetSource();
   layout.Clear();

   CValueArray modeItems(14);
   modeItems[0] = L"Scaling";
   modeItems[1] = (LONG)0l;
   modeItems[2] = L"Rotation";
   modeItems[3] = (LONG)1l;
   modeItems[4] = L"Translation";
   modeItems[5] = (LONG)2l;
   modeItems[6] = L"Scl + Rot";
   modeItems[7] = (LONG)3l;
   modeItems[8] = L"Rot + Tran";
   modeItems[9] = (LONG)4l;
   modeItems[10] = L"Scl + Tran";
   modeItems[11] = (LONG)5l;
   modeItems[12] = L"S + R + T";
   modeItems[13] = (LONG)6l;

   layout.AddEnumControl(L"mode",modeItems,L"Mode");
   layout.AddItem(L"speed",L"Speed");
   layout.AddItem(L"damping",L"Damping");
   layout.AddItem(L"scale",L"Scale");

   return CStatus::OK;
}

// Update ===================================================
XSIPLUGINCALLBACK CStatus sn_xfspring_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   KinematicState parentKine = (CRef)ctxt.GetInputValue(0);
   CTransformation parentXF = parentKine.GetTransform();
   CVector3 parentScl = parentXF.GetScaling();
   CQuaternion parentRot = parentXF.GetRotationQuaternion();
   CVector3 parentPos = parentXF.GetTranslation();

   // get the parameters
   double speed = 0.1 * (double)ctxt.GetParameterValue(L"speed");
   double damp = ctxt.GetParameterValue(L"damping");
   double scale = ctxt.GetParameterValue(L"scale");
   bool doScaling = false;
   bool doRotation = false;
   bool doTranslation = false;
   long mode = (LONG)ctxt.GetParameterValue(L"mode");
   switch(mode)
   {
      case 0:
      {
         doScaling = true;
         break;
      }
      case 1:
      {
         doRotation = true;
         break;
      }
      case 2:
      {
         doTranslation = true;
         break;
      }
      case 3:
      {
         doScaling = true;
         doRotation = true;
         break;
      }
      case 4:
      {
         doRotation = true;
         doTranslation = true;
         break;
      }
      case 5:
      {
         doScaling = true;
         doTranslation = true;
         break;
      }
      case 6:
      {
         doScaling = true;
         doRotation = true;
         doTranslation = true;
         break;
      }
   }
   long fc = (LONG)ctxt.GetParameterValue(L"fc");
   long fr = (LONG)ctxt.GetParameterValue(L"fr");

   // check if the userdata exists!
   CValue userDataFromOp = ctxt.GetUserData();
   sixXFSpringUserData * ud = NULL;

   if(userDataFromOp.m_t != CValue::siPtr)
   {
      ud = new sixXFSpringUserData;
      ud->s = parentScl;
      ud->sv.PutNull();
      ud->r = parentRot;
      ud->rv.SetIdentity();
      ud->t = parentPos;
      ud->tv.PutNull();
      ctxt.PutUserData(XSI::CValue(ud));
   }
   else
   {
      ud = (sixXFSpringUserData *)(void*) userDataFromOp;
      if(fc == fr)
      {
         ud->s = parentScl;
         ud->sv.PutNull();
         ud->r = parentRot;
         ud->rv.SetIdentity();
         ud->t = parentPos;
         ud->tv.PutNull();
      }
   }

   // calculate the scaling spring!
   if(doScaling)
   {
      CVector3 diff;
      diff.Sub(parentScl,ud->s);
      ud->sv.LinearlyInterpolate(ud->sv,diff,speed);
      ud->sv.ScaleInPlace(1.0 - damp);
      ud->s.AddInPlace(ud->sv);

      // scale the output
      diff.Sub(parentScl,ud->s);
      diff.ScaleInPlace(scale);
      diff.AddInPlace(parentScl);
      parentXF.SetScaling(diff);
   }

   // calculate the scaling spring!
   if(doRotation)
   {
      CQuaternion diff;
      diff.Invert(ud->r);
      diff.MulInPlace(parentRot);
      ud->rv.Slerp(ud->rv,diff,speed);
      ud->rv.Slerp(ud->rv,CQuaternion(),damp);
      ud->r.MulInPlace(ud->rv);

      // scale the output
      diff.Invert(ud->r);
      diff.MulInPlace(parentRot);
      diff.Slerp(CQuaternion(),diff,scale);
      diff.Mul(parentRot,diff);
      parentXF.SetRotationFromQuaternion(diff);
   }

   // calculate the position spring!
   if(doTranslation)
   {
      CVector3 diff;
      diff.Sub(parentPos,ud->t);
      ud->tv.LinearlyInterpolate(ud->tv,diff,speed);
      ud->tv.ScaleInPlace(1.0 - damp);
      ud->t.AddInPlace(ud->tv);

      // scale the output
      diff.Sub(ud->t,parentPos);
      diff.ScaleInPlace(scale);
      diff.AddInPlace(parentPos);
      parentXF.SetTranslation(diff);
   }

   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(parentXF);
   return CStatus::OK;
}

///////////////////////////////////////////////////////////////
// ROT SPRING OP
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_rotspring_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();
   pdef = factory.CreateParamDef(L"fr",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"fc",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"speed",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.25,0,100,0,1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"damping",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.01,0,1,0,.1);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"clamp_min",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,0,100000,0,10);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"clamp_max",CValue::siDouble,siPersistable | siAnimatable,L"",L"",10,0,100000,0,10);
   op.AddParameter(pdef,param);
   pdef = factory.CreateParamDef(L"x_pos",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,100000,0,10);
   op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ================================================
XSIPLUGINCALLBACK CStatus sn_rotspring_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;
   layout = ctxt.GetSource();
   layout.Clear();
   layout.AddItem(L"speed",L"Speed");
   layout.AddItem(L"damping",L"Damping");
   layout.AddItem(L"clamp_min",L"Clamp Min");
   layout.AddItem(L"clamp_max",L"Clamp Max");
   layout.AddItem(L"x_pos",L"Position X");
   return CStatus::OK;
}

// Update ====================================================
XSIPLUGINCALLBACK CStatus sn_rotspring_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   //KinematicState parentObjKine = ctxt.GetInputValue(0);
   KinematicState parentKine = (CRef)ctxt.GetInputValue(0);
   double boneLength = ctxt.GetInputValue(1);
   CTransformation parentXF = parentKine.GetTransform();

   // get the parameters
   double speed = ctxt.GetParameterValue(L"speed");
   speed *= .1;
   double damp = ctxt.GetParameterValue(L"damping");
   double clamp_min = ctxt.GetParameterValue(L"clamp_min");
   double clamp_max = ctxt.GetParameterValue(L"clamp_max");
   double pos_x = ctxt.GetParameterValue(L"x_pos");
   long fc = (LONG)ctxt.GetParameterValue(L"fc");
   long fr = (LONG)ctxt.GetParameterValue(L"fr");
   CVector3 parentPos = MapObjectPositionToWorldSpace(parentXF,CVector3(pos_x,0,0));
   CVector3 tipPos = MapObjectPositionToWorldSpace(parentXF,CVector3(pos_x+boneLength,0,0));
   CVector3 parentY = MapObjectPositionToWorldSpace(parentXF,CVector3(0,1,0));

   // check if the userdata exists!
   CValue userDataFromOp = ctxt.GetUserData();
   sixRotSpringUserData * ud = NULL;

   if(userDataFromOp.m_t != CValue::siPtr)
   {
      ud = new sixRotSpringUserData;
      ud->pos = tipPos;
      ud->vel.PutNull();
      ctxt.PutUserData(XSI::CValue(ud));
   }
   else
   {
      ud = (sixRotSpringUserData *)(void*) userDataFromOp;
      if(fc == fr)
      {
         ud->pos = tipPos;
         ud->vel.PutNull();
      }
   }

   // calculate the new vel + pos
   CVector3 diff;
   diff.Sub(tipPos,ud->pos);
   ud->vel.LinearlyInterpolate(ud->vel,diff,speed);
   ud->vel.ScaleInPlace(1.0 - damp);
   ud->pos.AddInPlace(ud->vel);

   // remap now using clamping
   diff.Sub(ud->pos,tipPos);
   double length = diff.GetLength();
   if(length > clamp_min)
   {
      double clamp_delta = clamp_max - clamp_min;

      if(length > clamp_max + clamp_delta)
      {
         length = clamp_max;
      }
      else
      {
         length = clamp_max - (clamp_max + clamp_delta - length) * .5;
      }

      // clamp the distance to the center!
      diff.NormalizeInPlace();
      diff.ScaleInPlace(length);
      ud->pos.Add(tipPos,diff);
      ud->pos.Sub(ud->pos,parentPos);
      ud->pos.NormalizeInPlace();
      ud->pos.ScaleInPlace(boneLength);
      ud->pos.AddInPlace(parentPos);
   }

   // calculate the output axes
   CVector3 parentX,parentZ;
   parentX.Sub(ud->pos,parentPos);
   parentX.NormalizeInPlace();
   parentZ.Cross(parentX,parentY);
   parentZ.NormalizeInPlace();
   parentY.Cross(parentZ,parentX);
   parentY.NormalizeInPlace();

   // output the spring's position
   parentXF.SetTranslation(parentPos);
   parentXF.SetRotationFromXYZAxes(parentX,parentY,parentZ);

   KinematicState outKine(ctxt.GetOutputTarget());
   //parentXF = MapWorldPoseToObjectSpace(parentObjKine.GetTransform(),parentXF);
   outKine.PutTransform(parentXF);
   return CStatus::OK;
}
