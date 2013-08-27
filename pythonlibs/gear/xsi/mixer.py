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

## @package gear.xsi.mixer
# @author Jeremie Passerin
#
# @brief
# 

##########################################################
# GLOBAL
##########################################################

# gear
import gear

from gear.xsi import xsi, Dispatch

##########################################################
# MIXER
##########################################################
class Mixer(object):
    '''
        Mixer object
    '''

    def __init__(self, model):

        self.model = model

        # Mixer
        if self.model.Mixer:
            self.mixer = self.model.Mixer
        else:
            self.mixer = self.model.AddMixer()

        # Sources
        self.sources = self.mixer.NestedObjects("Sources")

        # Tracks
        self.tracks = self.mixer.NestedObjects("Tracks")

    def getAnimSources(self):
       d = {}
       for source in self.sources.NestedObjects("Animation").NestedObjects:
          d[source.Name] = AnimationSource(source)
       return d

    def getShapeSources(self):
       d = {}
       for source in self.sources.NestedObjects("Shape").NestedObjects:
          d[source.Name] = ShapeSource(source)
       return d

    def getAudioSources(self):
       d = {}
       for source in self.sources.NestedObjects("Audio").NestedObjects:
          d[source.Name] = AudioSource(source)
       return d

    def getAnimTracks(self):
       d = {}
       for track in self.tracks.NestedObjects("Animation").NestedObjects:
          d[track.Name] = AnimationTrack(source)
       return d

    def getShapeTracks(self):
       d = {}
       for track in self.tracks.NestedObjects("Shape").NestedObjects:
          d[track.Name] = ShapeTrack(source)
       return d

    def getAudioTracks(self):
       d = {}
       for track in self.tracks.NestedObjects("Audio").NestedObjects:
          d[track.Name] = AudioTrack(source)
       return d

    # Properties
    animSources = property(getAnimSources)
    shapeSources = property(getAnimSources)
    audioSources = property(getAnimSources)
    animTracks = property(getAnimTracks)
    shapeTracks = property(getShapeTracks)
    audioTracks = property(getAudioTracks)

##########################################################
# SOURCES
##########################################################
class Source(object):
    '''
        Source object
    '''

    def __init__(self, source):

        self.value = source

        # Original Attributes
        self.name = self.value.Name
        self.fullName = self.value.FullName

        self._getParameters()

    def _getParameters(self):
        return

class AnimationSource(Source):
    pass

class ShapeSource(Source):
    pass

class AudioSource(Source):

    def _getParameters(self):

        self.fileName = self.value.FileName
        self.samplingRate = self.value.SamplingRate
        self.channelCount = self.value.ChannelCount
        self.duration = self.value.Duration

##########################################################
# TRACKS
##########################################################
class Track(object):

    def __init__(self, track):

        self.value = track

        # Original Attributes
        self.name = self.value.Name
        self.fullName = self.value.FullName

        # Clips
        self.getClips()

    def getClips(self):
        self.clips = [Clip(clip) for clip in self.value.NestedObjects("Clip List")]

class AnimationTrack(Track):
    pass

class ShapeTrack(Track):
    pass

class AudioTrack(Track):

    def getClips(self):
        self.clips = [AudioClip(clip) for clip in self.value.NestedObjects("Clip List").NestedObjects]


##########################################################
# CLIPS
##########################################################
class Clip(object):

    def __init__(self, clip):

        self.value = Dispatch(clip)
        self.name = self.value.Name
        self.fullName = self.value.FullName

class AudioClip(Clip):

    def __init__(self, clip):

        self.value = Dispatch(clip)
        self.name = self.value.Name
        self.fullName = self.value.FullName

        self.timeControl = Dispatch(self.value.NestedObjects("Time Control"))

        self.source = None
        for no in self.value.NestedObjects:
            if no.Type == "AudioSource":
                self.source = AudioSource(no)
                break
