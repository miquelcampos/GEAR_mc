#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// VOLUME OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gVolumeOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"Stretch",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,10l,0l,2l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Squash",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,10l,0l,2l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"RestLength",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1000l,0l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Axis",CValue::siInt4,siPersistable|siAnimatable,L"",L"",0l,0l,2l,0l,2l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gVolumeOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gVolumeOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	double dStretch = ctxt.GetParameterValue(L"Stretch");
	double dSquash = ctxt.GetParameterValue(L"Squash");
	double dRestLength = ctxt.GetParameterValue(L"RestLength");
	double iAxis = ctxt.GetParameterValue(L"Axis");

	Primitive oCrvPrim(ctxt.GetInputValue(0));
	NurbsCurveList oCrvList(oCrvPrim.GetGeometry());
	NurbsCurve oCurve(oCrvList.GetCurves().GetItem(0));

	KinematicState kCurve(ctxt.GetInputValue(1));
	CTransformation tCurve(kCurve.GetTransform());

	// Squash / Stretch ------------------------------------------------
	CVector3 vScale(tCurve.GetScaling());
	
	double dLength;
	oCurve.GetLength(dLength);

	double dDiff = 1 - dRestLength / dLength;
	
	if(dDiff > 0)
	{
		dStretch = 1 - dDiff*dStretch;
		if(iAxis == 0)
			vScale.Set(vScale.GetX(), dStretch*vScale.GetY(), dStretch*vScale.GetZ());
		else if(iAxis == 1)
			vScale.Set(dStretch*vScale.GetX(), vScale.GetY(), dStretch*vScale.GetZ());
		else if(iAxis == 2)
			vScale.Set(dStretch*vScale.GetX(), dStretch*vScale.GetY(), vScale.GetZ());
	}
	else
	{
		dSquash = 1 - dDiff*dSquash;
		if(iAxis == 0)
			vScale.Set(vScale.GetX(), dSquash*vScale.GetY(), dSquash*vScale.GetZ());
		else if(iAxis == 1)
			vScale.Set(dSquash*vScale.GetX(), vScale.GetY(), dSquash*vScale.GetZ());
		else if(iAxis == 2)
			vScale.Set(dSquash*vScale.GetX(), dSquash*vScale.GetY(), vScale.GetZ());
	}

	// Out ------------------------------------------------------------

	OutputPort Out = ctxt.GetOutputPort();
	
	if (Out.GetName() == L"Outsclx")
		Out.PutValue(vScale.GetX());
	else if (Out.GetName() == L"Outscly")
		Out.PutValue(vScale.GetY());
	else if (Out.GetName() == L"Outsclz")
		Out.PutValue(vScale.GetZ());

	return CStatus::OK;
}
