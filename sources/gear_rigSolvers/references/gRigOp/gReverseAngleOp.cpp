#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// REVERSE A?GLE OP
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gReverseAngleOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"Reverse",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1l,0l,1l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"OriginalPrefRot",CValue::siDouble,siPersistable|siAnimatable,L"",L"",-10l,-360l,360l,-180l,180l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gReverseAngleOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gReverseAngleOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	double dReverse				= ctxt.GetParameterValue(L"Reverse");
	double dOriginalPrefRot	= ctxt.GetParameterValue(L"OriginalPrefRot");
	
	double dOut = - ( dReverse - .5 ) * 2 * dOriginalPrefRot;

	OutputPort Out = ctxt.GetOutputPort();
	Out.PutValue(dOut);

	return CStatus::OK;
}
