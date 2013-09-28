'''

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

'''

## @package gear.encode
# @author Jeremie Passerin
#
# @brief encode / decode data

##########################################################
# GLOBAL
##########################################################
import binascii
import cPickle
import pickle
import base64

##########################################################
# COMPRESSION
##########################################################
def encodeData(data):
     return binascii.b2a_base64(binascii.rlecode_hqx(cPickle.dumps(data)))

def decodeData(str):
     return cPickle.loads(binascii.rledecode_hqx(binascii.a2b_base64(str)))

def serializeToBuffer(data):
     return base64.b64encode(pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL))

def deserializeFromBuffer(buffer):
     return pickle.loads(base64.b64decode(buffer))
