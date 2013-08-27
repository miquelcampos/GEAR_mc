/*

    This file is part of GEAR_mc.
    GEAR_mc is a fork of Jeremie Passerin's GEAR project.

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

    Author:     Jeremie Passerin    geerem@hotmail.com  www.jeremiepasserin.com
    Fork Author:  Miquel Campos       hello@miqueltd.com  www.miqueltd.com
    Date:       2013 / 08 / 16

*/

/*@cc_on
	 /*@if(@_jscript_version < 5.5)
		Array.prototype.push = function(val) {this[this.length] = val;}
		Array.prototype.pop  = function()    {if(this.length == 0) return null; else {var val = this[this.length - 1]; this.length--; return val;}}
	/*@end
@*/

function gear_zipper_Update(ctxt, out, crv0, crv1)
{
    // Inputs -------------------------------------
    // Parameters
    zip    = ctxt.Parameters("zip").Value;
    bias   = ctxt.Parameters("bias").Value;

    start_fcv = ctxt.Parameters("start_fcv").Value;
    speed_fcv = ctxt.Parameters("speed_fcv").Value;

    // Ports
    crv_geo_0 = crv0.Value.Geometry;
    nurbs_crv_0 = crv_geo_0.Curves(0);
    crv_geo_1 = crv1.Value.Geometry;
    nurbs_crv_1 = crv_geo_1.Curves(0);

    // Process ------------------------------------
    point_count_0  = crv_geo_0.Points.Count;
    point_count_1  = crv_geo_1.Points.Count;

    pnt_pos_0 = crv_geo_0.Points.PositionArray.toArray();
    pnt_pos_1 = crv_geo_1.Points.PositionArray.toArray();


        pos_0 = pnt_pos_0
        pos_1 = pnt_pos_1


    pos_mid = []
    for(i=0;i<pos_0.length;i++)
        pos_mid.push(pos_0[i]*bias+pos_1[i]*(1-bias))

    // Process ------------------------------------
    if(out.Index == 2)
    {
        t = pos_0
        p = point_count_0
    }
    else
    {
        t = pos_1
        p = point_count_1
    }

    positions = []
    v = XSIMath.CreateVector3()
    for(i=0;i<p;i++)
    {
        step = 1/(p-1.0)

        v0 = XSIMath.CreateVector3(t[i*3+0], t[i*3+1], t[i*3+2])
        v1 = XSIMath.CreateVector3(pos_mid[i*3+0], pos_mid[i*3+1], pos_mid[i*3+2])
        v.Sub(v1, v0)
        //  The nex line was commented out by jeremie
        d = start_fcv.Eval(i*step)

        if(zip < d)
            y = 0
        else
            y = changerange(zip, d, d+step, 0, 1)
        //  The nex line was commented out by jeremie
        y = speed_fcv.Eval(y)

        v.ScaleInPlace(y)

        positions.push(v0.X + v.X)
        positions.push(v0.Y + v.Y)
        positions.push(v0.Z + v.Z)
    }

    // Out ----------------------------------------
    out.Value.Geometry.Points.PositionArray = positions;
}

function changerange(x, a, b, c, d)
{
    return c + ( x - a ) * (( d-c) / (b-a+0.0))
}

