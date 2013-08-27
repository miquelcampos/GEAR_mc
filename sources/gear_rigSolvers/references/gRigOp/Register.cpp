#include "gRigOp.h"

XSIPLUGINCALLBACK CStatus XSILoadPlugin( PluginRegistrar& reg )
{
	reg.PutAuthor(L"Jeremie Passerin");
	reg.PutEmail(L"geerem@hotmail.com.com");
	reg.PutName(L"gRigOp");
	reg.PutVersion(1, 0);
	reg.RegisterOperator(L"gCurvyCurveOp");
	reg.RegisterOperator(L"gInvRotorderOp");
	reg.RegisterOperator(L"gLegRollOp");
	reg.RegisterOperator(L"gLipContactOp");
	reg.RegisterOperator(L"gMiddleRollOp");
	reg.RegisterOperator(L"gPackedCurveOp");
	reg.RegisterOperator(L"gReverseAngleOp");
	reg.RegisterOperator(L"gRollOp");
	reg.RegisterOperator(L"gStretchOp");
	reg.RegisterOperator(L"gStretchOp2");
	reg.RegisterOperator(L"gStretchOp2Multi");
	reg.RegisterOperator(L"gUtoPercOp");
	reg.RegisterOperator(L"gVolumeOp");
	reg.RegisterOperator(L"gSlerpOp");
	return CStatus::OK;
}

XSIPLUGINCALLBACK CStatus XSIUnloadPlugin( const PluginRegistrar& in_reg )
{
	CString strPluginName;
	strPluginName = in_reg.GetName();
	Application().LogMessage(strPluginName + L" has been unloaded.",siVerboseMsg);
	return CStatus::OK;
}