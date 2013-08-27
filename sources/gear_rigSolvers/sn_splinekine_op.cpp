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
// DEFINE METHODS
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_splinekine_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_splinekine_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_splinekine_op_Update( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_rollsplinekine_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_rollsplinekine_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_rollsplinekine_op_Update( CRef& in_ctxt );

CStatus splinekine_op_Update( CRef& in_ctxt, int mode );
CVector3Array bezier4point(CVector3 a, CVector3 tan_a, CVector3 d, CVector3 tan_d, double u);

double max(double a,double b);
double min(double a, double b);

///////////////////////////////////////////////////////////////
// SPLINE KINE OP
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_splinekine_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter oParam;
   CRef pdef;

   Factory factory = Application().GetFactory();
   op = ctxt.GetSource();

   pdef = factory.CreateParamDef(L"count",CValue::siInt4,siPersistable | siAnimatable,L"",L"",2,2,100000,2,3);
   op.AddParameter(pdef,oParam);
   pdef = factory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,oParam);
   pdef = factory.CreateParamDef(L"resample",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,oParam);
   pdef = factory.CreateParamDef(L"subdiv",CValue::siInt4,siPersistable | siAnimatable,L"",L"",10,3,100000,3,24);
   op.AddParameter(pdef,oParam);
   pdef = factory.CreateParamDef(L"absolute",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,oParam);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);

   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sn_splinekine_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;

   layout = ctxt.GetSource();
   layout.Clear();

   layout.AddItem(L"u",L"U Value");
   layout.AddGroup(L"Resampling");
   layout.AddItem(L"resample",L"Enable");
   layout.AddItem(L"subdiv",L"Subdivision");
   layout.AddItem(L"absolute",L"Absolute");

   layout.EndGroup();

   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus sn_splinekine_op_Update( CRef& in_ctxt )
{
   return splinekine_op_Update(in_ctxt,0);
}

XSIPLUGINCALLBACK CStatus sn_rollsplinekine_op_Define( CRef& in_ctxt )
{
   return sn_splinekine_op_Define( in_ctxt );
}

XSIPLUGINCALLBACK CStatus sn_rollsplinekine_op_DefineLayout( CRef& in_ctxt )
{
   return sn_splinekine_op_DefineLayout(in_ctxt);
}

XSIPLUGINCALLBACK CStatus sn_rollsplinekine_op_Update( CRef& in_ctxt )
{
   return splinekine_op_Update(in_ctxt, 1);
}

///////////////////////////////////////////////////////////////
// METHOD
///////////////////////////////////////////////////////////////
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
   scl1.LinearlyInterpolate(scl[index1temp], scl[index2temp],vtemp);
   scl1.PutX(1);
   // scl1.PutX(modelXF.GetSclX());
   // We need to find another way to manage global scaling

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
   if (mode == 1)
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
