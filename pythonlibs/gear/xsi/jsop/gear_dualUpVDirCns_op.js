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

    Author:     Jeremie Passerin      geerem@hotmail.com
    Url :       http://gear.jeremiepasserin.com
    Date:       2011 / 09 / 14

*/

/*@cc_on
	 /*@if(@_jscript_version < 5.5)
		Array.prototype.push = function(val) {this[this.length] = val;}
		Array.prototype.pop  = function()    {if(this.length == 0) return null; else {var val = this[this.length - 1]; this.length--; return val;}}
	/*@end
@*/

function gear_dualUpVDirCns_Update(ctxt, out, kcns, kref, ktar)
{
    // --------------------------------
    // Inputs
	negate = ctxt.Parameters("negate").Value; 
    
    tcns = kcns.Value.Transform;
    tref = kref.Value.Transform;
    ttar = ktar.Value.Transform;
    vcns = tcns.Translation;
    vtar = ttar.Translation;

    rref = tref.Rotation;
    
    // --------------------------------
    // Direction
    x = XSIMath.CreateVector3();
    x.Sub(vtar, vcns);
    x.NormalizeInPlace();
    if (negate)
        x.NegateInPlace();
    
    // Upvectors
    ref_y = XSIMath.CreateVector3(0,1,0);
    ref_z = XSIMath.CreateVector3(0,0,1);
    ref_y.MulByRotationInPlace(rref);
    ref_z.MulByRotationInPlace(rref);

    // Average
    ay = x.Angle(ref_y);
    az = x.Angle(ref_z);

    pi = XSIMath.PI
    dpi = pi*.5
    dy = 1 - Math.abs(dpi-ay)/dpi;
    dz = 1 - Math.abs(dpi-az)/dpi;
    d = dy/(dy+dz);

    // --------------------------------
    // Up Vector
    // Y upv
    z0 = XSIMath.CreateVector3();
    z0.Cross(x,ref_y);
    z0.NormalizeInPlace();
    y0 = XSIMath.CreateVector3();
    y0.Cross(z0,x);

    // Z upv
    y1 = XSIMath.CreateVector3();
    y1.Cross(ref_z,x);
    y1.NormalizeInPlace();

    // --------------------------------
    // Interpolate
    y = XSIMath.CreateVector3();
    y.LinearlyInterpolate(y1,y0,d);
    y.NormalizeInPlace();
    
    z = XSIMath.CreateVector3();
    z.Cross(x,y);

    // --------------------------------
    // Output
    r = XSIMath.CreateRotation();
    r.SetFromXYZAxes(x,y,z);

    tcns.SetRotation(r);

    out.Value.Transform = tcns
        
}