/*

    This file is part of GEAR.

    GEAR is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

    Author:     Helge Mathee, Jeremie Passerin      helge.mathee@gmx.net, geerem@hotmail.com
    Company:    Studio Nest (TM)
    Date:       2010 / 11 / 15

*/

function rollsplinekine_Update(In_UpdateContext, {inputs})
{
    splinekine_op_Update(In_UpdateContext, {inputs}, 1)
}

function splinekine_op_Update(In_UpdateContext, {inputs}, mode)
{

	count = In_UpdateContext.Parameters( "count" ).Value;

    pos = [];
    tangent = [];
    rot = [];
    roll = [];
    rotParent = [];
    scl = [];

    for (i=0;i<count;i++)
    {
        pos[i] = XSIMath.CreateVector3();
        tangent[i] = XSIMath.CreateVector3();
        rot[i] = XSIMath.CreateVector3();
        roll[i] = 0.0;
        rotParent[i] = XSIMath.CreateVector3();
        scl[i] = XSIMath.CreateVector3();
    }

    singleXF = XSIMath.CreateTransform();
    singleParentXF = XSIMath.CreateTransform();
    singleMat = XSIMath.CreateMatrix3();
    modelXF = XSIMath.CreateTransform();

    // ------------------------------------

    if(mode == 0) // simple 180 flipping interpolation
    {
        for(long i=0;i<count;i++)
        {
            singleXF = KinematicState(ctxt.GetInputValue(i)).GetTransform();
            singleMat = singleXF.GetRotationMatrix3();
            pos[i] = singleXF.GetTranslation();
            tangent[i].MulByMatrix3(CVector3(singleXF.GetSclX()*2.5,0,0),singleMat);
            rot[i] = singleXF.GetRotationXYZAngles();
            scl[i] = singleXF.GetScaling();
        }
        modelXF = KinematicState(ctxt.GetInputValue(count)).GetTransform();
    }
    else if(mode == 1) // local rotation X based roll
    {
        for(long i=0;i<count;i++)
        {
            singleParentXF = KinematicState(ctxt.GetInputValue(i*2+0)).GetTransform();
            singleXF = KinematicState(ctxt.GetInputValue(i*2+1)).GetTransform();
            roll[i] = singleXF.GetRotX();

            singleXF = MapObjectPoseToWorldSpace(singleParentXF,singleXF);
            singleMat = singleXF.GetRotationMatrix3();

            pos[i] = singleXF.GetTranslation();
            tangent[i].MulByMatrix3(CVector3(singleXF.GetSclX()*2.5,0,0),singleMat);
            rot[i] = singleParentXF.GetRotationXYZAngles();
            scl[i] = singleXF.GetScaling();
        }
        modelXF = KinematicState(ctxt.GetInputValue(count*2)).GetTransform();
    }

    double u = ctxt.GetParameterValue(L"u");
    bool resample = ctxt.GetParameterValue(L"resample");
    long subdiv = (LONG)ctxt.GetParameterValue(L"subdiv");
    bool absolute = ctxt.GetParameterValue(L"absolute");

    double step = 1.0 / max(1,count-1);
    int index1 = (int)min(count-2,u / step);
    int index2 = index1+1;
    int index1temp = index1;
    int index2temp = index2;
    double v = (u - step * double(index1)) / step;
    double vtemp = v;

    // calculate the bezier
    CVector3 bezierPos;
    CVector3 xAxis,yAxis,zAxis;
    if(!resample)
    {
        // straight bezier solve
        CVector3Array results = bezier4point(pos[index1],tangent[index1],pos[index2],tangent[index2],v);
        bezierPos = results[0];
        xAxis = results[1];
    }
    else if(!absolute)
    {
        CVector3Array presample(subdiv);
        CVector3Array presampletan(subdiv);
        CDoubleArray samplelen(subdiv);
        double samplestep = 1.0 / double(subdiv-1);
        double sampleu = samplestep;
        presample[0]  = pos[index1];
        presampletan[0]  = tangent[index1];
        CVector3 prevsample(presample[0]);
        CVector3 diff;
        samplelen[0] = 0;
        double overalllen = 0;
        CVector3Array results(2);
        for(long i=1;i<subdiv;i++,sampleu+=samplestep)
        {
            results = bezier4point(pos[index1],tangent[index1],pos[index2],tangent[index2],sampleu);
            presample[i] = results[0];
            presampletan[i] = results[1];
            diff.Sub(presample[i],prevsample);
            overalllen += diff.GetLength();
            samplelen[i] = overalllen;
            prevsample = presample[i];
        }
        // now as we have the
        sampleu = 0;
        for(long i=0;i<subdiv-1;i++,sampleu+=samplestep)
        {
            samplelen[i+1] = samplelen[i+1] / overalllen;
            if(v>=samplelen[i] && v <=  samplelen[i+1])
            {
                v = (v - samplelen[i]) / (samplelen[i+1] - samplelen[i]);
                bezierPos.LinearlyInterpolate(presample[i],presample[i+1],v);
                xAxis.LinearlyInterpolate(presampletan[i],presampletan[i+1],v);
                break;
            }
        }
    }
    else
    {
        CVector3Array presample(subdiv);
        CVector3Array presampletan(subdiv);
        CDoubleArray samplelen(subdiv);
        double samplestep = 1.0 / double(subdiv-1);
        double sampleu = samplestep;
        presample[0]  = pos[0];
        presampletan[0]  = tangent[0];
        CVector3 prevsample(presample[0]);
        CVector3 diff;
        samplelen[0] = 0;
        double overalllen = 0;
        CVector3Array results;
        for(long i=1;i<subdiv;i++,sampleu+=samplestep)
        {
            index1 = (int)min(count-2,sampleu / step);
            index2 = index1+1;
            v = (sampleu - step * double(index1)) / step;
            results = bezier4point(pos[index1],tangent[index1],pos[index2],tangent[index2],v);
            presample[i] = results[0];
            presampletan[i] = results[1];
            diff.Sub(presample[i],prevsample);
            overalllen += diff.GetLength();
            samplelen[i] = overalllen;
            prevsample = presample[i];
        }
        // now as we have the
        sampleu = 0;
        for(long i=0;i<subdiv-1;i++,sampleu+=samplestep)
        {
            samplelen[i+1] = samplelen[i+1] / overalllen;
            if(u>=samplelen[i] && u <= samplelen[i+1])
            {
                u = (u - samplelen[i]) / (samplelen[i+1] - samplelen[i]);
                bezierPos.LinearlyInterpolate(presample[i],presample[i+1],u);
                xAxis.LinearlyInterpolate(presampletan[i],presampletan[i+1],u);
                break;
            }
        }
    }

    // compute the scaling (straight interpolation!)
    CVector3 scl1;
    scl1.LinearlyInterpolate(scl[index1temp], scl[index2temp],vtemp);
    scl1.PutX(1);
    // scl1.PutX(modelXF.GetSclX());
    // We need to find another way to manage global scaling

    // compute the rotation!
    CRotation rot1,rot2;
    rot1.SetFromXYZAngles(rot[index1temp]);
    rot2.SetFromXYZAngles(rot[index2temp]);
    CQuaternion quat;
    quat.Slerp(rot1.GetQuaternion(),rot2.GetQuaternion(),vtemp);
    rot1.SetFromQuaternion(quat);
    yAxis.Set(0,1,0);
    yAxis.MulByMatrix3InPlace(rot1.GetMatrix());

    // use directly or project the roll values!
    if (mode == 1)
    {
        double thisRoll = roll[index1temp] * (1.0 - vtemp) + roll[index2temp] * vtemp;
        rot1.SetFromAxisAngle(xAxis,DegreesToRadians(thisRoll));
        yAxis.MulByMatrix3InPlace(rot1.GetMatrix());
    }

    zAxis.Cross(xAxis,yAxis);
    yAxis.Cross(zAxis,xAxis);
    xAxis.NormalizeInPlace();
    yAxis.NormalizeInPlace();
    zAxis.NormalizeInPlace();

    CTransformation result;
    result.SetScaling(scl1);
    result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
    result.SetTranslation(bezierPos);
    KinematicState outKine(ctxt.GetOutputTarget());
    outKine.PutTransform(result);

    return CStatus::OK;
}
