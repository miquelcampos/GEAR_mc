#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// LEG ROLL OP
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gLegRollOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"RestLength",CValue::siDouble,siPersistable,L"",L"",0l,0l,1000l,0l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"StretchLength",CValue::siDouble,siPersistable,L"",L"",0l,0l,1000l,0l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Offset",CValue::siDouble,siPersistable,L"",L"",0l,0l,1000l,0l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gLegRollOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gLegRollOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	double dRestLength = ctxt.GetParameterValue(L"RestLength");
	double dStretchLength = ctxt.GetParameterValue(L"StretchLength");
	double dOffset = ctxt.GetParameterValue(L"Offset");

	KinematicState kA(ctxt.GetInputValue(0));
	CTransformation tA(kA.GetTransform());

	KinematicState kB(ctxt.GetInputValue(1));
	CTransformation tB(kB.GetTransform());
	
	KinematicState kC(ctxt.GetInputValue(2));
	CTransformation tC(kC.GetTransform());

	CVector3 vA = tA.GetTranslation();
	CVector3 vB = tB.GetTranslation();
	CVector3 vC = tC.GetTranslation();

	CVector3 vDir;
	vDir.Sub(vA, vB);

	double dLength = vDir.GetLength();
	vDir.NormalizeInPlace();

	// Pos ---------------------------------------------------------------
	CVector3 vPos;
	vPos.Add(vA, vB);
	double d = vPos.GetLength();
	vPos.NormalizeInPlace();
	vPos.ScaleInPlace(d*.5);

	// Direction Offset -------------------------------------------------
	CVector3 vUp, vNormal, vBiNormal;
	vUp.Sub(vC, vPos);
	vUp.NormalizeInPlace();
	
	vNormal.Cross(vDir, vUp);
	vBiNormal.Cross(vDir, vNormal);

	// Offset -----------------------------------------------------------
	if( dLength < dRestLength)
		d = dLength / dRestLength;
	else
		d = 1 - ((dLength - dRestLength)/(dStretchLength - dRestLength));

	if(d < 0)
		d = 0;

	vBiNormal.ScaleInPlace( d * -dOffset );
	vPos.AddInPlace(vBiNormal);

	// Out --------------------------------------------------------------
	CTransformation tOut;
	tOut.SetTranslation(vPos);

	KinematicState out(ctxt.GetOutputTarget());
	out.PutTransform( tOut );

	return CStatus::OK;
}
