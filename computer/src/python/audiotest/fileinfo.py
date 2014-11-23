import mutagen.asf as asf
import mutagen.mp3 as mp3
import mutagen.mp4 as mp4
import mutagen.flac as flac
import mutagen.oggvorbis as ogg
import mutagen.oggflac as oga
import os, wave, aifc

class Error (Exception): pass

class waveinfo:
    def __init__ (self, filename):
        if filename.endswith(".wav") or filename.endswith(".wave"):
            wf = wave.open(filename)
            self.filetype = "PCM WAVE"
        else:
            wf = aifc.open(filename)
            self.filetype = "AIFF/AIFF-C"
        self.sample_rate = wf.getframerate()
        self.channels = wf.getnchannels()
        self.bits_per_sample = self.bitspersample = wf.getsampwidth()*8
        self.comptype = wf.getcomptype()
        self.compname = wf.getcompname()
        self.length = wf.getnframes()/self.sample_rate
        wf.close()

    def pprint (self):
        s = "%s (%s), %d channels, %d bps, %s Hz, %.2f seconds" % (
            self.filetype,
            self.compname, self.channels, self.bitspersample, self.sample_rate,
            self.length)
        return s

class wi:
    def __init__ (self, filename):
        self.info = waveinfo(filename)

class w:
    def __init__ (self): pass
    def Open (self, filename): return wi(filename)
wav = w()

def info (filename):
    filename = os.path.normpath(filename)
    if os.name=="nt": filename = filename.replace(os.sep, os.altsep)
    if not os.path.exists(filename): raise IOError, (2, "No such file or directory: '%s'" % filename)
    mod = os.path.splitext(filename)[-1][1:].lower()
    func = "Open"
    if mod=="wma": mod = "asf"
    elif mod=="m4a" or mod=="m4b" or mod=="aac": mod = "mp4"
    elif mod in ("mp1", "mp2", "mpg", "mpeg"): mod = "mp3"
    elif mod=="wave": mod = "wav"
    elif mod=="aiff" or mod=="aif": mod = "wav"
    elif mod in ("mp3", "asf", "mp4", "flac", "ogg", "oga", "wav"): pass
    else: raise Error, "unsuported filetype"
    exec "r = "+mod+".%s(\"%s\")" % (func, filename)
    r.info.size = os.path.getsize(filename)
    r.info.ctime = os.path.getctime(filename)
    r.info.atime = os.path.getatime(filename)
    r.info.mtime = os.path.getmtime(filename)
    return r
