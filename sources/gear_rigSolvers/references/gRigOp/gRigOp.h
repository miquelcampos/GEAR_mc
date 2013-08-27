#include <xsi_application.h>
#include <xsi_pluginregistrar.h>
#include <xsi_context.h>
#include <xsi_status.h>
#include <xsi_customoperator.h>
#include <xsi_operatorcontext.h>
#include <xsi_ppglayout.h>
#include <xsi_ppgeventcontext.h>
#include <xsi_selection.h>
#include <xsi_command.h>
#include <xsi_factory.h>
#include <xsi_primitive.h>
#include <xsi_kinematics.h>
#include <xsi_outputport.h>

#include <xsi_x3dobject.h>
#include <xsi_argument.h>
#include <xsi_matrix4.h>
#include <xsi_preferences.h>

#include <xsi_nurbscurvelist.h> 
#include <xsi_nurbscurve.h>
#include <xsi_point.h>

using namespace XSI; 
using namespace XSI::MATH;

// CurvyCurve Op -------------------------------------
XSIPLUGINCALLBACK CStatus gCurvyCurveOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gCurvyCurveOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gCurvyCurveOp_Update( CRef& in_ctxt );

// InvRotorder Op -------------------------------------
XSIPLUGINCALLBACK CStatus gInvRotorderOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gInvRotorderOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gInvRotorderOp_Update( CRef& in_ctxt );

// LegRoll Op ----------------------------------------
XSIPLUGINCALLBACK CStatus gLegRollOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gLegRollOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gLegRollOp_Update( CRef& in_ctxt );

// LipContact Op -------------------------------------
XSIPLUGINCALLBACK CStatus gLipContactOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gLipContactOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gLipContactOp_Update( CRef& in_ctxt );

// MiddleRoll Op -------------------------------------
XSIPLUGINCALLBACK CStatus gMiddleRollOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gMiddleRollOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gMiddleRollOp_Update( CRef& in_ctxt );

// PackedCurve Op -------------------------------------
XSIPLUGINCALLBACK CStatus gPackedCurveOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gPackedCurveOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gPackedCurveOp_Update( CRef& in_ctxt );

// ReverseAngle Op -------------------------------------
XSIPLUGINCALLBACK CStatus gReverseAngleOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gReverseAngleOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gReverseAngleOp_Update( CRef& in_ctxt );

// Roll Op -------------------------------------
XSIPLUGINCALLBACK CStatus gRollOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gRollOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gRollOp_Update( CRef& in_ctxt );

// Stretch Op ----------------------------------
XSIPLUGINCALLBACK CStatus gStretchOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gStretchOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gStretchOp_Update( CRef& in_ctxt );

// Stretch Op 2 ----------------------------------
XSIPLUGINCALLBACK CStatus gStretchOp2_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gStretchOp2_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gStretchOp2_Update( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gStretchOp2Multi_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gStretchOp2Multi_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gStretchOp2Multi_Update( CRef& in_ctxt );

// UtoPerc Op -------------------------------------
XSIPLUGINCALLBACK CStatus gUtoPercOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gUtoPercOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gUtoPercOp_Update( CRef& in_ctxt );

// Volumic Op -------------------------------------
XSIPLUGINCALLBACK CStatus gVolumeOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gVolumeOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gVolumeOp_Update( CRef& in_ctxt );


// InvRotorder Op -------------------------------------
XSIPLUGINCALLBACK CStatus gSlerpOp_Define( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gSlerpOp_Init( CRef& in_ctxt );
XSIPLUGINCALLBACK CStatus gSlerpOp_Update( CRef& in_ctxt );