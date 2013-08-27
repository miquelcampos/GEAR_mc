/////////////////////////////////////////////////////
// GLOBAL
/////////////////////////////////////////////////////

/////////////////////////////////////////////////////
// XSI LOAD / UNLOAD PLUGIN
/////////////////////////////////////////////////////
function XSILoadPlugin(in_reg)
{

    in_reg.Author = "Jeremie Passerin";
    in_reg.Name = "gear_rotationToPose";
    in_reg.Email = "";
    in_reg.URL = "";
    in_reg.Major = 1;
    in_reg.Minor = 0;
    
    // Operators
    in_reg.RegisterOperator("gear_rotationToPose");

    return true;
}

function XSIUnloadPlugin(in_reg)
{
	var pluginName = in_reg.Name;
	LogMessage(pluginName + " has been unloaded.", siVerbose);

	return true;
}
/////////////////////////////////////////////////////
// ROTATION TO PARAMETER DRIVER
/////////////////////////////////////////////////////
// ==================================================
function gear_rotationToPose_Define(ctxt)
{
	var op = ctxt.Source;

	var pdef = XSIFactory.CreateParamDef("slices", siInt4, 0, siPersistable |siReadOnly,"","",8,0,1000,0,1000);
	op.AddParameter(pdef);
    var pdef = XSIFactory.CreateParamDef("axis", siString, 0, siPersistable, "", "", "x", null, null, null, null);
    op.AddParameter(pdef);
    var pdef = XSIFactory.CreateParamDef("offset", siDouble, 0, siPersistable, "", "",0, 0, 360, 0, 360);
    op.AddParameter(pdef);

	op.AlwaysEvaluate = false;
	op.Debug = 0;

    return true;
}

// ==================================================
function gear_rotationToPose_DefineLayout(ctxt)
{
    layout = ctxt.Source;
    layout.Clear();

    axisItems = ["X", "x", "Y", "y", "Z", "z"];

    layout.AddGroup("Slices");
    layout.AddItem("slices", "Count");
    layout.EndGroup();

    layout.AddGroup("Axis");
    item = layout.AddEnumControl("axis", axisItems, "Axis", siControlCombo);
    item = layout.AddItem("offset", "Offset Angle");
    layout.EndGroup();
}

// ==================================================
function gear_rotationToPose_Update(ctxt)
{
    slices = ctxt.GetParameterValue("slices");

    aData = ctxt.UserData

    if (!aData || aData[0].length >= slices)
    {
        // ------------------------------------------
        // Inputs
        axis = ctxt.GetParameterValue("axis");
        offset = ctxt.GetParameterValue("offset");
        sliceSize = 2*Math.PI/slices;
        
        parent_rot = ctxt.GetInputValue(0, 0, 0).Transform.Rotation;
        ctrl_rot   = ctxt.GetInputValue(1, 0, 0).Transform.Rotation;

        parent_mat3 = XSIMath.CreateMatrix3();
        ctrl_mat3 = XSIMath.CreateMatrix3();

        parent_rot.GetMatrix3(parent_mat3);
        ctrl_rot.GetMatrix3(ctrl_mat3);

        parent_mat3.InvertInPlace();

        // ------------------------------------------
        // Arrow position
        if (axis == "x")
        {
            arrow = XSIMath.CreateVector3(1,0,0);
            ref = XSIMath.CreateVector3(0,1,0);
        }
        else if (axis == "y")
        {
            arrow = XSIMath.CreateVector3(0,1,0);
            ref = XSIMath.CreateVector3(0,0,1);
        }
        else if (axis == "z")
        {
            arrow = XSIMath.CreateVector3(0,0,1);
            ref = XSIMath.CreateVector3(1,0,0);
        }
        
        // offset
        r = XSIMath.CreateRotation()
        r.SetFromAxisAngle(arrow, XSIMath.DegreesToRadians(offset))
        ref.MulByRotationInPlace(r)
        
        arrow.MulByMatrix3InPlace(ctrl_mat3);
        arrow.MulByMatrix3InPlace(parent_mat3);
        
        if (axis == "x")
            flat_arrow = XSIMath.CreateVector3(0, arrow.Y, arrow.Z);
        else if (axis == "y")
            flat_arrow = XSIMath.CreateVector3(arrow.X, 0, arrow.Z);
        else if (axis == "z")
            flat_arrow = XSIMath.CreateVector3(arrow.X, arrow.Y, 0);

        angle = ref.Angle(flat_arrow);

        // ------------------------------------------
        // Angle
        cross = XSIMath.CreateVector3();
        cross.Cross(ref, flat_arrow);
        if (axis == "x")
            d = cross.Dot(XSIMath.CreateVector3(1,0,0));
        else if (axis == "y")
            d = cross.Dot(XSIMath.CreateVector3(0,1,0));
        else if (axis == "z")
            d = cross.Dot(XSIMath.CreateVector3(0,0,1));
        if (d>0)
            angle = (2*Math.PI - angle)%(2*Math.PI);

        // ------------------------------------------
        // Range
        index = parseInt(angle/sliceSize)%slices;
        average = 1-(angle-index*sliceSize)/sliceSize;

        aValues = new Array();
        for (i=0; i<slices; i++)
            aValues.push(0);

        // NORMALIZED
        if (flat_arrow.Length() > 1.0e-12)
            norm = 1-(arrow.Angle(flat_arrow)/(XSIMath.PI*.5));
        else
            norm = 0
        
        aValues[index] = average * norm;
        aValues[(index+1)%slices] = (1-average) * norm;

        aData = [[], aValues];
    }

    // ------------------------------------------
    // Output
    OutPort = ctxt.OutputPort;

    // When scrubling an Input, operator is called only once (even with four outputs)
    // With this method, I'm sure that my operator will be recomputed everytimes, all the ports have been evaluated.
    if (aData[0].toString().indexOf(OutPort.Name) == -1)
        aData[0].push(OutPort.Name);

    OutPort.Value = aData[1][OutPort.Index-2];

    aData[0] += 1;
    ctxt.UserData = aData;
}