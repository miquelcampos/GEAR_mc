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

function gear_pointAtObjectAxis_Update(ctxt, out, kine)
{
	x = ctxt.Parameters("x").value; 
	y = ctxt.Parameters("y").value; 
	z = ctxt.Parameters("z").value; 
    
    dir = XSIMath.CreateVector3(x,y,z);
    
	t = kine.Value.Transform;
    r = t.Rotation;
    
    dir.MulByRotationInPlace(r);
    
    if (out.Name == "out_x")
        out.Value = dir.X;
    else if (out.Name == "out_y")
        out.Value = dir.Y;
    else if (out.Name == "out_z")
        out.Value = dir.Z;
        
}