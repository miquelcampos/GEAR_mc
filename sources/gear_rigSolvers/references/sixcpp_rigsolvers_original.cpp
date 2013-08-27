/*
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/*
   Author:     Helge Mathee
   Betatester: Miquel Campos
   Company:    Sixbirds S.L.
   Date:       2010 / 01 / 18
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
#include <vector>
using namespace XSI;
using namespace MATH;


double min(double a, double b)
{
   if(a > b)
      return b;
   return a;
}
double max(double a,double b)
{
   if(a < b)
      return b;
   return a;
}
double clamp(double v,double a,double b)
{
   return max(a,min(b,v));
}

double pingpong(double v)
{
   if(v < .5)
      return v * 2.0;
   return (1.0 - v) * 2.0;
}

double smoothstep(double v)
{
   return sin((clamp(v,0,1)-.5) * XSI::MATH::PI) * 0.5 + 0.5;
}
double smoothstep2(double v)
{
   return 0.5 - cos(clamp(v,0,1) * 2.0 * XSI::MATH::PI) * 0.5;
}

XSIPLUGINCALLBACK CStatus XSILoadPlugin( PluginRegistrar& in_reg )
{
   in_reg.PutAuthor(L"matheeh");
   in_reg.PutName(L"sixcpp_rixsolvers_Plugin");
   in_reg.PutEmail(L"");
   in_reg.PutURL(L"");
   in_reg.PutVersion(1,0);

   // register all of the solvers
   in_reg.RegisterOperator(L"sixcpp_xfspring_op");
   in_reg.RegisterOperator(L"sixcpp_rotspring_op");
   in_reg.RegisterOperator(L"sixcpp_ik2bone_op");
   in_reg.RegisterOperator(L"sixcpp_ikfk2bone_op");
   in_reg.RegisterOperator(L"sixcpp_splinekine_op");
   in_reg.RegisterOperator(L"sixcpp_rollsplinekine_op");
   in_reg.RegisterOperator(L"sixcpp_interpose_op");
   in_reg.RegisterOperator(L"sixcpp_squashstretch_op");
   in_reg.RegisterOperator(L"sixcpp_iso4point_op");
   in_reg.RegisterOperator(L"sixcpp_null2curve_op");
   in_reg.RegisterOperator(L"sixcpp_null2surface_op");
   in_reg.RegisterOperator(L"sixcpp_curveslide_op");
   in_reg.RegisterOperator(L"sixcpp_mouthinterpose_op");

   // register all of the properties
   in_reg.RegisterProperty(L"sixcpp_ik2bone_prop");
   in_reg.RegisterProperty(L"sixcpp_ikfk2bone_prop");
   in_reg.RegisterProperty(L"sixcpp_splinekine_prop");
   in_reg.RegisterProperty(L"sixcpp_squashstretch_prop");
   in_reg.RegisterProperty(L"sixcpp_mouthinterpose_prop");

   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus XSIUnloadPlugin( const PluginRegistrar& in_reg )
{
   CString strPluginName;
   strPluginName = in_reg.GetName();
   Application().LogMessage(strPluginName + L" has been unloaded.",siVerboseMsg);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_xfspring_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"fr",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"fc",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"speed",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.25,0,100,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"damping",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.01,0,1,0,.1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"scale",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1000,0,2);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",2,0,1000,0,2);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_xfspring_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
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
   oLayout.AddEnumControl(L"mode",modeItems,L"Mode");
   oLayout.AddItem(L"speed",L"Speed");
   oLayout.AddItem(L"damping",L"Damping");
   oLayout.AddItem(L"scale",L"Scale");
   return CStatus::OK;
}

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

XSIPLUGINCALLBACK CStatus sixcpp_xfspring_op_Update( CRef& in_ctxt )
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

XSIPLUGINCALLBACK CStatus sixcpp_rotspring_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"fr",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"fc",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"speed",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.25,0,100,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"damping",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.01,0,1,0,.1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"clamp_min",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"clamp_max",CValue::siDouble,siPersistable | siAnimatable,L"",L"",10,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"x_pos",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_rotspring_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddItem(L"speed",L"Speed");
   oLayout.AddItem(L"damping",L"Damping");
   oLayout.AddItem(L"clamp_min",L"Clamp Min");
   oLayout.AddItem(L"clamp_max",L"Clamp Max");
   oLayout.AddItem(L"x_pos",L"Position X");
   return CStatus::OK;
}

class sixRotSpringUserData
{
public:
   CVector3 pos;
   CVector3 vel;
};

XSIPLUGINCALLBACK CStatus sixcpp_rotspring_op_Update( CRef& in_ctxt )
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

XSIPLUGINCALLBACK CStatus sixcpp_ik2bone_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",2,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"invert",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"boneA",CValue::siDouble,siPersistable | siAnimatable,L"",L"",3,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"boneB",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"stretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"softness",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_ik2bone_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddItem(L"invert",L"Invert");
   CValueArray modeItems(10);
   modeItems[0] = L"Bone A";
   modeItems[1] = (LONG)0l;
   modeItems[2] = L"Bone B";
   modeItems[3] = (LONG)1l;
   modeItems[4] = L"Center";
   modeItems[5] = (LONG)2l;
   modeItems[6] = L"Center Normalized";
   modeItems[7] = (LONG)3l;
   modeItems[8] = L"Effector";
   modeItems[9] = (LONG)4l;
   oLayout.AddEnumControl(L"mode",modeItems,L"Mode");
   oLayout.AddItem(L"boneA",L"Bone A");
   oLayout.AddItem(L"boneB",L"Bone B");
   oLayout.AddItem(L"stretch",L"Stretch");
   oLayout.AddItem(L"softness",L"Softness");
   return CStatus::OK;
}

struct s_sixcpp_GetIKTransform
{
   long mode;
   bool invert;
   double bone_a;
   double bone_b;
   double stretch;
   double softness;
   CTransformation root;
   CTransformation eff;
   CTransformation upv;
};

CTransformation sixcpp_GetIKTransform(s_sixcpp_GetIKTransform values)
{
   // prepare all variables
   CTransformation result;
   CVector3 bonePos,rootPos,effPos,upvPos,rootEff, xAxis,yAxis,zAxis;
   rootPos = values.root.GetTranslation();
   effPos = values.eff.GetTranslation();
   upvPos = values.upv.GetTranslation();
   rootEff.Sub(effPos,rootPos);
   double rootEffDistance = rootEff.GetLength();
   double softness = values.softness * values.root.GetSclX();

   // init the scaling
   result.SetScaling(values.root.GetScaling());

   // calculate the stretch!
   double stretchRatio = 1.0;
   {
      double da = (values.bone_a + values.bone_b) - softness;
      if(rootEffDistance > da)
      {
         double shortd = softness * (1.0 - exp(-(rootEffDistance - da) / softness)) + da;
         stretchRatio = rootEffDistance / shortd;
      }
      stretchRatio = 1.0 + (stretchRatio - 1.0) * values.stretch;
   }
   values.bone_a *= stretchRatio;
   values.bone_b *= stretchRatio;

   // calculate the angle inside the triangle!
   double angleA = 0;
   double angleB = 0;

   if(rootEffDistance < values.bone_a + values.bone_b)
   {
      // use the law of cosine for bone_a
      double a = values.bone_a;
      double b = rootEffDistance;
      double c = values.bone_b;
      angleA = acos((a * a + b * b - c * c ) / ( 2 * a * b));

      // use the law of cosine for bone_b
      a = values.bone_b;
      b = values.bone_a;
      c = rootEffDistance;
      angleB = acos((a * a + b * b - c * c ) / ( 2 * a * b));

      // invert the angles if need be
      if(values.invert)
      {
         angleA = -angleA;
         angleB = -angleB;
      }
   }

   // start with the X and Z axis
   xAxis = rootEff;
   yAxis.LinearlyInterpolate(rootPos,effPos,.5);
   yAxis.Sub(upvPos,yAxis);
   zAxis.Cross(xAxis,yAxis);
   xAxis.NormalizeInPlace();
   zAxis.NormalizeInPlace();

   // switch depending on our mode
   switch(values.mode)
   {
      case 0:  // bone_a
      {
         // check if we need to rotate the bone
         if(angleA != 0.0)
         {
            CRotation rot;
            rot.SetFromAxisAngle(zAxis,angleA);
            xAxis.MulByMatrix3InPlace(rot.GetMatrix());
         }

         // cross the yAxis and normalize
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // output the rotation
         result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

         // set the scaling + the position
         result.SetSclX(values.bone_a);
         result.SetTranslation(rootPos);
         break;
      }
      case 1:  // bone_a
      {
         // check if we need to rotate the bone
         if(angleA != 0.0)
         {
            CRotation rot;
            rot.SetFromAxisAngle(zAxis,angleA);
            xAxis.MulByMatrix3InPlace(rot.GetMatrix());
         }

         // calculate the position of the elbow!
         bonePos.Scale(values.bone_a,xAxis);
         bonePos.AddInPlace(rootPos);

         // check if we need to rotate the bone
         if(angleB != 0.0)
         {
            CRotation rot;
            rot.SetFromAxisAngle(zAxis,angleB-XSI::MATH::PI);
            xAxis.MulByMatrix3InPlace(rot.GetMatrix());
         }

         // cross the yAxis and normalize
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // output the rotation
         result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

         // set the scaling + the position
         result.SetSclX(values.bone_b);

         result.SetTranslation(bonePos);
         break;
      }
      case 2:  // center
      {
         // check if we need to rotate the bone
         bonePos.Scale(values.bone_a,xAxis);
         if(angleA != 0.0)
         {
            CRotation rot;
            rot.SetFromAxisAngle(zAxis,angleA);
            bonePos.MulByMatrix3InPlace(rot.GetMatrix());
         }
         bonePos.AddInPlace(rootPos);

         // cross the yAxis and normalize
         yAxis.Sub(upvPos,bonePos);
         zAxis.Cross(xAxis,yAxis);
         zAxis.NormalizeInPlace();
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // output the rotation
         result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

         // set the scaling + the position
         result.SetSclX(stretchRatio * values.root.GetSclX());

         result.SetTranslation(bonePos);
         break;
      }
      case 3:  // center normalized
      {
         // check if we need to rotate the bone
         if(angleA != 0.0)
         {
            CRotation rot;
            rot.SetFromAxisAngle(zAxis,angleA);
            xAxis.MulByMatrix3InPlace(rot.GetMatrix());
         }

         // calculate the position of the elbow!
         bonePos.Scale(values.bone_a,xAxis);
         bonePos.AddInPlace(rootPos);

         // check if we need to rotate the bone
         if(angleB != 0.0)
         {
            if(values.invert)
               angleB += XSI::MATH::PI * 2;
            CRotation rot;
            rot.SetFromAxisAngle(zAxis,angleB*.5-XSI::MATH::PI*.5);
            xAxis.MulByMatrix3InPlace(rot.GetMatrix());
         }

         // cross the yAxis and normalize
         yAxis.Sub(upvPos,bonePos);
         zAxis.Cross(xAxis,yAxis);
         zAxis.NormalizeInPlace();
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // output the rotation
         result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

         // set the scaling + the position
         result.SetSclX(stretchRatio * values.root.GetSclX());

         result.SetTranslation(bonePos);
         break;
      }
      case 4:  // effector
      {
         // check if we need to rotate the bone
         effPos = rootPos;
         if(angleA != 0.0)
         {
            CRotation rot;
            rot.SetFromAxisAngle(zAxis,angleA);
            xAxis.MulByMatrix3InPlace(rot.GetMatrix());
         }

         // calculate the position of the elbow!
         bonePos.Scale(values.bone_a,xAxis);
         effPos.AddInPlace(bonePos);

         // check if we need to rotate the bone
         if(angleB != 0.0)
         {
            CRotation rot;
            rot.SetFromAxisAngle(zAxis,angleB-XSI::MATH::PI);
            xAxis.MulByMatrix3InPlace(rot.GetMatrix());
         }

         // calculate the position of the effector!
         bonePos.Scale(values.bone_b,xAxis);
         effPos.AddInPlace(bonePos);

         // cross the yAxis and normalize
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // output the rotation
         result = values.eff;
         result.SetTranslation(effPos);
         break;
      }
   }

   return result;
}

XSIPLUGINCALLBACK CStatus sixcpp_ik2bone_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   //KinematicState parentKine = ctxt.GetInputValue(0);
   KinematicState rootKine = (CRef)ctxt.GetInputValue(0);
   KinematicState effKine = (CRef)ctxt.GetInputValue(1);
   KinematicState upvKine = (CRef)ctxt.GetInputValue(2);

   // create the struct
   s_sixcpp_GetIKTransform params;
   params.root = rootKine.GetTransform();
   params.eff = effKine.GetTransform();
   params.upv = upvKine.GetTransform();

   // get the parameters
   params.mode = (LONG)ctxt.GetParameterValue(L"mode");
   params.invert = ctxt.GetParameterValue(L"invert");
   params.bone_a = ctxt.GetParameterValue(L"boneA");
   params.bone_b = ctxt.GetParameterValue(L"boneB");
   params.stretch = ctxt.GetParameterValue(L"stretch");
   params.softness = ctxt.GetParameterValue(L"softness");

   // calculate the transform
   CTransformation ikXF = sixcpp_GetIKTransform(params);

   KinematicState outKine(ctxt.GetOutputTarget());
   //ikXF = MapWorldPoseToObjectSpace(parentKine.GetTransform(),ikXF);
   outKine.PutTransform(ikXF);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_ikfk2bone_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",2,-100000,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"invert",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"boneA",CValue::siDouble,siPersistable | siAnimatable,L"",L"",3,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"boneB",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"stretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"softness",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,100000,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_ikfk2bone_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddItem(L"blend",L"IK / FK");
   oLayout.AddItem(L"invert",L"Invert");
   CValueArray modeItems(10);
   modeItems[0] = L"Bone A";
   modeItems[1] = (LONG)0l;
   modeItems[2] = L"Bone B";
   modeItems[3] = (LONG)1l;
   modeItems[4] = L"Center";
   modeItems[5] = (LONG)2l;
   modeItems[6] = L"Center Normalized";
   modeItems[7] = (LONG)3l;
   modeItems[8] = L"Effector";
   modeItems[9] = (LONG)4l;
   oLayout.AddEnumControl(L"mode",modeItems,L"Mode");
   oLayout.AddItem(L"boneA",L"Bone A");
   oLayout.AddItem(L"boneB",L"Bone B");
   oLayout.AddItem(L"stretch",L"Stretch");
   oLayout.AddItem(L"softness",L"Softness");
   return CStatus::OK;
}

struct s_sixcpp_GetFKTransform
{
   long mode;
   double bone_a;
   double bone_b;
   CTransformation root;
   CTransformation bone1;
   CTransformation bone2;
   CTransformation eff;
};

CTransformation sixcpp_GetFKTransform(s_sixcpp_GetFKTransform values)
{
   // prepare all variables
   CTransformation result;
   CVector3 xAxis,yAxis,zAxis,temp;

   switch(values.mode)
   {
      case 0:  // bone_a
      {
         result = values.bone1;
         xAxis.Sub(values.bone2.GetTranslation(),values.bone1.GetTranslation());
         result.SetSclX(xAxis.GetLength());

         // cross the yAxis and normalize
         xAxis.NormalizeInPlace();
         yAxis.Set(0,1,0);
         yAxis.MulByMatrix3InPlace(values.bone1.GetRotationMatrix3());
         zAxis.Cross(xAxis,yAxis);
         zAxis.NormalizeInPlace();
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // rotation
         result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
         break;
      }
      case 1:  // bone_a
      {
         result = values.bone2;
         xAxis.Sub(values.eff.GetTranslation(),values.bone2.GetTranslation());
         result.SetSclX(xAxis.GetLength());

         // cross the yAxis and normalize
         xAxis.NormalizeInPlace();
         yAxis.Set(0,1,0);
         yAxis.MulByMatrix3InPlace(values.bone2.GetRotationMatrix3());
         zAxis.Cross(xAxis,yAxis);
         zAxis.NormalizeInPlace();
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // rotation
         result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
         break;
      }
      case 2:  // center
      {
         result = values.bone2;
         result.SetSclX(values.root.GetSclX() * values.bone2.GetSclX() / values.bone_b );
         xAxis.Sub(values.eff.GetTranslation(),values.bone1.GetTranslation());

         // cross the yAxis and normalize
         xAxis.NormalizeInPlace();
         temp.Set(1,0,0);
         yAxis.MulByMatrix3(temp,values.bone1.GetRotationMatrix3());
         temp.MulByMatrix3(CVector3(-1,0,0),values.bone2.GetRotationMatrix3());
         yAxis.AddInPlace(temp);
         if(yAxis.GetLength() <= 0.001)
            yAxis.MulByMatrix3(CVector3(0,1,0),values.bone2.GetRotationMatrix3());
         zAxis.Cross(xAxis,yAxis);
         zAxis.NormalizeInPlace();
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // rotation
         result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
         break;
      }
      case 3:  // center normalized
      {
         result = values.bone2;
         result.SetSclX(values.root.GetSclX() * values.bone2.GetSclX() / values.bone_b );
         xAxis.Sub(values.bone1.GetTranslation(),values.bone2.GetTranslation());
         temp.Sub(values.eff.GetTranslation(),values.bone2.GetTranslation());
         xAxis.NormalizeInPlace();
         temp.NormalizeInPlace();
         xAxis.Sub(temp,xAxis);
         temp.NormalizeInPlace();

         // cross the yAxis and normalize
         xAxis.NormalizeInPlace();
         temp.Set(1,0,0);
         yAxis.MulByMatrix3(temp,values.bone1.GetRotationMatrix3());
         temp.MulByMatrix3(CVector3(-1,0,0),values.bone2.GetRotationMatrix3());
         yAxis.AddInPlace(temp);
         if(yAxis.GetLength() <= 0.001)
            yAxis.MulByMatrix3(CVector3(0,1,0),values.bone2.GetRotationMatrix3());
         zAxis.Cross(xAxis,yAxis);
         zAxis.NormalizeInPlace();
         yAxis.Cross(zAxis,xAxis);
         yAxis.NormalizeInPlace();

         // rotation
         result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
         break;
      }
      case 4:  // effector
      {
         result = values.eff;
         break;
      }
   }

   return result;
}

CTransformation InterpolateTransform(CTransformation xf1, CTransformation xf2, double blend)
{
   if(blend == 1.0)
      return xf2;
   else if(blend == 0.0)
      return xf1;

   CTransformation result;
   CVector3 resultPos,resultScl;
   CQuaternion resultQuat;
   resultPos.LinearlyInterpolate(xf1.GetTranslation(),xf2.GetTranslation(),blend);
   resultScl.LinearlyInterpolate(xf1.GetScaling(),xf2.GetScaling(),blend);
   resultQuat.Slerp(xf1.GetRotationQuaternion(),xf2.GetRotationQuaternion(),blend);
   result.SetScaling(resultScl);
   result.SetRotationFromQuaternion(resultQuat);
   result.SetTranslation(resultPos);
   return result;
}

XSIPLUGINCALLBACK CStatus sixcpp_ikfk2bone_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   //KinematicState parentKine = ctxt.GetInputValue(0);
   KinematicState ikrootKine = (CRef)ctxt.GetInputValue(0);
   KinematicState ikeffKine = (CRef)ctxt.GetInputValue(1);
   KinematicState ikupvKine = (CRef)ctxt.GetInputValue(2);
   KinematicState fkbone1Kine = (CRef)ctxt.GetInputValue(3);
   KinematicState fkbone2Kine = (CRef)ctxt.GetInputValue(4);
   KinematicState fkeffKine = (CRef)ctxt.GetInputValue(5);

   double blend = ctxt.GetParameterValue(L"blend");
   long mode = (LONG)ctxt.GetParameterValue(L"mode");

   // setup the base IK parameters
   s_sixcpp_GetIKTransform ikparams;
   ikparams.root = ikrootKine.GetTransform();
   ikparams.eff = ikeffKine.GetTransform();
   ikparams.upv = ikupvKine.GetTransform();
   ikparams.mode = mode;
   ikparams.invert = ctxt.GetParameterValue(L"invert");
   ikparams.bone_a = ctxt.GetParameterValue(L"boneA");
   ikparams.bone_b = ctxt.GetParameterValue(L"boneB");
   ikparams.stretch = ctxt.GetParameterValue(L"stretch");
   ikparams.softness = ctxt.GetParameterValue(L"softness");

   // setup the base FK parameters
   s_sixcpp_GetFKTransform fkparams;
   fkparams.root = ikparams.root;
   fkparams.bone1 = fkbone1Kine.GetTransform();
   fkparams.bone2 = fkbone2Kine.GetTransform();
   fkparams.eff = fkeffKine.GetTransform();
   fkparams.mode = mode;
   fkparams.bone_a = ikparams.bone_a;
   fkparams.bone_b = ikparams.bone_b;

   // for optimization
   CTransformation result;
   if(blend == 0.0)
      result = sixcpp_GetIKTransform(ikparams);
   else if(blend == 1.0)
      result = sixcpp_GetFKTransform(fkparams);
   else
   {
      // here is where the blending happens!
      ikparams.mode = 0;
      CTransformation ikbone1 = sixcpp_GetIKTransform(ikparams);
      ikparams.mode = 1;
      CTransformation ikbone2 = sixcpp_GetIKTransform(ikparams);
      ikparams.mode = 4;
      CTransformation ikeff = sixcpp_GetIKTransform(ikparams);
      CTransformation fkbone1 = fkparams.bone1;
      CTransformation fkbone2 = fkparams.bone2;
      CTransformation fkeff = fkparams.eff;

      // map the secondary transforms from global to local
      ikeff = MapWorldPoseToObjectSpace(ikbone2,ikeff);
      fkeff = MapWorldPoseToObjectSpace(fkbone2,fkeff);
      ikbone2 = MapWorldPoseToObjectSpace(ikbone1,ikbone2);
      fkbone2 = MapWorldPoseToObjectSpace(fkbone1,fkbone2);

      // now blend them!
      fkparams.bone1 = InterpolateTransform(ikbone1,fkbone1,blend);
      fkparams.bone2 = InterpolateTransform(ikbone2,fkbone2,blend);
      fkparams.eff = InterpolateTransform(ikeff,fkeff,blend);

      // now map the local transform back to global!
      fkparams.bone2 = MapObjectPoseToWorldSpace(fkparams.bone1,fkparams.bone2);
      fkparams.eff = MapObjectPoseToWorldSpace(fkparams.bone2,fkparams.eff);

      // calculate the result based on that
      result = sixcpp_GetFKTransform(fkparams);
   }

   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(result);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_splinekine_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"count",CValue::siInt4,siPersistable | siAnimatable,L"",L"",2,2,100000,2,3);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"resample",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"subdiv",CValue::siInt4,siPersistable | siAnimatable,L"",L"",10,3,100000,3,24);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"absolute",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_splinekine_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddItem(L"u",L"U Value");
   oLayout.AddGroup(L"Resampling");
   oLayout.AddItem(L"resample",L"Enable");
   oLayout.AddItem(L"subdiv",L"Subdivision");
   oLayout.AddItem(L"absolute",L"Absolute");
   oLayout.EndGroup();
   return CStatus::OK;
}

CVector3Array bezier4point(CVector3 a, CVector3 tan_a, CVector3 d, CVector3 tan_d, double u)
{
   CVector3 b,c,ab,bc,cd,abbc,bccd,abbcbccd;
   b.Add(a,tan_a);
   c.Negate(tan_d);
   c.AddInPlace(d);

   // interpolate!
   ab.LinearlyInterpolate(a,b,u);
   bc.LinearlyInterpolate(b,c,u);
   cd.LinearlyInterpolate(c,d,u);
   abbc.LinearlyInterpolate(ab,bc,u);
   bccd.LinearlyInterpolate(bc,cd,u);
   abbcbccd.LinearlyInterpolate(abbc,bccd,u);

   CVector3Array results(2);
   results[0] = abbcbccd;
   results[1].Sub(bccd,abbc);
   return results;
}

CStatus splinekine_op_Update( CRef& in_ctxt, int mode = 0 )
{
   OperatorContext ctxt( in_ctxt );
   long count = (LONG)ctxt.GetParameterValue(L"count");
   CVector3Array pos(count);
   CVector3Array tangent(count);
   CVector3Array rot(count);
   CDoubleArray roll(count);
   CVector3Array rotParent(count);
   CVector3Array scl(count);
   CTransformation singleXF,singleParentXF;
   CMatrix3 singleMat;
   CTransformation modelXF;

   if(mode == 0) // simple 180 flipping interpolation
   {
      for(long i=0;i<count;i++)
      {
         singleXF = KinematicState(ctxt.GetInputValue(i)).GetTransform();
         singleMat = singleXF.GetRotationMatrix3();
         pos[i] = singleXF.GetTranslation();
         tangent[i].MulByMatrix3(CVector3(singleXF.GetSclX()*2.5,0,0),singleMat);
         rot[i] = singleXF.GetRotationXYZAngles();
         scl[i] = singleXF.GetScaling();
      }
      modelXF = KinematicState(ctxt.GetInputValue(count)).GetTransform();
   }
   else if(mode == 1) // local rotation X based roll
   {
      for(long i=0;i<count;i++)
      {
         singleParentXF = KinematicState(ctxt.GetInputValue(i*2+0)).GetTransform();
         singleXF = KinematicState(ctxt.GetInputValue(i*2+1)).GetTransform();
         roll[i] = singleXF.GetRotX();

         singleXF = MapObjectPoseToWorldSpace(singleParentXF,singleXF);
         singleMat = singleXF.GetRotationMatrix3();

         pos[i] = singleXF.GetTranslation();
         tangent[i].MulByMatrix3(CVector3(singleXF.GetSclX()*2.5,0,0),singleMat);
         rot[i] = singleParentXF.GetRotationXYZAngles();
         scl[i] = singleXF.GetScaling();
      }
      modelXF = KinematicState(ctxt.GetInputValue(count*2)).GetTransform();
   }
   double u = ctxt.GetParameterValue(L"u");
   bool resample = ctxt.GetParameterValue(L"resample");
   long subdiv = (LONG)ctxt.GetParameterValue(L"subdiv");
   bool absolute = ctxt.GetParameterValue(L"absolute");

   double step = 1.0 / max(1,count-1);
   int index1 = (int)min(count-2,u / step);
   int index2 = index1+1;
   int index1temp = index1;
   int index2temp = index2;
   double v = (u - step * double(index1)) / step;
   double vtemp = v;

   // calculate the bezier
   CVector3 bezierPos;
   CVector3 xAxis,yAxis,zAxis;
   if(!resample)
   {
      // straight bezier solve
      CVector3Array results = bezier4point(pos[index1],tangent[index1],pos[index2],tangent[index2],v);
      bezierPos = results[0];
      xAxis = results[1];
   }
   else if(!absolute)
   {
      CVector3Array presample(subdiv);
      CVector3Array presampletan(subdiv);
      CDoubleArray samplelen(subdiv);
      double samplestep = 1.0 / double(subdiv-1);
      double sampleu = samplestep;
      presample[0]  = pos[index1];
      presampletan[0]  = tangent[index1];
      CVector3 prevsample(presample[0]);
      CVector3 diff;
      samplelen[0] = 0;
      double overalllen = 0;
      CVector3Array results(2);
      for(long i=1;i<subdiv;i++,sampleu+=samplestep)
      {
         results = bezier4point(pos[index1],tangent[index1],pos[index2],tangent[index2],sampleu);
         presample[i] = results[0];
         presampletan[i] = results[1];
         diff.Sub(presample[i],prevsample);
         overalllen += diff.GetLength();
         samplelen[i] = overalllen;
         prevsample = presample[i];
      }
      // now as we have the
      sampleu = 0;
      for(long i=0;i<subdiv-1;i++,sampleu+=samplestep)
      {
         samplelen[i+1] = samplelen[i+1] / overalllen;
         if(v>=samplelen[i] && v <=  samplelen[i+1])
         {
            v = (v - samplelen[i]) / (samplelen[i+1] - samplelen[i]);
            bezierPos.LinearlyInterpolate(presample[i],presample[i+1],v);
            xAxis.LinearlyInterpolate(presampletan[i],presampletan[i+1],v);
            break;
         }
      }
   }
   else
   {
      CVector3Array presample(subdiv);
      CVector3Array presampletan(subdiv);
      CDoubleArray samplelen(subdiv);
      double samplestep = 1.0 / double(subdiv-1);
      double sampleu = samplestep;
      presample[0]  = pos[0];
      presampletan[0]  = tangent[0];
      CVector3 prevsample(presample[0]);
      CVector3 diff;
      samplelen[0] = 0;
      double overalllen = 0;
      CVector3Array results;
      for(long i=1;i<subdiv;i++,sampleu+=samplestep)
      {
         index1 = (int)min(count-2,sampleu / step);
         index2 = index1+1;
         v = (sampleu - step * double(index1)) / step;
         results = bezier4point(pos[index1],tangent[index1],pos[index2],tangent[index2],v);
         presample[i] = results[0];
         presampletan[i] = results[1];
         diff.Sub(presample[i],prevsample);
         overalllen += diff.GetLength();
         samplelen[i] = overalllen;
         prevsample = presample[i];
      }
      // now as we have the
      sampleu = 0;
      for(long i=0;i<subdiv-1;i++,sampleu+=samplestep)
      {
         samplelen[i+1] = samplelen[i+1] / overalllen;
         if(u>=samplelen[i] && u <= samplelen[i+1])
         {
            u = (u - samplelen[i]) / (samplelen[i+1] - samplelen[i]);
            bezierPos.LinearlyInterpolate(presample[i],presample[i+1],u);
            xAxis.LinearlyInterpolate(presampletan[i],presampletan[i+1],u);
            break;
         }
      }
   }

   // compute the scaling (straight interpolation!)
   CVector3 scl1;
   scl1.LinearlyInterpolate(scl[index1temp],scl[index2temp],vtemp);
   scl1.PutX(modelXF.GetSclX());

   // compute the rotation!
   CRotation rot1,rot2;
   rot1.SetFromXYZAngles(rot[index1temp]);
   rot2.SetFromXYZAngles(rot[index2temp]);
   CQuaternion quat;
   quat.Slerp(rot1.GetQuaternion(),rot2.GetQuaternion(),vtemp);
   rot1.SetFromQuaternion(quat);
   yAxis.Set(0,1,0);
   yAxis.MulByMatrix3InPlace(rot1.GetMatrix());

   // use directly or project the roll values!
   if(mode==1)
   {
      double thisRoll = roll[index1temp] * (1.0 - vtemp) + roll[index2temp] * vtemp;
      rot1.SetFromAxisAngle(xAxis,DegreesToRadians(thisRoll));
      yAxis.MulByMatrix3InPlace(rot1.GetMatrix());
   }

   zAxis.Cross(xAxis,yAxis);
   yAxis.Cross(zAxis,xAxis);
   xAxis.NormalizeInPlace();
   yAxis.NormalizeInPlace();
   zAxis.NormalizeInPlace();

   CTransformation result;
   result.SetScaling(scl1);
   result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
   result.SetTranslation(bezierPos);
   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(result);

   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_splinekine_op_Update( CRef& in_ctxt )
{
   return splinekine_op_Update(in_ctxt,0);
}

XSIPLUGINCALLBACK CStatus sixcpp_rollsplinekine_op_Define( CRef& in_ctxt )
{
   return sixcpp_splinekine_op_Define( in_ctxt );
}

XSIPLUGINCALLBACK CStatus sixcpp_rollsplinekine_op_DefineLayout( CRef& in_ctxt )
{
   return sixcpp_splinekine_op_DefineLayout(in_ctxt);
}

XSIPLUGINCALLBACK CStatus sixcpp_rollsplinekine_op_Update( CRef& in_ctxt )
{
   return splinekine_op_Update(in_ctxt,1);
}

XSIPLUGINCALLBACK CStatus sixcpp_ik2bone_prop_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomProperty oCustomProperty;
   Parameter oParam;
   oCustomProperty = ctxt.GetSource();
   oCustomProperty.AddParameter(L"invert",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1,oParam);
   oCustomProperty.AddParameter(L"boneA",CValue::siDouble,siPersistable | siAnimatable,L"",L"",3,0,100000,0,10,oParam);
   oCustomProperty.AddParameter(L"boneB",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,0,100000,0,10,oParam);
   oCustomProperty.AddParameter(L"stretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0,100000,0,1,oParam);
   oCustomProperty.AddParameter(L"softness",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,100000,0,1,oParam);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_ik2bone_prop_DefineLayout( CRef& in_ctxt )
{
   return sixcpp_ik2bone_op_DefineLayout(in_ctxt);
}

XSIPLUGINCALLBACK CStatus sixcpp_ikfk2bone_prop_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomProperty oCustomProperty;
   Parameter oParam;
   oCustomProperty = ctxt.GetSource();
   oCustomProperty.AddParameter(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1,oParam);
   oCustomProperty.AddParameter(L"invert",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1,oParam);
   oCustomProperty.AddParameter(L"boneA",CValue::siDouble,siPersistable | siAnimatable,L"",L"",3,0,100000,0,10,oParam);
   oCustomProperty.AddParameter(L"boneB",CValue::siDouble,siPersistable | siAnimatable,L"",L"",5,0,100000,0,10,oParam);
   oCustomProperty.AddParameter(L"stretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0,100000,0,1,oParam);
   oCustomProperty.AddParameter(L"softness",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,100000,0,1,oParam);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_ikfk2bone_prop_DefineLayout( CRef& in_ctxt )
{
   return sixcpp_ikfk2bone_op_DefineLayout(in_ctxt);
}

XSIPLUGINCALLBACK CStatus sixcpp_splinekine_prop_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomProperty oCustomProperty;
   Parameter oParam;
   oCustomProperty = ctxt.GetSource();
   oCustomProperty.AddParameter(L"resample",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1,oParam);
   oCustomProperty.AddParameter(L"subdiv",CValue::siInt4,siPersistable | siAnimatable,L"",L"",10,3,100000,3,24,oParam);
   oCustomProperty.AddParameter(L"absolute",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1,oParam);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_splinekine_prop_DefineLayout( CRef& in_ctxt )
{
   return sixcpp_splinekine_op_DefineLayout(in_ctxt);
}

XSIPLUGINCALLBACK CStatus sixcpp_interpose_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"blend_pos",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"blend_dir",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"blend_upv",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"blend_scl",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_interpose_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddItem(L"blend_pos",L"Blend Position");
   oLayout.AddItem(L"blend_dir",L"Blend Direction");
   oLayout.AddItem(L"blend_upv",L"Blend Upvector");
   oLayout.AddItem(L"blend_scl",L"Blend Scaling");
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_interpose_op_Update( CRef& in_ctxt )
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

XSIPLUGINCALLBACK CStatus sixcpp_squashstretch_op_Define( CRef& in_ctxt )
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

XSIPLUGINCALLBACK CStatus sixcpp_squashstretch_op_DefineLayout( CRef& in_ctxt )
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

XSIPLUGINCALLBACK CStatus sixcpp_squashstretch_op_Update( CRef& in_ctxt )
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

XSIPLUGINCALLBACK CStatus sixcpp_squashstretch_prop_Define( CRef& in_ctxt )
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

XSIPLUGINCALLBACK CStatus sixcpp_squashstretch_prop_DefineLayout( CRef& in_ctxt )
{
   return sixcpp_squashstretch_op_DefineLayout(in_ctxt);
}

XSIPLUGINCALLBACK CStatus sixcpp_iso4point_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"v",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"y_scaling",CValue::siBool,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_iso4point_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddItem(L"u",L"U Value");
   oLayout.AddItem(L"v",L"V Value");
   oLayout.AddItem(L"y_scaling",L"Y for Scaling");
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_iso4point_op_Update( CRef& in_ctxt )
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

XSIPLUGINCALLBACK CStatus sixcpp_null2curve_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"imin",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"imax",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"omin",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"omax",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"soft_blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"upv_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_null2curve_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddGroup("Input");
   oLayout.AddItem(L"blend",L"Blend to Slider");
   oLayout.AddItem(L"u",L"U Value");
   oLayout.AddItem(L"imin",L"Minimum");
   oLayout.AddItem(L"imax",L"Maximum");
   oLayout.EndGroup();
   oLayout.AddGroup("Output");
   oLayout.AddItem(L"omin",L"Minimum");
   oLayout.AddItem(L"omax",L"Maximum");
   oLayout.EndGroup();
   oLayout.AddGroup("Softness");
   oLayout.AddItem(L"soft_blend",L"Blend");
   oLayout.EndGroup();
   oLayout.AddGroup("Orientation");
   CValueArray modeItems(6);
   modeItems[0] = L"Use Driver Rot";
   modeItems[1] = (LONG)0l;
   modeItems[2] = L"Use Upvector Rot";
   modeItems[3] = (LONG)1l;
   modeItems[4] = L"Tangent+Upvector";
   modeItems[5] = (LONG)2l;
   oLayout.AddEnumControl(L"upv_mode",modeItems,L"Mode");
   oLayout.EndGroup();
   return CStatus::OK;
}

double smooth(double v)
{
   return sin(v * XSI::MATH::PI * .5);
}
double asmooth(double v)
{
   return asin(clamp((v - .5) * 2.0,-1,1)) / XSI::MATH::PI + .5;
}


XSIPLUGINCALLBACK CStatus sixcpp_null2curve_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   double blend = ctxt.GetParameterValue(L"blend");
   double u = ctxt.GetParameterValue(L"u");
   double imin = ctxt.GetParameterValue(L"imin");
   double imax = ctxt.GetParameterValue(L"imax");
   double omin = ctxt.GetParameterValue(L"omin");
   double omax = ctxt.GetParameterValue(L"omax");
   double soft_blend = ctxt.GetParameterValue(L"soft_blend");
   long upv_mode = (LONG)ctxt.GetParameterValue(L"upv_mode");
   u *= 100.0;
   imin *= 100.0;
   imax *= 100.0;
   omin *= 100.0;
   omax *= 100.0;
   double odiff = omax-omin;
   double idiff = imax-imin;

   KinematicState driverState = (CRef)ctxt.GetInputValue(0);
   KinematicState upvectorState = (CRef)ctxt.GetInputValue(1);
   CTransformation driverXF(driverState.GetTransform());
   CTransformation upvectorXF(upvectorState.GetTransform());
   Primitive curve1prim = (CRef)ctxt.GetInputValue(2);
   Primitive curve2prim = (CRef)ctxt.GetInputValue(3);
   NurbsCurveList curve1geo(curve1prim.GetGeometry());
   NurbsCurveList curve2geo(curve2prim.GetGeometry());

   // resulting values
   LONG curve_index;
   double curve_u;
   double curve_percentage;
   double curve_distance;
   CVector3 curve_pos;
   CVector3 curve_tan;
   CVector3 curve_nor;
   CVector3 curve_bin;

   // request the percentage
   CVector3 lookupPos(driverXF.GetTranslation());
   curve1geo.GetClosestCurvePosition(lookupPos,curve_index,curve_distance,curve_u,curve_pos);
   NurbsCurve curve1(curve1geo.GetCurves()[curve_index]);
   NurbsCurve curve2(curve2geo.GetCurves()[0]);
   curve1.GetPercentageFromU(curve_u,curve_percentage);

   // now we want to use the input clamping
   curve_percentage = 100.0 * clamp(curve_percentage - imin,0,idiff) / idiff;

   // here is where we smooth the percentage
   double smooth_percentage = curve_percentage * 0.01 - .5;
   smooth_percentage = smooth(smooth(smooth(smooth_percentage))) * 50.0 + 50.0;
   curve_percentage = soft_blend * smooth_percentage + (1.0 - soft_blend) * curve_percentage;

   // now blend the percentage with the slider one
   curve_percentage = u * blend + (1.0 - blend) * curve_percentage;

   // now let's remap in between min and max
   curve_percentage = omin + odiff * curve_percentage * 0.01;

   // panic check to use correct tangents
   if(curve_percentage >= 100.0)
      curve_percentage = 99.999;
   else if(curve_percentage < 0.0)
      curve_percentage = 0.0;

   // evaluate the curve values
   curve2.EvaluatePositionFromPercentage(curve_percentage,curve_pos,curve_tan,curve_nor,curve_bin);

   CTransformation result;
   // translation
   result.SetTranslation(curve_pos);
   // orientation
   switch(upv_mode)
   {
      case 0:
      {
         result.SetRotation(driverXF.GetRotation());
         break;
      }
      case 1:
      {
         result.SetRotation(upvectorXF.GetRotation());
         break;
      }
      case 2:
      {
         CVector3 upv_dir,z;
         upv_dir.Sub(upvectorXF.GetTranslation(),curve_pos);
         z.Cross(curve_tan,upv_dir);
         upv_dir.Cross(z,curve_tan);
         curve_tan.NormalizeInPlace();
         upv_dir.NormalizeInPlace();
         z.NormalizeInPlace();
         result.SetRotationFromXYZAxes(curve_tan,upv_dir,z);
         break;
      }
   }
   // scaling
   result.SetScaling(driverXF.GetScaling());

   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(result);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_null2surface_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"v",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"input_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"iu_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"iv_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"iu_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,10,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"iv_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,10,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"i0_minmax",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ix_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1000,1000,-2,2);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"iy_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1000,1000,-2,2);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ix_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",8,0,1000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"iy_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",8,0,1000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ix_invert",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"iy_invert",CValue::siBool,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"axis_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"i1_minmax",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ou_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ov_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ou_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,10,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ov_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,10,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"o_minmax",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"surf_index",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"upv_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"upv_offsetu",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-.5,.5);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"upv_offsetv",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-.5,.5);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"upv_debug_pos",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"scl_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,0,100000,0,10);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_null2surface_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddGroup("Override");
   oLayout.AddItem(L"blend",L"Blend to Sliders");
   oLayout.AddItem(L"u",L"U Value");
   oLayout.AddItem(L"v",L"V Value");
   oLayout.EndGroup();
   oLayout.AddGroup("Input");
   {
      CValueArray modeItems(4);
      modeItems[0] = L"Nurbs Based";
      modeItems[1] = (LONG)0l;
      modeItems[2] = L"Transform Based";
      modeItems[3] = (LONG)1l;
      oLayout.AddEnumControl(L"input_mode",modeItems,L"Mode");
   }
   oLayout.AddGroup("Nurbs Based");
   oLayout.AddItem(L"iu_center",L"U Center");
   oLayout.AddItem(L"iv_center",L"V Center");
   oLayout.AddItem(L"iu_variance",L"U Variance");
   oLayout.AddItem(L"iv_variance",L"V Variance");
   oLayout.AddItem(L"i0_minmax",L"Treat sliders as Min Max");
   oLayout.AddButton(L"setInputUV",L"Set from current Driver Pos");
   oLayout.EndGroup();
   oLayout.AddGroup("Transform Based");
   oLayout.AddItem(L"ix_center",L"Axis1 Center");
   oLayout.AddItem(L"iy_center",L"Axis2 Center");
   oLayout.AddItem(L"ix_variance",L"Axis1 Variance");
   oLayout.AddItem(L"iy_variance",L"Axis2 Variance");
   oLayout.AddItem(L"ix_invert",L"Axis1 Invert");
   oLayout.AddItem(L"iy_invert",L"Axis2 Invert");
   oLayout.AddItem(L"i1_minmax",L"Treat sliders as Min Max");
   {
      CValueArray modeItems(12);
      modeItems[0] = L"X / Y Plane";
      modeItems[1] = (LONG)0l;
      modeItems[2] = L"X / Z Plane";
      modeItems[3] = (LONG)1l;
      modeItems[4] = L"Y / Z Plane";
      modeItems[5] = (LONG)2l;
      modeItems[6] = L"Y / X Plane";
      modeItems[7] = (LONG)3l;
      modeItems[8] = L"Z / X Plane";
      modeItems[9] = (LONG)4l;
      modeItems[10] = L"Z / Y Plane";
      modeItems[11] = (LONG)5l;
      oLayout.AddEnumControl(L"axis_mode",modeItems,L"Axes");
   }
   oLayout.AddButton(L"setInputXY",L"Set from current Driver Pos");
   oLayout.EndGroup();
   oLayout.EndGroup();
   oLayout.AddGroup("Output");
   oLayout.AddItem(L"ou_center",L"U Center");
   oLayout.AddItem(L"ov_center",L"V Center");
   oLayout.AddItem(L"ou_variance",L"U Variance");
   oLayout.AddItem(L"ov_variance",L"V Variance");
   oLayout.AddItem(L"o_minmax",L"Treat sliders as Min Max");
   oLayout.AddItem(L"surf_index",L"Surface Index");
   oLayout.AddButton(L"setOutputUV",L"Set from current Driver Pos");
   oLayout.EndGroup();
   oLayout.AddGroup("Orientation");
   {
      CValueArray modeItems(14);
      modeItems[0] = L"Use Driver Rot";
      modeItems[1] = (LONG)0l;
      modeItems[2] = L"Use Upvector Rot";
      modeItems[3] = (LONG)1l;
      modeItems[4] = L"Orient by Surface (U)";
      modeItems[5] = (LONG)2l;
      modeItems[6] = L"Orient by Surface (V)";
      modeItems[7] = (LONG)3l;
      modeItems[8] = L"Normal + Upvector";
      modeItems[9] = (LONG)4l;
      modeItems[10] = L"Normal + Driver Orientation";
      modeItems[11] = (LONG)5l;
      modeItems[12] = L"UV Offset (Sliders below)";
      modeItems[13] = (LONG)6l;
      oLayout.AddEnumControl(L"upv_mode",modeItems,L"Mode");
   }
   oLayout.AddItem(L"upv_offsetu",L"U Offset");
   oLayout.AddItem(L"upv_offsetv",L"V Offset");
   oLayout.AddItem(L"upv_debug_pos",L"Show Upv Pos (debug)");
   oLayout.EndGroup();
   oLayout.AddGroup("Scaling");
   {
      CValueArray modeItems(4);
      modeItems[0] = L"Use Driver Scl";
      modeItems[1] = (LONG)0l;
      modeItems[2] = L"Use Upvector Scl";
      modeItems[3] = (LONG)1l;
      oLayout.AddEnumControl(L"scl_mode",modeItems,L"Mode");
   }
   oLayout.EndGroup();
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_null2surface_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );

   // retrieve all of the fixed port values
   Primitive surface2prim = (CRef)ctxt.GetInputValue(3);
   NurbsSurfaceMesh surface2geo(surface2prim.GetGeometry());
   long surf_index = (LONG)ctxt.GetParameterValue(L"surf_index");
   NurbsSurface surface2(surface2geo.GetSurfaces()[surf_index]);

   // remember the transforms so we really only query once for performance
   CTransformation driverXF;
   CTransformation upvectorXF;
   bool isGlobalDriverXF = false;
   bool isGlobalUpvectorXF = false;

   // now first choose on the input mode
   long input_mode = (LONG)ctxt.GetParameterValue(L"input_mode");
   double surface_u = 0;
   double surface_v = 0;
   double surface_distance;
   CVector3 surface_pos;
   CVector3 surface_utan;
   CVector3 surface_vtan;
   CVector3 surface_normal;

   switch(input_mode)
   {
      case 0:  // nurbs based
      {
         KinematicState driverState = (CRef)ctxt.GetInputValue(0);
         driverXF = driverState.GetTransform();
         isGlobalDriverXF = true;
         Primitive surface1prim = (CRef)ctxt.GetInputValue(2);
         NurbsSurfaceMesh surface1geo(surface1prim.GetGeometry());

         double iu_center = ctxt.GetParameterValue(L"iu_center");
         double iv_center = ctxt.GetParameterValue(L"iv_center");
         double iu_variance = ctxt.GetParameterValue(L"iu_variance");
         double iv_variance = ctxt.GetParameterValue(L"iv_variance");

         bool i_minmax = ctxt.GetParameterValue(L"i0_minmax");
         double iminu = 0;
         double imaxu = 1;
         double iminv = 0;
         double imaxv = 1;
         if(i_minmax)
         {
            iminu = iu_center;
            iminv = iv_center;
            imaxu = iu_variance;
            imaxv = iv_variance;
         }
         else
         {
            iu_variance *= .5;
            iv_variance *= .5;
            iminu = iu_center - iu_variance;
            imaxu = iu_center + iu_variance;
            iminv = iv_center - iv_variance;
            imaxv = iv_center + iv_variance;
         }

         // resulting values
         LONG surface_index;
         double surface_un;
         double surface_vn;

         // request the percentage
         CVector3 lookupPos(driverXF.GetTranslation());
         surface1geo.GetClosestSurfacePosition(lookupPos,surface_index,surface_distance,surface_un,surface_vn,surface_pos);
         NurbsSurface surface1(surface1geo.GetSurfaces()[surface_index]);
         surface1.GetUVFromNormalizedUV(surface_un,surface_vn,surface_u,surface_v);

         // now we want to use the input clamping
         surface_u = clamp(surface_u - iminu,0,(imaxu - iminu)) / (imaxu - iminu);
         surface_v = clamp(surface_v - iminv,0,(imaxv - iminv)) / (imaxv - iminv);

         // now blend the percentage with the slider one
         double blend = ctxt.GetParameterValue(L"blend");
         if(blend > 0)
         {
            double u = ctxt.GetParameterValue(L"u");
            double v = ctxt.GetParameterValue(L"v");
            surface_u = u * blend + (1.0 - blend) * surface_u;
            surface_v = v * blend + (1.0 - blend) * surface_v;
         }

         break;
      }
      case 1:  // transform based
      {
         // here we want to calculate area in a given transform plane
         // get the local connected transform!
         KinematicState driverState = (CRef)ctxt.GetInputValue(4);
         driverXF = driverState.GetTransform();
         CVector3 driverPos(driverXF.GetTranslation());

         // first get parameters for this operation
         double iu_center = ctxt.GetParameterValue(L"ix_center");
         double iv_center = ctxt.GetParameterValue(L"iy_center");
         double iu_variance = ctxt.GetParameterValue(L"ix_variance");
         double iv_variance = ctxt.GetParameterValue(L"iy_variance");

         bool i_minmax = ctxt.GetParameterValue(L"i1_minmax");
         double iminu = 0;
         double imaxu = 1;
         double iminv = 0;
         double imaxv = 1;
         if(i_minmax)
         {
            iminu = iu_center;
            iminv = iv_center;
            imaxu = iu_variance;
            imaxv = iv_variance;
         }
         else
         {
            iu_variance *= .5;
            iv_variance *= .5;
            iminu = iu_center - iu_variance;
            imaxu = iu_center + iu_variance;
            iminv = iv_center - iv_variance;
            imaxv = iv_center + iv_variance;
         }

         bool iu_invert = ctxt.GetParameterValue(L"ix_invert");
         bool iv_invert = ctxt.GetParameterValue(L"iy_invert");

         // choose the right values based on the plane
         long axis_mode = (LONG)ctxt.GetParameterValue(L"axis_mode");
         switch(axis_mode)
         {
            case 0: // X Y plane
            {
               surface_u = driverPos.GetX();
               surface_v = driverPos.GetY();
               break;
            }
            case 1: // X Z plane
            {
               surface_u = driverPos.GetX();
               surface_v = driverPos.GetZ();
               break;
            }
            case 2: // Y Z plane
            {
               surface_u = driverPos.GetY();
               surface_v = driverPos.GetZ();
               break;
            }
            case 3: // Y X plane
            {
               surface_u = driverPos.GetY();
               surface_v = driverPos.GetX();
               break;
            }
            case 4: // Z X plane
            {
               surface_u = driverPos.GetZ();
               surface_v = driverPos.GetX();
               break;
            }
            case 5: // Z Y plane
            {
               surface_u = driverPos.GetZ();
               surface_v = driverPos.GetY();
               break;
            }
         }

         // clamp the input values
         surface_u = clamp(surface_u - iminu,0,(imaxu - iminu)) / (imaxu - iminu);
         surface_v = clamp(surface_v - iminv,0,(imaxv - iminv)) / (imaxv - iminv);
         if(iu_invert)
            surface_u = 1.0 - surface_u;
         if(iv_invert)
            surface_v = 1.0 - surface_v;

         break;
      }
   }

   // access the output relevant parameters
   double ou_center = ctxt.GetParameterValue(L"ou_center");
   double ov_center = ctxt.GetParameterValue(L"ov_center");
   double ou_variance = ctxt.GetParameterValue(L"ou_variance");
   double ov_variance = ctxt.GetParameterValue(L"ov_variance");

   bool o_minmax = ctxt.GetParameterValue(L"o_minmax");
   double ominu = 0;
   double omaxu = 1;
   double ominv = 0;
   double omaxv = 1;
   if(o_minmax)
   {
      ominu = ou_center;
      ominv = ov_center;
      omaxu = ou_variance;
      omaxv = ov_variance;
   }
   else
   {
      ou_variance *= .5;
      ov_variance *= .5;
      ominu = ou_center - ou_variance;
      omaxu = ou_center + ou_variance;
      ominv = ov_center - ov_variance;
      omaxv = ov_center + ov_variance;
   }

   long upv_mode = (LONG)ctxt.GetParameterValue(L"upv_mode");

   // now let's remap in between min and max of the output
   surface_u = ominu + (omaxu-ominu) * surface_u;
   surface_v = ominv + (omaxv-ominv) * surface_v;

   // panic check to use correct tangents
   if(surface_u >= 1.0)
      surface_u = 1.0;
   else if(surface_u < 0.0)
      surface_u = 0.0;
   if(surface_v >= 1.0)
      surface_v = 1.0;
   else if(surface_v < 0.0)
      surface_v = 0.0;

   // evaluate the surface values
   surface2.EvaluateNormalizedPosition(surface_u,surface_v,surface_pos,surface_utan,surface_vtan,surface_normal);

   CTransformation result;
   // translation
   result.SetTranslation(surface_pos);
   // orientation
   switch(upv_mode)
   {
      case 0:
      {
         if(!isGlobalDriverXF)
         {
            KinematicState driverState = (CRef)ctxt.GetInputValue(0);
            driverXF = driverState.GetTransform();
            isGlobalDriverXF = true;
         }
         result.SetRotation(driverXF.GetRotation());
         break;
      }
      case 1:
      {
         KinematicState upvectorState = (CRef)ctxt.GetInputValue(1);
         upvectorXF = upvectorState.GetTransform();
         isGlobalUpvectorXF = true;
         result.SetRotation(upvectorXF.GetRotation());
         break;
      }
      case 2:
      {
         CVector3 x,y,z;
         x = surface_utan;
         y = surface_normal;
         z.Cross(x,y);
         x.Cross(y,z);
         x.NormalizeInPlace();
         y.NormalizeInPlace();
         z.NormalizeInPlace();
         result.SetRotationFromXYZAxes(x,y,z);
         break;
      }
      case 3:
      {
         CVector3 x,y,z;
         x = surface_vtan;
         y = surface_normal;
         z.Cross(x,y);
         x.Cross(y,z);
         x.NormalizeInPlace();
         y.NormalizeInPlace();
         z.NormalizeInPlace();
         result.SetRotationFromXYZAxes(x,y,z);
         break;
      }
      case 4:
      {
         KinematicState upvectorState = (CRef)ctxt.GetInputValue(1);
         upvectorXF = upvectorState.GetTransform();
         isGlobalUpvectorXF = true;
         CVector3 x,y,z;
         x.Sub(upvectorXF.GetTranslation(),surface_pos);
         y = surface_normal;
         z.Cross(x,y);
         x.Cross(y,z);
         x.NormalizeInPlace();
         y.NormalizeInPlace();
         z.NormalizeInPlace();
         result.SetRotationFromXYZAxes(x,y,z);
         break;
      }
      case 5:
      {
         CVector3 x,y,z;
         x.MulByMatrix3(CVector3(1,0,0),driverXF.GetRotationMatrix3());
         y = surface_normal;
         z.Cross(x,y);
         x.Cross(y,z);
         x.NormalizeInPlace();
         y.NormalizeInPlace();
         z.NormalizeInPlace();
         result.SetRotationFromXYZAxes(x,y,z);
         break;
      }
      case 6:
      {
         double upv_offsetu = ctxt.GetParameterValue(L"upv_offsetu");
         double upv_offsetv = ctxt.GetParameterValue(L"upv_offsetv");
         bool upv_debug_pos = ctxt.GetParameterValue(L"upv_debug_pos");

         CVector3 surface_pos_upv,surface_utan_upv,surface_vtan_upv,surface_normal_upv;
         surface2.EvaluateNormalizedPosition(clamp(surface_u + upv_offsetu,0,1),clamp(surface_v + upv_offsetv,0,1),surface_pos_upv,surface_utan_upv,surface_vtan_upv,surface_normal_upv);
         CVector3 x,y,z;
         x.Sub(surface_pos_upv,surface_pos);
         y = surface_normal;
         z.Cross(x,y);
         x.Cross(y,z);
         x.NormalizeInPlace();
         y.NormalizeInPlace();
         z.NormalizeInPlace();
         result.SetRotationFromXYZAxes(x,y,z);
         if(upv_debug_pos)
            result.SetTranslation(surface_pos_upv);
         break;
      }
   }
   // scaling
   long scl_mode = (LONG)ctxt.GetParameterValue(L"scl_mode");
   switch(scl_mode)
   {
      case 0: // driver scaling
      {
         if(!isGlobalDriverXF)
         {
            KinematicState driverState = (CRef)ctxt.GetInputValue(0);
            driverXF = driverState.GetTransform();
            isGlobalDriverXF = true;
         }
         result.SetScaling(driverXF.GetScaling());
         break;
      }
      case 1: // upvector scaling
      {
         if(!isGlobalUpvectorXF)
         {
            KinematicState upvectorState = (CRef)ctxt.GetInputValue(1);
            upvectorXF = upvectorState.GetTransform();
            isGlobalUpvectorXF = true;
         }
         result.SetScaling(upvectorXF.GetScaling());
         break;
      }
   }
   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(result);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_null2surface_op_PPGEvent( const CRef& in_ctxt )
{
   PPGEventContext ctxt( in_ctxt ) ;
   PPGEventContext::PPGEvent eventID = ctxt.GetEventID() ;

   if ( eventID == PPGEventContext::siOnInit )
   {
      CRefArray props = ctxt.GetInspectedObjects();
      for (LONG i=0; i<props.GetCount( ); i++)
      {
         // we don't do anything, but I keep the code around
         CustomOperator prop( props[i] );
      }
   }
   else if ( eventID == PPGEventContext::siOnClosed )
   {
      CRefArray props = ctxt.GetInspectedObjects();
      for (LONG i=0; i<props.GetCount( ); i++)
      {
         // we don't do anything, but I keep the code around
         CustomOperator prop( props[i] );
      }
   }
   else if ( eventID == PPGEventContext::siButtonClicked )
   {
      CValue buttonPressed = ctxt.GetAttribute( L"Button" ) ;
      if(buttonPressed.GetAsText() == L"setInputUV")
      {
         CRefArray ops = ctxt.GetInspectedObjects();
         for (LONG i=0; i<ops.GetCount( ); i++)
         {
            CustomOperator op( ops[i] );
            CRef driverRef = InputPort(op.GetInputPorts()[0]).GetTarget();
            KinematicState driverState(driverRef);
            CVector3 driverPos = driverState.GetTransform().GetTranslation();
            CRef surfacePrimRef = InputPort(op.GetInputPorts()[2]).GetTarget();
            NurbsSurfaceMesh surfaceMesh(Primitive(surfacePrimRef).GetGeometry());

            LONG surface_index;
            double surface_u;
            double surface_v;
            double surface_un;
            double surface_vn;
            double surface_distance;
            CVector3 surface_pos;
            CVector3 surface_utan;
            CVector3 surface_vtan;
            CVector3 surface_normal;

            surfaceMesh.GetClosestSurfacePosition(driverPos,surface_index,surface_distance,surface_un,surface_vn,surface_pos);
            NurbsSurface surface(surfaceMesh.GetSurfaces()[surface_index]);
            surface.GetUVFromNormalizedUV(surface_un,surface_vn,surface_u,surface_v);

            op.PutParameterValue(L"iu_center",surface_u);
            op.PutParameterValue(L"iv_center",surface_v);
         }
      }
      else if(buttonPressed.GetAsText() == L"setInputXY")
      {
         CRefArray ops = ctxt.GetInspectedObjects();
         for (LONG i=0; i<ops.GetCount( ); i++)
         {
            CustomOperator op( ops[i] );
            CRef driverRef = InputPort(op.GetInputPorts()[4]).GetTarget();
            KinematicState driverState(driverRef);
            CVector3 driverPos = driverState.GetTransform().GetTranslation();

            // choose the right values based on the axis_mode
            long axis_mode = (LONG)op.GetParameterValue(L"axis_mode");
            double surface_u = 0;
            double surface_v = 0;
            switch(axis_mode)
            {
               case 0: // X Y plane
               {
                  surface_u = driverPos.GetX();
                  surface_v = driverPos.GetY();
                  break;
               }
               case 1: // X Z plane
               {
                  surface_u = driverPos.GetX();
                  surface_v = driverPos.GetZ();
                  break;
               }
               case 2: // Y Z plane
               {
                  surface_u = driverPos.GetY();
                  surface_v = driverPos.GetZ();
                  break;
               }
               case 3: // Y X plane
               {
                  surface_u = driverPos.GetY();
                  surface_v = driverPos.GetX();
                  break;
               }
               case 4: // Z X plane
               {
                  surface_u = driverPos.GetZ();
                  surface_v = driverPos.GetX();
                  break;
               }
               case 5: // Z Y plane
               {
                  surface_u = driverPos.GetZ();
                  surface_v = driverPos.GetY();
                  break;
               }
            }

            op.PutParameterValue(L"ix_center",surface_u);
            op.PutParameterValue(L"iy_center",surface_v);
         }
      }
      else if(buttonPressed.GetAsText() == L"setOutputUV")
      {
         CRefArray ops = ctxt.GetInspectedObjects();
         for (LONG i=0; i<ops.GetCount( ); i++)
         {
            CustomOperator op( ops[i] );
            CRef driverRef = InputPort(op.GetInputPorts()[0]).GetTarget();
            KinematicState driverState(driverRef);
            CVector3 driverPos = driverState.GetTransform().GetTranslation();
            CRef surfacePrimRef = InputPort(op.GetInputPorts()[2]).GetTarget();
            NurbsSurfaceMesh surfaceMesh(Primitive(surfacePrimRef).GetGeometry());

            LONG surface_index;
            double surface_u;
            double surface_v;
            double surface_un;
            double surface_vn;
            double surface_distance;
            CVector3 surface_pos;
            CVector3 surface_utan;
            CVector3 surface_vtan;
            CVector3 surface_normal;

            surfaceMesh.GetClosestSurfacePosition(driverPos,surface_index,surface_distance,surface_un,surface_vn,surface_pos);
            NurbsSurface surface(surfaceMesh.GetSurfaces()[surface_index]);
            surface.GetUVFromNormalizedUV(surface_un,surface_vn,surface_u,surface_v);

            op.PutParameterValue(L"ou_center",surface_u);
            op.PutParameterValue(L"ov_center",surface_v);
         }
      }
   }
   else if ( eventID == PPGEventContext::siTabChange )
   {
      CRefArray props = ctxt.GetInspectedObjects();
      for (LONG i=0; i<props.GetCount( ); i++)
      {
         // we don't do anything, but I keep the code around
         CustomOperator prop( props[i] );
      }
   }
   else if ( eventID == PPGEventContext::siParameterChange )
   {
      CRefArray props = ctxt.GetInspectedObjects();
      for (LONG i=0; i<props.GetCount( ); i++)
      {
         // we don't do anything, but I keep the code around
         CustomOperator prop( props[i] );
      }
   }

   return CStatus::OK ;
}

XSIPLUGINCALLBACK CStatus sixcpp_curveslide_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"length",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0.01,10000,1,24);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"factor",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,100,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_curveslide_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddItem(L"length",L"Length");
   oLayout.AddItem(L"factor",L"Strength");
   oLayout.AddItem(L"center",L"Center");
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_curveslide_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   double length = ctxt.GetParameterValue(L"length");
   double factor = ctxt.GetParameterValue(L"factor");
   double center = ctxt.GetParameterValue(L"center");

   Primitive curvePrim = (CRef)ctxt.GetInputValue(0);
   NurbsCurveList curveGeo(curvePrim.GetGeometry());
   NurbsCurve curve(curveGeo.GetCurves()[0]);
   double curr_length = 0;
   curveGeo.GetLength(curr_length);
   double ratio = 1.0 + (length / curr_length - 1.0) * factor;
   double shift = 100.0 * (1.0 - ratio) * center;

   CControlPointRefArray curvePnts(curveGeo.GetControlPoints());
   CVector3Array curvePos = curvePnts.GetPositionArray();

   LONG curve_index;
   double curve_u;
   double curve_per;
   double curve_dist;
   CVector3 curve_pos;
   CVector3 curve_tan;
   CVector3 curve_nor;
   CVector3 curve_bin;

   for(LONG i=0;i<curvePos.GetCount();i++)
   {
      curveGeo.GetClosestCurvePosition(curvePos[i],curve_index,curve_dist,curve_u,curve_pos);
      curve.GetPercentageFromU(curve_u,curve_per);
      curve_per = curve_per * ratio + shift;
      if(curve_per < 0.0)
         curve_per = 0.0;
      else if(curve_per > 100.0)
         curve_per = 100.0;
      curve.EvaluatePositionFromPercentage(curve_per,curve_pos,curve_tan,curve_nor,curve_bin);
      curvePos[i] = curve_pos;
   }

   Primitive outPrim(ctxt.GetOutputTarget());
   NurbsCurveList outGeo(outPrim.GetGeometry());
   outGeo.GetControlPoints().PutPositionArray(curvePos);

   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_mouthinterpose_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator oCustomOperator;
   Parameter oParam;
   CRef oPDef;
   Factory oFactory = Application().GetFactory();
   oCustomOperator = ctxt.GetSource();
   oPDef = oFactory.CreateParamDef(L"ref1posx",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-10000,10000,-10,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ref1posy",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-10000,10000,-10,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ref1posz",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-10000,10000,-10,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ref2posx",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-10000,10000,-10,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ref2posy",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-10000,10000,-10,10);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"ref2posz",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-10000,10000,-10,10);
   oCustomOperator.AddParameter(oPDef,oParam);

   oPDef = oFactory.CreateParamDef(L"keyl",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.2,-10,10,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"keym",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,-10,10,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"keyr",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.8,-10,10,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"comisura",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-1,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oPDef = oFactory.CreateParamDef(L"corners",CValue::siBool,siPersistable | siAnimatable | siReadOnly,L"",L"",0,0,1,0,1);
   oCustomOperator.AddParameter(oPDef,oParam);
   oPDef = oFactory.CreateParamDef(L"cornerweight",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-1,1);
   oCustomOperator.AddParameter(oPDef,oParam);

   oCustomOperator.PutAlwaysEvaluate(false);
   oCustomOperator.PutDebug(0);
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_mouthinterpose_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddGroup("Reference Positions");
      oLayout.AddGroup("Head Position");
         oLayout.AddItem(L"ref1posx",L"X");
         oLayout.AddItem(L"ref1posy",L"Y");
         oLayout.AddItem(L"ref1posz",L"Z");
      oLayout.EndGroup();
      oLayout.AddGroup("Jaw Position");
         oLayout.AddItem(L"ref2posx",L"X");
         oLayout.AddItem(L"ref2posy",L"Y");
         oLayout.AddItem(L"ref2posz",L"Z");
      oLayout.EndGroup();
   oLayout.EndGroup();
   oLayout.AddGroup("Weights");
      oLayout.AddItem(L"keyl",L"Comi Up");
      oLayout.AddItem(L"keym",L"Comi Mid");
      oLayout.AddItem(L"keyr",L"Comi Dw");
      oLayout.AddItem(L"comisura",L"Comi Driver");
   oLayout.EndGroup();
   oLayout.AddGroup("Corners");
      oLayout.AddItem(L"corners",L"Enable");
      oLayout.AddItem(L"cornerweight",L"Weight");
   oLayout.EndGroup();
   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_mouthinterpose_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );
   KinematicState headKine = (CRef)ctxt.GetInputValue(0);
   KinematicState jawKine = (CRef)ctxt.GetInputValue(1);

   CTransformation headXF = headKine.GetTransform();
   CTransformation jawXF = jawKine.GetTransform();

   CVector3 headRefPos,jawRefPos,refPos;
   headRefPos.PutX((double)ctxt.GetParameterValue(L"ref1posx"));
   headRefPos.PutY((double)ctxt.GetParameterValue(L"ref1posy"));
   headRefPos.PutZ((double)ctxt.GetParameterValue(L"ref1posz"));
   jawRefPos.PutX((double)ctxt.GetParameterValue(L"ref2posx"));
   jawRefPos.PutY((double)ctxt.GetParameterValue(L"ref2posy"));
   jawRefPos.PutZ((double)ctxt.GetParameterValue(L"ref2posz"));

   double keyl = ctxt.GetParameterValue(L"keyl");
   double keym = ctxt.GetParameterValue(L"keym");
   double keyr = ctxt.GetParameterValue(L"keyr");
   double comi = ctxt.GetParameterValue(L"comisura");
   double corner = ctxt.GetParameterValue(L"cornerweight");
   bool docorners = ctxt.GetParameterValue(L"corners");
   corner = .5 + corner * .5;
   double weight = .5;

   // calculate the comisura weight based on the driven key!
   if(comi<0)
   {
      comi = fabs(comi);
      weight = keyl * comi + keym * (1.0-comi);
   }
   else
   {
      weight = keyr * comi + keym * (1.0-comi);
   }

   // create the output transform
   CTransformation refXF;

   // interpolate the scaling
   CVector3 headScl = headXF.GetScaling();
   CVector3 jawScl = jawXF.GetScaling();
   CVector3 refScl;
   refScl.Sub(jawScl,headScl);
   refScl.ScaleInPlace(weight);
   refScl.AddInPlace(headScl);
   refXF.SetScaling(refScl);

   // interpolate the rotation (clamped to 0 1)
   CMatrix3 headMat = headXF.GetRotationMatrix3();
   CMatrix3 jawMat = jawXF.GetRotationMatrix3();
   CVector3 headYAxis,headZAxis,jawYAxis,jawZAxis,refXAxis,refYAxis,refZAxis;
   headYAxis.MulByMatrix3(CVector3(0,1,0),headMat);
   jawYAxis.MulByMatrix3(CVector3(0,1,0),jawMat);
   headZAxis.MulByMatrix3(CVector3(0,0,1),headMat);
   jawZAxis.MulByMatrix3(CVector3(0,0,1),jawMat);
   refYAxis.Sub(jawYAxis,headYAxis);
   refYAxis.ScaleInPlace(weight);
   refYAxis.AddInPlace(headYAxis);
   refYAxis.NormalizeInPlace();
   refZAxis.Sub(jawZAxis,headZAxis);
   refZAxis.ScaleInPlace(weight);
   refZAxis.AddInPlace(headZAxis);
   refZAxis.NormalizeInPlace();
   refXAxis.Cross(refZAxis,refYAxis);
   refYAxis.Cross(refXAxis,refZAxis);
   refXAxis.NormalizeInPlace();
   refXAxis.NegateInPlace();
   refYAxis.NormalizeInPlace();
   refXF.SetRotationFromXYZAxes(refXAxis,refYAxis,refZAxis);

   // interpolate the translation
   refPos.Sub(jawXF.GetTranslation(),headXF.GetTranslation());
   refPos.ScaleInPlace(weight);
   refPos.AddInPlace(headXF.GetTranslation());
   refXF.SetTranslation(refPos);

   refPos.Sub(jawRefPos,headRefPos);
   refPos.ScaleInPlace(weight);
   refPos.AddInPlace(headRefPos);

   refPos = MapObjectPositionToWorldSpace(refXF,refPos);

   // scale the corner offsets
   if(docorners)
   {
      KinematicState cornerKineL = (CRef)ctxt.GetInputValue(2);
      KinematicState cornerKineR = (CRef)ctxt.GetInputValue(3);
      KinematicState cornerKineLG = (CRef)ctxt.GetInputValue(4);
      KinematicState cornerKineRG = (CRef)ctxt.GetInputValue(5);
      CTransformation cornerXFL = cornerKineL.GetTransform();
      CTransformation cornerXFR = cornerKineR.GetTransform();
      CMatrix3 cornerMatL = cornerKineLG.GetTransform().GetRotationMatrix3();
      CMatrix3 cornerMatR = cornerKineRG.GetTransform().GetRotationMatrix3();
      CVector3 cornerPosL = cornerXFL.GetTranslation();
      CVector3 cornerPosR = cornerXFR.GetTranslation();
      cornerPosL.MulByMatrix3InPlace(cornerMatL);
      cornerPosR.MulByMatrix3InPlace(cornerMatR);
      cornerPosL.ScaleInPlace(1.0 - corner);
      cornerPosR.ScaleInPlace(corner);
      cornerPosL.Set(cornerPosL.GetX() * refScl.GetX(),cornerPosL.GetY() * refScl.GetY(),cornerPosL.GetZ() * refScl.GetZ());
      cornerPosR.Set(cornerPosR.GetX() * refScl.GetX(),cornerPosR.GetY() * refScl.GetY(),cornerPosR.GetZ() * refScl.GetZ());
      refPos.AddInPlace(cornerPosL);
      refPos.AddInPlace(cornerPosR);
   }
   refXF.SetTranslation(refPos);

   // and output!
   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(refXF);

   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_mouthinterpose_prop_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomProperty oCustomProperty;
   Parameter oParam;
   oCustomProperty = ctxt.GetSource();
   oCustomProperty.AddParameter(L"comisuraL",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-1,1,oParam);
   oCustomProperty.AddParameter(L"comisuraR",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-1,1,oParam);

   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sixcpp_mouthinterpose_prop_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout oLayout;
   PPGItem oItem;
   oLayout = ctxt.GetSource();
   oLayout.Clear();
   oLayout.AddItem(L"comisuraL",L"ComisuraL");
   oLayout.AddItem(L"comisuraR",L"ComisuraR");
   return CStatus::OK;
}
