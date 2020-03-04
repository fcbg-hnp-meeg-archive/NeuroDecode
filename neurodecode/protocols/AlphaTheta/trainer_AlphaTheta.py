#!/usr/bin/env python3
#coding:utf-8
"""
  Author:  Arnaud Desvachez --<arnaud.desvachez@gmail.com>
  Purpose: Trainer protocol for deep meditation state neurofeedback
  
  It finds the subject's alpha and theta peaks, define the alpha and
  theta bands and compute the referencePSD in both alpha and theta bands.
  
  Created: 16.10.2019
"""
import sys

import numpy as np
import multiprocessing as mp

import neurodecode.decoder.features as features

from neurodecode import logger
import neurodecode.utils.pycnbi_utils as pu
from neurodecode.triggers.trigger_def import trigger_def
from neurodecode.gui.streams import redirect_stdout_to_queue


#----------------------------------------------------------------------
def check_config(cfg):
    """
    Ensure that the config file contains the parameters
    """
    critical_vars = {
        'COMMON': ['DATA_PATH'],
    }
    optional_vars = {
    }
    
    for key in critical_vars['COMMON']:
        if not hasattr(cfg, key):
            logger.error('%s is a required parameter' % key)
            raise RuntimeError
    
    for key in optional_vars:
        if not hasattr(cfg, key):
            setattr(cfg, key, optional_vars[key])
            logger.warning('Setting undefined parameter %s=%s' % (key, getattr(cfg, key)))
    
    return cfg

#----------------------------------------------------------------------
def run(cfg, state=mp.Value('i', 1), queue=None):
    """
    Training protocol for Alpha/Theta neurofeedback.
    """
    redirect_stdout_to_queue(logger, queue, 'INFO')

    # add tdef object
    cfg.tdef = trigger_def(cfg.TRIGGER_FILE)

    # Extract features
    if not state.value:
        sys.exit(-1)
        
    freqs = np.arange(cfg.FEATURES['PSD']['fmin'], cfg.FEATURES['PSD']['fmax']+0.5, 1/cfg.FEATURES['PSD']['wlen'])
    featdata = features.compute_features(cfg)
    
    # Average the PSD over the windows
    window_avg_psd =  np.mean(np.squeeze(featdata['X_data']), 0)
    
    # Alpha ref over the alpha band
    alpha_ref = round(np.mean(window_avg_psd[freqs>=8]))
    alpha_thr = round(alpha_ref - (0.5 * np.std(window_avg_psd[freqs>=8]) ))
    
    # Theta ref over Theta band
    theta_ref = round(np.mean(window_avg_psd[freqs<8]))
    theta_thr = round(theta_ref - (0.5 * np.std(window_avg_psd[freqs<8]) ))
        
    logger.info('Theta ref = {}; alpha ref ={}' .format(theta_ref, alpha_ref))
    logger.info('Theta thr = {}; alpha thr ={}' .format(theta_thr, alpha_thr))
    
#----------------------------------------------------------------------
def batch_run(cfg_module):
    """
    For batch run
    """
    cfg = pu.load_config(cfg_module)
    cfg = check_config(cfg)
    run(cfg)    

if __name__ == '__main__':
    # Load parameters
    if len(sys.argv) < 2:
        cfg_module = input('Config module name? ')
    else:
        cfg_module = sys.argv[1]
    batch_run(cfg_module)