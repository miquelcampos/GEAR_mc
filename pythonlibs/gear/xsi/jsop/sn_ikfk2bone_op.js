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

// Update =====================================================
function sn_ikfk2bone_op_Update( In_UpdateContext, Out, ikrootKine, ikeffKine, ikupvKine, fkbone1Kine, fkbone2Kine, fkeffKine )
{

    ikrootKine = ikrootKine.Value;
    ikeffKine = ikeffKine.Value;
    ikupvKine = ikupvKine.Value;
    fkbone1Kine = fkbone1Kine.Value;
    fkbone2Kine = fkbone2Kine.Value;
    fkeffKine = fkeffKine.Value;

    blend = In_UpdateContext.Parameters( "blend" ).Value;

    lengthA = In_UpdateContext.Parameters("lengthA").Value;
    lengthB = In_UpdateContext.Parameters("lengthB").Value;
    negate = In_UpdateContext.Parameters("negate").Value;
    roll = XSIMath.DegreesToRadians(In_UpdateContext.Parameters("roll").Value);
    scaleA = In_UpdateContext.Parameters("scaleA").Value;
    scaleB = In_UpdateContext.Parameters("scaleB").Value;
    maxstretch = In_UpdateContext.Parameters("maxstretch").Value;
    softness = In_UpdateContext.Parameters( "softness").Value;
    slide = In_UpdateContext.Parameters( "slide").Value;
    reverse = In_UpdateContext.Parameters("reverse").Value;

    // setup the base IK parameters
    ikparams = new Object();

    ikparams.root = ikrootKine.Transform;
    ikparams.eff = ikeffKine.Transform;
    ikparams.upv = ikupvKine.Transform;

    ikparams.lengthA = lengthA;
    ikparams.lengthB = lengthB;
    ikparams.negate = negate;
    ikparams.roll = roll;
    ikparams.scaleA = scaleA;
    ikparams.scaleB = scaleB;
    ikparams.maxstretch = maxstretch;
    ikparams.softness = softness;
    ikparams.slide = slide;
    ikparams.reverse = reverse;

    // setup the base FK parameters
    fkparams = new Object();

    fkparams.root = ikrootKine.Transform;
    fkparams.bone1 = fkbone1Kine.Transform;
    fkparams.bone2 = fkbone2Kine.Transform;
    fkparams.eff = fkeffKine.Transform;

    fkparams.lengthA = lengthA;
    fkparams.lengthB = lengthB;
    fkparams.negate = negate;

    // get output name
    outportName = Out.Name;

    // for optimization
    if (blend == 0.0)
        result = getFKTransform(fkparams, outportName);
    else if(blend == 1.0)
        result = getIKTransform(ikparams, outportName);
    else
    {
        // here is where the blending happens!
        ikbone1 = getIKTransform(ikparams, "OutBoneA");
        ikbone2 = getIKTransform(ikparams, "OutBoneB");
        ikeff = getIKTransform(ikparams, "OutEff");

        fkbone1 = fkparams.bone1;
        fkbone2 = fkparams.bone2;
        fkeff = fkparams.eff;

        // map the secondary transforms from global to local
        ikeff = XSIMath.MapWorldPoseToObjectSpace(ikbone2, ikeff);
        fkeff = XSIMath.MapWorldPoseToObjectSpace(fkbone2, fkeff);
        ikbone2 = XSIMath.MapWorldPoseToObjectSpace(ikbone1, ikbone2);
        fkbone2 = XSIMath.MapWorldPoseToObjectSpace(fkbone1, fkbone2);

        // now blend them!
        fkparams.bone1 = interpolateTransform(fkbone1, ikbone1, blend);
        fkparams.bone2 = interpolateTransform(fkbone2, ikbone2, blend);
        fkparams.eff = interpolateTransform(fkeff, ikeff, blend);

        // now map the local transform back to global!
        fkparams.bone2 = XSIMath.MapObjectPoseToWorldSpace(fkparams.bone1, fkparams.bone2);
        fkparams.eff = XSIMath.MapObjectPoseToWorldSpace(fkparams.bone2, fkparams.eff);

        // calculate the result based on that
        result = getFKTransform(fkparams, outportName);
    }

	Out.Value.Transform = result;
}

///////////////////////////////////////////////////////////////
// IK TRANSFORMS
///////////////////////////////////////////////////////////////
function getIKTransform(values, outportName)
{

    // prepare all variables
    result = XSIMath.CreateTransform();
    bonePos = XSIMath.CreateVector3();
    rootPos = XSIMath.CreateVector3();
    effPos = XSIMath.CreateVector3();
    upvPos = XSIMath.CreateVector3();
    rootEff = XSIMath.CreateVector3();
    xAxis = XSIMath.CreateVector3();
    yAxis = XSIMath.CreateVector3();
    zAxis = XSIMath.CreateVector3();
    rollAxis = XSIMath.CreateVector3();

    rootPos = values.root.Translation;
    effPos = values.eff.Translation;
    upvPos = values.upv.Translation;
    rootEff.Sub(effPos,rootPos);
    rollAxis.Normalize(rootEff);

    rootMatrix = values.root.Matrix4;
    rootMatrixNeg = XSIMath.CreateMatrix4();
    rootMatrixNeg.Invert(rootMatrix);

    rootEffDistance = rootEff.Length();

    // init the scaling
    global_scale = values.root.Scaling.X;
    result.SetScaling(values.root.Scaling);

    // Distance with MaxStretch ---------------------
    restLength = values.lengthA * values.scaleA + values.lengthB * values.scaleB;
    distanceVector = XSIMath.CreateVector3();
    distanceVector.MulByMatrix4(effPos, rootMatrixNeg);
    distance = distanceVector.Length();
    distance2 = distance;
    if (distance > (restLength * (values.maxstretch)))
    {
        distanceVector.NormalizeInPlace();
        distanceVector.ScaleInPlace(restLength * (values.maxstretch) );
        distance = restLength * (values.maxstretch);
    }

    // Adapt Softness value to chain length --------
    values.softness = values.softness * restLength *.1;

    // Stretch and softness ------------------------
    // We use the real distance from root to controler to calculate the softness
    // This way we have softness working even when there is no stretch
    stretch = max(1, distance / restLength);
    da = restLength - values.softness;
    if ((values.softness > 0) && (distance2 > da))
    {
        newlen = values.softness*(1.0 - Math.exp(-(distance2 -da)/values.softness)) + da;
        stretch = distance / newlen;
    }

    values.lengthA = values.lengthA * stretch * values.scaleA * global_scale;
    values.lengthB = values.lengthB * stretch * values.scaleB * global_scale;

    // Reverse -------------------------------------
    d = distance / (values.lengthA + values.lengthB);

    if (values.reverse < 0.5)
        reverse_scale = 1-(values.reverse*2 * (1-d));
    else
        reverse_scale = 1-((1-values.reverse)*2 * (1-d));

    values.lengthA *= reverse_scale;
    values.lengthB *= reverse_scale;

    invert = values.reverse > 0.5;

    // Slide ---------------------------------------
    if (values.slide < .5)
        slide_add = (values.lengthA * (values.slide * 2)) - (values.lengthA);
    else
        slide_add = (values.lengthB * (values.slide * 2)) - (values.lengthB);

    values.lengthA += slide_add;
    values.lengthB -= slide_add;

    // calculate the angle inside the triangle!
    angleA = 0;
    angleB = 0;

    // check if the divider is not null otherwise the result is nan
    // and the output disapear from xsi, that breaks constraints
    if((rootEffDistance < values.lengthA + values.lengthB) && (rootEffDistance > Math.abs(values.lengthA - values.lengthB) + 1E-6))
    {
        // use the law of cosine for lengthA
        a = values.lengthA;
        b = rootEffDistance;
        c = values.lengthB;

            angleA = Math.acos(min(1, (a * a + b * b - c * c ) / ( 2 * a * b)));

        // use the law of cosine for lengthB
        a = values.lengthB;
        b = values.lengthA;
        c = rootEffDistance;
        angleB = Math.acos(min(1, (a * a + b * b - c * c ) / ( 2 * a * b)));

        // invert the angles if need be
        if(invert)
        {
            angleA = -angleA;
            angleB = -angleB;
        }
    }

    // start with the X and Z axis
    xAxis = rootEff;
    yAxis.LinearlyInterpolate(rootPos,effPos,.5);
    yAxis.Sub(upvPos,yAxis);
    yAxis = rotateVectorAlongAxis(yAxis, rollAxis, values.roll);
    zAxis.Cross(xAxis,yAxis);
    xAxis.NormalizeInPlace();
    zAxis.NormalizeInPlace();

    // switch depending on our mode
    if(outportName == "OutBoneA")  // Bone A
    {
        // check if we need to rotate the bone
        if(angleA != 0.0)
        {
            rot = XSIMath.CreateRotation();
            rot.SetFromAxisAngle(zAxis,angleA);
            xAxis.MulByRotationInPlace(rot);
        }

        if (values.negate)
            xAxis.NegateInPlace();

        // cross the yAxis and normalize
        yAxis.Cross(zAxis,xAxis);
        yAxis.NormalizeInPlace();

        // output the rotation
        result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

        // set the scaling + the position
        result.SclX = values.lengthA;
        result.SetTranslation(rootPos);
    }
    else if(outportName == "OutBoneB")  // Bone B
    {
        // check if we need to rotate the bone
        if (angleA != 0.0)
        {
            rot = XSIMath.CreateRotation();
            rot.SetFromAxisAngle(zAxis,angleA);
            xAxis.MulByRotationInPlace(rot);
        }

        // calculate the position of the elbow!
        bonePos.Scale(values.lengthA,xAxis);
        bonePos.AddInPlace(rootPos);

        // check if we need to rotate the bone
        if (angleB != 0.0)
        {
            rot = XSIMath.CreateRotation();
            rot.SetFromAxisAngle(zAxis,angleB - Math.PI);
            xAxis.MulByRotationInPlace(rot);
        }

        if (values.negate)
            xAxis.NegateInPlace();

        // cross the yAxis and normalize
        yAxis.Cross(zAxis,xAxis);
        yAxis.NormalizeInPlace();

        // output the rotation
        result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

        // set the scaling + the position
        result.SclX = values.lengthB;
        result.SetTranslation(bonePos);
    }
    else if(outportName == "OutCenterN")  // center normalized
    {
        // check if we need to rotate the bone
        if(angleA != 0.0)
        {
            rot = XSIMath.CreateRotation();
            rot.SetFromAxisAngle(zAxis,angleA);
            xAxis.MulByRotationInPlace(rot);
        }

        // calculate the position of the elbow!
        bonePos.Scale(values.lengthA,xAxis);
        bonePos.AddInPlace(rootPos);

        // check if we need to rotate the bone
        if(angleB != 0.0)
        {
            if (invert)
                angleB += Math.PI * 2;

            rot = XSIMath.CreateRotation();
            rot.SetFromAxisAngle(zAxis, angleB *.5 - Math.PI*.5);
            xAxis.MulByRotationInPlace(rot);
        }
        // cross the yAxis and normalize
        // yAxis.Sub(upvPos,bonePos); // this was flipping the centerN when the elbow/upv was aligned to root/eff
        zAxis.Cross(xAxis,yAxis);
        zAxis.NormalizeInPlace();

        if (values.negate)
            xAxis.NegateInPlace();

        yAxis.Cross(zAxis,xAxis);
        yAxis.NormalizeInPlace();

        // output the rotation
        result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

        // set the scaling + the position
        // result.SetSclX(stretch * values.root.GetSclX());

        result.SetTranslation(bonePos);
    }
    else if(outportName == "OutEff")  // effector
    {
        // check if we need to rotate the bone
        effPos = rootPos;
        if(angleA != 0.0)
        {
            rot = XSIMath.CreateRotation();
            rot.SetFromAxisAngle(zAxis,angleA);
            xAxis.MulByRotationInPlace(rot);
        }

        // calculate the position of the elbow!
        bonePos.Scale(values.lengthA,xAxis);
        effPos.AddInPlace(bonePos);

        // check if we need to rotate the bone
        if(angleB != 0.0)
        {
            rot = XSIMath.CreateRotation();
            rot.SetFromAxisAngle(zAxis,angleB - Math.PI);
            xAxis.MulByRotationInPlace(rot);
        }

        // calculate the position of the effector!
        bonePos.Scale(values.lengthB,xAxis);
        effPos.AddInPlace(bonePos);

        // cross the yAxis and normalize
        yAxis.Cross(zAxis,xAxis);
        yAxis.NormalizeInPlace();

        // output the rotation
        result = values.eff;
        result.SetTranslation(effPos);
    }


    r = result.Rotation;
    eulerAngles = r.XYZAngles;

    rx = eulerAngles.X;
    ry = eulerAngles.Y;
    rz = eulerAngles.Z;

    return result;
}

///////////////////////////////////////////////////////////////
// FK TRANSFORMS
///////////////////////////////////////////////////////////////
function getFKTransform(values, outportName)
{
    // prepare all variables
    result = XSIMath.CreateTransform();
    xAxis = XSIMath.CreateVector3();
    yAxis = XSIMath.CreateVector3();
    zAxis = XSIMath.CreateVector3();
    temp = XSIMath.CreateVector3();

    if(outportName == "OutBoneA")
    {
        result = values.bone1;
        xAxis.Sub(values.bone2.Translation,values.bone1.Translation);
        result.SclX = xAxis.Length;

        if (values.negate)
            xAxis.NegateInPlace();

        // cross the yAxis and normalize
        xAxis.NormalizeInPlace();
        yAxis.Set(0,1,0);
        yAxis.MulByRotationInPlace(values.bone1.Rotation);
        zAxis.Cross(xAxis,yAxis);
        zAxis.NormalizeInPlace();
        yAxis.Cross(zAxis,xAxis);
        yAxis.NormalizeInPlace();

        // rotation
        result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);

    }
    else if(outportName == "OutBoneB")  //  Bone B
    {
        result = values.bone2;
        xAxis.Sub(values.eff.Translation,values.bone2.Translation);
        result.SclX(xAxis.Length);

        if (values.negate)
            xAxis.NegateInPlace();

        // cross the yAxis and normalize
        xAxis.NormalizeInPlace();
        yAxis.Set(0,1,0);
        yAxis.MulByRotationInPlace(values.bone2.Rotation);
        zAxis.Cross(xAxis,yAxis);
        zAxis.NormalizeInPlace();
        yAxis.Cross(zAxis,xAxis);
        yAxis.NormalizeInPlace();

        // rotation
        result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
    }
    else if(outportName == "OutCenterN") // center normalized
    {
    	/*
        // cross the yAxis and normalize
        temp.Set(1,0,0);
        yAxis.MulByRotation(temp, values.bone1.Rotation);
        temp.MulByRotation(XSIMath.CreateVector3(-1,0,0),values.bone2.Rotation);
        yAxis.AddInPlace(temp);
        if(yAxis.Length() <= 0.001)
            yAxis.MulByRotation(XSIMath.CreateVector3(0,1,0),values.bone2.Rotation);
        yAxis.NormalizeInPlace();

        zAxis.Set(0,0,1);
        zAxis.MulByRotationInPlace(values.bone2.Rotation);

        xAxis.Cross(yAxis, zAxis);
        xAxis.NormalizeInPlace();

        // Avoid flipping
        temp.Set(1,0,0);
        temp.MulByRotationInPlace(values.bone2.Rotation);
        if (temp.Dot(xAxis) < 0)
        {
            xAxis.NegateInPlace();
            yAxis.NegateInPlace();
        }
        */

	    // Only +/-180 degree with this one but we don't get the shear issue anymore
	    tLocalB = XSIMath.MapWorldPoseToObjectSpace(values.bone1, values.bone2)
	    v = tLocalB.Rotation.XYZAngles
	    v.ScaleInPlace(.5)
	    tLocalB.SetRotationFromXYZAngles(v)
	    tLocalB = XSIMath.MapObjectPoseToWorldSpace(values.bone1, tLocalB)
	    result.SetRotation(tLocalB.Rotation)

        // rotation
        result.SetTranslation(values.bone2.Translation);
        //result.SetRotationFromXYZAxes(xAxis,yAxis,zAxis);
    }
    else if(outportName == "OutEff")  // effector
        result = values.eff;


    return result;
}

///////////////////////////////////////////////////////////////
// MISC
///////////////////////////////////////////////////////////////
function rotateVectorAlongAxis(v, axis, a)
{
    // Angle as to be in radians

    sa = Math.sin(a / 2.0);
    ca = Math.cos(a / 2.0);

    q1 = XSIMath.CreateQuaternion();
    q2 = XSIMath.CreateQuaternion();
    q2n = XSIMath.CreateQuaternion();
    q = XSIMath.CreateQuaternion();
    out = XSIMath.CreateVector3();

    q1.Set(0, v.X, v.Y, v.Z);
    q2.Set(ca, axis.X * sa, axis.Y * sa, axis.Z * sa);
    q2n.Set(ca, -axis.X * sa, -axis.Y * sa, -axis.Z * sa);

    q.Mul(q2, q1);
    q.MulInPlace(q2n);

    out.Set(q.X, q.Y, q.Z);
    return out;
}

function interpolateTransform(xf1, xf2, blend)
{
    if(blend == 1.0)
        return xf2;
    else if(blend == 0.0)
        return xf1;

    result = XSIMath.CreateTransform();
    resultPos = XSIMath.CreateVector3();
    resultScl = XSIMath.CreateVector3();
    resultQuat = XSIMath.CreateQuaternion();

    resultPos.LinearlyInterpolate(xf1.Translation, xf2.Translation, blend);
    resultScl.LinearlyInterpolate(xf1.Scaling, xf2.Scaling, blend);
    resultQuat.Slerp(xf1.Rotation.Quaternion ,xf2.Rotation.Quaternion, blend);

    result.SetScaling(resultScl);
    result.SetRotationFromQuaternion(resultQuat);
    result.SetTranslation(resultPos);

    return result;
}

function max(a, b)
{
    if (a > b)
        return a
    else
        return b
}

function min(a, b)
{
    if (a < b)
        return a
    else
        return b
}
