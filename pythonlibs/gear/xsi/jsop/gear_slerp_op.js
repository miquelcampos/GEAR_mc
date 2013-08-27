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
    Date:       2011 / 03 / 21

*/

/*@cc_on
	 /*@if(@_jscript_version < 5.5)
		Array.prototype.push = function(val) {this[this.length] = val;}
		Array.prototype.pop  = function()    {if(this.length == 0) return null; else {var val = this[this.length - 1]; this.length--; return val;}}
	/*@end
@*/

function gear_slerp_Update(ctxt, out, in_obj, refA, refB)
{
	blend = ctxt.Parameters("blend").value; 

	t0 = refA.Value.Transform
	t1 = refB.Value.Transform

	t = in_obj.Value.Transform

	q0 = XSIMath.CreateQuaternion()
	q1 = XSIMath.CreateQuaternion()

	t0.GetRotationQuaternion(q0)
	t1.GetRotationQuaternion(q1)

	qOut = XSIMath.CreateQuaternion()

	qOut.slerp(q0, q1, blend)

	t.SetRotationFromQuaternion(qOut)

	out.Value.Transform = t
}