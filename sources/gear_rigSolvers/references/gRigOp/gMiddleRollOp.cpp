#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// MIDDLE ROLL OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gMiddleRollOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"Percentage",CValue::siFloat,siPersistable|siAnimatable,L"",L"",0l,0l,100l,0l,100l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gMiddleRollOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gMiddleRollOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	float dPerc = ctxt.GetParameterValue(L"Percentage");

	KinematicState kJntCtrl(ctxt.GetInputValue(0));
	CTransformation tJntCtrl(kJntCtrl.GetTransform());

	Primitive oCrvPrim(ctxt.GetInputValue(1));
	NurbsCurveList oCrvList(oCrvPrim.GetGeometry());
	NurbsCurve oCurve(oCrvList.GetCurves().GetItem(0));

	KinematicState kCurve(ctxt.GetInputValue(2));
	CTransformation tCurve(kCurve.GetTransform());

	// Evaluate From Curve -------------------------------------------------
	CVector3 vPos,vTan,vNorm,vBiNorm;
	oCurve.EvaluatePositionFromPercentage(dPerc,vPos,vTan,vNorm,vBiNorm);

	// Position ------------------------------------------------------------
	
	vPos.MulByMatrix4InPlace(tCurve.GetMatrix4());

	// Rotation ------------------------------------------------------------
	CRotation rRot = tJntCtrl.GetRotation();

	// Out ------------------------------------------------------------
	CTransformation tOut;
	tOut.SetRotation(rRot);
	tOut.SetTranslation(vPos);

	KinematicState out(ctxt.GetOutputTarget());
	out.PutTransform( tOut );

	return CStatus::OK;
}
