# Copyright (C) 2010-2011 by Dalen Bernaca
# YOU ARE ALLOWED TO USE AND DISTRIBUTE THIS PROGRAM FREELY
#
# YOU ARE ALLOWED TO MODIFY THIS PROGRAM IN ONE CONDITION:
# THAT YOU SEND YOUR MODIFIED VERSION TO THE AUTHOR BY E-MAIL
# WITH SHORT EXPLANATION REGARDING THE MODIFICATION(S)
# IF YOUR MODIFICATION(S) INCREASE THE QUALITY OF THE PROGRAM
# THEY WILL BE TAKEN IN VIEW FOR THE NEW OFFICIAL VERSION
#
# Author: Dalen Bernaca
#         dbernaca@blue-merlin.hr
# Version: 1.5XB
#
# THE AUTHOR IS NOT RESPONSIBLE FOR ANY DAMAGE INFLICTED BY MISSUSE/ABUSE OF THIS SOFTWARE
# ANY OTHER PROGRAM WITH SAME/SIMILAR NAME AND PURPOSE WHICH IS NOT PROCURED FROM
# http://www.brailleweb.com/
# IS NOT THE OFFICIAL VERSION WHATEVER MAY BE WRITTEN IN THE SOURCE CODE AND
# SHOULD BE TREATED WITH ENORMOUS CARE
# THE AUTHOR IS NOT ACCOUNTABLE FOR SUCH SOURCE CODE
#
# decoder.py is the result of author's knowledge, skill and creativity and a lot of asembled code legally optained from the internet.
# Thanks to all who put them there!

"""
decoder.py is a cross-platform module for decoding compressed audio files.
It uses external decoders by turning their stdout into file-like object which is completely compatible with wave.py module.

Usage:

>>> import decoder
>>>
>>> mp3 = decoder.open("something.mp3")
>>> print "Channels:", mp3.getnchannels()
Channels: 2
>>> print "Framerate:", mp3.getframerate()
Framerate: 44100
>>> print "Duration:", mp3.getnframes()/mp3.getframerate()
Duration: 206
>>>
>>> import wave
>>>
>>> wf = wave.open("something.wav", "w")
>>> wf.setnchannels(mp3.getnchannels())
>>> wf.setsampwidth(mp3.getsampwidth())
>>> wf.setnframes(mp3.getnframes())
>>> wf.setframerate(mp3.getframerate())
>>> data = mp3.readframes(1024)
>>> while data!="":
...     wf.writeframes(data)
...     data = mp3.readframes(1024)
...
>>> mp3.close()
>>> wf.close()
>>>
>>> # You can abbreviate the above code as this:
>>> mp3 = decoder.open("something.mp3")
>>> wf = wave.open("something.wav", "w")
>>> decoder.copywaveobj(mp3, wf)
>>> mp3.close()
>>> wf.close()
>>> 

The "from decoder import *" is also supported, but the function open() will then become
acopen(), so to avoid mixing with __builtin__.open().

You can use the audiodev module or PyAudio library or sys.stdout or some external command line player like aplay
in the same way as shown above.

FUNCTIONS:

open(name, fh=0) --> fakewave / wave.Wave_read / aifc.Aifc_read object
The name argument is the path to file you wish to decode.
Supported filetypes:
*.mp1, *.mp2, *.mp3
*.mp4, *.m4a, *.m4b, *.aac
*.ogg
*.flac
*.oga
*.wma
*.wav, *.aif (uncompressed files only)

fh (force header) argument can be one, zero, boolean or string representing the valid WAVE header.
It is used if an external decoder writes only raw data to stdout. For instance, "faad" under Linux.

The open() returns an instance of a class with the following public methods:
      getnchannels()  -- returns number of audio channels (1 for
                         mono, 2 for stereo)
      getsampwidth()  -- returns sample width in bytes
      getframerate()  -- returns sampling frequency
      getnframes()    -- returns number of audio frames
      getcomptype()   -- returns compression type (always 'NONE' - linear samples)
      getcompname()   -- returns human-readable version of
                         compression type (always 'not compressed' linear samples)
      getparams()     -- returns a tuple consisting of all of the
                         above in the above order
      getmarkers()    -- returns None (for compatibility with the
                         aifc module)
                         The exception goes when aiff file is used.
      getmark(id)     -- raises an error since the mark does not
                         exist (for compatibility with the aifc module)
                         The exception goes when aiff file is used.
      readframes(n)   -- returns at most n frames of decoded audio
      rewind()        -- rewind to the beginning of the audio stream
      setpos(pos)     -- seek to the specified position
      tell()          -- return the current position
      close()         -- close the instance (make it unusable)
The position returned by tell() and the position given to setpos()
are compatible and have nothing to do with the actual position on stdout.
The close() method is called automatically when the class instance
is destroyed.

NOTA BENE:

The setpos() and rewind() are usually not accessible because of on-fly decoding and use of one of them often raises
the IOError: [Erno 29] Illegal seek.

Unfortunately, you cannot give the open read file pointer to open(), not yet.

getnframes() returns correct number of frames, but decoders nearly always cut off some unimportant frames
and therefore be careful about this.
In this case fakewave.readframes() returns empty frames where the "" (empty string) would be returned if asking the external
decoder.

CreateWaveHeader(nchannels=2, sampwidth=2, samplerate=44100) --> string
      Returns the WAVE header string which can be used for force header argument of function open().
      You are adviced to use it when the specifications of the output of external decoder are static and known to you.
      This function is called (without arguments) if the force header argument of open() function is True or 1.

CreateWaveHeaderFromFile(name) --> string
      Returns the WAVE header string which can be used for force header argument of function open().
      The generated header does not always match the output of the external decoder and it is also not 100% correct.
      So you are adviced to use CreateWaveHeader() instead. (When possible)

The following functions have to be called with decoder.py imported as
"import decoder", not "from decoder import *".

CheckForUpdates() --> dictionary or None
      Checks for updates of decoder.py on the official page and mirror.
      If you are not connected to the internet or both servers are unavailable or the downloaded update script is corrupted,
      None is returned. If everything went fine, the dictionary of update script options, with their values, is returned.
      To check for new version do:
      >>> nv = decoder.CheckForUpdates()
      >>> if nv:
      >>>   if nv["__version__"] <= decoder.__version__:
      >>>     print "No new version available!"
      >>>   else:
      >>>     print "A new version is", nv["__version__"]
      >>> else:
      >>>   print "Something wrong with net connection, DNS, servers, uscripts etc."

update (udict=0) --> integer
      Updates decoder.py. This function is designed to help programers when creating
      software like players etc. Instead of packing new decoder.py with updates of your program, make it update itself.
      This way, you can be sure that the users have the latest stable official version.
      udict argument is a dictionary returned by CheckForUpdates() function.
      If it is 0 (default) the CheckForUpdates() will be called automaticaly.
      Firstly, the update() function, tries to make a backup of important files, before it starts updating them.
      If something went wrong while backing up, the error will not be raised.
      After making backup (ZIP file named decoder-__version__-backup.zip) update() tries to download ZIP file and unpack it.
      The existing files will be replaced with newones.
      This function may, also, add some new files and so be carefull when you are using it.
      Keep decoder.py isolated from other parts of your programs and everything will be fine.
      The updated version will be active when you start your program again.
      If you/your program discover that new version makes problem, you can easily rollback to the old one using
      restore() function. You should try the new version right away, and rollback if something is not working, because
      you cannot be sure if you would be able to access the restore() function after importing a new version.
      However, it is unlikely that you would ever need to use restore() function.
      'decoder.py' is strictly backward compatible and heavilly tested for bugs.
      update() returns 0 if it fails in any sense, -1, if there is no new version available, and 1 if everything went fine.
      This function requires write permissions on current working directory of decoder.py.
      WARNING:
            It may happen, that someone redirects your DNS to fool your system and tricks it to download the files
            from another location, protending to be brailleweb.com. The downloaded files may
            contain malicious code and harm your system.
            I hope that this warning would not give somebody an idea.

restore (v=None) --> None
      Rolls back the decoder.py from the backup file.
      If you ran the new version and want to restore it to the previous one,
      you need to specify the version of previous version.
      If you test the decoder.py and you want to restore to previous one, the restore() will be enough.
      The function tries to achieve its goal, but does not raise an error if there is one.
      The adequate backup file 'decoder-__version__-backup.zip' needs to be present in the directory i.e. the update() must be called first.

CLASSES:

Error       --> Exception raised when something is wrong with external decoder's output

fakewave    --> Instance returned by open() function if compressed audio file given

copywaveobj --> Instance that copies information from one wave object to another.
    Methods here:
    -------------
    __init__(self, src, dst, start=None, end=None, bufsize=1024, blocking=True) --> None
        Constructor that initialises copying information from one wave object to another.
        I.e. from Wave_read/like-Wave_read object to Wave_write/like-Wave_write object.
        This method also supports copying from file to file and mixed copying:
        from wave to file and vice versa, but then, you must have in mind that
        file-like.read() and file-like.seek() differs from wave-like.readframes() and wave-like.setpos().
        If you use the file-like/wave-like object that has both
        readframes() and read() or writeframes() and write() or setpos() and seek()
        methods, then, this function will mess the objects pretty badly.
        So be careful.
        The start argument sets the source object to ofset of frames/bytes from which to start copying.
        If you use fakewave object as a source, do not use this, because it will raise the Illegal seek error.
        End is the ofset of frames/bytes after which the copying will stop.
        Bufsize is, of course, the number of frames/bytes copied per one itteration.
        Blocking is the mode of copying informations.
        If it is True, then instance acts like a structural function and you need to wait until the copying is done.
        Else, the copying is launched in a thread, and you can control it using below described methods.

    begin(self) --> None
        A method that really does the copying of data.
        If you call it, and it is already started, nothing will happen.
        If the process is paused, and you call it, the copying will resume.
        If you call it after calling the stop() method, the copying will start again (from the beginning),
        but in structural manner - you will have to wait till the end.
        If you want to restart the unblocking way of copying, then do: a = copywaveobj(...); a.thread(a.begin, ())

    pause(self) --> None
        Freezes the copying (unblocking mode).

    resume(self) --> None
        Resumes the copying (Unblocking mode).
        If copying is not paused, no problems!

    stop(self) --> None
        Stops the copying (unblocking mode).

    status(self) --> int      (1; -1; 0)
        Returns -1, when copying is paused, 1 when it is in progress, and 0 when it is stopped.

    tell(self) --> int
        Returns the number of finished itterations while copying.
        The aproximate number of copied frames (wave-like) or bytes (file-like) is:
        a = copywaveobj(...); print a.bufsize*a.tell()

    wait(self) --> None
        Waits until copying STOPS (unblocking mode).

VARIABLES:
      wildcard --> A list containing all extensions that open() supports.
                   When imported with 'from', it is called "decoder_wildcard"

DEPENDENCIES:

decoder.py depends on mutagen library - to calculate number of frames and create WAVE headers.

In order to make it work (decoder.py), you need external decoders:
lame, faad, flac, oggdec, wmadec (on Windows) and ffmpeg (on Unix).
To install them on Ubuntu/Debian use:
apt-get install lame
apt-get install vorbis-tools
apt-get install faad
apt-get install flac
apt-get install ffmpeg

For Windows:
As I hate searching for dependencies for years and then finding the wrong ones,
you will get them along in the same ZIP as decoder.py.
But better be warned that there might be newer versions somewhere on the internet.
That especially goes for "wmadec" which is still buggy.

In the "codecs.pdc" file you should put commands for external decoders.
How the system reaches them.

Unix common configuration:
lame=lame
faad=faad
flac=flac
ffmpeg=ffmpeg
oggdec=oggdec
wmadec=None

Windows preferable configuration:
lame=./codecs/lame.exe
faad=./codecs/faad.exe
flac=./codecs/flac.exe
ffmpeg=None
oggdec=./codecs/oggdec.exe
wmadec=./codecs/wmadec.exe

If the "./codecs.pdc" does not exist, the above mentioned defaults will be used.

TEST:

decoder.py is tested on:
Ubuntu Linux, Windows 98 SE, Windows XP and Windows 7

TODO:

When you use decoder.py on Windows 98, the console window opens regulary regardless the CREATE_NO_WINDOW creation flag.
This is Windows 9x natural behaviour, but I am sure the way arround must exists.
I would be thankful for any help regarding this "problem".
"""

from subprocess import Popen, PIPE
from fileinfo import info
import os, struct, wave, aifc

if os.name=="nt":
    noWindow = 0x8000000
else: noWindow = 0

__author__   = "Dalen Bernaca"
__version__  = "1.5XB"
__revision__ = "light"

__all__ = ["lame", "faad", "flac", "ffmpeg", "oggdec", "wmadec", "CreateWaveHeaderFromFile", "CreateWaveHeader", "copywaveobj", "acopen", "decoder_wildcard"]

if os.path.exists("codecs.pdc"):
    file = open("codecs.pdc", "r")
    c = file.readlines()
    file.close()
    del file
    d = {}
    for x in c:
        x = x.strip().split("=")
        d[x[0].lower()] = x[1]
    del c, x
    lame = d["lame"]
    faad = d["faad"]
    flac = d["flac"]
    ffmpeg = d["ffmpeg"]
    oggdec = d["oggdec"]
    wmadec = d["wmadec"]
    del d
else:
    if os.name=="nt": pref = "./codecs/"; ext = ".exe"
    else: pref = ""; ext = ""
    lame = pref+"lame"+ext
    faad = pref+"faad"+ext
    flac = pref+"flac"+ext
    ffmpeg = pref+"ffmpeg"+ext
    oggdec = pref+"oggdec"+ext
    wmadec = pref+"wmadec"+ext
    del pref, ext
# Supported filetypes (extensions only)
wildcard = [".mp1", ".mp2", ".mp3", ".mp4", ".m4a", ".m4b", ".aac", ".flac", ".oga", ".ogg", ".wma", ".wav", ".wave", ".aif", ".aiff"]
decoder_wildcard = wildcard

class Error(Exception): pass

def CheckForUpdates ():
    """Checks for updates of decoder.py on the official page and mirror.
    If you are not connected to the internet or both servers are unavailable or the downloaded update script is corrupted,
    None is returned. If everything went fine, the dictionary of update script options, with their values, is returned.
    To check for new version do:
    >>> nv = decoder.CheckForUpdates()
    >>> if nv:
    >>>   if nv["__version__"] <= decoder.__version__:
    >>>     print "No new version available!"
    >>>   else:
    >>>     print "A new version is", nv["__version__"]
    >>> else:
    >>>   print "Something wrong with net connection, DNS, servers, uscripts etc."
    """
    from urllib2 import urlopen, Request
    from sys import platform
    from ConfigParser import ConfigParser
    # The first URL is a script that counts update checkers
    # It increases the counter and returns the file stored on second URL
    # Nothing to worry about, anyway. Just statistics.
    urls = ("http://www.brailleweb.com/cgi-bin/uscript.py",
            "http://www.brailleweb.com/projects/decoder.py",
            "http://brailleweb.webhop.net/decoder.py/updates.pdc")
    for x in urls:
        try:
            req = Request(x)
            req.add_header("User-Agent", "decoder.py/"+__version__+" on "+platform)
            u = urlopen(req)
            cp = ConfigParser()
            cp.readfp(u)
            d = {}
            for y in cp.options("decoder.py"): d[y] = cp.get("decoder.py", y)
            return d
        except: pass

def update (udict=0):
    """Updates decoder.py. udict argument is a dictionary returned by CheckForUpdates() function.
    If it is 0 (default) the CheckForUpdates() will be called automaticaly.
    Firstly, the update() function, tries to make a backup of important files, before it starts updating them.
    If something went wrong while backing up, the error will not be raised.
    After making backup (ZIP file named decoder-__version__-backup.zip) update() tries to download ZIP file and unpack it.
    The existing files will be replaced with newones.
    This function may, also, add some new files and so be carefull when you are using it.
    Keep decoder.py isolated from other parts of your programs and everything will be fine.
    The updated version will be active when you start your program again.
    If you/your program discover that new version makes problem, you can easily rollback to the old one using
    restore() function. You should try the new version right away, and rollback if something is not working, because
    you cannot be sure if you would be able to access the restore() function after importing a new version.
    However, it is unlikely that you would ever need to use restore() function.
    update() returns 0 if it fails in any sense, -1, if there is no new version available, and 1 if everything went fine.
    This function requires write permissions on current working directory.
    """
    if udict is 0: d = CheckForUpdates()
    else: d = udict
    if not d: return 0
    if d["__version__"] <= __version__: return -1
    # But may be that the new version is for Unix only and you are running Windows
    if os.name=="nt" and d["new_win32"]=="no": return -1
    if os.name!="nt" and d["new_unix"]=="no": return -1
    # Change the directory to the directory where this file is living
    olddir = os.getcwd()
    try: os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except: pass
    from urllib2 import urlopen, Request
    from zipfile import ZipFile
    from sys import platform
    # Try to make a backup
    ld = [x.strip() for x in d[__version__.lower()+"-"+("unix", "win32")[os.name=="nt"]+"_filelist"].split(";")]
    # ld is a list of decoder.py important files (of current version)
    # If you created a file which current version does not contain, and new one does,
    # your file will be backed up as well, and replaced by decoder.py one (unfortunately)
    # But the 'will be backed up' part is important
    try: bz = ZipFile("decoder-"+__version__+"-backup.zip", "w")
    except: os.chdir(olddir); return 0
    # Because, if backup fails, then, every other writting action will fail as well.
    for x in ld:
        try: bz.write(x.replace("/", os.sep), x)
        except: pass
    # Fetch new version
    from cStringIO import StringIO
    from __builtin__ import open
    fn = "decoder-"+d["__version__"]+"-" + ("Unix", "Win32")[os.name=="nt"] + ".zip"
    for x in (d["updateurl"], d["mirror"]):
        try:
            req = Request(x+fn)
            req.add_header("User-Agent", "decoder.py/"+__version__+" on "+platform)
            u = urlopen(req)
            z = ZipFile(StringIO(u.read()), "r")
            nl = z.namelist()
            for y in nl:
                # More backing ups
                if os.path.exists(y.replace("/", os.sep)) and y not in ld:
                    try: bz.write(y.replace("/", os.sep), y)
                    except: pass
                yp = y.split("/")
                if len(yp)>1:
                    ydir = os.sep.join(yp[:-1])
                    if not os.path.exists(ydir): os.makedirs(ydir)
                if not yp[0] or not yp[-1]: continue
                f = open(y.replace("/", os.sep), "wb")
                f.write(z.read(y))
                f.close()
            z.close(); bz.close()
            os.chdir(olddir)
            return 1
        except Exception, e: print e
    bz.close()
    os.chdir(olddir)
    return 0

def restore (v=None):
    """Rolls back the decoder.py from the backup file.
    If you ran the new version and want to restore it to the previous one,
    you need to specify the version of previous version.
    If you test the decoder.py and you want to restore to previous one, the restore() will be enough.
    The function tries to achieve its goal, but does not raise an error if there is one."""
    if not v: v = __version__
    olddir = os.getcwd()
    try: os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except: pass
    fn = "decoder-"+v+"-backup.zip"
    if not os.path.exists(fn): os.chdir(olddir); return
    from zipfile import ZipFile
    from __builtin__ import open
    # Just, if read permissions are not here
    try: z = ZipFile(fn, "r")
    except: os.chdir(olddir); return
    for x in z.namelist():
        try:
            f = open(x.replace("/", os.sep), "wb")
            f.write(z.read(x))
            f.close()
        except: pass
    z.close(); os.chdir(olddir)

def CreateWaveHeaderFromFile (name):
    """Returns the wave header string which can be used in force header argument of the open() function.
    The name argument is the path to the audio file which can be recognized by fileinfo module.
    (*.mp1, *.mp2, *.mp3, *.mp4, *.m4a, *.m4b, *.aac, *.wma, *.ogg, *.flac, *.wav, *.aif)
    Note that this is not accurate. In most cases all will be OK, but, for instance,
    when you have the two channeled MP3 file encoded with 24 bits depth, you will not get the correct header.
    The sample width will be assumed as for 16 bits depth i.e. sw = 2,
    which will lead into incorrect reading of stdout and wrong representation of the raw data.
    If you do know what specifications the output of the external decoder is going to have,
    then rather use the CreateWaveHeader() instead.
    I would be delighted if there is someone who can help fix this."""
    import cStringIO
    wh = cStringIO.StringIO()
    wf = wave.open(wh, "w")
    inf = info(name).info
    try: chn = inf.channels
    except: chn = int(inf.mode!=3)+1
    wf.setnchannels(chn)
    try: bps = inf.bits_per_sample # Only MP4 has bits_per_sample
    except:
        bps = 16 # This is stupid, completely mental, really
    wf.setsampwidth((bps+7)//8)
    wf.setframerate(inf.sample_rate)
    wf.setnframes(0)
    wf.writeframes("")
    wh.seek(0)
    return wh.read()

def CreateWaveHeader (nchannels=2, sampwidth=2, samplerate=44100):
    """Returns the wave header string which can be used in force header argument of the open() function.
    If called without arguments it returns 2 channeled, 44100 hz, sample width 2, WAVE header (0 frames)
    Use this when you know what specifications the output of the external decoder is going to have."""
    import cStringIO
    wh = cStringIO.StringIO()
    wf = wave.open(wh, "w")
    wf.setnchannels(nchannels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(samplerate)
    wf.setnframes(0)
    wf.writeframes("")
    wh.seek(0)
    return wh.read()

class copywaveobj:
    """Copies information from one wave object to another.
    I.e. from Wave_read/like-Wave_read object to Wave_write/like-Wave_write object.
    This also supports copying from file to file and mixed copying:
    from wave to file and vice versa.
    If you use the file-like/wave-like object that has both
    readframes() and read() or writeframes() and write() or setpos() and seek()
    methods, then, this will mess the objects pretty badly.
    So be careful."""

    from thread import start_new_thread as thread
    from time import sleep
    # This looks stupid! Doesn't it?  :D
    paused = 0
    stopped = 1
    position = 0
    def __init__ (self, src, dst, start=None, end=None, bufsize=1024, blocking=True):
        # Prepare objects
        try: dst.setnchannels(src.getnchannels())
        except: pass
        try: dst.setframerate(src.getframerate())
        except: pass
        try: dst.setnframes(src.getnframes())
        except: pass
        try: dst.setsampwidth(src.getsampwidth())
        except: pass
        self.src = src
        self.dst = dst
        self.start = start
        self.end = end
        self.bufsize = bufsize
        self.position = 0
        self.stopped = 1; self.paused = 0
        # Copying
        if blocking: self.begin()
        else: self.thread(self.begin, ())

    def begin (self):
        """Copies the data"""
        if self.paused: return self.resume()
        if not self.stopped: return
        self.stopped = 0
        start, end, bufsize = self.start, self.end, self.bufsize
        swrdf = 0
        if hasattr(self.src, "readframes"): self.src.read = self.src.readframes; swrdf = 1
        swwrf = 0
        if hasattr(self.dst, "writeframes"): self.dst.write = self.dst.writeframes; swwrf = 1
        swstp = 0
        if hasattr(self.src, "setpos"): self.src.seek = self.src.setpos; swstp = 1
        if start!=None: self.src.seek(start)
        if swstp: del self.src.seek
        if end!=None:
            startbuf = end/bufsize
            endbuf = end%bufsize
            for x in xrange(startbuf):
                if self.paused: self.wait()
                if self.stopped: break
                self.dst.write(self.src.read(bufsize))
                self.position += 1
            if not self.stopped:
                self.dst.write(self.src.read(endbuf))
                self.position += 1
            if swrdf: del self.src.read
            if swwrf: del self.dst.write
            self.stopped = 1; self.paused = 0
            return
        data = " "
        while data!="":
            if self.paused: self.wait()
            if self.stopped: break
            data = self.src.read(bufsize)
            self.dst.write(data)
            self.position += 1
        if swrdf: del self.src.read
        if swwrf: del self.dst.write
        self.stopped = 1; self.paused = 0

    def pause (self):
        self.paused = 1

    def resume (self):
        self.paused = 0

    def stop (self):
        self.stopped = 1; self.paused = 0

    def status (self):
        if self.paused and not self.stopped: return -1
        elif self.stopped: return 0
        else: return 1

    def tell (self):
        return self.position

    def wait (self):
        """Waits until copying is resumed or stopped"""
        while self.paused and not self.stopped:
            self.sleep(0.002)

class fakewave:
    _nframes = 0
    _nchannels = 0
    _sampwidth = 0
    _framerate = 0
    _comptype = "NONE"
    _compname = "not compressed"
    _soundpos = 0
    _framesize = 0

    """
    The following variables are added later and they don't exist in wav.Wave_read nor in aifc.Aifc_read.
    _chunksize
    _format
    _subchunk1size
    _audioformat
    _byterate
    _blockalign
    _bitspersample
    _dataloc
    These variables does not have their member access functions.
    """
    def __init__ (self, obj, fh=0):
        self.obj = obj
        if fh:
            if isinstance(fh, str): self.forceheader = fh
            else: self.forceheader = CreateWaveHeader()
        else: self.forceheader = 0
        self.close = obj.stdout.close
        self.initfp()

    def __del__ (self):
        self.close()

    def initfp (self):
        """Extracts data in the first 44 bytes in a WAVE stdout"""
        file = self.obj.stdout
        # Read in all data
        header = file.read(44)
        # Verify that the correct identifiers are present
        if (header[0:4] != "RIFF") or (header[12:16] != "fmt "):
            if self.forceheader: header = self.forceheader
            else: raise Error, "file does not start with RIFF id or fmt chunk missing"
        self._chunksize = struct.unpack('<L', header[4:8])[0]
        self._format = header[8:12]
        self._subchunk1size = struct.unpack('<L', header[16:20])[0]
        self._audioformat = struct.unpack('<H', header[20:22])[0]
        self._nchannels = struct.unpack('<H', header[22:24])[0]
        self._framerate = struct.unpack('<L', header[24:28])[0]
        self._byterate = struct.unpack('<L', header[28:32])[0]
        self._blockalign = struct.unpack('<H', header[32:34])[0]
        self._bitspersample = struct.unpack('<H', header[34:36])[0]
        self._sampwidth = (self._bitspersample+7)//8
        self._framesize = self._nchannels*self._sampwidth
        self._dataloc = header.find("data")
        self._nframes = int(self._framerate*info(self.obj.filename).info.length)

    def readframes (self, nframes):
        r = self.obj.stdout.read(nframes*self._framesize)
        if r=="" and self._soundpos+nframes<=self._nframes:
            r = (nframes*self._framesize)*"\x00"
        if r!="": self._soundpos += nframes
        return r

    def getnframes (self):
        return self._nframes

    def getnchannels (self):
        return self._nchannels

    def getframerate (self):
        return self._framerate

    def getsampwidth (self):
        return self._sampwidth

    def setpos (self, pos):
        pos = int(pos)
        l = self._nframes
        if pos < 0 or pos > l:
            raise Error, "position not in range"
        self.obj.stdout.seek(pos*self._framesize)
        self._soundpos = pos

    def tell (self):
        return self._soundpos

    def rewind (self):
        self.obj.stdout.seek(0)
        self._soundpos = 0

    def getmarkers (self): pass

    def getmark (self, id):
        raise Error, "no marks"

    def getcomptype (self):
        return self._comptype

    def getcompname (self):
        return self._compname

    def getparams (self):
        return self.getnchannels(), self.getsampwidth(), \
            self.getframerate(), self.getnframes(), \
            self.getcomptype(), self.getcompname()

    def getfp (self):
        return self.obj

def open (name, fh=0):
    name = os.path.normpath(name)
    if not os.path.exists(name):
        raise IOError, (2, "No such file or directory: '%s'" % name)
    ext = os.path.splitext(name)[1][1:].lower()
    if ext in ("mp4", "m4a", "m4b", "aac"):
        if os.name=="nt": cline = [faad, "-q", "-w", name]
        else: cline = [faad, "-q", "-f", "2", "-w", name]
        po = Popen(cline, shell=0, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=noWindow)
        po.stdin.close(); po.stderr.close()
        po.filename = name
        wf = fakewave(po, fh)
    elif ext=="ogg":
        if os.name=="nt": cline = [oggdec, "--stdout", name]
        else: cline = [oggdec, "-q", "-o", "-", name]
        po = Popen(cline, shell=0, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=noWindow)
        po.stdin.close(); po.stderr.close()
        po.filename = name
        wf = fakewave(po, fh)
    elif ext in ("wav", "wave"):
        wf = wave.open(name, "r")
    elif ext in ("aiff", "aif"):
        wf = aifc.open(name, "r")
    elif ext in ("mp1", "mp2", "mp3"):
        cline = [lame, "--quiet", "--decode", name, "-"]
        po = Popen(cline, shell=0, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=noWindow)
        po.stdin.close(); po.stderr.close()
        po.filename = name
        wf = fakewave(po, fh)
    elif ext in ("flac", "oga"):
        cline = [flac, "--silent", "--stdout", "-d", name]
        po = Popen(cline, shell=0, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=noWindow)
        po.stdin.close(); po.stderr.close()
        po.filename = name
        wf = fakewave(po, fh)
    elif ext=="wma":
        if os.name=="nt": cline = [wmadec, "-w", name]
        else: cline = [ffmpeg, "-i", name, "-f", "wav", "-"]
        po = Popen(cline, shell=0, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=noWindow)
        po.stdin.close(); po.stderr.close()
        po.filename = name
        wf = fakewave(po, fh)
    else: wf = None
    return wf

acopen = open
