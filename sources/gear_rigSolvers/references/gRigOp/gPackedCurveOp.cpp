#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// PACKED CURVE OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gPackedCurveOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"RestLength",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1000l,0l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);
	
	oPDef = oFactory.CreateParamDef(L"Ori_X",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,-1000l,1000l,-1000l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Ori_Y",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,-1000l,1000l,-1000l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Ori_Z",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,-1000l,1000l,-1000l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Offset",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,-1l,1l,-1000l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gPackedCurveOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gPackedCurveOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs -------------------------------------------------
	double dRestLength = ctxt.GetParameterValue(L"RestLength");
	double dOri_X = ctxt.GetParameterValue(L"Ori_X");
	double dOri_Y = ctxt.GetParameterValue(L"Ori_Y");
	double dOri_Z = ctxt.GetParameterValue(L"Ori_Z");
	double dOffset = ctxt.GetParameterValue(L"Offset");
	
	Primitive oCrvPrim(ctxt.GetInputValue(0));
	NurbsCurveList oCrvGeo(oCrvPrim.GetGeometry());
	NurbsCurve oCurve = oCrvGeo.GetCurves().GetItem(0);
	double dLength;
	oCurve.GetLength(dLength);

	KinematicState kCurve(ctxt.GetInputValue(1));
	CTransformation tCurve(kCurve.GetTransform());
	CMatrix4 mCurve = tCurve.GetMatrix4();

	KinematicState kUpV(ctxt.GetInputValue(2));
	CTransformation tUpV(kUpV.GetTransform());
	CVector3 vUpV = tUpV.GetTranslation();

	// Initial Position -----------------------------------
	CPointRefArray aPoints(oCrvGeo.GetPoints());
	CVector3Array aPositionArray(aPoints.GetPositionArray());

	CVector3 vPosStart	= aPositionArray[0];

	CVector3 vPosOri;
	vPosOri.Set(dOri_X, dOri_Y, dOri_Z);

	// Length Factor --------------------------------------
	double dFactor = 0.0;

	if( dLength < dRestLength )
		dFactor = 1 - (dLength/ dRestLength);

	CVector3 vMidPos;
	vMidPos.Sub(vPosStart, vPosOri);
	vMidPos.ScaleInPlace(dFactor);

	CVector3 vOutPos;
	vOutPos.Add(vPosOri, vMidPos);

	// Offset --------------------------------------------
	vUpV = MapWorldPositionToObjectSpace(tCurve, vUpV);

	CVector3 vDir;
	vDir.Sub(vUpV, vPosOri);
	vDir.NormalizeInPlace();
	
	vDir.ScaleInPlace(dOffset);
	
	vOutPos.AddInPlace(vDir);


	// Output --------------------------------------------
	aPositionArray[1] = vOutPos;

	Primitive OutPrim = ctxt.GetOutputTarget() ;
	OutPrim.GetGeometry().GetPoints().PutPositionArray( aPositionArray ) ;

	return CStatus::OK;
}
