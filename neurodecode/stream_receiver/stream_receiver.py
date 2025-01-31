import time
from threading import Thread

import pylsl
import numpy as np

from ._stream import StreamEEG, StreamMarker
from .. import logger


class StreamReceiver:
    """
    Class for data acquisition from LSL streams.

    It supports the streams of:
        - EEG
        - Markers

    Parameters
    ----------
    logger : logger
    winsize : int
        To extract the latest winsize samples from the buffer [secs].
    stream_name : list | str
        Servers' name or list of servers' name to connect to.
        None: no constraint.
    eeg_only : bool
        If true, ignores non-EEG servers.
    """

    def __init__(self, bufsize=1, winsize=1, stream_name=None, eeg_only=False):
        self._acquisition_threads = dict()
        self.connect(bufsize, winsize, stream_name, eeg_only)

    def connect(self, bufsize=1, winsize=1, stream_name=None, eeg_only=False):
        """
        Search for the available streams on the LSL network and connect to the
        appropriate ones. If a LSL stream fullfills the requirements (name...),
        a connection is established.

        This function is called while instanciating a StreamReceiver and can be
        recall to reconnect to the LSL streams.

        Parameters
        ----------
        bufsize : int
            The buffer's size [secs]. 1-day is the maximum size.
            Large buffer may lead to a delay if not pulled frequently.
        winsize : int
            To extract the latest winsize samples from the buffer [secs].
        stream_name : list | str
            Servers' name or list of servers' name to connect to.
            None: no constraint.
        eeg_only : bool
            If true, ignore non-EEG servers.
        """
        self._streams = dict()
        self._is_connected = False
        server_found = False

        while not server_found:

            if stream_name is None:
                logger.info(
                    "Looking for available lsl streaming servers...")
            else:
                logger.info(
                    f"Looking for server(s): '{stream_name}'...")

            streamInfos = pylsl.resolve_streams()

            if len(streamInfos) > 0:
                for streamInfo in streamInfos:

                    # EEG streaming server only?
                    if eeg_only and streamInfo.type().lower() != 'eeg':
                        logger.info(f'Stream {streamInfo.name()} skipped.')
                        continue
                    # connect to a specific amp only?
                    if isinstance(stream_name, str) and \
                            streamInfo.name() != stream_name:
                        if stream_name in streamInfo.name():
                            logger.info(
                                f'Stream {stream_name} skipped, '
                                f'however {streamInfo.name()} exists.')
                        continue
                    if isinstance(stream_name, (list, tuple)) and \
                            streamInfo.name() not in stream_name:
                        logger.info(f'Stream {streamInfo.name()} skipped.')
                        continue
                    # do not connect to StreamRecorderInfo
                    if streamInfo.name() == 'StreamRecorderInfo':
                        continue

                    # EEG stream
                    if streamInfo.type().lower() == "eeg":
                        self._streams[streamInfo.name()] = StreamEEG(
                            streamInfo, bufsize, winsize)
                    # Marker stream
                    elif streamInfo.nominal_srate() == 0:
                        self._streams[streamInfo.name()] = StreamMarker(
                            streamInfo, bufsize, winsize)

                    server_found = True
            time.sleep(1)

        for stream in self._streams:
            if stream not in self._acquisition_threads.keys():
                self._acquisition_threads[stream] = None

        self.show_info()
        self._is_connected = True
        logger.info('Ready to receive data from the connected streams.')

    def show_info(self):
        """
        Display the informations about the connected streams.
        """
        for stream in self.streams:
            logger.info("--------------------------------"
                        "--------------------------------")
            logger.info(f"The stream {stream} is connected to:")
            self.streams[stream].show_info()

    def disconnect_stream(self, stream_name=None):
        """
        Disconnects the stream 'stream_name' from the StreamReceiver.
        If several streams are connected, specify the name.

        Parameters
        ----------
        stream_name : str
            The name of the stream to extract from.
        """
        if len(self.streams) == 1:
            stream_name = list(self.streams.keys())[0]
        elif stream_name is None:
            logger.error(
                "Please provide a stream name to remove it.")
            raise ValueError

        try:
            self.streams[stream_name]._inlet.close_stream()
            del self.streams[stream_name]
        except KeyError:
            logger.error(
                f"The stream '{stream_name}' does not exist. Skipping.")

    def acquire(self):
        """
        Read data from the streams and fill their buffer using threading.
        """
        for stream in self._streams:
            if self._acquisition_threads[stream] is not None and \
                    self._acquisition_threads[stream].is_alive():
                continue

            thread = Thread(target=self._streams[stream].acquire, args=[])
            thread.daemon = True
            thread.start()
            self._acquisition_threads[stream] = thread

    def get_window(self, stream_name=None):
        """
        Get the latest window from a stream's buffer.
        If several streams are connected, specify the name.

        Parameters
        ----------
        stream_name : str
            The name of the stream to extract from.

        Returns
        -------
        data : np.array
             The data [samples x channels]
        timestamps : np.array
             The timestamps [samples]
        """
        if len(self.streams) == 1:
            stream_name = list(self.streams.keys())[0]
        elif stream_name is None:
            logger.error(
                "Please provide a stream name to get its latest window.")
            raise ValueError

        winsize = self.streams[stream_name].buffer.winsize
        self.is_connected
        try:
            self._acquisition_threads[stream_name].join()
        except AttributeError:
            logger.warning('.acquire() must be called before .get_window().')
            return (np.empty((0, len(self.streams[stream_name].ch_list))),
                    np.array([]))

        try:
            window = self.streams[stream_name].buffer.data[-winsize:]
            timestamps = self.streams[stream_name].buffer.timestamps[-winsize:]
        except IndexError:
            logger.warning(
                f"The buffer of {self._streams[stream_name].name} "
                "does not contain enough samples.")
            window = self.streams[stream_name].buffer.data[:]
            timestamps = self.streams[stream_name].buffer.timestamps[:]

        if len(timestamps) > 0:
            return (np.array(window), np.array(timestamps))
        else:
            return (np.empty((0, len(self.streams[stream_name].ch_list))),
                    np.array([]))

    def get_buffer(self, stream_name=None):
        """
        Get the entire buffer of a stream in numpy format.
        If several streams are connected, specify the name.

        Parameters
        ----------
        stream_name : str
            The name of the stream to extract from.

        Returns
        -------
        data : np.array
            The data [samples x channels]
        timestamps : np.array
            The timestamps [samples]
        """
        if len(self.streams) == 1:
            stream_name = list(self.streams.keys())[0]
        elif stream_name is None:
            logger.error(
                "Please provide a stream name to get its buffer.")
            raise ValueError

        self.is_connected
        try:
            self._acquisition_threads[stream_name].join()
        except AttributeError:
            logger.warning('.acquire() must be called before .get_window().')
            return (np.empty((0, len(self.streams[stream_name].ch_list))),
                    np.array([]))

        if len(self.streams[stream_name].buffer.timestamps) > 0:
            return (np.array(self.streams[stream_name].buffer.data),
                    np.array(self.streams[stream_name].buffer.timestamps))
        else:
            return (np.empty((0, len(self.streams[stream_name].ch_list))),
                    np.array([]))

    def reset_buffer(self, stream_name=None):
        """
        Clear the stream's buffer.
        If several streams are connected, specify the name.

        Parameters
        ----------
        stream_name : str
            The stream's name.
        """
        if len(self.streams) == 1:
            stream_name = list(self.streams.keys())[0]
        elif stream_name is None:
            logger.error(
                "Please provide a stream name to get reset its buffer.")
            raise ValueError

        self.streams[stream_name].buffer.reset_buffer()

    def reset_all_buffers(self):
        """
        Clear all the streams' buffer.
        """
        for stream in self._streams:
            self.reset_buffer(stream)

    @property
    def is_connected(self):
        """
        Check the connection status and automatically connect if not connected.
        """
        while not self._is_connected:
            logger.error('No LSL servers connected yet. '
                         'Trying to connect automatically.')
            self.connect()
            time.sleep(1)

        return self._is_connected

    @is_connected.setter
    def is_connected(self, is_connected):
        logger.warning("This attribute cannot be modified.")

    @property
    def streams(self):
        """
        The connected streams list.
        """
        return self._streams

    @streams.setter
    def streams(self, streams):
        logger.warning("The connected streams cannot be modified.")
