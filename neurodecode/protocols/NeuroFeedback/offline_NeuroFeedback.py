#!/usr/bin/env python3
#coding:utf-8
"""
  Author:  Arnaud Desvachez --<arnaud.desvachez@gmail.com>
  Purpose: Offline protocol for deep meditation state neurofeedback.
  Created: 15.10.2019
"""
import sys
import cv2
import time 
import multiprocessing as mp
import pygame.mixer as pgmixer

from builtins import input

import neurodecode.utils.pycnbi_utils as pu
import neurodecode.triggers.pyLptControl as pyLptControl

from neurodecode import logger
from neurodecode.utils import q_common as qc
from neurodecode.protocols.viz_bars import BarVisual
from neurodecode.triggers.trigger_def import trigger_def
from neurodecode.gui.streams import redirect_stdout_to_queue

#----------------------------------------------------------------------
def check_config(cfg):
    """
    Ensure that the config file contains the parameters
    """
    critical_vars = {
        'COMMON': ['TRIGGER_DEVICE',
                   'TRIGGER_FILE',
                   'SCREEN_SIZE',
                   'START_VOICE_FILE',
                   'END_VOICE_FILE'],
    }
    optional_vars = {
        'GLOBAL_TIME': 2 * 60,
        'SCREEN_POS': (0, 0),
        'GLASS_USE':False,
    }
    
    for key in critical_vars['COMMON']:
        if not hasattr(cfg, key):
            logger.error('%s is a required parameter' % key)
            raise RuntimeError
    
    for key in optional_vars:
        if not hasattr(cfg, key):
            setattr(cfg, key, optional_vars[key])
            logger.warning('Setting undefined parameter %s=%s' % (key, getattr(cfg, key)))    

#----------------------------------------------------------------------
def run(cfg, state=mp.Value('i', 1), queue=None):
    """
    Offline protocol for Alpha/Theta neurofeedback.
    """
    
    # visualizer
    keys = {'left':81, 'right':83, 'up':82, 'down':84, 'pgup':85, 'pgdn':86,
        'home':80, 'end':87, 'space':32, 'esc':27, ',':44, '.':46, 's':115, 'c':99,
        '[':91, ']':93, '1':49, '!':33, '2':50, '@':64, '3':51, '#':35}
    
    redirect_stdout_to_queue(logger, queue, 'INFO')
    
    # Wait the recording to start (GUI)
    while state.value == 2: # 0: stop, 1:start, 2:wait
        pass

    # Protocol runs if state equals to 1
    if not state.value:
        sys.exit(-1)
    
    global_timer = qc.Timer(autoreset=False)
    
    # Init trigger communication
    cfg.tdef = trigger_def(cfg.TRIGGER_FILE)
    trigger = pyLptControl.Trigger(state, cfg.TRIGGER_DEVICE)
    if trigger.init(50) == False:
        logger.error('\n** Error connecting to trigger device.')
        raise RuntimeError
    
    # Preload the starting voice
    pgmixer.init()
    pgmixer.music.load(cfg.START_VOICE_FILE)   
    
    # Init feedback
    viz = BarVisual(cfg.GLASS_USE, screen_pos=cfg.SCREEN_POS, screen_size=cfg.SCREEN_SIZE)
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
    
    #----------------------------------------------------------------------
    # Main
    #----------------------------------------------------------------------        
    trigger.signal(cfg.tdef.INIT)
    
    while state.value == 1 and global_timer.sec() < cfg.GLOBAL_TIME:
        
        key = cv2.waitKey(1)
        if key == keys['esc']:
            with state.get_lock():
                state.value = 0
                
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

if __name__ == '__main__':
    if len(sys.argv) < 2:
        cfg_module = input('Config module name? ')
    else:
        cfg_module = sys.argv[1]
    batch_run(cfg_module)    