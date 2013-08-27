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
XSIPLUGINCALLBACK CStatus sn_null2curve_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_null2curvee_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_null2curve_op_Update( CRef& in_ctxt );

XSIPLUGINCALLBACK CStatus sn_null2surface_op_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_null2surface_op_DefineLayout( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_null2surface_op_Update( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus sn_null2surface_op_PPGEvent( const CRef& in_ctxt );

double clamp(double v,double a,double b);
double smooth(double v);
double asmooth(double v);

///////////////////////////////////////////////////////////////
// NULL 2 CURVE
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_null2curve_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory oFactory = Application().GetFactory();
   op = ctxt.GetSource();
   pdef = oFactory.CreateParamDef(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"imin",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"imax",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"omin",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"omax",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"soft_blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"upv_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,100000,0,10);
   op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ==============================================
XSIPLUGINCALLBACK CStatus sn_null2curve_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;

   layout = ctxt.GetSource();
   layout.Clear();

   layout.AddGroup("Input");
   layout.AddItem(L"blend",L"Blend to Slider");
   layout.AddItem(L"u",L"U Value");
   layout.AddItem(L"imin",L"Minimum");
   layout.AddItem(L"imax",L"Maximum");
   layout.EndGroup();

   layout.AddGroup("Output");
   layout.AddItem(L"omin",L"Minimum");
   layout.AddItem(L"omax",L"Maximum");
   layout.EndGroup();

   layout.AddGroup("Softness");
   layout.AddItem(L"soft_blend",L"Blend");
   layout.EndGroup();

   layout.AddGroup("Orientation");
   CValueArray modeItems(6);
   modeItems[0] = L"Use Driver Rot";
   modeItems[1] = (LONG)0l;
   modeItems[2] = L"Use Upvector Rot";
   modeItems[3] = (LONG)1l;
   modeItems[4] = L"Tangent+Upvector";
   modeItems[5] = (LONG)2l;
   layout.AddEnumControl(L"upv_mode",modeItems,L"Mode");
   layout.EndGroup();

   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_null2curve_op_Update( CRef& in_ctxt )
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

///////////////////////////////////////////////////////////////
// NULL 2 SURFACE
///////////////////////////////////////////////////////////////
// Define =====================================================
XSIPLUGINCALLBACK CStatus sn_null2surface_op_Define( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   CustomOperator op;
   Parameter param;
   CRef pdef;
   Factory oFactory = Application().GetFactory();
   op = ctxt.GetSource();
   pdef = oFactory.CreateParamDef(L"blend",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"u",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"v",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"input_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,100000,0,10);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"iu_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"iv_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"iu_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,10,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"iv_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,10,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"i0_minmax",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"ix_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1000,1000,-2,2);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"iy_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1000,1000,-2,2);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"ix_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",8,0,1000,0,10);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"iy_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",8,0,1000,0,10);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"ix_invert",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"iy_invert",CValue::siBool,siPersistable | siAnimatable,L"",L"",1,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"axis_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,0,100000,0,10);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"i1_minmax",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"ou_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"ov_center",CValue::siDouble,siPersistable | siAnimatable,L"",L"",.5,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"ou_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,10,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"ov_variance",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1,0,10,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"o_minmax",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"surf_index",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,100000,0,10);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"upv_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",0,0,100000,0,10);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"upv_offsetu",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-.5,.5);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"upv_offsetv",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0,-1,1,-.5,.5);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"upv_debug_pos",CValue::siBool,siPersistable | siAnimatable,L"",L"",0,0,1,0,1);
   op.AddParameter(pdef,param);
   pdef = oFactory.CreateParamDef(L"scl_mode",CValue::siInt4,siPersistable | siAnimatable,L"",L"",1,0,100000,0,10);
   op.AddParameter(pdef,param);

   op.PutAlwaysEvaluate(false);
   op.PutDebug(0);
   return CStatus::OK;
}

// Define Layout ==============================================
XSIPLUGINCALLBACK CStatus sn_null2surface_op_DefineLayout( CRef& in_ctxt )
{
   Context ctxt( in_ctxt );
   PPGLayout layout;
   PPGItem oItem;
   layout = ctxt.GetSource();
   layout.Clear();
   layout.AddGroup("Override");
   layout.AddItem(L"blend",L"Blend to Sliders");
   layout.AddItem(L"u",L"U Value");
   layout.AddItem(L"v",L"V Value");
   layout.EndGroup();
   layout.AddGroup("Input");
   {
      CValueArray modeItems(4);
      modeItems[0] = L"Nurbs Based";
      modeItems[1] = (LONG)0l;
      modeItems[2] = L"Transform Based";
      modeItems[3] = (LONG)1l;
      layout.AddEnumControl(L"input_mode",modeItems,L"Mode");
   }
   layout.AddGroup("Nurbs Based");
   layout.AddItem(L"iu_center",L"U Center");
   layout.AddItem(L"iv_center",L"V Center");
   layout.AddItem(L"iu_variance",L"U Variance");
   layout.AddItem(L"iv_variance",L"V Variance");
   layout.AddItem(L"i0_minmax",L"Treat sliders as Min Max");
   layout.AddButton(L"setInputUV",L"Set from current Driver Pos");
   layout.EndGroup();
   layout.AddGroup("Transform Based");
   layout.AddItem(L"ix_center",L"Axis1 Center");
   layout.AddItem(L"iy_center",L"Axis2 Center");
   layout.AddItem(L"ix_variance",L"Axis1 Variance");
   layout.AddItem(L"iy_variance",L"Axis2 Variance");
   layout.AddItem(L"ix_invert",L"Axis1 Invert");
   layout.AddItem(L"iy_invert",L"Axis2 Invert");
   layout.AddItem(L"i1_minmax",L"Treat sliders as Min Max");
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
      layout.AddEnumControl(L"axis_mode",modeItems,L"Axes");
   }
   layout.AddButton(L"setInputXY",L"Set from current Driver Pos");
   layout.EndGroup();
   layout.EndGroup();
   layout.AddGroup("Output");
   layout.AddItem(L"ou_center",L"U Center");
   layout.AddItem(L"ov_center",L"V Center");
   layout.AddItem(L"ou_variance",L"U Variance");
   layout.AddItem(L"ov_variance",L"V Variance");
   layout.AddItem(L"o_minmax",L"Treat sliders as Min Max");
   layout.AddItem(L"surf_index",L"Surface Index");
   layout.AddButton(L"setOutputUV",L"Set from current Driver Pos");
   layout.EndGroup();
   layout.AddGroup("Orientation");
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
      layout.AddEnumControl(L"upv_mode",modeItems,L"Mode");
   }
   layout.AddItem(L"upv_offsetu",L"U Offset");
   layout.AddItem(L"upv_offsetv",L"V Offset");
   layout.AddItem(L"upv_debug_pos",L"Show Upv Pos (debug)");
   layout.EndGroup();
   layout.AddGroup("Scaling");
   {
      CValueArray modeItems(4);
      modeItems[0] = L"Use Driver Scl";
      modeItems[1] = (LONG)0l;
      modeItems[2] = L"Use Upvector Scl";
      modeItems[3] = (LONG)1l;
      layout.AddEnumControl(L"scl_mode",modeItems,L"Mode");
   }
   layout.EndGroup();
   return CStatus::OK;
}

// Update =====================================================
XSIPLUGINCALLBACK CStatus sn_null2surface_op_Update( CRef& in_ctxt )
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

// PPG Event ==================================================
XSIPLUGINCALLBACK CStatus sn_null2surface_op_PPGEvent( const CRef& in_ctxt )
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
