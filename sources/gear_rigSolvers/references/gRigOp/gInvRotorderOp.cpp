#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// INVERSE ROT ORDER OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gInvRotorderOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"Rotorder",CValue::siInt4,siPersistable|siAnimatable,L"",L"",0l,0l,5l,0l,5l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gInvRotorderOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gInvRotorderOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	long iRotorder = ctxt.GetParameterValue(L"Rotorder");
	long iOut = 0;

	if(iRotorder == 0)
		iOut = 5;
	else if (iRotorder == 1)
		iOut = 3;
	else if (iRotorder == 2)
		iOut = 4;
	else if (iRotorder == 3)
		iOut = 1;
	else if (iRotorder == 4)
		iOut = 2;
	else if (iRotorder == 5)
		iOut = 0;

	OutputPort Out = ctxt.GetOutputPort();
	Out.PutValue(iOut);

	return CStatus::OK;
}
