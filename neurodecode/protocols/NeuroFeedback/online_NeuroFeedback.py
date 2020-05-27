#!/usr/bin/env python3
#coding:utf-8
"""
  Author:  Arnaud Desvachez --<arnaud.desvachez@gmail.com>
  Purpose: Online protocol for deep meditation state neurofeedback.
  Created: 14.10.2019
"""

import mne
import os
import sys
import time
import numpy as np
import multiprocessing as mp
import pygame.mixer as pgmixer

import neurodecode.utils.pycnbi_utils as pu
import neurodecode.triggers.pyLptControl as pyLptControl

from neurodecode import logger
from neurodecode.protocols.viz_bars import BarVisual
from neurodecode.utils import q_common as qc
from neurodecode.gui.streams import redirect_stdout_to_queue
from neurodecode.triggers.trigger_def import trigger_def
from neurodecode.stream_receiver.stream_receiver import StreamReceiver

os.environ['OMP_NUM_THREADS'] = '1' # actually improves performance for multitaper
mne.set_log_level('ERROR')          # DEBUG, INFO, WARNING, ERROR, or CRITICAL

def add_to_queue(xs, x):
    xs[:-1] = xs[1:]
    xs[-1] = x
    return xs

def mix_sounds(style, sounds, feature_value):
    s1, s2 = sounds

    if style == 'REPLACING':
        s1.set_volume(feature_value)
        s2.set_volume(1 - feature_value)
    elif style == 'ADDITIVE_NEGATIVE':
        s2.set_volume(1 - feature_value)
    elif style == 'ADDITIVE_POSITIVE':
        s2.set_volume(feature_value)
    else:
        raise ValueError('MusicMixStyle not supported')

#----------------------------------------------------------------------
def check_config(cfg):
    """
    Ensure that the config file contains the parameters
    """
    critical_vars = {
        'COMMON': ['TRIGGER_DEVICE',
                   'TRIGGER_FILE',
                   'START_VOICE_FILE',
                   'END_VOICE_FILE',
                   'ALPHA_CHANNELS',
                   'THETA_CHANNELS',
                   'MUSIC_STATE_1_PATH',
                   'MUSIC_STATE_2_PATH',
                   'FEATURE_TYPE',
                   'MUSIC_MIX_STYLE',
                   'WINDOWSIZE',
                   'STREAMBUFFER'],
        'ALPHA_FREQ': ['min', 'max'],
        'THETA_FREQ': ['min', 'max'],
        }

    optional_vars = {
        'AMP_NAME':None,
        'AMP_SERIAL':None,
        'SPATIAL_FILTER': None,
        'SPATIAL_CHANNELS': None,
        'GLOBAL_TIME': 30.0 * 60,
        'NJOBS': 1,
        'SCREEN_POS': (0, 0)
    }

    for key in critical_vars['COMMON']:
        if not hasattr(cfg, key):
            logger.error('%s is a required parameter' % key)
            raise RuntimeError

    if not hasattr(cfg, 'ALPHA_FREQ'):
        logger.error('"ALPHA_FREQ" not defined in config.')
        raise RuntimeError
    for v in critical_vars['ALPHA_FREQ']:
        if v not in cfg.ALPHA_FREQ:
            logger.error('%s not defined in config.' % v)
            raise RuntimeError

    if not hasattr(cfg, 'THETA_FREQ'):
        logger.error('"THETA_FREQ" not defined in config.')
        raise RuntimeError
    for v in critical_vars['THETA_FREQ']:
        if v not in cfg.THETA_FREQ:
            logger.error('%s not defined in config.' % v)
            raise RuntimeError

    for key in optional_vars:
        if not hasattr(cfg, key):
            setattr(cfg, key, optional_vars[key])
            logger.warning('Setting undefined parameter %s=%s' % (key, getattr(cfg, key)))


#----------------------------------------------------------------------
def find_lsl_stream(cfg, state):
    """
    Find the amplifier name and its serial number to connect to

    cfg = config file
    state = GUI sharing variable
    """
    if cfg.AMP_NAME is None and cfg.AMP_SERIAL is None:
        amp_name, amp_serial = pu.search_lsl(state, ignore_markers=True)
    else:
        amp_name = cfg.AMP_NAME
        amp_serial = cfg.AMP_SERIAL

    return amp_name, amp_serial

#----------------------------------------------------------------------
def connect_lsl_stream(cfg, amp_name, amp_serial):
    """
    Connect to the lsl stream corresponding to the provided amplifier
    name and serial number

    cfg = config file
    amp_name =  amplifier's name to connect to
    amp_serial = amplifier's serial number
    """
    # Open the stream
    sr = StreamReceiver(window_size=cfg.WINDOWSIZE, buffer_size=cfg.STREAMBUFFER, amp_serial=amp_serial, eeg_only=False, amp_name=amp_name)

    return sr

#----------------------------------------------------------------------
def init_psde(cfg, sfreq):
    """
    Initialize the PSD estimators (MNE lib) for computation of alpha
    and theta bands PSD

    cfg = config file
    sfreq = sampling rate
    """
    psde_alpha = mne.decoding.PSDEstimator(sfreq=sfreq, fmin=cfg.ALPHA_FREQ['min'], fmax=cfg.ALPHA_FREQ['max'], bandwidth=None, \
             adaptive=False, low_bias=True, n_jobs=cfg.NJOBS, normalization='length', verbose=None)

    psde_theta = mne.decoding.PSDEstimator(sfreq=sfreq, fmin=cfg.THETA_FREQ['min'], fmax=cfg.THETA_FREQ['max'], bandwidth=None, \
             adaptive=False, low_bias=True, n_jobs=cfg.NJOBS, normalization='length', verbose=None)

    return psde_alpha, psde_theta

#----------------------------------------------------------------------
def init_feedback_sounds(path1, path2):
    pgmixer.init()
    pgmixer.set_num_channels(4)

    m1 = pgmixer.Sound(path1)
    m2 = pgmixer.Sound(path2)
    m1.set_volume(1.0)
    m2.set_volume(0.0)

    return m1, m2

#----------------------------------------------------------------------
def compute_psd(window, psde):
    """
    Compute the relative PSD

    psde = PSD estimator
    psd_ref = psd reference value defined during an offline run
    """
    psd = psde.transform(window.reshape((1, window.shape[0], -1)))
    psd = psd.reshape((psd.shape[1], psd.shape[2]))                 # channels x frequencies
    psd =  np.sum(psd, axis=1)                                      #  Over frequencies
    return np.mean(psd)                                            #  Over channels


keys = {'left':81, 'right':83, 'up':82, 'down':84, 'pgup':85, 'pgdn':86,
    'home':80, 'end':87, 'space':32, 'esc':27, ',':44, '.':46, 's':115, 'c':99,
    '[':91, ']':93, '1':49, '!':33, '2':50, '@':64, '3':51, '#':35}

#----------------------------------------------------------------------
def run(cfg, state=mp.Value('i', 1), queue=None):
    """
    Online protocol for Alpha/Theta neurofeedback.
    """

    redirect_stdout_to_queue(logger, queue, 'INFO')

    # Wait the recording to start (GUI)
    while state.value == 2: # 0: stop, 1:start, 2:wait
        pass

    # Protocol runs if state equals to 1
    if not state.value:
        sys.exit(-1)


    cfg.tdef = trigger_def(cfg.TRIGGER_FILE)
    trigger = pyLptControl.Trigger(state, cfg.TRIGGER_DEVICE)
    if trigger.init(50) == False:
        logger.error('\n** Error connecting to trigger device.')
        raise RuntimeError

    #----------------------------------------------------------------------
    # LSL stream connection
    #----------------------------------------------------------------------
    # chooose amp
    amp_name, amp_serial = find_lsl_stream(cfg, state)

    # Connect to lsl stream
    sr = connect_lsl_stream(cfg, amp_name, amp_serial)

    # Get sampling rate
    sfreq = sr.get_sample_rate()

    # Get trigger channel
    trg_ch = sr.get_trigger_channel()

    #----------------------------------------------------------------------
    # PSD estimators initialization
    #----------------------------------------------------------------------
    psde_alpha, psde_theta = init_psde(cfg, sfreq)

    #----------------------------------------------------------------------
    # Initialize the feedback sounds
    #----------------------------------------------------------------------
    sound_1, sound_2 = init_feedback_sounds(cfg.MUSIC_STATE_1_PATH,
                                            cfg.MUSIC_STATE_2_PATH)

    #----------------------------------------------------------------------
    # Main
    #----------------------------------------------------------------------

    current_max = 0

    last_ratio = None
    measured_psd_ratios = np.full(cfg.WINDOW_SIZE_PSD_MAX, np.nan)

    last_ts = None

    pgmixer.music.load(cfg.START_VOICE_FILE)

    # Init feedback
    viz = BarVisual(False, screen_pos=cfg.SCREEN_POS, screen_size=cfg.SCREEN_SIZE)
    viz.fill()
    viz.put_text('Close your eyes and relax')
    viz.update()

    # PLay the start voice
    pgmixer.music.play()

    # Wait a key press
    key = 0xFF & cv2.waitKey(0)
    if key == keys['esc'] or not state.value:
        sys.exit(-1)

    viz.fill()
    viz.put_text('Recording in progress')
    viz.update()

    trigger.signal(cfg.tdef.INIT)

    global_timer = qc.Timer(autoreset=False)
    internal_timer = qc.Timer(autoreset=True)

    sound_1.play(loops=-1)
    sound_2.play(loops=-1)
    while state.value == 1 and global_timer.sec() < cfg.GLOBAL_TIME:

        #----------------------------------------------------------------------
        # Data acquisition
        #----------------------------------------------------------------------
        #  Pz = 8
        sr.acquire()
        window, tslist = sr.get_window()    # window = [samples x channels]
        window = window.T                   # window = [channels x samples]

        # Check if proper real-time acquisition
        if last_ts:
            tsnew = np.where(np.array(tslist) > last_ts)[0]
            if len(tsnew) == 0:
                logger.warning('There seems to be delay in receiving data.')
                time.sleep(1)
                continue

        # Spatial filtering
        window = pu.preprocess(window, sfreq=sfreq, spatial=cfg.SPATIAL_FILTER, spatial_ch=cfg.SPATIAL_CHANNELS)

        #----------------------------------------------------------------------
        # Computing the Power Spectrum Densities using multitapers
        #----------------------------------------------------------------------
        # PSD

        if cfg.FEATURE_TYPE == 'THETA':
            feature = compute_psd(window, psde_theta)
        elif cfg.FEATURE_TYPE == 'ALPHA_THETA':
            psd_alpha = compute_psd(window, psde_alpha)
            psd_theta = compute_psd(window, psde_theta)

            feature = psd_alpha / psd_theta

        #----------------------------------------------------------------------
        # Auditory feedback
        #----------------------------------------------------------------------

        measured_psd_ratios = add_to_queue(measured_psd_ratios, feature)
        current_music_ratio  = feature / np.max(measured_psd_ratios[~np.isnan(measured_psd_ratios)])

        if last_ratio is not None:
            applied_music_ratio = last_ratio + (current_music_ratio - last_ratio) * 0.25
        else:
            applied_music_ratio = current_music_ratio

        mix_sounds(style=cfg.MUSIC_MIX_STYLE,
                   sounds=(sound_1, sound_2),
                   feature_value=applied_music_ratio)

        last_ts = tslist[-1]
        internal_timer.sleep_atleast(cfg.TIMER_SLEEP)

    trigger.signal(cfg.tdef.END)

    # Remove the text
    viz.fill()
    viz.put_text('Recording is finished')
    viz.update()

    # Ending voice
    pgmixer.music.load(cfg.END_VOICE_FILE)
    pgmixer.music.play()
    time.sleep(5)

    # Close cv2 window
    viz.finish()

#----------------------------------------------------------------------
def batch_run(cfg_module):
    """
    For batch script
    """
    cfg = pu.load_config(cfg_module)
    check_config(cfg)
    run(cfg)

#----------------------------------------------------------------------
if __name__ == '__main__':

    cfg_module = '/home/sam/proj/epfl/eeg-meditation-project/neurodecode_scripts/NeuroFeedback/sam-NeuroFeedback/config_online_sam-NeuroFeedback.py'
    #if len(sys.argv) < 2:
    #    cfg_module = input('Config module name? ')
    #else:
    #    cfg_module = sys.argv[1]
    batch_run(cfg_module)
