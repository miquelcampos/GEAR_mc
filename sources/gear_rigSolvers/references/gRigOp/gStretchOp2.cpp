#include "gRigOp.h"

/////////////////////////////////////////////////////////////////////////////////////////////
// USER DATA CLASS
/////////////////////////////////////////////////////////////////////////////////////////////
struct OpUserData
{

	double index;
	CTransformation t;
	double dLength0;
	double dLength1;
	double dPrefRot;

	OpUserData()
			{
	}
} ;

///////////////////////////////////////////////////////////////
// STRETCH OP 2 
///////////////////////////////////////////////////////////////

// Define =====================================================
CStatus gStretchOp2_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	// Initial Settings (Read Only)
	oPDef = oFactory.CreateParamDef(L"rest0",CValue::siDouble,siPersistable | siReadOnly,L"",L"",0.0,0,1000.0,0,10.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"rest1",CValue::siDouble,siPersistable | siReadOnly,L"",L"",0.0,0,1000.0,0,10.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"prefrot",CValue::siDouble,siPersistable | siReadOnly,L"",L"",0,-9999,9999,-90,90);
	oCustomOperator.AddParameter(oPDef,oParam);

	// Animatable Parameters
	oPDef = oFactory.CreateParamDef(L"scale0",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,0,1000.0,0,2.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"scale1",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,0,1000.0,0,2.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"maxstretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,1.0,1000.0,1.0,2.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"soft",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0.0,4.0,0.0,1.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"slide",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.5,0.0,1.0,0.0,1.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"reverse",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0.0,1.0,0.0,1.0);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);

	return CStatus::OK;
}


// DefineLayout =============================================================================
CStatus gStretchOp2_DefineLayout( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	PPGLayout oLayout;
	PPGItem oItem;
	oLayout = ctxt.GetSource();
	oLayout.Clear();

    oLayout.AddGroup(L"Init");
    oLayout.AddItem(L"rest0", L"Bone 0 Length");
    oLayout.AddItem(L"rest1", L"Bone 1 Length");
    oLayout.AddItem(L"prefrot", L"Bone 1 Rot");
    oLayout.EndGroup();

    oLayout.AddGroup(L"Animate");
    oItem = oLayout.AddItem(L"scale0", L"Bone 0 Scale");
    oItem = oLayout.AddItem(L"scale1", L"Bone 1 Scale");
    oItem = oLayout.AddItem(L"maxstretch", L"Max Stretch");
    oItem = oLayout.AddItem(L"soft", L"Softness");
    oItem = oLayout.AddItem(L"slide", L"Slide");
    oItem = oLayout.AddItem(L"reverse", L"Reverse");
    oLayout.EndGroup();

	return CStatus::OK;
}

// Update =================================================================================
CStatus gStretchOp2_Update( CRef& in_ctxt )
{
	OperatorContext ctxt( in_ctxt );

	// User Datas ------------------------------------
	CValue::siPtrType pUserData = ctxt.GetUserData();
	OpUserData* pOpState = (OpUserData*)pUserData;

	if ( pOpState == NULL || pOpState->index >= 4)
	{
		// First time called
		pOpState = new OpUserData();
		ctxt.PutUserData( (CValue::siPtrType)pOpState );

		// Inputs ---------------------------------------
		KinematicState kRoot(ctxt.GetInputValue(0));
		KinematicState kCtrl(ctxt.GetInputValue(1));
		CTransformation tRoot(kRoot.GetTransform());
		CTransformation tCtrl(kCtrl.GetTransform());
		CVector3 vRoot = tRoot.GetTranslation();
		CVector3 vCtrl = tCtrl.GetTranslation();
		CMatrix4 mRoot = tRoot.GetMatrix4();
		CMatrix4 mRootNeg;
		mRootNeg.Invert(mRoot);

		double dRest0      = ctxt.GetParameterValue(L"rest0");
		double dRest1      = ctxt.GetParameterValue(L"rest1");
		double dPrefRot    = ctxt.GetParameterValue(L"prefrot");
		double dScale0     = ctxt.GetParameterValue(L"scale0");
		double dScale1     = ctxt.GetParameterValue(L"scale1");
		double dSoftness   = ctxt.GetParameterValue(L"soft");
		double dMaxStretch = ctxt.GetParameterValue(L"maxstretch");
		double dSlide      = ctxt.GetParameterValue(L"slide");
		double dReverse    = ctxt.GetParameterValue(L"reverse");

		// Distance with MaxStretch ---------------------
		double dRestLength = dRest0 * dScale0 + dRest1 * dScale1;
		CVector3 vDistance;
		vDistance.MulByMatrix4(vCtrl, mRootNeg);
		double dDistance = vDistance.GetLength();
		double dDistance2 = dDistance;
		if (dDistance > (dRestLength * dMaxStretch))
		{
			vDistance.NormalizeInPlace();
			vDistance.ScaleInPlace(dRestLength * dMaxStretch);
			dDistance = dRestLength * dMaxStretch;
		}

		// Adapt Softness value to chain length --------
		dSoftness *= dRestLength*.1;

		// Stretch and softness ------------------------
		/// We use the real distance from root to controler to calculate the softness
		/// This way we have softness working even when there is no stretch
		double dStretch = dDistance/dRestLength;
		if (dStretch < 1)
			dStretch = 1;
		double da = dRestLength - dSoftness;
		if (dSoftness > 0 && dDistance2 > da)
		{
			double newlen = dSoftness*(1.0 - exp(-(dDistance2 -da)/dSoftness)) + da;
			dStretch = dDistance / newlen;
		}

		double dLength0 = dRest0 * dStretch * dScale0;
		double dLength1 = dRest1 * dStretch * dScale1;

		// Reverse -------------------------------------
		double d = dDistance/(dLength0 + dLength1);

		double dScale;
		if (dReverse < 0.5)
			dScale = 1-(dReverse*2 * (1-d));
		else
			dScale = 1-((1-dReverse)*2 * (1-d));

		dLength0 *= dScale;
		dLength1 *= dScale;

		dPrefRot = -(dReverse-0.5) * 2 * dPrefRot;

		// Slide ---------------------------------------
		double dAdd;
		if (dSlide < .5)
			dAdd = (dLength0 * (dSlide*2)) - (dLength0);
		else
			dAdd = (dLength1 * (dSlide*2)) - (dLength1);

		dLength0 += dAdd;
		dLength1 -= dAdd;

		// Effector Position ----------------------------
		CTransformation t;
		vDistance.MulByMatrix4(vDistance, mRoot);
		t.SetTranslation(vDistance);

		pOpState->index = 0;
		pOpState->t = t;
		pOpState->dLength0 = dLength0;
		pOpState->dLength1 = dLength1;
		pOpState->dPrefRot = dPrefRot;
	}

	// Outputs -------------------------------------
	CRef outputPortRef=ctxt.GetOutputPort();
	OutputPort OutPort(outputPortRef);

	// Effector Transform
	if (OutPort.GetIndex() == 2)
	{
		KinematicState kOut = ctxt.GetOutputTarget();
		kOut.PutTransform(pOpState->t);
	}
	// Bone 0 Length
	else if (OutPort.GetIndex() == 3)
	{
		OutPort.PutValue(pOpState->dLength0);
	}
	// Bone 1 Length
	else if (OutPort.GetIndex() == 4)
	{
		OutPort.PutValue(pOpState->dLength1);
	}
	// Bone 1 PrefRot
	else if (OutPort.GetIndex() == 5)
	{
		OutPort.PutValue(pOpState->dPrefRot);
	}

	pOpState->index += 1;

	return CStatus::OK;
}

/////////////////////////////////////////////////////////////////////////////////////////////
// SOFT IK MULTI (3 and more BONES CHAIN)
/////////////////////////////////////////////////////////////////////////////////////////////
// Define ===================================================================================
CStatus gStretchOp2Multi_Define( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	CustomOperator oCustomOperator;
	Parameter oParam;
	CRef oPDef;
	Factory oFactory = Application().GetFactory();
	oCustomOperator = ctxt.GetSource();

	// Initial Settings (Read Only)
	oPDef = oFactory.CreateParamDef(L"restlength",CValue::siDouble,siPersistable | siReadOnly,L"",L"",0.0,0,1000.0,0,10.0);
	oCustomOperator.AddParameter(oPDef,oParam);

	// Animatable Parameters
	oPDef = oFactory.CreateParamDef(L"scale",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,0,1000.0,0,2.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"maxstretch",CValue::siDouble,siPersistable | siAnimatable,L"",L"",1.0,1.0,1000.0,1.0,2.0);
	oCustomOperator.AddParameter(oPDef,oParam);
	oPDef = oFactory.CreateParamDef(L"soft",CValue::siDouble,siPersistable | siAnimatable,L"",L"",0.0,0.0,4.0,0.0,1.0);
	oCustomOperator.AddParameter(oPDef,oParam);

	oCustomOperator.PutAlwaysEvaluate(false);
	oCustomOperator.PutDebug(0);

	return CStatus::OK;
}

// DefineLayout =============================================================================
CStatus gStretchOp2Multi_DefineLayout( CRef& in_ctxt )
{
	Context ctxt( in_ctxt );
	PPGLayout oLayout;
	PPGItem oItem;
	oLayout = ctxt.GetSource();
	oLayout.Clear();

    oLayout.AddGroup(L"Init");
    oLayout.AddItem(L"restlength", L"Rest Length");
    oLayout.EndGroup();

    oLayout.AddGroup(L"Animate");
    oItem = oLayout.AddItem(L"scale", L"Scale");
    oItem = oLayout.AddItem(L"maxstretch", L"Max Stretch");
    oItem = oLayout.AddItem(L"soft", L"Softness");
    oLayout.EndGroup();


	return CStatus::OK;
}

// Update =============================================================================
CStatus gStretchOp2Multi_Update( CRef& in_ctxt )
{

	OperatorContext ctxt( in_ctxt );

		// User Datas ------------------------------------
		CValue::siPtrType pUserData = ctxt.GetUserData();
		OpUserData* pOpState = (OpUserData*)pUserData;

		if ( pOpState == NULL || pOpState->index >= 2)
		{
			// First time called
			pOpState = new OpUserData();
			ctxt.PutUserData( (CValue::siPtrType)pOpState );

			// Inputs ---------------------------------------
			KinematicState kRoot(ctxt.GetInputValue(0));
			KinematicState kCtrl(ctxt.GetInputValue(1));
			CTransformation tRoot(kRoot.GetTransform());
			CTransformation tCtrl(kCtrl.GetTransform());
			CVector3 vRoot = tRoot.GetTranslation();
			CVector3 vCtrl = tCtrl.GetTranslation();
			CMatrix4 mRoot = tRoot.GetMatrix4();
			CMatrix4 mRootNeg;
			mRootNeg.Invert(mRoot);

			double dRestLength = ctxt.GetParameterValue(L"restlength");
			double dScale      = ctxt.GetParameterValue(L"scale");
			double dSoftness   = ctxt.GetParameterValue(L"soft");
			double dMaxStretch = ctxt.GetParameterValue(L"maxstretch");

			// Distance with MaxStretch ---------------------
			dRestLength = dRestLength * dScale - .00001;
			CVector3 vDistance;
			vDistance.MulByMatrix4(vCtrl, mRootNeg);
			double dDistance = vDistance.GetLength();
			double dDistance2 = dDistance;
			if (dDistance > (dRestLength * dMaxStretch))
			{
				vDistance.NormalizeInPlace();
				vDistance.ScaleInPlace(dRestLength * dMaxStretch);
				dDistance = dRestLength * dMaxStretch;
			}

			Application app;
			app.LogMessage(L"dist : "+CString(dDistance));
			app.LogMessage(L"dist2 : "+CString(dDistance2));

			// Adapt Softness value to chain length --------
			dSoftness = dSoftness * dRestLength *.1;

			// Stretch and softness ------------------------
			/// We use the real distance from root to controler to calculate the softness
			/// This way we have softness working even when there is no stretch
			double dStretch = dDistance/dRestLength;
			if (dStretch < 1)
				dStretch = 1;
			double da = dRestLength - dSoftness;
			if (dSoftness > 0 && dDistance2 > da)
			{
				double newlen = dSoftness*(1.0 - exp(-(dDistance2 -da)/dSoftness)) + da;
				dStretch = dDistance / newlen;
			}

			double dScaleX = dStretch * dScale;
			app.LogMessage(L"scalex : "+CString(dScaleX));

			// Effector Position ----------------------------
			CTransformation t;
			vDistance.MulByMatrix4(vDistance, mRoot);
			t.SetTranslation(vDistance);

			pOpState->index = 0;
			pOpState->t = t;
			pOpState->dLength0 = dScaleX;
		}

	// Outputs -------------------------------------
	CRef outputPortRef=ctxt.GetOutputPort();
	OutputPort OutPort(outputPortRef);

	// Effector Transform
	if (OutPort.GetIndex() == 2)
	{
		KinematicState kOut = ctxt.GetOutputTarget();
		kOut.PutTransform(pOpState->t);
	}
	// Bone 0 Length
	else if (OutPort.GetIndex() == 3)
	{
		OutPort.PutValue(pOpState->dLength0);
	}

	pOpState->index += 1;

	return CStatus::OK;
}
