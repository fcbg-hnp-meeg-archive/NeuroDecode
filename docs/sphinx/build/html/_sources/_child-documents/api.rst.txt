=================
API Documentation
=================

This is the API documentation for ``NeuroDecode``.

Stream Receiver: :mod:`neurodecode.stream_receiver`
===================================================

.. automodule:: neurodecode.stream_receiver
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.stream_receiver

.. autosummary::
   :nosignatures:
   :toctree: generated

    StreamReceiver
    StreamMarker
    StreamEEG
    Buffer

.. code-block:: python

    from neurodecode.stream_receiver import StreamReceiver
    from neurodecode.utils.timer import Timer

    stream_name = int(input("Provide the name of the stream you want to acquire \n>> "))

    # Instance a StreamReceiver, which will look for all the available streams on the LSL network.
    sr = StreamReceiver(window_size=0.5, buffer_size=1, amp_name=stream_name, eeg_only=False)


    # Timer for acquisition rate, here 20 Hz
    tm = Timer(autoreset=True)

    while True:

        # Acquire data from all the connected LSL streams by filling each associated buffers.
        sr.acquire()

        # Extract the latest window from the buffer of the chosen stream.
        window, tslist = sr.get_window(stream_name=stream_name)              # window = [samples x channels], tslist = [samples]

        '''
        Add your processing here
        '''

        tm.sleep_atleast(0.05)


Stream Viewer: :mod:`neurodecode.stream_viewer`
===============================================

.. automodule:: neurodecode.stream_viewer
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.stream_viewer

.. autosummary::
   :nosignatures:
   :toctree: generated

    StreamViewer

.. code-block:: python

    from neurodecode.stream_viewer import StreamViewer
    sv = StreamViewer()
    sv.start()


Stream Recorder: :mod:`neurodecode.stream_recorder`
===================================================

.. automodule:: neurodecode.stream_recorder
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.stream_recorder

.. autosummary::
   :nosignatures:
   :toctree: generated

    StreamRecorder

.. code-block:: python

    from neurodecode.stream_recorder import StreamRecorder
    sr = StreamRecorder(record_dir="C:/")
    sr.start(amp_name="Biosemi", eeg_only=False, verbose=False)
    input(">> Press ENTER to stop the recording \n")
    sr.stop()


Stream Player: :mod:`neurodecode.stream_player`
===============================================

.. automodule:: neurodecode.stream_player
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.stream_player

.. autosummary::
   :nosignatures:
   :toctree: generated

    StreamPlayer
    Streamer

.. code-block:: python

    from neurodecode.stream_player import StreamPlayer
    sp = StreamPlayer(server_name='StreamPlayer', fif_file=r'C:\test.fif', chunk_size=16)
    sp.start()
    input("\n>> Press ENTER to stop streaming \n")
    sp.stop()


Trigger: :mod:`neurodecode.triggers`
====================================

.. automodule:: neurodecode.triggers
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.triggers

.. autosummary::
   :nosignatures:
   :toctree: generated

   Trigger
   TriggerDef

.. code-block:: python

    from neurodecode.triggers import Trigger, TriggerDef

    # Load from file the events pairs (str-int)
    tdef = TriggerDef(r'./triggerdef_template.ini')

    # Instance a communication with the desktop LPT.
    trg = Trigger(lpttype='DESKTOP', portaddr=0x378)

    # Initialize the trigger duration to 50ms
    trg.init(50)

    # Send int event: START_TRIAL
    trg.signal(tdef.START_TRIAL)


Decoder: :mod:`neurodecode.decoder`
===================================


.. automodule:: neurodecode.decoder
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.decoder

.. autosummary::
   :nosignatures:
   :toctree: generated

   BCIDecoder
   BCIDecoderDaemon
   get_decoder_info
   check_speed
   sample_decoding
   log_decoding
   compute_features
   feature2chz

Utils :mod:`neurodecode.utils`
==============================

:mod:`neurodecode.utils.benchmark`
----------------------------------

.. automodule:: neurodecode.utils.benchmark
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.utils.benchmark

.. autosummary::
   :nosignatures:
   :toctree: generated

   benchmark_BCIdecoder
   benchmark_multitaper

:mod:`neurodecode.utils.io`
---------------------------

.. automodule:: neurodecode.utils.io
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.utils.io

.. autosummary::
   :nosignatures:
   :toctree: generated

   pcl2fif
   any2fif
   dir_any2fif
   read_raw_fif
   read_raw_fif_multi
   load_config
   get_file_list
   get_dir_list
   make_dirs
   write_set
   dir_write_set

:mod:`neurodecode.utils.layouts`
--------------------------------

.. automodule:: neurodecode.utils.layouts
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.utils.layouts

.. autosummary::
   :nosignatures:
   :toctree: generated

   Layout

:mod:`neurodecode.utils.lsl`
----------------------------

.. automodule:: neurodecode.utils.lsl
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.utils.lsl

.. autosummary::
   :nosignatures:
   :toctree: generated

   start_server
   start_client
   list_lsl_streams
   search_lsl
   lsl_channel_list

:mod:`neurodecode.utils.math`
-----------------------------

.. automodule:: neurodecode.utils.math
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.utils.math

.. autosummary::
   :nosignatures:
   :toctree: generated

   sigmoid
   dirichlet
   beta
   poisson
   average_every_n

:mod:`neurodecode.utils.preprocess`
-----------------------------------

.. automodule:: neurodecode.utils.preprocess
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.utils.preprocess

.. autosummary::
   :nosignatures:
   :toctree: generated

   available_transformation
   preprocess
   current_source_density
   notch_filter
   spectral_filter
   laplacian_filter
   rename_channels
   resample
   set_channel_types
   set_eeg_reference
   set_montage
   dir_preprocess
   dir_current_source_density
   dir_notch_filter
   dir_laplacian_filter
   dir_rename_channels
   dir_resample
   dir_set_channel_types
   dir_set_eeg_reference
   dir_set_montage

:mod:`neurodecode.utils.timer`
------------------------------

.. automodule:: neurodecode.utils.timer
    :no-members:
    :no-inherited-members:

.. currentmodule:: neurodecode.utils.timer

.. autosummary::
   :nosignatures:
   :toctree: generated

   Timer
