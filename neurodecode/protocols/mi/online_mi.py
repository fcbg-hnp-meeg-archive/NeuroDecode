"""
Motor imagery testing.

After setting experimental parameters, it runs a trial with feedback
by calling the classify() method of a Feedback class object.
Trials are repeated until the set number of trials are achieved.


Kyuhwa Lee, 2015
Swiss Federal Institute of Technology (EPFL)


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os
import cv2
import sys
import time
import random
import multiprocessing as mp

import neurodecode.utils.io as io

from neurodecode import logger
from neurodecode.utils.lsl import search_lsl
from neurodecode.triggers import Trigger, TriggerDef
from neurodecode.protocols.feedback import Feedback
from neurodecode.decoder.decoder import BCIDecoderDaemon
from neurodecode.gui.streams import redirect_stdout_to_queue

# visualization
keys = {'left':81, 'right':83, 'up':82, 'down':84, 'pgup':85, 'pgdn':86,
        'home':80, 'end':87, 'space':32, 'esc':27, ',':44, '.':46, 's':115,
        'c':99, '[':91, ']':93, '1':49, '!':33, '2':50, '@':64, '3':51, '#':35}
color = dict(G=(20, 140, 0), B=(210, 0, 0), R=(0, 50, 200), Y=(0, 215, 235),
             K=(0, 0, 0), W=(255, 255, 255), w=(200, 200, 200))

def check_config(cfg):
    critical_vars = {
        'COMMON': ['DECODER_FILE',
                   'TRIGGER_DEVICE',
                   'TRIGGER_FILE',
                   'DIRECTIONS',
                   'TRIALS_EACH',
                   'PROB_ALPHA_NEW'],
        'TIMINGS': ['INIT', 'GAP', 'READY', 'FEEDBACK', 'DIR_CUE', 'CLASSIFY'],
        'BAR_STEP': ['left', 'right', 'up', 'down', 'both']
        }

    optional_vars = {
        'AMP_NAME':None,
        'FAKE_CLS':None,
        'TRIALS_RANDOMIZE':True,
        'BAR_SLOW_START':{'selected':'False', 'False':None, 'True':[1.0]},
        'PARALLEL_DECODING':{'selected':'False', 'False':None, 'True':{'period':0.06, 'num_strides':3}},
        'SHOW_TRIALS':True,
        'FREE_STYLE':False,
        'REFRESH_RATE':30,
        'BAR_BIAS':None,
        'BAR_REACH_FINISH':False,
        'FEEDBACK_TYPE':'BAR',
        'SHOW_CUE':True,
        'SCREEN_SIZE':(1920, 1080),
        'SCREEN_POS':(0, 0),
        'DEBUG_PROBS':False,
        'LOG_PROBS':False,
        'WITH_REX': False,
        'WITH_STIMO': False,
        'ADAPTIVE': None,
    }

    for key in critical_vars['COMMON']:
        if not hasattr(cfg, key):
            logger.error('%s is a required parameter' % key)
            raise RuntimeError

    if not hasattr(cfg, 'TIMINGS'):
        logger.error('"TIMINGS" not defined in config.')
        raise RuntimeError
    for v in critical_vars['TIMINGS']:
        if v not in cfg.TIMINGS:
            logger.error('%s not defined in config.' % v)
            raise RuntimeError

    if not hasattr(cfg, 'BAR_STEP'):
        logger.error('"BAR_STEP" not defined in config.')
        raise RuntimeError
    for v in critical_vars['BAR_STEP']:
        if v not in cfg.BAR_STEP:
            logger.error('%s not defined in config.' % v)
            raise RuntimeError

    for key in optional_vars:
        if not hasattr(cfg, key):
            setattr(cfg, key, optional_vars[key])
            logger.warning('Setting undefined parameter %s=%s' % (key, getattr(cfg, key)))

    if getattr(cfg, 'TRIGGER_DEVICE') == None:
        logger.warning('The trigger device is set to None! No events will be saved.')
        # raise RuntimeError('The trigger device is set to None! No events will be saved.')

def run(cfg, state=mp.Value('i', 1), queue=None):

    def confusion_matrix(Y_true, Y_pred, label_len=6):
        """
        Generate confusion matrix in a string format
        Parameters
        ----------
        Y_true : list
            The true labels
        Y_pred : list
            The test labels
        label_len : int
            The maximum label text length displayed (minimum length: 6)
        Returns
        -------
        cfmat : str
            The confusion matrix in str format (X-axis: prediction, -axis: ground truth)
        acc : float
            The accuracy
        """
        import numpy as np
        from sklearn.metrics import confusion_matrix as sk_confusion_matrix

        # find labels
        if type(Y_true) == np.ndarray:
            Y_labels = np.unique(Y_true)
        else:
            Y_labels = list(set(Y_true))

        # Check the provided label name length
        if label_len < 6:
            label_len = 6
            logger.warning('label_len < 6. Setting to 6.')
        label_tpl = '%' + '-%ds' % label_len
        col_tpl = '%' + '-%d.2f' % label_len

        # sanity check
        if len(Y_pred) > len(Y_true):
            raise RuntimeError('Y_pred has more items than Y_true')
        elif len(Y_pred) < len(Y_true):
            Y_true = Y_true[:len(Y_pred)]

        cm = sk_confusion_matrix(Y_true, Y_pred, Y_labels)

        # compute confusion matrix
        cm_rate = cm.copy().astype('float')
        cm_sum = np.sum(cm, axis=1)

        # Fill confusion string
        for r, s in zip(cm_rate, cm_sum):
            if s > 0:
                r /= s
        cm_txt = label_tpl % 'gt\dt'
        for l in Y_labels:
            cm_txt += label_tpl % str(l)[:label_len]
        cm_txt += '\n'
        for l, r in zip(Y_labels, cm_rate):
            cm_txt += label_tpl % str(l)[:label_len]
            for c in r:
                cm_txt += col_tpl % c
            cm_txt += '\n'

        # compute accuracy
        correct = 0.0
        for c in range(cm.shape[0]):
            correct += cm[c][c]
        cm_sum = cm.sum()
        if cm_sum > 0:
            acc = correct / cm.sum()
        else:
            acc = 0.0

        return cm_txt, acc


    redirect_stdout_to_queue(logger, queue, 'INFO')

    # Wait the recording to start (GUI)
    while state.value == 2: # 0: stop, 1:start, 2:wait
        pass

    #  Protocol runs if state equals to 1
    if not state.value:
        sys.exit(-1)

    if cfg.FAKE_CLS is None:
        # chooose amp
        if cfg.AMP_NAME is None:
            amp_name = search_lsl(ignore_markers=True, state=state)
        else:
            amp_name = cfg.AMP_NAME
        fake_dirs = None
    else:
        amp_name = None
        fake_dirs = [v for (k, v) in cfg.DIRECTIONS]

    # events and triggers
    tdef = TriggerDef(cfg.TRIGGER_FILE)
    #if cfg.TRIGGER_DEVICE is None:
    #    input('\n** Warning: No trigger device set. Press Ctrl+C to stop or Enter to continue.')
    trigger = Trigger(cfg.TRIGGER_DEVICE, state)
    if trigger.init(50) == False:
        logger.error('Cannot connect to USB2LPT device. Use a mock trigger instead?')
        input('Press Ctrl+C to stop or Enter to continue.')
        trigger = Trigger('FAKE', state)
        trigger.init(50)

    # For adaptive (need to share the actual true label accross process)
    label = mp.Value('i', 0)

    # init classification
    decoder = BCIDecoderDaemon(amp_name, cfg.DECODER_FILE, buffer_size=1.0, fake=(cfg.FAKE_CLS is not None), fake_dirs=fake_dirs, \
                               parallel=cfg.PARALLEL_DECODING[cfg.PARALLEL_DECODING['selected']], alpha_new=cfg.PROB_ALPHA_NEW, label=label)

    # OLD: requires trigger values to be always defined
    #labels = [tdef.by_value[x] for x in decoder.get_labels()]
    # NEW: events can be mapped into integers:
    labels = []
    dirdata = set([d[1] for d in cfg.DIRECTIONS])
    for x in decoder.get_labels():
        if x not in dirdata:
            labels.append(tdef.by_value[x])
        else:
            labels.append(x)

    # map class labels to bar directions
    bar_def = {label:str(dir) for dir, label in cfg.DIRECTIONS}
    bar_dirs = [bar_def[l] for l in labels]
    dir_seq = []
    for x in range(cfg.TRIALS_EACH):
        dir_seq.extend(bar_dirs)

    logger.info('Initializing decoder.')
    while decoder.is_running() == 0:
        time.sleep(0.01)

    # bar visual object
    if cfg.FEEDBACK_TYPE == 'BAR':
        from neurodecode.protocols.viz_bars import BarVisual
        visual = BarVisual(cfg.GLASS_USE, screen_pos=cfg.SCREEN_POS,
            screen_size=cfg.SCREEN_SIZE)
    elif cfg.FEEDBACK_TYPE == 'BODY':
        assert hasattr(cfg, 'FEEDBACK_IMAGE_PATH'), 'FEEDBACK_IMAGE_PATH is undefined in your config.'
        from neurodecode.protocols.viz_human import BodyVisual
        visual = BodyVisual(cfg.FEEDBACK_IMAGE_PATH, use_glass=cfg.GLASS_USE,
            screen_pos=cfg.SCREEN_POS, screen_size=cfg.SCREEN_SIZE)
    visual.put_text('Waiting to start')
    if cfg.LOG_PROBS:
        logdir = io.parse_path(cfg.DECODER_FILE).dir
        probs_logfile = time.strftime(logdir + "probs-%Y%m%d-%H%M%S.txt", time.localtime())
    else:
        probs_logfile = None
    feedback = Feedback(cfg, state, visual, tdef, trigger, probs_logfile)

    # If adaptive classifier
    if cfg.ADAPTIVE[cfg.ADAPTIVE['selected']]:
        nb_runs = cfg.ADAPTIVE[cfg.ADAPTIVE['selected']][0]
        adaptive = True
    else:
        nb_runs = 1
        adaptive = False

    run = 1
    while run <= nb_runs:

        if cfg.TRIALS_RANDOMIZE:
            random.shuffle(dir_seq)
        else:
            dir_seq = [d[0] for d in cfg.DIRECTIONS] * cfg.TRIALS_EACH
        num_trials = len(dir_seq)

        # For adaptive, retrain classifier
        if run > 1:

            #  Allow to retrain classifier
            with decoder.label.get_lock():
                decoder.label.value = 1

            # Wait that the retraining is done
            while decoder.label.value == 1:
                time.sleep(0.01)

            feedback.viz.put_text('Press any key')
            feedback.viz.update()
            cv2.waitKeyEx()
            feedback.viz.fill()

        # start
        trial = 1
        dir_detected = []
        prob_history = {c:[] for c in bar_dirs}
        while trial <= num_trials:
            if cfg.SHOW_TRIALS:
                title_text = 'Trial %d / %d' % (trial, num_trials)
            else:
                title_text = 'Ready'
            true_label = dir_seq[trial - 1]

            # profiling feedback
            #import cProfile
            #pr = cProfile.Profile()
            #pr.enable()
            result = feedback.classify(decoder, true_label, title_text, bar_dirs, prob_history=prob_history, adaptive=adaptive)
            #pr.disable()
            #pr.print_stats(sort='time')

            if result is None:
                decoder.stop()
                return
            else:
                pred_label = result
            dir_detected.append(pred_label)

            if cfg.WITH_REX is True and pred_label == true_label:
                # if cfg.WITH_REX is True:
                if pred_label == 'U':
                    rex_dir = 'N'
                elif pred_label == 'L':
                    rex_dir = 'W'
                elif pred_label == 'R':
                    rex_dir = 'E'
                elif pred_label == 'D':
                    rex_dir = 'S'
                else:
                    logger.warning('Rex cannot execute undefined action %s' % pred_label)
                    rex_dir = None
                if rex_dir is not None:
                    visual.move(pred_label, 100, overlay=False, barcolor='B')
                    visual.update()
                    logger.info('Executing Rex action %s' % rex_dir)
                    os.system('%s/Rex/RexControlSimple.exe %s %s' % (os.environ['NEUROD_ROOT'], cfg.REX_COMPORT, rex_dir))
                    time.sleep(8)

            if true_label == pred_label:
                msg = 'Correct'
            else:
                msg = 'Wrong'
            if cfg.TRIALS_RETRY is False or true_label == pred_label:
                logger.info('Trial %d: %s (%s -> %s)' % (trial, msg, true_label, pred_label))
                trial += 1

        if len(dir_detected) > 0:
            # write performance and log results
            fdir = io.parse_path(cfg.DECODER_FILE).dir
            logfile = time.strftime(fdir + "/online-%Y%m%d-%H%M%S.txt", time.localtime())
            with open(logfile, 'w') as fout:
                fout.write('Ground-truth,Prediction\n')
                for gt, dt in zip(dir_seq, dir_detected):
                    fout.write('%s,%s\n' % (gt, dt))
                cfmat, acc = confusion_matrix(dir_seq, dir_detected)
                fout.write('\nAccuracy %.3f\nConfusion matrix\n' % acc)
                fout.write(cfmat)
                logger.info('Log exported to %s' % logfile)
            print('\nAccuracy %.3f\nConfusion matrix\n' % acc)
            print(cfmat)

        run += 1

    visual.finish()

    with state.get_lock():
        state.value = 0

    if decoder.is_running():
        decoder.stop()

    '''
    # automatic thresholding
    if prob_history and len(bar_dirs) == 2:
        total = sum(len(prob_history[c]) for c in prob_history)
        fout = open(probs_logfile, 'a')
        msg = 'Automatic threshold optimization.\n'
        max_acc = 0
        max_bias = 0
        for bias in np.arange(-0.99, 1.00, 0.01):
            corrects = 0
            for p in prob_history[bar_dirs[0]]:
                p_biased = (p + bias) / (bias + 1) # new sum = (p+bias) + (1-p) = bias+1
                if p_biased >= 0.5:
                    corrects += 1
            for p in prob_history[bar_dirs[1]]:
                p_biased = (p + bias) / (bias + 1) # new sum = (p+bias) + (1-p) = bias+1
                if p_biased < 0.5:
                    corrects += 1
            acc = corrects / total
            msg += '%s%.2f: %.3f\n' % (bar_dirs[0], bias, acc)
            if acc > max_acc:
                max_acc = acc
                max_bias = bias
        msg += 'Max acc = %.3f at bias %.2f\n' % (max_acc, max_bias)
        fout.write(msg)
        fout.close()
        print(msg)
    '''

    logger.info('Finished.')

# for batch script
def batch_run(cfg_module):
    cfg = io.load_config(cfg_module)
    check_config(cfg)
    run(cfg)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        cfg_module = input('Config module name? ')
    else:
        cfg_module = sys.argv[1]
    batch_run(cfg_module)
