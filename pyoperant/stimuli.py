import fnmatch
import os
import wave
from contextlib import closing
from pyoperant.utils import Event


class Stimulus(Event):
    """docstring for Stimulus"""
    def __init__(self, *args, **kwargs):
        super(Stimulus, self).__init__(*args, **kwargs)
        if self.label=='':
            self.label = 'stimulus'

class AuditoryStimulus(Stimulus):
    """docstring for AuditoryStimulus"""
    def __init__(self, *args, **kwargs):
        super(AuditoryStimulus, self).__init__(*args, **kwargs)
        if self.label=='':
            self.label = 'auditory_stimulus'

    @classmethod
    def from_wav(cls, wavfile):

        with closing(wave.open(wavfile,'rb')) as wf:
            (nchannels, sampwidth, framerate, nframes, comptype, compname) = wf.getparams()

            duration = float(nframes)/sampwidth
            duration = duration * 2.0 / framerate
            stim = cls(time=0.0,
                       duration=duration,
                       name=wavfile,
                       label='wav',
                       description='',
                       file_origin=wavfile,
                       annotations={'nchannels': nchannels,
                                    'sampwidth': sampwidth,
                                    'framerate': framerate,
                                    'nframes': nframes,
                                    'comptype': comptype,
                                    'compname': compname,
                                    }
                       )
        return stim


class StimulusCondition(object):

    def __init__(self, name="", response=None, is_rewarded=False, is_punished=False,
                 file_path="", recursive=False, file_pattern="*"):

        # These should do something better than printing and returning
        if file_path is None:
            print("file_path must be specified!")
            return

        if not os.path.exists(file_path):
            print("file_path does not exist!")
            return

        self.name = name
        self.response = response
        self.is_rewarded = is_rewarded
        self.is_punished = is_punished

        self.files = list()
        self.file_path = file_path
        self.recursive = recursive
        self.file_pattern = file_pattern
        self.filter_files()

    def __str__(self):

        return "".join(["Condition %s: " % self.name,
                        "Rewarded = %s, " % self.is_rewarded,
                        "Punished = %s, " % self.is_punished,
                        "# files = %d" % len(self.files)])

    def filter_files(self):

        for rootdir, dirname, fnames in os.walk(self.file_path):
            matches = fnmatch.filter(fnames, self.file_pattern)
            self.files.extend(os.path.join(rootdir, fname) for fname in matches)
            if not self.recursive:
                dirname[:] = list()

    def get(self, replacement=True):

        index = random.choice(range(len(self.files)))
        if replacement:
            return self.files[index]
        else:
            return self.files.pop(index)


class StimulusConditionWav(StimulusCondition):

    def __init__(self, name="", response=None, is_rewarded=False, is_punished=False,
                 file_path="", recursive=False):

        super(StimulusConditionWav, self).__init__(name=name,
                                                   response=response,
                                                   is_rewarded=is_rewarded,
                                                   is_punished=is_punished,
                                                   file_path=file_path,
                                                   recursive=recursive,
                                                   file_pattern="*.wav")

    def get(self, replacement=True):

        wavfile = super(StimulusConditionWav, self).get(replacement=replacement)

        return AuditoryStimulus.from_wav(wavfile)
