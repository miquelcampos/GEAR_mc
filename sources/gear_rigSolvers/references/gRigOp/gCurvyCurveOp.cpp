#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// CURVY CURVE OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gCurvyCurveOp_Define( CRef& in_ctxt )
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
	oPDef = oFactory.CreateParamDef(L"Value",CValue::siDouble,siPersistable|siAnimatable,L"",L"",1l,-10l,10l,-1000l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Offset",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,-5l,5l,-1000l,1000l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gCurvyCurveOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gCurvyCurveOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	///////////////////////////////////////////////////////////
	// Inputs
	///////////////////////////////////////////////////////////
	// Connections
	Primitive oCrvPrim(ctxt.GetInputValue(0));
	NurbsCurveList oCrvGeo(oCrvPrim.GetGeometry());

	KinematicState kCurve(ctxt.GetInputValue(1));
	CTransformation tCurve(kCurve.GetTransform());
	CMatrix4 mCurve = tCurve.GetMatrix4();

	KinematicState kUpV(ctxt.GetInputValue(2));
	CTransformation tUpV(kUpV.GetTransform());
	CVector3 vUpV = tUpV.GetTranslation();

	NurbsCurve oCurve = oCrvGeo.GetCurves().GetItem(0);
	double dLength;
	oCurve.GetLength(dLength);

	// Variables
	double dRestLength = ctxt.GetParameterValue(L"RestLength");
	double dValue = ctxt.GetParameterValue(L"Value");
	double dOffset = ctxt.GetParameterValue(L"Offset");
	

	// Initial Position -----------------------------------
	CPointRefArray aPoints(oCrvGeo.GetPoints());
	CVector3Array aPositionArray(aPoints.GetPositionArray());

	CVector3 vPosStart	= aPositionArray[0];
	CVector3 vPosEnd	= aPositionArray[2];

	CVector3 vPosMid;
	vPosMid.Add(vPosStart, vPosEnd);
	vPosMid.ScaleInPlace(.5);

	// Length Factor --------------------------------------
	double dFactor = 0.0;

	if( dLength < dRestLength )
		dFactor = 1 - (dLength/ dRestLength);

	// UpVector Direction --------------------------------
	vUpV = MapWorldPositionToObjectSpace(tCurve, vUpV);

	CVector3 vX, vY, vZ;
	vX.Sub(vPosEnd, vPosStart);
	vX.NormalizeInPlace();

	vY.Sub(vUpV, vPosMid);
	vY.NormalizeInPlace();

	vZ.Cross(vX, vY);

	vY.Cross(vZ, vX);
	vY.NormalizeInPlace();
	vY.ScaleInPlace(dValue * dFactor);

	vPosMid.AddInPlace(vY);

	vX.ScaleInPlace(dOffset * dFactor);
	vPosMid.AddInPlace(vX);


	// Output -----------------------------------------
	aPositionArray[1] = vPosMid;

	Primitive OutPrim = ctxt.GetOutputTarget() ;
	OutPrim.GetGeometry().GetPoints().PutPositionArray( aPositionArray ) ;

	return CStatus::OK;
}
