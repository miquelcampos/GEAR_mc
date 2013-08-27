#include "gRigOp.h"

///////////////////////////////////////////////////////////////
// SLERP OP 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gLipContactOp_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	oCustomOperator = ctxt.GetSource();
	oPDef = oFactory.CreateParamDef(L"Thickness",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,0l,100l,0l,100l);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"Contact",CValue::siDouble,siPersistable|siAnimatable,L"",L"",0l,-1l,1l,-1l,1l);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);
	return CStatus::OK;
}

// Init =======================================================
CStatus gLipContactOp_Init( CRef& in_ctxt )
{
	Application app;
	OperatorContext ctxt( in_ctxt );

	return CStatus::OK;
}

// Update =====================================================
CStatus gLipContactOp_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// Inputs --------------------------------------------------------------
	double dThickness = ctxt.GetParameterValue(L"Thickness");
	double dContact = ctxt.GetParameterValue(L"Contact");
	
	KinematicState kA(ctxt.GetInputValue(0));
	CTransformation tA(kA.GetTransform());

	KinematicState kB(ctxt.GetInputValue(1));
	CTransformation tB(kB.GetTransform());

	KinematicState kRef(ctxt.GetInputValue(2));
	CTransformation tRef(kRef.GetTransform());

	CVector3 vA = tA.GetTranslation();
	CVector3 vB = tB.GetTranslation();

	CVector3 vRefA = MapWorldPositionToObjectSpace(tRef, vA);
	CVector3 vRefB = MapWorldPositionToObjectSpace(tRef, vB);

	double dValue = 0;
	if( vRefB.GetY() > vRefA.GetY() - dThickness)
		dValue = (vRefB.GetY() - vRefA.GetY() + (dThickness))* dContact;

	// OutPut
	OutputPort Out = ctxt.GetOutputPort();
	Out.PutValue(dValue);
	return CStatus::OK;
}
