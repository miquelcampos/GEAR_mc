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
// XSI LOAD / UNLOAD PLUGIN
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus XSILoadPlugin( PluginRegistrar& in_reg )
{
   in_reg.PutAuthor(L"Helge Mathee, Jeremie Passerin");
   in_reg.PutName(L"sn_RigSolvers");
   in_reg.PutEmail(L"opensource@studionestbarcelona.com");
   in_reg.PutURL(L"http://opensource.studionestbarcelona.com");
   in_reg.PutVersion(2,0);

   // register all of the solvers

   // sn_spring_op.cpp
   in_reg.RegisterOperator(L"sn_xfspring_op");
   in_reg.RegisterOperator(L"sn_rotspring_op");

   // sn_ikfk2bone_op.cpp
   in_reg.RegisterOperator(L"sn_ik2bone_op");
   in_reg.RegisterOperator(L"sn_ikfk2bone_op");
   in_reg.RegisterOperator(L"sn_interLocalOri_op");

   // sn_stretchchain_op.cpp
   in_reg.RegisterOperator(L"sn_stretchChain_op");
   in_reg.RegisterOperator(L"sn_stretchChainMulti_op");

   // sn_splinekine_op.cpp
   in_reg.RegisterOperator(L"sn_splinekine_op");
   in_reg.RegisterOperator(L"sn_rollsplinekine_op");

   // sn_curveslide_op.cpp
   in_reg.RegisterOperator(L"sn_curveslide_op");
   in_reg.RegisterOperator(L"sn_curveslide2_op");

   // sn_null2curve_op.cpp
   in_reg.RegisterOperator(L"sn_null2curve_op");
   in_reg.RegisterOperator(L"sn_null2surface_op");

   // sn_squashstretch_op.cpp
   in_reg.RegisterOperator(L"sn_squashstretch_op");
   in_reg.RegisterOperator(L"sn_squashstretch2_op");
   in_reg.RegisterOperator(L"sn_curvelength_op");

   // sn_iso4point_op.cpp
   in_reg.RegisterOperator(L"sn_iso4point_op");

   // sn_interpose_op.cpp
   in_reg.RegisterOperator(L"sn_interpose_op");

   // sn_slerp_op.cpp
   in_reg.RegisterOperator(L"sn_slerp_op");

   // sn_inverseRotorder_op
   in_reg.RegisterOperator(L"sn_inverseRotorder_op");


//   in_reg.RegisterOperator(L"sn_mouthinterpose_op");

   // register all of the properties
   in_reg.RegisterProperty(L"sn_squashstretch_prop");

   return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus XSIUnloadPlugin( const PluginRegistrar& in_reg )
{
   CString strPluginName;
   strPluginName = in_reg.GetName();
   Application().LogMessage(strPluginName + L" has been unloaded.",siVerboseMsg);
   return CStatus::OK;
}

///////////////////////////////////////////////////////////////
// DEFINE MISC METHOD
///////////////////////////////////////////////////////////////

double max(double a,double b);
double min(double a,double b);
double clamp(double v,double a,double b);
double pingpong(double v);
double smoothstep(double v);
double smoothstep2(double v);
double smooth(double v);
double asmooth(double v);
CTransformation InterpolateTransform(CTransformation xf1, CTransformation xf2, double blend);
CVector3 rotateVectorAlongAxis(CVector3 v, CVector3 axis, double a);
CVector3 InterpolateVector(CVector3 vA, CVector3 vB, double blend);

///////////////////////////////////////////////////////////////
// MISC METHODS
///////////////////////////////////////////////////////////////
double max(double a,double b)
{
   if(a < b)
      return b;
   return a;
}

double min(double a, double b)
{
   if(a > b)
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

double smooth(double v)
{
   return sin(v * XSI::MATH::PI * .5);
}
double asmooth(double v)
{
   return asin(clamp((v - .5) * 2.0,-1,1)) / XSI::MATH::PI + .5;
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

CVector3 rotateVectorAlongAxis(CVector3 v, CVector3 axis, double a)
{
   // Angle as to be in radians

   double sa = sin(a / 2.0);
   double ca = cos(a / 2.0);

   CQuaternion q1, q2, q2n, q;
   CVector3 out;

   q1.Set(0, v.GetX(), v.GetY(), v.GetZ());
   q2.Set(ca, axis.GetX() * sa, axis.GetY() * sa, axis.GetZ() * sa);
   q2n.Set(ca, -axis.GetX() * sa, -axis.GetY() * sa, -axis.GetZ() * sa);

   q.Mul(q2, q1);
   q.MulInPlace(q2n);

   out.Set(q.GetX(), q.GetY(), q.GetZ());
   return out;
}

CVector3 InterpolateVector(CVector3 vA, CVector3 vB, double blend)
{

   if (blend == 0)
      return vA;
   else if (blend == 1)
      return vB;

   CVector3 cross;
   cross.Cross(vA, vB);
   cross.NormalizeInPlace();

   double lengthA = vA.GetLength();
   double lengthB = vB.GetLength();

   double length = lengthB * blend + lengthA * (1 - blend);

   double a = vA.GetAngle(vB);
   CVector3 v = rotateVectorAlongAxis(vA, cross, a * blend);

   v.NormalizeInPlace();
   v.ScaleInPlace(length);

   return v;
}
