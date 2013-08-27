#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// U TO PERC OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gUtoPercOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"U",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1000l,0l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gUtoPercOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gUtoPercOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	double dU = ctxt.GetParameterValue(L"U");
	
	Primitive oCrvPrim(ctxt.GetInputValue(0));
	NurbsCurveList oCrvList(oCrvPrim.GetGeometry());
	NurbsCurve oCurve(oCrvList.GetCurves().GetItem(0));

	double dPerc;
	oCurve.GetPercentageFromU(dU, dPerc);

	OutputPort Out = ctxt.GetOutputPort();
	Out.PutValue(dPerc);

	return CStatus::OK;
}
