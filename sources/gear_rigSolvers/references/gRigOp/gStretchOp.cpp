#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// STRETCH OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gStretchOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"RestLength",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1l,0l,100l,0l,100l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"EffectorDist",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1l,0l,100l,0l,100l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Blend",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1l,0l,1l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Scale",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1l,0l,10l,0l,2l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"MaxStretch",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1l,1l,10l,1l,2l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Reverse",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1l,0l,1l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"SoftDist",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1l,0l,1l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gStretchOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gStretchOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	double dRestLength = ctxt.GetParameterValue(L"RestLength");
	double dEffDist = ctxt.GetParameterValue(L"EffectorDist");
	double dBlend = ctxt.GetParameterValue(L"Blend");
	double dScale = ctxt.GetParameterValue(L"Scale");
	double dMaxStretch = ctxt.GetParameterValue(L"MaxStretch");
	double dReverse = ctxt.GetParameterValue(L"Reverse");
	double dSoftDist = ctxt.GetParameterValue(L"SoftDist");

	// FK Par --------------------------------------------------------------
	double dFKLength = dRestLength * dScale;

	// IK Part --------------------------------------------------------------
	// Soft IK
	double dSoftScale 	= 1.0;
	double da			= dRestLength * dScale - dSoftDist;

	if( dEffDist > da )
	{
		double newlen	= dSoftDist * (1.0 - exp(-(dEffDist -da)/dSoftDist)) + da;
		dSoftScale = (dEffDist / newlen);
		if( dSoftScale > dMaxStretch )
			dSoftScale = dMaxStretch;
	}
	double dIKLength = dRestLength * dScale * dSoftScale;
	
	// Reverse IK
	if( dEffDist < dIKLength )
	{
		double dReverse2;
		if (dReverse > 0.5)
			dReverse2 =  abs(1 - dReverse);
		else
			dReverse2 = dReverse;
		dIKLength  = dEffDist  * dReverse2 * 2 + dIKLength *  abs((dReverse -0.5)*2);
	}

	// Blend --------------------------------------------------------------
	
	double dLength = (dIKLength * dBlend) + (dFKLength * (1-dBlend));

	OutputPort Out = ctxt.GetOutputPort();
	Out.PutValue(dLength);

	return CStatus::OK;
}
