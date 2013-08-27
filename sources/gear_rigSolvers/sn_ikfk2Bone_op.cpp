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
#include <stdio.h>


using namespace XSI;
using namespace MATH;

///////////////////////////////////////////////////////////////
// STRUCT
///////////////////////////////////////////////////////////////
// GetFKTransform =============================================
struct s_GetFKTransform
{
   double lengthA;
   double lengthB;
   bool negate;
   CTransformation root;
   CTransformation bone1;
   CTransformation bone2;
   CTransformation eff;
};

struct s_GetIKTransform
{
   double lengthA;
   double lengthB;
   bool negate;
   double roll;
   double scaleA;
   double scaleB;
   double maxstretch;
   double softness;
   double slide;
   double reverse;
   CTransformation root;
   CTransformation eff;
   CTransformation upv;
};

///////////////////////////////////////////////////////////////
// DEFINE METHODS
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_ik2bone_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_ik2bone_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_ik2bone_op_Update( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_ikfk2bone_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_ikfk2bone_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_ikfk2bone_op_Update( CRef& in_ctxt );

CTransformation GetIKTransform(s_GetIKTransform values, CString outportName);
CTransformation GetFKTransform(s_GetFKTransform values, CString outportName);
CTransformation InterpolateTransform(CTransformation xf1, CTransformation xf2, double blend);
CVector3 InterpolateLocalOrientation(CRotation globalRotA, CRotation globalRotB, CRotation globalRotParent, double localRotXA, double localRotXB, double blend);

double max(double a,double b);
double min(double a,double b);
CVector3 rotateVectorAlongAxis(CVector3 v, CVector3 axis, double a);
CVector3 InterpolateVector(CVector3 vA, CVector3 vB, double blend);

///////////////////////////////////////////////////////////////
// IK 2 BONE OP
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_ik2bone_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();

	pdef = factory.CreateParamDef(L"lengthA",CValue::siDouble,siPersistable|siAnimatable,L"",L"",3.0, 0.0, 999999.0, 0.0, 10.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"lengthB",CValue::siDouble,siPersistable|siAnimatable,L"",L"",5.0, 0.0, 999999.0, 0.0, 10.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"negate",CValue::siBool,siPersistable|siAnimatable,L"",L"",false);
	op.AddParameter(pdef,param);

	pdef = factory.CreateParamDef(L"roll",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.0, -360.0, 360.0, 0.-360.0, 360.0);
	op.AddParameter(pdef,param);

	pdef = factory.CreateParamDef(L"scaleA",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1.0, 0.0, 999999.0, 0.0, 2.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"scaleB",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1.0, 0.0, 999999.0, 0.0, 2.0);
	op.AddParameter(pdef,param);

	pdef = factory.CreateParamDef(L"maxstretch",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1.0, 1.0, 999999.0, 1.0, 2.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"softness",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.0, 0.0, 999999.0, 0.0, 1.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"slide",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.5,0.0, 1.0, 0.0, 1.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"reverse",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.0, 0.0, 1.0, 0.0, 1.0);
	op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout =====================================================
XSIPLUGINCALLBACK CStatus sn_ik2bone_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;

   layout = ctxt.GetSource();
   layout.Clear();

   layout.AddGroup("Default Length");
   layout.AddItem("lengthA", "Bone A");
   layout.AddItem("lengthB", "Bone B");
   layout.AddItem("negate", "Negate");
   layout.EndGroup();

   layout.AddGroup("Animate");
   layout.AddItem(L"roll",L"Roll");
   layout.AddItem(L"scaleA",L"Scale A");
   layout.AddItem(L"scaleB",L"Scale B");
   layout.AddItem(L"maxstretch",L" Max Stretch");
   layout.AddItem(L"softness",L"Softness");
   layout.AddItem(L"slide",L"Slide");
   layout.AddItem(L"reverse",L"Reverse");
   layout.EndGroup();

   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_ik2bone_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );

   KinematicState rootKine = (CRef)ctxt.GetInputValue(0);
   KinematicState effKine = (CRef)ctxt.GetInputValue(1);
   KinematicState upvKine = (CRef)ctxt.GetInputValue(2);

   // create the struct
   s_GetIKTransform params;
   params.root = rootKine.GetTransform();
   params.eff = effKine.GetTransform();
   params.upv = upvKine.GetTransform();

   // get the parameters
   params.lengthA = ctxt.GetParameterValue(L"lengthA");
   params.lengthB = ctxt.GetParameterValue(L"lengthB");
   params.negate = ctxt.GetParameterValue(L"negate");
   params.roll = DegreesToRadians(ctxt.GetParameterValue(L"roll"));
   params.scaleA = ctxt.GetParameterValue(L"scaleA");
   params.scaleB = ctxt.GetParameterValue(L"scaleB");
   params.maxstretch = ctxt.GetParameterValue(L"maxstretch");
   params.softness = ctxt.GetParameterValue(L"softness");
   params.slide = ctxt.GetParameterValue(L"slide");
   params.reverse = ctxt.GetParameterValue(L"reverse");

//   FILE * file = fopen("/tmp/rig.log","ab");
//   fprintf(file,"%.12f\n",params.lengthA);
//   fclose(file);

   // get output name
   CRef outputPortRef = ctxt.GetOutputPort();
   OutputPort outputPort(outputPortRef);
   CString outportName = outputPort.GetName();

   // calculate the transform
   CTransformation t = GetIKTransform(params, outportName);

   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(t);

   return CStatus::OK;
}

///////////////////////////////////////////////////////////////
// IK FK 2 BONE OP
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_ikfk2bone_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();

	pdef = factory.CreateParamDef(L"lengthA",CValue::siDouble,siPersistable|siAnimatable,L"",L"",3.0, 0.0, 999999.0, 0.0, 10.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"lengthB",CValue::siDouble,siPersistable|siAnimatable,L"",L"",5.0, 0.0, 999999.0, 0.0, 10.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"negate",CValue::siBool,siPersistable|siAnimatable,L"",L"",false);
	op.AddParameter(pdef,param);

   pdef = factory.CreateParamDef(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0, 0.0,1.0, 0.0, 1.0);
   op.AddParameter(pdef,param);

	pdef = factory.CreateParamDef(L"roll",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.0,  -360.0,  360.0,  -360.0,  360.0);
	op.AddParameter(pdef,param);

	pdef = factory.CreateParamDef(L"scaleA",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1.0, 0.0, 999999.0, 0.0, 2.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"scaleB",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1.0, 0.0, 999999.0, 0.0, 2.0);
	op.AddParameter(pdef,param);

	pdef = factory.CreateParamDef(L"maxstretch",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1.0, 1.0, 999999.0, 1.0, 2.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"softness",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.0, 0.0, 999999.0, 0.0, 1.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"slide",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.5,0.0, 1.0, 0.0, 1.0);
	op.AddParameter(pdef,param);
	pdef = factory.CreateParamDef(L"reverse",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.0, 0.0, 1.0, 0.0, 1.0);
	op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout =====================================================
XSIPLUGINCALLBACK CStatus sn_ikfk2bone_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;

   layout = ctxt.GetSource();
   layout.Clear();

   layout.AddGroup("Default Length");
   layout.AddItem("lengthA", "Bone A");
   layout.AddItem("lengthB", "Bone B");
   layout.AddItem("negate", "Negate");
   layout.EndGroup();

   layout.AddGroup("Animate");
   layout.AddItem(L"blend",L"Blend IK/FK");
   layout.AddItem(L"roll",L"Roll");
   layout.AddItem(L"scaleA",L"Scale A");
   layout.AddItem(L"scaleB",L"Scale B");
   layout.AddItem(L"maxstretch",L" Max Stretch");
   layout.AddItem(L"softness",L"Softness");
   layout.AddItem(L"slide",L"Slide");
   layout.AddItem(L"reverse",L"Reverse");
   layout.EndGroup();

   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_ikfk2bone_op_Update( CRef& in_ctxt )
{
   OperatorContext ctxt( in_ctxt );

   KinematicState ikrootKine = (CRef)ctxt.GetInputValue(0);
   KinematicState ikeffKine = (CRef)ctxt.GetInputValue(1);
   KinematicState ikupvKine = (CRef)ctxt.GetInputValue(2);
   KinematicState fkbone1Kine = (CRef)ctxt.GetInputValue(3);
   KinematicState fkbone2Kine = (CRef)ctxt.GetInputValue(4);
   KinematicState fkeffKine = (CRef)ctxt.GetInputValue(5);

   double blend = ctxt.GetParameterValue(L"blend");

   // setup the base IK parameters
   s_GetIKTransform ikparams;

   ikparams.root = ikrootKine.GetTransform();
   ikparams.eff = ikeffKine.GetTransform();
   ikparams.upv = ikupvKine.GetTransform();

   ikparams.lengthA = ctxt.GetParameterValue(L"lengthA");
   ikparams.lengthB = ctxt.GetParameterValue(L"lengthB");
   ikparams.negate = ctxt.GetParameterValue(L"negate");
   ikparams.roll = DegreesToRadians(ctxt.GetParameterValue(L"roll"));
   ikparams.scaleA = ctxt.GetParameterValue(L"scaleA");
   ikparams.scaleB = ctxt.GetParameterValue(L"scaleB");
   ikparams.maxstretch = ctxt.GetParameterValue(L"maxstretch");
   ikparams.softness = ctxt.GetParameterValue(L"softness");
   ikparams.slide = ctxt.GetParameterValue(L"slide");
   ikparams.reverse = ctxt.GetParameterValue(L"reverse");

   // setup the base FK parameters
   s_GetFKTransform fkparams;

   fkparams.root = ikparams.root;
   fkparams.bone1 = fkbone1Kine.GetTransform();
   fkparams.bone2 = fkbone2Kine.GetTransform();
   fkparams.eff = fkeffKine.GetTransform();

   fkparams.lengthA = ikparams.lengthA;
   fkparams.lengthB = ikparams.lengthB;
   fkparams.negate = ikparams.negate;

   // get output name
   CRef outputPortRef = ctxt.GetOutputPort();
   OutputPort outputPort(outputPortRef);
   CString outportName = outputPort.GetName();

   // for optimization
   CTransformation result;
   if(blend == 0.0)
      result = GetFKTransform(fkparams, outportName);
   else if(blend == 1.0)
      result = GetIKTransform(ikparams, outportName);
   else
   {
      // here is where the blending happens!
      CTransformation ikbone1 = GetIKTransform(ikparams, CString(L"OutBoneA"));
      CTransformation ikbone2 = GetIKTransform(ikparams, CString(L"OutBoneB"));
      CTransformation ikeff = GetIKTransform(ikparams, CString(L"OutEff"));

      CTransformation fkbone1 = fkparams.bone1;
      CTransformation fkbone2 = fkparams.bone2;
      CTransformation fkeff = fkparams.eff;

      // map the secondary transforms from global to local
      ikeff = MapWorldPoseToObjectSpace(ikbone2, ikeff);
      fkeff = MapWorldPoseToObjectSpace(fkbone2, fkeff);
      ikbone2 = MapWorldPoseToObjectSpace(ikbone1, ikbone2);
      fkbone2 = MapWorldPoseToObjectSpace(fkbone1, fkbone2);

      // now blend them!
      fkparams.bone1 = InterpolateTransform(fkbone1, ikbone1, blend);
      fkparams.bone2 = InterpolateTransform(fkbone2, ikbone2, blend);
      fkparams.eff = InterpolateTransform(fkeff, ikeff, blend);

      // now map the local transform back to global!
      fkparams.bone2 = MapObjectPoseToWorldSpace(fkparams.bone1, fkparams.bone2);
      fkparams.eff = MapObjectPoseToWorldSpace(fkparams.bone2, fkparams.eff);

      // calculate the result based on that
      result = GetFKTransform(fkparams, outportName);
   }

   // output
   KinematicState outKine(ctxt.GetOutputTarget());
   outKine.PutTransform(result);

   return CStatus::OK;
}

///////////////////////////////////////////////////////////////
// METHODS
///////////////////////////////////////////////////////////////
// GetIKTransform =============================================
CTransformation GetIKTransform(s_GetIKTransform values, CString outportName)
{
   // prepare all variables
   CTransformation result;
   CVector3 bonePos,rootPos,effPos,upvPos,rootEff, xAxis,yAxis,zAxis, rollAxis;

   rootPos = values.root.GetTranslation();
   effPos = values.eff.GetTranslation();
   upvPos = values.upv.GetTranslation();
   rootEff.Sub(effPos,rootPos);
   rollAxis.Normalize(rootEff);

   CMatrix4 rootMatrix = values.root.GetMatrix4();
   CMatrix4 rootMatrixNeg;
   rootMatrixNeg.Invert(rootMatrix);

   double rootEffDistance = rootEff.GetLength();

   // init the scaling
   double global_scale = values.root.GetScaling().GetX();
   result.SetScaling(values.root.GetScaling());

   // Distance with MaxStretch ---------------------
   double restLength = values.lengthA * values.scaleA + values.lengthB * values.scaleB;
   CVector3 distanceVector;
   distanceVector.MulByMatrix4(effPos, rootMatrixNeg);
   double distance = distanceVector.GetLength();
   double distance2 = distance;
   if (distance > (restLength * (values.maxstretch)))
   {
      distanceVector.NormalizeInPlace();
      distanceVector.ScaleInPlace(restLength * (values.maxstretch) );
      distance = restLength * (values.maxstretch);
   }

   // Adapt Softness value to chain length --------
   values.softness = values.softness * restLength *.1;

   // Stretch and softness ------------------------
   // We use the real distance from root to controler to calculate the softness
   // This way we have softness working even when there is no stretch
   double stretch = max(1, distance / restLength);
   double da = restLength - values.softness;
   if (values.softness > 0 && distance2 > da)
   {
      double newlen = values.softness*(1.0 - exp(-(distance2 -da)/values.softness)) + da;
      stretch = distance / newlen;
   }

   values.lengthA = values.lengthA * stretch * values.scaleA * global_scale;
   values.lengthB = values.lengthB * stretch * values.scaleB * global_scale;

   // Reverse -------------------------------------
   double d = distance / (values.lengthA + values.lengthB);

   double reverse_scale;
   if (values.reverse < 0.5)
      reverse_scale = 1-(values.reverse*2 * (1-d));
   else
      reverse_scale = 1-((1-values.reverse)*2 * (1-d));

   values.lengthA *= reverse_scale;
   values.lengthB *= reverse_scale;

   bool invert = values.reverse > 0.5;

   // Slide ---------------------------------------
   double slide_add;
   if (values.slide < .5)
      slide_add = (values.lengthA * (values.slide * 2)) - (values.lengthA);
   else
      slide_add = (values.lengthB * (values.slide * 2)) - (values.lengthB);

   values.lengthA += slide_add;
   values.lengthB -= slide_add;

   // calculate the angle inside the triangle!
   double angleA = 0;
   double angleB = 0;

   // check if the divider is not null otherwise the result is nan
   // and the output disapear from xsi, that breaks constraints
   if((rootEffDistance < values.lengthA + values.lengthB) && (rootEffDistance > fabs(values.lengthA - values.lengthB) + 1E-6))
   {
      // use the law of cosine for lengthA
      double a = values.lengthA;
      double b = rootEffDistance;
      double c = values.lengthB;

         angleA = acos(min(1, (a * a + b * b - c * c ) / ( 2 * a * b)));

      // use the law of cosine for lengthB
      a = values.lengthB;
      b = values.lengthA;
      c = rootEffDistance;
      angleB = acos(min(1, (a * a + b * b - c * c ) / ( 2 * a * b)));

      // invert the angles if need be
      if(invert)
      {
         angleA = -angleA;
         angleB = -angleB;
      }
   }

   // start with the X and Z axis
   xAxis = rootEff;
   yAxis.LinearlyInterpolate(rootPos,effPos,.5);
   yAxis.Sub(upvPos,yAxis);
   yAxis = rotateVectorAlongAxis(yAxis, rollAxis, values.roll);
   zAxis.Cross(xAxis,yAxis);
   xAxis.NormalizeInPlace();
   zAxis.NormalizeInPlace();

   // switch depending on our mode
   if(outportName == "OutBoneA")  // Bone A
   {
      // check if we need to rotate the bone
      if(angleA != 0.0)
      {
         CRotation rot;
         rot.SetFromAxisAngle(zAxis,angleA);
         xAxis.MulByMatrix3InPlace(rot.GetMatrix());
      }

      if (values.negate)
         xAxis.NegateInPlace();

      // cross the yAxis and normalize
      yAxis.Cross(zAxis,xAxis);
      yAxis.NormalizeInPlace();

      // output the rotation
      result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

      // set the scaling + the position
      result.SetSclX(values.lengthA);
      result.SetTranslation(rootPos);
   }
   else if(outportName == "OutBoneB")  // Bone B
   {
      // check if we need to rotate the bone
      if(angleA != 0.0)
      {
         CRotation rot;
         rot.SetFromAxisAngle(zAxis,angleA);
         xAxis.MulByMatrix3InPlace(rot.GetMatrix());
      }

      // calculate the position of the elbow!
      bonePos.Scale(values.lengthA,xAxis);
      bonePos.AddInPlace(rootPos);

      // check if we need to rotate the bone
      if(angleB != 0.0)
      {
         CRotation rot;
         rot.SetFromAxisAngle(zAxis,angleB-XSI::MATH::PI);
         xAxis.MulByMatrix3InPlace(rot.GetMatrix());
      }

      if (values.negate)
         xAxis.NegateInPlace();

      // cross the yAxis and normalize
      yAxis.Cross(zAxis,xAxis);
      yAxis.NormalizeInPlace();

      // output the rotation
      result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

      // set the scaling + the position
      result.SetSclX(values.lengthB);
      result.SetTranslation(bonePos);
   }
   else if(outportName == "OutCenter")  // center
   {
      // check if we need to rotate the bone
      bonePos.Scale(values.lengthA,xAxis);
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

      if (values.negate)
         xAxis.NegateInPlace();

      yAxis.Cross(zAxis,xAxis);
      yAxis.NormalizeInPlace();

      // output the rotation
      result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

      // set the scaling + the position
      result.SetSclX(stretch * values.root.GetSclX());

      result.SetTranslation(bonePos);
   }
   else if(outportName == "OutCenterN")  // center normalized
   {
      // check if we need to rotate the bone
      if(angleA != 0.0)
      {
         CRotation rot;
         rot.SetFromAxisAngle(zAxis,angleA);
         xAxis.MulByMatrix3InPlace(rot.GetMatrix());
      }

      // calculate the position of the elbow!
      bonePos.Scale(values.lengthA,xAxis);
      bonePos.AddInPlace(rootPos);

      // check if we need to rotate the bone
      if(angleB != 0.0)
      {
         if(invert)
            angleB += XSI::MATH::PI * 2;
         CRotation rot;
         rot.SetFromAxisAngle(zAxis,angleB*.5-XSI::MATH::PI*.5);
         xAxis.MulByMatrix3InPlace(rot.GetMatrix());
      }      // cross the yAxis and normalize
      // yAxis.Sub(upvPos,bonePos); // this was flipping the centerN when the elbow/upv was aligned to root/eff
      zAxis.Cross(xAxis,yAxis);
      zAxis.NormalizeInPlace();

      if (values.negate)
         xAxis.NegateInPlace();

      yAxis.Cross(zAxis,xAxis);
      yAxis.NormalizeInPlace();

      // output the rotation
      result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

      // set the scaling + the position
      // result.SetSclX(stretch * values.root.GetSclX());

      result.SetTranslation(bonePos);
   }
   else if(outportName == "OutEff")  // effector
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
      bonePos.Scale(values.lengthA,xAxis);
      effPos.AddInPlace(bonePos);

      // check if we need to rotate the bone
      if(angleB != 0.0)
      {
         CRotation rot;
         rot.SetFromAxisAngle(zAxis,angleB-XSI::MATH::PI);
         xAxis.MulByMatrix3InPlace(rot.GetMatrix());
      }

      // calculate the position of the effector!
      bonePos.Scale(values.lengthB,xAxis);
      effPos.AddInPlace(bonePos);

      // cross the yAxis and normalize
      yAxis.Cross(zAxis,xAxis);
      yAxis.NormalizeInPlace();

      // output the rotation
      result = values.eff;
      result.SetTranslation(effPos);
   }


   CRotation r = result.GetRotation();
   CVector3 eulerAngles = r.GetXYZAngles();

   double rx = eulerAngles.GetX();
   double ry = eulerAngles.GetY();
   double rz = eulerAngles.GetZ();

   return result;
}

// GetFKTransform =============================================
CTransformation GetFKTransform(s_GetFKTransform values, CString outportName)
{
   // prepare all variables
   CTransformation result;
   CVector3 xAxis,yAxis,zAxis,temp;

   if(outportName == "OutBoneA")
   {
      result = values.bone1;
      xAxis.Sub(values.bone2.GetTranslation(),values.bone1.GetTranslation());
      result.SetSclX(xAxis.GetLength());

      if (values.negate)
         xAxis.NegateInPlace();

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

   }
   else if(outportName == "OutBoneB")  //  Bone B
   {
      result = values.bone2;
      xAxis.Sub(values.eff.GetTranslation(),values.bone2.GetTranslation());
      result.SetSclX(xAxis.GetLength());

      if (values.negate)
         xAxis.NegateInPlace();

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
   }
   else if(outportName == "OutCenter") // center
   {
      result = values.bone2;
      result.SetSclX(values.root.GetSclX() * values.bone2.GetSclX() / values.lengthB );
      xAxis.Sub(values.eff.GetTranslation(),values.bone1.GetTranslation());

      // cross the yAxis and normalize
      xAxis.NormalizeInPlace();
      temp.Set(1,0,0);
      yAxis.MulByMatrix3(temp,values.bone1.GetRotationMatrix3());
      temp.MulByMatrix3(CVector3(-1,0,0),values.bone2.GetRotationMatrix3());
      yAxis.AddInPlace(temp);
      if(yAxis.GetLength() <= 0.001)
         yAxis.MulByMatrix3(CVector3(0,1,0),values.bone2.GetRotationMatrix3());

      if (values.negate)
         xAxis.NegateInPlace();

      zAxis.Cross(xAxis,yAxis);
      zAxis.NormalizeInPlace();
      yAxis.Cross(zAxis,xAxis);
      yAxis.NormalizeInPlace();

      // rotation
      result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

   }
   else if(outportName == "OutCenterN") // center normalized
   {
      /*
      // cross the yAxis and normalize
      temp.Set(1,0,0);
      yAxis.MulByMatrix3(temp, values.bone1.GetRotationMatrix3());
      temp.MulByMatrix3(CVector3(-1,0,0),values.bone2.GetRotationMatrix3());
      yAxis.AddInPlace(temp);
      if(yAxis.GetLength() <= 0.001)
         yAxis.MulByMatrix3(CVector3(0,1,0),values.bone2.GetRotationMatrix3());
      yAxis.NormalizeInPlace();

      zAxis.Set(0,0,1);
      zAxis.MulByMatrix3InPlace(values.bone2.GetRotationMatrix3());

      xAxis.Cross(yAxis, zAxis);
      xAxis.NormalizeInPlace();

      // Avoid flipping
      temp.Set(1,0,0);
      temp.MulByMatrix3InPlace(values.bone2.GetRotationMatrix3());
      if (temp.Dot(xAxis) < 0)
      {
         xAxis.NegateInPlace();
         yAxis.NegateInPlace();
      }
      result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
      */

	   // Only +/-180 degree with this one but we don't get the shear issue anymore
      CTransformation t = MapWorldPoseToObjectSpace(values.bone1, values.bone2);
	   CVector3 v = t.GetRotation().GetXYZAngles();
	   v.ScaleInPlace(.5);
	   t.SetRotationFromXYZAngles(v);
	   t = MapObjectPoseToWorldSpace(values.bone1, t);
	   result.SetRotation(t.GetRotation());

      // rotation
      result.SetTranslation(values.bone2.GetTranslation());
   }
   else if(outportName == "OutEff")  // effector
      result = values.eff;

   return result;
}

///////////////////////////////////////////////////////////////
// INTER LOCAL ORI
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_interLocalOri_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();

	pdef = factory.CreateParamDef(L"blend",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0.0,  0.0,  1.0,  0.0,  1.0);
	op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout =====================================================
XSIPLUGINCALLBACK CStatus sn_interLocalOri_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;

   layout = ctxt.GetSource();
   layout.Clear();

   layout.AddItem("blend", "Blend");

   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_interLocalOri_op_Update( CRef& in_ctxt )
{

   OperatorContext ctxt( in_ctxt );

   // Inputs
   double blend = ctxt.GetParameterValue(L"blend");

   KinematicState kA = (CRef)ctxt.GetInputValue(0);
   KinematicState kB = (CRef)ctxt.GetInputValue(1);
   KinematicState kParent = (CRef)ctxt.GetInputValue(2);
   double localRotXA = ctxt.GetInputValue(3);
   double localRotXB = ctxt.GetInputValue(4);

   CTransformation tA = kA.GetTransform();
   CTransformation tB = kB.GetTransform();
   CTransformation tParent = kParent.GetTransform();

   CRotation globalRotA = tA.GetRotation();
   CRotation globalRotB = tB.GetRotation();
   CRotation globalRotParent = tParent.GetRotation();

   Application().LogMessage(L"-------------");
   CVector3 vA = globalRotA.GetXYZAngles();
   CVector3 vB = globalRotB.GetXYZAngles();
   CVector3 vP = globalRotParent.GetXYZAngles();
   Application().LogMessage(CString(vA.GetX()));
   Application().LogMessage(CString(vB.GetX()));
   Application().LogMessage(CString(vP.GetX()));

   // Process
   CVector3 v = InterpolateLocalOrientation(globalRotA, globalRotB, globalRotParent, localRotXA, localRotXB, blend);

   // Get output name
   CRef outputPortRef = ctxt.GetOutputPort();
   OutputPort outputPort(outputPortRef);
   CString outportName = outputPort.GetName();

   Application().LogMessage(outportName);
   Application().LogMessage(CString(v.GetX()));
   Application().LogMessage(CString(v.GetY()));
   Application().LogMessage(CString(v.GetZ()));

   if (outportName == "rotx")
      outputPort.PutValue(v.GetX());
   else if (outportName == "nroty")
      outputPort.PutValue(v.GetY());
   else if (outportName == "nrotz")
      outputPort.PutValue(v.GetZ());
   else
      outputPort.PutValue(0);

   return CStatus::OK;
}

// InterpolateLocalOrientation =============================================
CVector3 InterpolateLocalOrientation(CRotation globalRotA, CRotation globalRotB, CRotation globalRotParent, double localRotXA, double localRotXB, double blend)
{
   CRotation globalRotParentInv;
   globalRotParentInv.Invert(globalRotParent);

   CVector3 vxA, vxB;
	vxA.Set(1,0,0);
	vxB.Set(1,0,0);
	vxA.MulByMatrix3InPlace(globalRotA.GetMatrix());
	vxB.MulByMatrix3InPlace(globalRotB.GetMatrix());

   CVector3 vX, vY, vZ;
   vX = InterpolateVector(vxA, vxB, blend);
	vX.NormalizeInPlace();
	vX.MulByMatrix3InPlace(globalRotParentInv.GetMatrix());

	vZ.Set(0,0,1);
	vZ.MulByMatrix3InPlace(globalRotParentInv.GetMatrix());

	vY.Cross(vZ, vX);

	CRotation r;
	r.SetFromXYZAxes(vX, vY, vZ);

   CVector3 result = r.GetXYZAngles();
   result.PutX(localRotXB * blend + localRotXA * (1 - blend));
   result.PutY(RadiansToDegrees(result.GetY()));
   result.PutZ(RadiansToDegrees(result.GetZ()));

	return result;
}

