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

function gear_curveslide2_Update(ctxt, out, slv_crv, mst_crv)
{
	// Inputs ---------------------------------------------------------
	var slvlength = ctxt.Parameters("slvlength").Value;
	var mstlength = ctxt.Parameters("mstlength").Value; 
	var position = ctxt.Parameters("position").Value;
	var max_stretch = ctxt.Parameters("maxstretch").Value;
	var max_squash = ctxt.Parameters("maxsquash").Value;
	var softness = ctxt.Parameters("softness").Value;
    
    var slv_geo = slv_crv.Value.Geometry;
    var slv_ncrv = slv_geo.Curves(0);
    var mst_crv = mst_crv.Value.Geometry;
    var mst_ncrv = mst_crv.Curves(0);

    var mstCrvLength = mst_ncrv.Length;
    var slv_pnt_count = slv_geo.Points.Count;
    var mst_pnt_count = mst_crv.Points.Count;
    
    // Stretch --------------------------------------------------------
    if ((mstCrvLength > mstlength) && (max_stretch > 1))
    {
        if (softness == 0)
            exp = 1
        else
        {
            stretch = (mstCrvLength - mstlength) / (slvlength*max_stretch)
            exp = 1 - Math.exp(-(stretch)/softness)
        }

        extension = min(slvlength*(max_stretch-1)*exp, mstCrvLength-mstlength)

        slvlength += extension
    }
    else if ((mstCrvLength < mstlength) && (max_squash < 1))
    {
        if (softness == 0)
            exp = 1
        else
        {
            dSquash = (mstlength - mstCrvLength) / (slvlength*max_squash)
            exp = 1 - Math.exp(-(dSquash)/softness)
        }

        extension = min(slvlength*(1-max_squash)*exp, mstlength-mstCrvLength)

        slvlength -= extension
    }

    // Position --------------------------------------------------------
    var size = (slvlength / mstCrvLength) * 100
    var size_left = 100 - size

    start = position * size_left
    end = start + size

	// Process --------------------------------------------------------
    var positions = new Array()

    for(var i=0; i<slv_pnt_count; i++)
    {
        step = (end - start) / (slv_pnt_count-1.0)
        perc = start + (i*step)

        if ((0 <= perc) && (perc <= 100))
            vPos = mst_ncrv.EvaluatePositionFromPercentage(perc).getItem(0)
        else
        {
            if (perc < 0)
            {
                overperc = perc
                rtn = mst_ncrv.EvaluatePositionFromPercentage(0)
            }
            else
            {
                overperc = perc - 100
                rtn = mst_ncrv.EvaluatePositionFromPercentage(100)
            }

            vPos = rtn.getItem(0)
            vTan = rtn.getItem(1)
            vTan.ScaleInPlace((mstCrvLength / 100.0) * overperc)
            vPos.AddInPlace(vTan)
        }
        
        positions.push(vPos.X)
        positions.push(vPos.Y)
        positions.push(vPos.Z)
    }

	// Out ------------------------------------------------------------
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