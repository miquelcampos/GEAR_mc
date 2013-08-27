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

function gear_resampler_Update(ctxt, out, in_crv, in_crv_kine, ref_crv, ref_crv_kine)
{
    // Inputs -------------------------------------
    // Parameters
    parametric  = ctxt.Parameters("parametric").Value; 
    mode      = ctxt.Parameters("mode").Value; 
    start       = ctxt.Parameters("start").Value; 
    end         = ctxt.Parameters("end").Value; 
    
    // Ports
    m_in_crv  = in_crv_kine.Value.Transform.Matrix4;
    m_ref_crv = ref_crv_kine.Value.Transform.Matrix4;
    m_inv_in_crv = XSIMath.CreateMatrix4();
    m_inv_in_crv.Invert(m_in_crv);
    
    crv_geo = ref_crv.Value.Geometry;
    nurbs_crv = crv_geo.Curves(0);
    point_count = in_crv.Value.Geometry.Points.Count;

    // Process ------------------------------------
    positions = [];
    
    for( i=0; i<point_count; i++ )
    {
        step = (end - start) / (point_count-1.0);
        u = start + (i*step);
        u = min(1,max(0,u));
        
        if(parametric == 1)
            pos = nurbs_crv.EvaluateNormalizedPosition(u).getItem(0);
        else
            pos = nurbs_crv.EvaluatePositionFromPercentage(u*100).getItem(0);
         
        // convert local position from target object to source object
        if (mode == 1)
        {
            pos.MulByMatrix4InPlace(m_ref_crv);
            pos.MulByMatrix4InPlace(m_inv_in_crv);
        }
            
        positions.push(pos.X);
        positions.push(pos.Y);
        positions.push(pos.Z);
    }

    // Out ----------------------------------------
    out.Value.Geometry.Points.PositionArray = positions;
}

function max(dA, dB)
{
    return dA>dB?dA:dB
}

function min(dA, dB)
{
    return dA<dB?dA:dB
}