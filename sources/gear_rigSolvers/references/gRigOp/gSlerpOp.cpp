#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// SLERP OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gSlerpOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"Ratio",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,1l,0l,1l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gSlerpOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gSlerpOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	double dRatio = ctxt.GetParameterValue(L"Ratio");
	
	KinematicState k(ctxt.GetInputValue(0));
	CTransformation t(k.GetTransform());

	KinematicState kA(ctxt.GetInputValue(1));
	CTransformation tA(kA.GetTransform());

	KinematicState kB(ctxt.GetInputValue(2));
	CTransformation tB(kB.GetTransform());

	CQuaternion qA(tA.GetRotationQuaternion());
	CQuaternion qB(tB.GetRotationQuaternion());

	qA.Normalize();
	qB.Normalize();

	// Rotation ------------------------------------------------------------
	CQuaternion qOut;
	qOut.Slerp(qA, qB, dRatio);

	// Out ------------------------------------------------------------
	t.SetRotationFromQuaternion (qOut);

	KinematicState out(ctxt.GetOutputTarget());
	out.PutTransform( t );

	return CStatus::OK;
}
