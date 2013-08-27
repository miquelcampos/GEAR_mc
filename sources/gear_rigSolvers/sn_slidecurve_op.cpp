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


///////////////////////////////////////////////////////////////
// DEFINE METHODS
///////////////////////////////////////////////////////////////
XSIPLUGINCALLBACK CStatus sn_curveslide_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_curveslide_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_curveslide_op_Update( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_curveslide2_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_curveslide2_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_curveslide2_op_Update( CRef& in_ctxt );

double max(double a,double b);
double min(double a, double b);

///////////////////////////////////////////////////////////////
// CURVE SLIDE OP
///////////////////////////////////////////////////////////////
// Define =====================================================

XSIPLUGINCALLBACK CStatus sn_curveslide_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory oFactory = Application().GetFactory();
   op = ctxt.GetSource();
   pdef = oFactory.CreateParamDef(L"length",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0.01,10000,1,24);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"factor",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,100,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ==============================================
XSIPLUGINCALLBACK CStatus sn_curveslide_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;
   layout = ctxt.GetSource();
   layout.Clear();
   layout.AddItem(L"length",L"Length");
   layout.AddItem(L"factor",L"Strength");
   layout.AddItem(L"center",L"Center");
   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_curveslide_op_Update( CRef& in_ctxt )
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


///////////////////////////////////////////////////////////////
// CURVE SLIDE 2 OP
///////////////////////////////////////////////////////////////
// Define =====================================================

XSIPLUGINCALLBACK CStatus sn_curveslide2_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory oFactory = Application().GetFactory();
   op = ctxt.GetSource();
   pdef = oFactory.CreateParamDef(L"slvlength",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0.01,10000,1,24);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"mstlength",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0.01,10000,1,24);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"position",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"maxstretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,1,10000,1,3);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"maxsquash",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"softness",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ==============================================
XSIPLUGINCALLBACK CStatus sn_curveslide2_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;

   layout = ctxt.GetSource();
   layout.Clear();

   layout.AddGroup("Default");
   layout.AddItem(L"slvlength", L"Slave Length");
   layout.AddItem(L"mstlength", L"Master Length");
   layout.EndGroup();
   layout.AddGroup("Animate");
   layout.AddItem(L"position", L"Position");
   layout.AddItem(L"maxstretch", L"Max Stretch");
   layout.AddItem(L"maxsquash", L"Max Squash");
   layout.AddItem(L"softness", L"Softness");
   layout.EndGroup();

   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_curveslide2_op_Update( CRef& in_ctxt )
{

   OperatorContext ctxt( in_ctxt );

   double slvlength = ctxt.GetParameterValue(L"slvlength"); // Length of the constrained curve
   double mstlength = ctxt.GetParameterValue(L"mstlength"); // Rest length of the Master Curve
   double position = ctxt.GetParameterValue(L"position");
   double maxstretch = ctxt.GetParameterValue(L"maxstretch");
   double maxsquash = ctxt.GetParameterValue(L"maxsquash");
   double softness = ctxt.GetParameterValue(L"softness");

   Primitive slvPrim = (CRef)ctxt.GetInputValue(0);
   NurbsCurveList slvGeo(slvPrim.GetGeometry());
   NurbsCurve slvCrv(slvGeo.GetCurves()[0]);

   Primitive mstPrim = (CRef)ctxt.GetInputValue(1);
   NurbsCurveList mstGeo(mstPrim.GetGeometry());
   NurbsCurve mstCrv(mstGeo.GetCurves()[0]);

   // Inputs ---------------------------------------------------------
   double mstCrvLength = 0;
   mstCrv.GetLength(mstCrvLength);

   int slvPointCount = CControlPointRefArray(slvGeo.GetControlPoints()).GetCount();
   int mstPointCount = CControlPointRefArray(mstGeo.GetControlPoints()).GetCount();


    // Stretch --------------------------------------------------------
    double expo, ext;
    if ((mstCrvLength > mstlength) && (maxstretch > 1))
    {
        if (softness == 0)
            expo = 1;
        else
        {
            double stretch = (mstCrvLength - mstlength) / (slvlength * maxstretch);
            expo = 1 - exp(-(stretch) / softness);
        }

        ext = min(slvlength * (maxstretch - 1) * expo, mstCrvLength - mstlength);

        slvlength += ext;
    }
    else if ((mstCrvLength < mstlength) && (maxsquash < 1))
    {
        if (softness == 0)
            expo = 1;
        else
        {
            double squash = (mstlength - mstCrvLength) / (slvlength * maxsquash);
            expo = 1 - exp(-(squash) / softness);
        }

        ext = min(slvlength * (1 - maxsquash) * expo, mstlength - mstCrvLength);

        slvlength -= ext;
    }

    // Position --------------------------------------------------------
    double size = (slvlength / mstCrvLength) * 100;
    double sizeLeft = 100 - size;

    double start = position * sizeLeft;
    double end = start + size;

	// Process --------------------------------------------------------
   CControlPointRefArray slvPnts(slvGeo.GetControlPoints());
   CVector3Array curvePos = slvPnts.GetPositionArray();

	double step, perc, overPerc;
	CVector3 vPos, vTan, vNor, vBin;
   for(LONG i = 0; i < slvPointCount; i++)
   {
      step = (end - start) / (slvPointCount - 1.0);
      perc = start + (i * step);

      if ((0 <= perc) && (perc <= 100))
         mstCrv.EvaluatePositionFromPercentage(perc, vPos, vTan, vNor, vBin);
      else
      {
         if (perc < 0)
         {
             overPerc = perc;
             mstCrv.EvaluatePositionFromPercentage(0, vPos, vTan, vNor, vBin);
         }
         else
         {
             overPerc = perc - 100;
             mstCrv.EvaluatePositionFromPercentage(100, vPos, vTan, vNor, vBin);
         }

         vTan.ScaleInPlace((mstCrvLength / 100.0) * overPerc);
         vPos.AddInPlace(vTan);
      }

      curvePos[i] = vPos;
   }

   // Out ------------------------------------------------------------
   Primitive outPrim(ctxt.GetOutputTarget());
   NurbsCurveList outGeo(outPrim.GetGeometry());
   outGeo.GetControlPoints().PutPositionArray(curvePos);

   return CStatus::OK;
}
