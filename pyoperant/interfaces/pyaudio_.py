import pyaudio
import wave
import logging
from pyoperant.interfaces import base_
from pyoperant import InterfaceError

logger = logging.getLogger(__name__)
# TODO: Clean up _stop_wav logging changes

class PyAudioInterface(base_.BaseInterface):
    """Class which holds information about an audio device

    assign a simple callback function that will execute on each frame
    presentation by writing interface.callback

    interface.callback() should return either True (to continue playback) or
    False (to terminate playback)

    Before assigning any callback function, please read the following:
    https://www.assembla.com/spaces/portaudio/wiki/Tips_Callbacks

    """
    def __init__(self,device_name='default',*args,**kwargs):
        super(PyAudioInterface, self).__init__(*args,**kwargs)
        self.device_name = device_name
        self.device_index = None
        self.stream = None
        self.wf = None
        self.callback = None
        self.open()

    def open(self):
        self.pa = pyaudio.PyAudio()
        for index in range(self.pa.get_device_count()):
            if self.device_name == self.pa.get_device_info_by_index(index)['name']:
                logger.debug("Found device %s at index %d" % (self.device_name, index))
                self.device_index = index
                break
            else:
                self.device_index = None
        if self.device_index == None:
            raise InterfaceError('could not find pyaudio device %s' % (self.device_name))

        self.device_info = self.pa.get_device_info_by_index(self.device_index)

    def close(self):
        logger.debug("Closing device")
        try:
            self.stream.close()
        except AttributeError:
            self.stream = None
        try:
            self.wf.close()
        except AttributeError:
            self.wf = None
        self.pa.terminate()

    def validate(self):
        if self.wf is not None:
            return True
        else:
            raise InterfaceError('there is something wrong with this wav file')

    def _get_stream(self,start=False):
        """
        """
        def _callback(in_data, frame_count, time_info, status):
            try:
                cont = self.callback()
            except TypeError:
                cont = True

            if cont:
                data = self.wf.readframes(frame_count)
                return (data, pyaudio.paContinue)
            else:
                return (0, pyaudio.paComplete)

        self.stream = self.pa.open(format=self.pa.get_format_from_width(self.wf.getsampwidth()),
                                   channels=self.wf.getnchannels(),
                                   rate=self.wf.getframerate(),
                                   output=True,
                                   output_device_index=self.device_index,
                                   start=start,
                                   stream_callback=_callback)

    def _queue_wav(self,wav_file,start=False):
        logger.debug("Queueing wavfile %s" % wav_file)
        self.wf = wave.open(wav_file)
        self.validate()
        self._get_stream(start=start)

    def _play_wav(self):
        logger.debug("Playing wavfile")
        self.stream.start_stream()

    def _stop_wav(self):
        try:
            logger.debug("Attempting to close stream")
            logger.debug("There are currently %d open streams" % len(self.pa._streams))
            logger.debug("Stream activity: %s, %s" % (self.stream.is_active(), self.stream.is_stopped()))
            # self.stream.stop_stream()
            # logger.debug("Stream stopped")
            # while self.stream.is_active():
            #     logger.debug("Stream is still active!")
            #     pass
            self.stream.close()
            logger.debug("Stream closed")
        except AttributeError:
            self.stream = None
