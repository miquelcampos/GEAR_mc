#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// ROLL OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gRollOp_Define( CRef& in_ctxt )
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
	oPDef = oFactory.CreateParamDef(L"Roll",CValue::siFloat,siPersistable|siAnimatable,L"",L"",0l,0l,1l,0l,1l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gRollOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gRollOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	float dPerc = ctxt.GetParameterValue(L"Percentage");
	float dRoll = ctxt.GetParameterValue(L"Roll");

	KinematicState kA(ctxt.GetInputValue(0));
	CTransformation tA(kA.GetTransform());

	KinematicState kB(ctxt.GetInputValue(1));
	CTransformation tB(kB.GetTransform());

	Primitive oCrvPrim(ctxt.GetInputValue(2));
	NurbsCurveList oCrvList(oCrvPrim.GetGeometry());
	NurbsCurve oCurve(oCrvList.GetCurves().GetItem(0));

	KinematicState kCurve(ctxt.GetInputValue(3));
	CTransformation tCurve(kCurve.GetTransform());

	CQuaternion qA(tA.GetRotationQuaternion());
	CQuaternion qB(tB.GetRotationQuaternion());

	qA.Normalize();
	qB.Normalize();

	// Evaluate From Curve -------------------------------------------------
	CVector3 vPos,vTan,vNorm,vBiNorm;
	oCurve.EvaluatePositionFromPercentage(dPerc,vPos,vTan,vNorm,vBiNorm);

	// Position ------------------------------------------------------------
	
	vPos.MulByMatrix4InPlace(tCurve.GetMatrix4());

	// Rotation ------------------------------------------------------------
	CQuaternion qOut;
	qOut.Slerp(qA, qB, dRoll);

	CMatrix3 mRot;
	mRot.SetFromQuaternion(qOut);

	CVector3 vUp(0,0,-1);
	vUp.MulByMatrix3InPlace(mRot);
	
	CMatrix3 m3Crv = tCurve.GetRotationMatrix3();
	vTan.MulByMatrix3InPlace(m3Crv);
	vTan.NormalizeInPlace();

	CVector3 vSide;
	vSide.Cross(vTan, vUp);
	vSide.NormalizeInPlace();
	vUp.Cross(vTan, vSide);
	vUp.NormalizeInPlace();

	CMatrix3 m3Rot;
	m3Rot.Set(vTan.GetX(), vTan.GetY(), vTan.GetZ(),
				 vSide.GetX(), vSide.GetY(), vSide.GetZ(),
				 vUp.GetX(), vUp.GetY(), vUp.GetZ());

	// Out ------------------------------------------------------------
	CTransformation tOut;
	tOut.SetRotationFromMatrix3 (m3Rot);
	tOut.SetTranslation(vPos);

	KinematicState out(ctxt.GetOutputTarget());
	out.PutTransform( tOut );

	return CStatus::OK;
}
